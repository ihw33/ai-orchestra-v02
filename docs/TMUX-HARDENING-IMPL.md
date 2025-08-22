# tmux 하드닝 구현 완료

## 구현된 기능
- _needs_safe_send(): 특수문자 감지
- _safe_send(): base64 인코딩 전송
- capture_tail(): 성능 최적화 (마지막 N줄)
- 타임아웃 시 디버깅 스냅샷

## 테스트 
- tests/test_advanced_scenarios.py: 9개 테스트 클래스
- 21/21 테스트 통과
