import soundfile as sf
import numpy as np
import winsound
import base64
from .logger import get_logger
import io
import os
from datetime import datetime

logger = get_logger("audio_processor")

def extract_audio_amplitude(wav: str | bytes, fps: int = 30) -> np.ndarray:
    """
    从音频文件中提取振幅（音量）信息，用于口型同步。
    
    Args:
        wav: 音频文件路径或字节流
        fps: 每秒采样的帧数，通常与Live2D模型的刷新率一致（如30或60）
        
    Returns:
        numpy.ndarray: 归一化后的振幅数组，值范围 [0, 1]
    """
    # 加载音频，sr=None 保持原始采样率
    try:
        if isinstance(wav, bytes):
            # soundfile.read supports file-like objects
            y, sr = sf.read(io.BytesIO(wav))
        else:
            y, sr = sf.read(wav)
    except Exception as e:
        logger.error(f"Failed to load audio with soundfile: {e}")
        return np.array([0.0])

    # 如果是多声道，取平均值转为单声道
    if y.ndim > 1:
        y = np.mean(y, axis=1)

    # 计算 hop_length 以匹配目标 fps
    # hop_length 是两帧之间的样本数
    hop_length = int(sr / fps)
    
    if hop_length <= 0:
        return np.array([0.0])

    # 计算 RMS (Root Mean Square) 振幅
    # Manual sliding window RMS
    # Pad y to handle the last frame
    pad_width = hop_length - (len(y) % hop_length)
    if pad_width != hop_length:
        y = np.pad(y, (0, pad_width), mode='constant')
        
    # Reshape to (num_frames, hop_length) and calculate RMS
    # This is a non-overlapping window approximation, which is close enough for lip sync
    # If we want overlapping, we'd need stride_tricks, but simple non-overlapping is faster and usually fine.
    # Librosa's rms uses centered frames which overlap.
    # For lip sync, simple block RMS is often sufficient.
    
    num_frames = len(y) // hop_length
    frames = y.reshape(num_frames, hop_length)
    rms = np.sqrt(np.mean(frames**2, axis=1))
    
    # 归一化处理
    # 可以根据需要调整归一化策略，例如使用对数刻度或设置阈值
    if np.max(rms) > 0:
        rms = rms / np.max(rms)
        
    # 平滑处理（可选），避免嘴巴抖动过快
    # rms = np.convolve(rms, np.ones(3)/3, mode='same')
    
    return rms

def decode_from_base64(base64_str: str) -> bytes:
    """
    从 Base64 编码的字符串解码为音频字节流。
    
    Args:
        base64_str: Base64 编码的音频字符串
        
    Returns:
        bytes: 解码后的音频数据
    """
    if not base64_str:
        return b""
    try:
        return base64.b64decode(base64_str)
    except Exception as e:
        logger.error(f"Error decoding base64 audio: {e}")
        return b""

def save_to_wav(wav_data: bytes) -> str:
    """
    将音频字节流保存为 WAV 文件。
    
    Args:
        wav_data: 音频数据的字节流
    Returns:
        str: 保存的文件路径
    """
    cwd = os.getcwd()
    output_dir = os.path.join(cwd, "temp", "tts_outputs")
    os.makedirs(output_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = os.path.join(output_dir, timestamp + ".wav")
    with open(output_path, "wb") as f:
        f.write(wav_data)
    logger.info(f"Saved WAV file to {output_path}")
    return output_path

HAS_WINSOUND = True

def play_audio(wav_data: bytes):
    """
    播放音频数据的函数占位符。
    实际实现应根据项目需求使用适当的音频播放库。
    
    Args:
        wav_data: 音频数据的字节流
    """
    if HAS_WINSOUND:
        try:
            # winsound.SND_MEMORY 指示第一个参数是内存中的数据
            # winsound.SND_NODEFAULT 如果找不到声音，不播放系统默认声音
            winsound.PlaySound(wav_data, winsound.SND_MEMORY | winsound.SND_NODEFAULT)
            logger.info("Audio playback finished.")
        except Exception as e:
            logger.error(f"Error playing sound: {e}")
    else:
        # 非 Windows 环境或者是需要跨平台时的备选方案 (需要安装 pyaudio)
        try:
            import pyaudio
            import wave
            import io
            
            logger.info("Using PyAudio for playback...")
            with wave.open(io.BytesIO(wav_data), 'rb') as wf:
                p = pyaudio.PyAudio()
                stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                                channels=wf.getnchannels(),
                                rate=wf.getframerate(),
                                output=True)
                
                chunk = 1024
                data = wf.readframes(chunk)
                while len(data) > 0:
                    stream.write(data)
                    data = wf.readframes(chunk)
                
                stream.stop_stream()
                stream.close()
                p.terminate()
            logger.info("Audio playback finished.")
        except ImportError:
            logger.warning("'winsound' not available (not Windows?) and 'pyaudio' not installed.")
            logger.warning("Cannot play audio directly.")
        except Exception as e:
            logger.error(f"Error utilizing PyAudio: {e}")