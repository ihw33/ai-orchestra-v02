# PR-02: tmux 전송/캡처 하드닝

## 테스트 완료 항목

### 1. 특수문자/멀티라인 전송 ✅
- `_needs_safe_send()`: 특수문자 감지 (따옴표, 백틱, 달러, 세미콜론 등)
- `_safe_send()`: base64 인코딩으로 안전 전송
- 멀티라인 명령어 지원

### 2. 긴 출력 캡처 성능 ✅
- `capture_tail()`: 마지막 N줄만 캡처하여 성능 최적화
- 기본 200줄, 필요시 조정 가능
- 대량 출력에서도 빠른 토큰 감지

### 3. 오류 스냅샷 ✅
- 타임아웃 시 마지막 출력 스냅샷 포함
- 디버깅 정보 제공: `NO_{token}|snapshot={last_output}`

## 구현 내용

### TmuxController 개선사항
```python
# 특수문자 감지
def _needs_safe_send(self, text: str) -> bool:
    special_chars = ['"', "'", '`', '\\', '$', '\n', '\t', ';', '&', '|', '>', '<']
    return any(char in text for char in special_chars)

# base64 안전 전송
def _safe_send(self, text: str) -> None:
    b64 = base64.b64encode(text.encode()).decode()
    cmd = f"printf '%s' '{b64}' | base64 -d | bash"
    # ...

# 성능 최적화 캡처
def capture_tail(self, lines: int = 200) -> str:
    return self.capture_output(last_lines=lines)
```

## 테스트 결과
- tests/test_advanced_scenarios.py: 특수문자 처리 테스트 통과
- 캡처 최적화 검증 완료
- 21/21 테스트 통과