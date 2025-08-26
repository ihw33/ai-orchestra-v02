# 📊 Node-DAG-Executor 패턴 라이브러리

## 🏷️ KEYWORD_ENRICHMENT 노드 (키워드 강화)

### 노드 타입
**METADATA_ENRICHMENT** - 메타데이터 자동 추가 노드

### 목적
이슈 생성 시 자동으로 적절한 라벨과 해시태그를 추가하여 검색성과 자동화 효율성 향상

### 실행 시점
- **자동**: 이슈 생성 직후
- **수동**: 필요시 호출
- **조건부**: 특정 라벨이 없을 때

### Node-DAG 구조
```
[ANALYZE_CONTENT] → [RECOMMEND_KEYWORDS] → [APPLY_LABELS] → [INJECT_HASHTAGS]
```

### 🔹 노드 정의

#### Node 1: ANALYZE_CONTENT (내용 분석)
- **타입**: TEXT_ANALYSIS
- **실행자**: PM Claude 또는 자동 스크립트
- **입력**: 이슈 제목 + 본문
- **출력**: 키워드 목록
- **도구**: issue_keyword_recommender.py

#### Node 2: RECOMMEND_KEYWORDS (키워드 추천)
- **타입**: CLASSIFICATION
- **실행자**: 추천 시스템
- **입력**: 추출된 키워드
- **출력**: 
  - 프로세스 라벨 (GitHub Labels)
  - 주제 해시태그 (Content Tags)
- **규칙**:
  ```python
  프로세스 라벨: ['analysis', 'research', 'implementation', 'testing']
  주제 해시태그: ['#백업시스템', '#자동화', '#클라우드코드']
  ```

#### Node 3: APPLY_LABELS (라벨 적용)
- **타입**: GITHUB_ACTION
- **실행자**: gh CLI
- **입력**: 추천된 라벨 목록
- **출력**: GitHub 이슈에 라벨 추가
- **명령어**:
  ```bash
  gh issue edit ISSUE_NUM --add-label "analysis,research"
  ```

#### Node 4: INJECT_HASHTAGS (해시태그 주입)
- **타입**: CONTENT_UPDATE
- **실행자**: 이슈 본문 업데이트
- **입력**: 추천된 해시태그
- **출력**: 본문에 해시태그 섹션 추가
- **형식**:
  ```markdown
  ## 🏷️ 키워드
  #분석 #리서치 #자동백업 #클라우드코드
  ```

### 실행 예시
```bash
# 1. 키워드 분석 및 추천
python3 issue_keyword_recommender.py "$TITLE" "$BODY"

# 2. 자동 적용
./apply_keywords.sh ISSUE_NUM
```

### 효과
- 🔍 **검색성 향상**: 라벨과 해시태그로 이중 검색
- 🤖 **자동화 트리거**: 라벨 기반 GitHub Actions
- 📊 **분류 체계화**: 프로세스와 주제 명확 구분
- 🔗 **연관성 파악**: 해시태그로 관련 이슈 그룹핑

---

## 🔄 ISSUE_REVISION 패턴 (이슈 수정)

### 목적
잘못된 지시사항을 발견했을 때 연결된 수정 이슈 생성 및 AI 재지시

### Node-DAG 구조
```
[DETECT_ERROR] → [CREATE_REVISION] → [LINK_ISSUES] → [REDIRECT_AI]
```

### 🔹 노드 정의

#### Node 1: DETECT_ERROR (오류 감지)
- **타입**: REVIEW
- **실행자**: PM Claude
- **입력**: AI 작업 결과
- **출력**: 수정 필요 사항
- **판단 기준**:
  - 구현 vs 분석 혼동
  - 요구사항 불일치
  - 작업 범위 오류

#### Node 2: CREATE_REVISION (수정 이슈 생성)
- **타입**: ISSUE_CREATE
- **실행자**: PM Claude
- **입력**: 수정된 요구사항
- **출력**: 새 이슈 번호
- **템플릿**: issue_revision_template.md

#### Node 3: LINK_ISSUES (이슈 연결)
- **타입**: REFERENCE
- **실행자**: gh CLI
- **입력**: 원본 이슈 + 수정 이슈
- **출력**: 상호 참조 코멘트
- **명령어**:
  ```bash
  gh issue comment ORIGINAL --body "후속 이슈: #NEW"
  gh issue comment NEW --body "원본 이슈: #ORIGINAL"
  ```

#### Node 4: REDIRECT_AI (AI 재지시)
- **타입**: AI_COMMAND
- **실행자**: PM Claude
- **입력**: 수정된 작업 내용
- **출력**: AI별 새 지시사항
- **형식**:
  ```bash
  gemini -p "이슈 #NEW: [수정된 지시]"
  claude -p "이슈 #NEW: [수정된 지시]"
  codex exec "이슈 #NEW: [수정된 지시]"
  ```

### 실행 예시
```bash
./pm_revision_workflow.sh ORIGINAL_ISSUE "clarify" "새로운 지시사항"
```

---

## 🚀 PARALLEL_ANALYSIS 패턴 (병렬 분석)

### 목적
복잡한 문서나 시스템을 여러 AI가 동시에 다른 관점에서 분석

### Node-DAG 구조
```
       [SPLIT_TASK]
    ┌────────┼────────┐
[ANALYZE_A] [ANALYZE_B] [ANALYZE_C]
    └────────┼────────┘
       [SYNTHESIZE]
```

### 적용 사례
- 이슈 #70: Claude Code 자동 백업 솔루션 분석
  - Gemini: 문서 구조 분석
  - Claude: 메커니즘 분석
  - Codex: 코드 품질 평가

---

## 🔍 SOLUTION_ADOPTION_ANALYSIS 패턴 (솔루션 도입 분석)

### 목적
외부 솔루션이나 도구를 우리 프로젝트에 도입하기 위한 타당성 분석

### Node-DAG 구조
```
[PARSE_SOLUTION] → [ANALYZE_FEATURES] → [EVALUATE_FIT] → [ADOPTION_REPORT]
     Gemini            Claude              Codex            PM Claude
```

### 🔹 노드 정의

#### Node 1: PARSE_SOLUTION (솔루션 파싱)
- **타입**: DOCUMENT_ANALYSIS
- **실행자**: Gemini
- **입력**: 솔루션 문서/설명
- **출력**: 구조화된 기능 목록
- **작업**: 디렉토리 구조, 파일 역할, 설치 방법 정리

#### Node 2: ANALYZE_FEATURES (기능 분석)
- **타입**: TECHNICAL_ANALYSIS
- **실행자**: Claude
- **입력**: 파싱된 기능 목록
- **출력**: 작동 메커니즘 설명
- **작업**: Hook 시스템, 자동화 흐름, 핵심 로직 분석

#### Node 3: EVALUATE_FIT (적합성 평가)
- **타입**: EVALUATION
- **실행자**: Codex
- **입력**: 기능 분석 결과
- **출력**: 장단점 및 위험 요소
- **작업**: 보안, 성능, 유지보수성 평가

#### Node 4: ADOPTION_REPORT (도입 보고서)
- **타입**: REPORT_GENERATION
- **실행자**: PM Claude
- **입력**: 모든 분석 결과
- **출력**: 최종 도입 권장사항
- **작업**: 종합 보고서 작성, 적용 방안 제시

### 실행 예시
```bash
# Claude Code 자동 백업 시스템 도입 분석
1. 솔루션 문서 제공
2. SOLUTION_ADOPTION_ANALYSIS 패턴 실행
3. 도입 권장사항 보고서 생성
```

## 📝 DOCUMENTATION_PIPELINE 패턴

### 목적
프로젝트 문서를 체계적으로 생성하고 유지보수

### Node-DAG 구조
```
[GATHER_INFO] → [STRUCTURE_CONTENT] → [WRITE_DOCS] → [REVIEW] → [PUBLISH]
```

### 노드별 담당
- **GATHER_INFO**: Gemini (정보 수집)
- **STRUCTURE_CONTENT**: PM Claude (구조화)
- **WRITE_DOCS**: Claude (작성)
- **REVIEW**: Codex (기술 검토)
- **PUBLISH**: 자동화 스크립트

---

## 🔍 패턴 선택 가이드

| 상황 | 추천 패턴 |
|------|----------|
| 이슈 생성 시 | KEYWORD_ENRICHMENT |
| 지시 오류 발견 | ISSUE_REVISION |
| 복잡한 분석 | PARALLEL_ANALYSIS |
| 문서 작성 | DOCUMENTATION_PIPELINE |
| 긴급 수정 | HOTFIX_EXPRESS |
| 대규모 리팩토링 | REFACTOR_CASCADE |

## 📌 패턴 조합 예시

```yaml
이슈_생성_플로우:
  1. KEYWORD_ENRICHMENT  # 키워드 자동 추가
  2. PARALLEL_ANALYSIS   # AI 분석 시작
  3. DOCUMENTATION_PIPELINE  # 결과 문서화

이슈_수정_플로우:
  1. ISSUE_REVISION     # 수정 이슈 생성
  2. KEYWORD_ENRICHMENT # 새 키워드 추가
  3. REDIRECT_AI        # AI 재실행
```