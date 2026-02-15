import {
  Text, View, TextInput, TouchableOpacity, Image, StyleSheet, useWindowDimensions, Keyboard
} from "react-native";
import { useSafeAreaInsets } from 'react-native-safe-area-context';
import { useState, useEffect } from 'react';

export default function Index() {
  const insets = useSafeAreaInsets();
  const { height: screenHeight } = useWindowDimensions();
  const live2dHeight = screenHeight * 0.4;
  const [keyboardHeight, setKeyboardHeight] = useState(0);

  useEffect(() => {
    const showSubscription = Keyboard.addListener('keyboardDidShow', (e) => {
      setKeyboardHeight(e.endCoordinates.height);
    });
    const hideSubscription = Keyboard.addListener('keyboardDidHide', () => {
      setKeyboardHeight(0);
    });

    return () => {
      showSubscription.remove();
      hideSubscription.remove();
    };
  }, []);

  return (
    <View style={{ flex: 1, backgroundColor: 'white' }}>

      {/* 顶部安全区占位 */}
      <View style={{ height: insets.top, backgroundColor: 'white' }} />

      {/* 【固定层：Live2D 区域】- 绝对定位，不参与 flex 布局，永远固定在顶部 */}
      <View style={[styles.live2dFixedLayer, { top: insets.top, height: live2dHeight }]}>
        <Text>这里是天依，我纹丝不动</Text>
      </View>

      {/* 【可压缩区域：聊天历史 + 输入框】- 使用 flex 布局，会被键盘压缩 */}
      <View style={{ flex: 1, marginTop: live2dHeight, marginBottom: keyboardHeight }}>
        {/* 聊天历史区域 - 会被键盘压缩 */}
        <View style={{ flex: 1, backgroundColor: 'white', borderTopWidth: 1, borderColor: '#eee' }}>
          <Text style={{ padding: 10 }}>聊天历史区域</Text>
          <Text style={{ padding: 10 }}>键盘弹起时，我会被压缩变短</Text>
        </View>

        {/* 输入框区域 - 跟随键盘 */}
        <View style={[styles.inputContainer, { paddingBottom: Math.max(insets.bottom, 10) }]}>
          <TextInput
            style={styles.inputField}
            placeholder="给天依发消息..."
            placeholderTextColor="#999"
          />
          
          <TouchableOpacity style={styles.iconButton} onPress={() => console.log('发送图片')}>
            <Image
              source={require('../assets/images/picture_icon_activate.png')}
              style={styles.iconImage}
            />
          </TouchableOpacity>

          <TouchableOpacity style={styles.iconButton} onPress={() => console.log('发送文本')}>
            <Image
              source={require('../assets/images/send_button_activate.png')}
              style={styles.iconImage}
            />
          </TouchableOpacity>
        </View>
      </View>
    </View>
  );
}


const styles = StyleSheet.create({
  live2dFixedLayer: {
    position: 'absolute',
    left: 0,
    right: 0,
    backgroundColor: 'lightblue',
    justifyContent: 'center',
    alignItems: 'center',
    zIndex: 10, // 最高层级，永远显示在最上面
  },
  inputContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#f0f0f0',
    padding: 10,
    borderTopWidth: 1,
    borderTopColor: '#ddd',
  },
  inputField: {
    flex: 1,
    height: 40,
    backgroundColor: '#ffffff',
    borderRadius: 20,
    paddingHorizontal: 15,
    marginRight: 10,
  },
  iconButton: {
    padding: 5,
    marginLeft: 5,
  },
  iconImage: {
    width: 30,
    height: 30,
    resizeMode: 'stretch',
  },
});