from flask import Flask, render_template, redirect, url_for, jsonify, request
import db

app = Flask(__name__)

# 카테고리(페이지) → 해당 board 접두사 매핑
CATEGORIES = {
    "전체":     None,
    "서울여대":  "서울여자대학교",
    "지능정보":  "지능정보보호학부",
    "KISA":     "KISA",
    "금융보안원": "금융보안원",
}

# 세부 카테고리: 사이트명 → 게시판명 목록
SUB_CATEGORIES = {
    "서울여자대학교":  ["학사", "장학", "행사", "채용/취업", "일반/봉사"],
    "지능정보보호학부": ["공지사항"],
    "KISA":          ["공지사항", "보도자료", "입찰공고", "채용정보"],
    "금융보안원":     ["공지사항", "보도자료"],
}


def _filter_notices(site: str | None, sub: str | None) -> list[dict]:
    """site/sub 조합으로 notices 필터링."""
    all_notices = db.get_notices()
    if not site:
        return all_notices
    if sub:
        board_key = f"{site}-{sub}"
        return [n for n in all_notices if n["board"] == board_key]
    return [n for n in all_notices if n["board"].startswith(site)]


@app.route("/")
def index():
    # 메인: 카테고리별 최신 3건 미리보기
    previews = {}
    for cat, site in CATEGORIES.items():
        if cat == "전체":
            continue
        notices = _filter_notices(site, None)
        previews[cat] = {"site": site, "notices": notices[:3]}
    return render_template("index.html", previews=previews, categories=list(CATEGORIES.keys()))


@app.route("/board/<category>")
def board(category: str):
    sub = request.args.get("sub")  # ?sub=채용/취업 처럼 쿼리스트링으로 받음
    site = CATEGORIES.get(category)
    notices = _filter_notices(site, sub)
    subs = SUB_CATEGORIES.get(site, []) if site else []
    return render_template(
        "board.html",
        category=category,
        sub=sub,
        site=site,
        notices=notices,
        subs=subs,
        categories=list(CATEGORIES.keys()),
    )


@app.route("/bookmark/<int:notice_id>", methods=["POST"])
def bookmark(notice_id: int):
    is_bookmarked = db.toggle_bookmark(notice_id)
    return jsonify({"bookmarked": is_bookmarked})


@app.route("/bookmarks")
def bookmarks():
    notices = [n for n in db.get_notices() if n["bookmarked"]]
    return render_template(
        "board.html",
        category="북마크",
        sub=None,
        site=None,
        notices=notices,
        subs=[],
        categories=list(CATEGORIES.keys()),
    )


if __name__ == "__main__":
    db.init_db()
    app.run(debug=True)
