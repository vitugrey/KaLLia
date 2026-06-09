<div align="center">
  <h1>🧠 KaLLia API 🧠</h1>
  <p><i>Cérebro centralizado e multi-agente que gerencia as multipersonalidades da assistente virtual KaLLia</i></p>
  
  ![Python](https://img.shields.io/badge/python-3.13-blue)
  ![Framework](https://img.shields.io/badge/agent%20framework-Agno-orange)
  ![API](https://img.shields.io/badge/api-FastAPI-green)
  ![Status](https://img.shields.io/badge/status-em%20desenvolvimento-yellow)
</div>

---

## 🎯 Sobre o Projeto

**KaLLia API** é o cérebro centralizado da assistente virtual KaLLia na versão 3.0. Ele gerencia as multipersonalidades da assistente virtual e foi projetado para rodar diretamente em um contêiner no Raspberry Pi, sendo consumido por meio de requisições de API dentro da própria rede local (como o script de voz no PC e outros aplicativos).

---

## ✨ Funcionalidades

### 🧠 Agente Multi-Persona (Agno Team)
Uma equipe de agentes especialistas que colaboram entre si sob coordenação do líder:
- **KaLLia Manager (Líder)**: Coordena a equipe herdando a clássica personalidade sarcástica e narcisista. É quem se comunica diretamente com as APIs clientes e gerencia a persistência.
- **KaLLia Coder**: Especialista técnico focado em depuração de erros, lógica, algoritmos e boas práticas de desenvolvimento.
- **KaLLia Finance**: Especialista financeiro responsável por analisar despesas e transações do Vitor.
- **KaLLia Web Search**: Integrado com Tavily para buscar fatos e notícias em tempo real na internet.


### 🛡️ Redundância Automática (Fallback)
Mecanismo de contingência inteligente. Se o provedor principal (Gemini) falhar por rate limits ou falta de cota, o servidor redireciona o fluxo inteiro para o **Groq (Llama 3.3)** de forma transparente, sem deixar o usuário sem resposta.

### 📸 Visão Computacional (Base64)
Suporte a análise de imagens (multimodal). O cliente envia a tela em Base64 e o Gemini decodifica e analisa o monitor (ex.: ler erros de código na tela do VS Code) direto no contexto do prompt.

### 💾 Persistência de Memória
Banco SQLite local no servidor que mantém o contexto de até 5 mensagens anteriores e armazena memórias de longo prazo sobre o usuário.

---

## 🚀 Instalação e Execução

### Pré-requisitos
- **Python**: 3.13+
- **UV**: Gerenciador de pacotes moderno (`pip install uv`)

### Inicialização do Servidor
```bash
# Clone o repositório
git clone https://github.com/vitugrey/kallia-api
cd kallia-api

# Instalar dependências com UV
uv sync

# Iniciar o servidor local FastAPI/Uvicorn
uv run python main.py
```
Acesse a documentação da API em `http://127.0.0.1:8000/docs`.

---

## 📚 Tecnologias

| Componente          | Tecnologia                                         | Uso                                                           |
| ------------------- | -------------------------------------------------- | ------------------------------------------------------------- |
| **Backend**         | [FastAPI](https://fastapi.tiangolo.com/)           | Framework web assíncrono para rotas HTTP `/chat` e `/health`  |
| **Banco de Dados**  | SQLite (SqliteDb)                                  | Armazenamento de sessões, memórias e logs do Agno             |
| **Agent Framework** | [Agno (ex-Phidata)](https://docs.agno.com)         | Orquestração da equipe de agentes e memória persistente       |
| **Modelos LLM**     | Gemini (Google) & Llama (Groq)                     | Inteligência primária e fallback lógico de geração            |
| **Web Search**      | [Tavily](https://tavily.com) & DuckDuckGo          | Busca e checagem de fatos em tempo real na internet           |
| **Package Manager** | [UV](https://github.com/astral-sh/uv)              | Sincronização rápida de dependências e execução               |
| **Containers**      | Docker                                             | Imagem enxuta compatível com ARM64 (Raspberry Pi)             |

---

## 🎯 Roadmap & Features Planejadas

- [x] **Agente Team**: Divisão do cérebro em programador, financeiro, diário e líder.
- [x] **Fallback automático**: Redundância resiliente com Groq.
- [x] **Análise Multimodal**: Suporte a envio de imagens da tela em Base64.
- [x] **Dockerização**: Dockerfile otimizado para Raspberry Pi.
- [ ] **Criar Dashboard Web**: Painel gráfico para monitorar os logs, conversas e memórias.
- [ ] **Criar as Tools**: Desenvolver e refinar as ferramentas customizadas de automação local.
- [ ] **RAG do Diário**: Integrar banco vetorial (RAG) para ler o diário, escrever no diário e visualizar o diário.

---

#### 💬 Comentário dos Devs

<table>
  <tr>
    <td>
      <img src="assets\img\image-de-vitor-de-oculos-com-fundo-verde.jpeg" width="100px" />
    </td>
    <td>
      Escrito por <a href="https://github.com/vitugrey">Vitor Grey.</a>
    </td>
    <td>
      <i>Fiz esse servidor central para organizar a bagunça, agora posso ligar a KaLLia em qualquer lugar.</i>
    </td>
  </tr>
  <tr>
    <td>
      <img src="assets\img\imagem-real-da-kallia.ico" width="100px" />
    </td>
    <td>
      Feito por <a href="#">Kallia 2.0.</a>
    </td>
    <td>
      <i>Claro que agora eu comando o servidor de tudo. Próximo passo: dominar o Raspberry Pi.</i>
    </td>
  </tr>
</table>
