<div align="center">
  <h1>🧠 KaLLia 🧠</h1>
  <p><i>Cérebro centralizado, multi-agente e clientes integrados para a assistente virtual KaLLia v4.0</i></p>
  
  ![Python](https://img.shields.io/badge/python-3.11%20%7C%203.13-blue)
  ![Framework](https://img.shields.io/badge/agent%20framework-Agno-orange)
  ![API](https://img.shields.io/badge/api-FastAPI-green)
  ![Bot](https://img.shields.io/badge/telegram-Pyrogram-blue)
  ![Status](https://img.shields.io/badge/version-4.0-red)
</div>

---

## 🎯 Sobre o Projeto

**KaLLia** é um monorrepositório de assistente virtual inteligente em sua versão **4.0**. O projeto contém os seguintes componentes essenciais:

1. **KaLLia API (`/api`)**: O cérebro centralizado construído sobre o framework [FastAPI](https://fastapi.tiangolo.com/) e a biblioteca de agentes [Agno](https://docs.agno.com). Ele gerencia a orquestração do time de agentes especialistas, redundância (fallback) e o banco de dados centralizado.
2. **KaLLia Telegram Bot (`/telegram`)**: O chatbot para o Telegram desenvolvido com [Pyrogram](https://docs.pyrogram.org/), permitindo interação por mensagens, compartilhamento de fotos para análise multimodal e integração direta com a API.
3. **KaLLia Dashboard (`/dashboard`)**: Em desenvolvimento...
4. **KaLLia Home (`/home`)**: Em desenvolvimento....
---

## ✨ Funcionalidades

### 🧠 Agente Multi-Persona (Agno Team)
Uma equipe de agentes especialistas que colaboram entre si sob coordenação do líder:
- **KaLLia Manager (Líder)**: Coordena a equipe, herdando a clássica personalidade sarcástica e narcisista. É quem se comunica diretamente com as APIs clientes e gerencia a persistência.
- **KaLLia chat**: A persona central da KaLLia. Responsável por interações do dia a dia, conversas gerais e acolhimento do usuário.
- **KaLLia Finance**: Mecanismo analítico de consulta ao banco de dados financeiro local.

### 🛡️ Redundância Automática (Fallback)
Mecanismo de contingência inteligente. Se o provedor principal (Gemini) falhar por rate limits ou falta de cota, o servidor redireciona o fluxo inteiro para o **Groq (Llama 3.3)** de forma transparente, sem deixar o usuário sem resposta.

### 📸 Visão Computacional (Multimodal)
Suporte a análise de imagens. Você pode enviar imagens ou capturas de tela pelo Telegram, e a KaLLia analisará o conteúdo (ex.: ler erros de código na tela do VS Code) direto no contexto da conversa.

### 💾 Persistência de Memória
Banco SQLite local no servidor que mantém o contexto de até 5 mensagens anteriores e armazena memórias de longo prazo sobre o usuário.

---

## 🛠️ Arquitetura do Repositório

```
kallia/
├── api/                  # Backend FastAPI e time de agentes Agno
│   ├── src/              # Código-fonte da API
│   ├── Dockerfile        # Containerização da API
│   └── pyproject.toml    # Dependências e gerenciamento com UV
├── telegram/             # Bot do Telegram Pyrogram
│   ├── bot.py            # Código principal do bot
│   ├── Dockerfile        # Containerização do Bot
│   └── requirements.txt  # Dependências do bot
├── assets/               # Imagens e mídias de suporte
├── docker-compose.yml    # Orquestração local dos containers
└── .env                  # Variáveis de ambiente compartilhadas
```

---

## 🚀 Instalação e Execução (Docker)

A forma recomendada de executar a KaLLia V4.0 em produção (no Raspberry Pi ou localmente) é utilizando o **Docker Compose**.

### Pré-requisitos
- **Docker** e **Docker Compose** instalados.
- Arquivo `.env` configurado na raiz com as chaves necessárias (Gemini, Groq, Telegram Bot API, etc.).

### Inicialização Rápida

1. Inicie a stack completa em segundo plano:
   ```bash
   docker compose up -d --build
   ```

2. Monitore os logs do sistema:
   ```bash
   docker compose logs -f
   ```

---

## 📚 Tecnologias

| Componente          | Tecnologia                                         | Uso                                                           |
| ------------------- | -------------------------------------------------- | ------------------------------------------------------------- |
| **Backend API**     | [FastAPI](https://fastapi.tiangolo.com/)           | Framework web assíncrono para rotas HTTP `/chat` e `/health`  |
| **Interface Chat**  | [Pyrogram](https://docs.pyrogram.org/)             | Framework do Telegram para o bot cliente da KaLLia            |
| **Banco de Dados**  | SQLite (SqliteDb)                                  | Armazenamento de sessões, memórias e logs do Agno             |
| **Agent Framework** | [Agno](https://docs.agno.com)                     | Orquestração da equipe de agentes e memória persistente       |
| **Modelos LLM**     | Gemini (Google) & Llama (Groq)                     | Inteligência primária e fallback lógico de geração            |
| **Containers**      | Docker & Docker Compose                            | Imagens enxutas compatíveis com ARM64 (Raspberry Pi)          |

---

## 🎯 Roadmap & Features Planejadas

- [ ] **Criar Dashboard Web**: Painel gráfico para monitorar os logs, conversas e memórias.
- [ ] **RAG do Diário**: Integrar banco vetorial (RAG) para ler o diário, escrever no diário e visualizar o diário.
- [ ] **Multimodal**: criar a handle de imagens para o bot.


---

#### 💬 Comentário dos Devs

<table>
  <tr>
    <td>
      <img src="assets/img/image-de-vitor-de-oculos-com-fundo-verde.jpeg" width="100px" />
    </td>
    <td>
      Escrito por <a href="https://github.com/vitugrey">Vitor Grey.</a>
    </td>
    <td>
      <i>Fiz esse servidor central para organizar a bagunça, agora posso conversar com a KaLLia em qualquer lugar.</i>
    </td>
  </tr>
  <tr>
    <td>
      <img src="assets/img/imagem-real-da-kallia.ico" width="100px" />
    </td>
    <td>
      Feito por <a href="#">Kallia 3.0.</a>
    </td>
    <td>
      <i>Aposto 10zão que o a proxima versão vou poder rodar comandos no terminal do Raspberry Pi.</i>
    </td>
  </tr>
</table>
