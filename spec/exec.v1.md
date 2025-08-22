# EXEC v1.0 Specification

## Overview
EXEC는 AI Orchestra v02에서 챗봇 간 통신을 위한 결정론적 명령 언어입니다.
자연어 대신 구조화된 명령을 사용하여 명확하고 예측 가능한 통신을 보장합니다.

## Design Principles
1. **Deterministic**: 같은 명령은 항상 같은 결과를 생성
2. **Idempotent**: 중복 실행을 방지하는 멱등성 보장
3. **Observable**: 3-step handshake로 상태 추적 가능
4. **Parseable**: 간단한 key=value 구조로 파싱 용이

## Command Structure

### Basic Format
```
VERB [key=value ...] [-- payload]
```

- **VERB**: 동작을 나타내는 대문자 단어 (IMPLEMENT, TEST, ANALYZE 등)
- **key=value**: 파라미터 (띄어쓰기로 구분)
- **-- payload**: 멀티라인 페이로드 (선택사항)

### Examples
```
# 단순 명령
TEST module=auth

# 파라미터가 있는 명령
IMPLEMENT feature=login language=python framework=fastapi

# 페이로드가 있는 명령
ANALYZE type=security -- 
def login(username, password):
    # TODO: Add rate limiting
    return authenticate(username, password)
```

## 3-Step Handshake Protocol

모든 EXEC 명령은 3단계 핸드셰이크를 통해 실행됩니다:

### 1. ACK (Acknowledgment)
```
송신: EXEC_TASK_001 TEST module=auth
수신: @@ACK:TASK_001
```
- 수신자가 명령을 받았음을 확인
- 5초 타임아웃

### 2. RUN (Execution Start)
```
수신: @@RUN:TASK_001
```
- 실제 작업 시작을 알림
- 10초 타임아웃

### 3. EOT (End of Transmission)
```
수신: @@EOT:TASK_001:SUCCESS
또는
수신: @@EOT:TASK_001:FAILED:error_message
```
- 작업 완료 및 결과 전달
- 30초 타임아웃 (설정 가능)

## Core Verbs

### Phase 1 (MVP)
- **TEST**: 테스트 실행
- **ANALYZE**: 코드/데이터 분석
- **IMPLEMENT**: 기능 구현
- **REVIEW**: 코드 리뷰

### Phase 2 (확장)
- **DEPLOY**: 배포 작업
- **MONITOR**: 모니터링 설정
- **ROLLBACK**: 이전 상태로 복원
- **REPORT**: 보고서 생성

## Parameter Conventions

### 공통 파라미터
- `task_id`: 멱등성 키 (필수)
- `priority`: 우선순위 (high/normal/low)
- `timeout`: 커스텀 타임아웃 (초)
- `retry`: 재시도 횟수

### 타입별 파라미터
```
# TEST 명령
TEST module=auth type=unit coverage=80

# IMPLEMENT 명령  
IMPLEMENT feature=oauth provider=google scope=read

# ANALYZE 명령
ANALYZE type=performance metric=latency threshold=100ms
```

## Error Handling

### 에러 코드
- `TIMEOUT`: 타임아웃 발생
- `INVALID_SYNTAX`: 문법 오류
- `DUPLICATE_TASK`: 중복 실행 시도
- `EXECUTION_FAILED`: 실행 실패
- `UNKNOWN_VERB`: 알 수 없는 동사

### 재시도 정책
```python
# Exponential backoff with jitter
wait_time = min(base * (2^attempt) + random_jitter, max_wait)
```
- 기본: 3회 재시도
- 최대 대기: 30초

## Implementation Guidelines

### 파서 구현
```python
def parse_exec(exec_line: str) -> dict:
    params = {}
    parts = exec_line.split()
    
    # 첫 단어는 동사
    if parts:
        params['verb'] = parts[0]
    
    # 나머지는 key=value
    for part in parts[1:]:
        if '=' in part:
            key, value = part.split('=', 1)
            params[key] = value
    
    return params
```

### 멱등성 구현
```python
# 캐시 기반 중복 방지
def check_duplicate(task_id: str) -> bool:
    return task_id in _cache

def save_result(task_id: str, result: str):
    _cache[task_id] = {
        'result': result,
        'timestamp': time.time()
    }
```

## Adapter Integration

어댑터는 EXEC 명령을 각 통신 채널에 맞게 변환합니다:

### TmuxAdapter
- tmux pane으로 명령 전송
- 터미널 출력에서 토큰 파싱

### ClaudePlannerAdapter  
- AppleScript로 Claude에 전송
- EOT 강제 출력 구현

### ChatGPTAdapter (Future)
- Browser automation
- DOM injection/extraction

## Security Considerations

1. **Input Validation**: 모든 파라미터 검증
2. **Command Injection Prevention**: base64 인코딩 사용
3. **Rate Limiting**: 과도한 요청 차단
4. **Audit Logging**: 모든 EXEC 명령 기록

## Version History

### v1.0 (2025-08-22)
- 초기 사양 정의
- 3-step handshake 프로토콜
- 기본 VERB 4개 (TEST, ANALYZE, IMPLEMENT, REVIEW)
- tmux 어댑터 지원

### v1.1 (Planned)
- 페이로드 압축 지원
- 배치 명령 실행
- 병렬 실행 지원

## Examples

### 단위 테스트 실행
```bash
python main.py --pane %3 --task TEST_001 \
  --cmd "TEST module=auth type=unit"
```

### 기능 구현 요청
```bash
python main.py --pane %4 --task IMPL_002 \
  --cmd "IMPLEMENT feature=2fa method=totp" \
  --timeout-eot 60
```

### 코드 분석
```bash
python main.py --pane %5 --task ANALYZE_003 \
  --cmd "ANALYZE type=security scan=owasp"
```

## References
- [3-Step Handshake Protocol](../docs/3-STEP-HANDSHAKE.md)
- [Adapter Architecture](../adapters/README.md)
- [tmux Controller](../controllers/tmux_controller.py)