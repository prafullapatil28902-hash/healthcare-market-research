"""
Thin SQLite persistence layer.

The app keeps the working dataset in a SQLite database so that uploaded data
survives reruns, can be queried with SQL, and is shared across the different
analysis tabs. The schema is deliberately a single denormalised table that
mirrors the CSV — appropriate for an analytical, read-mostly workload.
"""
from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from typing import Iterator

import pandas as pd

from app.config import DATABASE_PATH, REQUIRED_COLUMNS

_TABLE = "market_data"


@contextmanager
def get_connection() -> Iterator[sqlite3.Connection]:
    """Yield a SQLite connection with row access by column name."""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db() -> None:
    """Create the ``market_data`` table if it does not already exist."""
    columns_sql = ",\n            ".join(f'"{col}" TEXT' for col in REQUIRED_COLUMNS)
    with get_connection() as conn:
        conn.execute(
            f"""
            CREATE TABLE IF NOT EXISTS {_TABLE} (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            {columns_sql}
            )
            """
        )


def save_dataframe(df: pd.DataFrame) -> int:
    """Replace the stored dataset with ``df``. Returns the row count written."""
    init_db()
    # Keep only known columns, in canonical order, to guard against stray fields.
    ordered = df[[c for c in REQUIRED_COLUMNS if c in df.columns]].copy()
    with get_connection() as conn:
        conn.execute(f"DROP TABLE IF EXISTS {_TABLE}")
        ordered.to_sql(_TABLE, conn, if_exists="replace", index=False)
    return len(ordered)


def load_dataframe() -> pd.DataFrame:
    """Load the stored dataset, or an empty DataFrame if nothing is saved yet."""
    init_db()
    with get_connection() as conn:
        try:
            df = pd.read_sql(f"SELECT * FROM {_TABLE}", conn)
        except Exception:
            return pd.DataFrame(columns=REQUIRED_COLUMNS)

    # SQLite stores everything as TEXT here; coerce numeric columns back.
    df = df.drop(columns=[c for c in ("id",) if c in df.columns], errors="ignore")
    return df


def has_data() -> bool:
    """Return True if a non-empty dataset is currently stored."""
    return not load_dataframe().empty
