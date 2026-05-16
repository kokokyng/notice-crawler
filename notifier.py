from datetime import datetime
import requests
from config import DISCORD_WEBHOOK_URL

DISCORD_LIMIT = 2000


def _time_label() -> str:
    hour = datetime.now().hour
    return "오전 11시" if hour < 15 else "오후 6시"


def _webhook(content: str):
    if not DISCORD_WEBHOOK_URL:
        print("[WARN] DISCORD_WEBHOOK_URL 미설정 — 알림 생략")
        return
    resp = requests.post(
        DISCORD_WEBHOOK_URL,
        json={"content": content},
        timeout=10,
    )
    resp.raise_for_status()


def send(notices: list[dict]):
    """
    notices: db.get_unnotified() 반환값
    신규 글 없을 때도 알림 전송.
    2000자 초과 시 여러 번에 나눠 전송.
    """
    label = _time_label()
    count = len(notices)

    if count == 0:
        _webhook(f"[{label} 업데이트] 신규 공지 없음")
        return

    header = f"[{label} 업데이트] 신규 {count}건"
    notice_lines = []
    for n in notices:
        board_display = n["board"].replace("-", " - ", 1)
        notice_lines.append(f"• {board_display}: {n['title']} → {n['url']}")

    # 2000자 단위로 청크 분할
    chunks = []
    current = header
    for line in notice_lines:
        candidate = current + "\n" + line
        if len(candidate) > DISCORD_LIMIT:
            chunks.append(current)
            current = line
        else:
            current = candidate
    chunks.append(current)

    for chunk in chunks:
        _webhook(chunk)
