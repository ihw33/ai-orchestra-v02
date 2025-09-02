#!/bin/bash
# 4개 Claude 오케스트레이션 실행 스크립트

echo "🎭 IWL v5 Claude Orchestra 시작..."

# 1. Master Issue 생성 (아직 없다면)
if [ "$1" == "init" ]; then
    echo "📋 Master Issue 생성 중..."
    gh issue create \
        --title "🏗️ IWL v5 Build Phase Tasks" \
        --body "$(cat <<'EOF'
# Build Phase Task Board

## 📋 Main Platform Tasks
- [ ] Database Schema 설계
- [ ] Auth System 구축  
- [ ] API Gateway 설정
- [ ] UI Components 생성

## 📚 Knowledge Base Tasks
- [ ] 콘텐츠 구조 설계
- [ ] Vector DB 설정
- [ ] 임베딩 파이프라인
- [ ] 검색 API 구현

## 🤖 LLM Tasks
- [ ] 모델 선택/설정
- [ ] Fine-tuning 데이터 준비
- [ ] Inference API 구축
- [ ] 프롬프트 템플릿

## 🔄 Integration
- [ ] KB ↔ Main 연결
- [ ] LLM ↔ Main 통합
- [ ] KB ↔ LLM 파이프라인
EOF
)" \
        -R ihw33/iwl-v5-rebuild
fi

# 2. AppleScript 실행하여 4개 세션에 명령 전송
echo "🚀 4개 Claude 세션에 작업 지시..."
osascript orchestrate_4_claudes.applescript

# 3. 상태 모니터링
echo "📊 현재 상태:"
gh issue view 1 -R ihw33/iwl-v5-rebuild | grep -E "^\- \["

echo ""
echo "✅ Orchestra 실행 완료!"
echo "💡 Tip: 각 세션에서 작업이 진행됩니다."