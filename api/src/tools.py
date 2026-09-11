# ============ Import ============= #
import sqlite3
from typing import Dict, List, Optional, Union
import json

from agno.tools.sql import SQLTools

# pyrefly: ignore [missing-import]
from src.config import AGENT_DB, FINANCE_DB


# ============== Code =============== #
class SQLiteTools(SQLTools):
    """Ferramenta para executar consultas SQL de leitura (SELECT) diretamente no banco de dados SQLite."""

    def __init__(self, db_url: str, **kwargs):
        # Desabilita list_tables e describe_table para que a LLM execute direto o run_sql_query em 1 turno só
        super().__init__(
            db_url=db_url,
            enable_list_tables=False,
            enable_describe_table=False,
            enable_run_sql_query=True,
            **kwargs,
        )

    def run_sql_query(self, query: str, limit: Optional[int] = 20) -> str:
        """Executa uma instrução SQL SELECT no banco de dados financeiro local e retorna o resultado em JSON.

        DIRETRIZES DE USO E ESQUEMA DO BANCO:
        - Use APENAS comandos SELECT. Modificações (INSERT, UPDATE, DELETE, etc.) são proibidas.
        - Não use 'SELECT *'. Especifique apenas as colunas estritamente necessárias.
        - Para somas, médias ou contagens, use funções de agregação SQL (SUM, AVG, COUNT).

        TABELAS E COLUNAS:
        1. budget_category (categorias de despesas/receitas):
           - id (int), name (str), description (str)
        2. budget_transaction (histório de gastos e receitas do orçamento):
           - id, description (str), value (decimal), date (date), is_credit (bool), is_fixed_expense (bool), is_fixed_income (bool)
           - transaction_type: 'INCOME' (receita) ou 'EXPENSE' (despesa)
           - category_id: chave estrangeira para budget_category.id
        3. investments_category (categorias de ativos):
           - id (int), name (str), description (str)
        4. investments_asset (ativos da carteira de investimentos):
           - id, ticker (ex: 'BBAS3', 'TAEE4', 'VILG11'), name (str), asset_type (str), is_active (bool, 1 para ativo), current_price (decimal)
           - category_id: chave estrangeira para investments_category.id
        5. investments_transaction (hisótico de compras e vendas de ativos):
           - id, transaction_type ('BUY' para compra, 'SELL' para venda), quantity (decimal), price (decimal), total_value (decimal), date, broker, notes, asset_id
           - CÁLCULO DE COTAS ATUAIS: Filtrar pelo ticker e calcular: SUM(CASE WHEN transaction_type = 'BUY' THEN quantity ELSE -quantity END)
           - asset_id: chave estrangeira para investments_asset.id
        6. investments_dividend (proventos e dividendos recebidos):
           - id, dividend_type, value_per_unit, total_value, ex_date, payment_date, asset_id

        Args:
            query (str): Instrução SQL SELECT pura para ser executada.
            limit (int, optional): Limite de linhas retornadas. Padrão 20.
        Returns:
            str: Dados retornados da query em formato JSON.
        """
        clean_query = query.strip().lower()

        if not clean_query.startswith("select"):
            return "Erro: Operação negada. Este agente possui apenas permissões de LEITURA (SELECT)."

        palavras_proibidas = ["insert", "update", "delete", "drop", "alter", "replace", "create table"]
        if any(palavra in clean_query for palavra in palavras_proibidas):
            return "Erro: A query contém comandos de modificação não autorizados."

        try:
            return json.dumps(self.run_sql(sql=query, limit=limit), default=str)
        except Exception as e:
            return f"Error running query: {e}"


# ============= Run ============== #
if __name__ == "__main__":
    pass
