#!/bin/bash
# PM Claude의 자동화 워크플로우
# /clear 후에도 이 스크립트로 동일하게 실행 가능

# 사용법: ./pm_workflow.sh "작업 제목" "작업 설명"

TITLE="${1:-테스트 작업}"
DESCRIPTION="${2:-자동 생성된 작업}"

echo "🚀 PM 워크플로우 시작..."

# 1. 이슈 템플릿 생성
cat > /tmp/issue_temp.md << 'EOF'
## 🎯 목표
'$DESCRIPTION'

## 🎭 페르소나: speedster (⚡ 빠른 실행)
- **특성**: MVP 우선, 핵심 기능만
- **목표 시간**: 30분 내 완료

## 🔷 Node-DAG-Executor 구조

### 📊 워크플로우: Parallel (병렬 처리)
```
[ANALYZE] → [IMPLEMENT] + [TEST] → [INTEGRATE]
```

### 🔹 노드 정의
- **ANALYZE**: Gemini가 분석
- **IMPLEMENT**: Claude가 구현
- **TEST**: Codex가 테스트

## 📋 체크리스트
- [ ] 분석 완료
- [ ] 구현 완료
- [ ] 테스트 완료

## ✅ 완료 조건
1. 30분 내 작동 확인
2. 결과 GitHub 기록
EOF

# 2. 이슈 생성 및 번호 추출
echo "📝 이슈 생성 중..."
ISSUE_URL=$(gh issue create \
  --title "[AI] $TITLE" \
  --body-file /tmp/issue_temp.md \
  --label "ai-task,persona-speedster,parallel" \
  -R ihw33/ai-orchestra-v02)

ISSUE_NUM=$(echo $ISSUE_URL | grep -o '[0-9]*$')
echo "✅ 이슈 #$ISSUE_NUM 생성 완료"

# 3. AI 병렬 실행
echo "🤖 AI 3개 병렬 실행..."
gemini -p "이슈 #$ISSUE_NUM: $DESCRIPTION 분석 (speedster 모드, 5분 내)" &
claude -p "이슈 #$ISSUE_NUM: $DESCRIPTION 구현 (speedster 모드, 10분 내)" &
codex exec "이슈 #$ISSUE_NUM: $DESCRIPTION 테스트 (speedster 모드, 5분 내)" &

echo "⏳ AI 작업 진행 중..."
sleep 5

# 4. 결과 GitHub 기록
echo "📊 결과를 GitHub에 기록 중..."
gh issue comment $ISSUE_NUM -R ihw33/ai-orchestra-v02 --body "## 🤖 AI 작업 시작
- Gemini: 분석 중
- Claude: 구현 중  
- Codex: 테스트 중

작업 완료 시 각 AI가 결과 업데이트 예정"

echo "✅ PM 워크플로우 완료!"
echo "📍 이슈 확인: $ISSUE_URL"