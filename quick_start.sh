#!/bin/bash
# AI Orchestra v02 빠른 시작 스크립트

echo "🚀 AI Orchestra v02 - Quick Start"
echo "=================================="

# Python 확인
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3가 필요합니다"
    exit 1
fi

# GitHub CLI 확인
if ! command -v gh &> /dev/null; then
    echo "❌ GitHub CLI (gh)가 필요합니다"
    echo "설치: brew install gh"
    exit 1
fi

# 실행 권한 부여
chmod +x *.py *.sh 2>/dev/null

# 옵션 메뉴
echo ""
echo "선택하세요:"
echo "1) 🤖 대화형 모드 (Interactive Mode)"
echo "2) 📋 워크플로우 목록 보기"
echo "3) 🧪 테스트 실행"
echo "4) 📝 단일 요청 처리"
echo "5) 🔧 노드 단독 실행"
echo ""
read -p "선택 (1-5): " choice

case $choice in
    1)
        echo "🎮 대화형 모드 시작..."
        python3 master_orchestrator.py --interactive
        ;;
    2)
        echo "📋 사용 가능한 워크플로우:"
        python3 workflow_runner.py list
        ;;
    3)
        echo "🧪 테스트 실행..."
        echo ""
        echo "1. 노드 테스트:"
        python3 node_executor.py CREATE_ISSUE '{"title":"테스트 이슈"}'
        echo ""
        echo "2. 워크플로우 테스트:"
        python3 workflow_runner.py ANALYSIS_PIPELINE
        ;;
    4)
        read -p "요청 입력: " request
        python3 master_orchestrator.py "$request"
        ;;
    5)
        echo "사용 가능한 노드:"
        echo "- CREATE_ISSUE"
        echo "- KEYWORD_ENRICHMENT"
        echo "- AI_ANALYSIS"
        echo "- AI_IMPLEMENTATION"
        echo "- GENERATE_REPORT"
        echo ""
        read -p "노드 이름: " node
        read -p "파라미터 (JSON 또는 텍스트): " params
        python3 node_executor.py "$node" "$params"
        ;;
    *)
        echo "❌ 잘못된 선택"
        exit 1
        ;;
esac