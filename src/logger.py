import sys
from loguru import logger

# pyrefly: ignore [missing-import]
from src.config import DATA_DIR

# ============ Configuração de Logging ============ #

LOG_DIR = DATA_DIR / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)

LOG_FILE = LOG_DIR / "kallia.log"

# Formato padrão para arquivo (sem cores, com todos os detalhes)
_FILE_FORMAT = (
    "{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}"
)

# Formato legível para o terminal
_CONSOLE_FORMAT = (
    "<green>{time:HH:mm:ss}</green> | "
    "<level>{level: <8}</level> | "
    "<cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>"
)


def setup_logger():
    """
    Configura o Loguru com dois destinos:
      - Terminal: colorido, nível DEBUG
      - Arquivo:  kallia.log rotativo por dia, nível DEBUG, retido por 30 dias
    Deve ser chamado uma única vez na inicialização da aplicação.
    """
    logger.remove()  # Remove o handler padrão

    # Sink 1: Terminal
    logger.add(
        sys.stderr,
        format=_CONSOLE_FORMAT,
        level="DEBUG",
        colorize=True,
    )

    # Sink 2: Arquivo rotativo diário
    logger.add(
        str(LOG_FILE),
        format=_FILE_FORMAT,
        level="DEBUG",
        rotation="00:00",       # Novo arquivo todo dia à meia-noite
        retention="30 days",    # Mantém 30 dias de histórico
        compression="zip",      # Comprime os logs antigos
        encoding="utf-8",
        enqueue=True,           # Thread-safe (importante para o FastAPI)
    )

    logger.info(f"Logger inicializado. Arquivo de log: {LOG_FILE}")
