from contextlib import asynccontextmanager
from fastapi import FastAPI, Body, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import uvicorn
import os
import random
import sys
import base64
import asyncio
import json
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization, hashes

# Ensure src is importable
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)
    
from src.database import init_db, register_user, verify_user


@asynccontextmanager
async def startup_event(app: FastAPI):
    init_db()
    generate_keys()
    yield
    # Any shutdown logic can go here

app = FastAPI(lifespan=startup_event)

# --- RSA Key Management ---
private_key = None
public_key_pem = None

def generate_keys():
    global private_key, public_key_pem
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )
    public_key = private_key.public_key()
    public_key_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    ).decode('utf-8')
    print("RSA Keys generated.")

def decrypt_password(encrypted_b64: str) -> str:
    try:
        encrypted_bytes = base64.b64decode(encrypted_b64)
        original_message = private_key.decrypt(
            encrypted_bytes,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        return original_message.decode('utf-8')
    except Exception as e:
        print(f"Decryption error: {e}")
        raise HTTPException(status_code=400, detail="Encryption error")

@app.get("/auth/public_key")
async def get_public_key():
    return {"public_key": public_key_pem}
# --------------------------

class ChatRequest(BaseModel):
    text: str
    user_id: str

class ChatResponse(BaseModel):
    text: str
    audio: str | None = None
    expression: str | None = None

class LoginRequest(BaseModel):
    username: str
    password: str
    request_token: bool = False

class RegisterRequest(BaseModel):
    username: str
    password: str
    invite_code: str

class AutoLoginRequest(BaseModel):
    username: str
    token: str


@app.post("/auto_login")
async def auto_login(req: AutoLoginRequest):
    print(f"Auto login request: {req.username}")
    # Dummy token verification: token must equal username for now
    if req.token == req.username:
        return {"message": "Auto login successful", "user_id": req.username}
    raise HTTPException(status_code=401, detail="Invalid token")



@app.post("/register")
async def register(req: RegisterRequest):
    print(f"Register request: {req.username} with code {req.invite_code}") 
    # Decrypt password
    decrypted_password = decrypt_password(req.password)
    
    success, msg = register_user(req.username, decrypted_password, req.invite_code)
    if not success:
        raise HTTPException(status_code=400, detail=msg)
    return {"message": "Registration successful"}

@app.post("/login")
async def login(req: LoginRequest):
    request_token = req.request_token
    print(f"Login request: {req.username}")
    # Decrypt password
    decrypted_password = decrypt_password(req.password)
    
    if verify_user(req.username, decrypted_password):
        return {"token": req.username, "user_id": req.username}
    raise HTTPException(status_code=401, detail="Invalid credentials")

@app.post("/chat")
async def chat(request: ChatRequest):
    print(f"Server received: {request.text} from {request.user_id}")
    audio_path = "example_audio.wav"
    with open(audio_path, "rb") as audio_file:
            original_audio_data = audio_file.read()
            base64_audio = base64.b64encode(original_audio_data).decode('utf-8')
    
    async def event_generator():
        # Dummy logic: split response to demonstrate SSE
        response_text_1 = f"服务端收到({request.user_id}): {request.text} (1/2)"
        response_text_2 = f"这是后续的消息 (2/2)"
        
        responses = [
            ChatResponse(text=response_text_1, expression="happy", audio=base64_audio),
            ChatResponse(text=response_text_2, expression="normal", audio=base64_audio)
        ]
        
        for response in responses:
            await asyncio.sleep(0.5) 
            data = response.model_dump_json() if hasattr(response, "model_dump_json") else response.json()
            yield f"data: {data}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")

@app.get("/history")
async def get_history(user_id: str, count: int = 10, end_index: int = -1):
    # Return dummy history
    return {
        "history": [
            {"timestamp": "2025-10-01 16:00:00", "source": "user", "content": f"Hello I am {user_id}", "type": "text"},
            {"timestamp": "2025-10-01 16:00:00", "source": "agent", "content": "Hi there!", "type": "text"}
        ],
        "start_index": 0
    }

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
