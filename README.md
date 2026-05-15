# Report Service

Microservice responsible for storing and serving AI-generated architecture analysis reports.

## Responsibilities
- `POST /api/v1/reports` — Internal endpoint, receives report from ai-processing-service
- `GET /api/v1/reports/{upload_id}` — Returns the full analysis report

## Architecture
Clean Architecture: Domain → Application → Infrastructure → API

## Environment Variables

| Variable | Description |
|---|---|
| `MONGODB_URL` | MongoDB connection string |
| `MONGODB_DATABASE` | Database name |
| `INTERNAL_SERVICE_TOKEN` | Token for internal service-to-service calls |

## Running locally

```bash
cp .env.example .env
pip install -r requirements.txt
uvicorn src.api.main:app --port 8003 --reload
```

## Running tests

```bash
pytest tests/ -v --cov=src
```

## API

### GET /api/v1/reports/{upload_id}
```json
{
  "report_id": "uuid",
  "upload_id": "uuid",
  "summary": "Microservices architecture with API Gateway...",
  "components": [{"name": "API Gateway", "type": "Gateway", ...}],
  "risks": [{"title": "...", "severity": "HIGH", ...}],
  "recommendations": [{"title": "...", "priority": "HIGH", ...}],
  "ai_model": "gemini-2.0-flash",
  "processing_time_seconds": 14.2,
  "created_at": "2026-05-08T10:30:45"
}
```
