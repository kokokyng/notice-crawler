from bs4 import BeautifulSoup
from .base import BaseCrawler

BASE_URL = "https://www.kisa.or.kr"


class KisaCrawler(BaseCrawler):
    """KISA 공지사항/보도자료/입찰공고 등 9개 게시판 크롤러."""

    def parse(self, html: str, site: str, board_name: str, base_url: str) -> list[dict]:
        soup = BeautifulSoup(html, "html.parser")
        results = []

        for tr in soup.select("table.tbl_board tr"):
            a_tag = tr.select_one("td.sbj a")
            if not a_tag:
                continue

            title = a_tag.get_text(strip=True)
            href = a_tag.get("href", "")
            if not href:
                continue
            url = BASE_URL + href

            date_td = tr.select_one("td.date")
            date = date_td.get_text(strip=True) if date_td else ""

            results.append(
                {
                    "title": title,
                    "url": url,
                    "date": date,
                    "board": f"{site}-{board_name}",
                }
            )

        return results
