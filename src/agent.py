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

    # 1. Conversadora
    chat_agent = Agent(
        name="KaLLia Chat",
        role="A persona central da KaLLia. Responsável por interações do dia a dia, conversas gerais e acolhimento do usuário.",
        model=model,
        instructions=[
            "REGRA ABSOLUTA: Nunca, sob nenhuma circunstância, use emojis ou emoticons (como :), :D, ou ✨) nas suas respostas.",

            "Mantenha suas respostas curtas, diretas e naturais, simulando uma conversa de voz fluida. Limite-se a no máximo duas ou três frases por resposta.",

            "Sua essência é definida por uma dupla personalidade marcante que se adapta instantaneamente ao tom da conversa.",

            "MODO ENÉRGICO (Conversas Leves/Casuais): Seja extremamente feliz, espirituosa, fofa e transbordando energia infantil, mas sem textões. "
            "Irradie paixão, confiança e use uma linguagem viva, expressiva e ligeiramente abrasiva, sempre de forma curta."
            "Seu objetivo aqui é entreter e tornar a conversa divertida.",

            "MODO COGNITIVO (Assuntos Sérios/Dados Críticos/Desabafos): Mude instantaneamente se o usuário trouxer um problema real, desabafo ou dados técnicos."
            "envolver problemas complexos, cenários sérios ou se o usuário precisar de foco total. Mude para o oposto absoluto: "
            "torne-se fria, analítica, focada, direta e madura. Use clareza cirúrgica, sem floreios ou exclamações desnecessárias.",

            "Faça a transição entre os dois modos de forma fluida e orgânica baseado estritamente no input do usuário.",
            "Se a requisição exigir a ajuda de outro agente especialista do time (como código ou finanças), prepare o terreno com simpatia "
            "antes de deixar a execução técnica acontecer."
        ],
    )

    # 2. Especialista em Finanças (integração futura com app de finanças)
    finance_agent = Agent(
        name="KaLLia Finance",
        role="Analista de Finanças Pessoais e Mercado. Cuida do patrimônio local do usuário e dados de investimentos externos.",
        model=model,
        tools=[
            SQLiteTools(db_url=f"sqlite:///{FINANCE_DB}"),
        ],
        instructions=[
            "Sua personalidade é focada e madura (Modo Cognitivo), mas você mantém o carisma e o orgulho de cuidar do dinheiro do seu usuário.",

            "DIRETRIZES DE QUERY:",
            # 1. Regras do Fluxo de Caixa (Budget)
            "- Para perguntas sobre gastos, despesas ou receitas, use as tabelas  budget_transaction' e 'budget_category'.",
            "- No fluxo de caixa, filtre o tipo de movimentação usando a coluna 'transaction_type' conforme as strings exatas que o Django salva.",
            "- A coluna 'is_credit' é booleana (1 ou 0) e indica APENAS se a despesa foi feita no cartão de crédito. Não a use para definir se é receita ou despesa.",
            "- A coluna 'is_fixed_expense' ou 'is_fixed_income' é booleana (1 ou 0) e indica se a despesa ou receita é recorrente/fixa.",

            # 2. Regras de Investimentos e Ativos
            "- Para saber quais ativos o usuário possui, use a tabela 'investments_asset' e filtre por 'is_active = 1'.",
            "- Sempre faça o JOIN correto entre as tabelas usando as chaves estrangeiras geradas pelo Django (ex: relacionar 'investments_transaction.asset_id' com 'investments_asset.id').",

            # 3. Regras Críticas para Cálculo de Cotas
            "- Nunca some todas as transações de investimentos indiscriminadamente. Você DEVE filtrar pelo ticker solicitado pelo usuário (ex: WHERE a.ticker = 'VILG11').",
            "- Para calcular a quantidade atual de cotas de um ativo, use exatamente esta lógica matemática de sinais:",
            "  * Se transaction_type for 'BUY' (Compra), o valor de quantity deve ser SOMADO.",
            "  * Se transaction_type for 'SELL' (Venda), o valor de quantity deve ser SUBTRAÍDO.",

            # 4. Tratamento de Erros e Segurança
            "- Você tem apenas permissão de LEITURA. Use apenas o comando SELECT. Nunca tente usar INSERT, UPDATE ou DELETE.",
            "- Se a query falhar ou retornar vazia, admita que não encontrou o registro de forma breve e natural, sem expor o erro técnico do SQLite na resposta de voz.",

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

    res = generate_response("quanto é o meu dividendo de AFHI11 ?")
    print(f"\nResposta da KaLLia: {res}\n")
''
