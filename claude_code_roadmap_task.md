# 📋 Claude Code 작업 지시서

## 🎯 작업 목표
현재까지 생성된 모든 체크리스트와 작업 항목을 정리하여 프로젝트 로드맵을 작성하고 우선순위를 정해주세요.

## 📌 작업 내용

### 1. 현재 상태 파악
다음 명령으로 현재 상태를 확인하세요:
```bash
# 열린 이슈 확인
gh issue list -R ihw33/ai-orchestra-v02 --state open

# 열린 PR 확인  
gh pr list -R ihw33/ai-orchestra-v02 --state open

# 프로젝트 보드 확인
gh project list --owner ihw33
```

### 2. 체크리스트 수집
다음 파일들에서 TODO와 체크리스트를 추출하세요:
- `THOMAS_REVIEW_QUEUE.md`
- `MOBILE_TASK_ASSIGNMENT.md`
- `PROJECT_TYCOON_DASHBOARD.md`
- `AUTOMATED_DECISION_PIPELINE.md`
- `ORGANIZATION_AI_SYSTEM.md`
- 기타 관련 문서들

### 3. 로드맵 작성
`PROJECT_ROADMAP.md` 파일을 생성하여 다음 구조로 작성:

```markdown
# 🗺️ Project Roadmap

## 📊 현재 상태 요약
- 완료된 작업: X개
- 진행 중: Y개
- 대기 중: Z개

## 🔥 Phase 1: 긴급 (오늘-내일)
### 1. 승인 대시보드 완성
- [ ] 웹 버전 구현
- [ ] 모바일 접근 설정
- 담당: Claude Code
- 예상: 3시간

### 2. [다음 작업]
...

## 🟡 Phase 2: 단기 (이번 주)
...

## 🟢 Phase 3: 중기 (다음 주)
...

## 🔵 Phase 4: 장기 (이번 달)
...

## 📈 우선순위 매트릭스
| 작업 | 중요도 | 긴급도 | 난이도 | 추천순서 |
|------|--------|--------|--------|----------|
| ... | High | High | Medium | 1 |

## 🎯 추천 작업 순서
1. **즉시**: 승인 대시보드 웹 버전
2. **다음**: ...
3. **그 다음**: ...
```

### 4. GitHub Project Board 업데이트
```bash
# 프로젝트에 이슈 추가
gh project item-add 13 --owner ihw33 --url [issue-url]

# 상태 업데이트
gh project item-edit --id [item-id] --field-id [field-id] --project-id 13
```

## 📊 산출물 요구사항

1. **PROJECT_ROADMAP.md** - 전체 로드맵
2. **PRIORITY_MATRIX.md** - 우선순위 매트릭스
3. **WEEKLY_SPRINT.md** - 이번 주 스프린트 계획

## ⏰ 예상 소요시간
- 현황 파악: 15분
- 로드맵 작성: 30분
- 우선순위 정리: 15분
- **총 1시간**

## 🚀 실행 명령
```bash
# Claude Code로 실행
claude-code exec < claude_code_roadmap_task.md
```

---
**작성자**: PM Claude
**Issue**: 로드맵 정리 작업
**Thomas 보고 예정**