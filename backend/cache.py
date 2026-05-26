"""
ChronoDyne Systems // ILO Analyzer v4
Cache Layer — SQLite-backed persistent store for CDX, bias, and weather baseline data.

TTL policy:
  - CDX results:         7 days  (snapshot history stable, not worth re-hitting Wayback)
  - Bias scores:         30 days (AllSides/MBFC update infrequently)
  - Weather baseline:    1 day   (decay constants are stable; daily refresh is plenty)
"""

import sqlite3
import json
import time
import os
from typing import Optional, Any

DB_PATH = os.environ.get("CACHE_DB_PATH", "/tmp/chronodyne_cache.db")

TTL = {
    "cdx":     7  * 24 * 3600,
    "bias":    30 * 24 * 3600,
    "weather": 1  * 24 * 3600,
    "tavily":  1  * 24 * 3600,
}


def _connect() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def initialize_db() -> None:
    """Create tables if they don't exist. Safe to call on every startup."""
    with _connect() as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS cache (
                namespace   TEXT NOT NULL,
                key         TEXT NOT NULL,
                value       TEXT NOT NULL,
                created_at  REAL NOT NULL,
                expires_at  REAL NOT NULL,
                PRIMARY KEY (namespace, key)
            );

            CREATE INDEX IF NOT EXISTS idx_cache_expires
                ON cache (expires_at);
        """)


def get(namespace: str, key: str) -> Optional[Any]:
    """
    Retrieve a cached value. Returns None on miss or expiry.
    Expired entries are pruned lazily on read.
    """
    now = time.time()
    with _connect() as conn:
        row = conn.execute(
            "SELECT value, expires_at FROM cache WHERE namespace = ? AND key = ?",
            (namespace, key)
        ).fetchone()

        if row is None:
            return None

        if row["expires_at"] < now:
            # Lazy eviction
            conn.execute(
                "DELETE FROM cache WHERE namespace = ? AND key = ?",
                (namespace, key)
            )
            return None

        try:
            return json.loads(row["value"])
        except json.JSONDecodeError:
            return None


def set(namespace: str, key: str, value: Any, ttl_seconds: Optional[int] = None) -> None:
    """
    Store a value. TTL defaults to namespace policy if not specified.
    Overwrites existing entry for the same (namespace, key).
    """
    if ttl_seconds is None:
        ttl_seconds = TTL.get(namespace, 3600)

    now = time.time()
    expires_at = now + ttl_seconds

    with _connect() as conn:
        conn.execute(
            """
            INSERT INTO cache (namespace, key, value, created_at, expires_at)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(namespace, key) DO UPDATE SET
                value      = excluded.value,
                created_at = excluded.created_at,
                expires_at = excluded.expires_at
            """,
            (namespace, key, json.dumps(value), now, expires_at)
        )


def invalidate(namespace: str, key: str) -> None:
    """Explicitly remove a single cache entry."""
    with _connect() as conn:
        conn.execute(
            "DELETE FROM cache WHERE namespace = ? AND key = ?",
            (namespace, key)
        )


def purge_expired() -> int:
    """Remove all expired entries. Returns count of pruned rows."""
    now = time.time()
    with _connect() as conn:
        cursor = conn.execute(
            "DELETE FROM cache WHERE expires_at < ?",
            (now,)
        )
        return cursor.rowcount


def stats() -> dict:
    """Return basic cache health metrics."""
    now = time.time()
    with _connect() as conn:
        total = conn.execute("SELECT COUNT(*) FROM cache").fetchone()[0]
        expired = conn.execute(
            "SELECT COUNT(*) FROM cache WHERE expires_at < ?", (now,)
        ).fetchone()[0]
        by_namespace = conn.execute(
            "SELECT namespace, COUNT(*) as count FROM cache GROUP BY namespace"
        ).fetchall()

    return {
        "total_entries": total,
        "expired_entries": expired,
        "live_entries": total - expired,
        "by_namespace": {row["namespace"]: row["count"] for row in by_namespace},
        "db_path": DB_PATH,
    }
