"""Gemini-powered natural-language dataset Q&A.

This module:
- Loads GEMINI_API_KEY from backend/.env
- Uses Google's Gemini REST API
- Supports conversation history
- Provides clear errors to the FastAPI layer
- Keeps the API key on the backend only
"""

from __future__ import annotations

import os
from pathlib import Path

import httpx
from dotenv import load_dotenv


# ---------------------------------------------------------------------------
# ENVIRONMENT
# ---------------------------------------------------------------------------

# app/ai.py
#   ↑ parent = app/
#   ↑ parent.parent = backend/
BACKEND_DIR = Path(__file__).resolve().parent.parent
ENV_FILE = BACKEND_DIR / ".env"

# Explicitly load backend/.env
load_dotenv(dotenv_path=ENV_FILE, override=False)


GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()

# Use a current Flash model.
# You can override this in backend/.env.
GEMINI_MODEL = os.getenv(
    "GEMINI_MODEL",
    "gemini-3.1-flash-lite",
).strip()

GEMINI_URL = (
    f"https://generativelanguage.googleapis.com/"
    f"v1beta/models/{GEMINI_MODEL}:generateContent"
)


# ---------------------------------------------------------------------------
# SYSTEM INSTRUCTION
# ---------------------------------------------------------------------------

SYSTEM_INSTRUCTION = """
You are an AI data analyst assistant embedded in a web application.

You are given:
1. A statistical summary of a CSV dataset.
2. A few sample rows.
3. The user's question.

Answer using only the information available in the supplied dataset context.

Rules:
- Do not invent data.
- Do not make up numbers.
- If the supplied context is insufficient, clearly say that.
- Explain calculations when useful.
- Use simple, professional language.
- Use Markdown formatting where helpful.
- For numerical questions, show the relevant calculation when possible.
- For comparison questions, use a small table when useful.
- If the user asks something unrelated to the dataset, politely explain that
  you are designed to answer questions about the uploaded dataset.
""".strip()


# ---------------------------------------------------------------------------
# CUSTOM ERROR
# ---------------------------------------------------------------------------

class AIError(Exception):
    """Raised when Gemini cannot generate an answer."""

    pass


# ---------------------------------------------------------------------------
# HELPERS
# ---------------------------------------------------------------------------

def _get_api_key() -> str:
    """Return the configured Gemini API key."""

    key = os.getenv("GEMINI_API_KEY", "").strip()

    if not key:
        raise AIError(
            "GEMINI_API_KEY is not set. "
            "Add your Gemini API key to backend/.env "
            "and restart the backend."
        )

    return key


def _build_contents(
    context: str,
    question: str,
    history: list[dict] | None = None,
) -> list[dict]:
    """Build Gemini conversation contents."""

    contents: list[dict] = [
        {
            "role": "user",
            "parts": [
                {
                    "text": (
                        "Here is the dataset context you must use:\n\n"
                        f"{context}"
                    )
                }
            ],
        },
        {
            "role": "model",
            "parts": [
                {
                    "text": (
                        "Understood. I have the dataset context. "
                        "I will answer questions using only that information."
                    )
                }
            ],
        },
    ]

    # Add previous conversation turns.
    for turn in history or []:
        role = "model" if turn.get("role") == "assistant" else "user"
        content = str(turn.get("content", "")).strip()

        if not content:
            continue

        contents.append(
            {
                "role": role,
                "parts": [{"text": content}],
            }
        )

    # Current question.
    contents.append(
        {
            "role": "user",
            "parts": [{"text": question.strip()}],
        }
    )

    return contents


# ---------------------------------------------------------------------------
# GEMINI REQUEST
# ---------------------------------------------------------------------------

async def ask_about_dataset(
    context: str,
    question: str,
    history: list[dict] | None = None,
) -> str:
    """Ask Gemini a question about the uploaded dataset."""

    api_key = _get_api_key()

    if not question or not question.strip():
        raise AIError("Please enter a question.")

    if not context or not context.strip():
        raise AIError("No dataset context is available for AI analysis.")

    contents = _build_contents(
        context=context,
        question=question,
        history=history,
    )

    payload = {
        "system_instruction": {
            "parts": [
                {
                    "text": SYSTEM_INSTRUCTION,
                }
            ]
        },
        "contents": contents,
        "generationConfig": {
            "temperature": 0.2,
            "maxOutputTokens": 2048,
        },
    }

    headers = {
        "Content-Type": "application/json",
        "x-goog-api-key": api_key,
    }

    timeout = httpx.Timeout(
        connect=10.0,
        read=60.0,
        write=30.0,
        pool=10.0,
    )

    async with httpx.AsyncClient(timeout=timeout) as client:

        try:
            response = await client.post(
                GEMINI_URL,
                headers=headers,
                json=payload,
            )

        except httpx.TimeoutException as exc:
            raise AIError(
                "The Gemini API request timed out. "
                "Please try again."
            ) from exc

        except httpx.HTTPError as exc:
            raise AIError(
                f"Could not connect to the Gemini API: {exc}"
            ) from exc

    # -----------------------------------------------------------------------
    # ERROR HANDLING
    # -----------------------------------------------------------------------

    if response.status_code != 200:

        try:
            error_data = response.json()
            error_message = (
                error_data
                .get("error", {})
                .get("message", response.text)
            )
        except Exception:
            error_message = response.text

        if response.status_code == 400:
            raise AIError(
                f"Gemini rejected the request: {error_message}"
            )

        if response.status_code == 401:
            raise AIError(
                "Gemini API authentication failed. "
                "Please check your GEMINI_API_KEY."
            )

        if response.status_code == 403:
            raise AIError(
                "Gemini API access was denied. "
                "Check your API key, project permissions, and quota."
            )

        if response.status_code == 404:
            raise AIError(
                f"Gemini model '{GEMINI_MODEL}' is unavailable. "
                "Check GEMINI_MODEL in backend/.env."
            )

        if response.status_code == 429:
            raise AIError(
                "Gemini API quota or rate limit exceeded. "
                "Please wait and try again, or use a model/project "
                "with available quota."
            )

        if response.status_code >= 500:
            raise AIError(
                "Gemini is temporarily unavailable. "
                "Please try again shortly."
            )

        raise AIError(
            f"Gemini API error ({response.status_code}): "
            f"{error_message}"
        )

    # -----------------------------------------------------------------------
    # PARSE RESPONSE
    # -----------------------------------------------------------------------

    try:
        data = response.json()

        candidates = data.get("candidates", [])

        if not candidates:
            raise AIError(
                "Gemini returned no answer."
            )

        candidate = candidates[0]

        content = candidate.get("content", {})
        parts = content.get("parts", [])

        text_parts = [
            part.get("text", "")
            for part in parts
            if isinstance(part, dict)
        ]

        answer = "".join(text_parts).strip()

        if not answer:
            raise AIError(
                "Gemini returned an empty answer. "
                "Please try asking the question again."
            )

        return answer

    except AIError:
        raise

    except Exception as exc:
        raise AIError(
            f"Unexpected Gemini response: {exc}"
        ) from exc