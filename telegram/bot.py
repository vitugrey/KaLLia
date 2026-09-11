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
from pyrogram import Client, filters, idle
# pyrefly: ignore [missing-import]
from pyrogram.types import Message, BotCommand
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
        "Pode falar mestre..."
    )

@app.on_message(filters.command("status") & filters.private)
async def status_handler(client: Client, message: Message):
    """Informações do Raspberry Pi onde roda a KaLLia."""
    if message.from_user.id != ALLOWED_USER_ID:
        await message.reply_text("Acesso negado.")
        return

    logger.info(f"[TELEGRAM] Comando status recebido pelo mestre.")
    await client.send_chat_action(message.chat.id, ChatAction.TYPING)

    try:
        async with httpx.AsyncClient(timeout=120.0) as http:
            resp = await http.get(
                f"{KALLIA_API_URL}/status",
                headers={
                    "X-Client-Name": "telegram-bot"
                },
            )
            resp.raise_for_status()
            status_data = resp.json(); kallia_response = "\n".join([f"{k.capitalize()}: {v}" for k, v in status_data.items()]) if isinstance(status_data, dict) else str(status_data)
            logger.info(f"[TELEGRAM] Resposta enviada: {kallia_response}")
            await message.reply_text(kallia_response)

    except httpx.ConnectError:
        logger.error("[TELEGRAM] Não foi possível conectar à KaLLia API.")
        await message.reply_text("Não consegui conectar ao meu servidor. Verifica se a API está rodando.")
    except Exception as e:
        logger.error(f"[TELEGRAM] Erro no status_handler: {e}")
        await message.reply_text("Algo deu errado aqui.")

@app.on_message(filters.command("saldo") & filters.private)
async def saldo_handler(client: Client, message: Message):
    """Consultar o saldo e resumo mensal no banco de financas."""
    if message.from_user.id != ALLOWED_USER_ID:
        await message.reply_text("Acesso negado.")
        return

    logger.info("[TELEGRAM] Comando saldo recebido pelo mestre.")
    await client.send_chat_action(message.chat.id, ChatAction.TYPING)

    try:
        async with httpx.AsyncClient(timeout=30.0) as http:
            resp = await http.get(
                f"{KALLIA_API_URL}/finance/saldo",
                headers={
                    "X-Client-Name": "telegram-bot"
                },
            )
            resp.raise_for_status()
            data = resp.json()

            mes = data.get("mes", 0)
            ano = data.get("ano", 0)

            def fmt_brl(val):
                return f"R$ {val:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

            rec_mes = fmt_brl(data.get("receita_mes", 0))
            desp_mes = fmt_brl(data.get("despesa_mes", 0))
            saldo_mes = fmt_brl(data.get("saldo_mes", 0))
            cartao_mes = fmt_brl(data.get("cartao_mes", 0))
            rec_ano = fmt_brl(data.get("receita_ano", 0))

            texto = (
                f"📊 **Resumo Financeiro ({mes:02d}/{ano})**\n\n"
                f"💵 **Receita do Mês:** `{rec_mes}`\n"
                f"💸 **Despesas do Mês:** `{desp_mes}`\n"
                f"💳 **Cartão de Crédito:** `{cartao_mes}`\n"
                f"💰 **Saldo do Mês:** `{saldo_mes}`\n\n"
                f"📈 **Receita do Ano ({ano}):** `{rec_ano}`"
            )

            await message.reply_text(texto)
    except httpx.ConnectError:
        logger.error("[TELEGRAM] Não foi possível conectar à KaLLia API.")
        await message.reply_text("Não consegui conectar ao meu servidor de API.")
    except Exception as e:
        logger.error(f"[TELEGRAM] Erro no saldo_handler: {e}")
        await message.reply_text("Houve um erro ao consultar as informações financeiras.")

@app.on_message(filters.command("help") & filters.private)
async def help_handler(client: Client, message: Message):
    """Exibe ajuda e lista de comandos disponíveis."""
    if message.from_user.id != ALLOWED_USER_ID:
        await message.reply_text("Acesso negado.")
        return

    help_text = (
        "👑 **KaLLia - Comandos e Funcionalidades**\n\n"
        "💬 **Conversa Direta:**\n"
        "Basta me enviar qualquer mensagem de texto ou dúvida financeira em linguagem natural.\n\n"
        "📋 **Comandos Rápidos:**\n"
        "• `/saldo` - Resumo financeiro do mês (receitas, despesas, cartão e saldo)\n"
        "• `/status` - Diagnóstico do Raspberry Pi (temperatura, RAM, disco e energia)\n"
        "• `/start` - Reinicia a conversa e exibe status online\n"
        "• `/help` - Exibe esta mensagem de ajuda\n\n"
        "🔒 **Controle de Sessão:**\n"
        "• `/normal` - Retorna para a sessão padrão de histórico\n"
        "• `/secret` - Alterna para sessão privada temporária"
    )
    await message.reply_text(help_text)

@app.on_message(filters.command("secret") & filters.private)
async def secret_handler(client: Client, message: Message):
    """Mudar para session_id secreta."""
    if message.from_user.id != ALLOWED_USER_ID:
        await message.reply_text("Acesso negado.")
        return

    global SESSION_ID
    SESSION_ID = "secret_session"
    await message.reply_text(
        "Modo secreto ativado!"
    )

@app.on_message(filters.command("normal") & filters.private)
async def normal_handler(client: Client, message: Message):
    """Mudar para session_id normal."""
    if message.from_user.id != ALLOWED_USER_ID:
        await message.reply_text("Acesso negado.")
        return

    global SESSION_ID
    SESSION_ID = "telegram_session"
    await message.reply_text(
        "Modo normal ativado!"
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
async def main():
    async with app:
        logger.info("[TELEGRAM] Registrando comandos no menu do Telegram...")
        try:
            await app.set_bot_commands([
                BotCommand("saldo", "Resumo financeiro e saldo do mês"),
                BotCommand("status", "Status do sistema e hardware do Raspberry Pi"),
                BotCommand("help", "Lista de comandos e funcionalidades"),
                BotCommand("start", "Inicia a conversa com a KaLLia"),
                BotCommand("normal", "Sessão principal de histórico"),
                BotCommand("secret", "Sessão privada temporária"),
            ])
            logger.info("[TELEGRAM] Menu de comandos registrado com sucesso!")
        except Exception as e:
            logger.error(f"[TELEGRAM] Erro ao registrar comandos no Telegram: {e}")

        logger.info("[TELEGRAM] KaLLia Telegram Bot online e operando.")
        await idle()

if __name__ == "__main__":
    logger.info("[TELEGRAM] Iniciando KaLLia Telegram Bot...")
    app.run(main())
