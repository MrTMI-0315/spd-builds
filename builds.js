/* Builds & gear tiers page. Data: SPD_HEROES / SPD_GEAR (extracted from code), SPD_TIERS (hand-written
   judgments), SPD_BUILDS (drafted builds validated by tools/merge_builds.py). */
(async () => {
  const { T, C, $, h, srcLink, sprite, chrome, bg, button, zoomControl, SHEETS } = await window.SPD_UI;
  const HERO = window.SPD_HEROES, GEAR = window.SPD_GEAR, TIERS = window.SPD_TIERS, BUILDS = window.SPD_BUILDS || {};
  SHEETS.items = ['assets/items.png', 256, 512];
  SHEETS.talents = ['assets/talent_icons.png', 512, 128];
  SHEETS.heroes = ['assets/hero_icons.png', 128, 256];

  const TALENT = HERO.talents;
  const SUB = Object.fromEntries(HERO.subclasses.map((s) => [s.id, s]));
  const ABIL = Object.fromEntries(HERO.abilities.map((a) => [a.id, a]));
  const WEAPON = Object.fromEntries(GEAR.meleeWeapons.map((w) => [w.id, w]));
  const ARMOR = Object.fromEntries(GEAR.armor.items.map((a) => [a.id, a]));
  const ENCH = Object.fromEntries(GEAR.enchantments.items.map((e) => [e.id, e]));
  const GLYPH = Object.fromEntries(GEAR.glyphs.items.map((e) => [e.id, e]));
  const RES = Object.fromEntries(GEAR.scenarios.list.map((s) => [s.id, s.results]));

  const plain = (s) => (s || '').replace(/_/g, '').replace(/\*\*/g, '');
  const quoteText = (s) => plain(s).replace(/core\/src\/main\/java\/com\/shatteredpixel\/shatteredpixeldungeon\//g, '').replace(/core\/src\/main\/assets\/messages\//g, '');
  const enchName = (e) => e.name.ko.text.replace(/\s*%s\s*/, '').trim();
  function markup(str) {
    const out = [];
    let hl = false;
    for (const part of (str || '').split(/(_|\*\*)/)) {
      if (part === '_' || part === '**') { hl = !hl; continue; }
      if (part) out.push(h('span', { class: hl ? 'hl' : null }, part));
    }
    return out;
  }
  const TAGCLS = { '코드 계산': 'calc', '코드 확인': 'calc', '설명문 기준': 'text', '추정': 'inf', '커뮤니티': 'comm' };
  const tag = (t) => h('span', { class: `prov ${TAGCLS[t] || ''}` }, t);
  // [url, date] → "나무위키 10-27" / "DC #84430 11-04"
  const cite = ([url, date]) => h('a', { class: 'cite', href: url, target: '_blank', rel: 'noopener' },
    url.includes('namu.wiki') ? '나무위키' : `DC #${new URL(url).searchParams.get('no')}`, ` ${date.slice(5)}`);
  const DC = 'https://gall.dcinside.com/mgallery/board/view/?id=spd&no=';
  // [grade, why, mentions, [[no,date]…], quote] → evidence cell contents
  const evidence = ([, why, n, posts, q]) => [why, ' ', tag(posts.length ? '커뮤니티' : '추정'),
    posts.length ? h('span', { class: 'dim' }, ` 언급 ${n}건`) : null, ...posts.flatMap(([no, d]) => [' ', cite([DC + no, d])]),
    q ? h('div', { class: 'dim' }, `“${q}”`) : null];
  const rectSprite = (sheet, r) => sprite(sheet, Array.isArray(r) ? r : [r.x, r.y, r.w, r.h]);
  const talentIcon = (id, cls) => {
    const t = TALENT[id];
    const r = (cls && t.iconByClass && t.iconByClass[cls]) ? t.iconByClass[cls].rect || t.iconByClass[cls] : t.rect;
    const el = rectSprite('talents', r);
    el.setAttribute('data-tip', `${t.title_ko}\n\n${plain(t.desc_ko)}`);
    el.setAttribute('aria-label', t.title_ko); el.setAttribute('role', 'img'); el.removeAttribute('aria-hidden');
    el.tabIndex = 0;
    return el;
  };
  const gearSprite = (ref) => {
    const g = WEAPON[ref] || ARMOR[ref];
    return g && g.sprite ? rectSprite('items', g.sprite) : null;
  };
  const gearName = (gi) => {
    if (gi.name) return gi.name;
    const g = WEAPON[gi.ref] || ARMOR[gi.ref];
    if (g) return g.name.ko.text;
    const e = ENCH[gi.ref] || GLYPH[gi.ref];
    return e ? enchName(e) : gi.ref;
  };

  /* ---------------- header ---------------- */
  $('#meta').append(h('span', {}, `v${T.meta.version}`), h('span', {}, T.meta.commit.hash.slice(0, 7)), h('span', {}, T.meta.commit.date));
  zoomControl($('#zoom-btns'));
  $('#home-link').append(h('a', { class: 'btn', href: 'https://mrtmi-0315.github.io/spd-design-system/', style: '--bh:16;font-size:calc(6 * var(--u));text-decoration:none' }, bg('GREY_BUTTON'), h('span', { class: 'lbl' }, '디자인 시스템 ↗')));
  $('#legend').append(
    h('span', {}, tag('코드 계산'), ' 게임 코드로 계산한 값'),
    h('span', {}, tag('설명문 기준'), ' 게임 속 한국어 설명의 수치'),
    h('span', {}, tag('추정'), ' 수치를 바탕으로 한 판단'),
    h('span', {}, tag('커뮤니티'), ' DC 녹픽던 마이너 갤러리 글·댓글과 특성 칼럼(출처 링크 표시)'),
  );
  $('#foot-meta').textContent = `기준: v${T.meta.version} (커밋 ${T.meta.commit.hash.slice(0, 7)}, ${T.meta.commit.date}). 빌드 초안은 tools/merge_builds.py로 포인트 예산을 검증했습니다.`;

  const main = $('#main');
  function section(id, title, iconEl, ...kids) {
    const sec = h('section', { class: 'win', id },
      h('div', { class: 'inner' }, h('h2', { class: 'icontitle' }, iconEl, title), ...kids));
    chrome(sec, 'WINDOW');
    main.append(sec);
    $('#toc').append(h('a', { href: '#' + id, class: 'btn', style: '--bh:18;font-size:calc(6 * var(--u));justify-content:flex-start' },
      bg('GREY_BUTTON'), iconEl.cloneNode(true), h('span', { class: 'lbl' }, title)));
  }

  /* ---------------- classes ---------------- */
  const startWeapon = Object.fromEntries(GEAR.meleeWeapons.filter((w) => w.classStart).map((w) => [w.classStart.hero.toUpperCase(), w]));

  function buildCard(cls, b, verdict) {
    const sub = SUB[b.subclass];
    const ab = ABIL[b.armorAbility.id.toUpperCase()];
    const byTier = { 1: [], 2: [], 3: [], 4: [] };
    for (const t of b.talents) byTier[TALENT[t.id].tier].push(t);
    const tierBlock = (tier) => {
      const pts = byTier[tier].reduce((n, t) => n + t.points, 0);
      const lv = HERO.pointBudget.tiers[tier - 1];
      return [
        h('div', { class: 'tier-h' }, h('span', {}, `${tier}티어`), h('span', { class: 't5' }, `Lv${lv.firstPointLevel}–${lv.lastPointLevel} · ${pts}포인트`)),
        ...byTier[tier].map((t) => h('div', { class: 'talent' },
          talentIcon(t.id, cls.id),
          h('div', { class: 'tn' }, h('span', {}, TALENT[t.id].title_ko),
            h('span', { class: 'pips', 'aria-label': `${t.points}/${TALENT[t.id].maxPoints}` },
              ...Array.from({ length: TALENT[t.id].maxPoints }, (_, i) => h('i', { class: i < t.points ? 'on' : null }))),
            tag(t.tag)),
          h('div', { class: 'why' }, t.why, t.quote ? h('span', { class: 'dim' }, ` — “${quoteText(t.quote)}”`) : null, t.src ? cite(t.src) : null))),
      ];
    };
    return h('div', { class: 'build' },
      h('div', { class: 'build-head' }, rectSprite('heroes', sub.rect),
        h('div', {},
          h('div', { class: 'sub' }, sub.name_ko, verdict === b.subclass ? h('span', { class: 'verdict' }, '추천') : null),
          h('div', { class: 'ttl' }, b.title))),
      h('p', { class: 'small', style: 'margin:0' }, b.concept),
      ...[1, 2, 3].flatMap(tierBlock),
      h('div', { class: 'tier-h' }, h('span', {}, '갑옷 능력'), h('span', { class: 't5' }, 'Lv21+ · 드워프 제왕의 왕관')),
      h('div', { class: 'talent' }, rectSprite('heroes', ab.rect),
        h('div', { class: 'tn' }, h('span', { 'data-tip': plain(ab.desc_ko) }, ab.name_ko), tag(b.armorAbility.tag)),
        h('div', { class: 'why' }, b.armorAbility.why, b.armorAbility.quote ? h('span', { class: 'dim' }, ` — “${quoteText(b.armorAbility.quote)}”`) : null, b.armorAbility.src ? [' ', cite(b.armorAbility.src)] : null)),
      ...tierBlock(4),
      b.bonus && b.bonus.length ? h('div', {},
        h('div', { class: 'tier-h' }, h('span', {}, '신성한 영감의 물약 (+2)'), h('span', { class: 't5' }, '티어당 1회')),
        ...b.bonus.map((x) => h('div', { class: 'talent' }, talentIcon(x.id, cls.id),
          h('div', { class: 'tn' }, h('span', {}, `${x.tier}티어 · ${TALENT[x.id].title_ko} +${x.points}`), tag(x.tag)),
          h('div', { class: 'why' }, x.why, x.src ? [' ', cite(x.src)] : null)))) : null,
      h('div', { class: 'tier-h' }, h('span', {}, '핵심 장비'), h('span', {})),
      ...b.gear.map((gi) => h('div', { class: 'gear-row' },
        h('div', { class: 'slot' }, gearSprite(gi.ref) || h('span', {}, gi.slot)),
        h('div', {}, h('div', { class: 'tn row', style: 'gap:calc(2*var(--u))' }, h('span', {}, gearName(gi)), tag(gi.tag)),
          h('div', { class: 'small' }, gi.why, gi.quote ? h('span', { class: 'dim' }, ` — “${quoteText(gi.quote)}”`) : null, gi.src ? [' ', cite(gi.src)] : null)))),
      h('div', { class: 'tier-h' }, h('span', {}, '운영'), tag(b.playstyleTag)),
      h('p', { class: 'small', style: 'margin:0' }, b.playstyle),
    );
  }

  for (const cls of HERO.classes) {
    const B = BUILDS[cls.id];
    const iconEl = rectSprite('items', startWeapon[cls.id].sprite);
    const allTalents = [...cls.talents.t1, ...cls.talents.t2, ...cls.talents.t3,
      ...cls.subclasses.flatMap((s) => SUB[s].talents)];
    section(cls.id, cls.name_ko, iconEl,
      h('p', {}, ...markup(cls.descShort_ko)),
      h('div', { class: 'small' }, '시작 장비: ', (cls.startItems || []).map((i) => i.name_ko).filter(Boolean).join(', '), ' ', srcLink(cls.src)),
      B ? [
        h('p', { style: 'margin-top:calc(4*var(--u))' }, B.summary, tag(B.summaryTag)),
        h('p', { class: 'small' }, '서브클래스 추천: ', h('span', { class: 'hl' }, SUB[B.subclassVerdict.pick]?.name_ko || '상황에 따라'), ' — ', B.subclassVerdict.why, B.subclassVerdict.quote ? h('span', { class: 'dim' }, ` — “${quoteText(B.subclassVerdict.quote)}”`) : null, tag(B.subclassVerdict.tag), B.subclassVerdict.src ? [' ', cite(B.subclassVerdict.src)] : null),
        ...(B.subclassVerdict.community || []).map((c) => h('p', { class: 'small', style: 'margin-top:0' }, tag('커뮤니티'), ' ', c.text, ...c.src.flatMap((x) => [' ', cite(x)]))),
        h('div', { class: 'builds' }, ...B.builds.map((b) => buildCard(cls, b, B.subclassVerdict.pick))),
      ] : h('p', { class: 'pending' }, '빌드 작성 중입니다.'),
      h('details', { class: 'all' }, h('summary', { class: 't6' }, `${cls.name_ko} 특성 전체 보기 (${allTalents.length}개)`),
        h('div', { class: 'all-talents' }, ...allTalents.map((id) => h('div', { class: 'card' },
          h('div', { class: 'row', style: 'gap:calc(2*var(--u));margin-bottom:calc(1*var(--u))' }, talentIcon(id, cls.id),
            h('span', { class: 'hl t6' }, TALENT[id].title_ko), h('span', { class: 'dim' }, `${TALENT[id].tier}티어 · 최대 ${TALENT[id].maxPoints}`)),
          ...markup(TALENT[id].desc_ko))))),
    );
  }

  /* ---------------- weapon tiers ---------------- */
  // Grade = hand-written, compared within the same weapon tier (data/tiers.js weaponGrades).
  const ranked = GEAR.meleeWeapons.filter((w) => w.id !== 'MagesStaff');
  const WG = TIERS.weaponGrades, GORD = { S: 0, A: 1, B: 2, C: 3, D: 4 };
  const gradeEl = (g) => h('span', { class: `grade ${g}` }, g);
  const traits = (w) => {
    const t = [];
    if (w.ACC.value !== 1) t.push(`명중 ×${w.ACC.value}`);
    if (w.DLY.value !== 1) t.push(w.DLY.value < 1 ? `${+(1 / w.DLY.value).toFixed(2)}배 빠름` : `${+(1 / w.DLY.value).toFixed(2)}배 느림`);
    if (w.RCH.value > 1) t.push(`사거리 ${w.RCH.value}`);
    if (TIERS.weaponNotes[w.id]) t.push(TIERS.weaponNotes[w.id]);
    return t.join(' · ');
  };
  let sortKey = 'grade';
  const wBody = h('tbody');
  const byKey = (a, b) => sortKey === 'grade' ? GORD[WG[a.id][0]] - GORD[WG[b.id][0]] || WG[b.id][2] - WG[a.id][2]
    : RES[sortKey][b.id].dpt - RES[sortKey][a.id].dpt;
  const renderWeapons = () => {
    wBody.replaceChildren(...[...ranked].sort(byKey).map((w) => {
      const d = w.damage, g = WG[w.id][0];
      return h('tr', {},
        h('td', { class: 'nm' }, rectSprite('items', w.sprite), w.name.ko.text),
        h('td', {}, String(w.tier)), h('td', {}, String(w.strReq.base)),
        h('td', {}, `${d.minBase}–${d.maxBase}`),
        h('td', {}, gradeEl(g)),
        h('td', { class: 'small', style: 'min-width:calc(90*var(--u))' }, ...evidence(WG[w.id])),
        h('td', { class: 'num' }, RES.A[w.id].dpt.toFixed(2)),
        h('td', { class: 'num' }, RES.A_atReq[w.id].dpt.toFixed(2)),
        h('td', { class: 'num' }, RES.B[w.id].dpt.toFixed(2)),
        h('td', { class: 'small' }, traits(w)),
      );
    }));
    sortBar.replaceChildren(...[['grade', '등급순'], ['A', 'DPT 중반순'], ['A_atReq', 'DPT 힘 충족순'], ['B', 'DPT 후반순']].map(([k, l]) =>
      button(l, { size: 6, height: 16, pressed: k === sortKey, onclick: () => { sortKey = k; renderWeapons(); } })));
  };
  const sortBar = h('div', { class: 'sortbar' });
  const scen = GEAR.scenarios.list;
  section('weapons', '근접 무기 티어', rectSprite('items', WEAPON.Sword.sprite),
    h('p', {}, '등급은 DC 녹픽던 마이너 갤러리 글 694개(2025-09~2026-11, 댓글·추천이 달린 글)를 무기 이름으로 검색해 모은 평가를 바탕으로 매겼습니다. 갤러리처럼 티어와 상관없이 "끝까지 쓸 만한가"를 기준으로 비교했습니다. 언급 수는 그 무기를 평가한 글·댓글 수(대략)이고, 언급이 없는 무기는 추정입니다.', tag('커뮤니티')),
    h('p', { class: 'small' }, '턴당 기대 피해(DPT)는 게임 공식 그대로 계산했습니다. 명중 확률, 상대 방어(DR), 공격 속도, 힘 부족 페널티, 초과 힘 보너스를 넣었습니다.', tag('코드 계산')),
    h('ul', { class: 'small' }, ...scen.map((s) => h('li', {}, h('span', { class: 'hl' }, s.id === 'A' ? '중반' : s.id === 'B' ? '후반' : '힘 충족'), ` ${s.label_ko}`))),
    sortBar,
    h('div', { class: 'scroll-x' }, h('table', {},
      h('thead', {}, h('tr', {}, ...['무기', '티어', '힘', '피해 +0', '등급', '근거', 'DPT 중반', 'DPT 힘 충족', 'DPT 후반', '특징'].map((x) => h('th', {}, x)))),
      wBody)),
    h('p', { class: 'small', style: 'margin-top:calc(3*var(--u))' }, '마법사의 지팡이는 마법사 전용이고 융합한 막대에 따라 성능이 달라져 순위에서 뺐습니다(31종). DPT 읽는 법: 중반(힘 14)에는 힘 요구치가 낮은 3티어가 앞서고, 후반(+6, 힘 18)에는 5티어와 철퇴가 앞섭니다. 결투자 무기 능력, 인챈트, 특성, 기습, 막기는 DPT에 넣지 않았고 등급 근거와 특징 칸에서 따로 다룹니다.'),
  );
  renderWeapons();

  /* ---------------- armor ---------------- */
  section('armor', '방어구', rectSprite('items', GEAR.armor.items[4].sprite),
    h('p', {}, '방어구는 티어가 높을수록 피해 감소(DR)가 커지고, 힘이 모자라면 페널티를 받습니다. 남는 힘에는 보너스가 없습니다.', tag('코드 계산')),
    h('div', { class: 'scroll-x' }, h('table', {},
      h('thead', {}, h('tr', {}, ...['방어구', '티어', '힘 +0', 'DR +0', 'DR +6', '출처'].map((x) => h('th', {}, x)))),
      h('tbody', {}, ...GEAR.armor.items.map((a) => h('tr', {},
        h('td', { class: 'nm' }, rectSprite('items', a.sprite), a.name.ko.text), h('td', {}, String(a.tier)), h('td', {}, String(a.strReq.base)),
        h('td', { class: 'num' }, a.dr.at0.join('–')), h('td', { class: 'num' }, a.dr.at6.join('–')), h('td', {}, srcLink(a.dr.maxSrc))))))),
    h('ul', { class: 'small' },
      h('li', {}, '힘 1 부족할 때마다: 회피 ÷1.5, 이동 속도 ÷1.2, DR −2 ', srcLink(GEAR.armor.rules.lowStr[0].src)),
      h('li', {}, '직업 갑옷은 재료로 쓴 갑옷의 티어를 그대로 이어받습니다 ', srcLink(GEAR.armor.classArmor.defaultTierSrc))),
  );

  /* ---------------- enchant / glyph ---------------- */
  const pct = (v) => v == null ? '—' : Math.round(v * 100) + '%';
  function enchTable(kind, list, grades) {
    const order = { S: 0, A: 1, B: 2, C: 3, D: 4 };
    const rows = [...list].filter((e) => grades[e.id]).sort((a, b) => order[grades[a.id][0]] - order[grades[b.id][0]] || grades[b.id][2] - grades[a.id][2]);
    return h('div', { class: 'scroll-x' }, h('table', {},
      h('thead', {}, h('tr', {}, ...['이름', '등급', '희귀도', '발동 +0→+6', '효과', '근거', 'v4 변경 (원문)'].map((x) => h('th', {}, x)))),
      h('tbody', {}, ...rows.map((e) => {
        const p = e.proc || {};
        const chg = (e.changelog || []).map((c) => `${c.version}: ${plain(c.quote).replace(/"\)\);?$/, '')}`).join('\n');
        return h('tr', {},
          h('td', { class: 'nm' }, enchName(e)),
          h('td', {}, gradeEl(grades[e.id][0])),
          h('td', { class: 'small' }, `${({ common: '일반', uncommon: '고급', rare: '희귀' })[e.rarity.bucket]} ${e.rarity.weightPct}%`),
          h('td', { class: 'num' }, p.chanceAt0 != null ? `${pct(p.chanceAt0)}→${pct(p.chanceAt6)}` : '본문 참고'),
          h('td', { class: 'small', style: 'min-width:calc(80*var(--u))' }, e.desc.ko.text),
          h('td', { class: 'small', style: 'min-width:calc(90*var(--u))' }, ...evidence(grades[e.id])),
          h('td', { class: 'small', style: 'white-space:pre-line;min-width:calc(60*var(--u))' }, chg || '—'));
      }))));
  }
  section('enchants', '무기 인챈트', h('span', {}, rectSprite('items', WEAPON.RunicBlade.sprite)),
    h('p', {}, '발동 확률과 희귀도는 코드에서 계산했습니다. 등급은 DC 녹픽던 갤러리 평가(근접 무기 기준)로 매겼습니다. 활(영혼의 활) 기준 평가는 빼고, 근접 평가가 없으면 추정으로 표시했습니다. v4.0 이전 글은 v4.0에서 바뀐 인챈트(맹독·예리·수정·타락·섬뜩·생장)에 대해서는 참고만 했습니다. 저주는 뺐습니다.', tag('코드 계산'), tag('커뮤니티')),
    enchTable('enchantments', GEAR.enchantments.items, TIERS.enchantments));
  section('glyphs', '방어구 글리프', rectSprite('items', GEAR.armor.items[2].sprite),
    h('p', {}, '등급 기준은 인챈트와 같습니다. 글리프는 v4.0에서 바뀌지 않아 v3.x 시절 글(2026-05 "상형문자 청문회" 연재 포함)도 그대로 썼습니다. 확률 대신 조건으로 발동하는 글리프는 "본문 참고"로 표시했습니다.', tag('코드 계산'), tag('커뮤니티')),
    enchTable('glyphs', GEAR.glyphs.items, TIERS.glyphs));

  /* ---------------- method ---------------- */
  const PB = HERO.pointBudget;
  // Korean restatement of gear.json scenarios[].choice
  const SCEN_NOTE = {
    A: '힘 14 = 시작 10 + 12층까지 끝낸 두 구간(5층마다)의 보장 힘 물약 4개. 4~5티어 무기는 힘이 모자라 페널티를 받습니다.',
    A_atReq: '힘을 각 무기의 요구치에 딱 맞춘 비교용 조건입니다.',
    B: '힘 18 = 시작 10 + 20층까지 보장되는 힘 물약 8개. 무기는 +6으로 가정했습니다.',
  };
  section('method', '기준 · 한계', rectSprite('items', WEAPON.Sword.sprite),
    h('h3', {}, '특성 포인트'),
    h('ul', { class: 'small' },
      ...PB.tiers.map((t) => h('li', {}, `${t.tier}티어: Lv${t.firstPointLevel}–${t.lastPointLevel}, ${t.points}포인트`)),
      h('li', {}, '3티어는 서브클래스(텐구의 가면), 4티어는 갑옷 능력(드워프 제왕의 왕관)을 고른 뒤에 열립니다. ', srcLink(PB.locks.src)),
      h('li', {}, '신성한 영감의 물약으로 한 티어에 +2, 티어당 1회 더 받을 수 있습니다.'),
      h('li', {}, srcLink(PB.tierLevelThresholdsSrc))),
    h('h3', {}, 'DPT 시나리오'),
    h('ul', { class: 'small' }, ...scen.map((s) => h('li', {}, `${s.label_ko} — 영웅 명중 ${s.attackSkill}. ${SCEN_NOTE[s.id] || ''}`))),
    h('ul', { class: 'small' },
      ...Object.entries(GEAR.scenarios.mobs).map(([, m]) => h('li', {}, `${m.name.text}(${m.depth}층): 회피 ${m.defenseSkill}, DR 0–${m.drMax} `, srcLink(m.defenseSrc)))),
    h('h3', {}, '계산에서 뺀 것'),
    h('ul', { class: 'small' },
      h('li', {}, '인챈트, 글리프, 특성, 반지, 결투자 무기 능력, 기습 공격, 결투자 충전'),
      h('li', {}, '막기 무기(방패, 육척봉, 도, 레이피어)는 공격력만 계산'),
      h('li', {}, '적 1명과의 정지 상태 전투만 가정: 적의 반격, 회복, 영웅의 방어구는 계산하지 않음'),
      h('li', {}, '몬스터는 기본 능력치 기준: 나무껍질 피부, 챔피언, 상승 보정 제외')),
    h('h3', {}, '커뮤니티 자료'),
    h('ul', { class: 'small' },
      h('li', {}, 'DC 녹픽던 마이너 갤러리(id=spd)를 무기·인챈트·글리프·전직·갑옷 능력 이름 등 키워드 116개로 검색했습니다. 댓글이나 추천이 달린 글 694개(2025-09-29~2026-11-05)의 본문과 댓글 5,238개를 모아 항목별로 평가를 정리했습니다.'),
      h('li', {}, '전사·마법사·도적·사냥꾼 특성 배분은 갤러리 칼럼 "녹픽던 특성 공략 최신판"(#82739, #82783, 2026-08 v4.0 베타 시점)을 그대로 따랐습니다. 숫자 배분과 특성 순서는 칼럼 설명문으로 검증했습니다. v4.0 정식판에서 바뀐 특성은 수치뿐이라 배분은 그대로 유효합니다. 결투자·성직자는 칼럼이 아직 없어 특성을 바꾸지 않았습니다.'),
      h('li', {}, '언급 수는 그 항목을 평가한 글·댓글 수를 대략 센 값입니다. 추천 수는 대부분 0~20이라, 많이 언급될수록 믿을 만하다는 정도로 읽어 주세요. 다른 변형 게임(총픽던, 블픽던 등) 글은 뺐습니다.'),
      h('li', {}, 'v4.0.x에서는 근접 무기와 글리프가 바뀌지 않아 v3.x 시절 글도 그대로 썼습니다. v4.0에서 바뀐 인챈트(맹독·예리·수정·타락·섬뜩·생장), 숲지기 나무껍질, 수도사는 v4.0 베타(2026-08) 이후 글을 우선했습니다.'),
      h('li', {}, '레딧과 공식 블로그는 자동 접속이 막혀 보지 못했습니다.')),
  );
})();
