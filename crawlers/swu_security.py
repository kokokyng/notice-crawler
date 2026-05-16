from bs4 import BeautifulSoup
from .base import BaseCrawler

BASE_URL = "http://security.swu.ac.kr"


class SwuSecurityCrawler(BaseCrawler):
    """서울여자대학교 지능정보보호학부 공지사항 크롤러 (정적 페이지)."""

    def parse(self, html: str, site: str, board_name: str, base_url: str) -> list[dict]:
        soup = BeautifulSoup(html, "html.parser")
        results = []

        for tr in soup.select("tr.woocommerce-cart-form__cart-item"):
            a_tag = tr.select_one("td.product-name a")
            if not a_tag:
                continue

            title = a_tag.get_text(strip=True)
            href = a_tag.get("href", "")
            if not href:
                continue
            url = f"{BASE_URL}/{href.lstrip('/')}"

            # 날짜: td 순서상 3번째 (index 2)
            tds = tr.select("td")
            date = ""
            if len(tds) >= 3:
                date = tds[2].get_text(strip=True)

            results.append(
                {
                    "title": title,
                    "url": url,
                    "date": date,
                    "board": f"{site}-{board_name}",
                }
            )

        return results
