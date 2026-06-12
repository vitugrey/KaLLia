# ============ Import ============= #
import sqlite3
from typing import Dict, List, Optional, Union

from agno.tools import Toolkit

# pyrefly: ignore [missing-import]
from src.config import AGENT_DB, FINANCE_DB, FINANCE_TABLES


# ============== Code =============== #
class SQLiteTools(Toolkit):
    def __init__(
            self,
            db_path: str = AGENT_DB,
            db_tables: Optional[Dict[str, Dict[str, Union[str, List[str]]]]] = None):
        super().__init__(name="SQLiteTools")
        self.db_path = db_path
        self.db_tables = db_tables
        # Registra os métodos para o Agno conseguir chamá-los como ferramentas
        self.register(self.execute_query)
        self.register(self.get_database_schema)

    def execute_query(self, query: str) -> str:
        """Executa uma query SQL de leitura em um banco de dados e retorna o resultado."""
        if not query.strip().lower().startswith("select"):
            return "Erro: Apenas consultas de leitura (SELECT) são permitidas por este agente."

        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute(query)
            columns = [description[0] for description in cursor.description]
            rows = cursor.fetchall()
            conn.close()
            if not rows:
                return "Nenhum registro encontrado para esta consulta."

            result = [dict(zip(columns, row)) for row in rows]
            return str(result)
        except Exception as e:
            return f"Erro ao executar consulta no banco: {str(e)}"

    def get_database_schema(self) -> str:
        """Retorna o schema do banco. Se as tabelas foram passadas no parâmetro,
        usa elas direto. Se não, varre o SQLite para descobrir dinamicamente."""
        if self.db_tables:
            schema_info = "Estrutura do Banco de Dados (Mapeamento Direto):\n"
            for table_name, table_data in self.db_tables.items():
                schema_info += f"- Tabela '{table_name}': Colunas -> {', '.join(table_data['colunas'])}, Contexto -> {table_data['contexto']}\n"
            return schema_info

        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()

            schema_info = "Estrutura do Banco de Dados:\n"
            for table in tables:
                table_name = table[0]
                cursor.execute(f"PRAGMA table_info({table_name});")
                columns = [f"{col[1]} ({col[2]})" for col in cursor.fetchall()]
                schema_info += f"- Tabela '{table_name}': Colunas -> {', '.join(columns)}\n"

            conn.close()
            return schema_info
        except Exception as e:
            return f"Erro ao ler o schema do banco: {str(e)}"


# ============= Run ============== #
if __name__ == "__main__":
    print(SQLiteTools(db_path=FINANCE_DB,
          db_tables=FINANCE_TABLES).get_database_schema())
