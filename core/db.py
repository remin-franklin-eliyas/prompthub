import sqlite3
from datetime import datetime
from pathlib import Path
from models.schemas import Prompt, Version, TestCase

DB_PATH = Path(".prompthub/prompthub.db")


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    DB_PATH.parent.mkdir(exist_ok=True)
    conn = get_connection()
    cursor = conn.cursor()

    cursor.executescript("""
        CREATE TABLE IF NOT EXISTS prompts (
            id          INTEGER PRIMARY KEY,
            name        TEXT NOT NULL UNIQUE,
            filepath    TEXT NOT NULL,
            created_at  DATETIME DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS versions (
            id            INTEGER PRIMARY KEY,
            prompt_id     INTEGER NOT NULL REFERENCES prompts(id),
            version_tag   TEXT NOT NULL,
            content       TEXT NOT NULL,
            message       TEXT NOT NULL,
            embedding     BLOB,
            committed_at  DATETIME DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(prompt_id, version_tag)
        );

        CREATE TABLE IF NOT EXISTS test_cases (
            id          INTEGER PRIMARY KEY,
            prompt_id   INTEGER NOT NULL REFERENCES prompts(id),
            name        TEXT NOT NULL,
            input       TEXT NOT NULL,
            created_at  DATETIME DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS test_results (
            id           INTEGER PRIMARY KEY,
            version_id   INTEGER NOT NULL REFERENCES versions(id),
            test_case_id INTEGER NOT NULL REFERENCES test_cases(id),
            output       TEXT NOT NULL,
            model        TEXT NOT NULL,
            ran_at       DATETIME DEFAULT CURRENT_TIMESTAMP
        );
    """)

    conn.commit()
    conn.close()


def add_prompt(name: str, filepath: str) -> Prompt:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO prompts (name, filepath) VALUES (?, ?)",
        (name, filepath)
    )
    conn.commit()
    row = cursor.execute(
        "SELECT * FROM prompts WHERE id = ?", (cursor.lastrowid,)
    ).fetchone()
    conn.close()
    return Prompt(**dict(row))


def get_prompt(name: str) -> Prompt | None:
    conn = get_connection()
    row = conn.execute(
        "SELECT * FROM prompts WHERE name = ?", (name,)
    ).fetchone()
    conn.close()
    return Prompt(**dict(row)) if row else None


def get_all_prompts() -> list[Prompt]:
    conn = get_connection()
    rows = conn.execute("SELECT * FROM prompts").fetchall()
    conn.close()
    return [Prompt(**dict(r)) for r in rows]


def add_version(
    prompt_id: int,
    version_tag: str,
    content: str,
    message: str,
    embedding: bytes | None = None
) -> Version:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """INSERT INTO versions (prompt_id, version_tag, content, message, embedding)
           VALUES (?, ?, ?, ?, ?)""",
        (prompt_id, version_tag, content, message, embedding)
    )
    conn.commit()
    row = cursor.execute(
        "SELECT * FROM versions WHERE id = ?", (cursor.lastrowid,)
    ).fetchone()
    conn.close()
    return Version(**dict(row))


def get_version(prompt_id: int, version_tag: str) -> Version | None:
    conn = get_connection()
    row = conn.execute(
        "SELECT * FROM versions WHERE prompt_id = ? AND version_tag = ?",
        (prompt_id, version_tag)
    ).fetchone()
    conn.close()
    return Version(**dict(row)) if row else None


def get_all_versions(prompt_id: int) -> list[Version]:
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM versions WHERE prompt_id = ? ORDER BY id ASC",
        (prompt_id,)
    ).fetchall()
    conn.close()
    return [Version(**dict(r)) for r in rows]


def get_latest_version(prompt_id: int) -> Version | None:
    conn = get_connection()
    row = conn.execute(
        "SELECT * FROM versions WHERE prompt_id = ? ORDER BY id DESC LIMIT 1",
        (prompt_id,)
    ).fetchone()
    conn.close()
    return Version(**dict(row)) if row else None