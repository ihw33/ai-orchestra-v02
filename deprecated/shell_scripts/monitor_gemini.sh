#!/bin/bash

# Gemini 백그라운드 실행 및 모니터링

# 1. Gemini 작업 시작
echo "🚀 Gemini 작업 시작..."
gemini -p "Write a Python function to calculate fibonacci numbers, include docstring and type hints" > /tmp/gemini_result.txt 2>&1 &
GEMINI_PID=$!
echo "   PID: $GEMINI_PID"

# 2. 다른 작업 수행하면서 주기적으로 확인
echo "💻 다른 작업 수행 중..."
for i in {1..30}; do
    # 다른 작업 시뮬레이션
    echo -n "   작업 $i 수행 중..."
    sleep 1
    
    # Gemini 상태 확인
    if ps -p $GEMINI_PID > /dev/null 2>&1; then
        echo " [Gemini 실행 중]"
    else
        echo " [Gemini 완료!]"
        break
    fi
done

# 3. 결과 확인
echo ""
echo "📋 Gemini 결과:"
echo "=================="
cat /tmp/gemini_result.txt | grep -v "Data collection" | grep -v "Loaded cached"
echo "=================="

# 4. 정리
rm -f /tmp/gemini_result.txt
echo "✨ 완료!"