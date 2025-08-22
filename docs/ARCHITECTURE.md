# OrchestrEX / FlowCTRL Architecture

## 핵심 철학: 결정론적 실행

> **"챗봇 기억은 보조 도구일 뿐, EXEC 기반 결정론적 실행만이 진정한 자동화"**

### 왜 EXEC인가?
- **챗봇 기억의 한계**: LLM은 맥락 보존은 잘하지만 결정론적 실행을 보장 못함
- **재현성**: 어떤 챗봇이든, 어떤 시점이든 같은 EXEC를 받으면 같은 행동 재현
- **신뢰성**: 기억 없이도 fresh하게 실행 가능 → 실패 시 재실행이 단순

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

## 아키텍처 다이어그램

```
┌─────────────────────────────────────────────────────────┐
│                      FlowCTRL (UI)                       │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐│
│  │Dashboard │  │Workflow  │  │Monitor   │  │Analytics ││
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘│
└────────────────────────┬────────────────────────────────┘
                         │ REST/WebSocket
┌────────────────────────┴────────────────────────────────┐
│                    OrchestrEX (Core)                     │
│  ┌──────────────────────────────────────────────────┐  │
│  │             Security & Validation Layer           │  │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐      │  │
│  │  │Sanitizer │→ │Validator │→ │Authorizer│      │  │
│  │  └──────────┘  └──────────┘  └──────────┘      │  │
│  └──────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────┐  │
│  │                 EXEC Processor                    │  │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐      │  │
│  │  │Parser    │→ │Scheduler │→ │Executor  │      │  │
│  │  └──────────┘  └──────────┘  └──────────┘      │  │
│  └──────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────┐  │
│  │              3-Step Handshake Engine              │  │
│  │  @@ACK → @@RUN → @@EOT (with error handling)    │  │
│  └──────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────┐  │
│  │           Resilience Components                   │  │
│  │  ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐   │  │
│  │  │Circuit │ │Retry   │ │DLQ     │ │Cache   │   │  │
│  │  │Breaker │ │Logic   │ │System  │ │Layer   │   │  │
│  │  └────────┘ └────────┘ └────────┘ └────────┘   │  │
│  └──────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────┐  │
│  │                  Adapters                         │  │
│  │  ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐   │  │
│  │  │Tmux    │ │Claude  │ │ChatGPT │ │Gemini  │   │  │
│  │  └────────┘ └────────┘ └────────┘ └────────┘   │  │
│  └──────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────┘
                         │
┌────────────────────────┴────────────────────────────────┐
│                    External AIs                          │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐│
│  │Claude    │  │ChatGPT   │  │Gemini    │  │Codex     ││
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘│
└──────────────────────────────────────────────────────────┘
```

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

## 확장 계획

### Phase 2 - FlowCTRL 구현
- WebSocket 실시간 통신
- 워크플로우 디자이너 (drag & drop)
- 메트릭 수집 및 시각화
- Circuit Breaker UI
- DLQ 관리 인터페이스

### Phase 3 - 고급 기능
- 병렬 실행 지원 (DAG 기반)
- 조건부 워크플로우
- 자동 롤백 메커니즘
- A/B 테스트 지원
- ML 기반 오류 예측

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