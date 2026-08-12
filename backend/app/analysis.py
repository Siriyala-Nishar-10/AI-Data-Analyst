"""Pandas-based helpers for dataset summaries, chart data and AI context."""

import math
from typing import Any

import pandas as pd


def _clean(value: Any) -> Any:
    """Make a value JSON-safe (handles NaN/NaT/numpy types)."""
    if value is None:
        return None
    if isinstance(value, float) and math.isnan(value):
        return None
    try:
        if pd.isna(value):
            return None
    except (TypeError, ValueError):
        pass
    if hasattr(value, "item"):
        try:
            return value.item()
        except Exception:
            return str(value)
    if isinstance(value, (pd.Timestamp,)):
        return value.isoformat()
    return value


def load_dataframe(file_path: str) -> pd.DataFrame:
    df = pd.read_csv(file_path)
    return df


def dataframe_preview(df: pd.DataFrame, n: int = 10) -> list[dict]:
    records = df.head(n).to_dict(orient="records")
    return [{k: _clean(v) for k, v in row.items()} for row in records]


def dataframe_summary(df: pd.DataFrame) -> dict:
    columns = []
    for col in df.columns:
        series = df[col]
        is_numeric = pd.api.types.is_numeric_dtype(series)
        col_info: dict[str, Any] = {
            "name": col,
            "dtype": str(series.dtype),
            "is_numeric": is_numeric,
            "missing_count": int(series.isna().sum()),
            "missing_pct": round(float(series.isna().mean()) * 100, 2),
            "unique_count": int(series.nunique(dropna=True)),
        }

        if is_numeric:
            desc = series.describe()
            col_info["stats"] = {
                "min": _clean(desc.get("min")),
                "max": _clean(desc.get("max")),
                "mean": _clean(round(desc.get("mean"), 4)) if desc.get("mean") is not None else None,
                "median": _clean(series.median()),
                "std": _clean(round(desc.get("std"), 4)) if pd.notna(desc.get("std")) else None,
            }
        else:
            top_values = series.value_counts(dropna=True).head(5)
            col_info["top_values"] = [
                {"value": str(idx), "count": int(count)} for idx, count in top_values.items()
            ]

        columns.append(col_info)

    numeric_cols = df.select_dtypes(include="number").columns.tolist()
    correlation = None
    if len(numeric_cols) >= 2:
        corr_df = df[numeric_cols].corr(numeric_only=True).round(3)
        correlation = {
            "columns": numeric_cols,
            "matrix": [[_clean(v) for v in row] for row in corr_df.values.tolist()],
        }

    return {
        "row_count": int(len(df)),
        "column_count": int(len(df.columns)),
        "duplicate_rows": int(df.duplicated().sum()),
        "columns": columns,
        "correlation": correlation,
    }


def column_chart_data(df: pd.DataFrame, column: str, bins: int = 10) -> dict:
    if column not in df.columns:
        raise KeyError(f"Column '{column}' not found")

    series = df[column].dropna()
    is_numeric = pd.api.types.is_numeric_dtype(series)

    if is_numeric:
        counts, edges = pd.cut(series, bins=bins, retbins=True, duplicates="drop")
        value_counts = counts.value_counts().sort_index()
        labels = [f"{edges[i]:.2f} - {edges[i + 1]:.2f}" for i in range(len(edges) - 1)]
        data = [
            {"label": label, "value": int(value_counts.iloc[i]) if i < len(value_counts) else 0}
            for i, label in enumerate(labels)
        ]
        return {"column": column, "type": "histogram", "data": data}
    else:
        value_counts = series.value_counts().head(20)
        data = [{"label": str(idx), "value": int(count)} for idx, count in value_counts.items()]
        return {"column": column, "type": "bar", "data": data}


def build_ai_context(df: pd.DataFrame, dataset_name: str, max_sample_rows: int = 5) -> str:
    """Compact textual context describing the dataset, for prompting the AI model."""
    summary = dataframe_summary(df)

    lines = [
        f"Dataset name: {dataset_name}",
        f"Rows: {summary['row_count']}, Columns: {summary['column_count']}",
        "Column details:",
    ]
    for col in summary["columns"]:
        if col["is_numeric"]:
            stats = col.get("stats", {})
            lines.append(
                f"- {col['name']} ({col['dtype']}, numeric): "
                f"min={stats.get('min')}, max={stats.get('max')}, mean={stats.get('mean')}, "
                f"missing={col['missing_count']}"
            )
        else:
            top = ", ".join(f"{v['value']} ({v['count']})" for v in col.get("top_values", [])[:3])
            lines.append(
                f"- {col['name']} ({col['dtype']}, categorical): "
                f"unique={col['unique_count']}, missing={col['missing_count']}, top values: {top}"
            )

    lines.append("\nSample rows:")
    sample = dataframe_preview(df, n=max_sample_rows)
    for row in sample:
        lines.append(str(row))

    return "\n".join(lines)
