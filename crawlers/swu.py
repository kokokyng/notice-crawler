import re
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
from .base import BaseCrawler


class SwuCrawler(BaseCrawler):
    """
    서울여자대학교 공지사항 크롤러.
    게시판 목록이 iframe(#mainFrm) 안에 있어 crawl()을 오버라이드함.
    """

    def crawl(self) -> list[dict]:
        results = []
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            for site, board_name, url in self.boards:
                try:
                    page.goto(url, wait_until="networkidle", timeout=30_000)
                    page.wait_for_selector("#mainFrm", timeout=10_000)

                    iframe_src = page.get_attribute("#mainFrm", "src")
                    m = re.search(r"bbsConfigFK=(\d+)", iframe_src or "")
                    if not m:
                        print(f"[WARN] {site}-{board_name}: bbsConfigFK 없음")
                        continue
                    bbs_fk = m.group(1)

                    frame = page.frame(name="mainFrm")
                    if frame is None:
                        print(f"[WARN] {site}-{board_name}: iframe 프레임 없음")
                        continue
                    frame.wait_for_load_state("networkidle")

                    html = frame.content()
                    notices = self.parse(html, site, board_name, bbs_fk)
                    results.extend(notices)
                except Exception as e:
                    print(f"[ERROR] {site}-{board_name}: {e}")
            browser.close()
        return results

    def parse(self, html: str, site: str, board_name: str, base_url: str) -> list[dict]:
        """
        base_url 자리에 bbs_fk 값을 받음 (crawl()에서 직접 전달).
        TOP 고정 행과 일반 행에 동일 글이 중복 등장하므로 pkid로 중복 제거.
        """
        bbs_fk = base_url
        soup = BeautifulSoup(html, "html.parser")
        results = []
        seen_pkids: set[str] = set()

        for td_title in soup.select("td.title"):
            tr = td_title.parent
            a_tag = td_title.select_one("a[onclick]")
            if not a_tag:
                continue

            # 제목: notice행은 <strong>, 일반행은 <span>
            title_el = a_tag.select_one("strong") or a_tag.select_one("div > span")
            if not title_el:
                continue
            title = title_el.get_text(strip=True)
            if not title:
                continue

            onclick = a_tag.get("onclick", "")
            m = re.search(r"boardMove\('[^']*','(\d+)'\)", onclick)
            if not m:
                continue
            pkid = m.group(1)
            if pkid in seen_pkids:
                continue
            seen_pkids.add(pkid)

            post_url = (
                f"https://www.swu.ac.kr/gopage/goboard1.jsp"
                f"?bbsConfigFK={bbs_fk}&pkid={pkid}"
            )

            date = ""
            for td in tr.select("td"):
                div = td.select_one("div.ls0")
                if div:
                    text = div.get_text(strip=True)
                    if re.match(r"\d{4}\.\d{2}\.\d{2}", text):
                        date = text
                        break

            results.append(
                {
                    "title": title,
                    "url": post_url,
                    "date": date,
                    "board": f"{site}-{board_name}",
                }
            )

        return results
