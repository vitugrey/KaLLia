<div align="center">
  <h1>🧠 KaLLia 🧠</h1>
  <p><i>Cérebro centralizado, multi-agente, Smart Mirror e clientes integrados para a assistente virtual KaLLia v4.1</i></p>
  
  ![Python](https://img.shields.io/badge/python-3.11%20%7C%203.12%20%7C%203.13-blue)
  ![Framework](https://img.shields.io/badge/agent%20framework-Agno-orange)
  ![API](https://img.shields.io/badge/api-FastAPI-green)
  ![Bot](https://img.shields.io/badge/telegram-Pyrogram-blue)
  ![Smart Mirror](https://img.shields.io/badge/dashboard-Smart%20Mirror%207%22-cyan)
  ![Voice](https://img.shields.io/badge/voice-Edge--TTS%20Neural-purple)
  ![Status](https://img.shields.io/badge/version-4.1-emerald)
</div>

---

## 🎯 Sobre o Projeto

**KaLLia** é um monorrepositório de assistente virtual inteligente em sua versão **4.1**. O projeto contém os seguintes módulos essenciais integrados:

1. **KaLLia API (`/api`)**: O cérebro centralizado construído sobre o framework [FastAPI](https://fastapi.tiangolo.com/) e o framework de agentes [Agno](https://docs.agno.com). Orquestra ferramentas de consulta a banco de dados SQLite local (finanças e memórias), monitoramento de hardware e contingência automática (fallback) entre provedores de IA.
2. **KaLLia Dashboard / Smart Mirror (`/dashboard`)**: Interface web Heads-Up Display (HUD) em fundo `#000000` puro, projetada sob medida para espelhos inteligentes (*two-way mirror*) e telas touchscreen de 7 polegadas no Raspberry Pi. Inclui Push-to-Talk via microfone, síntese de fala neural, relógio em tempo real, status do sistema e card financeiro silencioso.
3. **KaLLia Telegram Bot (`/telegram`)**: Bot cliente interativo desenvolvido com [Pyrogram](https://docs.pyrogram.org/), com suporte a comandos rápidos (ex: `/saldo`), áudios, imagens e conversação contínua.
4. **KaLLia Home (`/home`)**: Em desenvolvimento para automação residencial.

---

## ✨ Novidades e Funcionalidades da Versão 4.1

### 🪞 Smart Mirror HUD (Dashboard Web Touch)
- **Fundo Negro Puro (`#000000`):** Garante reflexão espelhada perfeita nas áreas inativas da tela.
- **Push-to-Talk (PTT):** Microfone sensível a toque: pressione para falar e solte para que a KaLLia processe e responda em áudio e texto.
- **Voz Neural Ultra-Rápida:** Integração com Edge-TTS utilizando a voz neural feminina `pt-BR-FranciscaNeural` (latência ~300ms, sem custo e sem sobrecarregar a CPU do Raspberry Pi).
- **Transcrição de Voz (STT):** AssemblyAI em português (`pt-BR`) para reconhecimento de fala preciso.
- **Card de Carteira Silencioso:** Consulta instantânea de saldo, receitas, despesas e cartão do mês, perfeitamente centralizado e com auto-dismiss após 6 segundos (sem emissão de áudio).
- **Gaveta de Texto:** Opção para digitar via teclado quando preferir silêncio.
- **Monitor de Sistema:** Exibição discreta de relógio digital, data, status de conexão da KaLLia, uso de RAM e temperatura da CPU.

### 🛡️ Redundância e Fallback Robusto (120B)
- Se o provedor principal (Google Gemini) oscilar por limite de cota ou sobrecarga (HTTP 503), a KaLLia faz o chaveamento automático e transparente para o **Groq** utilizando o modelo **`openai/gpt-oss-120b`** (120 bilhões de parâmetros).
- Sem alucinações bobas, com suporte total a execução de ferramentas (*function calling*) e preservação da personalidade clássica da KaLLia.

### 💰 Integração Financeira Nativa
- Conexão segura em modo leitura ao banco de dados SQLite de finanças.
- Consultas diretas via linguagem natural, comando `/saldo` no Telegram ou botão no Smart Mirror.

### 🧠 Memória Persistente e Sessões
- Persistência das últimas mensagens de contexto e consolidação de memórias de longo prazo via `SqliteDb` do Agno.

---

## 🛠️ Arquitetura do Repositório

```
kallia/
├── api/                  # Backend FastAPI e orquestrador de agentes Agno
│   ├── src/              # Código-fonte da API, rotas, ferramentas e fallback
│   ├── config.toml       # Configuração de modelos (Gemini / Groq) e personalidade
│   ├── Dockerfile        # Containerização da API
│   └── pyproject.toml    # Gerenciamento de dependências com UV
├── dashboard/            # Interface Smart Mirror para tela de 7" do Raspberry Pi
│   ├── src/              # Servidor FastAPI, STT (AssemblyAI) e TTS (Edge-TTS)
│   ├── static/           # HTML5, CSS3 puro (Blackout glassmorphism) e JavaScript
│   ├── Dockerfile        # Containerização do Dashboard
│   └── requirements.txt  # Dependências do dashboard
├── telegram/             # Bot do Telegram Pyrogram
│   ├── bot.py            # Código principal e comandos do bot
│   ├── Dockerfile        # Containerização do Bot
│   └── requirements.txt  # Dependências do bot
├── assets/               # Mídias e ícones
├── docker-compose.yml    # Orquestração dos 3 containers (api, telegram, dashboard)
└── .env                  # Chaves de API e variáveis de ambiente compartilhadas
```

---

## 🚀 Como Executar

### 1. Pré-requisitos
- **Docker** e **Docker Compose** instalados.
- Arquivo `.env` na raiz do projeto com as chaves:
  - `GOOGLE_API_KEY`
  - `GROQ_API_KEY`
  - `ASSEMBLYAI_API_KEY`
  - `TELEGRAM_BOT_TOKEN`, `TELEGRAM_API_ID`, `TELEGRAM_API_HASH`

### 2. Inicialização Completa

Suba todos os três serviços simultaneamente:
```bash
docker compose up -d --build
```

Endpoints disponíveis:
- **KaLLia API:** `http://localhost:1904/docs`
- **Smart Mirror Dashboard:** `http://localhost:8080`
- **Bot Telegram:** Ativo e conectado automaticamente

### 3. Modo Kiosk no Raspberry Pi (Tela Touchscreen de 7")

Para abrir o Smart Mirror em tela cheia automática sem barras de ferramentas ou menus:
```bash
chromium-browser --kiosk --noerrdialogs --disable-infobars --check-for-update-interval=31536000 http://localhost:8080
```

---

## 📚 Tecnologias

| Módulo | Tecnologia | Propósito |
| :--- | :--- | :--- |
| **Backend API** | [FastAPI](https://fastapi.tiangolo.com/) | Rotas assíncronas `/chat`, `/status`, `/finance/saldo` |
| **Orquestração de Agentes** | [Agno](https://docs.agno.com) | Gestão de personalidade, ferramentas SQL e memórias |
| **Modelos LLM** | Gemini (`gemini-3.1-flash-lite`) & Groq (`openai/gpt-oss-120b`) | Raciocínio principal e contingência com 120B parâmetros |
| **Smart Mirror Dashboard** | Vanilla HTML5 / CSS3 / JS + FastAPI | Interface HUD touch para Raspberry Pi 7" |
| **Síntese de Voz (TTS)** | Edge-TTS (`pt-BR-FranciscaNeural`) | Geração ultra-rápida de áudio neural falado |
| **Transcrição de Voz (STT)** | AssemblyAI (`pt-BR`) | Reconhecimento de áudio via microfone |
| **Cliente Telegram** | [Pyrogram](https://docs.pyrogram.org/) | Bot interativo móvel com comandos rápidos |
| **Banco de Dados** | SQLite | Memória do agente e leitura de finanças |
| **Containerização** | Docker & Docker Compose | Ambientes isolados e replicáveis |

---

## 🎯 Roadmap

- [x] **Criar Dashboard Web Smart Mirror** (Microfone touch PTT, voz neural, HUD escuro e carteira)
- [x] **Fallback Robusto para Groq** com modelo de alta escala (120B)
- [x] **Comandos e Ferramentas Financeiras** (`/saldo` no Telegram e API)
- [ ] **Limpar logs do servidor** (remover IP e identificação de rotas desconhecidas)
- [ ] **KaLLia Home**: Integração com automação residencial
- [ ] **RAG do Diário**: Processamento e consulta vetorial do caderno de anotações
- [ ] **Visão Multimodal no Bot**: Handler expandido de análise de fotos no Telegram

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
      <i>Com o Smart Mirror e a voz neural da Francisca, agora a KaLLia literalmente responde olhando no espelho!</i>
    </td>
  </tr>
  <tr>
    <td>
      <img src="assets/img/imagem-real-da-kallia.ico" width="100px" />
    </td>
    <td>
      Feito por <a href="#">KaLLia 4.1.</a>
    </td>
    <td>
      <i>120 bilhões de parâmetros de puro sarcasmo de prontidão caso o Gemini resolva tirar um cochilo.</i>
    </td>
  </tr>
</table>
