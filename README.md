<div align="center">
  <h1>🧠 KaLLia 🧠</h1>
  <p><i>Cérebro centralizado, multi-agente, Dashboard Touchscreen e clientes integrados para a assistente virtual KaLLia v4.2</i></p>
  
  ![Python](https://img.shields.io/badge/python-3.13-blue)
  ![Framework](https://img.shields.io/badge/agent%20framework-Agno-orange)
  ![API](https://img.shields.io/badge/api-FastAPI-green)
  ![Bot](https://img.shields.io/badge/telegram-Pyrogram-blue)
  ![Dashboard](https://img.shields.io/badge/dashboard-Touchscreen%207%22-cyan)
  ![Status](https://img.shields.io/badge/version-4.2-emerald)
</div>

---

## 🎯 Sobre o Projeto

**KaLLia** é um monorrepositório de assistente virtual inteligente em sua versão **4.2**. O projeto contém os seguintes módulos essenciais integrados:

1. **KaLLia API (`/api`)**: O cérebro centralizado construído sobre o framework [FastAPI](https://fastapi.tiangolo.com/) e o framework de agentes [Agno](https://docs.agno.com). Orquestra ferramentas de consulta a banco de dados SQLite local (finanças e memórias), monitoramento de hardware e contingência automática (fallback) entre provedores de IA.
2. **KaLLia Dashboard (`/dashboard`)**: Interface web Heads-Up Display (HUD) em fundo `#000000` puro, projetada sob medida para telas touchscreen de 7 polegadas (Raspberry Pi, tablet ou desktop ao lado do teclado). Inclui microfone com acionamento por toque único (Start/Stop), suporte multimodal com `Ctrl+V` ou anexo de fotos, síntese de fala neural, relógio em tempo real, status do sistema e card financeiro silencioso.
3. **KaLLia Telegram Bot (`/telegram`)**: Bot cliente interativo desenvolvido com [Pyrogram](https://docs.pyrogram.org/), com suporte a comandos rápidos (ex: `/saldo`), envio de fotos e imagens para análise visual, áudios e conversação contínua.
4. **KaLLia Home (`/home`)**: Em desenvolvimento para automação residencial.

---

## ✨ Novidades e Funcionalidades da Versão 4.2

### 🖥️ Dashboard Touchscreen (Interface Web Central)
- **Microfone por Toque Único (Start / Stop):** Pressione uma vez para iniciar a gravação e fale à vontade; pressione novamente para encerrar e enviar. Não é necessário segurar o botão.
- **Visão Multimodal (`Ctrl+V` & Anexo de Arquivos):** Envie capturas de tela ou fotos colando diretamente com `Ctrl+V` ou pelo botão de anexo `[🖼️]`, acompanhadas ou não de texto explicativo.
- **Voz Neural Instantânea:** Integração com Edge-TTS utilizando a voz neural feminina `pt-BR-FranciscaNeural` (latência ~300ms, sem custo de tokens e sem sobrecarregar o hardware).
- **Transcrição de Voz (STT):** AssemblyAI em português (`pt-BR`) para reconhecimento de fala com alta precisão.
- **Card de Carteira Silencioso Centralizado:** Consulta instantânea de saldo, receitas, despesas e cartão do mês, perfeitamente centralizado e com auto-dismiss após 6 segundos (sem emissão de áudio).
- **Gaveta de Texto:** Opção para digitar via teclado quando preferir silêncio.
- **Monitor de Sistema:** Exibição discreta de relógio digital, data, status de conexão da KaLLia, uso de RAM e temperatura da CPU.
- **Design Blackout Glass (`#000000`):** Visual de alto contraste, moderno e elegante, ideal para displays OLED, LCD de mesa ou tablets.

### 🛡️ Redundância e Fallback Robusto (120B)
- Se o provedor principal (Google Gemini) oscilar por limite de cota ou sobrecarga (HTTP 503), a KaLLia faz o chaveamento automático e transparente para o **Groq** utilizando o modelo **`openai/gpt-oss-120b`** (120 bilhões de parâmetros).
- Sem alucinações bobas, com suporte total a execução de ferramentas (*function calling*) e preservação da personalidade clássica da KaLLia.

### 📸 Visão Computacional no Telegram
- Suporte a fotos comprimidas e imagens sem compressão enviadas como documento.
- Processamento em memória e resposta analítica imediata da KaLLia sobre o conteúdo da imagem.

### 💰 Integração Financeira Nativa
- Conexão segura em modo leitura ao banco de dados SQLite de finanças.
- Consultas diretas via linguagem natural, comando `/saldo` no Telegram ou botão no Dashboard.

### 🧠 Memória Persistente e Sessões
- Persistência das últimas mensagens de contexto e consolidação de memórias de longo prazo via `SqliteDb` do Agno.

---

## 🛠️ Arquitetura do Repositório

```
kallia/
├── api/                  # Backend FastAPI e orquestrador de agentes Agno
│   ├── src/              # Código-fonte da API, rotas, ferramentas e fallback
│   ├── Dockerfile        # Containerização da API
│   └── pyproject.toml    # Gerenciamento de dependências com UV
├── dashboard/            # Interface Touchscreen para tela de 7" ou desktop
│   ├── src/              # Servidor FastAPI, STT (AssemblyAI) e TTS (Edge-TTS)
│   ├── static/           # HTML5, CSS3 puro (Blackout glassmorphism) e JavaScript
│   ├── Dockerfile        # Containerização do Dashboard
│   └── requirements.txt  # Dependências do dashboard
├── telegram/             # Bot do Telegram Pyrogram
│   ├── bot.py            # Código principal, comandos e handler de fotos
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
- **KaLLia Dashboard:** `http://localhost:8080`
- **Bot Telegram:** Ativo e conectado automaticamente

### 3. Modo Kiosk na Tela de 7" (Raspberry Pi / Linux)

Para abrir o Dashboard em tela cheia automática sem barras de ferramentas ou menus:
```bash
chromium-browser --kiosk --noerrdialogs --disable-infobars --check-for-update-interval=31536000 http://localhost:8080
```

---

## 📚 Tecnologias

| Módulo | Tecnologia | Propósito |
| :--- | :--- | :--- |
| **Backend API** | [FastAPI](https://fastapi.tiangolo.com/) | Rotas assíncronas `/chat`, `/status`, `/finance/saldo` |
| **Orquestração de Agentes** | [Agno](https://docs.agno.com) | Gestão de personalidade, ferramentas SQL e memórias |
| **Modelos LLM** | Gemini (`gemini-3-pro-preview`) & Groq (`openai/gpt-oss-120b`) | Raciocínio principal e contingência com 120B parâmetros |
| **Touchscreen Dashboard** | Vanilla HTML5 / CSS3 / JS + FastAPI | Interface HUD touch para Raspberry Pi 7", tablet ou desktop |
| **Síntese de Voz (TTS)** | Edge-TTS (`pt-BR-FranciscaNeural`) | Geração ultra-rápida de áudio neural falado |
| **Transcrição de Voz (STT)** | AssemblyAI (`pt-BR`) | Reconhecimento de áudio via microfone |
| **Cliente Telegram** | [Pyrogram](https://docs.pyrogram.org/) | Bot interativo móvel com comandos rápidos e visão |
| **Banco de Dados** | SQLite | Memória do agente e leitura de finanças |
| **Containerização** | Docker & Docker Compose | Ambientes isolados e replicáveis |

---

## 🎯 Roadmap

- [ ] **KaLLia Home**: Integração com automação residencial
- [ ] **KaLLia finança**: Gestão proativa e relatórios
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
      <i>Agora que vai jogar indireta sou eu vc vai ficar na mesinha de cabeça baixa e quieta, viu?</i>
    </td>
  </tr>
  <tr>
    <td>
      <img src="assets/img/imagem-real-da-kallia.ico" width="100px" />
    </td>
    <td>
      Feito por <a href="#">KaLLia 4.1</a>
    </td>
    <td>
      <i>Você me deve 10zão!</i>
    </td>
  </tr>
</table>
