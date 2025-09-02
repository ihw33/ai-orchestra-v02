#!/bin/bash
# PM 모니터링 스크립트 - Issue #34 진행 상황 확인

echo "🔍 PM 모니터링 시작..."
echo "================================"

# Issue #34 최신 댓글 확인
echo "📋 Issue #34 최신 상태:"
gh issue view 34 -R ihw33/iwl-v5-rebuild --comments | tail -30

echo ""
echo "================================"
echo "⏰ 다음 확인: 5분 후"
echo "💡 새 보고가 있으면 다음 작업 지시를 내리겠습니다."