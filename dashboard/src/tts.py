import io
# pyrefly: ignore [missing-import]
import edge_tts
from loguru import logger
from src.config import TTS_VOICE

async def text_to_speech(text: str, voice: str = TTS_VOICE) -> bytes:
    """
    Sintetiza texto em áudio MP3 utilizando o Edge-TTS com voz neural brasileira.
    """
    if not text or not text.strip():
        return b""

    logger.debug(f"[TTS] Sintetizando áudio com voz '{voice}': {text[:40]}...")
    communicate = edge_tts.Communicate(text, voice)
    
    audio_buffer = bytearray()
    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            audio_buffer.extend(chunk["data"])

    logger.info(f"[TTS] Áudio gerado com sucesso: {len(audio_buffer)} bytes")
    return bytes(audio_buffer)
