from abc import ABC, abstractmethod
from playwright.sync_api import sync_playwright


class BaseCrawler(ABC):
    """
    boards: config.BOARDS 중 해당 크롤러 담당 항목
            [(site, board_name, url), ...]
    """

    def __init__(self, boards: list[tuple]):
        self.boards = boards

    def crawl(self) -> list[dict]:
        """브라우저 1회 실행 후 담당 게시판을 순회하며 파싱 결과 반환."""
        results = []
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            for site, board_name, url in self.boards:
                try:
                    page.goto(url, wait_until="networkidle", timeout=30_000)
                    html = page.content()
                    notices = self.parse(html, site, board_name, url)
                    results.extend(notices)
                except Exception as e:
                    print(f"[ERROR] {site}-{board_name}: {e}")
            browser.close()
        return results

    @abstractmethod
    def parse(self, html: str, site: str, board_name: str, base_url: str) -> list[dict]:
        """
        반환 형식:
        [{"title": str, "url": str, "date": str, "board": str}, ...]

        board 값 예시: "서울여자대학교-학사"
        url은 반드시 절대 URL로 반환.
        """
