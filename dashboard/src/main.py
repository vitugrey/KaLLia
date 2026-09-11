import os
import base64
from pathlib import Path
from typing import Optional
from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import httpx
from loguru import logger

from src.config import KALLIA_API_URL
from src.stt import transcribe_audio
from src.tts import text_to_speech

app = FastAPI(
    title="KaLLia Smart Mirror Dashboard",
    description="Interface e middleware de áudio para o Smart Mirror de 7 polegadas da KaLLia.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

STATIC_DIR = Path(__file__).parent.parent / "static"

class ChatInput(BaseModel):
    message: str
    session_id: Optional[str] = "mirror_session"

@app.post("/api/chat")
async def chat_text(input_data: ChatInput):
    """Envia texto digitado para a KaLLia e retorna texto e áudio sintetizado."""
    user_text = input_data.message.strip()
    if not user_text:
        raise HTTPException(status_code=400, detail="Mensagem vazia.")

    logger.info(f"[MIRROR] Mensagem de texto recebida: '{user_text}'")

    # 1. Enviar para a KaLLia API
    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            resp = await client.post(
                f"{KALLIA_API_URL}/chat",
                json={
                    "message": user_text,
                    "session_id": input_data.session_id,
                    "image_base64": None,
                },
                headers={
                    "X-Client-Name": "smart-mirror",
                    "Content-Type": "application/json",
                },
            )
            resp.raise_for_status()
            kallia_reply = resp.json().get("response", "")
    except Exception as e:
        logger.error(f"[MIRROR] Erro ao comunicar com a KaLLia API: {e}")
        raise HTTPException(status_code=502, detail=f"Erro ao conectar com a API: {e}")

    # 2. Sintetizar áudio com Edge-TTS
    audio_b64 = ""
    try:
        audio_bytes = await text_to_speech(kallia_reply)
        if audio_bytes:
            audio_b64 = base64.b64encode(audio_bytes).decode("utf-8")
    except Exception as e:
        logger.warning(f"[MIRROR] Erro ao sintetizar áudio: {e}")

    return {
        "user_text": user_text,
        "reply_text": kallia_reply,
        "audio_base64": audio_b64,
    }

@app.post("/api/voice/talk")
async def voice_talk(
    file: UploadFile = File(...),
    session_id: Optional[str] = Form("mirror_session")
):
    """Recebe o áudio do microfone (Push-to-talk), transcreve via STT e devolve resposta + voz."""
    logger.info(f"[MIRROR] Áudio recebido do microfone: {file.filename}, content-type: {file.content_type}")
    
    audio_bytes = await file.read()
    if not audio_bytes or len(audio_bytes) < 1000:
        raise HTTPException(status_code=400, detail="Áudio muito curto ou vazio.")

    # 1. Transcrever com AssemblyAI
    try:
        user_text = await transcribe_audio(audio_bytes)
    except Exception as e:
        logger.error(f"[MIRROR] Erro no STT: {e}")
        raise HTTPException(status_code=500, detail=f"Falha ao transcrever voz: {e}")

    if not user_text:
        return {
            "user_text": "",
            "reply_text": "Não consegui te ouvir direito. Poderia repetir?",
            "audio_base64": "",
        }

    # 2. Enviar texto para a KaLLia API
    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            resp = await client.post(
                f"{KALLIA_API_URL}/chat",
                json={
                    "message": user_text,
                    "session_id": session_id,
                    "image_base64": None,
                },
                headers={
                    "X-Client-Name": "smart-mirror-voice",
                    "Content-Type": "application/json",
                },
            )
            resp.raise_for_status()
            kallia_reply = resp.json().get("response", "")
    except Exception as e:
        logger.error(f"[MIRROR] Erro ao comunicar com a KaLLia API: {e}")
        raise HTTPException(status_code=502, detail=f"Erro na KaLLia API: {e}")

    # 3. Sintetizar áudio com Edge-TTS
    audio_b64 = ""
    try:
        audio_bytes = await text_to_speech(kallia_reply)
        if audio_bytes:
            audio_b64 = base64.b64encode(audio_bytes).decode("utf-8")
    except Exception as e:
        logger.warning(f"[MIRROR] Erro ao sintetizar áudio: {e}")

    return {
        "user_text": user_text,
        "reply_text": kallia_reply,
        "audio_base64": audio_b64,
    }

@app.get("/api/system/status")
async def get_system_status():
    """Consulta os dados vitais do Raspberry Pi (temperatura, RAM, armazenamento)."""
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(
                f"{KALLIA_API_URL}/status",
                headers={"X-Client-Name": "smart-mirror-widget"}
            )
            resp.raise_for_status()
            return resp.json()
    except Exception as e:
        logger.warning(f"[MIRROR] Falha ao obter status: {e}")
        return {"temperatura": "N/A", "memoria": "N/A", "energia": "N/A"}

@app.get("/api/finance/saldo")
async def get_saldo():
    """Consulta rápida do saldo financeiro para widget do espelho."""
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(
                f"{KALLIA_API_URL}/finance/saldo",
                headers={"X-Client-Name": "smart-mirror-widget"}
            )
            resp.raise_for_status()
            return resp.json()
    except Exception as e:
        logger.warning(f"[MIRROR] Falha ao obter saldo: {e}")
        return {}

# Serve frontend estático
if STATIC_DIR.exists():
    app.mount("/", StaticFiles(directory=str(STATIC_DIR), html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.main:app", host="0.0.0.0", port=8080, reload=True)
