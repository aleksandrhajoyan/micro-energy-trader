# ⚡ Micro Energy Trader

An autonomous, production-ready AI energy trading system for microgrids. The system fetches live weather metrics, processes them using a multi-agent **LangGraph** pipeline with **Human-in-the-Loop (HITL)** safety guardrails, stores time-series data in **TimescaleDB**, and presents real-time analytics on a **Streamlit** dashboard.

---

## 🌟 Key Features

* **Real-Time Data Ingestion:** Automatically ingests live, high-precision weather metrics (Temperature, Wind Speed, Cloud Cover, Relative Humidity) via the **Open-Meteo API** through an **n8n** automation pipeline.
* **AI Trading Agent (LangGraph):** Uses LLM-powered nodes (`gpt-4o-mini`) with strictly typed Pydantic outputs to evaluate energy supply/demand and formulate market strategies (`buy`, `sell`, `hold`).
* **Human-in-the-Loop (HITL):** Built-in risk management policy that interrupts execution for trades requiring manual validation, sending interactive single-click approval webhooks via **Telegram**.
* **Time-Series Storage:** High-performance storage of metrics and trading execution history powered by **TimescaleDB** (PostgreSQL).
* **Monitoring Dashboard:** Interactive **Streamlit** visualizer displaying live weather trends and historical AI trading actions.

---

## 🏗️ Architecture & Data Flow

```text
[ Open-Meteo API ]
       │ (Real-time Weather Data)
       ▼
   [ n8n Workflow ] ──► [ JS Payload Formatter ]
                               │
                               ▼
                        [ FastAPI App ]
                               │
            ┌──────────────────┴──────────────────┐
            ▼                                     ▼
     [ TimescaleDB ]                    [ LangGraph Agent ]
  (Store Weather Metrics)                         │
                                          (Risk Evaluation)
                                                  │
                                                  ▼
                                       [ Telegram Approval ]
                                                  │
                                            (User Clicks)
                                                  │
                                                  ▼
                                         [ Execute & Persist ]
```

---

## 🛠️ Tech Stack

| Component | Technology |
| --- | --- |
| **Data Provider** | Open-Meteo API (Live Meteorological Data) |
| **Backend API** | FastAPI, Python 3.11, Pydantic |
| **AI / Multi-Agent** | LangGraph, LangChain, OpenAI (`gpt-4o-mini`) |
| **Database** | TimescaleDB (PostgreSQL), `asyncpg` |
| **Frontend / UI** | Streamlit, Plotly |
| **Workflow Automation** | n8n (Webhooks, Scheduled Ingestion, Telegram Integration) |
| **Containerization** | Docker, Docker Compose |

---

## 🚀 Getting Started

### Prerequisites

* **Docker Desktop** (with Docker Compose)
* An **OpenAI API Key**
* *(Optional)* An **n8n** instance & **Telegram Bot Token** for full workflow automation.

### Quick Start

1. **Clone the repository:**

   ```bash
   git clone https://github.com/aleksandrhajoyan/micro-energy-trader.git
   cd micro-energy-trader
   ```

2. **Configure environment variables:**

   Copy `.env.example` to `.env` and fill in your OpenAI API Key:

   ```bash
   cp .env.example .env
   ```

3. **Build and run containers:**

   Launch all microservices (TimescaleDB, FastAPI, Streamlit) in detached mode:

   ```bash
   docker-compose up -d --build
   ```

---

## 📊 Services & Endpoints

| Service | Access URL | Description |
| --- | --- | --- |
| **Streamlit Dashboard** | `http://localhost:8505` | Real-time graphs and AI decision log |
| **FastAPI Swagger Docs** | `http://localhost:8000/docs` | Interactive API documentation |
| **TimescaleDB** | `localhost:5432` | PostgreSQL time-series database |

---

## 📁 Project Structure

```text
micro_energy_trader/
├── api/                   # FastAPI Backend & AI Agents
│   ├── main.py            # API routes and HITL endpoints
│   ├── graph.py           # LangGraph state graph & trade execution node
│   ├── database.py        # TimescaleDB connection pool & queries
│   ├── models.py          # Pydantic schema validation
│   └── Dockerfile
├── dashboard/             # Streamlit Analytics UI
│   ├── app.py             # Dashboard UI logic
│   └── Dockerfile
├── .env.example           # Template for environment variables
├── .gitignore             # Ignored tracking files (credentials, data)
└── docker-compose.yml     # Multi-container orchestrator
```
