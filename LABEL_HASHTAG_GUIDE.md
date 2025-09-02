# 🏷️ 라벨 & 해시태그 활용 가이드

## 구분 기준

### 🏷️ GitHub 라벨 (프로세스/워크플로우)
**목적**: GitHub 필터링, 자동화 트리거, 워크플로우 관리

#### 프로세스 라벨
- `analysis` - 분석 작업
- `research` - 리서치/조사
- `implementation` - 구현/개발
- `documentation` - 문서화
- `testing` - 테스트
- `review` - 리뷰/검토
- `refactor` - 리팩토링

#### DAG 패턴 라벨
- `parallel` - 병렬 처리
- `relay` - 순차 처리
- `pipeline` - 파이프라인
- `feedback-loop` - 피드백 루프

#### 상태 라벨
- `ai-task` - AI 작업 필요
- `ai-responded` - AI 응답 완료
- `needs-revision` - 수정 필요
- `blocked` - 차단됨

### #️⃣ 해시태그 (컨텐츠/주제)
**목적**: 내용 검색, 주제 분류, 관련 이슈 연결
**위치**: 이슈 본문 하단

#### 주제 해시태그
- `#백업시스템` - 백업 관련
- `#자동화` - 자동화 기능
- `#클라우드코드` - Claude Code 관련
- `#깃훅` - Git Hooks
- `#CI/CD` - 지속적 통합/배포

#### 기술 해시태그
- `#bash` - Bash 스크립트
- `#python` - Python 코드
- `#nodejs` - Node.js
- `#settings.json` - 설정 파일

#### 플랫폼 해시태그
- `#macOS` - Mac 관련
- `#windows` - Windows 관련
- `#linux` - Linux 관련

## 실제 적용 예시

### 이슈 #70의 경우:

**라벨 (GitHub Labels):**
```
- ai-task (AI 작업)
- analysis (분석 프로세스)
- relay (순차 처리)
- documentation (문서화)
```

**해시태그 (본문 내):**
```markdown
## 관련 키워드
#이슈수정 #분석 #리서치 #자동백업 #클라우드코드 
#githooks #settings.json #autocommit #크로스플랫폼
```

## 활용 방법

### 1. 이슈 생성 시
```bash
# 라벨은 gh 명령어로
gh issue create --label "ai-task,analysis,relay"

# 해시태그는 본문에
"...
## 태그
#백업시스템 #자동화 #분석작업
"
```

### 2. 검색 시
```bash
# 라벨로 필터
gh issue list --label "analysis"

# 해시태그로 검색
gh issue list --search "#백업시스템"
```

### 3. 자동화 트리거
- GitHub Actions는 라벨 기반으로 트리거
- 해시태그는 관련 이슈 그룹핑용

## 장점

1. **명확한 구분**: 프로세스(라벨) vs 내용(해시태그)
2. **이중 분류**: 다양한 관점에서 이슈 관리
3. **검색 최적화**: 라벨 필터 + 텍스트 검색
4. **자동화 가능**: 라벨은 Actions 트리거로 활용

## 구현 제안

### 자동 해시태그 추가 스크립트
```bash
#!/bin/bash
# 이슈 내용 분석 후 자동 해시태그 추가
ISSUE_NUM=$1
CONTENT=$(gh issue view $ISSUE_NUM --json body -q .body)

# 키워드 분석
if [[ $CONTENT == *"backup"* ]]; then
  TAGS+=" #백업시스템"
fi
if [[ $CONTENT == *"analysis"* ]]; then
  TAGS+=" #분석"
fi

# 해시태그 추가
gh issue edit $ISSUE_NUM --body "$CONTENT

## 자동 태그
$TAGS"
```