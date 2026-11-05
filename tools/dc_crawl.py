# Keyword crawl of the DC 녹픽던 minor gallery (id=spd). Polite: one request at a time, 2s apart.
# Usage: python3 -I dc_crawl.py OUT_DIR   (resumable: skips posts already saved)
import sys, re, html, json, time, urllib.request, urllib.parse
from pathlib import Path

OUT = Path(sys.argv[1]); (OUT / "posts").mkdir(parents=True, exist_ok=True)
H = {"User-Agent": "Mozilla/5.0"}
BASE = "https://gall.dcinside.com/mgallery/board"
KEYWORDS = [
    # meta
    "티어", "무기 추천", "종결", "칼럼", "공략", "빌드", "마부", "인챈", "마법부여", "글리프", "상형문자", "특성 추천", "갑옷 추천",
    # weapons (game names + slang)
    "암살자의 칼", "암칼", "전투 도끼", "전투도끼", "쇠뇌", "곤봉", "단검", "더크", "철퇴", "건틀릿", "글레이브", "글레", "징 박힌",
    "특대 도끼", "특대도끼", "특도", "특대 방패", "특대방패", "특방", "특대검", "손도끼", "장검", "메이스", "육척봉", "레이피어",
    "원형 방패", "원방", "룬 검", "룬검", "쌍차", "시미타", "소검", "손낫", "전쟁 망치", "망치", "전쟁 낫", "전쟁낫", "채찍",
    # enchants
    "음침", "흡혈", "관성", "불타는", "타락의", "도달", "짜릿", "맹독", "차가운", "수정 마법", "불안정", "탄성", "예리", "섬뜩",
    "생장", "행운의", "방어의",
    # glyphs
    "애정", "점성", "항마", "가시의", "반발", "육중", "전위", "신속함", "속박", "유황", "흐름의", "흐릿", "위장의",
    # armor
    "사슬 갑옷", "사슬갑옷", "미늘", "판금",
    # subclasses / abilities
    "광전사", "광전", "검투사", "검투", "전투 마법사", "전마", "흑마법사", "흑마", "암살자", "프리러너", "저격수", "숲지기",
    "챔피언", "수도사", "사제", "성기사", "영웅의 도약", "충격파", "원소 폭발", "격렬한 마법", "연막탄", "죽음의 표식",
    "그림자 분신", "유령 칼날", "자연의 힘", "영혼의 매", "원소 해방", "눈속임", "승천자", "삼위일체", "집단의 힘",
]
MAX_PAGES, MAX_POSTS = 3, 700


def get(url, data=None, extra=None):
    time.sleep(2)
    req = urllib.request.Request(url, data=data, headers={**H, **(extra or {})})
    return urllib.request.urlopen(req, timeout=30).read().decode("utf-8", "ignore")


def clean(s):
    s = re.sub(r"<br\s*/?>|</p>|</div>", "\n", s)
    return re.sub(r"[ \t]+", " ", re.sub(r"<[^>]+>", " ", html.unescape(s))).strip()


index_path = OUT / "index.json"
index = json.loads(index_path.read_text()) if index_path.exists() else {}
done = set((OUT / "kw_done.txt").read_text().split("\n")) if (OUT / "kw_done.txt").exists() else set()
for kw in KEYWORDS:
    if kw in done:
        continue
    for page in range(1, MAX_PAGES + 1):
        q = urllib.parse.urlencode({"id": "spd", "s_type": "search_subject_memo", "s_keyword": kw, "page": page})
        try:
            t = get(f"{BASE}/lists/?{q}")
        except Exception as e:
            print("list fail", kw, page, e, flush=True); break
        rows = list(re.finditer(r'<tr class="ub-content[^"]*"[^>]*data-no="(\d+)"(.*?)</tr>', t, re.S))
        for m in rows:
            r = m.group(2)
            tit = re.search(r'class="gall_tit[^"]*".*?<a[^>]*>(.*?)</a>', r, re.S)
            d = re.search(r'class="gall_date" title="([^"]*)"', r)
            rp = re.search(r'class="reply_num">\[(\d+)', r)
            rec = re.search(r'class="gall_recommend">(\d+)', r)
            no = m.group(1)
            e = index.setdefault(no, {"no": int(no), "title": clean(tit.group(1)) if tit else "", "date": d.group(1) if d else "",
                                      "rec": int(rec.group(1)) if rec else 0, "replies": int(rp.group(1)) if rp else 0, "kw": []})
            if kw not in e["kw"]: e["kw"].append(kw)
        if len(rows) < 20: break
    with open(OUT / "kw_done.txt", "a") as f: f.write(kw + "\n")
    index_path.write_text(json.dumps(index, ensure_ascii=False))
    print(f"kw {kw}: index {len(index)}", flush=True)

# fetch bodies + comments: posts with any engagement, most-engaged first
cand = sorted((v for v in index.values() if v["replies"] or v["rec"]), key=lambda v: -(v["rec"] * 3 + v["replies"] + len(v["kw"])))[:MAX_POSTS]
print("fetching", len(cand), "posts", flush=True)
for i, v in enumerate(cand):
    p = OUT / "posts" / f"{v['no']}.json"
    if p.exists(): continue
    u = f"{BASE}/view/?id=spd&no={v['no']}"
    try:
        t = get(u)
        body = re.search(r'class="write_div"[^>]*>(.*?)<script', t, re.S)
        esno = re.search(r'e_s_n_o" value="([^"]*)"', t)
        cm = []
        if v["replies"] and esno:
            d = urllib.parse.urlencode({"id": "spd", "no": v["no"], "cmt_id": "spd", "cmt_no": v["no"], "e_s_n_o": esno.group(1),
                                        "comment_page": "1", "sort": "", "_GALLTYPE_": "M"}).encode()
            j = json.loads(get("https://gall.dcinside.com/board/comment/", d, {"X-Requested-With": "XMLHttpRequest", "Referer": u}))
            cm = [clean(c["memo"]) for c in (j.get("comments") or []) if c.get("del_yn") != "Y" and c.get("memo") and "dccon" not in c["memo"]]
        p.write_text(json.dumps({**v, "url": u, "body": clean(body.group(1))[:8000] if body else "", "comments": cm}, ensure_ascii=False))
    except Exception as e:
        print("post fail", v["no"], e, flush=True)
    if i % 25 == 0: print(f"post {i}/{len(cand)}", flush=True)
print("DONE", flush=True)
