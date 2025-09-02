#!/bin/bash
# 페르소나 테스트용 이슈 생성

echo "🧪 페르소나 적용 테스트 이슈 생성"
echo "================================="

# 테스트 1: 긴급 버그 (speedster 페르소나)
gh issue create \
  --title "[긴급] 로그인 버그 빨리 수정 필요!" \
  --body "사용자가 로그인할 수 없는 심각한 버그입니다. 빨리 해결해주세요!" \
  -R ihw33/ai-orchestra-v02

# 테스트 2: 완벽한 기능 (perfectionist 페르소나)  
gh issue create \
  --title "완벽한 테스트 커버리지로 결제 시스템 구현" \
  --body "모든 엣지케이스를 처리하고, 100% 테스트 커버리지가 필요합니다." \
  -R ihw33/ai-orchestra-v02

# 테스트 3: 간단한 작업 (minimalist 페르소나)
gh issue create \
  --title "간단하게 환경변수 설정만" \
  --body "복잡하게 하지 말고 최소한의 코드로 환경변수 설정만 추가해주세요." \
  -R ihw33/ai-orchestra-v02

echo "✅ 테스트 이슈 생성 완료!"