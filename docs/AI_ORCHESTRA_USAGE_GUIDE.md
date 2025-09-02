# AI Orchestra v3.0 - 완전 자동화 사용 가이드

## 🧬 새로운 기능: 재귀 성장 시스템
- **자동 노드 생성**: 필요한 노드가 없으면 AI가 자동으로 코드 생성
- **자동 DAG 구성**: 작업에 맞는 워크플로우를 AI가 자동 구성
- **학습 및 진화**: 실행 결과로부터 학습하여 지속적 개선

### 테스트 방법
```bash
# 재귀 성장 시스템 테스트
python test_recursive_growth.py
```

## 🚀 Quick Start

### 방법 1: 완전 자동 (GitHub Actions)
```bash
# 이슈 생성만 하면 모든 것이 자동!
gh issue create \
  --title "[AI] KB System 데이터베이스 영속성 구현" \
  --body "$(cat .github/ISSUE_TEMPLATE/ai-task-enhanced.md)"
```

→ 자동으로 실행되는 것들:
1. 🔗 관련 이슈 교차 링크
2. 🌿 브랜치 자동 생성
3. 📊 진행 상황 실시간 보고
4. 🤖 AI 에이전트 자동 할당
5. 🔨 코드 구현
6. 🚀 PR 자동 생성

### 방법 2: 로컬 트리거 (테스트용)
```bash
# 로컬에서 전체 워크플로우 실행
./trigger_orchestration.sh 81 feature_development
```

### 방법 3: 개별 실행 (디버깅용)
```bash
# 1. Enhanced Workflow
python dags/enhanced_ai_task_dag.py --issue 81 --title "[AI] 작업"

# 2. IWL Executor
python executors/iwl_executor.py --issue-id 81 --workflow feature_development

# 3. 개별 노드
python nodes/cross_link_issues_node.py
python nodes/auto_branch_creation_node.py
python nodes/progress_reporting_node.py
```

## 📋 이슈 템플릿 활용

### 필수 섹션
```markdown
[AI] 작업 제목

## 🔗 관련 이슈
- Parent Issue: #34
- Related: #13, #31

## 📦 구현 범위
### Backend
- [ ] API: `app/api/...`
- [ ] DB: `prisma/schema.prisma`

## 🤖 AI 역할 분담
### Gemini: 설계
### Claude: 구현
### Codex: 백엔드
```

## 🎮 이슈 코멘트 명령어

이슈에 코멘트로 명령 실행:

```bash
/ai status          # 워크플로우 상태 확인
/ai run            # 워크플로우 재실행
/ai assign gemini  # 특정 AI에게 할당
/ai report         # 진행 상황 보고 요청
```

## 🔄 워크플로우 단계

### Phase 1: 준비 (자동)
- ✅ 이슈 파싱
- ✅ 관련 이슈 링크
- ✅ 브랜치 생성
- ✅ 초기 보고

### Phase 2: AI 작업 (자동)
- 🔷 Gemini: 아키텍처 설계
- 🔵 Claude: 코드 구현
- 🔶 Codex: 백엔드 서비스

### Phase 3: 완료 (자동)
- ✅ 테스트 실행
- ✅ PR 생성
- ✅ 최종 보고

## 📊 모니터링

### 실시간 상태 확인
```bash
# 시스템 상태
python executors/iwl_executor.py --status

# 메트릭 확인
python executors/iwl_executor.py --metrics

# 이슈 진행 상황
gh issue view 81
```

### 로그 확인
```bash
# GitHub Actions 로그
gh run list --workflow="AI Orchestra"
gh run view <run_id>

# 로컬 로그
tail -f logs/orchestration.log
```

## 🛠️ 문제 해결

### 워크플로우가 시작되지 않을 때
1. 이슈 제목에 `[AI]` 태그 확인
2. GitHub Actions 활성화 확인
3. 권한 확인 (GITHUB_TOKEN)

### 브랜치 생성 실패
```bash
# 수동으로 브랜치 생성
git checkout -b feat/작업명-이슈번호
git push -u origin feat/작업명-이슈번호
```

### AI 에이전트 응답 없음
```bash
# 수동으로 트리거
python nodes/progress_reporting_node.py
```

## 🔐 환경 변수 설정

### GitHub Secrets 필요
```
GITHUB_TOKEN       # 자동 제공
OPENAI_API_KEY    # OpenAI API
ANTHROPIC_API_KEY # Claude API
GOOGLE_AI_KEY     # Gemini API
```

### 로컬 환경 (.env)
```bash
export GITHUB_TOKEN="ghp_..."
export OPENAI_API_KEY="sk-..."
export ANTHROPIC_API_KEY="sk-ant-..."
```

## 📈 성능 최적화

### 병렬 실행
- 3개 AI 동시 작업
- 노드 비동기 실행
- 캐싱 활용

### 리소스 관리
- 타임아웃: 30분
- 재시도: 3회
- 큐 관리

## 🎯 Best Practices

### DO ✅
- 이슈 템플릿 사용
- 관련 이슈 명시
- 구체적인 요구사항
- 체크리스트 활용

### DON'T ❌
- 너무 큰 작업 (분할 필요)
- 불명확한 요구사항
- 수동 개입 (자동화 활용)

## 📚 참고 문서

- [ARCHITECTURE.md](./ARCHITECTURE.md) - 시스템 구조
- [NODE_DAG_PATTERNS.md](../NODE_DAG_PATTERNS.md) - 패턴 라이브러리
- [IWL_ORCHESTRA_DETAILED_ARCHITECTURE_v2.md](./IWL_ORCHESTRA_DETAILED_ARCHITECTURE_v2.md) - 상세 아키텍처

## 💬 지원

문제가 있으면:
1. Issue 생성: `gh issue create --label bug`
2. 로그 첨부
3. 재현 단계 설명

---
🤖 AI Orchestra v3.0 - Fully Automated Orchestration System