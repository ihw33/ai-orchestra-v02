#!/bin/bash

# GitHub Actions 시뮬레이션 - 로컬 테스트

echo "🎯 GitHub → Gemini → GitHub 자동화 데모"
echo "=" * 60

# 1. 새 Issue 생성 (계산 요청 포함)
echo "1️⃣ GitHub Issue 생성 중..."
ISSUE_URL=$(gh issue create \
  --title "[CALC] 복잡한 계산 요청" \
  --body "Calculate: (123 * 456) + (789 - 321)" \
  --label "calculation")

ISSUE_NUMBER=$(echo $ISSUE_URL | grep -oP '\d+$')
echo "   ✅ Issue #$ISSUE_NUMBER 생성됨"

# 2. Issue에서 계산식 추출
echo ""
echo "2️⃣ Issue에서 계산식 추출..."
ISSUE_BODY=$(gh issue view $ISSUE_NUMBER --json body -q .body)
CALCULATION=$(echo "$ISSUE_BODY" | grep -oP 'Calculate:\s*\K.*' | head -1)
echo "   📐 추출된 식: $CALCULATION"

# 3. Gemini로 전송
echo ""
echo "3️⃣ Gemini로 계산 중..."
GEMINI_RESULT=$(gemini -p "Calculate $CALCULATION and output ONLY the number result" 2>/dev/null | grep -v "Data" | grep -v "Loaded" | head -1)
echo "   🧮 Gemini 결과: $GEMINI_RESULT"

# 4. 결과를 Issue에 댓글로 추가
echo ""
echo "4️⃣ GitHub Issue에 결과 댓글 추가..."
gh issue comment $ISSUE_NUMBER --body "## 🤖 Gemini 자동 계산 완료

**계산식**: \`$CALCULATION\`
**결과**: **$GEMINI_RESULT**

### 처리 단계:
1. ✅ Issue에서 계산식 추출
2. ✅ Gemini CLI로 전송 
3. ✅ 결과 파싱
4. ✅ 자동 댓글 작성

---
🔧 GitHub Actions + Gemini CLI 자동화
⏱️ 처리 시간: $(date '+%Y-%m-%d %H:%M:%S')"

echo "   ✅ 댓글 추가 완료"

# 5. 라벨 추가
echo ""
echo "5️⃣ 처리 완료 라벨 추가..."
gh issue edit $ISSUE_NUMBER --add-label "gemini-processed"
echo "   ✅ 라벨 추가 완료"

echo ""
echo "=" * 60
echo "✨ 전체 자동화 완료!"
echo "📌 Issue 확인: $ISSUE_URL"