# Amazon Cockpit API (Step 3)

## Endpoints
- `GET /health` → returns `{ "ok": true }`
- `GET /v1/products?limit=50&offset=0` → returns list of products (requires API key)

## Auth
Pass header `X-API-Key: <YOUR_KEY>`

## Render Setup
Create a second Web Service on Render pointing to this repo with:
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `uvicorn api:app --host 0.0.0.0 --port $PORT`

Environment variables to add on the API service:
- `DATABASE_URL` (use the **Internal Database URL** of your DB)
- `API_KEY` (set a strong random string)
