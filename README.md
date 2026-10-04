# Cloud-Based Credit Card Fraud Detection System Using Machine Learning

## Overview
A Machine Learning and Cloud-Based Framework for Real-Time Transaction Fraud Risk Prediction.
This system accepts transaction information, evaluates it using an Isotonic-Calibrated XGBoost model, and predicts whether a transaction is legitimate or potentially fraudulent, providing an accurate, calibrated fraud probability score.

## Architecture
User -> Frontend Dashboard -> FastAPI (REST) -> Calibrated XGBoost ML Model -> Prediction -> PostgreSQL Database
- **Machine Learning**: XGBClassifier with Isotonic Calibration (Trained on OpenML ID 1597)
- **Backend API**: FastAPI (Python)
- **Database**: PostgreSQL (Production/Docker) / SQLite (Local testing fallback)
- **Frontend**: HTML / Bootstrap 5 / JavaScript
- **Infrastructure**: Fully containerized with Docker and Docker Compose

## Prerequisites
- [Docker](https://www.docker.com/) and Docker Compose
- (Optional) Python 3.10+ to run natively without Docker

## Environment Variables
Copy `.env.example` to `.env` to configure your environment:
```bash
cp .env.example .env
```
**Variables:**
- `DATABASE_URL`: Connection string. Use `postgresql://fraud_user:fraud_pass@db:5432/fraud_db` for Docker. Use `sqlite:///./transactions.db` for local native development.

## 🚀 Running with Docker (Production Setup)
The entire application (FastAPI + PostgreSQL + Frontend) is orchestrated via Docker Compose.

**1. PostgreSQL Setup & Build:**
```bash
docker compose build
docker compose up -d
```
*Note: The backend is configured to wait automatically until PostgreSQL passes its healthcheck before starting.*

**2. View Logs:**
```bash
docker compose logs -f backend
docker compose logs -f db
```

**3. Access the Application:**
- Frontend Dashboard: [http://localhost:8080](http://localhost:8080)
- API Docs (Swagger): [http://localhost:8000/docs](http://localhost:8000/docs)

**4. Stop Containers:**
```bash
docker compose down
```

**5. Reset the Database:**
To wipe the PostgreSQL database completely, stop the containers and remove the volumes:
```bash
docker compose down -v
```

## Running Locally (Without Docker)
If you cannot install Docker, you can run the backend and frontend natively using SQLite.

1. **Start Backend (FastAPI):**
```bash
.\venv\Scripts\activate
set PYTHONPATH=.
uvicorn backend.main:app --host 127.0.0.1 --port 8000
```
2. **Start Frontend:**
```bash
cd frontend
python -m http.server 8080
```

## API Endpoints
- `GET /health`: System health check
- `GET /model-info`: Returns loaded ML model information
- `GET /demo/transaction?type={fraud|legitimate|random}`: Fetches 30-feature dataset examples
- `POST /predict/`: Takes a transaction and returns calibrated fraud probability
- `GET /transactions/`: Retrieves recent transaction history from the database
- `GET /statistics/`: Retrieves aggregate dashboard metrics from the database

## Actual ML Results
- **Accuracy**: 99.95%
- **Precision**: 86.96%
- **Recall**: 84.51%
- **F1-Score**: 85.71%
- **ROC-AUC**: 97.81%
- **Brier Score**: 0.00040 (Calibrated)

## Troubleshooting
- **Database Connection Error in Docker**: Ensure you are using the `postgresql://` string in `.env`.
- **"Module Not Found" locally**: Ensure you run `set PYTHONPATH=.` before starting uvicorn.

## Cloud Deployment (Render)
The repository is fully configured for automated cloud deployment via Render Blueprints.

**Production Architecture:**
```text
Cloud Architecture:
Internet -> Render Frontend (Static Site) -> Render Backend (FastAPI Docker) -> ML Model -> Render PostgreSQL Database
```

**Deployment Steps:**
1. Push this repository to GitHub/GitLab.
2. Go to your [Render Dashboard](https://dashboard.render.com/).
3. Click **New** -> **Blueprint**.
4. Connect the repository and select the automatically detected `render.yaml` file.
5. Render will automatically provision:
   - A free PostgreSQL database
   - The FastAPI backend (Docker container)
   - The Static Site frontend (with dynamic backend URL injection)
6. Once deployed, Render will provide the public URLs for both the backend and frontend.
