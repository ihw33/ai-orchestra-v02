#!/bin/bash

# PR #29 완전 자동화: Gemini 백그라운드 실행 + GitHub 댓글

ISSUE_NUMBER=${1:-30}  # 기본값: Issue #30
EXPRESSION=${2:-"7*8"}  # 기본값: 7*8

echo "🚀 Gemini 백그라운드 실행 시작..."
echo "   Issue: #$ISSUE_NUMBER"
echo "   계산식: $EXPRESSION"

# 1. Gemini 백그라운드 실행
(
    # Gemini 실행
    RESULT=$(gemini -p "Calculate $EXPRESSION and output ONLY: @@ACK id=AUTO, @@RUN id=AUTO, @@EOT id=AUTO status=OK answer=[result]" 2>/dev/null)
    
    # 결과 파싱
    ANSWER=$(echo "$RESULT" | grep "@@EOT" | sed 's/.*answer=\([0-9]*\).*/\1/')
    
    # GitHub 댓글 자동 추가
    if [ ! -z "$ANSWER" ]; then
        gh issue comment $ISSUE_NUMBER --body "## 🤖 Gemini 자동 계산 완료

**계산식**: \`$EXPRESSION\`
**결과**: **$ANSWER**

### 처리 로그:
\`\`\`
$RESULT
\`\`\`

---
✅ 백그라운드에서 자동 처리됨
⏱️ 처리 시간: $(date '+%Y-%m-%d %H:%M:%S')"
        
        echo "   ✅ GitHub 댓글 추가 완료!"
    else
        echo "   ❌ 계산 실패"
    fi
) &

GEMINI_PID=$!
echo "   PID: $GEMINI_PID"
echo ""

# 2. 다른 작업 계속 수행
echo "💻 Claude는 다른 작업 계속 수행 중..."
for i in {1..5}; do
    echo "   다른 작업 $i..."
    sleep 1
done

# 3. Gemini 작업 완료 대기 (옵션)
echo ""
echo "⏳ Gemini 작업 완료 대기 중..."
wait $GEMINI_PID
echo "✨ 모든 작업 완료! GitHub Issue #$ISSUE_NUMBER 확인하세요."