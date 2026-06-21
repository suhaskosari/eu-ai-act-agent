# EU AI Act Compliance Agent

A LangGraph-powered agent that scans AI systems for EU AI Act compliance, classifies risk categories, identifies compliance gaps, and generates audit-ready documentation with a human-in-the-loop approval step.

## What it does

- Accepts an AI system description as input
- Classifies it under EU AI Act risk categories (Unacceptable / High / Limited / Minimal)
- Identifies specific compliance gaps based on the risk level
- Generates a formal audit document
- Stores everything in PostgreSQL with full reasoning traces
- Requires human approval before an audit is finalized

## Architecture
## Tech Stack

- **Agent framework**: LangGraph
- **API**: FastAPI
- **Database**: PostgreSQL (Docker)
- **LLM**: Llama 3.2 via Ollama (runs locally, no API cost)
- **ORM**: SQLAlchemy

## Setup

**Prerequisites**: Docker Desktop, Python 3.10+, Ollama

```bash
# Clone the repo
git clone https://github.com/suhaskosari/eu-ai-act-agent.git
cd eu-ai-act-agent

# Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Copy environment variables
cp .env.example .env

# Start PostgreSQL
docker compose up -d

# Pull the LLM
ollama pull llama3.2

# Start the server
uvicorn main:app --reload
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/scan` | Submit an AI system for compliance scanning |
| GET | `/api/v1/audit/{id}` | Get full audit details |
| POST | `/api/v1/audit/{id}/review` | Approve or reject an audit (human-in-the-loop) |
| GET | `/api/v1/audits` | List all audits |

API documentation available at `http://localhost:8000/docs`

## Example

Submit a system for scanning:

```json
POST /api/v1/scan
{
  "system_name": "HireBot AI",
  "system_description": "Automated CV screening system that ranks applicants using ML based on past hiring decisions. Used by HR without human review."
}
```

Response:
```json
{
  "audit_id": "84c50bc6-...",
  "risk_category": "HIGH",
  "compliance_gaps": ["Missing human oversight mechanism", "No technical documentation"],
  "status": "PENDING_HUMAN_REVIEW"
}
```

## Why this project exists

The EU AI Act is now in enforcement. Companies deploying AI systems — especially in hiring, credit, healthcare, and law enforcement — are legally required to classify risk, document compliance, and maintain audit trails. This agent automates that process.