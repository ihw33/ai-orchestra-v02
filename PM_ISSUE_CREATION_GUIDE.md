# 📋 PM Issue Creation Guide

## 🎯 PM의 이슈 생성 프로세스

### 0️⃣ 이슈 vs PR 결정
| 구분 | 이슈 (Issue) | PR (Pull Request) |
|------|--------------|-------------------|
| **목적** | 작업 계획/추적 | 코드 변경 제안 |
| **생성 시점** | 작업 시작 전 | 작업 완료 후 |
| **내용** | 요구사항, TODO | 구현 코드, 변경사항 |
| **사용 케이스** | - 새 기능 요청<br>- 버그 리포트<br>- 논의 필요<br>- 작업 할당 | - 코드 수정 완료<br>- 리뷰 요청<br>- 머지 준비됨 |
| **AI 작업** | 이슈로 시작 | AI가 작업 후 PR 생성 |

#### 결정 기준
```python
if "코드가 이미 준비됨":
    create_pr()
elif "작업이 필요함":
    create_issue()
elif "논의가 필요함":
    create_issue()
else:
    create_issue()  # 기본값
```

### 1️⃣ 요청 분석
```
사용자 요청
    ↓
[분석 항목]
- 목표: 무엇을 달성하려 하는가?
- 복잡도: 단순/중간/복잡?
- 긴급도: 즉시/오늘/이번주?
- AI 필요: 코드 작성 필요한가?
```

### 2️⃣ 페르소나 결정
| 키워드 | 페르소나 | 특징 |
|--------|----------|------|
| 긴급, 빨리, ASAP | speedster | ⚡ MVP 우선, 30분 내 |
| 완벽, 꼼꼼, 모든 | perfectionist | ⭐ 엣지케이스 처리 |
| 버그, 문제, 에러 | critic | 🔍 근본 원인 분석 |
| 간단, 최소, 심플 | minimalist | ✨ 최소 코드 |
| (기본값) | balanced | ⚖️ 균형잡힌 접근 |

### 3️⃣ Node-DAG 구조 정의

#### 워크플로우 선택
```python
if "버그" in request:
    workflow = "relay"  # 순차: 수정→검증→테스트
elif "기능" in request:
    workflow = "parallel"  # 병렬: 설계+구현+API
else:
    workflow = "parallel"  # 기본: 병렬
```

#### 노드 템플릿
```yaml
Node:
  name: "ANALYZE_SYSTEM"
  type: "ANALYZE_CODE"
  executor: "Gemini"
  input: "현재 코드베이스"
  output: "분석 결과"
  persona_instruction: "speedster 모드로 핵심만"
  estimated_time: "15분"
```

### 4️⃣ 이슈 구조 템플릿

```markdown
## 🎯 목표
[한 줄로 명확한 목표]

## 🎭 페르소나: [speedster/perfectionist/critic/minimalist/balanced]
- **특성**: [페르소나 특징]
- **목표 시간**: [예상 시간]
- **작업 스타일**: [스타일 설명]

## 🔷 Node-DAG-Executor 구조

### 📊 워크플로우: [Parallel/Relay]
```
[DAG 다이어그램]
```

### 🔹 노드 정의
[각 노드별 상세 정의]

### 🚀 페르소나별 AI 지시사항
[각 AI별 페르소나 지시]

## 📋 체크리스트
- [ ] Phase 1 작업
- [ ] Phase 2 작업
- [ ] Phase 3 작업

## ✅ 완료 조건
1. [구체적 완료 조건 1]
2. [구체적 완료 조건 2]
3. [구체적 완료 조건 3]
```

### 5️⃣ 키워드 추가 (KEYWORD_ENRICHMENT 패턴)

#### 라벨 선택 (프로세스/워크플로우)
```bash
# 자동 추천
python3 issue_keyword_recommender.py "$TITLE" "$BODY"

# 프로세스 라벨
- analysis      # 분석 작업
- research      # 리서치/조사  
- implementation # 구현/개발
- testing       # 테스트
- documentation # 문서화

# DAG 패턴 라벨
- parallel      # 병렬 처리
- relay         # 순차 처리
- pipeline      # 파이프라인
```

#### 해시태그 추가 (주제/기술)
```markdown
## 🏷️ 키워드
#백업시스템 #자동화 #클라우드코드 #깃훅
#python #javascript #bash
```

### 6️⃣ 실행 명령

```bash
# 이슈 생성과 동시에 AI 실행
gh issue create \
  --title "[AI] 작업 제목" \
  --body "$(cat issue_body.md)" \
  --label "ai-task,persona-speedster,parallel" \
  -R ihw33/ai-orchestra-v02

# 즉시 AI 실행 (이슈 번호 받아서)
ISSUE_NUM=$(gh issue list --limit 1 --json number -q '.[0].number')
python3 multi_ai_orchestrator.py $ISSUE_NUM
```

## 📊 패턴 라이브러리

### 🐛 버그 수정 패턴
```
[FIND_BUG] → [FIX_CODE] → [TEST_FIX] → [REVIEW]
   Gemini      Claude       Codex       Gemini
```

### 🎮 기능 개발 패턴
```
        [DESIGN]
           ↓
    ┌──────┴──────┐
[IMPLEMENT]  [API_DESIGN]
    └──────┬──────┘
        [INTEGRATE]
```

### 🔍 분석 패턴
```
    ┌─[ANALYZE_CODE]─┐
    │   [ANALYZE_DB]  │
    └─[ANALYZE_PERF]─┘
           ↓
      [SYNTHESIZE]
```

## 🎯 의사결정 트리

```
사용자 요청
    ↓
Q: 코드 작성/수정 필요?
├─ YES → Q: 복잡한가?
│        ├─ YES → 병렬 3 AI
│        └─ NO → 단일 AI
└─ NO → Q: 분석/조사?
         ├─ YES → Gemini
         └─ NO → 이슈만 생성
```

## 📌 핵심 원칙

1. **이슈는 기록용** - 실행은 바로
2. **페르소나 명확히** - AI 스타일 결정
3. **Node 구조 정의** - 작업 단위 명확히
4. **완료 조건 구체적** - 측정 가능하게

---
마지막 업데이트: 2025-08-25