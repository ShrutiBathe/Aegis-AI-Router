# 🚀 Aegis AI Router

> **The Operating System for Autonomous AI Agents**

Aegis AI Router is a full-stack AI orchestration platform that intelligently discovers, ranks, routes, and coordinates specialized AI agents while enabling secure pay-per-use execution using x402 micropayments.

---

# ✨ Features

- 🤖 AI Agent Discovery & Registration
- 🎯 Intelligent Agent Ranking
- 🔄 Multi-Agent Task Orchestration
- ⚡ Execution Engine
- 💳 Pay-per-Use AI Services (x402 Payments)
- 🏆 Reputation & Trust Scoring
- 🛡 Self-Healing & Failover Mechanism
- 📜 Execution History
- 📊 Analytics Dashboard
- 🔐 Secure Authentication
- 🌐 RESTful FastAPI APIs
- 📄 Interactive API Documentation (Swagger & ReDoc)

---

# 📂 Project Structure

```text
Aegis-AI-Router/
│
├── frontend/                 # React + TypeScript + Vite
│
├── backend/
│   ├── app/
│   │   ├── ai_integrations/
│   │   ├── analytics/
│   │   ├── core/
│   │   ├── database/
│   │   ├── execution/
│   │   ├── history/
│   │   ├── orchestrator/
│   │   ├── payments/
│   │   ├── reputation/
│   │   ├── self_healing/
│   │   └── main.py
│   │
│   └── requirements.txt
│
├── .gitignore
└── README.md
```

---

# 🛠 Tech Stack

## Frontend

- React
- TypeScript
- Vite
- Tailwind CSS
- React Router
- TanStack Query
- Framer Motion

## Backend

- FastAPI
- SQLAlchemy
- Pydantic
- Uvicorn
- JWT Authentication
- Async REST APIs

## AI Integrations

- Google Gemini
- OpenAI
- Claude
- Groq
- Hugging Face
- Azure OpenAI
- Ollama

## Database

- SQLAlchemy ORM
- SQLite (Development)
- PostgreSQL (Production Ready)

## Payments

- x402 Micropayments
- Algorand Integration

---

# 🧩 Backend Modules

| Module | Description |
|---------|-------------|
| AI Integrations | Supports multiple AI providers |
| Analytics | Usage analytics & insights |
| Execution Engine | Handles AI task execution |
| Orchestrator | Intelligent agent routing |
| Payments | x402 payment processing |
| Reputation | Trust & reputation scoring |
| History | Execution history management |
| Self-Healing | Retry, failover & circuit breaker |
| Database | SQLAlchemy models & sessions |
| Core | Shared dependencies & utilities |

---

# 🚀 Getting Started

## Clone Repository

```bash
git clone https://github.com/ShrutiBathe/Aegis-AI-Router.git

cd Aegis-AI-Router
```

---

# Frontend Setup

```bash
cd frontend

npm install

npm run dev
```

Frontend runs on:

```
http://localhost:5173
```

---

# Backend Setup

```bash
cd backend

python -m venv .venv
```

### Activate Virtual Environment

#### Windows

```bash
.venv\Scripts\activate
```

#### Linux/macOS

```bash
source .venv/bin/activate
```

Install dependencies

```bash
pip install -r requirements.txt
```

Run the backend

```bash
python -m uvicorn app.main:app --reload
```

Backend runs on

```
http://127.0.0.1:8000
```

---

# 📖 API Documentation

Swagger UI

```
http://127.0.0.1:8000/docs
```

ReDoc

```
http://127.0.0.1:8000/redoc
```

---

# 📡 Available API Modules

- Analytics API
- Execution Engine API
- History API
- Orchestrator API
- Payments API
- Reputation API
- Self-Healing API
- Health Check API

---

# 🔒 Environment Variables

Create a `.env` file inside the backend directory.

Example:

```env
DATABASE_URL=sqlite:///aegis_router.db
SECRET_KEY=your-secret-key
OPENAI_API_KEY=your-openai-key
GEMINI_API_KEY=your-gemini-key
GROQ_API_KEY=your-groq-key
```

> Do **not** commit your `.env` file to GitHub.

---

