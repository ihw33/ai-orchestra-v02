# AI Orchestra v02

안정적인 챗봇 간 통신 시스템

## 🎯 목표

여러 AI 도구들(Claude, ChatGPT, Gemini, Codex 등) 간 **안정적인 통신**을 구현하여 복잡한 작업을 자동화합니다.

## 🏗️ 프로젝트 구조

```
ai-orchestra-v02/
├── core/                   # 핵심 통신 모듈
│   ├── protocol.py         # 3단계 핸드셰이크 (@@ACK/@@RUN/@@EOT)
│   ├── idempotency.py      # 중복 실행 방지
│   └── retry.py            # 재시도 메커니즘
├── controllers/            # 제어 모듈
│   └── tmux_controller.py  # tmux 세션 제어 (pane_id 고정)
├── tests/                  # 테스트
│   └── test_ping_pong.py   # 기본 통신 테스트
├── main.py                 # 최소 실행 엔진(스모크)
└── requirements.txt        # dev 의존성(pytest 포함)
```

## 📋 Phase 1 - MVP (진행 중)

- [ ] [#2](https://github.com/ihw33/ai-orchestra-v02/issues/2) 프로젝트 기본 구조
- [ ] [#3](https://github.com/ihw33/ai-orchestra-v02/issues/3) 3단계 핸드셰이크 프로토콜
- [ ] [#4](https://github.com/ihw33/ai-orchestra-v02/issues/4) 멱등성 시스템
- [ ] [#5](https://github.com/ihw33/ai-orchestra-v02/issues/5) 재시도 메커니즘
- [ ] [#6](https://github.com/ihw33/ai-orchestra-v02/issues/6) tmux 컨트롤러
- [ ] [#7](https://github.com/ihw33/ai-orchestra-v02/issues/7) Ping-Pong 테스트

> 전체 진행 상황은 [Epic #1](https://github.com/ihw33/ai-orchestra-v02/issues/1)에서 확인하세요.

## 🚀 Quick Start

> **주의:** tmux는 반드시 **pane_id 고정**(`%3` 등)으로 제어합니다. "현재 pane" 의존 금지.

```bash
# 1) 의존성 설치 (pytest 포함)
pip install -r requirements.txt

# 2) 스모크 실행 (ACK→RUN→EOT)
python main.py --pane %3 --task t1 --cmd "printf '@@ACK id=t1\n@@RUN id=t1\n@@EOT id=t1 status=OK\n'"

# 3) 테스트 실행 (권장)
pytest -q
```

## 💡 핵심 원칙

- **Simple is better than complex**
- **통신 안정성 먼저, 업무 프로세스는 나중**
- **실제 문제 발생 시 해결**

## ✅ PR 체크(요약)

- [ ] `@@ACK`/`@@RUN`/`@@EOT` 토큰 정확
- [ ] 멱등키/재시도 공용 유틸 사용
- [ ] tmux pane_id 고정 사용
- [ ] 테스트(단위/스모크) 통과

## 📝 License

MIT