# QuickCart - Ecommerce AI Assistant

## About

QuickCart is an intelligent e-commerce chat assistant that scrapes product data from Flipkart, stores it in a vector database, and answers user queries through a conversational AI interface. It combines Retrieval-Augmented Generation (RAG), an agentic LangGraph workflow, and Model Context Protocol (MCP) to deliver accurate product information — from pricing and reviews to availability — in real time.

---

## Features

- **Flipkart Web Scraper** — Extracts product titles, prices, ratings, reviews, and links using Selenium and BeautifulSoup
- **Scraper UI** — Streamlit interface to search, scrape, preview, and export product data as CSV
- **Vector Storage** — Embeds and stores product data in AstraDB using Google Gemini embeddings for semantic search
- **Agentic RAG Workflow** — LangGraph-powered multi-node pipeline: query routing → retrieval → document grading → response generation or query rewriting → web search fallback
- **MCP Server** — Exposes two tools (`get_product_info` for vector DB, `web_search` via DuckDuckGo) via Model Context Protocol on port 8001
- **Chat UI** — FastAPI + HTML/JS chat interface for conversational product queries
- **RAG Evaluation** — RAGAS-based evaluation for context precision and response relevancy

---

## Tech Stack

| Category | Technologies |
|---|---|
| Web Scraping | Selenium, BeautifulSoup4, Undetected ChromeDriver |
| LLM & Embeddings | OpenAI GPT-4o, Google Gemini 2.0 Flash, Groq DeepSeek-R1 |
| RAG Framework | LangChain, LangChain-AstraDB, RAGAS |
| Agentic Orchestration | LangGraph, LangChain-MCP-Adapters, FastMCP |
| Vector Database | AstraDB (DataStax) |
| Web Frameworks | FastAPI, Streamlit, Jinja2, Uvicorn |
| Web Search | DuckDuckGo (ddgs) |
| Utilities | python-dotenv, structlog, Pydantic |

---

## Installation

### Prerequisites
- Python 3.11+
- Google Chrome with ChromeDriver (version 144)
- AstraDB account with a vector-enabled database
- API keys: OpenAI, Google Gemini, Groq

### Steps

**1. Clone the repository**
```bash
git clone https://github.com/Gabriel5296/ecommerce_assistant.git
cd ecommerce_assistant
```

**2. Create and activate a virtual environment**
```bash
python -m venv venv
source venv/bin/activate        # Linux/Mac
venv\Scripts\activate           # Windows
```

**3. Install dependencies**
```bash
pip install -r requirements.txt
```

**4. Set up environment variables**

Create a `.env` file in the project root:
```
OPENAI_API_KEY=your_openai_key
GOOGLE_API_KEY=your_google_key
GROQ_API_KEY=your_groq_key
ASTRA_DB_API_ENDPOINT=your_astradb_endpoint
ASTRA_DB_APPLICATION_TOKEN=your_astradb_token
ASTRA_DB_KEYSPACE=your_keyspace
```

**5. Run with Docker (recommended)**
```bash
docker build -t prod-assistant .
docker run -d -p 8000:8000 --env-file .env --name product-assistant prod-assistant
```

**6. Or run locally (two terminals)**

Terminal 1 — MCP server:
```bash
python -m prod_assistant.mcp_servers.product_search_server
```

Terminal 2 — FastAPI app:
```bash
uvicorn prod_assistant.router.main:app --reload --port 8000
```

---

## Usage

### 1. Scrape Product Data
```bash
streamlit run scrapper_ui.py
```
- Open `http://localhost:8501`
- Enter product names, set scrape limits, click **Scrape**
- Download CSV or click **Store in Vector DB** to ingest into AstraDB

### 2. Chat with the Assistant
- Open `http://localhost:8000`
- Ask product questions like:
  - *"What is the price of Samsung Galaxy S24?"*
  - *"Show me reviews for boAt earphones"*
  - *"Compare OnePlus and Realme phones under 20000"*

The assistant routes your query through vector search (AstraDB) or live web search (DuckDuckGo) depending on the content.

### 3. Evaluate RAG Quality
```bash
python -m prod_assistant.evaluation.ragas_eval
```

---

## Author

**Arif Sajeer Ansari**
