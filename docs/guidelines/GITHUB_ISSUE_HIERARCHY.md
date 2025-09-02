# GitHub Issue 계층 구조 가이드라인

## 🚨 중요: GitHub 서브이슈 vs Story 구분

### 1. GitHub 서브이슈 (Native Feature)
**GitHub의 기본 기능**
- 이슈 내 체크리스트에서 `Convert to issue` 사용
- 이슈 본문에 `- [ ] #번호` 형식으로 연결
- Parent-Child 관계 자동 추적

**사용 시기**:
- 큰 이슈를 작은 단위로 분해
- 진행 상황 자동 추적 필요
- GitHub Projects 보드 연동

**예시**:
```markdown
## 하위 작업
- [ ] #101 데이터베이스 스키마 설계
- [ ] #102 API 엔드포인트 구현
- [ ] #103 프론트엔드 통합
```

### 2. Story (우리의 라벨 시스템)
**우리가 정의한 계층 구조**
```
[Epic] → [Story] → [Task]
```

**사용 시기**:
- 작업 규모/복잡도 표시
- AI 자동화 트리거
- PR 체인 병합 전략

**예시**:
```markdown
[Epic] #88 GitHub 워크플로우
  └─ [Story] #90 PR 자동화
      └─ [Task] #93 Adapter 구현
```

## 📋 올바른 사용법

### Case 1: 큰 Story를 분해할 때
```bash
# ❌ 잘못된 방법
gh issue create --title "[Story] 하위 작업"

# ✅ 올바른 방법
1. 부모 이슈에 체크리스트 추가
2. Convert to issue 클릭
3. 또는 생성 후 부모 이슈에 - [ ] #번호 추가
```

### Case 2: Epic의 Story 생성할 때
```bash
# ✅ 올바른 방법 (둘 다 사용)
1. Story 라벨로 이슈 생성
2. Epic 이슈에 서브이슈로 연결
```

## 🤖 AI/자동화 시 주의사항

### 서브이슈 생성 자동화
```python
def create_subissue(parent_id: int, title: str):
    # 1. 이슈 생성
    new_issue = create_issue(title)
    
    # 2. 부모 이슈에 연결
    parent_body = get_issue_body(parent_id)
    updated_body = parent_body + f"\n- [ ] #{new_issue.number}"
    update_issue(parent_id, body=updated_body)
```

### Story vs 서브이슈 판단
```python
def should_create_subissue(context):
    if "큰 작업 분해" in context:
        return "subissue"
    elif "Epic 하위 Story" in context:
        return "both"  # Story 라벨 + 서브이슈
    else:
        return "regular"
```

## ⚠️ 혼동 방지 체크리스트

- [ ] "서브이슈"라고 하면 → GitHub 기본 기능
- [ ] "Story"라고 하면 → 우리 라벨 시스템
- [ ] 부모-자식 관계 필요 → 서브이슈 사용
- [ ] 작업 규모 표시 → Story/Task 라벨 사용
- [ ] 둘 다 필요할 수 있음 → 동시 적용 가능

## 📌 기억하기

**"서브이슈 ≠ Story"**
- 서브이슈: GitHub 기능 (관계)
- Story: 우리 라벨 (규모)

두 개념은 **독립적**이며 **함께 사용 가능**