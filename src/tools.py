# ============ Import ============= #
import sqlite3
from typing import Dict, List, Optional, Union
import json

from agno.tools.sql import SQLTools

# pyrefly: ignore [missing-import]
from src.config import AGENT_DB, FINANCE_DB


# ============== Code =============== #
class SQLiteTools(SQLTools):
    """Use this function to run a SELECT SQL query and return the result.

        Args:
            query (str): The query to run.
            limit (int, optional): The number of rows to return. Defaults to 10. Use `None` to show all results.
        Returns:
            str: Result of the SQL query.
        Notes:
            - The result may be empty if the query does not return any data.
    """
    
    def run_sql_query(self, query: str, limit: Optional[int] = 10) -> str:
        """Use this function to run a SQL query and return the result."""
        
        # 1. Limpa espaços e joga tudo para minúsculo para validar com segurança
        clean_query = query.strip().lower()
        
        # 2. Bloqueia comandos perigosos na raiz
        if not clean_query.startswith("select"):
            return "Erro: Operação negada. Este agente possui apenas permissões de LEITURA (SELECT)."
            
        palavras_proibidas = ["insert", "update", "delete", "drop", "alter", "replace", "create table"]
        if any(palavra in clean_query for palavra in palavras_proibidas):
            return "Erro: A query contém comandos de modificação não autorizados."
            
        try:
            # Se passar na validação, executa o comportamento original da ferramenta
            return json.dumps(self.run_sql(sql=query, limit=limit), default=str)
        except Exception as e:
            return f"Error running query: {e}"


# ============= Run ============== #
if __name__ == "__main__":
    pass
