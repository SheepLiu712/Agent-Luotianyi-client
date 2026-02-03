import requests
from typing import Tuple, List, Dict
from .types import ConversationItem
from .utils.logger import get_logger
from .safety import credential, encrypt_pwd

import os
import json

class NetworkClient:
    def __init__(self, base_url="http://127.0.0.1:8000"):
        self.base_url = base_url
        self.user_id = None
        self.message_token = None
        self.login_token = None
        self.logger = get_logger(self.__class__.__name__)



    def login(self, username: str, password: str, request_token: bool = False) -> Tuple[bool, str]:
        try:
            encrypted_password = encrypt_pwd.encrypt_password(password, base_url=self.base_url)
            if not encrypted_password:
                return False, "Failed to encrypt password. Check server connection."
                
            resp = requests.post(f"{self.base_url}/auth/login", json={
                "username": username, 
                "password": encrypted_password,
                "request_token": request_token
            })
            if resp.status_code == 200:
                data = resp.json()
                self.user_id = data.get("user_id")
                self.login_token = data.get("login_token")
                self.message_token = data.get("message_token")
                if request_token:
                    credential.save_credentials(self.user_id, self.login_token, True)
                else:
                    credential.save_credentials(self.user_id, None, False)

                return True, "Login Successful"
            else:
                try:
                    detail = resp.json().get("detail", "Login Failed")
                except:
                    detail = "Login Failed"
                return False, detail
        except Exception as e:
            return False, str(e)

    def auto_login(self, username: str, token: str) -> bool:
        try:
            resp = requests.post(f"{self.base_url}/auth/auto_login", json={"username": username, "token": token})
            if resp.status_code == 200:
                data = resp.json()
                self.user_id = data.get("user_id")
                self.login_token = data.get("login_token")
                self.message_token = data.get("message_token")
                credential.save_credentials(self.user_id, self.login_token, True)
                return True
            return False
        except Exception as e:
            print(f"Auto login error: {e}")
            return False

    def register(self, username: str, password: str, invite_code: str) -> Tuple[bool, str]:
        try:
            encrypted_password = encrypt_pwd.encrypt_password(password, base_url=self.base_url)
            if not encrypted_password:
                return False, "Failed to encrypt password. Check server connection."

            resp = requests.post(f"{self.base_url}/auth/register", 
                                 json={"username": username, "password": encrypted_password, "invite_code": invite_code})
            if resp.status_code == 200:
                return True, "Registration Successful"
            else:
                try:
                    detail = resp.json().get("detail", "Registration Failed")
                except:
                    detail = "Registration Failed"
                return False, detail
        except Exception as e:
            return False, str(e)

    def send_chat(self, text: str):
        if not self.user_id:
            yield {"text": "Not logged in"}
            return
            
        try:
            payload = {"text": text, "user_id": self.user_id, "token": self.message_token}
            # Use stream=True for SSE
            with requests.post(f"{self.base_url}/chat", json=payload, stream=True) as resp:
                if resp.status_code == 200:
                    for line in resp.iter_lines():
                        if line:
                            decoded_line = line.decode('utf-8')
                            if decoded_line.startswith("data: "):
                                json_str = decoded_line[6:]
                                try:
                                    data = json.loads(json_str)
                                    yield data
                                except json.JSONDecodeError:
                                    pass
                else:
                    self.logger.error(f"Server Error: {resp.status_code}")
                    yield {"text": f"Error: {resp.status_code}"}
        except Exception as e:
            self.logger.error(f"Connection Error: {e}")
            yield {"text": f"Connection Error: {e}"}

    def get_history(self, count: int, end_index: int) -> Tuple[List[ConversationItem], int]:
        if not self.user_id:
            return [], 0
            
        try:
            params = {"user_id": self.user_id, "token": self.message_token, "count": count, "end_index": end_index}
            resp = requests.get(f"{self.base_url}/history", params=params)
            if resp.status_code == 200:
                data = resp.json()
                # Ensure we handle the response correctly. The provided attachment showed ConversationItem mapping
                if "history" in data:
                     history_items = [ConversationItem(**item) for item in data.get("history", [])]
                     return history_items, data.get("start_index", 0)
                else:
                    return [], 0

        except Exception as e:
            self.logger.error(f"History Error: {e}")
        return [], 0

    def network_hear_callback(self, text: str):
        return self.send_chat(text)

    def network_history_callback(self, count: int, end_index: int) -> Tuple[List[ConversationItem], int]:
        return self.get_history(count, end_index)
