# 🎯 AI Orchestra v02 - 정상 실행 가이드

## 📌 Port-Adapter 패턴 기반 실행

### 1. 이슈 자동 처리
```bash
# 최신 이슈 5개를 확인하고 AI가 필요한 이슈 자동 처리
python3 -m src.main process-issues

# 특정 이슈 번호를 지정하여 처리 (예: Issue #109)
python3 -m src.main process-issue 109
```

### 2. 특정 워크플로우 실행
```bash
# AI 처리 워크플로우 (병렬 실행)
python3 -m src.main execute-workflow ai_processing

# 이슈 처리 워크플로우 (DAG 실행)
python3 -m src.main execute-workflow issue_processing

# 코드 리뷰 워크플로우
python3 -m src.main execute-workflow code_review
```

### 3. PR 코드 리뷰
```bash
# 특정 PR 리뷰 실행
python3 -m src.main review-pr 45
```

### 4. 이벤트 핸들링
```bash
# GitHub webhook 이벤트 처리
python3 -m src.main handle-event '{"source": "github", "type": "issue", "action": "opened"}'
```

## 🏗️ 시스템 구조

```
src/
├── main.py                 # 메인 엔트리 포인트
├── ports/                  # 인터페이스 정의
│   ├── pm_processor_port.py
│   ├── trigger_port.py
│   └── orchestration_port.py
└── adapters/               # 구현체
    ├── pm/                 # PM 프로세서
    ├── trigger/            # 트리거 시스템
    ├── orchestration/      # 오케스트레이터
    └── ai/                 # AI 통합
```

## 🔄 작동 흐름

1. **이슈 생성** → GitHub에 [AI] 태그로 이슈 생성
2. **트리거 감지** → TriggerSystemAdapter가 이슈 감지
3. **PM 처리** → PMProcessorAdapter가 AI 필요 여부 판단
4. **오케스트레이션** → OrchestratorAdapter가 워크플로우 실행
5. **AI 실행** → 각 AI 어댑터가 작업 수행
6. **결과 보고** → GitHub에 결과 코멘트

## ✅ 정상 작동 확인

```bash
# 시스템 상태 확인
python3 -m src.main

# 로그 확인
tail -f logs/global_*.log
```

## ❌ 사용하지 말아야 할 것들 (Deprecated)

- `pm_direct_workflow.sh` - 임시 셸 스크립트
- `multi_ai_orchestrator.py` - 존재하지 않음
- `pm_auto_processor.py` - 존재하지 않음
- GitHub Actions (현재 주석 처리됨)

## 📝 주의사항

- 모든 실행은 `src.main` 모듈을 통해 진행
- AI CLI 도구들이 설치되어 있어야 함 (gemini, claude, codex)
- GitHub CLI (`gh`)가 설치되어 있어야 함

---
*작성: 2025-09-02*
*버전: 1.0.0*