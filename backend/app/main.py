import base64
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
    """
    Application startup/shutdown lifecycle.
    """

    os.makedirs(DATASETS_DIR, exist_ok=True)

    # Create database tables and migrations.
    init_db()

    yield


app = FastAPI(
    title="AI Data Analyst API",
    lifespan=lifespan,
)


# ---------------------------------------------------------
# CORS
# ---------------------------------------------------------

origins = [
    "https://ai-data-analyst-frontend-1wyn.onrender.com",
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

frontend_url = os.getenv("FRONTEND_URL")

if frontend_url:
    origins.append(frontend_url)


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------
# Helpers
# ---------------------------------------------------------


def _get_dataset_or_404(dataset_id: int) -> dict:
    """
    Get a dataset from PostgreSQL.

    Dataset content can come from:
    1. Persistent PostgreSQL storage
    2. Legacy local filesystem storage
    """

    with engine.connect() as connection:

        result = connection.execute(
            text(
                """
                SELECT *
                FROM datasets
                WHERE id = :id
                """
            ),
            {"id": dataset_id},
        )

        row = result.fetchone()

    if not row:
        raise HTTPException(
            status_code=404,
            detail="Dataset not found",
        )

    dataset = dict(row._mapping)

    # New persistent storage.
    if dataset.get("file_content"):
        return dataset

    # Legacy filesystem storage.
    file_path = dataset.get("file_path")

    if file_path and os.path.exists(file_path):
        return dataset

    raise HTTPException(
        status_code=404,
        detail="Dataset content is no longer available",
    )


def _load_dataset(dataset: dict):
    """
    Load a dataset using PostgreSQL content first.

    Falls back to the old filesystem path for legacy
    datasets that still have their CSV file.
    """

    # -----------------------------------------------------
    # New persistent PostgreSQL storage
    # -----------------------------------------------------

    if dataset.get("file_content"):

        try:
            content = base64.b64decode(
                dataset["file_content"]
            )
        except Exception as exc:
            raise HTTPException(
                status_code=500,
                detail="Stored dataset content is invalid",
            ) from exc

        try:
            return analysis.load_dataframe_from_bytes(
                content
            )
        except Exception as exc:
            raise HTTPException(
                status_code=500,
                detail=f"Could not read stored dataset: {exc}",
            ) from exc

    # -----------------------------------------------------
    # Legacy filesystem storage
    # -----------------------------------------------------

    file_path = dataset.get("file_path")

    if file_path and os.path.exists(file_path):

        try:
            return analysis.load_dataframe(
                file_path
            )
        except Exception as exc:
            raise HTTPException(
                status_code=500,
                detail=f"Could not read dataset: {exc}",
            ) from exc

    raise HTTPException(
        status_code=404,
        detail="Dataset content is no longer available",
    )


# ---------------------------------------------------------
# Schemas
# ---------------------------------------------------------


class ChatMessage(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    question: str
    history: list[ChatMessage] = []


# ---------------------------------------------------------
# Routes
# ---------------------------------------------------------


@app.get("/")
def home():
    return {
        "message": "AI Data Analyst API is running!"
    }


# ---------------------------------------------------------
# Get datasets
# ---------------------------------------------------------


@app.get("/datasets")
def get_datasets():

    with engine.connect() as connection:

        result = connection.execute(
            text(
                """
                SELECT
                    id,
                    name,
                    filename,
                    file_path,
                    row_count,
                    column_count,
                    uploaded_at
                FROM datasets
                ORDER BY id DESC
                """
            )
        )

        datasets = [
            dict(row._mapping)
            for row in result
        ]

    return {
        "datasets": datasets
    }


# ---------------------------------------------------------
# Upload dataset
# ---------------------------------------------------------


@app.post("/datasets/upload")
async def upload_dataset(
    file: UploadFile = File(...),
):
    """
    Upload a CSV and persist its content in PostgreSQL.
    """

    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="Filename is required",
        )

    if not file.filename.lower().endswith(".csv"):
        raise HTTPException(
            status_code=400,
            detail="Only CSV files are supported",
        )

    # Read the complete CSV into memory.
    content = await file.read()

    if not content:
        raise HTTPException(
            status_code=400,
            detail="The uploaded CSV is empty",
        )

    # Parse CSV using Pandas.
    try:
        df = analysis.load_dataframe_from_bytes(
            content
        )

    except Exception as exc:
        raise HTTPException(
            status_code=400,
            detail=f"Could not parse CSV: {exc}",
        ) from exc

    # Encode CSV bytes for PostgreSQL TEXT storage.
    encoded_content = base64.b64encode(
        content
    ).decode("ascii")

    # Save metadata + CSV content.
    with engine.begin() as connection:

        result = connection.execute(
            text(
                """
                INSERT INTO datasets
                (
                    name,
                    filename,
                    file_path,
                    file_content,
                    row_count,
                    column_count
                )
                VALUES
                (
                    :name,
                    :filename,
                    :file_path,
                    :file_content,
                    :row_count,
                    :column_count
                )
                RETURNING
                    id,
                    name,
                    filename,
                    file_path,
                    row_count,
                    column_count,
                    uploaded_at
                """
            ),
            {
                "name": file.filename.rsplit(
                    ".",
                    1,
                )[0],
                "filename": file.filename,
                "file_path": "",
                "file_content": encoded_content,
                "row_count": len(df),
                "column_count": len(df.columns),
            },
        )

        dataset = result.fetchone()

    return {
        "message": "Dataset uploaded successfully",
        "dataset": dict(
            dataset._mapping
        ),
    }


# ---------------------------------------------------------
# Delete dataset
# ---------------------------------------------------------


@app.delete("/datasets/{dataset_id}")
def delete_dataset(
    dataset_id: int,
):
    """
    Delete a dataset from PostgreSQL.

    Also removes the old filesystem file if one exists.
    """

    # We intentionally do not require the file to exist.
    # This allows deleting old broken datasets such as ID 2.
    with engine.begin() as connection:

        result = connection.execute(
            text(
                """
                SELECT file_path
                FROM datasets
                WHERE id = :id
                """
            ),
            {"id": dataset_id},
        )

        row = result.fetchone()

        if not row:
            raise HTTPException(
                status_code=404,
                detail="Dataset not found",
            )

        file_path = row.file_path

        connection.execute(
            text(
                """
                DELETE FROM datasets
                WHERE id = :id
                """
            ),
            {"id": dataset_id},
        )

    # Remove legacy local file if it still exists.
    if file_path and os.path.exists(file_path):

        try:
            os.remove(file_path)
        except OSError:
            pass

    return {
        "message": "Dataset deleted"
    }


# ---------------------------------------------------------
# Preview
# ---------------------------------------------------------


@app.get("/datasets/{dataset_id}/preview")
def preview_dataset(
    dataset_id: int,
    rows: int = 10,
):
    """
    Return a preview of the dataset.
    """

    dataset = _get_dataset_or_404(
        dataset_id
    )

    df = _load_dataset(dataset)

    return {
        "dataset_id": dataset_id,
        "rows": len(df),
        "columns": list(df.columns),
        "preview": analysis.dataframe_preview(
            df,
            n=rows,
        ),
    }


# ---------------------------------------------------------
# Summary
# ---------------------------------------------------------


@app.get("/datasets/{dataset_id}/summary")
def summarize_dataset(
    dataset_id: int,
):
    """
    Return Pandas-based dataset summary.
    """

    dataset = _get_dataset_or_404(
        dataset_id
    )

    df = _load_dataset(dataset)

    return {
        "dataset_id": dataset_id,
        **analysis.dataframe_summary(df),
    }


# ---------------------------------------------------------
# Chart data
# ---------------------------------------------------------


@app.get("/datasets/{dataset_id}/chart-data")
def chart_data(
    dataset_id: int,
    column: str,
    bins: int = 10,
):
    """
    Generate chart data for a selected column.
    """

    dataset = _get_dataset_or_404(
        dataset_id
    )

    df = _load_dataset(dataset)

    try:

        return analysis.column_chart_data(
            df,
            column,
            bins=bins,
        )

    except KeyError as exc:

        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc


# ---------------------------------------------------------
# AI Chat
# ---------------------------------------------------------


@app.post("/datasets/{dataset_id}/chat")
async def chat_with_dataset(
    dataset_id: int,
    request: ChatRequest,
):
    """
    Ask Gemini questions about a dataset.
    """

    dataset = _get_dataset_or_404(
        dataset_id
    )

    df = _load_dataset(dataset)

    context = analysis.build_ai_context(
        df,
        dataset["name"],
    )

    try:

        answer = await ai.ask_about_dataset(
            context=context,
            question=request.question,
            history=[
                message.model_dump()
                for message in request.history
            ],
        )

    except ai.AIError as exc:

        raise HTTPException(
            status_code=502,
            detail=str(exc),
        ) from exc

    return {
        "answer": answer
    }