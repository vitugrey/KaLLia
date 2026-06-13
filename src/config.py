# ============ Importação ============= #
import os
import toml
from pathlib import Path
from dotenv import load_dotenv
from loguru import logger

# ============ Caminhos ============= #
_THIS = Path(__file__)
SRC_DIR = _THIS.parent                     # \kallia\projetos\kallia-api\src
PROJECT_ROOT = SRC_DIR.parent              # \kallia\projetos\kallia-api
BASE_DIR = PROJECT_ROOT.parent             # \kallia\projetos
DATA_DIR = BASE_DIR / "databases"          # \kallia\projetos\databases

if DATA_DIR.exists():
    DATA_DIR.mkdir(parents=True, exist_ok=True)

AGENT_DB = DATA_DIR / "kallia-agent.db"
FINANCE_DB = DATA_DIR / "kallia-financa.db"
CONFIG_FILE = PROJECT_ROOT / "config.toml"

if (PROJECT_ROOT / ".env").exists():
    load_dotenv(PROJECT_ROOT / ".env")
    logger.debug(f".env carregado de: {PROJECT_ROOT / '.env'}")
else:
    load_dotenv()
    logger.debug(".env não encontrado, usando variáveis de ambiente padrão")


# ============ Leitura de Configurações ============= #


def _load_config() -> dict:
    if CONFIG_FILE.exists():
        try:
            return toml.load(CONFIG_FILE)
        except Exception as e:
            logger.error(f"Erro ao ler config.toml: {e}")
    logger.warning("config.toml não encontrado ou ilegível, usando padrões")
    return {}


_cfg = _load_config()
_server = _cfg.get("server", {})
_agent = _cfg.get("agent", {})

# ============ API Keys ============ #
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# ============ Configurações do Servidor ============ #
HOST = _server.get("host", "0.0.0.0")
PORT = _server.get("port", 1904)

# ============ Configurações do Agente ============ #
GEMINI_MODEL_LLM = _agent.get("gemini_model_llm", "gemini-2.5-flash")
GROQ_MODEL = _agent.get("groq_model", "llama-3.3-70b-versatile")
PERSONALITY = _agent.get("personality", "Você é um assistente virtual.")

# ============= Run (Teste) ============== #
if __name__ == "__main__":
    import sys
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding='utf-8')

    print(f"Raiz do Projeto: {PROJECT_ROOT}")
    print(f"DB do Agente: {AGENT_DB}")
    print(f"Servidor: {HOST}:{PORT}")
    print(f"Modelo LLM: {GEMINI_MODEL_LLM}")
    print(f"Personalidade: {PERSONALITY}")
