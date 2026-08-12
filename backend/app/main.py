import os
import shutil
from contextlib import asynccontextmanager

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy import text

from app import ai, analysis
from app.database import engine, init_db

DATASETS_DIR = "datasets"


@asynccontextmanager
async def lifespan(app: FastAPI):
    os.makedirs(DATASETS_DIR, exist_ok=True)
    init_db()
    yield


app = FastAPI(title="AI Data Analyst API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------- helpers ----------


def _get_dataset_or_404(dataset_id: int) -> dict:
    with engine.connect() as connection:
        result = connection.execute(
            text("SELECT * FROM datasets WHERE id = :id"), {"id": dataset_id}
        )
        row = result.fetchone()

    if not row:
        raise HTTPException(status_code=404, detail="Dataset not found")

    dataset = dict(row._mapping)
    if not os.path.exists(dataset["file_path"]):
        raise HTTPException(status_code=404, detail="Dataset file is missing on disk")

    return dataset


# ---------- schemas ----------


class ChatMessage(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    question: str
    history: list[ChatMessage] = []


# ---------- routes ----------


@app.get("/")
def home():
    return {"message": "AI Data Analyst API is running!"}


@app.get("/datasets")
def get_datasets():
    with engine.connect() as connection:
        result = connection.execute(text("SELECT * FROM datasets ORDER BY id DESC"))
        datasets = [dict(row._mapping) for row in result]
    return {"datasets": datasets}


@app.post("/datasets/upload")
def upload_dataset(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are supported")

    os.makedirs(DATASETS_DIR, exist_ok=True)
    file_path = os.path.join(DATASETS_DIR, file.filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        df = analysis.load_dataframe(file_path)
    except Exception as exc:
        os.remove(file_path)
        raise HTTPException(status_code=400, detail=f"Could not parse CSV: {exc}") from exc

    with engine.connect() as connection:
        result = connection.execute(
            text(
                """
                INSERT INTO datasets (name, filename, file_path, row_count, column_count)
                VALUES (:name, :filename, :file_path, :row_count, :column_count)
                RETURNING id, name, filename, file_path, row_count, column_count, uploaded_at
                """
            ),
            {
                "name": file.filename.rsplit(".", 1)[0],
                "filename": file.filename,
                "file_path": file_path,
                "row_count": len(df),
                "column_count": len(df.columns),
            },
        )
        dataset = result.fetchone()
        connection.commit()

    return {"message": "Dataset uploaded successfully", "dataset": dict(dataset._mapping)}


@app.delete("/datasets/{dataset_id}")
def delete_dataset(dataset_id: int):
    dataset = _get_dataset_or_404(dataset_id)

    with engine.connect() as connection:
        connection.execute(text("DELETE FROM datasets WHERE id = :id"), {"id": dataset_id})
        connection.commit()

    if os.path.exists(dataset["file_path"]):
        os.remove(dataset["file_path"])

    return {"message": "Dataset deleted"}


@app.get("/datasets/{dataset_id}/preview")
def preview_dataset(dataset_id: int, rows: int = 10):
    dataset = _get_dataset_or_404(dataset_id)
    df = analysis.load_dataframe(dataset["file_path"])

    return {
        "dataset_id": dataset_id,
        "rows": len(df),
        "columns": list(df.columns),
        "preview": analysis.dataframe_preview(df, n=rows),
    }


@app.get("/datasets/{dataset_id}/summary")
def summarize_dataset(dataset_id: int):
    dataset = _get_dataset_or_404(dataset_id)
    df = analysis.load_dataframe(dataset["file_path"])
    return {"dataset_id": dataset_id, **analysis.dataframe_summary(df)}


@app.get("/datasets/{dataset_id}/chart-data")
def chart_data(dataset_id: int, column: str, bins: int = 10):
    dataset = _get_dataset_or_404(dataset_id)
    df = analysis.load_dataframe(dataset["file_path"])

    try:
        return analysis.column_chart_data(df, column, bins=bins)
    except KeyError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/datasets/{dataset_id}/chat")
async def chat_with_dataset(dataset_id: int, request: ChatRequest):
    dataset = _get_dataset_or_404(dataset_id)
    df = analysis.load_dataframe(dataset["file_path"])
    context = analysis.build_ai_context(df, dataset["name"])

    try:
        answer = await ai.ask_about_dataset(
            context=context,
            question=request.question,
            history=[m.model_dump() for m in request.history],
        )
    except ai.AIError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    return {"answer": answer}
