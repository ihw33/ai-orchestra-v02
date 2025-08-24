# 📨 각 AI에게 보낼 실제 지시 메시지

## 1️⃣ ChatGPT (Emma) - 게임 디자인
```
cursor exec "
[Project Tycoon 게임 디자인 요청]

안녕 Emma! Project Tycoon 게임 디자인이 필요해.

목표: GitHub 프로젝트 관리를 Football Manager + 타이쿤 게임으로
플랫폼: 터미널 텍스트 기반

필요한 디자인:
1. 게임 루프 (일일 사이클)
2. 팀 스탯 시스템 (각 AI의 능력치)
3. 스프린트 매치 (2주 = 1경기)
4. 랜덤 이벤트 20개
5. 승리 조건

산출물: GAME_DESIGN_DOC.md 파일 생성
위치: /Users/m4_macbook/Projects/ai-orchestra-v02/

완료 후 다음 형식으로 보고:
'✅ Emma: 게임 디자인 완료! [요약 내용]'
"
```

## 2️⃣ Codex CLI (Rajiv) - 게임 엔진
```
codex exec "
[Project Tycoon 게임 엔진 구현]

Rajiv, 게임 엔진 필요.

Requirements:
- Python 3.10+
- No external dependencies (except GitHub API)

Classes needed:
1. GameState - 게임 상태 관리
2. Team - AI 팀원 관리 (name, stats, morale)
3. Sprint - 스프린트 시뮬레이션
4. EventManager - 랜덤 이벤트
5. ScoreCalculator - 점수 계산

Key methods:
- start_game()
- run_sprint()
- handle_event()
- calculate_score()

Output: game_engine.py
Location: /Users/m4_macbook/Projects/ai-orchestra-v02/

Report format when done:
'✅ Rajiv: Engine ready. 200 lines. PR #XXX'
"
```

## 3️⃣ Claude Code (Yui) - 터미널 UI
```
/SC Frontend
/SC Implement

Yui님, Project Tycoon 터미널 UI 부탁드립니다.

요구사항:
- Python curses 라이브러리 사용
- 텍스트 기반 (ASCII 아트 환영)

화면 구성:
1. 상단: 게임 상태 (Day, Budget, Score)
2. 중앙: 팀 리스트 (이름, 스탯바, 상태)
3. 하단: 이벤트 로그
4. 메뉴: 선택지 (1-5 숫자)

예시 레이아웃:
╔══════════════════════════════╗
║ Day 15 | 💰 $8,420 | ⭐ 750  ║
╠══════════════════════════════╣
║ Emma    [████████] 85% 😊    ║
║ Rajiv   [██████  ] 72% 😤    ║
║ Anna    [█████████] 95% 🎯   ║
╚══════════════════════════════╝

파일: terminal_ui.py
위치: /Users/m4_macbook/Projects/ai-orchestra-v02/

완료 보고: '✅ Yui: UI 완성! 픽셀 단위로 조정했습니다 🎨'
```

## 4️⃣ Claude Code Agent (Anna) - 테스트
```
/SC Test
/SC Debug

Anna, 게임 테스트 부탁해요!

테스트 항목:
1. 게임 밸런스 (너무 쉽거나 어렵지 않은지)
2. 버그 체크 (크래시, 무한루프 등)
3. 엣지 케이스 (budget=0, team=0 등)
4. 재미 요소 (실제로 재밌는지)

테스트 케이스:
- 정상 플레이 10회
- 극단적 선택 5회
- 랜덤 입력 5회

산출물: test_report.md, test_gameplay.py
위치: /Users/m4_macbook/Projects/ai-orchestra-v02/

보고: '✅ Anna: 테스트 완료. 버그 3개 발견. 밸런스 조정 필요'
```

## 5️⃣ Gemini CLI (Olaf) - 배포 환경
```
gemini exec "
[Project Tycoon 배포 준비]

Olaf, 배포 패키지 준비.

필요 파일:
1. requirements.txt (의존성)
2. Dockerfile (컨테이너)
3. run_game.sh (실행 스크립트)
4. README.md (설치/실행 가이드)

실행 방법:
- 원클릭: ./run_game.sh
- Docker: docker run project-tycoon
- Python: python main.py

테스트:
- Ubuntu 20.04
- macOS 12+
- Windows WSL2

Location: /Users/m4_macbook/Projects/ai-orchestra-v02/

완료 보고: '✅ Olaf: Deployment ready. 14:00 sharp.'
"
```

---

## 📊 보고 체계

### 각 AI는 완료 시 Issue #50에 코멘트
```bash
gh issue comment 50 -R ihw33/ai-orchestra-v02 -b "✅ [이름]: 작업 완료
- 산출물: [파일명]
- 소요시간: [XX분]
- 특이사항: [있으면]
- 다음 단계: [제안]"
```

### PM (나)는 30분마다 상태 체크
```bash
# 진행 상황 확인
gh issue view 50 -R ihw33/ai-orchestra-v02 --comments

# 종합 보고
"📊 Project Tycoon 진행률: X/5 완료"
```

---

## ⏰ 예상 일정
- T+0: 지시 전달
- T+30: Emma 완료 (디자인)
- T+45: Rajiv, Yui 완료 (엔진, UI)
- T+60: Anna 완료 (테스트)
- T+70: Olaf 완료 (배포)
- T+90: 통합 및 최종 테스트