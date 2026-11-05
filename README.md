# SPD 빌드 · 장비 티어 (비공식)

[Shattered Pixel Dungeon](https://github.com/00-Evan/shattered-pixel-dungeon) v4.0.2(커밋 `57a4e06`) 기준 직업별 추천 빌드와 무기·방어구·인챈트·글리프 티어표입니다.
화면은 [SPD 디자인 시스템](https://mrtmi-0315.github.io/spd-design-system/)의 부품(`ui.js`, `ui.css`)으로 그립니다.

모든 항목에 근거 종류를 붙였습니다: **코드 계산**(게임 공식으로 계산), **설명문 기준**(게임 속 한국어 설명의 수치), **추정**(판단).
수치는 게임 코드에서 계산했고, 장비 등급·서브클래스 추천·특성 배분은 DC 녹픽던 마이너 갤러리 글 694개(2025-09~2026-11)와 특성 칼럼(#82739, #82783)을 근거로 원글 링크와 함께 정리했습니다(`data/tiers.js`, `data/builds/*.json`).

## 데이터 다시 만들기

```sh
git clone --depth 1 https://github.com/00-Evan/shattered-pixel-dungeon.git
python3 -I tools/extract.py shattered-pixel-dungeon         # tokens.* (디자인 토큰, 9-patch)
python3 -I tools/extract_gear.py shattered-pixel-dungeon    # data/gear.*: 무기 DPT(시나리오 3개), 방어구, 인챈트, 글리프
python3 -I tools/extract_heroes.py shattered-pixel-dungeon  # data/heroes.*: 직업, 서브클래스, 갑옷 능력, 특성 160개
python3 -I tools/merge_builds.py                            # data/builds/*.json 검증 → data/builds.js
```

- `data/builds/*.json`: 직업별 빌드(판단 포함). 작성 지침은 `tools/BUILD_BRIEF.md`.
- `data/tiers.js`: 인챈트·글리프 등급(추정)과 무기 특수 효과 설명. 직접 작성한 파일입니다.

## 라이선스

`assets/`의 이미지와 `pixel_font.ttf`는 Shattered Pixel Dungeon(© Evan Debenham, 원작 Pixel Dungeon © Watabou)에서 가져왔고 GPLv3를 따릅니다. 이 저장소도 GPLv3입니다(`LICENSE`). 공식 공략이 아니며 개발자와 관련이 없습니다.
