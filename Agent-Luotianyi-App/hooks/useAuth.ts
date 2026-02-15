import { useState, useEffect, useCallback } from 'react';
import AsyncStorage from '@react-native-async-storage/async-storage';

const AUTH_KEY = 'auth_token';
const AUTO_LOGIN_KEY = 'auto_login';
const USERNAME_KEY = 'saved_username';
const PASSWORD_KEY = 'saved_password';

export interface AuthState {
  isLoggedIn: boolean;
  isLoading: boolean;  // 正在检查自动登录
  username: string;
}

export function useAuth() {
  const [authState, setAuthState] = useState<AuthState>({
    isLoggedIn: false,
    isLoading: true,
    username: '',
  });

  // 启动时检查是否有自动登录凭据
  useEffect(() => {
    checkAutoLogin();
  }, []);

  const checkAutoLogin = async () => {
    try {
      const autoLogin = await AsyncStorage.getItem(AUTO_LOGIN_KEY);
      if (autoLogin === 'true') {
        const savedUsername = await AsyncStorage.getItem(USERNAME_KEY);
        const savedPassword = await AsyncStorage.getItem(PASSWORD_KEY);
        if (savedUsername && savedPassword) {
          // TODO: 实际调用服务器登录接口验证
          // 目前先模拟自动登录成功
          setAuthState({
            isLoggedIn: true,
            isLoading: false,
            username: savedUsername,
          });
          return;
        }
      }
    } catch (e) {
      console.error('自动登录检查失败:', e);
    }
    setAuthState(prev => ({ ...prev, isLoading: false }));
  };

  const login = useCallback(async (username: string, password: string, autoLogin: boolean): Promise<{ success: boolean; message: string }> => {
    try {
      // TODO: 替换为实际的服务器登录请求
      // 目前模拟：用户名和密码非空即可登录
      if (!username.trim() || !password.trim()) {
        return { success: false, message: '用户名或密码不能为空' };
      }

      // 模拟网络请求延迟
      await new Promise(resolve => setTimeout(resolve, 500));

      // 保存自动登录设置
      if (autoLogin) {
        await AsyncStorage.setItem(AUTO_LOGIN_KEY, 'true');
        await AsyncStorage.setItem(USERNAME_KEY, username);
        await AsyncStorage.setItem(PASSWORD_KEY, password);
      } else {
        await AsyncStorage.removeItem(AUTO_LOGIN_KEY);
        await AsyncStorage.removeItem(USERNAME_KEY);
        await AsyncStorage.removeItem(PASSWORD_KEY);
      }

      await AsyncStorage.setItem(AUTH_KEY, 'dummy_token');

      setAuthState({
        isLoggedIn: true,
        isLoading: false,
        username,
      });

      return { success: true, message: '登录成功' };
    } catch (e) {
      console.error('登录失败:', e);
      return { success: false, message: '登录失败，请重试' };
    }
  }, []);

  const register = useCallback(async (username: string, password: string, inviteCode: string): Promise<{ success: boolean; message: string }> => {
    try {
      // TODO: 替换为实际的服务器注册请求
      if (!username.trim()) return { success: false, message: '用户名不能为空' };
      if (!password.trim()) return { success: false, message: '密码不能为空' };
      if (!inviteCode.trim()) return { success: false, message: '邀请码不能为空' };

      // 模拟网络请求延迟
      await new Promise(resolve => setTimeout(resolve, 500));

      return { success: true, message: '注册成功，请登录' };
    } catch (e) {
      console.error('注册失败:', e);
      return { success: false, message: '注册失败，请重试' };
    }
  }, []);

  const logout = useCallback(async () => {
    await AsyncStorage.removeItem(AUTH_KEY);
    setAuthState({
      isLoggedIn: false,
      isLoading: false,
      username: '',
    });
  }, []);

  return {
    ...authState,
    login,
    register,
    logout,
  };
}
