#!/bin/bash
# payhug-io 조직에 대한 쓰기 동작 차단 (PreToolUse / Bash)
# 허용: 읽기(clone·fetch·view·list), 그리고 데모 레포 삭제(정리 목적)
# 차단: 조직에 새 레포 생성 / 조직 원격으로 push / 회사 원본 레포에 대한 모든 쓰기
set -u
input=$(cat)
cmd=$(printf '%s' "$input" | jq -r '.tool_input.command // ""')
cwd=$(printf '%s' "$input" | jq -r '.cwd // ""')

deny() {
  printf '{"hookSpecificOutput":{"hookEventName":"PreToolUse","permissionDecision":"deny","permissionDecisionReason":"%s"}}' "$1"
  exit 0
}

# 1) 조직에 새 레포 생성 — 전면 금지
if printf '%s' "$cmd" | grep -qE 'gh[[:space:]]+repo[[:space:]]+(create|fork)[[:space:]]+[^[:space:]]*payhug-io/'; then
  deny "payhug-io 조직에 레포 생성 금지. 데모·배포용 레포는 개인 계정(Joo2n)에만 만든다."
fi

# 2) 회사 원본 레포 2개에 대한 모든 쓰기 동작 — 전면 금지 (-demo 접미사는 제외)
if printf '%s' "$cmd" | grep -qE 'payhug-io/payhug-(admin|merchant)-web([^-]|$)' \
   && printf '%s' "$cmd" | grep -qE '(git[[:space:]]+push|gh[[:space:]]+repo[[:space:]]+(delete|edit|rename|archive|transfer)|gh[[:space:]]+api[[:space:]].*(-X|--method)[[:space:]]*(POST|PUT|PATCH|DELETE)|gh[[:space:]]+(release|secret)|gh[[:space:]]+pr[[:space:]]+create|gh[[:space:]]+workflow[[:space:]]+run)'; then
  deny "회사 원본 레포(payhug-io/payhug-admin-web·payhug-merchant-web)에 대한 쓰기 동작 금지. 읽기 전용으로만 사용한다."
fi

# 3) push 대상 원격이 payhug-io를 가리키면 차단
if printf '%s' "$cmd" | grep -qE 'git[[:space:]]+push'; then
  dir=$(printf '%s' "$cmd" | grep -oE 'cd[[:space:]]+[^&;|]+' | head -1 | sed -E 's/^cd[[:space:]]+//' | tr -d "\"'" | sed 's/[[:space:]]*$//')
  [ -z "$dir" ] && dir="$cwd"
  remote=$(printf '%s' "$cmd" | sed -E 's/.*git[[:space:]]+push[[:space:]]*//' | tr ' ' '\n' | grep -vE '^-|^$' | head -1)
  [ -z "$remote" ] && remote="origin"
  if [ -d "$dir" ]; then
    url=$(git -C "$dir" remote get-url "$remote" 2>/dev/null || true)
    if printf '%s' "$url" | grep -q 'payhug-io'; then
      deny "원격 '$remote'($url)가 payhug-io를 가리킴 — 조직 푸시 금지. 개인 계정(Joo2n) 레포로만 푸시한다."
    fi
  fi
fi
exit 0
