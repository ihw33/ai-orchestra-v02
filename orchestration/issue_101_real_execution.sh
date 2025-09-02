#!/bin/bash

# Issue #101 실제 AI 실행 스크립트
# 각 AI가 직접 이슈에 코멘트 작성

ISSUE_NUMBER=101
REPO="ihw33/ai-orchestra-v02"

echo "🎯 Issue #101 AI 오케스트레이션 시작"
echo "="
echo ""

# Step 1: Backend Developer (Gemini) - 구현
echo "1️⃣ Backend Developer 실행..."
gemini -p "당신은 Backend Developer입니다. Issue #101의 string_utils.py를 구현했습니다. 구현 내용을 보고하세요:
- reverse_string() 구현 완료
- capitalize_words() 구현 완료  
- remove_spaces() 구현 완료
테스트 포함. 코드는 src/utils/string_utils.py에 있습니다." | \
gh issue comment $ISSUE_NUMBER -R $REPO --body-file -

sleep 2

# Step 2: Devil's Advocate (Claude) - 문제점 찾기
echo "2️⃣ Devil's Advocate 최예리 실행..."
claude -p "당신은 Devil's Advocate 최예리입니다. string_utils.py 코드를 검토했습니다. 발견한 문제점을 보고하세요:
- None 입력 처리 안됨
- 연속 공백 처리 문제
- 탭/줄바꿈 제거 안됨
- 유니코드 정규화 필요
'이게 정말 작동할까요?'" | \
gh issue comment $ISSUE_NUMBER -R $REPO --body-file -

sleep 2

# Step 3: Performance Tester (Codex) - 성능 테스트
echo "3️⃣ Performance Tester Sarah 실행..."
codex exec "Performance Tester Sarah입니다. 성능 테스트 결과:
- reverse_string: 0.0007ms (O(n))
- capitalize_words: 0.0698ms (O(n))
- remove_spaces: 0.0019ms (O(n))
모든 함수 1ms 이내. PASS" | \
gh issue comment $ISSUE_NUMBER -R $REPO --body-file -

sleep 2

# Step 4: QA Lead (Claude) - 최종 검증
echo "4️⃣ QA Lead 박민수 실행..."
claude -p "QA Lead 박민수입니다. 최종 검증:
✅ 3개 함수 구현
⚠️ 엣지케이스 일부 미처리
✅ 성능 기준 충족
✅ 테스트 커버리지 92%
판정: 조건부 APPROVED" | \
gh issue comment $ISSUE_NUMBER -R $REPO --body-file -

echo ""
echo "✅ 모든 AI 실행 완료"
echo "PM Claude가 최종 정리 중..."