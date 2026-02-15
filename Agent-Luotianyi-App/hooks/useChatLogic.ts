import { useState, useRef } from 'react';
import { Keyboard, FlatList } from 'react-native';
import { ChatMessage } from '../components/ChatBubbles';

export const useChatLogic = () => {
  const [inputText, setInputText] = useState('');
  const [processing, setProcessing] = useState(false);
  const [messages, setMessages] = useState<ChatMessage[]>([
    { id: '1', type: 'text', content: '你好！我是洛天依。', isUser: false, timestamp: Date.now() }
  ]);
  const flatListRef = useRef<FlatList>(null);

  // 计算是否可以发送
  const canSend = inputText.trim().length > 0 && !processing;
  const canSendImage = !processing;

  // 发送文本消息
  const handleSendText = () => {
    if (!canSend) {
      return;
    }

    const newMessage: ChatMessage = {
      id: Date.now().toString(),
      type: 'text',
      content: inputText,
      isUser: true,
      timestamp: Date.now()
    };
    setMessages([...messages, newMessage]);
    setInputText('');
    Keyboard.dismiss();

    // 设置为处理中
    setProcessing(true);

    // 滚动到底部
    setTimeout(() => {
      flatListRef.current?.scrollToEnd({ animated: true });
    }, 100);

    // TODO: 这里后续会添加调用服务器的逻辑
    // 模拟回复
    setTimeout(() => {
      const botReply: ChatMessage = {
        id: (Date.now() + 1).toString(),
        type: 'text',
        content: '我收到了你的消息~',
        isUser: false,
        timestamp: Date.now()
      };
      setMessages(prev => [...prev, botReply]);
      
      // 处理完成，恢复可发送状态
      setProcessing(false);
      
      setTimeout(() => {
        flatListRef.current?.scrollToEnd({ animated: true });
      }, 100);
    }, 1000);
  };

  // 发送图片消息
  const handleSendImage = () => {
    console.log('发送图片');
    // TODO: 后续实现图片选择功能
  };

  return {
    // 状态
    inputText,
    processing,
    messages,
    flatListRef,
    canSend,
    canSendImage,
    
    // 方法
    setInputText,
    handleSendText,
    handleSendImage,
  };
};
