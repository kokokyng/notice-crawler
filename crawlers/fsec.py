import re
from bs4 import BeautifulSoup
from .base import BaseCrawler

BASE_URL = "https://www.fsec.or.kr"


class FsecCrawler(BaseCrawler):
    """금융보안원 공지사항/보도자료 크롤러."""

    def parse(self, html: str, site: str, board_name: str, base_url: str) -> list[dict]:
        # base_url: "https://www.fsec.or.kr/bbs/66" → board_id = "66"
        m = re.search(r"/bbs/(\d+)", base_url)
        board_id = m.group(1) if m else ""

        soup = BeautifulSoup(html, "html.parser")
        results = []

        for li in soup.select("ul#bbsList li[onclick]"):
            onclick = li.get("onclick", "")
            m = re.search(r"moveToBbsDetail\((\d+)\)", onclick)
            if not m:
                continue
            post_id = m.group(1)
            url = f"{BASE_URL}/bbs/{board_id}/{post_id}"

            title_el = li.select_one("strong.tit")
            if not title_el:
                continue
            title = title_el.get_text(strip=True)

            date_el = li.select_one("em.date")
            date = date_el.get_text(strip=True) if date_el else ""

            results.append(
                {
                    "title": title,
                    "url": url,
                    "date": date,
                    "board": f"{site}-{board_name}",
                }
            )

        return results
