import os
from dotenv import load_dotenv

load_dotenv()

DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")

# (사이트명, 게시판명, URL) 튜플 리스트
# board_key 형식: "사이트명-게시판명" → DB 및 알림 메시지에 사용
BOARDS = [
    # 서울여자대학교
    ("서울여자대학교", "학사",      "http://www.swu.ac.kr/www/noticea.html"),
    ("서울여자대학교", "장학",      "http://www.swu.ac.kr/www/noticeb.html"),
    ("서울여자대학교", "행사",      "http://www.swu.ac.kr/www/noticec.html"),
    ("서울여자대학교", "채용/취업", "http://www.swu.ac.kr/www/noticed.html"),
    ("서울여자대학교", "일반/봉사", "http://www.swu.ac.kr/www/noticee.html"),

    # 서울여자대학교 지능정보보호학부
    ("지능정보보호학부", "공지사항", "http://security.swu.ac.kr/sub.html?page=community_notice"),

    # KISA 알림마당
    ("KISA", "공지사항", "https://www.kisa.or.kr/401"),
    ("KISA", "보도자료", "https://www.kisa.or.kr/402"),
    ("KISA", "입찰공고", "https://www.kisa.or.kr/403"),
    ("KISA", "채용정보", "https://www.kisa.or.kr/404"),

    # KISA 지식플랫폼
    ("KISA", "연구보고서", "https://www.kisa.or.kr/201"),
    ("KISA", "동향분석",   "https://www.kisa.or.kr/20207"),
    ("KISA", "정기간행물", "https://www.kisa.or.kr/20305"),
    ("KISA", "가이드라인", "https://www.kisa.or.kr/2060207"),
    ("KISA", "안내서",     "https://www.kisa.or.kr/2060307"),

    # 금융보안원
    ("금융보안원", "공지사항", "https://www.fsec.or.kr/bbs/66"),
    ("금융보안원", "보도자료", "https://www.fsec.or.kr/bbs/69"),

]

# 크롤러 모듈 매핑: 사이트명 → crawler 파일명(모듈명)
SITE_CRAWLER_MAP = {
    "서울여자대학교":   "swu",
    "지능정보보호학부": "swu_security",
    "KISA":            "kisa",
    "금융보안원":       "fsec",
}
