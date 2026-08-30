#!/usr/bin/env bash
# 용어 해설 단독 배포본 수동 동기화.
#
#   payhug-investor-admin/glossary.html  ──변환──▶  payhug-investor-glossary/index.html  ──▶  Vercel
#
# 변환 로직은 여기 있지 않다 — payhug-investor-admin/scripts/sync_glossary.py 가 갖는다
# (시연본이 scripts/sync_prototype.py 를 원본 저장소에 두는 것과 같은 자리다).
# 검사에 하나라도 걸리면 push 하지 않는다.
#
#   bash sync_glossary.sh              빌드·게이트·push·배포 실측
#   bash sync_glossary.sh --dry-run    빌드·게이트까지만
set -euo pipefail

PIPE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SRC_REPO="${SRC_REPO:-/Users/semi/cursor/payhug-investor-admin}"
export DST_REPO="${DST_REPO:-/Users/semi/cursor/payhug-investor-glossary}"
LIVE_URL="${LIVE_URL:-https://payhug-investor-glossary.vercel.app/}"
DRY=0; [ "${1:-}" = "--dry-run" ] && DRY=1

step(){ printf '\n\033[1m▶ %s\033[0m\n' "$*"; }
die(){ printf '\n\033[31m■ 중단 — %s\033[0m\n' "$*" >&2; exit 1; }

[ -f "$SRC_REPO/scripts/sync_glossary.py" ] || die "변환기가 없다: $SRC_REPO/scripts/sync_glossary.py"
[ -d "$DST_REPO/.git" ] || die "용어 저장소가 없다: $DST_REPO"

step "1/5  변환 · 통로 차단 재적용 · 자산 동기화"
python3 "$SRC_REPO/scripts/sync_glossary.py" --dst "$DST_REPO" || die "통로 검사 실패. index.html 을 쓰지 않았다."

step "2/5  게이트 (로컬, 창 없음)"
node "$PIPE/gate_glossary.js" || die "게이트 실패. push 하지 않는다."

if [ "$DRY" = 1 ]; then printf '\n\033[33m■ --dry-run — push 하지 않았다.\033[0m\n'; exit 0; fi

step "3/5  커밋 · push"
cd "$DST_REPO"
git add -A
if git diff --cached --quiet; then
  exit 0                                  # 바뀐 것 없음 — 커밋도 push 도 배포 대기도 하지 않는다
fi
git remote get-url origin >/dev/null 2>&1 || die "원격이 없다. GitHub 저장소를 만들고 origin 을 붙인 뒤 다시 돌린다."
git -c user.email=cx@payhug.io -c user.name=Joo2n commit -q \
  -m "용어 해설 단독 배포본 동기화 — 원본 glossary.html 기준 재생성" \
  -m "상단 .tb-alt 블록(형제 문서 앵커 2건)을 다시 들어내고 제목을 배포본 것으로 맞춘다. 본문의 화면 이름 코드 표기와 캡처 참조는 그대로 두고 자산은 원본 assets 를 거울로 맞춘다.

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>"
git log --oneline -1 | sed 's/^/  /'
for i in 1 2 3; do
  git push origin main && break
  echo "  push 거절 — pull --rebase 후 재시도 ($i/3)"
  git pull --rebase origin main || die "rebase 실패. 수동 확인 필요 (force push 금지)."
  [ "$i" = 3 ] && die "push 3회 실패."
done

step "4/5  배포 반영 대기"
WANT=$(shasum -a 256 "$DST_REPO/index.html" | cut -d' ' -f1)
for i in $(seq 1 60); do
  GOT=$(curl -fsSL "$LIVE_URL" 2>/dev/null | shasum -a 256 | cut -d' ' -f1 || echo "")
  [ "$GOT" = "$WANT" ] && { echo "  반영 확인 (${i}회차)"; break; }
  [ "$i" = 60 ] && die "10분 안에 반영되지 않았다. Vercel 빌드 로그 확인."
  sleep 10
done

step "5/5  게이트 (배포 URL 실측)"
node "$PIPE/gate_glossary.js" --url="$LIVE_URL" || die "배포본 게이트 실패."

printf '\n\033[32m■ 동기화 완료 — %s\033[0m\n' "$LIVE_URL"
