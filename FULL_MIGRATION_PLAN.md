# 🔄 AI Orchestra 전체 마이그레이션 계획
**작성일**: 2025-08-23  
**범위**: Round 1-5 수정 + 현재 v02 프로젝트 정리

---

## 📊 Round 1-5 수정 계획

### ✅ Round 1-3: 기본 구조 (수정 불필요)
- **현재 상태**: 완료
- **수정 필요도**: 0%
- **이유**: 기본 GitHub 연동, 프로젝트 구조는 그대로 유지

### 🔧 Round 4: Auto-Onboarding + PL Bot (30% 수정)
**현재 구현**:
```python
# pl-bot/pl-bot-v3.py
class PLBot:
    def send_to_ai(self, ai_name, message):
        # iTerm 세션으로 전송
        send_via_applescript(tab_number, message)
```

**수정 후**:
```python
# pl-bot/pl-bot-v4.py  
class PLBotV4:
    def send_to_ai(self, ai_name, message):
        # -p 모드로 직접 실행
        result = subprocess.run(f'{ai_name} -p "{message}"', capture_output=True)
        return result.stdout
```

**수정 사항**:
- ❌ 제거: AppleScript 의존성
- ✅ 추가: -p 모드 실행
- ✅ 유지: GitHub 통합, Allow 시스템

### 🔧 Round 5: iTerm2 Native (70% 수정)

**현재 문제점**:
```python
# unified_ai_communicator.py
class UnifiedAICommunicator:
    def __init__(self):
        self.tab_mapping = {  # iTerm 탭 매핑
            "Gemini": 2,
            "Codex": 3,
            "Claude": 4
        }
    
    def send_to_ai(self, ai_name, message):
        # 복잡한 세션 관리
        script = f'tell application "iTerm2"...'
        subprocess.run(['osascript', '-e', script])
```

**수정 후**:
```python
# p_mode_orchestrator.py
class PModeOrchestrator:
    def execute_parallel(self, tasks):
        with ThreadPoolExecutor() as executor:
            futures = []
            for ai, task in tasks.items():
                future = executor.submit(
                    lambda: subprocess.run(f'{ai} -p "{task}"', capture_output=True)
                )
                futures.append(future)
        return [f.result() for f in futures]
```

**대대적 수정**:
- ❌ 완전 제거: `iterm2_orchestra.py`, `iterm_session_manager.py`
- ❌ 제거: 모든 AppleScript 파일
- ✅ 새로 구현: 병렬 처리 시스템
- ✅ 유지: KPI 측정 로직

---

## 🗂️ 현재 v02 프로젝트 수정 사항

### 1. **즉시 제거 대상** (50+ 파일)
```bash
# AppleScript 파일들 (30개+)
rm -f *.applescript
rm -f send_*.applescript
rm -f test_*.applescript

# iTerm 세션 관련 Python (10개+)
rm -f iterm2_api_test.py
rm -f gemini_iterm_api.py
rm -f send_to_gemini*.py
rm -f activate_and_send.py
rm -f check_sessions.py

# 테스트 파일들 (아카이브)
mkdir -p archive/old_tests
mv test_*.py archive/old_tests/
mv test_*.sh archive/old_tests/

# 불필요한 데모 파일
rm -f bts_*.sh  # BTS 데모는 문서로 충분
rm -f simple_test*.sh
```

### 2. **수정 필요 파일** (핵심 5개)

#### A. `multi_ai_orchestrator.py` (이미 -p 모드)
```python
# 현재: 좋음, 약간 개선 필요
class MultiAIOrchestrator:
    def __init__(self):
        self.ais = {
            "gemini": {"cmd": "gemini -p"},  # ✅ 이미 -p 모드
            "claude": {"cmd": "claude -p"},
            "codex": {"cmd": "codex -p"}
        }

# 개선: 에러 처리 강화
    def run_ai(self, ai_name, prompt):
        try:
            result = subprocess.run(...)
        except subprocess.TimeoutExpired:
            # 재시도 로직 추가
            return self.retry_with_backoff(ai_name, prompt)
```

#### B. `relay_pipeline_system.py` (유지, 개선)
```python
# 현재: 좋은 구조
class RelayPipeline:
    stages = [
        {"ai": "claude", "role": "구현"},
        {"ai": "gemini", "role": "테스트"},
        {"ai": "codex", "role": "리뷰"}
    ]

# 개선: GitHub Issue 자동 생성 추가
    def create_pipeline_issue(self, title, body):
        issue = gh.create_issue(
            title=f"[Pipeline] {title}",
            body=body,
            labels=["relay-pipeline", "auto-generated"]
        )
        return self.process_issue(issue.number)
```

#### C. `persona_training_system.py` (유지, 최적화)
```python
# 현재: 메모리 과다 사용 가능성
def generate_training_data(self, problem):
    # 6개 페르소나 동시 실행
    
# 개선: 배치 처리
def generate_training_data_batch(self, problems, batch_size=3):
    for i in range(0, len(self.personas), batch_size):
        batch = self.personas[i:i+batch_size]
        # 3개씩 처리하여 메모리 절약
```

### 3. **새로 생성 필요** (5개)

```python
# 1. migration_helper.py
class MigrationHelper:
    """기존 프로젝트에서 데이터 마이그레이션"""
    def migrate_from_dashboard(self):
        # KPI 데이터 이전
        # PL Bot 설정 이전
        # Round 진행 상황 이전

# 2. memory_manager.py  
class MemoryManager:
    """컨텍스트 자동 관리"""
    def checkpoint(self):
        # 현재 상태 저장
    def compress(self):
        # 대화 압축
    def cleanup(self):
        # 불필요한 메모리 정리

# 3. issue_template_generator.py
class IssueTemplateGenerator:
    """Round별 Issue 자동 생성"""
    def generate_round_issues(self, round_num):
        templates = {
            6: "Terminal OS 구축",
            7: "Framework API",
            8: "Marketplace",
            9: "AI Learning",
            10: "Full Automation"
        }

# 4. performance_monitor.py
class PerformanceMonitor:
    """실시간 성능 모니터링"""
    def track_memory(self):
        # 메모리 사용량 추적
    def track_response_time(self):
        # AI 응답 시간 측정

# 5. auto_documenter.py
class AutoDocumenter:
    """자동 문서 생성"""
    def generate_round_report(self, round_num):
        # Round 완료 리포트
    def update_readme(self):
        # README 자동 업데이트
```

---

## 📋 통합 수정 체크리스트

### Round 1-3 (기본 구조)
- [x] 수정 불필요 - GitHub 연동 유지

### Round 4 (Auto-Onboarding)
- [ ] `pl-bot-v3.py` → `pl-bot-v4.py` (-p 모드)
- [ ] Allow 시스템 유지
- [ ] `setup-wizard.py` 업데이트

### Round 5 (iTerm2 Native)
- [ ] `unified_ai_communicator.py` → 제거
- [ ] `iterm_session_manager.py` → 제거  
- [ ] `team_kpi_tracker.py` → 유지 (로직만)
- [ ] 새로운 병렬 처리 시스템 구현

### 현재 v02 프로젝트
- [ ] AppleScript 파일 30개+ 제거
- [ ] iTerm 관련 Python 10개+ 제거
- [ ] 테스트 파일 아카이브
- [ ] 핵심 3개 파일 개선
- [ ] 새 파일 5개 생성

---

## 🚀 실행 순서

### Day 1: 정리 & 준비
```bash
# 1. 백업
cp -r . ../ai-orchestra-v02-backup/

# 2. 대청소
rm -f *.applescript
rm -f test_*.py
mkdir -p archive && mv old_files archive/

# 3. 핵심 파일 정리
mkdir -p core
cp multi_ai_orchestrator.py core/
cp relay_pipeline_system.py core/
cp persona_training_system.py core/
```

### Day 2: Round 4-5 수정
```bash
# 1. Dashboard에서 가져오기
cp ../ai-orchestra-dashboard/pl-bot/pl-bot-v3.py .
cp ../ai-orchestra-dashboard/team_kpi_tracker.py .

# 2. -p 모드로 수정
python upgrade_to_p_mode.py

# 3. 테스트
python test_p_mode_integration.py
```

### Day 3: 새 기능 구현
```bash
# 1. 메모리 관리
python memory_manager.py

# 2. 성능 모니터
python performance_monitor.py  

# 3. 통합 테스트
python full_integration_test.py
```

---

## 📊 예상 결과

### 파일 수 변화
- **현재**: 70+ 파일 (복잡)
- **수정 후**: 20개 파일 (간결)
- **감소율**: 70%

### 코드 라인 수
- **현재**: 5,000+ 라인
- **수정 후**: 1,500 라인
- **감소율**: 70%

### 메모리 사용량
- **현재**: 500MB+
- **수정 후**: 50MB
- **감소율**: 90%

### 응답 속도
- **Round 5 현재**: 4.1초
- **수정 후**: 0.5초
- **개선율**: 88%

---

## 💡 핵심 인사이트

**"Less is More"** - 복잡한 세션 관리를 제거하고 -p 모드로 단순화하면:

1. **코드 70% 감소** → 유지보수 용이
2. **메모리 90% 절약** → 성능 향상  
3. **속도 88% 개선** → 사용자 경험 향상
4. **Round 6-10 개발 시간 75% 단축** → 빠른 완성

**결론**: 지금이 전환의 최적 시기! 🚀

*작성: Claude Code & Thomas*  
*2025-08-23*