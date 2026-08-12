# AI Data Analyst

Upload a CSV, get instant stats and charts, and ask an AI questions about your data in plain English.

## Tech Stack

- **Backend:** FastAPI, SQLAlchemy, PostgreSQL, Pandas
- **Frontend:** React (Vite), Recharts, Axios
- **AI:** Google Gemini API

## Features

- Drag-and-drop CSV upload, stored on disk with metadata in PostgreSQL
- Overview tab: row/column counts, data types, missing values, min/max/mean/median, top categorical values, and correlation matrix
- Data tab: paginated table preview
- Charts tab: histograms for numeric columns and bar charts for categorical columns
- Ask AI tab: chat interface that sends the dataset schema, statistics, sample rows, and conversation history to Gemini
- AI conversation remains available while switching between tabs
- Clear chat functionality

## Prerequisites

- Python 3.11+
- Node.js 18+
- PostgreSQL running locally (or update `DATABASE_URL` to point elsewhere)
- A free Gemini API key from [Google AI Studio](https://aistudio.google.com/apikey) (only needed for the "Ask AI" tab — everything else works without it)

## Setup

### 1. Database

```bash
# create the database (adjust user/password to match backend/.env)
psql -U postgres -c "CREATE DATABASE ai_data_analyst;"
```

The app creates its own tables automatically on first run — no migrations needed.

### 2. Backend

```bash
cd backend
python -m venv .venv
```

Activate the virtual environment.

**Windows:**

```powershell
.venv\Scripts\activate
```

**macOS / Linux:**

```bash
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Create `backend/.env`:

```env
DATABASE_URL=postgresql+psycopg://postgres:<your-password>@localhost:5432/ai_data_analyst
GEMINI_API_KEY=<your-gemini-key>
GEMINI_MODEL=<supported-gemini-model>
```

Run the backend:

```bash
python -m uvicorn app.main:app --reload --port 8000
```

API docs available at:

```text
http://localhost:8000/docs
```

### 3. Frontend

```bash
cd frontend
npm install
```

Create the frontend environment file:

**Windows:**

```powershell
Copy-Item .env.example .env
```

**macOS / Linux:**

```bash
cp .env.example .env
```

The default backend URL is:

```env
VITE_API_BASE=http://localhost:8000
```

Run the frontend:

```bash
npm run dev
```

Open:

```text
http://localhost:5173
```

## API Overview

| Method | Endpoint | Description |
| ------ | -------- | ----------- |
| GET | `/` | API health check |
| GET | `/datasets` | List uploaded datasets |
| POST | `/datasets/upload` | Upload a CSV file |
| DELETE | `/datasets/{id}` | Delete a dataset |
| GET | `/datasets/{id}/preview` | First N rows |
| GET | `/datasets/{id}/summary` | Full statistical summary |
| GET | `/datasets/{id}/chart-data?column=` | Chart-ready data for one column |
| POST | `/datasets/{id}/chat` | Ask Gemini a question about the dataset |

## Project Structure

```text
app/
├── backend/
│   ├── app/
│   │   ├── ai.py
│   │   ├── analysis.py
│   │   ├── database.py
│   │   ├── main.py
│   │   └── models.py
│   ├── datasets/
│   │   └── sample_sales_data.csv
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── App.jsx
│   │   ├── App.css
│   │   ├── api.js
│   │   └── main.jsx
│   ├── package.json
│   └── vite.config.js
│
├── .gitignore
└── README.md
```

## Security

Environment files containing API keys and database credentials are excluded from Git.

Do not commit:

```text
.env
.venv/
node_modules/
__pycache__/
```

Use `.env.example` files to document required environment variables without exposing secrets.

## Project Status

Core flow (upload → analyze → visualize → chat) is fully built and tested end to end.

### Completed

- CSV upload
- PostgreSQL integration
- Dataset analysis
- Dataset preview
- Statistical summaries
- Charts and visualizations
- Gemini AI integration
- Ask AI chat
- Persistent conversation while switching tabs
- Clear chat functionality
- React frontend
- FastAPI backend
- REST API

### Future Improvements

- User accounts
- Multi-file joins
- Export-to-PDF reports
- Saved chart dashboards
- Cloud storage
- Advanced AI-generated analysis

```