#!/bin/bash

echo "🚀 Gemini 작업 속도 테스트"
echo "=" * 50

# 테스트 1: 간단한 텍스트 출력
echo -e "\n1️⃣ 간단한 텍스트 출력"
START=$(date +%s)
echo "Hello World" | head -1
END=$(date +%s)
echo "   시간: $((END-START))초"

# 테스트 2: 파일 생성 및 쓰기
echo -e "\n2️⃣ 파일 작업 (1000줄)"
START=$(date +%s)
for i in {1..1000}; do
    echo "Line $i" >> /tmp/speed_test.txt
done
END=$(date +%s)
echo "   시간: $((END-START))초"
rm -f /tmp/speed_test.txt

# 테스트 3: 계산 작업
echo -e "\n3️⃣ 계산 작업 (1000번)"
START=$(date +%s)
RESULT=0
for i in {1..1000}; do
    RESULT=$((RESULT + i))
done
END=$(date +%s)
echo "   결과: $RESULT"
echo "   시간: $((END-START))초"

# 테스트 4: GitHub API 호출
echo -e "\n4️⃣ GitHub API 응답 속도"
START=$(date +%s)
gh api user --jq .login > /dev/null 2>&1
END=$(date +%s)
echo "   시간: $((END-START))초"

# 테스트 5: 복잡한 작업 시뮬레이션
echo -e "\n5️⃣ 복잡한 작업 시뮬레이션"
START=$(date +%s)
# JSON 파싱, 정렬, 필터링
echo '{"items":[{"id":1,"value":100},{"id":2,"value":200}]}' | \
    python3 -c "import json,sys; data=json.load(sys.stdin); print(sum(item['value'] for item in data['items']))"
END=$(date +%s)
echo "   시간: $((END-START))초"

echo -e "\n" + "=" * 50
echo "✅ 속도 테스트 완료!"