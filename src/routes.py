# ============ Importação ============ #
from fastapi import FastAPI, HTTPException, Request
from loguru import logger

# pyrefly: ignore [missing-import]
from src.agent import generate_response
# pyrefly: ignore [missing-import]
from src.schema import ChatRequest, ChatResponse

# ============ Inicialização ============ #
app = FastAPI(
    title="KaLLia Server API",
    description="Servidor central de IA para conversação e integrações.",
    version="3.0.0"
)


# ============ Rotas ============ #

@app.get("/")
def health_check():
    """Rota de verificação para saber se o servidor está online."""
    return {
        "status": "online",
        "agent": "KaLLia Central Server v3.0",
        "endpoints": {
            "chat": "POST /chat"
        }
    }


@app.post("/chat", response_model=ChatResponse)
def chat_endpoint(request: ChatRequest, req: Request):
    """
    Rota principal para conversar com o agente.
    Recebe a mensagem, o ID da sessão para o histórico e a imagem opcional em Base64.
    """
    # Identificação do cliente
    client_ip   = req.client.host if req.client else "desconhecido"
    client_name = req.headers.get("x-client-name", "desconhecido")

    logger.info(f"[CLIENTE] {client_name} | IP: {client_ip} | Session: '{request.session_id}'")
    logger.debug(f"Mensagem: {request.message[:50]}...")

    try:
        response_text = generate_response(
            prompt=request.message,
            image_base64=request.image_base64,
            session_id=request.session_id
        )

        return ChatResponse(response=response_text)
    except Exception as e:
        logger.error(f"Erro ao processar endpoint /chat: {e}")
        raise HTTPException(
            status_code=500,
            detail="Erro interno no servidor ao processar a resposta da IA."
        )

