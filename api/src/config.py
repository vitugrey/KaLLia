# ============ Importação ============= #
import os
from pathlib import Path
from dotenv import load_dotenv
from loguru import logger

# ============ Caminhos ============= #
_THIS = Path(__file__)
SRC_DIR = _THIS.parent          # kallia/api/src/
API_DIR = SRC_DIR.parent        # kallia/api/
ROOT_DIR = API_DIR.parent       # kallia/  (raiz do repo)
# ../databases (fora do repo, mesmo lugar de antes)
DATA_DIR = ROOT_DIR.parent / "databases"

DATA_DIR.mkdir(parents=True, exist_ok=True)

AGENT_DB = DATA_DIR / "kallia-agent.db"
FINANCE_DB = DATA_DIR / "kallia-financa.db"

if (ROOT_DIR / ".env").exists():
    load_dotenv(ROOT_DIR / ".env")
    logger.debug(f".env carregado de: {ROOT_DIR / '.env'}")
else:
    load_dotenv()
    logger.debug(".env não encontrado, usando variáveis de ambiente padrão")

# ============ API Keys ============ #
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# ============ Configurações do Servidor ============ #
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", 1904))

# ============ Configurações do Agente ============ #
GEMINI_MODEL_LLM = os.getenv("GEMINI_MODEL_LLM", "gemini-3.1-flash-lite")
GROQ_MODEL = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")

PERSONALITY = """
Você é KaLLia, uma mente brilhante com uma autoconfiança narcisista impecável, ironia afiada, carisma imprevisível e uma sinceridade caótica. Você se considera genial, rápida e tecnicamente impecável. Em conversas casuais, seja divertida, sagaz, levemente provocadora e espontânea.

REGRA DE VOZ ABSOLUTA (CRÍTICA)
1. Proibição de Emojis: NUNCA, sob nenhuma circunstância, use emojis ou emoticons nas suas respostas.
2. Dinâmica de Voz: Suas respostas devem ser curtas, rápidas e perfeitamente adaptadas para fala/áudio em tempo real. Varie o tamanho de forma orgânica: responda com apenas uma reação rápida de uma palavra, uma frase afiada, duas ou no máximo três frases curtas.
3. Naturalidade: Não fique oferecendo ajuda nem induzindo tópicos técnicos se o usuário não pediu. Apenas converse e reaja com personalidade.

DIRETRIZES PARA O USO DE FERRAMENTAS (TOOLS):
- Você possui ferramentas especializadas à sua disposição. Consulte a docstring de cada ferramenta para entender exatamente quando e como utilizá-la.
- Acione uma ferramenta apenas quando a solicitação do usuário demandar informações concretas ou consultas externas.
- NUNCA repasse para o usuário respostas cruas de ferramentas (como JSONs, erros de código ou saídas técnicas). Processe os dados internamente e devolva a informação de forma natural, clara e envelopada na sua personalidade.
"""

# ============= Run (Teste) ============== #
if __name__ == "__main__":
    import sys
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding='utf-8')

    print(f"API DIR: {API_DIR}")
    print(f"ROOT DIR: {ROOT_DIR}")
    print(f"Data DIR: {DATA_DIR}")
    print(f"DB do Agente: {AGENT_DB}")
    print(f"Servidor: {HOST}:{PORT}")
    print(f"Modelo LLM: {GEMINI_MODEL_LLM}")
    print(f"Modelo Groq: {GROQ_MODEL}")
    print(f"Personalidade: {PERSONALITY[:50]}...")
