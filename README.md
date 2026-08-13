# AI Data Analyst

Upload a CSV, get instant stats and charts, and ask an AI questions about your data in plain English.

## 🚀 Live Demo

**Frontend:**
https://ai-data-analyst-frontend-1wyn.onrender.com

**Backend API:**
https://ai-data-analyst-backend-hoxe.onrender.com

**API Documentation:**
https://ai-data-analyst-backend-hoxe.onrender.com/docs

---

## 🛠️ Tech Stack

* **Backend:** FastAPI, SQLAlchemy, PostgreSQL, Pandas
* **Frontend:** React (Vite), Recharts, Axios
* **AI:** Google Gemini API
* **Deployment:** Render
* **Version Control:** Git & GitHub

---

## ✨ Features

* Drag-and-drop CSV upload
* CSV files stored on disk with metadata in PostgreSQL
* Overview tab with:

  * Row and column counts
  * Data types
  * Missing values
  * Minimum, maximum, mean, and median
  * Top categorical values
  * Correlation matrix
* Data tab with paginated table preview
* Charts tab with:

  * Histograms for numerical columns
  * Bar charts for categorical columns
* Ask AI tab for natural-language questions about the dataset
* Gemini receives dataset schema, statistics, sample rows, and conversation history
* AI conversation remains available while switching between tabs
* Clear chat functionality
* Responsive interface for desktop and mobile
* Dataset selection and deletion
* Production deployment with separate frontend and backend services

---

## 🏗️ Architecture

```text
User
 │
 ▼
React + Vite Frontend
 │
 ▼
FastAPI REST API
 │
 ├──► Pandas → Data Analysis
 │
 ├──► PostgreSQL → Dataset Metadata
 │
 └──► Google Gemini → AI Questions
```

---

## 📋 Prerequisites

* Python 3.11+
* Node.js 18+
* PostgreSQL
* Google Gemini API key

A Gemini API key is only required for the **Ask AI** functionality. Other dataset analysis features work without the Gemini API.

---

## ⚙️ Setup

### 1. Database

Create the PostgreSQL database:

```bash
psql -U postgres -c "CREATE DATABASE ai_data_analyst;"
```

The application creates its required tables automatically when the backend starts.

---

### 2. Backend

Navigate to the backend:

```bash
cd backend
```

Create a virtual environment:

```bash
python -m venv .venv
```

Activate it.

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

Create:

```text
backend/.env
```

Add:

```env
DATABASE_URL=postgresql+psycopg://postgres:<your-password>@localhost:5432/ai_data_analyst
GEMINI_API_KEY=<your-gemini-key>
GEMINI_MODEL=<supported-gemini-model>
```

Run the backend:

```bash
python -m uvicorn app.main:app --reload --port 8000
```

API documentation:

```text
http://localhost:8000/docs
```

---

### 3. Frontend

Open another terminal:

```bash
cd frontend
```

Install dependencies:

```bash
npm install
```

Create the environment file.

**Windows:**

```powershell
Copy-Item .env.example .env
```

**macOS / Linux:**

```bash
cp .env.example .env
```

The local backend URL is:

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

---

## 🔌 API Overview

| Method | Endpoint                            | Description                  |
| ------ | ----------------------------------- | ---------------------------- |
| GET    | `/`                                 | API health check             |
| GET    | `/datasets`                         | List uploaded datasets       |
| POST   | `/datasets/upload`                  | Upload a CSV file            |
| DELETE | `/datasets/{id}`                    | Delete a dataset             |
| GET    | `/datasets/{id}/preview`            | Get dataset preview          |
| GET    | `/datasets/{id}/summary`            | Get statistical summary      |
| GET    | `/datasets/{id}/chart-data?column=` | Get chart-ready data         |
| POST   | `/datasets/{id}/chat`               | Ask Gemini about the dataset |

---

## 📁 Project Structure

```text
app/
├── backend/
│   ├── app/
│   │   ├── ai.py
│   │   ├── analysis.py
│   │   ├── database.py
│   │   ├── main.py
│   │   └── models.py
│   │
│   ├── datasets/
│   │   └── sample_sales_data.csv
│   │
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── App.jsx
│   │   ├── App.css
│   │   ├── api.js
│   │   └── main.jsx
│   │
│   ├── package.json
│   └── vite.config.js
│
├── docs/
│   └── AI_Data_Analyst_Technical_Documentation.docx
│
├── reports/
│   └── AI_Data_Analyst_Project_Report.pdf
│
├── screenshots/
│   ├── dashboard.png
│   ├── overview.png
│   ├── data.png
│   ├── charts.png
│   └── ask-ai.png
│
├── notebooks/
│
├── .gitignore
└── README.md
```

---

## 📚 Documentation

Detailed project documentation and the final project report are included in the repository.

### 📘 Technical Documentation

The technical documentation covers:

* System architecture
* Project structure
* Frontend components
* Backend modules
* Database integration
* Gemini integration
* Environment variables
* Deployment
* Responsive design
* Testing
* Future enhancements

Location:

```text
docs/AI_Data_Analyst_Technical_Documentation.docx
```

### 📄 Project Report

The final project report contains:

* Abstract
* Introduction
* Problem statement
* Objectives
* Proposed solution
* Features
* Technology stack
* System architecture
* Functional workflow
* Testing
* Deployment
* Challenges and solutions
* Future scope
* Conclusion

Location:

```text
reports/AI_Data_Analyst_Project_Report.pdf
```

### 📸 Screenshots

Project screenshots are available in:

```text
screenshots/
```

Recommended screenshots include:

* Dashboard
* Overview
* Data
* Charts
* Ask AI

---

## 🔐 Security

Environment files containing API keys and database credentials are excluded from Git.

Never commit:

```text
.env
.venv/
node_modules/
__pycache__/
```

Use `.env.example` files to document required environment variables without exposing secrets.

**Never expose your Gemini API key, PostgreSQL password, or production database URL in the repository.**

---

## 📱 Responsive Design

The application is designed to work on both:

* 💻 Laptop/Desktop
* 📱 Mobile

The interface includes responsive layouts, mobile-friendly CSV upload, horizontally scrollable data tables, and charts that adapt to smaller screens.

---

## 🚀 Deployment

The application is deployed using Render.

### Frontend

https://ai-data-analyst-frontend-1wyn.onrender.com

### Backend

https://ai-data-analyst-backend-hoxe.onrender.com

### API Documentation

https://ai-data-analyst-backend-hoxe.onrender.com/docs

### Production Architecture

```text
Public User
     │
     ▼
Render Frontend
     │
     ▼
Render FastAPI Backend
     │
     ├──► PostgreSQL
     │
     ├──► Pandas
     │
     └──► Google Gemini
```

> Note: The free Render instance may spin down after inactivity, which can cause a delay when the application receives its first request after being idle.

---

## 📊 Project Status

### Completed

* [x] CSV upload
* [x] PostgreSQL integration
* [x] Dataset analysis
* [x] Dataset preview
* [x] Statistical summaries
* [x] Charts and visualizations
* [x] Gemini AI integration
* [x] Ask AI chat
* [x] Persistent conversation while switching tabs
* [x] Clear chat functionality
* [x] React frontend
* [x] FastAPI backend
* [x] REST API
* [x] Responsive desktop interface
* [x] Responsive mobile interface
* [x] Production deployment
* [x] Technical documentation
* [x] Project report
* [x] Project screenshots

---

## 🔮 Future Improvements

* User accounts
* Multi-file joins
* Export-to-PDF reports directly from the application
* Saved chart dashboards
* Cloud storage
* Advanced AI-generated analysis
* More file formats such as Excel
* Advanced filtering
* Saved analysis history

---

## 👨‍💻 Project

**AI Data Analyst**

A full-stack AI-powered data analysis application built to make CSV exploration, visualization, and natural-language data analysis easier.

**GitHub:**
https://github.com/Siriyala-Nishar-10/AI-Data-Analyst

**Live Demo:**
https://ai-data-analyst-frontend-1wyn.onrender.com
