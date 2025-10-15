import sqlite3
from typing import List, Tuple, Optional
import threading


class SessionMemory:
    """SQLite-based session memory for storing dialog context and state."""

    def __init__(self, db_path: str = "memory/session_memory.db"):
        self.db_path = db_path
        self._lock = threading.Lock()
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS session_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT,
                    sender TEXT,
                    text TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            # Для хранения состояния (например, последний город)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS session_state (
                    session_id TEXT PRIMARY KEY,
                    last_city TEXT
                )
            """)

    def add_message(self, session_id: str, sender: str, text: str):
        with self._lock, sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT INTO session_history (session_id, sender, text) VALUES (?, ?, ?)",
                (session_id, sender, text)
            )

    def get_history(self, session_id: str, limit: Optional[int] = None) -> List[Tuple[str, str, str]]:
        with self._lock, sqlite3.connect(self.db_path) as conn:
            query = "SELECT sender, text, timestamp FROM session_history WHERE session_id = ? ORDER BY id"
            params = [session_id]
            if limit:
                query += " DESC LIMIT ?"
                params.append(limit)
            cur = conn.execute(query, params)
            return cur.fetchall()

    def get_last_user_city(self, session_id: str) -> Optional[str]:
        with self._lock, sqlite3.connect(self.db_path) as conn:
            query = """
                SELECT text FROM session_history
                WHERE session_id = ? AND sender = 'user' AND text LIKE '/weather %'
                ORDER BY id DESC LIMIT 1
            """
            cur = conn.execute(query, (session_id,))
            row = cur.fetchone()
            if row:
                # пример текста: "/weather Москва"
                parts = row[0].split(maxsplit=1)
                if len(parts) == 2:
                    return parts[1].strip()
        return None

    def set_last_city(self, session_id: str, city: str):
        with self._lock, sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT INTO session_state (session_id, last_city) VALUES (?, ?) "
                "ON CONFLICT(session_id) DO UPDATE SET last_city=excluded.last_city",
                (session_id, city.strip())
            )

    def get_last_city(self, session_id: str) -> Optional[str]:
        with self._lock, sqlite3.connect(self.db_path) as conn:
            cur = conn.execute(
                "SELECT last_city FROM session_state WHERE session_id = ?",
                (session_id,)
            )
            row = cur.fetchone()
            return row[0] if row else None
