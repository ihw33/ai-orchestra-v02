#!/bin/bash
# AI 템플릿 테스트 스크립트

echo "🧪 AI Task 템플릿 테스트"
echo "================================="
echo ""
echo "GitHub에서 이슈 생성 방법:"
echo "1. https://github.com/ihw33/ai-orchestra-v02/issues/new/choose"
echo "2. 'AI Task' 템플릿 선택"
echo "3. 양식 작성:"
echo "   - 작업 유형: 기능 개발"
echo "   - 긴급도: 긴급 (speedster 페르소나)"
echo "   - 설명: 구체적인 작업 내용"
echo ""
echo "또는 CLI로 직접 생성:"
echo ""

# CLI로 AI 작업 이슈 생성
gh issue create \
  --title "[AI] 대시보드 컴포넌트 구현" \
  --body "## 작업 유형
🚀 기능 개발

## 긴급도
🔥 긴급 - 빠른 구현 필요

## 작업 설명
사용자 대시보드 React 컴포넌트 구현

## 요구사항
- 사용자 통계 표시
- 차트 라이브러리 통합
- 반응형 디자인
- 다크모드 지원

## AI 할당
- [x] Gemini - 아키텍처 설계
- [x] Claude - 구현
- [x] Codex - API 연동

## 워크플로우
병렬 처리 (3 AI 동시 작업)

@ai #feature #urgent" \
  --label "ai-task" \
  -R ihw33/ai-orchestra-v02

echo ""
echo "✅ AI 작업 이슈 생성 완료!"
echo "pm_auto_processor.py가 자동으로:"
echo "1. [AI] 태그 감지"
echo "2. speedster 페르소나 적용"
echo "3. 3개 AI 병렬 실행"