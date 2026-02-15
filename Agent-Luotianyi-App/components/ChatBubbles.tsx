import React from 'react';
import { View, Text, Image, StyleSheet } from 'react-native';

// 消息类型定义
export interface ChatMessage {
  id: string;
  type: 'text' | 'image';
  content: string; // 对于文本是文字内容，对于图片是图片路径
  isUser: boolean;
  timestamp?: number;
}

// 文本气泡组件
export const ChatBubble: React.FC<{ message: ChatMessage }> = ({ message }) => {
  const { content, isUser } = message;

  return (
    <View style={styles.bubbleContainer}>
      <View
        style={[
          styles.bubble,
          isUser ? styles.userBubble : styles.botBubble,
        ]}
      >
        <Text style={styles.bubbleText}>{content}</Text>
      </View>
    </View>
  );
};

// 图片气泡组件
export const ChatImageBubble: React.FC<{ message: ChatMessage }> = ({ message }) => {
  const { content, isUser } = message;

  return (
    <View style={styles.imageBubbleContainer}>
      <View style={isUser ? styles.imageWrapperUser : styles.imageWrapperBot}>
        <Image
          source={{ uri: content }}
          style={styles.chatImage}
          resizeMode="contain"
        />
      </View>
    </View>
  );
};

// 统一的消息渲染组件
export const MessageItem: React.FC<{ message: ChatMessage }> = ({ message }) => {
  if (message.type === 'image') {
    return <ChatImageBubble message={message} />;
  }
  return <ChatBubble message={message} />;
};

const styles = StyleSheet.create({
  // 文本气泡样式
  bubbleContainer: {
    paddingHorizontal: 10,
    paddingVertical: 5,
  },
  bubble: {
    maxWidth: '80%',
    paddingHorizontal: 15,
    paddingVertical: 10,
    borderRadius: 10,
  },
  userBubble: {
    alignSelf: 'flex-end',
    backgroundColor: '#FFFFFF', // 白色，对应 Python 版本的用户气泡
    borderBottomRightRadius: 2,
  },
  botBubble: {
    alignSelf: 'flex-start',
    backgroundColor: '#88EDFF', // 天依蓝，对应 Python 版本的机器人气泡
    borderBottomLeftRadius: 2,
  },
  bubbleText: {
    fontSize: 16,
    color: '#000000',
  },

  // 图片气泡样式
  imageBubbleContainer: {
    paddingHorizontal: 10,
    paddingVertical: 5,
  },
  imageWrapperUser: {
    alignSelf: 'flex-end',
    maxWidth: '80%',
  },
  imageWrapperBot: {
    alignSelf: 'flex-start',
    maxWidth: '80%',
  },
  chatImage: {
    width: 250,
    height: 250,
    borderRadius: 10,
  },
});
