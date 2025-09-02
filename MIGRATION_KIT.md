# 🚀 AI Orchestra v02 이식 가이드

## 📋 이식 전 체크리스트

### 필수 요구사항
- [ ] GitHub CLI 설치 (`gh`)
- [ ] Python 3.8+ 설치
- [ ] AI CLI 도구들 설치
  - [ ] gemini CLI
  - [ ] codex CLI
  - [ ] claude CLI
  - [ ] cursor CLI (선택)
  - [ ] chatgpt CLI (선택)

### 대상 프로젝트 준비
- [ ] GitHub 레포지토리 생성
- [ ] Git 초기화
- [ ] 기본 폴더 구조 생성

## 📦 이식 키트 구성

### 1. 핵심 파일 (필수)
```bash
# 이식할 파일 목록
ai-orchestra-v02/
├── orchestrator.py          # 자연어 분석 엔진
├── node_system.py           # 노드 시스템
├── process_engine.py        # 프로세스 엔진
├── metrics_system.py        # 메트릭 수집
├── trigger_system.py        # 트리거 시스템
├── multi_ai_orchestrator.py # AI 실행 로직
├── evolution_logger.py      # 진화 시스템 로거
├── EVOLUTION_SYSTEM.md      # 진화 시스템 문서
├── learned_patterns.json    # 학습된 패턴
├── learned_dag_patterns.json # 학습된 DAG 패턴
└── personas/                # 페르소나 조직도
    ├── iwl_team/           # 이력서 포함 팀
    ├── persona_loader.py   # 페르소나 로더
    ├── subagent_selector.py # AI 선택기
    ├── auto_persona_injector.py # 자동 페르소나 주입
    └── iwl_recursive_growth_system.py # 재귀 성장 시스템
```

### 2. GitHub 이슈 템플릿 (필수)
```bash
.github/ISSUE_TEMPLATE/
├── ai_task.yml             # AI 작업 메인 템플릿
├── ai-task-enhanced.md     # 향상된 AI 작업
├── bug.yml                 # 버그 보고
├── epic.yml                # 에픽 생성
├── general_task.yml        # 일반 작업
└── mvp_task.yml           # MVP 작업
```

### 3. 프로젝트별 스크립트 (커스터마이징 필요)
```bash
# StockIQ에서 실제 사용 중인 파일들
├── multi_ai_orchestrator.py  # 메인 오케스트레이터 (수정 필요)
├── stockiq_pm.sh             # PM 작업 통합 스크립트
├── run_ai_orchestra.sh       # 수동 실행 스크립트
└── CLAUDE.md                 # PM 역할 정의
```

## 🧬 재귀적 성장 시스템 (핵심 기능)

### 자동 페르소나 적용
- **auto_persona_injector.py**: 작업 내용 분석 → 적절한 페르소나 자동 선택
- **subagent_selector.py**: 키워드 기반 서브에이전트 자동 매칭
- **persona_loader.py**: 30+ 페르소나 로드 및 관리

### 재귀적 협업 프로세스
- **iwl_recursive_growth_system.py**: AI들이 작업하며 경험치 획득
- **evolution_logger.py**: 성장 단계 추적 (🥚→🐣→🐥→🦆→🦅→🐉)
- **learned_patterns.json**: 학습된 패턴 자동 재사용

### 작동 방식
```python
# 1. 이슈 생성 시 자동 페르소나 주입
persona = auto_persona_injector.inject(issue_content)

# 2. 작업 수행 시 경험치 획득
growth_system.process_task_completion(persona_id, task, success_rate)

# 3. 레벨업 시 새로운 스킬 학습
if level_up:
    new_skills = growth_system.discover_new_skills(persona, task)

# 4. 다른 AI에게 지식 전수
knowledge_transfer = growth_system.transfer_knowledge(mentor, mentee)
```

## 🔧 이식 단계별 가이드

### Step 1: 기본 구조 생성
```bash
cd [대상프로젝트]
mkdir -p ai_orchestra/personas
mkdir -p .github/ISSUE_TEMPLATE
```

### Step 2: 핵심 파일 복사
```bash
# 이식 스크립트 실행
./migrate.sh [대상프로젝트경로]

# 또는 수동 복사
cp -r ai-orchestra-v02/personas/iwl_team [대상]/ai_orchestra/personas/
cp -r ai-orchestra-v02/.github/ISSUE_TEMPLATE/* [대상]/.github/ISSUE_TEMPLATE/
```

### Step 3: 프로젝트별 설정
```python
# multi_ai_orchestrator.py 수정
class YourProjectOrchestrator:
    def __init__(self):
        self.repo = "your-github/your-repo"  # 수정!
        self.ais = {
            # 프로젝트에 맞게 AI 역할 수정
        }
```

### Step 4: PM 스크립트 설정
```bash
# stockiq_pm.sh → your_project_pm.sh로 이름 변경
chmod +x your_project_pm.sh
```

### Step 5: 테스트
```bash
# 상태 확인
./your_project_pm.sh status

# 테스트 이슈 생성
./your_project_pm.sh create "테스트" "테스트 내용"

# 실행
./your_project_pm.sh run [이슈번호]
```

## ⚠️ 주의사항

### 하지 말아야 할 것
1. **자동 모니터링 설정 금지** - PM과 상의하며 수동 실행
2. **기존 작업 파일 덮어쓰기 금지** - 프로젝트 고유 파일 보호
3. **무분별한 파일 삭제 금지** - 필요한 파일 확인 후 정리

### 확인해야 할 것
1. **GitHub 레포 권한** - 이슈 생성/수정 권한 필요
2. **AI CLI 경로** - 각 AI 도구가 PATH에 있는지 확인
3. **Python 의존성** - 필요한 패키지 설치 확인

## 🐛 문제 해결

### AI CLI가 실행되지 않을 때
```bash
which gemini
which codex
which claude
# 없으면 설치 필요
```

### GitHub 이슈 접근 실패
```bash
gh auth status
# 로그인 필요시
gh auth login
```

### Python 모듈 임포트 에러
```bash
# sys.path에 경로 추가
sys.path.append('[프로젝트]/ai_orchestra')
```

## 📝 프로젝트별 커스터마이징

### StockIQ 예시
- Graph RAG 중심 작업
- 투자 데이터 분석 특화
- 5개 핵심 AI 사용

### IWL v5 예시
- 교육 플랫폼 중심
- 8×4 매트릭스 구조
- 학습 모듈 개발

## 🚀 빠른 시작 명령어
```bash
# 한 줄로 이식 시작
curl -L https://raw.githubusercontent.com/ihw33/ai-orchestra-v02/main/migrate.sh | bash -s [대상프로젝트]
```

---
**버전**: v2.0
**최종 업데이트**: 2024-09-01
**문의**: ihw33/ai-orchestra-v02 이슈 생성