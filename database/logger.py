import sqlite3
from pathlib import Path
from typing import Optional, List, Dict, Any
import json

DB_PATH = Path(__file__).resolve().parents[1] / "logs.sqlite"

_schema = '''
CREATE TABLE IF NOT EXISTS logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL,
    level TEXT NOT NULL,
    source TEXT,
    message TEXT,
    meta TEXT
);
'''


def _get_conn():
    conn = sqlite3.connect(DB_PATH)
    return conn


def init_db():
    conn = _get_conn()
    cur = conn.cursor()
    cur.executescript(_schema)
    conn.commit()
    conn.close()


def write_log(
    timestamp: str,
    level: str,
    source: Optional[str],
    message: str,
    meta: Optional[Dict[str, Any]] = None,
    response_time_ms: Optional[float] = None,
):
    conn = _get_conn()
    cur = conn.cursor()
    final_meta = dict(meta or {})
    if response_time_ms is not None:
        final_meta["response_time_ms"] = response_time_ms
    meta_json = json.dumps(final_meta)
    cur.execute(
        "INSERT INTO logs (timestamp, level, source, message, meta) VALUES (?, ?, ?, ?, ?)",
        (timestamp, level, source, message, meta_json),
    )
    conn.commit()
    conn.close()


def read_logs(limit: int = 100) -> List[Dict[str, Any]]:
    conn = _get_conn()
    cur = conn.cursor()
    cur.execute("SELECT id, timestamp, level, source, message, meta FROM logs ORDER BY id DESC LIMIT ?", (limit,))
    rows = cur.fetchall()
    conn.close()
    results = []
    for r in rows:
        try:
            meta = json.loads(r[5])
        except Exception:
            meta = {}
        results.append({
            "id": r[0],
            "timestamp": r[1],
            "level": r[2],
            "source": r[3],
            "message": r[4],
            "meta": meta,
        })
    return results
