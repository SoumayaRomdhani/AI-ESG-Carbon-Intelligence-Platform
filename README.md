# CarbonLens — ESG & Carbon Intelligence Platform

CarbonLens is a portfolio-grade AI project for ESG analysis, carbon forecasting, grounded Q&A, and automated sustainability memo generation.

This repository is designed to be:
- **ready to run locally**
- **strong for recruiters**
- **clean for GitHub**
- **good for a company demo**

## What is inside

### 1) Carbon Forecaster
Predicts the next 12 months of emissions for a company using:
- historical monthly emissions
- operational signals
- ESG metadata

### 2) ESG Report Analyzer
Analyzes ESG report text or uploaded files and produces:
- environment / social / governance scores
- greenwashing risk
- extracted commitments
- measurable KPI evidence
- red flags

### 3) ESG Copilot
A retrieval-based ESG Q&A module over:
- company profiles
- ESG notes
- greenwashing patterns
- reporting knowledge

### 4) Auto Report Generator
Generates a structured sustainability memo with sections such as:
- executive summary
- emissions overview
- ESG findings
- material risks
- recommended actions

### 5) Dashboard
A polished Streamlit interface for demo use.

### 6) FastAPI backend
Clean API endpoints, easy to plug into React or a future production stack.

## Why this project is strong

This project demonstrates:
- applied AI product thinking
- forecasting
- NLP / document intelligence
- retrieval-based assistant design
- API engineering
- dashboard UX
- containerization

It is intentionally built as a **working MVP** that runs on a normal laptop with no paid API and no GPU.

## Architecture

```text
carbonlens_portfolio/
├── backend/app/
├── dashboard_streamlit/
├── frontend_react/
├── data/
├── models_artifacts/
├── scripts/
├── tests/
├── Dockerfile.backend
├── Dockerfile.streamlit
├── docker-compose.yml
├── requirements.txt
└── .env.example
```

## Quick start

```bash
git clone <your-repo-url>
cd carbonlens_portfolio
python -m venv .venv
```

### Windows PowerShell
```powershell
.venv\Scripts\Activate.ps1
```

### Windows CMD
```cmd
.venv\Scripts\activate.bat
```

### macOS / Linux
```bash
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Generate demo data and train the forecasting artifact:

```bash
python scripts/generate_sample_data.py
python scripts/train_models.py
```

Run the backend:

```bash
uvicorn backend.app.main:app --reload --port 8000
```

Run the dashboard in another terminal:

```bash
streamlit run dashboard_streamlit/streamlit_app.py --server.port 8501
```

Open:
- API docs: `http://127.0.0.1:8000/docs`
- Dashboard: `http://127.0.0.1:8501`

## Docker

```bash
docker compose up --build
```

## Demo flow for recruiter

1. Open the dashboard and show company overview
2. Pick a company and show the 12-month emissions forecast
3. Paste an ESG report excerpt and run the analyzer
4. Ask the ESG copilot a question
5. Generate the final sustainability memo

## Honest positioning

This is a production-style MVP:
- fully runnable locally
- modular
- recruiter-friendly
- easy to upgrade later with:
  - real public ESG document ingestion
  - vector DB
  - local LLMs like Mistral / Llama 3
  - Celery / Redis
  - React/Vercel deployment

## Suggested CV bullets

- Built **CarbonLens**, an end-to-end ESG and carbon intelligence platform combining forecasting, ESG report analysis, grounded Q&A, and automated memo generation
- Developed a **FastAPI + Streamlit** architecture for a recruiter-ready AI product demo
- Implemented an ESG text analysis pipeline to score commitment quality and flag potential greenwashing patterns
- Designed a retrieval-based ESG copilot over sustainability knowledge and company data
- Containerized the application with Docker Compose and structured it for future production upgrades

## License

MIT
