# 🎮 Project Tycoon 개발 - 업무 분산 계획

## 🎯 결정 사항
- ✅ **게임 스타일**: Football Manager + 타이쿤 혼합
- ✅ **플랫폼**: 터미널 텍스트 기반
- ✅ **MVP**: 텍스트로 시작

## 👥 업무 분담 (병렬 진행)

### 🎨 Emma (CPO) - ChatGPT/Cursor
**작업**: 게임 디자인 문서 & UX 플로우
```bash
# bash 없이 진행
cursor exec "Project Tycoon 게임 디자인:
- 게임 루프 설계
- 팀 스탯 시스템
- 랜덤 이벤트 목록
- 유저 스토리"
```
**산출물**: `GAME_DESIGN_DOC.md`
**예상**: 30분

### 💻 Rajiv (Engineering) - Codex CLI  
**작업**: 백엔드 로직 & 데이터 구조
```bash
# bash 없이 진행
codex exec "게임 엔진 구현:
- GameState 클래스
- Team 클래스
- Sprint 시뮬레이션
- GitHub API 연동"
```
**산출물**: `game_engine.py`
**예상**: 45분

### 🎮 Yui (Frontend) - Claude Code
**작업**: 터미널 UI (curses)
```bash
/SC Frontend
/SC Implement

터미널 게임 UI:
- curses 기반 레이아웃
- 팀 스탯 표시
- 메뉴 시스템
- ASCII 아트
```
**산출물**: `terminal_ui.py`
**예상**: 45분

### 🧪 Anna (QA) - Claude Code Agent
**작업**: 테스트 & 밸런싱
```bash
/SC Test

게임 플레이 테스트:
- 난이도 밸런싱
- 버그 찾기
- 게임 플로우 검증
```
**산출물**: `test_gameplay.py`
**예상**: 30분

### 🚀 Olaf (DevOps) - Gemini CLI
**작업**: 실행 환경 & 패키징
```bash
# bash 없이 진행
gemini exec "게임 배포 준비:
- requirements.txt
- Docker 컨테이너
- 실행 스크립트
- README"
```
**산출물**: `Dockerfile`, `run_game.sh`
**예상**: 20분

---

## 📅 병렬 진행 타임라인

```
시간  | Emma    | Rajiv   | Yui     | Anna    | Olaf
------|---------|---------|---------|---------|--------
00:00 | 디자인  | 엔진    | UI      | -       | -
00:30 | 완료    | 진행중  | 진행중  | 테스트  | 환경
01:00 | 리뷰    | 완료    | 완료    | 완료    | 완료
```

## 🔄 작업 연계

```
[Phase 1: 동시 시작]
Emma (디자인) ─┐
               ├→ [Phase 2: 통합]
Rajiv (엔진) ──┤     │
               │     ↓
Yui (UI) ──────┘   Marcus
                   (아키텍처 리뷰)
                      ↓
[Phase 3: 테스트]    
Anna (QA) → Olaf (배포)
```

## 📝 각 팀원 지시서

### Emma 지시
"Hey Emma! 🎮 Design a fun project management game!
Mix Football Manager team management with Tycoon resources.
Focus on: Team stats, Sprint matches, Random events
Make it FUN and ADDICTIVE!"

### Rajiv 지시  
"Rajiv, need game engine. Python. Clean code.
Classes: GameState, Team, Player, Sprint
GitHub API integration for real data.
Performance matters. Make it fast."

### Yui 지시
"Yui-san, 터미널 UI를 예쁘게 만들어주세요!
curses 라이브러리 사용
ASCII 아트로 팀 표시
깔끔하고 직관적인 레이아웃 🎨"

### Anna 지시
"Anna, test everything!
Check game balance - not too easy, not too hard
Find edge cases (what if budget = 0?)
Make sure it's actually fun to play"

### Olaf 지시
"Deployment package needed.
Docker container for consistency.
One-click run script.
Documentation. German precision required."

---

## 🎯 MVP 목표 (오늘)

### 핵심 기능만
1. **팀 구성**: 5명 AI 선택
2. **스프린트**: 자동 진행 & 결과
3. **스탯**: 간단한 숫자 표시
4. **이벤트**: 3-5개 랜덤 이벤트
5. **점수**: 최종 스코어

### 구현 안 할 것
- 복잡한 그래픽
- 멀티플레이어
- 세이브/로드 (일단은)
- 사운드

---

## 🚦 시작 신호

**PM Claude**: "팀 여러분, Project Tycoon 개발 시작합니다!

Emma는 디자인, Rajiv는 엔진, Yui는 UI 담당.
각자 작업 후 1시간 뒤 통합합니다.

Thomas님, 이렇게 진행하겠습니다.
제가 조율만 하고, 실제 작업은 팀원들이 병렬로 진행합니다!"

**Emma**: "OMG SO EXCITED! 🎮"
**Rajiv**: "Starting engine. ETA 45min."
**Yui**: "UI 스케치 시작합니다!"
**Anna**: "테스트 환경 준비 완료"
**Olaf**: "Docker ready in 20."