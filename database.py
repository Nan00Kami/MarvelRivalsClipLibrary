import os
import sqlite3
from typing import Any, Dict, List

DB_PATH = os.path.join("data", "clips.db")


def init_db():
    """Initializes the database schema."""
    os.makedirs("data", exist_ok=True)
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS clips (
                id TEXT PRIMARY KEY,
                url TEXT NOT NULL,
                embed_url TEXT,
                broadcaster_name TEXT,
                creator_name TEXT,
                title TEXT,
                view_count INTEGER,
                created_at TEXT,
                thumbnail_url TEXT,
                duration REAL,
                is_downloaded INTEGER DEFAULT 0,
                file_path TEXT
            )
        """)
        conn.commit()


def save_clips(clips: List[Dict[str, Any]]) -> int:
    """Inserts new clips, ignoring existing IDs. Returns count of new clips added."""
    init_db()
    inserted = 0
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        for clip in clips:
            cursor.execute(
                """
                INSERT OR IGNORE INTO clips (
                    id, url, embed_url, broadcaster_name,
                    creator_name, title, view_count,
                    created_at, thumbnail_url, duration
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    clip["id"],
                    clip["url"],
                    clip.get("embed_url"),
                    clip.get("broadcaster_name"),
                    clip.get("creator_name"),
                    clip.get("title"),
                    clip.get("view_count", 0),
                    clip.get("created_at"),
                    clip.get("thumbnail_url"),
                    clip.get("duration", 0.0),
                ),
            )
            if cursor.rowcount > 0:
                inserted += 1
        conn.commit()
    return inserted

def mark_clip_downloaded(clip_id: str, file_path: str):
    """Flags a clip as downloaded and records its storage location."""
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            """
            UPDATE clips
            SET is_downloaded = 1, file_path = ?
            WHERE id = ?
        """,
            (file_path, clip_id),
        )
        conn.commit()


def get_undownloaded_clips(limit: int = 10) -> List[Dict[str, Any]]:
    """Retrieves clips from DB that haven't been downloaded yet."""
    init_db()
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT id, title, thumbnail_url, view_count
            FROM clips
            WHERE is_downloaded = 0
            ORDER BY view_count DESC
            LIMIT ?
        """,
            (limit,),
        )
        return [dict(row) for row in cursor.fetchall()]
