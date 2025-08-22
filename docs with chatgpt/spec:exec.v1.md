spec/exec.v1.md
0. 목적 (Why)

자연어 계획을 **안정적·예측가능한 “명령(EXEC)”**으로 컴파일해 챗봇이 생각/추측 없이 정해진 작업만 수행하도록 만든다.

시스템이 검증/멱등성/재시도를 책임지고,

챗봇은 EXEC 한 줄을 받아 @@ACK → @@RUN → @@EOT로만 응답한다.

1. 범위 (Scope)

이 문서는 EXEC v1 명령 형식과 검증 규칙, 핸드셰이크, 오류 코드, 보안 가드를 정의한다.

전송/실행은 orchestra가 담당; 챗봇은 파싱/실행/토큰 응답만 담당한다.

2. 버저닝 (Versioning)

현재: protocol=v1

하위 호환 원칙: v1 필드 유지, 신규 필드는 옵셔널로 추가.

파기 변경은 v2로 분리.

3. 핸드셰이크 (Handshake Tokens)

모든 실행은 정확히 아래 토큰 시퀀스를 따른다.

@@ACK id=<task_id>
@@RUN id=<task_id> ts=<unix_ms>
@@EOT id=<task_id> status=OK|FAIL [code=<ERR_*>] [meta=k1:v1,k2:v2]


ACK: 명령 수신 확인(재전송 금지 신호)

RUN: 실행 시작(타이밍/상태 추적용)

EOT: 종료. status=OK|FAIL 필수. 실패 시 code 권장.

노이즈/컬러/프롬프트 문자열은 무시 가능해야 함(파서 내성).

4. EXEC 문법 (Syntax, EBNF)
command     = verb, 1*(SP, arg);
verb        = "DESIGN" | "IMPLEMENT" | "REVIEW" | "TEST" | "DOCS";
arg         = key, "=", value;
key         = 1*(ALNUM | "_" | "-");
value       = 1*(~SPACE) | quoted;
quoted      = '"', *CHAR, '"';


모든 값은 공백 없는 토큰 또는 "따옴표"로 감싼 문자열.

필수 공통 인자: task_id, protocol, timeout_s, idempotency_key.

5. 공통 필드 (Required Common Args)
필드	타입	예	설명
task_id	string	t42	실행 단위 ID(로그/토큰 식별자)
protocol	enum	v1	EXEC 프로토콜 버전
timeout_s	int	30	총 실행 제한(sec)
idempotency_key	string	abc123	중복 실행 방지 키
6. Verb별 필수 인자 (Per-Verb Required Args)

DESIGN: requirements_ref | issue_id, out

IMPLEMENT: spec_ref, lang, out

REVIEW: pr | target, scope

TEST: target | pr, suite

DOCS: target, format

리소스 경로는 허용 스킴만: repo://, s3://, gh:// 등(화이트리스트).

7. 예시 (Examples)
7.1 IMPLEMENT
IMPLEMENT spec_ref=repo://specs/login_v1.md lang=python out=repo://svc/auth task_id=t100 protocol=v1 timeout_s=30 idempotency_key=ab12

7.2 REVIEW
REVIEW pr=123 scope=security task_id=t99 protocol=v1 timeout_s=20 idempotency_key=r9k

7.3 TEST
TEST target=repo://svc/auth suite=smoke task_id=t101 protocol=v1 timeout_s=60 idempotency_key=ab13

8. 검증(Validator) 규칙

화이트리스트 Verb: {DESIGN, IMPLEMENT, REVIEW, TEST, DOCS} 외 거부

필수 인자 존재(상단 표 참조)

스킴 제한: 리소스 값은 repo://, s3://, gh:// 등 허용 목록만

길이 제한: 전체 2KB 이내, arg 수 ≤ 20

기본값 주입: 누락 시 timeout_s=30, protocol=v1

모호/누락: NEEDS_INFO 태스크로 전환(실행 금지), 깃허브 코멘트 체크리스트 반환

9. 오류 코드 (Failure Codes)
code	의미	권장 복구
ERR_TIMEOUT	timeout 초과	백오프 후 재시도
ERR_RATE_LIMIT	레이트리밋	Retry-After 준수
ERR_AUTH	인증/권한 문제	자격 확인
ERR_INPUT	인자 검증 실패	NEEDS_INFO 재요청
ERR_RUNTIME	실행 중 예외	스냅샷 첨부 후 재시도
ERR_DEP	의존성/외부 리소스 실패	격리 후 재시도

@@EOT ... status=FAIL code=ERR_* meta=... 형태 권장. meta에는 detail/hint/retry_after_ms 등 포함 가능.

10. 보안/안전 가드 (Safety)

자연어 금지: 챗봇 입력은 EXEC 한 줄만 허용.

명령 확장 금지: 파이프/서브쉘/리다이렉션 등 임의 실행 불가(어댑터가 안전 전송(base64 파이프) 사용).

출력 마스킹: 토큰/비밀키 마스킹.

읽기 전용 기본값: 파일 쓰기/원격 fetch는 시스템 정책으로 제어.

11. 전송/실행 (Transport)

Orchestra가 EXEC를 큐에 넣고, tmux_controller.exec_handshake()로 실행.

챗봇은 수신 즉시 @@ACK, 실행 시작 시 @@RUN, 종료 시 @@EOT를 반드시 출력.

멱등성: idempotency_key 중복 요청 시 재실행 금지(캐시 응답 허용).

12. GitHub 연동 (Issue/PR → EXEC)

이슈/PR 템플릿 하단에 머신 섹션을 둔다:

## 🔧 Machine Section (exec.v1)
```exec.v1
- verb: IMPLEMENT
  args: { spec_ref: repo://specs/login_v1.md, lang: python, out: repo://svc/auth }
- verb: TEST
  args: { target: repo://svc/auth, suite: smoke }
```


액션이 exec.v1 블록을 YAML→EXEC으로 컴파일 → 큐 투입.

블록이 없거나 검증 실패 시 NEEDS_INFO 체크리스트 코멘트 생성.

13. 어댑터 규약 (Adapter Contract)

어댑터는 EXEC를 안전한 실행 명령으로 변환하고, 마지막에 토큰을 강제 출력해야 한다.

build_command(task) -> str (안전 이스케이프/멀티라인 허용)

명령 마지막에 항상:

&& printf "@@ACK id=<id>\n@@RUN id=<id> ts=$(date +%s%3N)\n@@EOT id=<id> status=OK\n"


혹은 실행 과정에서 순차 출력.

실패 시 status=FAIL code=ERR_ meta=...* 출력.

14. 타임아웃/재시도/멱등 (Runtime Policy)

timeout_s: 오케스트라가 총 한도 관리

재시도: 지수 백오프 + 지터(기본 3회)

멱등: 동일 idempotency_key 요청은 캐시 응답 반환

15. 상태 머신 (State)
IDLE -> ACKED -> RUNNING -> (EOT_OK | EOT_FAIL)
            ^                 |
            +-----(retry)-----+


역전 토큰/중복 토큰은 무시(첫 유효 시점 고정), 순서 위반 시 실패.

16. 테스트 (Conformance)

필수 테스트(모두 통과해야 “v1 적합”):

정상: ACK→RUN→EOT(OK)

NO_ACK/NO_RUN/NO_EOT 타임아웃

중복 토큰(ACK/ RUN 2회) 허용

노이즈 포함 로그에서 파싱 성공

FAIL with code (ERR_INPUT 등)

멱등: 같은 idempotency_key 재요청 캐시 응답

17. 확장(Extensions)

신규 verb는 registry에만 추가(파서/검증 업데이트).

필드 확장은 옵셔널 키로 추가.

비호환 변경은 protocol=v2.

18. 간단 JSON 스키마 (파서 후 검증용)
{
  "type": "object",
  "required": ["verb", "args", "task_id", "protocol", "timeout_s", "idempotency_key"],
  "properties": {
    "verb": {"enum": ["DESIGN", "IMPLEMENT", "REVIEW", "TEST", "DOCS"]},
    "args": {"type": "object"},
    "task_id": {"type": "string"},
    "protocol": {"const": "v1"},
    "timeout_s": {"type": "integer", "minimum": 1, "maximum": 3600},
    "idempotency_key": {"type": "string", "minLength": 1, "maxLength": 128}
  },
  "additionalProperties": true
}

19. 운용 가이드 (운영 체크리스트)

 EXEC는 한 줄, 자연어 금지

 핸드셰이크 3토큰 보장

 FAIL 시 code 포함

 멱등/재시도 정책 준수

 GitHub Machine Section에서만 컴파일 허용

 어댑터는 명령 끝에 EOT 강제 출력