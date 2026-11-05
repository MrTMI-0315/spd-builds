# Rewrite spd-builds/data/builds/*.json builds from the DC 녹픽던 talent columns (#82739 전사·마법사, #82783 도적·사냥꾼)
# and gallery gear opinions. Usage: python3 -I rebuild_builds.py SITE_DIR
import json, re, sys
from pathlib import Path

SITE = Path(sys.argv[1])
H = json.loads((SITE / 'data/heroes.json').read_text())
T, SUB, AB = H['talents'], {s['id']: s for s in H['subclasses']}, {a['id']: a for a in H['abilities']}
CLS = {c['id']: c for c in H['classes']}
DC = 'https://gall.dcinside.com/mgallery/board/view/?id=spd&no='
def U(no, d): return [DC + str(no), d]
COL_WM, COL_RH = U(82739, '2026-08-28'), U(82783, '2026-08-29')

def tier_ids(cid, sub, ab, tier):
    c = CLS[cid]['talents']
    return {1: c['t1'], 2: c['t2'], 3: c['t3'] + SUB[sub]['talents'], 4: AB[ab]['talents']}[tier]

def level_line(tid, pts):
    m = re.search(r'_\+%d:_\s*(.*?)(?=\s*_\+\d:_|$)' % pts, T[tid]['desc_ko'], re.S)
    s = re.sub(r'[_*]', '', m.group(1) if m else T[tid]['desc_ko']).split('\n')[0].strip()
    return s[:90]

def talents_from(cid, sub, ab, digits, label, src, old):
    """digits: {tier: 'base(+bonus)'} → (talents, bonus)"""
    tal, bon = [], []
    for tier, spec in digits.items():
        m = re.fullmatch(r'(\d+)(?:\(\+(\d+)\))?', spec)
        base, extra = m.group(1), m.group(2) or ''
        ids = tier_ids(cid, sub, ab, tier)
        assert len(base) == len(ids) and (not extra or len(extra) == len(ids)), (cid, tier, spec)
        q = f'칼럼 {tier}티어 {spec} ({label[tier]})' if label.get(tier) else f'칼럼 {tier}티어 {spec}'
        for tid, ch in zip(ids, base):
            if ch != '0':
                p = int(ch)
                tal.append({'id': tid, 'points': p, 'why': old.get((tid, p)) or level_line(tid, p), 'tag': '커뮤니티', 'quote': q, 'src': src})
        for tid, ch in zip(ids, extra):
            if ch != '0':
                bon.append({'tier': tier, 'id': tid, 'points': int(ch), 'why': level_line(tid, int(ch) + int(base[ids.index(tid)])), 'tag': '커뮤니티', 'quote': q, 'src': src})
    return tal, bon

# anchors from the columns' own prose: if any fails, heroes.json order != in-game order
def at(cid, sub, ab, tier, i): return tier_ids(cid, sub, ab, tier)[i - 1]
assert at('WARRIOR', 'BERSERKER', 'SHOCKWAVE', 3, 2) == 'STRONGMAN'          # "3-2 … 힘이 1 부족할 때 판금"
assert at('WARRIOR', 'GLADIATOR', 'SHOCKWAVE', 3, 4) == 'LETHAL_DEFENSE'     # 검투사 3-4 가장 중요
assert at('WARRIOR', 'GLADIATOR', 'SHOCKWAVE', 4, 3) == 'SHOCK_FORCE'        # 충격파 4-3 (마비)
assert at('MAGE', 'WARLOCK', 'WARPBEACON', 1, 4) == 'BACKUP_BARRIER'         # 1-4 방어막
assert at('ROGUE', 'ASSASSIN', 'SMOKEBOMB', 3, 3) == 'ENHANCED_LETHALITY'    # 암살자 3-3
assert at('ROGUE', 'ASSASSIN', 'SMOKEBOMB', 3, 2) == 'LIGHT_CLOAK'           # "3-2 사실상 유물칸 +1"
assert at('HUNTRESS', 'WARDEN', 'NATURESPOWER', 3, 4) == 'BARKSKIN'          # 숲지기 3-4
assert at('MAGE', 'WARLOCK', 'WARPBEACON', 3, 3) == 'SOUL_EATER'             # 흑마 3-3 필수(허기 회복)

def G(slot, ref, why, src, quote, name=None, code=None):
    g = {'slot': slot, 'why': why, 'tag': '커뮤니티', 'quote': quote, 'src': src}
    g['name' if name else 'ref'] = name or ref
    if code: g['code'] = code
    return g

# code/description evidence kept next to the community claim (verified in 3516848)
JP = 'core/src/main/java/com/shatteredpixel/shatteredpixeldungeon/'
KO = 'core/src/main/assets/messages/items/items_ko.properties'
def C(tag, why, quote): return {'tag': tag, 'why': why, 'quote': quote}

SPECS = {
 'WARRIOR': {
  'summary': '부러진 인장의 방어막으로 버티며 정면으로 싸우는 직업입니다. 갤러리 정석은 판금(없으면 미늘)에 강화를 6~8강까지 몰아주고, 4~5티어 무기가 3강 이상 뜨면 나머지를 무기에 넣는 것입니다.',
  'builds': {
   'GLADIATOR': dict(ab='SHOCKWAVE', title='판금 몰빵 매치기 검투사', src=COL_WM,
     digits={1: '2201(+0011)', 2: '20220(+00002)', 3: '00233', 4: '2044(+2000)'},
     label={2: '공격력 높은 빌드', 3: '기본 빌드', 4: '일반적인 원거리 견제'},
     concept='강화를 판금 갑옷에 몰아 방어력을 올리고, 쌍차·돌 건틀릿처럼 빠른 무기로 콤보를 쌓아 방어력에 비례하는 필살기(매치기)로 마무리합니다. 뉴비도 깨는 정석이라는 평입니다.',
     playstyle='초반엔 시작 소검과 인장 방어막으로 싸우고, 강화 주문서는 갑옷에 넣습니다(상형문자 전이 +2로 갑옷을 바꿔도 글리프를 옮김). 검투사 이후엔 쌍차나 돌 건틀릿으로 콤보를 쌓고, 치명적인 방어로 필살기 처치 때 인장 방어막을 다시 채웁니다. 판금 6~8강을 맞춘 뒤 남는 강화를 무기에 나눕니다. 후반엔 충격파로 전갈·악마의 눈을 마비시켜 잡거나 도망칩니다.',
     abwhy='전갈이나 악마의 눈을 마비시키고 잡거나 도망치는 데 좋아 4-3(충격력)이 가장 중요하다는 칼럼 설명',
     gear=[G('armor', 'PlateArmor', '판금 6강이 국룰, 7강 추천. 방어구 6~8강 후 나머지를 무기에', U(82610, '2026-08-24'), '일단 판금6강 국룰인데 7강추천'),
           G('weapon', 'Sai', '공속 0.5턴이라 콤보가 잘 쌓임. 3티어라 3~4강까지만 강화', U(80107, '2026-06-15'), '무기는 쌍차도나 돌 건틀릿처럼 공속이 빨라서 콤보 잘 쌓이는 무기가 좋음'),
           G('weapon', 'Gauntlet', '5티어 공속 0.5턴. 쌍차 다음 단계', U(83873, '2026-10-12'), '검투사 + 돌건틀릿이 정석 조합'),
           G('enchantment', 'Shocking', '타수가 많아 자주 터짐. 짜릿한 돌 건틀릿 검투사 추천', U(79001, '2026-05-07'), '짜릿한 돌 건틀릿'),
           G('glyph', 'Stone', '판금 몰빵과 함께 쓰면 물리 피해를 크게 줄임', U(83108, '2026-09-11'), '역시 믿나방 아니면 육중함이 최고인듯 강줌은 판금 몰빵')]),
   'BERSERKER': dict(ab='HEROICLEAP', title='판금 광전사 (원거리 견제형)', src=COL_WM,
     digits={1: '2201(+0011)', 2: '20202(+00020)', 3: '00323(+20000)', 4: '4042(+0002)'},
     label={2: '원거리 견제 빌드', 3: '방어력 확보를 이미 했을 때', 4: '공격 수단으로 활용'},
     concept='판금에 강화를 몰아 광포화 방어막(8+2×갑옷 강화)을 키우고, 끝없는 분노로 오래 버팁니다. 급조한 투척물(2-5)로 원거리 적을 실명시키고 다가갑니다.',
     playstyle='갤러리 평가는 검투사보다 낮아서, 이미 판금·특대 방패 같은 방어 장비를 확보했을 때 고르는 전직입니다. 강화는 판금 6강 이상을 먼저 맞추고, 원거리 적에게는 아무 아이템이나 던져 실명시킨 뒤 붙습니다. 분노가 차면 광포화로 위기를 넘기고, 영웅의 도약 몸통 박치기(방어력 비례 피해)로 포위를 끊습니다.',
     abwhy='칼럼의 공격 수단용 배분(몸통 박치기 4, 이중 도약 4). 이동기가 없으면 도약이 최선이라는 평',
     abcode=C('설명문 기준', '몸통 박치기 +4는 착지 시 4-16 + 방어력 100% 피해라 갑옷 강화와 맞음',
              '몸통 박치기 +4: 근접한 모든 적들은 4-16 + 전사의 방어력의 100% 만큼 피해'),
     gear=[G('armor', 'PlateArmor', '광포화 방어막도 갑옷 강화당 +2라 판금 몰빵과 맞음', U(84318, '2026-10-30'), '상식적으로는 판금 6강 수준의 방어 갖추고 하는게 정상적임'),
           G('weapon', 'Greatshield', '방어와 딜을 같이 챙기는 몰빵 무기. 맞으면서 이기는 운영', U(83971, '2026-10-15'), '나는 그냥 특대방패 사랑꾼임'),
           G('enchantment', 'Vampiric', '맞으면서 싸우는 운영이라 유지력이 중요', U(83633, '2026-10-02'), '흡혈 특방'),
           G('glyph', 'Thorns', '가시 판금 + 신비의 반지로 출혈 처치까지 하는 광전사 사례', U(84150, '2026-10-23'), '광전사로 가시 상형문자 + 판금갑옷 + 신비반')]),
  }},
 'MAGE': {
  'builds': {
   'WARLOCK': dict(ab='WARPBEACON', title='타락·아군 흑마법사', src=COL_WM,
     digits={1: '0212', 2: '20112(+01010)', 3: '02330(+01001)', 4: '0424(+0020)'},
     label={2: '일반적인 빌드', 3: '아군 빌드'},
     concept='영혼 표식을 새긴 적을 때려 체력과 허기를 함께 회복하고(영혼 포식자), 타락의 마법 막대로 만든 아군이 대신 싸웁니다. 9챌 기본 선택으로 꼽히는 전직입니다.',
     playstyle='강화는 지팡이에 넣어 표식 확률을 올리고, 타락처럼 적을 방해하는 막대를 같이 씁니다. 근접 무기는 채찍·글레이브처럼 사거리가 긴 것으로 표식 대상을 때립니다. 위험하면 미리 깔아 둔 순간이동 신호기로 빠집니다. 타락 막대는 "특정 빌드가 아니면 못 쓴다"는 평이라, 없으면 흡혈 빌드(30302)로 바꿉니다.',
     abwhy='칼럼: 공격용으로 쓰지 말고, 위험할 때 에테르 사슬처럼 쓰는 비상 탈출기',
     gear=[G('weapon', 'MagesStaff', '강화를 지팡이에 몰아 표식 확률과 막대 위력을 올림', U(79339, '2026-05-19'), '그냥 지팡이를 강화박고 판금에 6~10정도 박으면'),
           G('wand', None, '타락시킨 적이 아군이 됨. 타락흑마는 유명한 사기빌드라는 평(다른 직업에선 D)', U(78173, '2026-04-01'), 'ㅊㅊ 타락흑마는 유명한 사기빌드임', name='타락의 마법 막대',
             code=C('코드 계산', '영혼 흡수 +3이면 아군 물리 공격도 표식 회복을 40%로 발동',
                    f'{JP}actors/mobs/Mob.java:880-886 enemy != hero → restoration × 0.4×SOUL_SIPHON/3')),
           G('weapon', 'Whip', '9챌 흑마는 채찍·글레이브로 거리를 두고 때림', U(80965, '2026-07-13'), '9챌에서는 채찍이랑 글레이프만 무기로 쓰는 거임'),
           G('enchantment', 'Vampiric', '흡혈 채찍이면 회복이 겹침', U(83043, '2026-09-07'), '흡혈의 채찍을 줬어야 했다')]),
   'BATTLEMAGE': dict(ab='ELEMENTALBLAST', title='충격파 전투 마법사 (노챌)', src=COL_WM,
     digits={1: '0212', 2: '20112(+01010)', 3: '00332(+10001)', 4: '2404(+2000)'},
     label={2: '일반적인 빌드', 3: '일반적인 빌드', 4: '공격용'},
     concept='지팡이에 충격파(또는 붕괴) 막대를 융합해 쏘고, 지팡이 근접 타격으로 막대와 유물을 충전합니다. 노챌·저챌에서 가장 편한 마법사입니다.',
     playstyle='강화는 지팡이에 몰고, 쏜 뒤 지팡이로 쳐서 강력한 일격과 신비한 충전(유물 충전)을 굴립니다. 충격파·부식·화염 폭발 막대는 갤러리 막대 티어표 S입니다. 풍요의 뿔이나 피의 성배가 있으면 흑마보다 낫다는 평도 있습니다. 후반엔 원소 폭발로 무리를 처리합니다.',
     abwhy='칼럼의 공격용 배분(폭발 반경 2, 원소의 힘 4). 단순 공격용이면 격렬한 마법이 나을 수 있다는 단서가 붙음',
     gear=[G('weapon', 'MagesStaff', '전마는 지팡이를 최종 무기로 강화를 몰아줌', U(80093, '2026-06-15'), '법사는 전투마법사 몇 번 해보면 익숙해지는데 쉽고 간편함'),
           G('wand', None, '충격파 전마가 1티어라는 평. 마법사 3-3과 조합하면 한 방', U(83628, '2026-10-02'), '갠적으로 이제 전마 1티어는 충격파 전마라고 생각한다.', name='충격파의 마법 막대 (지팡이 융합)'),
           G('wand', None, '붕괴 전마가 제일 편하다는 대안', U(84454, '2026-11-04'), '일단 전마로 가고 붕괴전마가 젤 편하고 성능도좋아요', name='붕괴의 마법 막대 (대안)'),
           G('artifact', None, '풍뿔·피의 성배가 있으면 흑마 상위호환이라는 평', U(83353, '2026-09-22'), '피성풍뿔전마가 흑마 상위호환임', name='풍요의 뿔'),
           G('glyph', 'Potential', '자해 없이 충전만 해 줘 셀프 보호막 운영', U(84246, '2026-10-26'), '자해 데미지 없이 충전만 해주니까 셀프 보호막')]),
  }},
 'ROGUE': {
  'builds': {
   'FREERUNNER': dict(ab='SMOKEBOMB', title='저격 반지 프리러너', src=COL_RH,
     digits={1: '1022', 2: '20220', 3: '03032(+00101)', 4: '4204(+0200)'},
     label={3: '저반 프리러너'},
     concept='맞을 생각 없이 거리를 두고 투척 무기·쇠뇌로 잡는 빌드입니다. 프리러닝 중 발사체 가속으로 투척 피해·정확성을 올리고, 망토 투명화로 다시 거리를 벌립니다.',
     playstyle='고챌 도적의 기본 선택입니다. 강화는 저격의 반지에 넣고, 이동 속도와 투명화 관리가 핵심입니다. 칼럼 기준 3-4(발사체 가속)는 필수입니다. 4티어는 연막탄만 쓰고, 죽음의 표식·그림자 분신은 "쓰지 마"입니다. 판금을 입고 전사처럼 싸우는 일반 프리러너(03203), 회피 증강 사슬 10강의 회피탱(03302)도 있습니다.',
     abwhy='칼럼에서 도적 4티어 중 유일하게 권하는 능력. 죽음의 표식·그림자 분신은 "쓰지마"',
     gear=[G('ring', None, '저반 프리러너의 핵심. 투척 무기를 강화하지 않아도 됨', U(79201, '2026-05-14'), '노강 저격반지 다수 투척무기 나옴', name='저격의 반지',
             code=C('설명문 기준', '모든 발사체 무기를 강화', f'{KO}:1116 모든 발사체 무기들을 더 강력하고 오래 사용할 수 있게 합니다')),
           G('weapon', 'Crossbow', '전 직업 종결급, 다트에 인챈트 적용', U(76982, '2026-01-31'), '쇠뇌에 안어울리는 직업이 없음'),
           G('weapon', 'Glaive', '사거리 2로 카이팅. 9챌 프리러너 무기', U(80965, '2026-07-13'), '9챌에서는 채찍이랑 글레이프만 무기로 쓰는 거임'),
           G('glyph', 'Flow', '이동 속도가 매우 높아 카이팅과 맞음', U(83664, '2026-10-04'), '흐름의 상형문자는 신이야...')]),
   'ASSASSIN': dict(ab='SMOKEBOMB', title='암살자의 칼 암살자', src=COL_RH,
     digits={1: '1022', 2: '20220', 3: '03320(+10010)', 4: '4204(+0200)'},
     label={3: '일반 암살자'},
     concept='망토로 투명화해 마음가짐을 쌓고, 암살자의 칼 기습(최소 피해 보정)으로 한 번에 지웁니다. 경량화 망토(3-2)는 사실상 유물 칸 +1입니다.',
     playstyle='노챌·재미 위주 선택입니다. 초반엔 단검 기습으로 싸우고, 4티어 암살자의 칼이 나오면 강화를 몰아줍니다. 암살자의 접근으로 먼 적에게 점멸해 암살하고, 연막탄으로 빠진 뒤 다시 마음가짐을 쌓습니다. 칼럼 기준 3-3(향상된 치사율)이 가장 중요하고, 투척이나 채찍처럼 멀리서 암살하면 3-4는 안 찍습니다.',
     abwhy='칼럼에서 도적 4티어 중 유일하게 권하는 능력',
     abcode=C('코드 계산', '빠른 후퇴 +4로 점멸 후 4턴 투명화, 투명한 동안 마음가짐이 쌓임',
              f'{JP}actors/hero/abilities/rogue/SmokeBomb.java:134 duration = 0.67f + HASTY_RETREAT; {JP}actors/buffs/Preparation.java:136 if (target.invisible > 0) turnsInvis++'),
     gear=[G('weapon', 'AssassinsBlade', '암살자는 5티어보다 암칼. 기습 최소 피해 보정으로 저점 확보', U(83682, '2026-10-04'), '암살자는 암칼이 무조건 좋아, 저점이 확보되서'),
           G('enchantment', 'Vampiric', '"무조건 흡혈". 흡혈 암칼 시드 호평', U(80609, '2026-07-03'), '무조건 흡혈'),
           G('artifact', None, '시작 유물. 투명화·마음가짐의 중심', U(80081, '2026-06-14'), '암살자의 칼에 풍요의 뿔이라 3차지만 해도 다 한방에 썰렸음', name='그림자의 망토',
             code=C('설명문 기준', '사용하면 일시적으로 완전히 투명해짐', f'{KO}:203 이 망토를 입으면 일시적으로 완전히 투명해질 수 있습니다')),
           G('artifact', None, '경량화 망토로 남는 유물 칸에. 암칼과 함께 쓴 사례', U(80081, '2026-06-14'), '암살자의 칼에 풍요의 뿔이라 3차지만 해도 다 한방에 썰렸음', name='풍요의 뿔')]),
  }},
 'HUNTRESS': {
  'builds': {
   'SNIPER': dict(ab='SPECTRALBLADES', title='강화 투척 무기 저격수', src=COL_RH,
     digits={1: '1220', 2: '10221(+10001)', 3: '00233(+20000)', 4: '4240(+0002)'},
     label={3: '투척무기 6강 빌드', 4: '활에 좋은 마부가 있다'},
     concept='투척 무기 한 묶음에 강화를 몰아 강화 공유·마법부여 공유로 저격수 특수 사격 피해를 키웁니다. 저격의 반지가 있으면 투척 무기 대신 반지에 강화를 넣는 저반 빌드(30230)로 바꿉니다.',
     playstyle='초반엔 활로 견제하고 붙은 적은 근접 공격으로 마무리합니다. 텐구 이후 투척 무기 한 묶음을 6강까지 올리고, 활 공격의 방어 무시로 단일 대상을 잡습니다. 쇠뇌를 들면 다트가 강해져 "거의 클리어 스펙"이라는 평입니다. 후반엔 유령 칼날로 활 인챈트를 광역으로 퍼뜨립니다.',
     abwhy='칼럼: 활에 좋은 인챈트가 있으면 칼날부채 4·영혼의 칼날 4로 인챈트를 광역으로 씀',
     gear=[G('weapon', 'Crossbow', '쇠뇌 들면 숲지기든 저격수든 거의 클리어 스펙', U(76982, '2026-01-31'), '쇠뇌에 안어울리는 직업이 없음'),
           G('ring', None, '있으면 저반 빌드로 전환. "저반 저격수는 무기걱정은 없음"', U(79901, '2026-06-09'), '저반 저격수는 무기걱정은 없음', name='저격의 반지'),
           G('enchantment', 'Chilling', '활에 부여. 활 인챈트 서열글에서 1티어(생장·차가운·타락)', U(84118, '2026-10-21'), '1티어 생장(황무지면 2티어) 차가운 타락'),
           G('glyph', 'Flow', '이동 속도로 거리를 유지', U(83664, '2026-10-04'), '흐름의 상형문자는 신이야...')]),
   'WARDEN': dict(ab='NATURESPOWER', title='풀숲 숲지기', src=COL_RH,
     digits={1: '1220', 2: '10221(+10001)', 3: '20330(+11000)', 4: '4024(+0020)'},
     label={4: '해로운 식물 효과 안 쓸 거다'},
     concept='긴 풀 위에서 나무껍질로 방어력을 올리고, 풀 너머 시야로 먼저 쏩니다. 숲지기는 3-4(나무껍질) 때문에 고르는 전직이라 다른 특성 선택지가 거의 없습니다.',
     playstyle='저격의 반지가 없을 때 고르는 쪽입니다. v4.0에서 나무껍질이 레벨의 50%→33%로 줄고 헤쳐진 풀에서 안 터지게 바뀌어 평가가 내려갔지만, 임프 퀘스트 금고에서는 여전히 강하다는 평입니다. 재성장 막대와 자연의 신발로 풀을 계속 만들고, 쇠뇌로 다트를 강화해 씁니다. 자연의 힘은 저격수·숲지기 모두에게 좋다는 평입니다.',
     abwhy='저격수·숲지기 구분 없이 자연의 힘이 좋다는 평. 칼럼의 해로운 식물 미사용 배분',
     gear=[G('wand', None, '풀을 만들어 나무껍질·시야 유지. 갤러리 막대 티어에서도 따로 언급', U(80692, '2026-07-06'), '숲지기 + 자연샌들 + 위장인챈 + 재생막대기 즐겜했다', name='재성장의 마법 막대'),
           G('artifact', None, 'v4.0에서 강화당 충전 속도 상향', U(83114, '2026-09-11'), '자연의 샌들, 대도의 팔찌 버프', name='자연의 신발'),
           G('weapon', 'Crossbow', '다트 강화. 실명 다트와 함께', U(76982, '2026-01-31'), '쇠뇌에 안어울리는 직업이 없음'),
           G('glyph', 'Camouflage', '풀을 계속 만들어 상시 투명화', U(80692, '2026-07-06'), '숲지기 + 자연샌들 + 위장인챈 + 재생막대기 즐겜했다'),
           G('enchantment', 'Blooming', '활에 부여. 활 서열글 1티어', U(84118, '2026-10-21'), '1티어 생장(황무지면 2티어) 차가운 타락')]),
  }},
}

for cid, spec in SPECS.items():
    p = SITE / f'data/builds/{cid}.json'
    d = json.loads(p.read_text())
    if 'summary' in spec:
        d['summary'], d['summaryTag'] = spec['summary'], '커뮤니티'
    for b in d['builds']:
        s = spec['builds'][b['subclass']]
        old = {(t['id'], t['points']): t['why'] for t in b['talents']}
        tal, bon = talents_from(cid, b['subclass'], s['ab'], s['digits'], s['label'], s['src'], old)
        b.update(title=s['title'], concept=s['concept'], talents=tal, bonus=bon, gear=s['gear'],
                 playstyle=s['playstyle'], playstyleTag='커뮤니티',
                 armorAbility={'id': s['ab'], 'why': s['abwhy'], 'tag': '커뮤니티', 'quote': f"칼럼 4티어 {s['digits'][4]}", 'src': s['src']})
        if s.get('abcode'): b['armorAbility']['code'] = s['abcode']
    p.write_text(json.dumps(d, ensure_ascii=False, indent=2) + '\n')
print('ok')
