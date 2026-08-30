#!/usr/bin/env bash
# 시연용 프로토타입 수동 동기화 — 자동화(GitHub Actions)가 도는 동안에는 쓸 일이 없다.
#
# 자동화는 payhug-investor-admin/.github/workflows/sync-prototype.yml 가 맡는다.
# 이 스크립트는 시크릿 PROTOTYPE_SYNC_TOKEN 등록 전 공백 기간과, 게이트를 깊게 돌려 보고 싶을 때 쓴다.
#
# 변환 로직은 여기 있지 않다 — payhug-investor-admin/scripts/sync_prototype.py 가 갖는다(자동화와 같은 파일).
# 검사에 하나라도 걸리면 push 하지 않는다.
#
#   bash sync_prototype.sh              빌드·게이트·push·배포 실측
#   bash sync_prototype.sh --dry-run    빌드·게이트까지만
set -euo pipefail

PIPE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SRC_REPO="${SRC_REPO:-/Users/semi/cursor/payhug-investor-admin}"
export DST_REPO="${DST_REPO:-/Users/semi/cursor/payhug-investor-prototype}"
LIVE_URL="${LIVE_URL:-https://payhug-investor-prototype.vercel.app/}"
DRY=0; [ "${1:-}" = "--dry-run" ] && DRY=1

step(){ printf '\n\033[1m▶ %s\033[0m\n' "$*"; }
die(){ printf '\n\033[31m■ 중단 — %s\033[0m\n' "$*" >&2; exit 1; }

[ -f "$SRC_REPO/scripts/sync_prototype.py" ] || die "변환기가 없다: $SRC_REPO/scripts/sync_prototype.py"
[ -d "$DST_REPO/.git" ] || die "시연본 저장소가 없다: $DST_REPO"

step "1/5  변환 · 통로 차단 재적용 · 자산 역산 복사 (자동화와 같은 스크립트)"
python3 "$SRC_REPO/scripts/sync_prototype.py" --dst "$DST_REPO" || die "통로 검사 실패. index.html 을 쓰지 않았다."

step "2/5  게이트 (로컬, 창 없음)"
node "$PIPE/gate_prototype.js" || die "게이트 실패. push 하지 않는다."

if [ "$DRY" = 1 ]; then printf '\n\033[33m■ --dry-run — push 하지 않았다.\033[0m\n'; exit 0; fi

step "3/5  커밋 · push"
cd "$DST_REPO"
git add -A
if git diff --cached --quiet; then
  echo "  바뀐 것 없음 — 커밋 건너뜀"
else
  git -c user.email=cx@payhug.io -c user.name=Joo2n commit -q \
    -m "시연용 프로토타입 동기화 — 원본 app.html 기준 재생성" \
    -m "랜딩 갤러리 제거·로고 자기 자신 고정·형제 문서 링크 해시 전환을 다시 적용하고 화면이 부르는 자산만 역산해 맞춘다.

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>"
  git log --oneline -1 | sed 's/^/  /'
fi
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
node "$PIPE/gate_prototype.js" --url="$LIVE_URL" || die "배포본 게이트 실패."

printf '\n\033[32m■ 동기화 완료 — %s\033[0m\n' "$LIVE_URL"
