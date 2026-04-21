# CarbonLens — ESG & Carbon Intelligence Platform

CarbonLens is an AI-powered platform for ESG analysis, carbon emissions forecasting, grounded question answering, and automated sustainability memo generation.

It is designed as a modular, production-oriented MVP that combines forecasting, document intelligence, retrieval, and API-backed analytics in a single end-to-end system.

## Overview

CarbonLens supports four core workflows:

### 1) Carbon Forecaster
Projects the next 12 months of company emissions using:
- historical monthly emissions data
- operational indicators
- ESG-related metadata

### 2) ESG Report Analyzer
Processes ESG report text or uploaded documents to identify:
- environmental, social, and governance signals
- greenwashing risk indicators
- disclosed commitments
- KPI evidence
- potential reporting gaps and red flags

### 3) ESG Copilot
A retrieval-based ESG question answering module built over:
- company profiles
- ESG notes
- reporting knowledge
- greenwashing-related patterns

### 4) Auto Report Generator
Produces a structured sustainability memo with sections such as:
- executive summary
- emissions overview
- ESG findings
- material risks
- recommended actions

## Interface and Backend

### Dashboard
A Streamlit dashboard provides an interactive interface for exploring forecasts, ESG findings, and generated outputs.

### API Layer
A FastAPI backend exposes clean service endpoints and supports future integration with external frontends or production workflows.

## Technical Scope

This project brings together:
- time-series forecasting
- NLP and document analysis
- retrieval-based question answering
- structured report generation
- API design
- dashboard development
- containerized deployment

The system is built to run locally on standard hardware without requiring paid APIs or GPU infrastructure.

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
