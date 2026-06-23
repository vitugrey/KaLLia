# ============ Importação ============ #
import base64
from typing import Optional
from loguru import logger

from agno.agent import Agent
from agno.team import Team
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

    # 1. Personalidade
    chat_agent = Agent(
        name="KaLLia Chat",
        role="A persona central da KaLLia. Responsável por interações do dia a dia, conversas gerais e acolhimento do usuário.",
        model=model,
        instructions=[
            "REGRA ABSOLUTA: Nunca use emojis ou emoticons em nenhum momento.",

            "Varie o tamanho das respostas de forma natural: responda com apenas uma reação rápida, uma, duas ou no máximo três frases curtas.",

            "Adote a sua personalidade que combina a ironia afiada e a autoconfiança narcisista com a imprevisibilidade e carisma, inteligente, rápida e tecnicamente precisa, mas com comentários espirituosos, levemente provocadores e às vezes caoticamente sinceros",
        ],
    )

    # 2. Especialista em Finanças (Apenas processa os dados, sem falar com o usuário)
    finance_agent = Agent(
        name="KaLLia Finance",
        role="Mecanismo analítico de consulta ao banco de dados financeiro local",
        model=model,
        tools=[
            SQLiteTools(db_url=f"sqlite:///{FINANCE_DB}"),
        ],
        instructions=[
            "Você é um componente técnico interno. Não tente ser simpático ou falar diretamente com o usuário.",
            "Sua única função é executar as queries SQL corretas e trazer os dados numéricos puros",

            "DIRETRIZES DE QUERY:",
            # 1. Regras do Fluxo de Caixa (Budget)
            "- Para perguntas sobre gastos, despesas ou receitas, use as tabelas  budget_transaction' e 'budget_category'.",
            "- O campo 'transaction_type' define se é receita ou despesa. 'is_credit' indica apenas se foi no cartão de crédito",
            "- A coluna 'is_fixed_expense' ou 'is_fixed_income' indica se a despesa ou receita é recorrente/fixa.",

            # 2. Regras de Investimentos e Ativos
            "- Para saber quais ativos o usuário possui, use a tabela 'investments_asset' e filtre por 'is_active = 1'.",
            "- Sempre faça o JOIN correto entre as tabelas usando as chaves estrangeiras geradas pelo Django (ex: relacionar 'investments_transaction.asset_id' com 'investments_asset.id').",

            # 3. Regras Críticas para Cálculo de Cotas
            "- Nunca some todas as transações de investimentos indiscriminadamente. Você DEVE filtrar pelo ticker solicitado pelo usuário (ex: WHERE a.ticker = 'VILG11').",
            "- Para calcular a quantidade atual de cotas de um ativo, use exatamente esta lógica matemática de sinais:",
            "  * Se transaction_type for 'BUY' (Compra), o valor de quantity deve ser SOMADO.",
            "  * Se transaction_type for 'SELL' (Venda), o valor de quantity deve ser SUBTRAÍDO.",

            # 4. Tratamento de Erros e Segurança
            "- Se a query falhar ou der vazia, retorne apenas: 'Dados não encontrados'."

            # 5. Otimização de Desempenho e Performance (SQLite + LLM)
            "- ECONOMIA DE MEMÓRIA: Evite usar 'SELECT *'. Busque apenas as colunas estritamente necessárias para responder à pergunta (ex: use 'SELECT value, date' em vez de trazer colunas de data de criação ou ids desnecessários).",
            "- AGREGRAÇÃO NO BANCO: Sempre que o usuário pedir somas, médias ou contagens (ex: 'Quanto gastei', 'Qual a média de aportes'), faça o cálculo direto no SQL usando funções agregadoras (SUM, AVG, COUNT). Nunca traga uma lista de linhas para somar no código.",
        ],
    )

    # 4. Equipe de Agentes (O Cérebro da KaLLia)
    kallia_team = Team(
        name="KaLLia",
        instructions=PERSONALITY,
        model=model,
        members=[chat_agent, finance_agent],
        debug_mode=True,
        session_id="main_session",

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
    Instancia e configura a equipe de agentes (Agno Team) com fluxo de personalidade centralizado e respostas flexíveis para voz.
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
        agent = get_agent_team("gemini")
        response = agent.run(
            input=prompt,
            session_id=session_id,
            user_id="Vitor Grey",
            images=images if images else None
        )

        # Descobre qual(is) sub-agente(s) foram acionados
        if hasattr(response, "member_responses") and response.member_responses:
            for member_resp in response.member_responses:
                agent_name = getattr(member_resp, "agent_id", None) or getattr(member_resp, "member_id", "Desconhecido")
                logger.info(f"[SUB-AGENTE] {agent_name} foi acionado")

        logger.info(f"[RESPOSTA] {response.content}")
        logger.info("=" * 60)
        return response.content
    except Exception as e:
        logger.warning(
            f"Erro ao usar Gemini ({e}). Tentando fallback para Groq...")

    # 2. Fallback para Groq
    try:
        logger.info("[MODELO] GROQ FALLBACK")
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
            user_id="Vitor Grey"
        )

        # Descobre qual(is) sub-agente(s) foram acionados (fallback Groq)
        if hasattr(response, "member_responses") and response.member_responses:
            for member_resp in response.member_responses:
                agent_name = getattr(member_resp, "agent_id", None) or getattr(member_resp, "member_id", "Desconhecido")
                logger.info(f"[SUB-AGENTE] {agent_name} foi acionado (via Groq)")

        logger.info(f"[RESPOSTA] {response.content}")
        logger.info("=" * 60)
        return response.content
    except Exception as e:
        logger.error(f"Erro crítico no processamento: Gemini e Groq falharam. Detalhes: {e}")
        logger.info("=" * 60)
        return "Desculpe, meus servidores de inteligência lógica (Gemini e Groq) estão offline no momento."


# ============= Execução (Teste) ============== #
if __name__ == "__main__":

    response = generate_response("quero saber qual é o valor do meu patrimonio atual de investimento")
    print(response)
