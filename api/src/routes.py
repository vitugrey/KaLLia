# ============ Importação ============ #
from fastapi import FastAPI, HTTPException, Request
from loguru import logger

# pyrefly: ignore [missing-import]
from src.agent import generate_response
# pyrefly: ignore [missing-import]
from src.schema import ChatRequest, ChatResponse, BudgetSummaryResponse
from typing import Optional
import sqlite3
from datetime import datetime
# pyrefly: ignore [missing-import]
from src.config import FINANCE_DB

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
        "agent": "KaLLia Central Server v4.0",
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
    # Identificação do cliente pelo header customizado
    client_name = req.headers.get("x-client-name", "desconhecido")

    logger.info(f"[CLIENTE] {client_name} | Session: '{request.session_id}'")
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



@app.get("/finance/saldo", response_model=BudgetSummaryResponse)
def get_budget_saldo(year: Optional[int] = None, month: Optional[int] = None):
    """
    Retorna o resumo financeiro mensal e anual:
    - Receita do mês
    - Despesas do mês
    - Saldo do mês
    - Gasto com cartão de crédito no mês
    - Receita acumulada do ano
    Consulta somente leitura e restrita ao ano/mês para performance instantânea.
    """
    now = datetime.now()
    ano = year if year else now.year
    mes = month if month else now.month
    ano_str = f"{ano:04d}"
    mes_str = f"{ano:04d}-{mes:02d}"

    try:
        conn = sqlite3.connect(f"file:{FINANCE_DB}?mode=ro", uri=True)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 
                COALESCE(SUM(CASE WHEN transaction_type = 'income' AND strftime('%Y-%m', date) = ? THEN value ELSE 0 END), 0) as receita_mes,
                COALESCE(SUM(CASE WHEN transaction_type = 'expense' AND strftime('%Y-%m', date) = ? THEN value ELSE 0 END), 0) as despesa_mes,
                COALESCE(SUM(CASE WHEN is_credit = 1 AND transaction_type = 'expense' AND strftime('%Y-%m', date) = ? THEN value ELSE 0 END), 0) as cartao_mes,
                COALESCE(SUM(CASE WHEN transaction_type = 'income' AND strftime('%Y', date) = ? THEN value ELSE 0 END), 0) as receita_ano
            FROM budget_transaction
            WHERE strftime('%Y', date) = ?
        """, (mes_str, mes_str, mes_str, ano_str, ano_str))

        row = cursor.fetchone()
        conn.close()

        rec_mes, desp_mes, cartao_mes, rec_ano = row
        saldo_mes = rec_mes - desp_mes

        return BudgetSummaryResponse(
            ano=ano,
            mes=mes,
            receita_mes=round(float(rec_mes), 2),
            despesa_mes=round(float(desp_mes), 2),
            saldo_mes=round(float(saldo_mes), 2),
            cartao_mes=round(float(cartao_mes), 2),
            receita_ano=round(float(rec_ano), 2),
        )
    except Exception as e:
        logger.error(f"Erro ao consultar saldo do budget: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao consultar banco financeiro: {e}"
        )


@app.get("/status")
def get_raspberry_status():
    import shutil
    import subprocess
    import os

    # 1. Temperatura
    temp_str = "N/A"
    if os.path.exists("/sys/class/thermal/thermal_zone0/temp"):
        try:
            with open("/sys/class/thermal/thermal_zone0/temp", "r") as f:
                temp_raw = int(f.read().strip())
                temp_str = f"{temp_raw / 1000.0:.1f}°C"
        except Exception:
            pass
    else:
        try:
            res = subprocess.run(["vcgencmd", "measure_temp"], capture_output=True, text=True, timeout=2)
            if res.returncode == 0:
                temp_str = res.stdout.strip().replace("temp=", "")
        except Exception:
            pass

    # 2. Armazenamento
    try:
        total, used, free = shutil.disk_usage("/")
        gb = 1024 ** 3
        disk_str = f"{used/gb:.1f}GB de {total/gb:.1f}GB usados ({free/gb:.1f}GB livres)"
    except Exception:
        disk_str = "N/A"

    # 3. Memória
    mem_str = "N/A"
    if os.path.exists("/proc/meminfo"):
        try:
            with open("/proc/meminfo", "r") as f:
                lines = f.readlines()
            mem_total = 0
            mem_free = 0
            for line in lines:
                if "MemTotal" in line:
                    mem_total = int(line.split()[1])
                if "MemAvailable" in line:
                    mem_free = int(line.split()[1])
            if mem_total > 0:
                mem_used = mem_total - mem_free
                mem_str = f"{mem_used // 1024}MB de {mem_total // 1024}MB usados ({mem_free // 1024}MB livres)"
        except Exception:
            pass

    # 4. Energia / Voltagem
    energia_str = "Normal / Estável (5V)"
    try:
        res = subprocess.run(["vcgencmd", "get_throttled"], capture_output=True, text=True, timeout=2)
        if res.returncode == 0:
            val = res.stdout.strip().split("=")[-1]
            if val != "0x0":
                val_int = int(val, 16)
                alerts = []
                if val_int & 0x1:
                    alerts.append("Subtensão detectada (Under-voltage)")
                if val_int & 0x2:
                    alerts.append("Arm frequency capped")
                if val_int & 0x4:
                    alerts.append("Capping limit ativo")
                if val_int & 0x8:
                    alerts.append("Soft temperature limit ativo")
                if val_int & 0x10000:
                    alerts.append("Subtensão ocorreu no passado")
                energia_str = f"Alerta ({val}): " + ", ".join(alerts) if alerts else f"Alerta ({val})"
    except Exception:
        pass

    return {
        "temperatura": temp_str,
        "memoria": mem_str,
        "armazenamento": disk_str,
        "energia": energia_str,
    }
