# PR-03: 파서/시나리오 강화

## 테스트 완료 항목

### 1. 순서 역전 처리 ✅
- RUN이 ACK보다 먼저 오는 경우 → 타임아웃 처리
- 잘못된 순서는 실패로 판정
- test_run_before_ack 테스트 통과

### 2. 중복 토큰 무시 ✅
- 같은 토큰이 여러 번 나와도 첫 번째 유효 토큰만 처리
- seen_tokens set으로 중복 방지
- test_duplicate_tokens 테스트 통과

### 3. 노이즈 포함 출력 ✅
- 로그, 디버그 메시지가 섞여도 토큰 정확히 파싱
- ANSI 컬러 코드 자동 제거
- test_tokens_with_noise, test_colored_output 테스트 통과

## 구현 내용

### ANSI 컬러 코드 제거
```python
# protocol.py
ANSI_ESCAPE = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')

def strip_ansi_codes(text: str) -> str:
    return ANSI_ESCAPE.sub('', text)

def parse_ack(line: str) -> Optional[Ack]:
    clean_line = strip_ansi_codes(line)
    # ...
```

### 중복 토큰 처리
```python
# tmux_controller.py
seen_tokens = set()  # 중복 토큰 방지
for line in lines:
    line_hash = hash(line)
    if line_hash in seen_tokens:
        continue
    # ...
```

## 테스트 결과
- 순서 역전 시나리오 테스트 통과
- 노이즈/컬러 코드 처리 테스트 통과
- 21/21 전체 테스트 통과