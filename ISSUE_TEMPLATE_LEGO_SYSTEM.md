# 🧱 레고식 이슈 템플릿 시스템

## 개념: 조합 가능한 모듈

템플릿을 **기본 블록 + 작업 블록 + 옵션 블록**으로 구성하여 필요에 따라 조합

```
[기본 블록] + [작업 블록] + [옵션 블록] = 완성된 이슈
```

---

## 📦 기본 블록 (필수)

### BASIC_HEADER
```markdown
## 🎯 목표
[한 줄 명확한 목표]

## 🎭 페르소나: [선택]
- **특성**: [특징]
- **목표 시간**: [시간]
```

### BASIC_FOOTER
```markdown
## ✅ 완료 조건
1. [조건1]
2. [조건2]

## 🏷️ 키워드
#태그1 #태그2
```

---

## 🔧 작업 블록 (선택 1개)

### 🔍 ANALYSIS_BLOCK (분석 작업)
```markdown
## 🔷 분석 구조
### 📊 워크플로우: Parallel Analysis
```
    [READ_DOCS]
         ↓
    ┌────┴────┐
[ANALYZE_A] [ANALYZE_B]
    └────┬────┘
         ↓
    [SYNTHESIZE]
```

### 분석 대상
- [ ] 코드베이스 분석
- [ ] 성능 메트릭 분석
- [ ] 보안 취약점 분석
```

### 🛠️ IMPLEMENTATION_BLOCK (구현 작업)
```markdown
## 🔷 구현 구조
### 📊 워크플로우: Pipeline
```
[DESIGN] → [CODE] → [TEST] → [DEPLOY]
```

### 구현 항목
- [ ] API 엔드포인트
- [ ] 프론트엔드 컴포넌트
- [ ] 데이터베이스 스키마
```

### 🐛 BUGFIX_BLOCK (버그 수정)
```markdown
## 🔷 버그 수정 구조
### 📊 워크플로우: Relay
```
[REPRODUCE] → [DIAGNOSE] → [FIX] → [VERIFY]
```

### 버그 정보
- **재현 단계**: [단계]
- **예상 동작**: [동작]
- **실제 동작**: [동작]
```

### 📚 DOCUMENTATION_BLOCK (문서화)
```markdown
## 🔷 문서화 구조
### 📊 워크플로우: Sequential
```
[GATHER] → [STRUCTURE] → [WRITE] → [REVIEW]
```

### 문서 종류
- [ ] API 문서
- [ ] 사용자 가이드
- [ ] 기술 문서
```

### 🔄 REFACTOR_BLOCK (리팩토링)
```markdown
## 🔷 리팩토링 구조
### 📊 워크플로우: Cascade
```
[IDENTIFY] → [PLAN] → [REFACTOR] → [TEST]
```

### 리팩토링 범위
- [ ] 코드 구조 개선
- [ ] 성능 최적화
- [ ] 의존성 업데이트
```

---

## ➕ 옵션 블록 (선택적 추가)

### 🚨 URGENT_ADDON (긴급 작업)
```markdown
## ⚡ 긴급도: CRITICAL
- **마감**: [시간]
- **영향 범위**: [범위]
- **차단 이슈**: #[번호]
```

### 🔗 DEPENDENCY_ADDON (의존성)
```markdown
## 🔗 의존성
- **선행 작업**: #[이슈번호]
- **차단하는 작업**: #[이슈번호]
- **관련 PR**: #[PR번호]
```

### 📊 METRICS_ADDON (측정 지표)
```markdown
## 📊 성공 지표
- **성능**: [목표 수치]
- **커버리지**: [목표 %]
- **사용자 만족도**: [목표 점수]
```

### 🤝 COLLABORATION_ADDON (협업)
```markdown
## 🤝 협업 필요
- **리뷰어**: @[사용자]
- **담당 AI**: [Gemini/Claude/Codex]
- **외부 팀**: [팀명]
```

---

## 🎲 조합 예시

### 예시 1: 긴급 버그 수정
```
BASIC_HEADER 
+ BUGFIX_BLOCK 
+ URGENT_ADDON 
+ BASIC_FOOTER
```

### 예시 2: 복잡한 기능 구현
```
BASIC_HEADER 
+ IMPLEMENTATION_BLOCK 
+ DEPENDENCY_ADDON 
+ METRICS_ADDON 
+ BASIC_FOOTER
```

### 예시 3: 문서화 작업
```
BASIC_HEADER 
+ DOCUMENTATION_BLOCK 
+ COLLABORATION_ADDON 
+ BASIC_FOOTER
```

---

## 🤖 자동 조합 스크립트

```python
class IssueTemplateBuilder:
    def __init__(self):
        self.template = []
    
    def add_basic_header(self, goal, persona):
        self.template.append(BASIC_HEADER.format(goal, persona))
        return self
    
    def add_work_block(self, work_type):
        blocks = {
            'analysis': ANALYSIS_BLOCK,
            'implementation': IMPLEMENTATION_BLOCK,
            'bugfix': BUGFIX_BLOCK,
            'documentation': DOCUMENTATION_BLOCK,
            'refactor': REFACTOR_BLOCK
        }
        self.template.append(blocks[work_type])
        return self
    
    def add_addon(self, addon_type):
        addons = {
            'urgent': URGENT_ADDON,
            'dependency': DEPENDENCY_ADDON,
            'metrics': METRICS_ADDON,
            'collaboration': COLLABORATION_ADDON
        }
        self.template.append(addons[addon_type])
        return self
    
    def build(self):
        self.template.append(BASIC_FOOTER)
        return '\n'.join(self.template)

# 사용 예
builder = IssueTemplateBuilder()
template = (builder
    .add_basic_header("버그 수정", "speedster")
    .add_work_block("bugfix")
    .add_addon("urgent")
    .build())
```

---

## 🎯 선택 가이드

### Q: 어떤 작업 블록을 선택할까?

| 상황 | 추천 블록 |
|------|----------|
| "분석해줘", "조사해줘" | ANALYSIS_BLOCK |
| "만들어줘", "구현해줘" | IMPLEMENTATION_BLOCK |
| "고쳐줘", "에러 나요" | BUGFIX_BLOCK |
| "문서 작성", "설명 필요" | DOCUMENTATION_BLOCK |
| "개선해줘", "정리해줘" | REFACTOR_BLOCK |

### Q: 어떤 옵션을 추가할까?

| 상황 | 추천 옵션 |
|------|----------|
| "급해요", "ASAP" | URGENT_ADDON |
| "A 끝나면 B" | DEPENDENCY_ADDON |
| "성능 중요" | METRICS_ADDON |
| "리뷰 필요" | COLLABORATION_ADDON |

---

## 📝 빠른 생성 명령어

```bash
# 분석 작업
./create_issue.sh analysis "시스템 분석" --addon urgent

# 버그 수정
./create_issue.sh bugfix "로그인 오류" --addon urgent,metrics

# 기능 구현
./create_issue.sh implementation "대시보드 개발" --addon dependency,collaboration
```