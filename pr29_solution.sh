#!/bin/bash
# PR #29 최종 해결책

# GitHub Issue에서 계산식 추출 (예시)
EXPRESSION="$1"  # 예: "1+1"

# Gemini로 계산 실행 (비대화형)
RESULT=$(gemini -p "Calculate $EXPRESSION and output ONLY these 3 lines:
@@ACK id=ISSUE-$GITHUB_RUN_NUMBER
@@RUN id=ISSUE-$GITHUB_RUN_NUMBER  
@@EOT id=ISSUE-$GITHUB_RUN_NUMBER status=OK answer=[result]
Replace [result] with the actual calculation result." 2>/dev/null | grep "^@@")

# 결과 파싱
if echo "$RESULT" | grep -q "@@EOT.*status=OK"; then
    ANSWER=$(echo "$RESULT" | grep "@@EOT" | sed 's/.*answer=\([0-9]*\).*/\1/')
    echo "✅ 계산 성공: $EXPRESSION = $ANSWER"
    
    # GitHub Issue에 코멘트 추가
    gh issue comment "$ISSUE_NUMBER" --body "## 계산 결과
    
식: $EXPRESSION
답: $ANSWER

\`\`\`
$RESULT
\`\`\`

🤖 Processed by Gemini"
else
    echo "❌ 계산 실패"
    exit 1
fi