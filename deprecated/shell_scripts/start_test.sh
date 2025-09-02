#!/bin/bash
# 실시간 테스트 시작 스크립트

echo "🎯 PM Auto Processor 실시간 테스트"
echo "=================================="
echo ""
echo "이 스크립트는 두 가지 방법으로 테스트할 수 있습니다:"
echo ""
echo "📌 방법 1: 자동 감지 테스트"
echo "   1) 새 터미널 열기"
echo "   2) python3 pm_auto_processor.py 실행"
echo "   3) 이 터미널에서: ./start_test.sh auto"
echo ""
echo "📌 방법 2: 직접 실행 테스트"
echo "   ./start_test.sh direct [이슈번호]"
echo ""
echo "=================================="

if [ "$1" == "auto" ]; then
    echo ""
    echo "🤖 자동 감지 테스트 시작..."
    echo "3초 후 테스트 이슈를 생성합니다..."
    sleep 3
    
    # 테스트 이슈 생성
    python3 test_live_demo.py --create-issue
    
    echo ""
    echo "✅ 이제 pm_auto_processor.py가 이슈를 감지해야 합니다!"
    echo "   터미널 1을 확인하세요!"
    
elif [ "$1" == "direct" ]; then
    if [ -z "$2" ]; then
        echo "❌ 이슈 번호를 입력하세요"
        echo "   예: ./start_test.sh direct 63"
    else
        echo ""
        echo "🚀 이슈 #$2 직접 처리 시작..."
        echo "실행: python3 multi_ai_orchestrator.py $2"
        python3 multi_ai_orchestrator.py $2
    fi
    
elif [ "$1" == "monitor" ]; then
    echo ""
    echo "📊 실시간 모니터링..."
    while true; do
        clear
        echo "🔄 PM 시스템 상태 ($(date '+%H:%M:%S'))"
        echo "=================================="
        
        echo "📝 최근 이슈:"
        gh issue list -R ihw33/ai-orchestra-v02 --state open --limit 3
        
        echo ""
        echo "🤖 실행 중인 프로세스:"
        ps aux | grep -E "pm_auto|orchestrator|pipeline" | grep -v grep | head -5
        
        echo ""
        echo "📊 최근 활동:"
        gh issue list -R ihw33/ai-orchestra-v02 --state all --limit 3
        
        echo ""
        echo "(Ctrl+C로 종료)"
        sleep 5
    done
    
else
    echo ""
    echo "사용법:"
    echo "  ./start_test.sh auto      - 자동 감지 테스트"
    echo "  ./start_test.sh direct 63 - 이슈 #63 직접 처리"
    echo "  ./start_test.sh monitor   - 실시간 모니터링"
fi