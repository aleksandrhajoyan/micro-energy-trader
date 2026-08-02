# ⚡ Micro Energy Trader

An autonomous AI-powered microgrid energy trading system built with a **Human-in-the-Loop (HITL)** architecture. The system monitors weather metrics, analyzes them using LLM-based agents, and proposes energy trading strategies (Buy, Sell, Hold). All high-risk decisions are paused for human approval via Telegram before execution.

## 🌟 Key Features

*   **Automated Data Ingestion:** Weather and grid metrics are continuously ingested via an automated **n8n** workflow.
*   **AI Agent Workflow (LangGraph):** A structured LLM pipeline that analyzes metrics, determines confidence levels, and outputs strictly typed trading strategies using Pydantic.
*   **Human-in-the-Loop (HITL):** Risk-policy routing automatically pauses executions if the AI's confidence is below a certain threshold, awaiting human approval via one-click Telegram notifications.
*   **Time-Series Database:** All metrics and executed trades are securely stored in **TimescaleDB** (PostgreSQL) for high-performance querying.
*   **Real-time Dashboard:** A responsive **Streamlit** interface to monitor weather trends and review the AI agent's historical decisions.

## 🛠️ Tech Stack

| Component | Technology |
| :--- | :--- |
| **Backend API** | FastAPI, Python 3.11 |
| **AI / Multi-Agent** | LangGraph, LangChain, OpenAI (`gpt-4o-mini`) |
| **Database** | TimescaleDB (PostgreSQL), `asyncpg` |
| **Frontend / UI** | Streamlit |
| **Automation** | n8n (Workflow automation & Telegram Webhooks) |
| **Infrastructure** | Docker, Docker Compose |

## 🚀 Getting Started

### Prerequisites
*   Docker and Docker Compose
*   OpenAI API Key
*   *(Optional)* n8n instance and Telegram Bot Token for automated workflows.

### Installation

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/aleksandrhajoyan/micro-energy-trader.git](https://github.com/aleksandrhajoyan/micro-energy-trader.git)
   cd micro-energy-trader
