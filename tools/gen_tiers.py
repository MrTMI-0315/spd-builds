# Build community grade blocks for spd-builds/data/tiers.js from the DC analysis outputs.
import json, sys
D = sys.argv[1]
def load(k):
    a = json.load(open(f'{D}/out_{k}_1.json')); b = json.load(open(f'{D}/out_{k}_2.json'))
    return {s: (a.get(s, {}), b.get(s, {})) for s in dict.fromkeys(list(a) + list(b))}
W, E = load('weapons'), load('enchglyph')
def n_of(v): return v.get('n_sources') if isinstance(v.get('n_sources'), int) else 0
BOW_LIST = {84118}  # bow-only enchant ranking: not evidence for melee enchants
ALIAS = {'쌍차': '쌍차', '암살자의 칼': '암칼', '특대 방패': '특', '특대 도끼': '특', '돌 건틀릿': '건틀', '징 박힌 장갑': '장갑', '전쟁 망치': '망치', '전쟁 낫': '낫', '원형 방패': '원'}
def pack(src, name, bow_ok=True):
    r, o = src.get(name, ({}, {}))
    allq = [q for q in r.get('quotes', []) + o.get('quotes', []) if bow_ok or (q['no'] not in BOW_LIST and '활' not in q['text'])]
    posts, seen = [], set()
    for q in sorted(allq, key=lambda q: (-(q.get('rec') or 0), q['date'] < '2026-08')):
        if q['no'] not in seen: seen.add(q['no']); posts.append([q['no'], q['date'][:10]])
    stem = ALIAS.get(name, name.replace('의', '').replace(' ', '')[:2])
    quote = next((q['text'] for q in allq if stem in q['text'].replace(' ', '')), '')
    return n_of(r) + n_of(o), posts[:2], quote[:70]
WEAP = {  # id: (ko name, grade, why)
 'Glaive': ('글레이브', 'S', '사거리 2로 먼저 때리는 5티어. 도달·속증·흡혈이 붙으면 핵심 무기라는 평. 요그제바전에선 사거리 이점이 줄어듦'),
 'Crossbow': ('쇠뇌', 'S', '4티어지만 5티어와 같은 가치로 봄. 전 직업 종결로 쓰이고, 쇠뇌의 인챈트가 다트에도 적용됨'),
 'AssassinsBlade': ('암살자의 칼', 'S', '기습 최소 피해 보정으로 저점이 안정적이고 5티어보다 일찍 낌. 암살자는 5티어보다 암칼이라는 의견 다수'),
 'Whip': ('채찍', 'A', '3티어지만 사거리 3으로 일방적으로 때려 저티어 종결로 쓰임. 고챌 카이팅, 흡혈·음침·탄성과 궁합'),
 'Greatshield': ('특대 방패', 'A', '맞으면서 이기는 몰빵 무기. 믿나방(방어구 금지) 챌린지에선 필수급, 광전사·결투자와 궁합'),
 'Dirk': ('더크', 'A', '유틸 무기. 결투자의 은신 점멸(조용한 발걸음)이 핵심이라 수도사·챔피언이 들고 다님. 주력 딜은 아님'),
 'Greataxe': ('특대 도끼', 'A', '빨리 들면 이기는 판이라는 5티어 범용 종결. +0 요구 힘 20이라 늦게 낀다는 게 단점'),
 'Sai': ('쌍차', 'A', '검투사 대표 조합(콤보 4연타). 3티어라 강화는 3~4강까지, 나머지는 갑옷·반지에 넣으라는 의견 다수'),
 'Gauntlet': ('돌 건틀릿', 'A', '공속 2배로 콤보를 쌓는 검투사 정석 무기. 짜릿한 인챈트와 궁합'),
 'RunicBlade': ('룬 검', 'B', '결투자·챔피언이 인챈트 효과를 키워 쓰는 무기. 기본 피해가 낮다는 평과 갈림'),
 'WarHammer': ('전쟁 망치', 'B', '명중 보정이 높아 뉴비에게 추천. 성직자 종결 사례. 고점 평가는 적음'),
 'Greatsword': ('특대검', 'B', '무난한 5티어. 강한 지지도 반대도 적음'),
 'RoundShield': ('원형 방패', 'B', '초반 방어 보강, 고챌의 채찍+원방 조합. 공속·명중 하락에 대한 불만도 있음'),
 'Scimitar': ('시미타', 'B', '챔피언이 칼춤 버프용 보조 무기로 씀'),
 'Gloves': ('징 박힌 장갑', 'B', '수도사가 완력의 반지 몰빵과 함께 쓰는 메타. 다른 직업 평가는 없음'),
 'WarScythe': ('전쟁 낫', 'C', '명중 ×0.8로 너무 안 맞는다는 불만. 정확성 반지가 있을 때만 쓸 만'),
 'Flail': ('철퇴', 'C', '기습 불가에 명중 ×0.8. 정확성 반지를 낀 결투자·성직자만 종결로 쓰고, 도적은 금지'),
 'Longsword': ('장검', 'C', '개성 없는 기본 4티어라는 평'),
 'Katana': ('도', 'C', '챔피언 말고는 쓸 데 없다는 평'),
 'BattleAxe': ('전투 도끼', 'C', '챔피언 말고는 직업 시너지가 없다는 평'),
 'Quarterstaff': ('육척봉', 'C', '초반 피해 감소용. 감옥까지 무난'),
 'Spear': ('창', 'C', '초반 사거리 무기. 짜릿한 창·고챌 결투자 사례가 소수 있음'),
 'Sickle': ('손낫', 'C', '초반 보스를 쉽게 잡았다는 후기가 있지만 명중이 낮음'),
 'Dagger': ('단검', 'C', '도적 시작 무기, 초반용'),
 'Rapier': ('레이피어', 'C', '결투자 시작 무기. 더크로 바꾸니 낫다는 후기'),
 'Cudgel': ('곤봉', 'C', '성직자 시작 무기. 수도사에겐 단검이 낫다는 의견'),
 'HandAxe': ('손도끼', 'C', '"3강 장검 있으면 노강 손도끼는 버리라" 정도의 언급뿐'),
 'Sword': ('검', 'C', '갤러리 언급 없음. DPT는 3티어 중반 1위'),
 'Shortsword': ('소검', 'C', '갤러리 언급 없음'),
 'WornShortsword': ('낡은 소검', 'C', '전사 시작 무기. 갤러리 언급 없음'),
 'Mace': ('메이스', 'C', '갤러리 언급 없음. 결투자 강타 보너스는 기습일 때만'),
}
ENCH = {
 'Vampiric': ('흡혈의', 'S', '유지력 최고. 9챌에서 흡혈 특대 방패·채찍이 없으면 못 깬다는 말까지 나옴'),
 'Projecting': ('도달의', 'A', '운이 필요 없고 거의 모든 빌드에 쓰임. 쇠뇌·채찍·글레이브와 궁합'),
 'Grim': ('음침한', 'A', '적 체력이 낮을수록 즉사. v3 시절엔 사기 인챈(S), 최근엔 운빨·막타 보조라는 평으로 한 단계 내려감'),
 'Chilling': ('차가운', 'B', '발동하면 사기라는 평과 확률상 잘 안 쌓인다는 평이 섞임'),
 'Shocking': ('짜릿한', 'B', '돌 건틀릿·검투사와 궁합, 서브 무기 채찍질과 조합 호평. 후반엔 불타는이 낫다는 의견도'),
 'Elastic': ('탄성의', 'B', '채찍·쇠뇌·창과 궁합이지만 고수용. 원거리 몹은 오히려 멀어짐'),
 'Blazing': ('불타는', 'B', '추가 피해는 좋지만 풀·문 위에서 내게 번지고 주문서를 태워 뉴비용은 아님'),
 'Corrupting': ('타락의', 'B', '근접 평가는 "음침·흡혈보다 별로"(v4.0.1 버프 이전) 정도. 활 서열에선 1티어'),
 'Vorpal': ('예리한', 'B', 'v4.0 복귀. 근접 평가는 없고, 활 서열글에서 딜 증가류 중간(2티어)'),
 'Eldritch': ('섬뜩한', 'C', '근접 평가는 없고, 활 서열글에서 집단지성 챌린지일 때만 1.5티어, 아니면 하위권'),
 'Blooming': ('생장의', 'C', '풀을 만들어 기습 유도. 근접 평가는 거의 없음(활 서열에선 1티어)'),
 'Venomous': ('맹독의', 'C', 'v4.0 리뉴얼 후 "쓸 만하다"와 "쓰레기"로 갈림'),
 'Lucky': ('행운의', 'C', '전투 평가 없음, 파밍용'),
 'Unstable': ('불안정한', 'C', '엉뚱한 때 엉뚱한 효과가 터짐. 연금 에너지로 바꾸라는 평'),
 'Blocking': ('방어의', 'C', '근접 평가는 없고, 활 서열글에서 최하위(3티어)'),
 'Kinetic': ('관성의', 'D', '"관성 나오면 삭제", 체감은 인챈트 없는 무기와 같다는 평'),
 'Crystal': ('수정', 'D', 'v4.0 신규. 근접은 20~50타에 부서져 "마부의 탈을 쓴 저주". v4.0.1 버프 뒤에도 D라는 댓글'),
}
GLY = {
 'Stone': ('육중함의', 'S', '회피 고강·신비반과 조합하면 물리 피해에 거의 면역. 방어구 금지 챌린지만 예외'),
 'Thorns': ('가시의', 'A', '고강 판금·신비반이면 출혈로 처치까지 함. 검투사 가시 판금 사례'),
 'Flow': ('흐름의', 'A', '"신이야", 9챌 노강줌 핵심. 신속함보다 훨씬 낫다는 평'),
 'Viscosity': ('점성의', 'A', '급사 방지, 후반으로 갈수록 효과. 막대 보호막·명상과 조합하면 피해를 지움'),
 'AntiMagic': ('항마의', 'B', '마법 피해만 줄여 줌. 점성·육중함 다음 상위권이라는 평도'),
 'Brimstone': ('유황불의', 'B', '불 함정·화염 걱정이 없어짐. 화염 폭발 전투 마법사가 안정성용으로 고름'),
 'Camouflage': ('위장의', 'B', '숲지기·사냥꾼은 풀을 계속 만들어 상시 발동, 재미있다는 평'),
 'Potential': ('전위의', 'B', '전투 마법사가 막대 충전·자가 보호막용으로 씀'),
 'Affection': ('애정의', 'B', '갤러리 언급 없음. 공격자를 매혹해 잠시 무력화'),
 'Swiftness': ('신속함의', 'C', '이동이 빨라 식량을 아끼는 정도. 다른 이동 수단이 있으면 효율이 낮음'),
 'Entanglement': ('속박의', 'C', '"육중함 하위호환"과 "꽤 괜찮다"로 갈림'),
 'Obfuscation': ('흐릿함의', 'C', '효과가 작아 다른 글리프가 뜨면 대개 그쪽'),
 'Repulsion': ('반발의', 'C', '"육중함보다 짜증남". 벽·문에 밀치는 응용은 소수'),
}
out = {}
for key, table, src, bow_ok in (('weaponGrades', WEAP, W, True), ('enchantments', ENCH, E, False), ('glyphs', GLY, E, True)):
    out[key] = {}
    for i, (ko, g, why) in table.items():
        n, posts, q = pack(src, ko, bow_ok)
        assert ko in src or n == 0, ko
        out[key][i] = [g, why, n if posts else 0, posts, q]
print(json.dumps(out, ensure_ascii=False, indent=1))
