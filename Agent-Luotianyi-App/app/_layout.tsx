import { View, ActivityIndicator, StyleSheet } from "react-native";
import { SafeAreaProvider } from 'react-native-safe-area-context';
import { useAuth } from '../hooks/useAuth';
import LoginScreen from './login';
import Index from './index';

export default function RootLayout() {
  const { isLoggedIn, isLoading, login, register } = useAuth();

  // 正在检查自动登录状态时，显示加载画面
  if (isLoading) {
    return (
      <SafeAreaProvider>
        <View style={styles.loadingContainer}>
          <ActivityIndicator size="large" color="#66CCFF" />
        </View>
      </SafeAreaProvider>
    );
  }

  // 未登录 → 显示登录/注册界面
  if (!isLoggedIn) {
    return (
      <SafeAreaProvider>
        <LoginScreen onLogin={login} onRegister={register} />
      </SafeAreaProvider>
    );
  }

  // 已登录 → 显示主界面
  return (
    <SafeAreaProvider>
      <Index />
    </SafeAreaProvider>
  );
}

const styles = StyleSheet.create({
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#f5f5f5',
  },
});
