# AI Orchestra v3.0 Architecture (2025-08-28 Updated)

## 🏗️ 전체 시스템 구조

### 3대 핵심 프로젝트
1. **ai-orchestra-v02**: 오케스트레이션 코어 엔진
2. **iwl-v5-rebuild**: IWL 교육 플랫폼 (Main Platform)
3. **iwl-kb-system**: 지식 기반 시스템 (KB System)
4. **ai-engine-hub**: LLM 서비스 허브 (LLM Service)

## 핵심 철학: Node-DAG 기반 재귀 성장형 자동화

> **"모든 작업은 Node로, 모든 프로세스는 DAG로, 모든 실행자는 성장하는 Persona로"**

### 왜 Node-DAG-Executor 패턴인가?
- **Node**: 재사용 가능한 작업 단위로 모듈화
- **DAG**: 복잡한 워크플로우를 의존성 그래프로 표현
- **Executor**: 30명 페르소나가 자율적으로 학습하며 성장
- **재귀 성장**: 작업 경험이 자동으로 스킬과 지식으로 전환

## 네이밍 체계

| 구분 | 이름 | 역할 | 사용 맥락 |
|------|------|------|-----------|
| **내부 코어** | OrchestrEX | 실행 엔진, 프로토콜 처리 | 코드, 기술 문서 |
| **운영 UI** | FlowCTRL | 대시보드, 모니터링 | 코드, 기술 문서 |
| **브랜드명** | AI Orchestra | 전체 시스템 통칭 | 외부 커뮤니케이션, 마케팅 |

## 프로젝트 구분

### OrchestrEX (이 저장소)
**내부 코어 엔진** - AI 간 통신의 실행 레이어

- **역할**: 실제 명령 실행, 통신 프로토콜 처리, 어댑터 관리
- **기술**: Python, tmux, AppleScript
- **핵심 기능**:
  - 3-step handshake (@@ACK/@@RUN/@@EOT)
  - EXEC DSL 파싱 및 검증
  - 멱등성/재시도 메커니즘
  - 다양한 AI 어댑터 (tmux, Claude, ChatGPT 등)

### FlowCTRL (별도 저장소)
**대시보드/운영 툴** - 프로세스 정의 및 오케스트레이션

- **역할**: 프로세스 정의, 루틴 실행, 상태 집계
- **기술**: Next.js, React, WebSocket
- **핵심 기능** (프로세스 = 기능):
  - **세션 등록/관리**: 각 챗봇/워크플로우 세션 식별 (claude@planning, chatgpt@analysis)
  - **작업 큐잉**: EXEC 항목을 세션별로 push → 실행 후 ack/eot 반환
  - **상태 모니터링**: 진행 중/성공/실패/재시도 필요 여부 표시
  - **루틴 실행**: 반복 업무를 EXEC 패턴으로 저장·재사용 (PR 리뷰, smoke-test 등)
  - **PM 역할**: EXEC 배치/순서/조건 관리, 세션별 분배 orchestration

## EXEC DSL 사양

### 문법 정의 (BNF)
```bnf
EXEC_LINE  ::= VERB PARAMS [PAYLOAD]
VERB       ::= "TEST" | "IMPLEMENT" | "ANALYZE" | "REVIEW" | 
               "DEPLOY" | "MONITOR" | "ROLLBACK" | "REPORT"
PARAMS     ::= KEY "=" VALUE { " " KEY "=" VALUE }
KEY        ::= [a-zA-Z_][a-zA-Z0-9_]*
VALUE      ::= [a-zA-Z0-9._-]+ | '"' [^"]* '"'
PAYLOAD    ::= "--" NEWLINE MULTILINE_TEXT
```

### 예약어 및 공통 파라미터
```yaml
# 필수 파라미터
task_id: string     # 멱등성 키 (중복 실행 방지)

# 선택 파라미터
priority: high|normal|low
timeout: number     # 초 단위, 기본값 30
retry: number       # 재시도 횟수, 기본값 3
async: boolean      # 비동기 실행 여부
```

### EXEC 명령 예시
```bash
# 단순 테스트
TEST task_id=T001 module=auth

# 복잡한 구현
IMPLEMENT task_id=I002 feature=oauth provider=google scope="email profile"

# 페이로드 포함
ANALYZE task_id=A003 type=security --
def vulnerable_function(user_input):
    exec(user_input)  # Dangerous!
    return "done"
```

## 3-Step Handshake Protocol

### 정상 플로우
```
1. ACK (Acknowledgment) - 5초 타임아웃
   송신: EXEC_TASK_001 TEST module=auth
   수신: @@ACK:TASK_001

2. RUN (Execution Start) - 10초 타임아웃
   수신: @@RUN:TASK_001

3. EOT (End of Transmission) - 30초 타임아웃
   수신: @@EOT:TASK_001:SUCCESS
```

### 에러 플로우
```
# 타임아웃 에러
송신: EXEC_TASK_002 DEPLOY service=api
수신: @@ACK:TASK_002
수신: @@RUN:TASK_002
(30초 경과)
시스템: @@EOT:TASK_002:TIMEOUT:Max wait exceeded

# 실행 실패
송신: EXEC_TASK_003 TEST module=broken
수신: @@ACK:TASK_003
수신: @@RUN:TASK_003
수신: @@EOT:TASK_003:ERROR:ModuleNotFoundError

# 검증 실패 (ACK 전)
송신: EXEC_TASK_004 INVALID_VERB
수신: @@EOT:TASK_004:INVALID:Unknown verb INVALID_VERB
```

### 에러 코드 체계
| 코드 | 설명 | 복구 방법 |
|------|------|-----------|
| TIMEOUT | 응답 시간 초과 | 재시도 또는 타임아웃 증가 |
| ERROR | 실행 중 오류 | 에러 메시지 확인 후 수정 |
| INVALID | 문법/검증 오류 | EXEC 명령 수정 |
| DUPLICATE | 중복 실행 시도 | 캐시된 결과 사용 |
| UNAUTHORIZED | 권한 없음 | 권한 확인 |
| RATE_LIMITED | 요청 제한 초과 | 대기 후 재시도 |

## 보안 및 검증 계층

### Validator 역할
```python
class ExecValidator:
    def validate(self, exec_line: str) -> ValidationResult:
        # 1. 문법 검증
        if not self.is_valid_syntax(exec_line):
            return ValidationResult(False, "INVALID_SYNTAX")
        
        # 2. VERB 화이트리스트 체크
        verb = self.extract_verb(exec_line)
        if verb not in ALLOWED_VERBS:
            return ValidationResult(False, "UNKNOWN_VERB")
        
        # 3. 파라미터 검증
        params = self.extract_params(exec_line)
        if not self.validate_params(verb, params):
            return ValidationResult(False, "INVALID_PARAMS")
        
        # 4. 권한 체크
        if not self.check_permissions(verb, params):
            return ValidationResult(False, "UNAUTHORIZED")
        
        # 5. Rate limiting
        if self.is_rate_limited(params['task_id']):
            return ValidationResult(False, "RATE_LIMITED")
        
        return ValidationResult(True, "OK")
```

### 보안 조치
1. **Command Injection 방지**: Base64 인코딩으로 특수문자 이스케이프
2. **Input Sanitization**: 모든 파라미터 값 검증
3. **Rate Limiting**: IP/세션별 요청 제한
4. **Audit Logging**: 모든 EXEC 명령 기록
5. **Sandboxing**: 어댑터별 격리 실행 환경

## FlowCTRL ↔ OrchestrEX 인터페이스

### 요청 스키마
| 필드 | 타입 | 필수 | 설명 |
|------|------|------|------|
| task_id | string | ✓ | 고유 작업 식별자 |
| exec | string | ✓ | EXEC DSL 명령 |
| target | string | ✓ | 대상 어댑터 (claude, chatgpt, tmux) |
| timeout | number | | 제한 시간 (초), 기본값 30 |
| priority | string | | 우선순위 (high/normal/low) |
| callback_url | string | | 완료 시 웹훅 URL |

### 응답 스키마
| 필드 | 타입 | 설명 |
|------|------|------|
| task_id | string | 요청한 작업 ID |
| status | string | SUCCESS / ERROR / TIMEOUT |
| duration | number | 실행 시간 (초) |
| output | string | 실행 결과 |
| error | object | 에러 상세 (status가 ERROR일 때) |
| metrics | object | 성능 메트릭 |

### 워크플로우 정의 (YAML)
```yaml
# FlowCTRL에서 정의하는 워크플로우
name: feature_development
version: 1.0
tasks:
  - id: design
    exec: ANALYZE task_id=D001 type=requirements
    target: claude
    
  - id: implement
    exec: IMPLEMENT task_id=I001 feature=login
    target: chatgpt
    depends_on: [design]
    
  - id: test
    exec: TEST task_id=T001 module=login
    target: codex
    depends_on: [implement]
    
  - id: review
    exec: REVIEW task_id=R001 pr=123
    target: gemini
    depends_on: [test]
    
conditions:
  - if: test.status == "FAILED"
    then: rollback
    
error_handlers:
  - on: TIMEOUT
    retry: 3
    backoff: exponential
```

### 루틴 실행 예시
```yaml
# pm_session.yaml - 자동화된 PM 루틴
name: daily_pr_review
version: 1.0
triggers:
  - type: schedule
    cron: "0 9 * * *"  # 매일 오전 9시
  - type: webhook
    event: pull_request.opened  # PR 생성 시
  - type: exec
    command: TRIGGER routine=daily_pr_review  # 다른 AI가 트리거

sessions:
  - name: pm@orchestrator
    type: claude
    role: project_manager  # PM도 AI 세션
    
  - name: claude@planning
    type: claude
    role: planner
    
  - name: chatgpt@analysis  
    type: chatgpt
    role: analyzer
    
  - name: gemini@testing
    type: gemini
    role: tester

routine:
  # PM이 먼저 상황 판단
  - id: assess-001
    target: pm@orchestrator
    exec: |
      ANALYZE task=check_pr_queue repo=ai-orchestra-v02
      timeout_s=60
      
  # PM 판단에 따라 조건부 실행
  - id: plan-001
    target: claude@planning
    exec: |
      IMPLEMENT task=pr_review repo=ai-orchestra-v02 id=pr-14
      timeout_s=300
    condition: assess-001.output contains "needs_review"
      
  - id: analyze-001
    target: chatgpt@analysis
    exec: |
      ANALYZE task=code_quality pr=14 metrics=complexity,coverage
      timeout_s=180
      
  - id: test-001
    target: gemini@testing
    exec: |
      TEST task=smoke_test suite=core id=smk-01
      timeout_s=120

# 실행 흐름:
# 1. 트리거 발생 (시간/이벤트/명령)
# 2. PM AI가 먼저 상황 분석
# 3. 각 EXEC가 조건에 따라 큐에 들어감
# 4. 세션들이 받아서 실행 → @@ACK / @@RUN / @@EOT 반환
# 5. FlowCTRL이 결과 집계 및 다음 트리거 준비
# → 완전 자동화, 인간 개입 불필요
```

## 🏛️ 최신 아키텍처 다이어그램 (2025-08-28)

```
┌──────────────────────────────────────────────────────────────────┐
│                        IWL v5.0 ECOSYSTEM                         │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │                    iwl-v5-rebuild (Main)                    │ │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  │ │
│  │  │Next.js   │  │JWT Auth  │  │Rate Limit│  │Vector DB │  │ │
│  │  │Frontend  │  │Middleware│  │@upstash  │  │Interface │  │ │
│  │  └──────────┘  └──────────┘  └──────────┘  └──────────┘  │ │
│  └───────────────────────────┬──────────────────────────────┘ │
│                              │ :3000                            │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │                   iwl-kb-system (KB)                       │ │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  │ │
│  │  │FastAPI   │  │Redis/    │  │FAISS/    │  │ChromaDB  │  │ │
│  │  │CRUD API  │  │PostgreSQL│  │Annoy     │  │Vector    │  │ │
│  │  └──────────┘  └──────────┘  └──────────┘  └──────────┘  │ │
│  └───────────────────────────┬──────────────────────────────┘ │
│                              │ :8002                            │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │                  ai-engine-hub (LLM)                       │ │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  │ │
│  │  │Bearer    │  │Redis     │  │OpenAI/   │  │Batch     │  │ │
│  │  │Auth      │  │Cache     │  │Claude/   │  │Processing│  │ │
│  │  └──────────┘  └──────────┘  │Gemini    │  └──────────┘  │ │
│  └───────────────────────────┬──────────────────────────────┘ │
└──────────────────────────────┼──────────────────────────────────┘
                               │ :8888
┌──────────────────────────────┴──────────────────────────────────┐
│                    AI Orchestra v3.0 (Core)                      │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                   Node-DAG-Executor System                │  │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────────┐  │  │
│  │  │   NODES     │  │    DAGS     │  │   EXECUTORS     │  │  │
│  │  │             │  │             │  │                 │  │  │
│  │  │ • pm_monitor│  │ • pm_orch   │  │ • iwl_executor  │  │  │
│  │  │ • enforce_  │  │ • iwl_dev   │  │ • 30 Personas   │  │  │
│  │  │   reporting │  │   _dag      │  │ • Growth System │  │  │
│  │  │ • check_    │  │             │  │                 │  │  │
│  │  │   before    │  │             │  │                 │  │  │
│  │  │ • iwl_dev   │  │             │  │                 │  │  │
│  │  └─────────────┘  └─────────────┘  └─────────────────┘  │  │
│  └──────────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                  30-Person Organization                   │  │
│  │  ┌─────────────────────────────────────────────────────┐ │  │
│  │  │     EXECUTIVES (3)      │      TEAM LEADS (7)      │ │  │
│  │  ├─────────────────────────┼───────────────────────────┤ │  │
│  │  │ • CEO (Strategy)        │ • Frontend Lead          │ │  │
│  │  │ • CTO (Architecture)    │ • Backend Lead           │ │  │
│  │  │ • COO (Operations)      │ • AI/ML Lead             │ │  │
│  │  │                         │ • Design Lead            │ │  │
│  │  │                         │ • QA Lead                │ │  │
│  │  │                         │ • DevOps Lead            │ │  │
│  │  │                         │ • Content Lead           │ │  │
│  │  └─────────────────────────┴───────────────────────────┘ │  │
│  │  ┌─────────────────────────────────────────────────────┐ │  │
│  │  │ DEVELOPERS (8) │ DESIGNERS (4) │ QA (3) │ OPS (5)  │ │  │
│  │  └─────────────────────────────────────────────────────┘ │  │
│  └──────────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              Recursive Growth System                      │  │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐│  │
│  │  │Experience│→ │Skill     │→ │Knowledge │→ │Innovation││  │
│  │  │Points    │  │Leveling  │  │Transfer  │  │Detection ││  │
│  │  └──────────┘  └──────────┘  └──────────┘  └──────────┘│  │
│  └──────────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                  GitHub Integration                       │  │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐│  │
│  │  │Issue     │→ │Work      │→ │PR        │→ │Auto      ││  │
│  │  │Parser    │  │Breakdown │  │Creation  │  │Merge     ││  │
│  │  └──────────┘  └──────────┘  └──────────┘  └──────────┘│  │
│  └──────────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              iTerm2 Session Management                    │  │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐│  │
│  │  │PM Claude │  │Main      │  │KB Claude │  │LLM Claude││  │
│  │  │(Orches.) │  │Claude    │  │(KB Sys)  │  │(AI Hub)  ││  │
│  │  └──────────┘  └──────────┘  └──────────┘  └──────────┘│  │
│  └──────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────┘

## 통신 흐름 예시

### 성공 케이스
```javascript
// 1. FlowCTRL → OrchestrEX
POST /api/execute
{
  "task_id": "TASK_001",
  "exec": "IMPLEMENT task_id=TASK_001 feature=login language=python",
  "target": "claude",
  "timeout": 60
}

// 2. OrchestrEX 내부 처리
validator.validate(exec) // 보안 검증
adapter = get_adapter("claude")
result = adapter.execute_with_handshake(exec, "TASK_001")

// 3. 3-Step Handshake
OrchestrEX → Claude: EXEC_TASK_001 IMPLEMENT feature=login language=python
Claude → OrchestrEX: @@ACK:TASK_001
Claude → OrchestrEX: @@RUN:TASK_001
Claude → OrchestrEX: @@EOT:TASK_001:SUCCESS

// 4. OrchestrEX → FlowCTRL
{
  "task_id": "TASK_001",
  "status": "SUCCESS",
  "duration": 45.2,
  "output": "Login feature implemented",
  "metrics": {
    "ack_time": 0.5,
    "run_time": 1.2,
    "exec_time": 43.5
  }
}
```

### 실패 케이스 (Circuit Breaker)
```javascript
// 1. 연속 실패 감지
failures["claude"] = 5  // 5회 연속 실패

// 2. Circuit Open
circuit_state["claude"] = "OPEN"

// 3. 빠른 실패 응답
{
  "task_id": "TASK_002",
  "status": "ERROR",
  "error": {
    "code": "CIRCUIT_OPEN",
    "message": "Claude adapter circuit is open",
    "retry_after": 30
  }
}

// 4. DLQ로 이동
dead_letter_queue.push({
  "task_id": "TASK_002",
  "exec": "TEST module=auth",
  "retry_count": 0,
  "queued_at": "2025-08-22T10:00:00Z"
})
```

## 배포 구성

### 개발 환경
```bash
# OrchestrEX (로컬)
python main.py --pane %3 --task dev_001 --cmd "TEST module=auth"

# FlowCTRL (로컬)
npm run dev  # http://localhost:3000
```

### 프로덕션 환경
```yaml
# docker-compose.yml
services:
  orchestrex:
    image: ihw33/orchestrex:latest
    volumes:
      - ./config:/app/config
      - ./logs:/app/logs
    environment:
      - ADAPTERS=tmux,claude,chatgpt
      - RATE_LIMIT=100/minute
      - CIRCUIT_THRESHOLD=5
      - LOG_LEVEL=INFO
    security_opt:
      - no-new-privileges:true
    read_only: true
    tmpfs:
      - /tmp
  
  flowctrl:
    image: ihw33/flowctrl:latest
    ports:
      - "80:3000"
    environment:
      - ORCHESTREX_URL=http://orchestrex:8080
      - AUTH_PROVIDER=supabase
    depends_on:
      - orchestrex
```

## 📅 최신 작업 현황 (2025-08-28)

### ✅ 완료된 주요 이슈

#### Issue #34: 3개 서비스 통합 구축
- **Main Platform** (iwl-v5-rebuild#35): JWT 인증, Rate Limiting
- **KB System** (iwl-kb-system#1): 데이터베이스 영속성, FAISS/Annoy
- **LLM Service** (ai-engine-hub#3): Bearer 토큰, Redis 캐싱

#### Issue #81: IWL Orchestra 시스템
- **30명 페르소나 조직**: 경영진, 팀리더, 개발자, 디자이너, QA, 운영
- **재귀 성장 시스템**: 자동 스킬 향상, 지식 전수, 혁신 탐지
- **GitHub 통합**: 이슈 파싱, 작업 분해, PR 생성

### 🚀 현재 실행 가능 명령

```bash
# IWL Orchestra 시스템
python /Users/m4_macbook/Projects/ai-orchestra-v02/executors/iwl_executor.py --status
python /Users/m4_macbook/Projects/ai-orchestra-v02/executors/iwl_executor.py --issue-id 35

# 페르소나 성장 테스트
python /Users/m4_macbook/Projects/ai-orchestra-v02/personas/iwl_recursive_growth_system.py --test-persona alex_kim

# 4개 Claude 세션 오케스트레이션
osascript /Users/m4_macbook/Projects/ai-orchestra-v02/orchestrate_4_claudes.applescript

# PM 모니터링 시작/중지
python /Users/m4_macbook/Projects/ai-orchestra-v02/pm_orchestration_controller.py start 34 ihw33/ai-orchestra-v02
python /Users/m4_macbook/Projects/ai-orchestra-v02/pm_orchestration_controller.py stop

# 서비스 상태 확인
curl http://localhost:3000   # Main Platform (Next.js)
curl http://localhost:8002/health  # KB System (FastAPI)
curl http://localhost:8888/health  # LLM Service (FastAPI)
```

### 📊 시스템 메트릭

| 구성 요소 | 수량 | 상태 |
|----------|------|------|
| Nodes | 5개 | ✅ 모두 작동 |
| DAGs | 2개 | ✅ 활성화 |
| Personas | 30명 (8명 구현) | ⏳ 확장 중 |
| Services | 4개 | ✅ 모두 실행 중 |
| Issues | 81개 | 📈 계속 증가 |

## 🔮 향후 계획

### Phase 4 - IWL 교육 매트릭스
- 8x4 교육 콘텐츠 노드 구현
- 학습 경로 자동 생성
- 개인화된 커리큘럼

### Phase 5 - 완전 자율 운영
- 인간 개입 없는 24/7 개발
- 자가 치유 시스템
- 예측적 스케일링

## 네이밍 사용 예시

```python
# 코드 내부
from orchestrex.core import protocol
from orchestrex.adapters import ClaudeAdapter
from orchestrex.security import ExecValidator

# 로그
logger.info("[OrchestrEX] Task TASK_001 validated and queued")
logger.info("[OrchestrEX] Circuit breaker opened for claude adapter")
logger.info("[FlowCTRL] Dashboard updated with task status")

# 문서/대화
"이건 OrchestrEX에서 처리할 거고, FlowCTRL에서 모니터링 붙인다"
"OrchestrEX의 Validator가 EXEC 명령 검증한다"
"FlowCTRL의 워크플로우 디자이너에서 YAML 생성한다"
"AI Orchestra v3.0 출시 예정" (외부 발표)