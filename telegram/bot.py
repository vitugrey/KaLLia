# ============ Importações ============ #
import os
import sys
import asyncio
import httpx
from loguru import logger
from pathlib import Path

# Fix de compatibilidade: Pyrogram 2.x quebra no Python 3.12+ sem um event loop ativo
asyncio.set_event_loop(asyncio.new_event_loop())

# pyrefly: ignore [missing-import]
from pyrogram import Client, filters
# pyrefly: ignore [missing-import]
from pyrogram.types import Message
# pyrefly: ignore [missing-import]
from pyrogram.enums import ChatAction



# ============ Logger ============ #
def setup_logger():
    """Configura o Loguru: terminal sempre + arquivo compartilhado se o volume estiver montado."""
    LOG_FILE = Path("/databases/kallia.log")

    logger.remove()

    # Sink 1: terminal
    logger.add(
        sys.stderr,
        format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan> - <level>{message}</level>",
        level="DEBUG",
        colorize=True,
    )

    # Sink 2: arquivo compartilhado com a API (só se o volume estiver montado)
    if LOG_FILE.parent.exists():
        logger.add(
            str(LOG_FILE),
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
            level="DEBUG",
            rotation="00:00",
            retention="30 days",
            compression="zip",
            encoding="utf-8",
            enqueue=True,
        )
        logger.info(f"[TELEGRAM] Logger em arquivo ativo: {LOG_FILE}")
    else:
        logger.warning("[TELEGRAM] Volume /databases não montado — logs apenas no terminal.")


setup_logger()


# ============ Configurações ============ #
API_ID    = int(os.getenv("TELEGRAM_API_ID", "0"))
API_HASH  = os.getenv("TELEGRAM_API_HASH", "")
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")

ALLOWED_USER_ID = int(os.getenv("TELEGRAM_ALLOWED_USER_ID", "0"))

# URL interna do Docker para a API da KaLLia
KALLIA_API_URL = os.getenv("KALLIA_API_URL", "http://kallia-api:1904")

SESSION_ID = "telegram_session"


# ============ Cliente Pyrogram ============ #
app = Client(
    name="kallia_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
)


# ============ Handlers ============ #
@app.on_message(filters.command("start") & filters.private)
async def start_handler(client: Client, message: Message):
    """Mensagem de boas-vindas."""
    if message.from_user.id != ALLOWED_USER_ID:
        await message.reply_text("Acesso negado.")
        return

    await message.reply_text(
        "KaLLia online.\n"
        "Pode falar."
    )


@app.on_message(filters.text & filters.private & ~filters.command("start"))
async def chat_handler(client: Client, message: Message):
    """Recebe a mensagem, valida o usuário e manda para a API da KaLLia."""

    # Validação: só responde ao usuário autorizado
    if message.from_user.id != ALLOWED_USER_ID:
        logger.warning(f"[TELEGRAM] Acesso negado para user_id={message.from_user.id}")
        await message.reply_text("Acesso negado.")
        return

    user_text = message.text
    logger.info(f"[TELEGRAM] Mensagem recebida: {user_text[:60]}...")

    # Mostra "digitando..." enquanto processa
    await client.send_chat_action(message.chat.id, ChatAction.TYPING)

    try:
        async with httpx.AsyncClient(timeout=120.0) as http:
            resp = await http.post(
                f"{KALLIA_API_URL}/chat",
                json={
                    "message": user_text,
                    "session_id": SESSION_ID,
                    "image_base64": None,
                },
                headers={
                    "X-Client-Name": "telegram-bot",
                    "Content-Type": "application/json",
                },
            )
            resp.raise_for_status()
            kallia_response = resp.json().get("response", "Sem resposta.")
            logger.info(f"[TELEGRAM] Resposta enviada: {kallia_response[:60]}...")
            await message.reply_text(kallia_response)

    except httpx.ConnectError:
        logger.error("[TELEGRAM] Não foi possível conectar à KaLLia API.")
        await message.reply_text("Não consegui conectar ao meu servidor. Verifica se a API está rodando.")
    except Exception as e:
        logger.error(f"[TELEGRAM] Erro no chat_handler: {e}")
        await message.reply_text("Algo deu errado aqui.")


# ============ Entrada ============ #
if __name__ == "__main__":
    logger.info("[TELEGRAM] Iniciando KaLLia Telegram Bot...")
    app.run()
