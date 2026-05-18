import argparse
import sys
from apscheduler.schedulers.blocking import BlockingScheduler

import db
import notifier
from config import BOARDS, SITE_CRAWLER_MAP
from crawlers.swu import SwuCrawler
from crawlers.swu_security import SwuSecurityCrawler
from crawlers.kisa import KisaCrawler
from crawlers.fsec import FsecCrawler

CRAWLER_CLASSES = {
    "swu":          SwuCrawler,
    "swu_security": SwuSecurityCrawler,
    "kisa":         KisaCrawler,
    "fsec":         FsecCrawler,
}


def _group_boards() -> dict[str, list[tuple]]:
    """BOARDS를 사이트명 기준으로 그룹화."""
    groups: dict[str, list] = {}
    for site, board_name, url in BOARDS:
        groups.setdefault(site, []).append((site, board_name, url))
    return groups


def run_crawl(init_mode: bool = False):
    """
    전체 사이트 크롤링 → 신규 감지 → 저장 → 알림 전송.
    init_mode=True 이면 DB 씨딩만 하고 알림은 생략.
    """
    label = "초기화" if init_mode else "크롤링"
    print(f"[{label}] 시작")

    for site, boards in _group_boards().items():
        module_name = SITE_CRAWLER_MAP.get(site)
        crawler_class = CRAWLER_CLASSES.get(module_name)
        if not crawler_class:
            print(f"  [WARN] {site}: 크롤러 없음, 건너뜀")
            continue

        try:
            notices = crawler_class(boards).crawl()
            new_count = 0
            for n in notices:
                if db.is_new(n["url"]):
                    db.save_notice(n["title"], n["url"], n["date"], n["board"])
                    new_count += 1
            print(f"  {site}: {len(notices)}건 수집, {new_count}건 신규")
        except Exception as e:
            print(f"  [ERROR] {site}: {e}")

    if init_mode:
        # 씨딩된 글을 모두 전송 완료 처리 → 이후 스케줄 실행 시 중복 알림 방지
        unnotified = db.get_unnotified()
        if unnotified:
            db.mark_notified([n["id"] for n in unnotified])
        print(f"[초기화] 완료 — {len(unnotified)}건 DB 등록 (알림 미전송)")
        return

    unnotified = db.get_unnotified()
    notifier.send(unnotified)
    if unnotified:
        db.mark_notified([n["id"] for n in unnotified])
    print(f"[크롤링] 완료 — 알림 전송 {len(unnotified)}건")


def main():
    parser = argparse.ArgumentParser(description="공지사항 자동 수집 크롤러")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--init", action="store_true",
                       help="현재 게시글을 DB에 등록만 하고 알림 없이 종료 (최초 1회 실행)")
    group.add_argument("--run-now", action="store_true",
                       help="스케줄 없이 즉시 1회 실행 후 종료 (테스트용)")
    args = parser.parse_args()

    db.init_db()

    if args.init:
        run_crawl(init_mode=True)
        sys.exit(0)

    if args.run_now:
        run_crawl()
        sys.exit(0)

    # 스케줄러 모드
    scheduler = BlockingScheduler(timezone="Asia/Seoul")
    scheduler.add_job(run_crawl, "cron", hour=11, minute=0)
    scheduler.add_job(run_crawl, "cron", hour=18, minute=0)
    scheduler.add_job(db.delete_old_notices, "cron", hour=0, minute=0)  # 매일 자정 정리
    print("스케줄러 시작 — 실행 시각: 11:00, 18:00 / 자동 삭제: 00:00 (Asia/Seoul)")
    try:
        scheduler.start()
    except KeyboardInterrupt:
        print("스케줄러 종료")


if __name__ == "__main__":
    main()
