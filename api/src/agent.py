# ============ Importação ============= #
import base64
from typing import Optional
from loguru import logger

from agno.agent import Agent
from agno.run.agent import RunStatus
from agno.db.sqlite import SqliteDb
from agno.models.google import Gemini
from agno.models.groq import Groq
from agno.media import Image

# Importações locais de configuração
# pyrefly: ignore [missing-import]
from src.config import (
    GOOGLE_API_KEY,
    GROQ_API_KEY,
    GEMINI_MODEL_LLM,
    GROQ_MODEL,
    PERSONALITY,
    AGENT_DB,
    DATA_DIR,
    FINANCE_DB,
)

# pyrefly: ignore [missing-import]
from src.tools import SQLiteTools


# ============ Banco de Dados ============ #
# Centraliza a persistência das sessões e memórias
DB = SqliteDb(
    db_file=str(AGENT_DB),
    session_table="kallia_sessions",
    memory_table="kallia_memories",
    knowledge_table="kallia_knowledge",
)


# ============ Auxiliares de Modelagem ============ #
def get_model(provider: str):
    """Retorna a instância do modelo do provedor escolhido (Gemini ou Groq)."""
    if provider == "gemini":
        if not GOOGLE_API_KEY:
            raise ValueError("GOOGLE_API_KEY não configurada no servidor.")
        return Gemini(id=GEMINI_MODEL_LLM, api_key=GOOGLE_API_KEY)
    elif provider == "groq":
        if not GROQ_API_KEY:
            raise ValueError("GROQ_API_KEY não configurada no servidor.")
        return Groq(id=GROQ_MODEL, api_key=GROQ_API_KEY, max_tokens=350)
    else:
        raise ValueError(f"Provedor de modelo desconhecido: {provider}")



# ============ Inicialização do Agente Único ============ #
def get_kallia_agent(provider: str) -> Agent:
    """
    Instancia e configura o agente único KaLLia usando o provedor especificado.
    """
    model = get_model(provider)

    kallia_agent = Agent(
        name="KaLLia",
        model=model,
        tools=[
            SQLiteTools(db_url=f"sqlite:///{FINANCE_DB}"),
        ],
        instructions=[PERSONALITY],
        db=DB,
        add_history_to_context=True,
        num_history_runs=5,
        enable_user_memories=True,
        add_memories_to_context=True,
        add_datetime_to_context=True,
        add_location_to_context=True,
        add_name_to_context=True,
        debug_mode=True,
    )

    return kallia_agent


# ============ Função de Execução Principal ============ #
def generate_response(prompt: str, image_base64: Optional[str] = None, session_id: str = "main_session") -> str:
    """
    Executa o agente único KaLLia com personalidade centralizada, histórico e persistência.
    Tenta utilizar o Gemini. Se falhar, faz o fallback automático para o Groq.
    """
    if not prompt or not prompt.strip():
        return ""

    images = []

    # Se houver imagem Base64, decodifica e salva em data/screenshot.png
    if image_base64:
        try:
            logger.debug("Decodificando imagem recebida em Base64...")
            if "," in image_base64:
                image_base64 = image_base64.split(",")[1]

            image_data = base64.b64decode(image_base64)
            screenshot_path = DATA_DIR / "screenshot.png"

            with open(screenshot_path, "wb") as f:
                f.write(image_data)

            images.append(Image(filepath=str(screenshot_path)))
            logger.info("Imagem da tela anexada com sucesso.")
        except Exception as e:
            logger.error(f"Erro ao processar imagem Base64: {e}")

    # Log de entrada da conversa
    logger.info("=" * 60)
    logger.info(f"[CONVERSA] Session_id: {session_id}")
    logger.info(f"[PROMPT] {prompt}")
    if images:
        logger.info("[IMAGEM] Screenshot anexado")

    # 1. Tentar com Gemini (Principal)
    try:
        logger.info("[MODELO] GEMINI")
        agent = get_kallia_agent("gemini")
        response = agent.run(
            input=prompt,
            session_id=session_id,
            user_id="Vitor Grey",
            images=images if images else None,
        )

        is_error = (
            getattr(response, "status", None) == RunStatus.error
            or not response.content
            or (isinstance(response.content, str) and '"error":' in response.content and '"code":' in response.content)
        )
        if is_error:
            raise RuntimeError(f"Gemini retornou erro de execução: {response.content}")

        # Registra ferramentas que foram acionadas
        if hasattr(response, "tools") and response.tools:
            for tool in response.tools:
                tool_name = getattr(tool, "tool_name", None) or getattr(tool, "name", "desconhecida")
                logger.info(f"[FERRAMENTA] Tool '{tool_name}' foi executada")

        logger.info(f"[RESPOSTA] {response.content}")
        logger.info("=" * 60)
        return response.content
    except Exception as e:
        logger.warning(
            f"Erro ao usar Gemini ({e}). Tentando fallback para Groq..."
        )

    # 2. Fallback para Groq
    try:
        logger.info("[MODELO] GROQ FALLBACK")
        agent = get_kallia_agent("groq")

        # Modelos do Groq no Agno padrão não lidam com imagens locais em run() de forma direta.
        prompt_final = prompt
        if images:
            prompt_final = (
                "[Nota do Sistema: O usuário enviou uma captura de tela, mas o modelo "
                "de fallback (Groq) não suporta visão. Por favor, desconsidere a imagem "
                "e tente ajudar apenas com base no texto.]\n\n"
                f"{prompt}"
            )

        response = agent.run(
            input=prompt_final,
            session_id=session_id,
            user_id="Vitor Grey",
        )

        is_error = (
            getattr(response, "status", None) == RunStatus.error
            or not response.content
            or (isinstance(response.content, str) and '"error":' in response.content and '"code":' in response.content)
        )
        if is_error:
            raise RuntimeError(f"Groq retornou erro de execução: {response.content}")

        # Registra ferramentas que foram acionadas (Groq)
        if hasattr(response, "tools") and response.tools:
            for tool in response.tools:
                tool_name = getattr(tool, "tool_name", None) or getattr(tool, "name", "desconhecida")
                logger.info(f"[FERRAMENTA] Tool '{tool_name}' foi executada (via Groq)")

        logger.info(f"[RESPOSTA] {response.content}")
        logger.info("=" * 60)
        return response.content
    except Exception as e:
        logger.error(
            f"Erro crítico no processamento: Gemini e Groq falharam. Detalhes: {e}"
        )
        logger.info("=" * 60)
        return "Desculpe, meus servidores de inteligência lógica (Gemini e Groq) estão offline no momento."


# ============= Execução (Teste) ============== #
if __name__ == "__main__":
    response = generate_response(
        "quero saber qual é o valor do meu patrimonio atual de investimento"
    )
    print(response)
