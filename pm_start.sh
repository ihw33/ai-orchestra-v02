#!/bin/bash
# pm_start.sh - PM Claude 필수 시작 스크립트

echo "🤖 PM Claude 초기화 중..."

# 1. 작업 방식 확인
echo "📖 작업 방식 로딩..."
if [ -f "CLI_P_MODE_GUIDE.md" ]; then
    cat CLI_P_MODE_GUIDE.md | head -20
fi

# 2. Python 시스템 파일 확인
echo "🔧 시스템 모듈 확인:"
for file in multi_ai_orchestrator.py orchestrator.py node_system.py; do
    if [ -f "$file" ]; then
        echo "  ✅ $file"
    else
        echo "  ❌ $file 없음"
    fi
done

# 3. 현재 실행 중인 파이프라인
echo "🔄 진행 중인 자동 워크플로우:"
ps aux | grep -E "orchestrator|pipeline|relay" | grep -v grep

# 4. 최근 GitHub 활동
echo "📝 최근 GitHub 활동:"
gh issue list -R ihw33/ai-orchestra-v02 --limit 5

# 5. 활성 백그라운드 작업
echo "🌐 백그라운드 AI 작업:"
jobs -l

# 6. 오늘 할 일
echo "📋 오늘의 작업:"
if [ -f "pm_status.json" ]; then
    cat pm_status.json | python3 -m json.tool
fi

echo ""
echo "============================================"
echo "🎯 PM 핵심 명령어 (/clear 후에도 사용 가능)"
echo "============================================"
echo "  ./pm_workflow.sh \"제목\" \"설명\"  # 자동 워크플로우"
echo "  ./pm_start.sh                    # PM 모드 재시작"
echo "  cat PM_ISSUE_CREATION_GUIDE.md   # 이슈 생성 가이드"
echo "  cat PM_CRITICAL_RULES.md         # PM 규칙 확인"
echo ""
echo "✅ PM Claude 준비 완료!"