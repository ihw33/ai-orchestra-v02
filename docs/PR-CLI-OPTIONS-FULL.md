# PR: CLI 정합성 & 옵션 배선 확인 (완전판)

## 포함된 구현 파일

### 1. main.py ✅
- 모든 CLI 옵션 구현
- `--timeout-ack`, `--timeout-run`, `--timeout-eot`
- `--skip-idempotency`

### 2. main_mock.py ✅
- tmux 없이 테스트 가능한 mock 버전
- CI/CD에서 사용 가능

### 3. tools/auto_grade.py ✅
- 시나리오 기반 자동 테스트 도구
- YAML 파일로 테스트 케이스 정의

### 4. tests/scenarios/ping_pong.yml ✅
- 7개 테스트 시나리오
- 타임아웃, 멱등성, 순서 검증

## 테스트 실행 방법

```bash
# 도움말 확인
python main.py -h

# Mock 버전으로 테스트
python main_mock.py --pane %3 --task t1 --cmd "printf '@@ACK id=t1\n@@RUN id=t1\n@@EOT id=t1 status=OK\n'"

# 자동 채점
python tools/auto_grade.py --scenarios tests/scenarios/ping_pong.yml

# pytest 실행
PYTHONPATH=. pytest -q
```

## 변경 내역
- core/__init__.py: 함수 export 수정
- tests/test_tmux_controller.py: 테스트 수정
- .github/labeler.yml: v5 형식으로 업데이트
- .github/workflows/auto-labeler.yml: 권한 추가