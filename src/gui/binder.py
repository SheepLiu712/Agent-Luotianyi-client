import time
import threading
from PySide6.QtCore import QObject, Signal
from ..live2d import Live2dModel, live2d
from ..utils.audio_processor import extract_audio_amplitude, decode_from_base64, play_audio, save_to_wav
from ..utils.logger import get_logger
import numpy as np
from typing import Dict, Callable

class AgentBinder(QObject):

    response_signal = Signal(str)
    update_signal = Signal(str)
    delete_signal = Signal()
    free_signal = Signal(bool)
    history_signal = Signal(list, int)  # history_list, current_top_index

    def __init__(self, hear_callback: Callable[[str], Dict], history_callback: Callable[[int, int], tuple] = None):
        super().__init__()
        self.logger = get_logger(self.__class__.__name__)
        if hear_callback:
            self.recv_callback = hear_callback
        else:
            raise ValueError("hear_callback must be provided")
        
        self.history_callback = history_callback
    
        self.thinking_thread: threading.Thread | None = None
        self.thinking: bool = False
        self.model: Live2dModel | None = None

    def hear(self, text: str):
        """
        接收用户输入的文本，并在后台处理
        """
        
        def _hear(text:str):
            self.start_thinking()
            try:
                # recv_callback return a generator for SSE
                response_generator = self.recv_callback(text)
                
                for response in response_generator:
                    self.start_thinking()
                    reply_text = response.get("text", "")
                    expression = response.get("expression", None)
                    audio_data = response.get("audio", b"")
                    audio_data = decode_from_base64(audio_data)
                    self.start_mouth_move(audio_data)

                    if expression and self.model:
                        self.model.set_expression_by_cmd(expression)
                    self.stop_thinking()
                    self.response_signal.emit(reply_text)
                    play_audio(audio_data)
 
                    
            except Exception as e:
                print(f"Error in hear loop: {e}")
            finally:
                self.stop_thinking()
                self.finish_reply()

        # 使用线程避免阻塞 UI
        thread = threading.Thread(target=_hear, args=(text,))
        thread.daemon = True
        thread.start()

    def load_history(self, count: int, end_index: int = -1):
        """
        请求加载历史记录
        :param count: 加载的数量
        :param end_index: 结束索引（不包含），-1表示从最新开始
        """
        if self.history_callback:
            thread = threading.Thread(target=self._fetch_history, args=(count, end_index))
            thread.daemon = True
            thread.start()

    def _fetch_history(self, count, end_index):
        if self.history_callback:
            history_data, start_index = self.history_callback(count, end_index)
            self.history_signal.emit(history_data, start_index)

    def update_bubble(self) -> None:
        '''
        等待LLM响应，在这个过程中在气泡中显示'...'直到响应完成
        '''
        self.response_signal.emit(" ")
        while self.thinking:
            for i in range(3):
                if not self.thinking:
                    break
                self.update_signal.emit("." * (i + 1))
                time.sleep(0.1)

        self.delete_signal.emit()

    def start_thinking(self):
        """
        开始思考，显示动态气泡
        """
        if self.thinking_thread and self.thinking_thread.is_alive():
            return  # 已经在思考中

        self.thinking = True
        self.free_signal.emit(False)
        self.thinking_thread = threading.Thread(target=self.update_bubble)
        self.thinking_thread.daemon = True
        self.thinking_thread.start()

    def stop_thinking(self):
        """
        停止思考，移除动态气泡
        """
        if not self.thinking:
            return  # 不在思考中
        self.thinking = False
        if self.thinking_thread:
            self.thinking_thread.join()
            self.thinking_thread = None
    
    def finish_reply(self):
        '''
        本轮对话结束，允许用户输入
        '''
        self.free_signal.emit(True)

    def start_mouth_move(self, wav: str | bytes, fps: int = 60):
        """
        开始口型同步
        """
        if not self.model:
            self.logger.warning("No Live2D model loaded for mouth movement.")
            return

        # # 保存音频数据
        # if isinstance(wav, str):
        #     wav_path = wav
        # else:
        #     # 将字节数据保存到temp/tts_output/目录下的临时文件
        #     wav_path = save_to_wav(wav)
        init_value = self.model.GetParameterValue("ParamMouthOpenY")
        amp = np.clip(extract_audio_amplitude(wav=wav, fps=fps) * 6 - 1, -1.0, 1.0)

        # 开始口型同步线程
        mouth_move_thread = threading.Thread(target=self._mouth_move, args=(init_value, amp, fps), daemon=True)
        mouth_move_thread.start()

    def _mouth_move(self, init_value: float, amp: np.ndarray, fps: int = 60):
        if not self.model:
            return
        
        st_time = time.time()
        while True:

            elapsed = time.time() - st_time
            frame_index = int(elapsed * fps)
            if frame_index >= len(amp):
                break
            weight = np.clip(frame_index / len(amp) - 0.95, 0, 1) * 20
            target_value = amp[frame_index] * (1-weight) + init_value * weight  # 最后一段平滑回到初始值
            self.model.SetParameterValue("ParamMouthOpenY", target_value, weight=0.3)
            time.sleep(1 / fps)

        self.model.SetParameterValue("ParamMouthOpenY", init_value, weight=1)