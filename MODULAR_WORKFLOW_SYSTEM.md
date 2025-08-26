# 🔧 모듈식 워크플로우 시스템

## 개념: 모든 작업을 노드로

**"모든 작업은 조합 가능한 노드다"**

```
[노드1] → [노드2] → [노드3] = 완성된 워크플로우
```

---

## 📦 기본 노드 카탈로그

### 🎯 시작 노드 (Entry Points)

#### CREATE_ISSUE
```yaml
타입: ENTRY_POINT
실행자: PM Claude
입력: 사용자 요청
출력: 이슈 번호
도구: gh issue create
```

#### READ_ISSUE
```yaml
타입: ENTRY_POINT
실행자: 자동 스크립트
입력: 이슈 번호
출력: 이슈 내용
도구: gh issue view
```

### 🏷️ 메타데이터 노드

#### KEYWORD_ENRICHMENT
```yaml
타입: METADATA_ENRICHMENT
실행자: 자동 스크립트
입력: 이슈 제목 + 본문
출력: 라벨 + 해시태그
도구: issue_keyword_recommender.py
언제: 이슈 생성 직후 (선택적)
```

#### PRIORITY_ASSIGNMENT
```yaml
타입: METADATA_ENRICHMENT
실행자: PM Claude
입력: 이슈 내용
출력: P0/P1/P2/P3 라벨
언제: 긴급도 판단 필요시
```

### 🤖 AI 작업 노드

#### AI_ANALYSIS
```yaml
타입: AI_WORK
실행자: Gemini
입력: 분석 대상
출력: 분석 보고서
언제: 리서치/조사 필요시
```

#### AI_IMPLEMENTATION
```yaml
타입: AI_WORK
실행자: Claude
입력: 구현 사양
출력: 코드
언제: 개발 필요시
```

#### AI_TESTING
```yaml
타입: AI_WORK
실행자: Codex
입력: 구현된 코드
출력: 테스트 결과
언제: 검증 필요시
```

### 📝 문서화 노드

#### GENERATE_REPORT
```yaml
타입: DOCUMENTATION
실행자: PM Claude
입력: AI 결과들
출력: 종합 보고서
언제: 작업 완료 후
```

#### UPDATE_README
```yaml
타입: DOCUMENTATION
실행자: 자동 스크립트
입력: 변경사항
출력: README.md 업데이트
언제: 기능 추가 후
```

### ✅ 검증 노드

#### VERIFY_COMPLETION
```yaml
타입: VALIDATION
실행자: PM Claude
입력: 완료 조건 + 현재 상태
출력: 완료 여부
언제: 작업 종료 전
```

#### RUN_TESTS
```yaml
타입: VALIDATION
실행자: 자동 스크립트
입력: 테스트 대상
출력: 테스트 결과
도구: npm test, pytest 등
```

### 🔔 알림 노드

#### NOTIFY_COMPLETION
```yaml
타입: NOTIFICATION
실행자: GitHub Actions
입력: 완료된 작업
출력: 알림 전송
언제: 모든 작업 완료 시
```

---

## 🎲 워크플로우 조합 예시

### 예시 1: 완전 자동화 분석
```
[CREATE_ISSUE] 
    ↓
[KEYWORD_ENRICHMENT]  # 자동 키워드
    ↓
[AI_ANALYSIS]         # AI 분석
    ↓
[GENERATE_REPORT]     # 보고서 생성
    ↓
[NOTIFY_COMPLETION]   # 알림
```

### 예시 2: 긴급 버그 수정
```
[READ_ISSUE]
    ↓
[PRIORITY_ASSIGNMENT] # P0 라벨
    ↓
[AI_IMPLEMENTATION]   # 즉시 수정
    ↓
[RUN_TESTS]          # 테스트
    ↓
[VERIFY_COMPLETION]   # 검증
```

### 예시 3: 문서화 작업
```
[CREATE_ISSUE]
    ↓
[KEYWORD_ENRICHMENT]  # #문서화 태그
    ↓
[AI_ANALYSIS]        # 정보 수집
    ↓
[UPDATE_README]      # 문서 업데이트
```

---

## 🔄 조건부 실행

### IF-THEN 노드
```python
if issue.has_label('urgent'):
    execute(PRIORITY_ASSIGNMENT)
    execute(AI_IMPLEMENTATION, mode='speedster')
else:
    execute(KEYWORD_ENRICHMENT)
    execute(AI_ANALYSIS, mode='perfectionist')
```

### PARALLEL 노드
```python
parallel(
    AI_ANALYSIS,
    AI_IMPLEMENTATION,
    UPDATE_README
)
```

### LOOP 노드
```python
for file in changed_files:
    execute(RUN_TESTS, target=file)
```

---

## 📐 워크플로우 정의 언어

### YAML 방식
```yaml
workflow: analyze_and_fix
nodes:
  - id: create
    type: CREATE_ISSUE
    params:
      title: "버그 수정"
  
  - id: enrich
    type: KEYWORD_ENRICHMENT
    depends_on: create
    optional: true
  
  - id: analyze
    type: AI_ANALYSIS
    depends_on: enrich
    params:
      ai: gemini
      persona: perfectionist
  
  - id: implement
    type: AI_IMPLEMENTATION
    depends_on: analyze
    params:
      ai: claude
```

### Python 방식
```python
workflow = Workflow("analyze_and_fix")
workflow.add_node(CREATE_ISSUE, title="버그 수정")
workflow.add_node(KEYWORD_ENRICHMENT, optional=True)
workflow.add_node(AI_ANALYSIS, ai="gemini")
workflow.add_node(AI_IMPLEMENTATION, ai="claude")
workflow.execute()
```

---

## 🎯 노드 선택 가이드

| 상황 | 필수 노드 | 선택적 노드 |
|------|----------|------------|
| 새 이슈 | CREATE_ISSUE | KEYWORD_ENRICHMENT |
| 분석 작업 | AI_ANALYSIS | GENERATE_REPORT |
| 구현 작업 | AI_IMPLEMENTATION | RUN_TESTS |
| 문서화 | UPDATE_README | AI_ANALYSIS |
| 긴급 작업 | PRIORITY_ASSIGNMENT | NOTIFY_COMPLETION |

---

## 🚀 실행 명령어

### 단일 노드 실행
```bash
./execute_node.sh KEYWORD_ENRICHMENT --issue 70
```

### 워크플로우 실행
```bash
./run_workflow.sh analysis_pipeline --issue 70
```

### 커스텀 조합
```bash
./compose_workflow.sh \
  CREATE_ISSUE \
  KEYWORD_ENRICHMENT \
  AI_ANALYSIS \
  GENERATE_REPORT
```

---

## 📊 노드 실행 통계

```python
# 각 노드의 평균 실행 시간
node_stats = {
    'CREATE_ISSUE': '5초',
    'KEYWORD_ENRICHMENT': '3초',
    'AI_ANALYSIS': '2-5분',
    'AI_IMPLEMENTATION': '5-10분',
    'RUN_TESTS': '1-3분',
    'GENERATE_REPORT': '1분'
}
```

---

## 💡 핵심 원칙

1. **모든 것은 노드**: 작은 단위로 분할
2. **조합 가능**: 레고처럼 조립
3. **선택적 실행**: 필요한 것만
4. **자동화 우선**: 가능한 자동으로
5. **투명성**: 모든 과정 추적 가능