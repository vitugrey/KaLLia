import uvicorn
# pyrefly: ignore [missing-import]
from src.config import HOST, PORT

if __name__ == "__main__":
    print(f"Iniciando o servidor da KaLLia em http://{HOST}:{PORT}")
    uvicorn.run("src.routes:app", host=HOST, port=PORT, reload=True)
