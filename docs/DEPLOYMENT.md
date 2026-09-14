# Deployment Guide: AGENTOPS OBSERVATORY

AGENTOPS OBSERVATORY supports two deployment modes:
1. **Local-First (Zero-Config Development)**: Uses SQLite and Python out-of-the-box with zero external database containers needed.
2. **Containerized Production**: Uses Docker Compose with PostgreSQL + pgvector, Redis, and Nginx.

---

## 1. Local-First Run

### Step 1: Start Backend
```bash
python -m uvicorn backend.main:app --reload --port 8000
```
Backend will automatically initialize the database schema in `./agentops_observatory.db`.

### Step 2: Seed Sample Data
```bash
python scripts/seed.py
```

### Step 3: Run Benchmark Suite
```bash
python -m evaluation.evaluator
```

### Step 4: Start Frontend Dashboard
```bash
cd frontend
npm install
npm run dev
```
Open [http://localhost:5173](http://localhost:5173) in your browser.

---

## 2. Docker Compose Production Run

```bash
docker compose up --build -d
```
Services started:
- `agentops-backend`: http://localhost:8000
- `agentops-frontend`: http://localhost:5173
- `agentops-postgres`: localhost:5432
- `agentops-redis`: localhost:6379
