import asyncio
import httpx
from loguru import logger
from src.config import ASSEMBLYAI_API_KEY

async def transcribe_audio(audio_bytes: bytes) -> str:
    """
    Transcreve áudio em bytes utilizando a API do AssemblyAI em português.
    """
    if not ASSEMBLYAI_API_KEY:
        raise ValueError("ASSEMBLYAI_API_KEY não configurada no .env")

    headers = {
        "authorization": ASSEMBLYAI_API_KEY
    }

    async with httpx.AsyncClient(timeout=60.0) as client:
        # 1. Upload do áudio
        logger.debug(f"[STT] Enviando {len(audio_bytes)} bytes para AssemblyAI...")
        upload_resp = await client.post(
            "https://api.assemblyai.com/v2/upload",
            headers=headers,
            content=audio_bytes
        )
        upload_resp.raise_for_status()
        upload_url = upload_resp.json().get("upload_url")

        # 2. Solicitar transcrição em pt
        logger.debug("[STT] Solicitando transcrição com language_code=pt...")
        transcript_resp = await client.post(
            "https://api.assemblyai.com/v2/transcript",
            headers=headers,
            json={
                "audio_url": upload_url,
                "language_code": "pt"
            }
        )
        transcript_resp.raise_for_status()
        transcript_id = transcript_resp.json().get("id")

        # 3. Polling do resultado
        for _ in range(60):
            await asyncio.sleep(0.5)
            poll_resp = await client.get(
                f"https://api.assemblyai.com/v2/transcript/{transcript_id}",
                headers=headers
            )
            poll_resp.raise_for_status()
            data = poll_resp.json()
            status = data.get("status")

            if status == "completed":
                text = data.get("text", "").strip()
                logger.info(f"[STT] Transcrição concluída: '{text}'")
                return text
            elif status == "error":
                err = data.get("error", "Erro desconhecido")
                logger.error(f"[STT] Erro no AssemblyAI: {err}")
                raise RuntimeError(f"Erro no AssemblyAI: {err}")

        raise TimeoutError("Tempo limite excedido aguardando transcrição.")
