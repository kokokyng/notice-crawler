import sqlite3
from datetime import datetime

DB_PATH = "notices.db"


def get_conn():
    return sqlite3.connect(DB_PATH)


def init_db():
    with get_conn() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS notices (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                title      TEXT    NOT NULL,
                url        TEXT    NOT NULL UNIQUE,
                date       TEXT,
                board      TEXT    NOT NULL,
                created_at TEXT    NOT NULL,
                notified   INTEGER NOT NULL DEFAULT 0,
                bookmarked INTEGER NOT NULL DEFAULT 0
            )
        """)
        # 기존 DB에 컬럼이 없을 경우 추가 (마이그레이션)
        try:
            conn.execute("ALTER TABLE notices ADD COLUMN bookmarked INTEGER NOT NULL DEFAULT 0")
        except Exception:
            pass


def is_new(url: str) -> bool:
    with get_conn() as conn:
        row = conn.execute("SELECT 1 FROM notices WHERE url = ?", (url,)).fetchone()
        return row is None


def save_notice(title: str, url: str, date: str, board: str):
    """신규 공지 저장. URL 중복 시 무시."""
    with get_conn() as conn:
        conn.execute(
            """
            INSERT OR IGNORE INTO notices (title, url, date, board, created_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (title, url, date, board, datetime.now().isoformat()),
        )


def get_unnotified() -> list[dict]:
    """아직 Discord로 전송하지 않은 공지 목록 반환."""
    with get_conn() as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute(
            "SELECT * FROM notices WHERE notified = 0 ORDER BY id"
        ).fetchall()
        return [dict(row) for row in rows]


def mark_notified(ids: list[int]):
    """전송 완료 처리."""
    if not ids:
        return
    placeholders = ",".join("?" * len(ids))
    with get_conn() as conn:
        conn.execute(
            f"UPDATE notices SET notified = 1 WHERE id IN ({placeholders})", ids
        )


def get_notices(board: str | None = None) -> list[dict]:
    """대시보드용 공지 조회. board 미지정 시 전체 반환. 최신순 정렬."""
    with get_conn() as conn:
        conn.row_factory = sqlite3.Row
        if board:
            rows = conn.execute(
                "SELECT * FROM notices WHERE board = ? ORDER BY date DESC, id DESC",
                (board,),
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT * FROM notices ORDER BY date DESC, id DESC"
            ).fetchall()
        return [dict(row) for row in rows]


def toggle_bookmark(notice_id: int) -> bool:
    """북마크 토글. 변경 후 bookmarked 값 반환."""
    with get_conn() as conn:
        row = conn.execute(
            "SELECT bookmarked FROM notices WHERE id = ?", (notice_id,)
        ).fetchone()
        if row is None:
            return False
        new_val = 0 if row[0] else 1
        conn.execute(
            "UPDATE notices SET bookmarked = ? WHERE id = ?", (new_val, notice_id)
        )
        return bool(new_val)


def delete_old_notices():
    """7일 지난 게시글 삭제 (북마크 제외)."""
    with get_conn() as conn:
        conn.execute(
            """
            DELETE FROM notices
            WHERE bookmarked = 0
              AND created_at < datetime('now', '-7 days')
            """
        )
