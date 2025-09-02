#!/bin/bash
# 이슈에 자동으로 키워드(라벨+해시태그) 적용

ISSUE_NUM="${1}"
REPO="ihw33/ai-orchestra-v02"

if [ -z "$ISSUE_NUM" ]; then
    echo "Usage: ./apply_keywords.sh ISSUE_NUMBER"
    exit 1
fi

echo "🏷️ 이슈 #$ISSUE_NUM 키워드 자동 적용 시작..."

# 1. 이슈 내용 가져오기
TITLE=$(gh issue view $ISSUE_NUM -R $REPO --json title -q .title)
BODY=$(gh issue view $ISSUE_NUM -R $REPO --json body -q .body)

# 2. 키워드 추천 받기
echo "🤖 키워드 분석 중..."
RECOMMENDATIONS=$(python3 issue_keyword_recommender.py "$TITLE" "$BODY")

# 3. 라벨 추출 및 적용
LABELS=$(echo "$RECOMMENDATIONS" | grep -A1 "추천 라벨" | tail -1 | tr -d '`')
if [ ! -z "$LABELS" ]; then
    echo "📌 라벨 추가: $LABELS"
    gh issue edit $ISSUE_NUM -R $REPO --add-label "$LABELS" 2>/dev/null || echo "⚠️ 일부 라벨이 존재하지 않을 수 있음"
fi

# 4. 해시태그 추출
HASHTAGS=$(echo "$RECOMMENDATIONS" | grep "#" | grep -v "추천" | head -1)

# 5. 본문에 해시태그 추가 (기존에 없으면)
if [ ! -z "$HASHTAGS" ] && ! echo "$BODY" | grep -q "🏷️ 키워드"; then
    echo "🏷️ 해시태그 추가: $HASHTAGS"
    NEW_BODY="$BODY

## 🏷️ 키워드
$HASHTAGS"
    
    gh issue edit $ISSUE_NUM -R $REPO --body "$NEW_BODY"
fi

echo "✅ 키워드 적용 완료!"

# 6. 결과 확인
echo ""
echo "📊 적용 결과:"
gh issue view $ISSUE_NUM -R $REPO --json labels,body | python3 -c "
import json, sys
data = json.load(sys.stdin)
print('라벨:', ', '.join(l['name'] for l in data['labels']))
if '🏷️ 키워드' in data['body']:
    keywords = data['body'].split('🏷️ 키워드')[1].split('\n')[1]
    print('해시태그:', keywords)
"