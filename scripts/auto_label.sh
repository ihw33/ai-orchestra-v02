#!/bin/bash
# 자동 라벨링 스크립트
# 이슈 제목과 본문을 분석하여 적절한 라벨 자동 부여

ISSUE_NUM=$1
REPO="ihw33/ai-orchestra-v02"

if [ -z "$ISSUE_NUM" ]; then
    echo "Usage: $0 <issue_number>"
    exit 1
fi

# 이슈 정보 가져오기
TITLE=$(gh issue view $ISSUE_NUM -R $REPO --json title -q .title)
BODY=$(gh issue view $ISSUE_NUM -R $REPO --json body -q .body)
CURRENT_LABELS=$(gh issue view $ISSUE_NUM -R $REPO --json labels -q '.labels[].name' | tr '\n' ',')

echo "🔍 Analyzing issue #$ISSUE_NUM: $TITLE"

# 적용할 라벨 배열
LABELS=()

# AI 태그 확인
if [[ $TITLE == *"[AI]"* ]]; then
    LABELS+=("ai-task")
fi

# 우선순위 자동 설정 (현재 우선순위 라벨이 없는 경우만)
if [[ ! $CURRENT_LABELS =~ p[0-3]: ]]; then
    if [[ $BODY =~ "긴급"|"즉시"|"critical"|"ASAP" ]] || [[ $TITLE =~ "긴급"|"즉시" ]]; then
        LABELS+=("p0:critical")
    elif [[ $BODY =~ "오늘"|"today"|"urgent" ]] || [[ $TITLE =~ "urgent" ]]; then
        LABELS+=("p1:high")
    elif [[ $BODY =~ "낮음"|"나중"|"low" ]]; then
        LABELS+=("p3:low")
    else
        LABELS+=("p2:medium")
    fi
fi

# 작업 유형 패턴 매칭
if [[ $TITLE =~ "분석"|"검토"|"조사" ]] || [[ $BODY =~ "분석"|"검토" ]]; then
    LABELS+=("analysis")
fi

if [[ $TITLE =~ "구현"|"개발"|"만들" ]] || [[ $BODY =~ "구현"|"개발" ]]; then
    LABELS+=("implementation")
fi

if [[ $TITLE =~ "버그"|"오류"|"수정"|"fix" ]]; then
    LABELS+=("bugfix")
fi

if [[ $TITLE =~ "테스트"|"검증" ]]; then
    LABELS+=("test")
fi

if [[ $TITLE =~ "문서"|"docs"|"README" ]]; then
    LABELS+=("documentation")
fi

if [[ $TITLE =~ "최적화"|"개선"|"리팩토링" ]]; then
    LABELS+=("optimization")
fi

# 라벨 적용
if [ ${#LABELS[@]} -gt 0 ]; then
    LABEL_STRING=$(IFS=,; echo "${LABELS[*]}")
    gh issue edit $ISSUE_NUM -R $REPO --add-label "$LABEL_STRING"
    echo "✅ Applied labels: $LABEL_STRING"
else
    echo "ℹ️ No new labels to apply"
fi