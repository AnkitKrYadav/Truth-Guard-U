# Backend (Flask)

Quick steps to run the backend locally.

1. Create and activate a virtual environment (PowerShell):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2. Install dependencies:

```powershell
pip install -r requirements.txt
```

3. Copy `.env.example` to `.env` and set values (if you want AI support):

```powershell
copy .env.example .env
# then edit .env to add your keys
```

4. Run the server (dev):

```powershell
python app.py
```

Production (Render):

1. Commit the root `Procfile` (already added):

```
web: cd Backend && gunicorn -w 2 -k gthread -t 60 -b 0.0.0.0:$PORT wsgi:app
```

2. Set environment variables in Render Dashboard:
	- `FLASK_DEBUG=0`
	- `GEMINI_API_KEY`, `OPENAI_API_KEY`, `NEWS_API_KEY`, `FACTCHECK_API_KEY`
	- Optional: `ALLOWED_ORIGIN` (your frontend URL), `TRENDING_TOP_TTL`, `STATS_TTL`

3. Use a persistent disk or managed DB if you need data persistence beyond deploys.

Notes:
- The API serves the built React frontend from `../Frontend/react-app/build` when available.
- `/api/verify` will use a minimal AI agent if `OPENAI_API_KEY` is set. Otherwise it falls back to simple placeholder logic.
- The SQLite DB is created under `Backend/database/news.db` and seeded with sample data if empty.
