#!/bin/bash
# PM의 직접 워크플로우 - multi_ai_orchestrator.py 없이
# 이슈 생성과 동시에 AI 실행 + 결과 자동 기록

TITLE="${1:-테스트 작업}"
DESCRIPTION="${2:-자동 생성된 작업}"
REPO="ihw33/ai-orchestra-v02"

echo "🚀 PM 직접 워크플로우 시작..."

# 1. 이슈 생성
ISSUE_URL=$(gh issue create \
  --title "[AI] $TITLE" \
  --body "$DESCRIPTION" \
  --label "ai-task,persona-speedster,parallel" \
  -R $REPO)

ISSUE_NUM=$(echo $ISSUE_URL | grep -o '[0-9]*$')
echo "✅ 이슈 #$ISSUE_NUM 생성"

# 2. AI 병렬 실행 + 결과 GitHub 기록
(
  RESULT=$(gemini -p "이슈 #$ISSUE_NUM: $DESCRIPTION 분석")
  gh issue comment $ISSUE_NUM -R $REPO --body "### ✅ Gemini (분석)
$RESULT"
  gh issue edit $ISSUE_NUM -R $REPO --add-label "ai-gemini-done"
) &

(
  RESULT=$(claude -p "이슈 #$ISSUE_NUM: $DESCRIPTION 구현")
  gh issue comment $ISSUE_NUM -R $REPO --body "### ✅ Claude (구현)
$RESULT"
  gh issue edit $ISSUE_NUM -R $REPO --add-label "ai-claude-done"
) &

(
  RESULT=$(codex exec "이슈 #$ISSUE_NUM: $DESCRIPTION 테스트")
  gh issue comment $ISSUE_NUM -R $REPO --body "### ✅ Codex (테스트)
$RESULT"
  gh issue edit $ISSUE_NUM -R $REPO --add-label "ai-codex-done"
) &

echo "✅ AI 3개 실행 + GitHub 자동 기록 중..."
echo "📍 이슈: $ISSUE_URL"

# 백그라운드 작업 대기 (선택적)
wait
echo "✅ 모든 AI 작업 완료!"