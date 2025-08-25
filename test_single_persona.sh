#!/bin/bash
# 하나의 페르소나 테스트 이슈만 생성

echo "🧪 페르소나 테스트: 긴급 버그 수정"
echo "================================="

gh issue create \
  --title "[테스트] 긴급! 서버 다운 버그 빨리 수정" \
  --body "프로덕션 서버가 다운되었습니다. 매우 긴급합니다! 빨리 수정 필요!" \
  -R ihw33/ai-orchestra-v02

echo "✅ speedster 페르소나가 적용되어야 합니다"
echo "   - ⚡ 빠른 해결"
echo "   - 핵심만 구현"
echo "   - MVP 우선"