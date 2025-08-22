# PR-01: CLI 정합성 확인

## 테스트 완료 항목

### 1. 옵션 노출 확인 ✅
```bash
python main.py -h
```
- `--timeout-ack`: ACK 대기 타임아웃 (기본 5초)
- `--timeout-run`: RUN 대기 타임아웃 (기본 10초)
- `--timeout-eot`: EOT 대기 타임아웃 (기본 30초)
- `--skip-idempotency`: 멱등성 체크 스킵

### 2. 타임아웃 동작 확인 ✅
```bash
# EOT 없이 타임아웃 테스트
python main_mock.py --pane %3 --task t_to --timeout-eot 1 --cmd "printf '@@ACK id=t_to\n@@RUN id=t_to\n'"
```
결과: `NO_EOT` 메시지와 함께 실패

### 3. 멱등성 기능 확인 ✅
- 프로세스 내에서 같은 task_id 재실행 시 캐시 반환
- `--skip-idempotency` 옵션으로 멱등성 체크 무시 가능

### 4. 테스트 스위트 ✅
- pytest: 21/21 테스트 통과
- auto_grade.py: 시나리오 기반 자동 테스트 도구 추가

## 구현 내용
- main.py: 모든 CLI 옵션 구현 및 연결
- main_mock.py: tmux 없이 테스트 가능한 목 버전
- tools/auto_grade.py: 자동 채점 도구
- tests/scenarios/ping_pong.yml: 테스트 시나리오