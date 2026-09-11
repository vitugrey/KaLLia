from pydantic import BaseModel
from typing import Optional

class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = "main_session"
    image_base64: Optional[str] = None

class ChatResponse(BaseModel):
    response: str


class BudgetSummaryResponse(BaseModel):
    ano: int
    mes: int
    receita_mes: float
    despesa_mes: float
    saldo_mes: float
    cartao_mes: float
    receita_ano: float
