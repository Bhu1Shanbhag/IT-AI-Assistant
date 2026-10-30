# 🛠️ AI-Powered IT Support Agent

An intelligent, multi-agent IT support chatbot system built with **FastAPI**, **LangChain**, **Azure OpenAI (GPT-4o)**, and **ChromaDB**. 

The system utilizes an intent-routing architecture that classifies user questions, handles general conversation, and retrieves technical solutions from a vectorized knowledge base (RAG) to provide automated troubleshooting assistance.

---

## 🌟 Key Features

- **Multi-Agent Orchestration**:
  - `ValidatoryAgent`: Evaluates user intent to route queries between smalltalk and technical troubleshooting.
  - `SmalltalkAgent`: Handles conversational greetings and general questions naturally in plain text.
  - `RetrieverAgent`: Performs similarity search on a Chroma vector database to provide step-by-step IT issue resolutions.
- **RAG Knowledge Base**: Uses Azure OpenAI embeddings (`text-embedding-ada-002`) and ChromaDB to index and retrieve technical troubleshooting guides.
- **Automated Data Ingestion**: Automatically reads raw Excel support logs/articles and embeds them into ChromaDB if the database is uninitialized.
- **Modern Web Chat UI**: Built with responsive glassmorphism dark-mode UI for seamless real-time interaction.
- **FastAPI Backend**: Fast, asynchronous REST API with CORS support.

---

## 🏗️ Architecture

```text
User Request
     │
     ▼
[FastAPI /chat]
     │
     ▼
[ValidatoryAgent] ── (Routes Query)
     ├── Smalltalk ──► [SmalltalkAgent] (AzureChatOpenAI)
     └── Technical ──► [RetrieverAgent] ──► [ChromaDB Vector Store] ──► [AzureChatOpenAI]
                                                   ▲
                                                   │ (Pre-indexed)
                                          [Knowledge Base Articles]
```

---

## 📁 Project Structure

```text
├── agent.py            # Multi-agent definitions (Validatory, Smalltalk, Retriever)
├── main.py             # Azure OpenAI & Chroma vector store setup and RAG pipeline
├── app.py              # FastAPI server and chat endpoint
├── index.html          # Web chat user interface
├── vector_db/          # Persisted Chroma vector database
├── requirements.txt    # Project dependencies
└── .gitignore          # Git exclusion rules
```

---

## 🚀 Getting Started

### 1. Prerequisites
- Python 3.10+
- An active Azure OpenAI resource with chat (`gpt-4o`) and embedding (`text-embedding-ada-002`) deployments.

### 2. Installation
Clone the repository and install required packages:
```bash
git clone https://github.com/<your-username>/<your-repo-name>.git
cd <your-repo-name>
pip install -r requirements.txt
```

### 3. Environment Configuration
Create a `.env` file in the root directory (based on `.env.example`):
```env
AOAI_CHAT_ENDPOINT=https://your-resource-name.openai.azure.com
AOAI_CHAT_KEY=your_azure_openai_key
AOAI_CHAT_DEPLOYMENT=gpt-4o
AOAI_API_VERSION_GPT=2024-08-01-preview
AOAI_EMBEDDING_DEPLOYMENT=text-embedding-ada-002
```

### 4. Running the Application
Start the FastAPI server:
```bash
python app.py
```

Open your browser and navigate to:
**[http://127.0.0.1:8000](http://127.0.0.1:8000)**

---

## 📄 License
This project is open-source and available under the [MIT License](LICENSE).
