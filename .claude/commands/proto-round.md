---
description: 투자자 어드민 프로토타입 한 라운드 — 분석 → 적용 → 검증 → QA → 감사 → 배포
---

투자자 어드민 프로토타입을 한 라운드 돌린다. 대상: $ARGUMENTS

## 순서

**1. 분석** — `proto-analyst`
근거(스토리보드 / 실제 프론트 / 대표 정의)를 대조해 무엇을 어떻게 바꿀지 결정안을 낸다. 값은 임의로 찍지 말고 도출한다. 파일 수정 0건.

**2. 적용** — `proto-builder`
결정안을 생성기에 넣고 재생성한다. 정적 낱장도 맞춘다. 여러 조가 붙으면 파일 소유를 겹치지 않게 나눈다.

**3. 검증** — `proto-verifier`
검증기 전종 실행. FAIL마다 화면 결함인지 기준 노후인지 가른다. 통과시키려고 기준을 낮추지 않는다.

**4. QA** — `proto-qa`
실제로 눌러 보고 실제 프론트와 대조한다. DOM만 보고 판정하지 않는다. 파일 수정 0건.

**5. 감사** — `proto-auditor`
2~4번 조가 지시대로 했는지 산출물을 직접 열어 재확인한다. 보고서를 믿지 않는다. 특히 생성기에 안 들어간 `소멸위험`과 맡지 않은 곳이 깨진 `부수피해`.

**6. 정합 검사** — `proto-consistency`
화면·프로토타입·용어·정책서 사이에 서로 다른 정보가 있는지 다섯 축으로 대조한다. 숫자·용어·산식·규칙·문서 간 참조.

**7. 배포**
감사와 정합 검사에서 `미이행`·`부수피해`·`불일치` 0건이면 배포한다.

```
cd /Users/semi/cursor/payhug-investor-admin && git add -A && git commit && git push
cd /Users/semi/cursor/payhug/payhug-spec/_pipeline/investor_admin
bash sync_prototype.sh
bash sync_glossary.sh
```

배포 주소 — 전체 `payhug-investor-demo.vercel.app` / 시연 `payhug-investor-prototype.vercel.app` / 용어 `payhug-investor-glossary.vercel.app`

**8. 동기화 확인**
```
node verify_sync_chain.js --rounds=12 --gap=90
```
GitHub push 성공과 Vercel 배포 성공은 다르다. 실배포 바이트를 정본 재생성분과 대조한다.

**9. 지침 검사** — `proto-guard`
**마지막 관문.** 전역 지침·저장된 피드백·프로젝트 규칙을 읽고 산출물이 그것을 지켰는지 검사한다. 위반 0건이어야 완료다.

**10. 잔여 보고**
사용자에게 무엇이 됐고 무엇이 남았는지. 결정이 필요한 것은 따로.

## 병렬

2번에서 여러 조를 동시에 돌릴 때 **파일 소유를 배타로 나눈다.** `build_app.py`는 늘 경합하므로 블록 단위로 나누고, 편집 직전 다시 읽고 즉시 저장하게 한다.

3·4번은 동시에 돌려도 된다. 5번은 2~4가 다 끝난 뒤에.

## 절대 규칙

- 이건 **기획자가 만드는 프론트 프로토타입**이다. 화면 숫자는 우리가 정해 넣는 예시값이고 개발 명세서가 아니다
- 메뉴 라벨 변경 금지 · 화면 설명문 0건 · 파일명 노출 0건 · 죽은 버튼 0건
- 불변식 — 1,523,100,000 / 105,300,000 / 1,628,400,000 / 비중 합 100.0% / 로스터 16건
- `payhug-admin-web` · `payhug-merchant-web` 은 읽기 전용
- Figma는 화면이 굳은 뒤 마지막에
