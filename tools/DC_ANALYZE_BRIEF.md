# Brief: extract item evaluations from DC 녹픽던 gallery posts

Input: a JSONL file (path in your task). Each line is one post from the Korean Shattered Pixel Dungeon (SPD) gallery
`gall.dcinside.com/mgallery/board/view/?id=spd&no=N`: {no, title, date, rec (추천 votes), replies, kw (search keywords that
matched), url, body, comments[]}. Posts are 2025-2026. v4.0 released 2026-09-09 (its beta was played from ~2026-08); v4.0
changed enchants (Venomous/Vorpal returned, Crystal new, Corrupting/Eldritch/Blooming buffed in v4.0.1), Barkskin (Warden),
Monk, vault. Melee weapons did NOT change in v4.0.

Task: for every SUBJECT in your scope (listed in your task), collect what posters and commenters actually say about how good
it is. A claim must be an evaluation (good/bad/ranking/comparison/when to use), not a question or a story with no verdict.
Gallery slang: 암칼=암살자의 칼, 특도=특대 도끼, 특방=특대 방패, 원방=원형 방패, 글레=글레이브, 망치=전쟁 망치, 전마=전투 마법사,
흑마=흑마법사, 광전=광전사, 마부=enchant, 강줌=강화 주문서, 힘물=힘 물약, N챌=N challenges, 노강=no upgrades, 몰빵=all-in.
"도" as a weapon = Katana (in-game name 도), 쌍차 = Sai. 음침한=Grim, 섬뜩한=Eldritch, 예리한=Vorpal, 짜릿한=Shocking,
도달=Projecting, 생장=Blooming, 육중함=Stone, 전위=Potential, 흐릿함=Obfuscation, 속박=Entanglement.
Ignore jokes, pure luck stories, and posts about other PD variants (총픽던, 픽던, 요괴픽던 etc. — say which if you skip many).

Output 1 — write JSON to the output path in your task:
{ "<subject>": { "verdict": "S|A|B|C|D or 'split' or 'no data'", "n_sources": <posts+comments that evaluate it>,
   "pros": ["short Korean point (N명)"], "cons": [...], "context": "when it shines / which class or subclass",
   "quotes": [{"no": 84430, "date": "2026-11-04", "rec": 0, "who": "post|comment", "text": "verbatim ≤150자"}] (max 5, strongest first) } }
Verdict = what the gallery overall seems to think, relative to other options of the same kind/tier. Weigh column posts
([녹픽던 칼럼], 공략) and high-rec posts more; one offhand comment ≠ consensus. If evidence is thin, say 'no data' or give the
verdict with n_sources ≤ 2 so the reader can see it is weak. Quotes must be copied verbatim from the input.

Output 2 — reply in ≤ 20 lines: posts read, which subjects had strong signal, notable disagreements, and any tier list /
ranking posts you found (no + title), especially image-free text rankings.
