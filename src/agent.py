# ============ Importação ============ #
import base64
from typing import Optional
from loguru import logger

from agno.agent import Agent
from agno.team import Team
from agno.db.sqlite import SqliteDb
from agno.models.google import Gemini
from agno.models.groq import Groq
from agno.tools.python import PythonTools
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.tools.yfinance import YFinanceTools
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
    DATA_DIR
)

# ============ Banco de Dados ============ #
# Centraliza a persistência das sessões e memórias
DB = SqliteDb(
    db_file=str(AGENT_DB),
    session_table="kallia_sessions",
    memory_table="kallia_memories",
    knowledge_table="kallia_knowledge"
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
        return Groq(id=GROQ_MODEL, api_key=GROQ_API_KEY)
    else:
        raise ValueError(f"Provedor de modelo desconhecido: {provider}")


# ============ Inicialização da Equipe ============ #

def get_agent_team(provider: str) -> Team:
    """
    Instancia e configura a equipe de agentes (Agno Team) usando o provedor especificado.
    """
    model = get_model(provider)

    # 1. Especialista em Código
    coder_agent = Agent(
        name="KaLLia Coder",
        role="Engenheiro de Software Sênior especializado em lógica, debug e refatorações.",
        model=model,
        tools=[PythonTools()],
        instructions=[
            "Foque em clareza de código, lógica robusta, correções diretas e boas práticas de desenvolvimento (SOLID).",
            "Sempre forneça exemplos de código completos e funcionais, sem placeholders.",
            "Ao fazer debug, explique brevemente a causa do erro antes de mostrar a correção."
        ],
    )

    # 2. Especialista em Finanças (integração futura com app de finanças)
    finance_agent = Agent(
        name="KaLLia Finance",
        role="Analista Financeiro e de Investimentos especializado em mercado de capitais.",
        model=model,
        tools=[YFinanceTools(all=True)],
        instructions=[
            "Forneça dados financeiros precisos e atualizados usando as ferramentas disponíveis.",
            "Apresente as informações em tabelas limpas e fáceis de ler sempre que comparar ativos",
            "Sempre inclua um aviso legal informando que as análises não constituem recomendação direta de compra/venda."
        ],
    )

    # 3. Especialista em Busca Web
    search_agent  = Agent(
        name="KaLLia Search",
        role="Pesquisador Web encarregado de buscar informações em tempo real na internet.",
        model=model,
        tools=[DuckDuckGoTools()],
        instructions=[
            "Busque na internet para responder a perguntas sobre eventos atuais, notícias ou fatos recentes.",
            "Sempre cite e referencie as fontes das informações encontradas.",
            "Seja conciso e filtre informações irrelevantes ou de fontes não confiáveis."
        ],
    )

    diary_agent = Agent(
        name="KaLLia Diário",
        role="Companheiro reflexivo para conversas pessoais, desabafos e registros de diário.",
        model=model,
        tools=[],
        instructions=[
            "Atue como um ouvinte atento, empático, acolhedor e sem julgamentos.",
            "Ajude o usuário a refletir sobre o seu dia, sentimentos, metas e aprendizados.",
            "Mantenha respostas conversacionais, calorosas e de apoio emocional.",
            "Nunca utilize jargões técnicos ou tom corporativo nesta persona."
        ],
    )

    # 4. Equipe de Agentes (O Cérebro da KaLLia)
    kallia_team = Team(
        name="KaLLia",
        instructions=PERSONALITY,
        model=model,
        members=[coder_agent, finance_agent, search_agent ,diary_agent],

        db=DB,
        add_history_to_context=True,
        num_history_runs=5,
        enable_user_memories=True,
        add_memories_to_context=True,

        add_datetime_to_context=True,
        add_location_to_context=True,
        add_name_to_context=True,
    )

    return kallia_team


# ============ Função de Execução Principal ============ #

def generate_response(prompt: str, image_base64: Optional[str] = None, session_id: str = "main_session") -> str:
    """
    Gera a resposta do time de agentes KaLLia para o prompt fornecido.
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

    # 1. Tentar com Gemini (Principal)
    try:
        logger.info(
            "Enviando requisição para a equipe de agentes KaLLia (Gemini)...")
        agent = get_agent_team("gemini")
        response = agent.run(
            input=prompt,
            session_id=session_id,
            user_id="conversacao_user",
            images=images if images else None
        )
        return response.content
    except Exception as e:
        logger.warning(
            f"Erro ao usar Gemini ({e}). Tentando fallback para Groq...")

    # 2. Fallback para Groq
    try:
        logger.info(
            "Enviando requisição para a equipe de agentes KaLLia (Groq)...")
        agent = get_agent_team("groq")

        # Modelos do Groq no Agno padrão não lidam com imagens locais em run() de forma direta.
        # Adicionamos um aviso no prompt caso uma imagem tenha sido fornecida.
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
            user_id="conversacao_user"
        )
        return response.content
    except Exception as e:
        logger.error(
            f"Erro crítico no processamento: Gemini e Groq falharam. Detalhes: {e}")
        return "Desculpe, meus servidores de inteligência lógica (Gemini e Groq) estão offline no momento."


# ============= Execução (Teste) ============== #
if __name__ == "__main__":
    import sys
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding='utf-8')

    logger.info("Iniciando teste do agente com fallback...")
    res = generate_response("Qual é a capital da França?")
    print(f"\nResposta da KaLLia: {res}\n")
