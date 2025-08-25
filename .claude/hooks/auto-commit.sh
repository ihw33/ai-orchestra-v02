#!/bin/bash

# Claude Code 자동 커밋 스크립트
# 코드 변경 시 자동으로 Git 커밋 생성

cd "$CLAUDE_PROJECT_DIR" || exit 1

# Git 저장소 확인
if [ ! -d ".git" ]; then
    exit 0
fi

# 변경사항 확인
if [ -z "$(git status --porcelain)" ]; then
    exit 0
fi

# 커밋 메시지 읽기
if [ -f ".commit_message.txt" ]; then
    commit_message=$(cat .commit_message.txt 2>/dev/null)
    if [ -z "$commit_message" ]; then
        commit_message="🔄 자동 백업: $(date '+%Y-%m-%d %H:%M:%S')"
    fi
else
    commit_message="🔄 자동 백업: $(date '+%Y-%m-%d %H:%M:%S')"
fi

# 모든 변경사항 추가 및 커밋
git add -A
git commit -m "$commit_message" --no-verify >/dev/null 2>&1

exit 0