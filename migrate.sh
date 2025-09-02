#!/bin/bash

# AI Orchestra v02 Migration Script
# 사용법: ./migrate.sh [대상프로젝트경로]

set -e

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# 소스 경로
SOURCE_DIR="/Users/m4_macbook/Projects/ai-orchestra-v02"

# 대상 경로 확인
if [ -z "$1" ]; then
    echo -e "${RED}❌ 사용법: ./migrate.sh [대상프로젝트경로]${NC}"
    exit 1
fi

TARGET_DIR="$1"

if [ ! -d "$TARGET_DIR" ]; then
    echo -e "${RED}❌ 대상 디렉토리가 존재하지 않습니다: $TARGET_DIR${NC}"
    exit 1
fi

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}🚀 AI Orchestra v02 이식 시작${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""
echo -e "${YELLOW}소스: $SOURCE_DIR${NC}"
echo -e "${YELLOW}대상: $TARGET_DIR${NC}"
echo ""

# 1. 폴더 구조 생성
echo -e "${GREEN}📁 폴더 구조 생성...${NC}"
mkdir -p "$TARGET_DIR/ai_orchestra/personas"
mkdir -p "$TARGET_DIR/ai_orchestra/nodes"
mkdir -p "$TARGET_DIR/ai_orchestra/dags"
mkdir -p "$TARGET_DIR/.github/ISSUE_TEMPLATE"

# 2. 핵심 파일 복사
echo -e "${GREEN}📦 핵심 파일 복사...${NC}"

# 엔진 파일들
cp "$SOURCE_DIR/orchestrator.py" "$TARGET_DIR/ai_orchestra/" 2>/dev/null || true
cp "$SOURCE_DIR/node_system.py" "$TARGET_DIR/ai_orchestra/" 2>/dev/null || true
cp "$SOURCE_DIR/process_engine.py" "$TARGET_DIR/ai_orchestra/" 2>/dev/null || true
cp "$SOURCE_DIR/metrics_system.py" "$TARGET_DIR/ai_orchestra/" 2>/dev/null || true
cp "$SOURCE_DIR/trigger_system.py" "$TARGET_DIR/ai_orchestra/" 2>/dev/null || true

# 진화 시스템
cp "$SOURCE_DIR/evolution_logger.py" "$TARGET_DIR/ai_orchestra/" 2>/dev/null || true
cp "$SOURCE_DIR/EVOLUTION_SYSTEM.md" "$TARGET_DIR/ai_orchestra/" 2>/dev/null || true

# 학습된 패턴 파일들
cp "$SOURCE_DIR/learned_patterns.json" "$TARGET_DIR/ai_orchestra/" 2>/dev/null || true
cp "$SOURCE_DIR/learned_dag_patterns.json" "$TARGET_DIR/ai_orchestra/" 2>/dev/null || true

# 페르소나 시스템
cp -r "$SOURCE_DIR/personas/iwl_team" "$TARGET_DIR/ai_orchestra/personas/" 2>/dev/null || true
cp "$SOURCE_DIR/personas/persona_loader.py" "$TARGET_DIR/ai_orchestra/personas/" 2>/dev/null || true
cp "$SOURCE_DIR/personas/subagent_selector.py" "$TARGET_DIR/ai_orchestra/personas/" 2>/dev/null || true
cp "$SOURCE_DIR/personas/auto_persona_injector.py" "$TARGET_DIR/ai_orchestra/personas/" 2>/dev/null || true
cp "$SOURCE_DIR/personas/iwl_recursive_growth_system.py" "$TARGET_DIR/ai_orchestra/personas/" 2>/dev/null || true

# GitHub 이슈 템플릿
echo -e "${GREEN}📋 이슈 템플릿 복사...${NC}"
cp -r "$SOURCE_DIR/.github/ISSUE_TEMPLATE/"* "$TARGET_DIR/.github/ISSUE_TEMPLATE/" 2>/dev/null || true

# 3. 템플릿 파일 생성
echo -e "${GREEN}📝 템플릿 파일 생성...${NC}"

# multi_ai_orchestrator.py 템플릿
cat > "$TARGET_DIR/multi_ai_orchestrator.py" << 'EOF'
#!/usr/bin/env python3
"""
Multi-AI Orchestrator for [PROJECT_NAME]
GitHub Issue → Multiple AIs → Automatic Execution → Push Results
"""

import subprocess
import json
import time
import re
import os
import sys
from datetime import datetime
from typing import Dict, List, Any

# ai-orchestra-v02 시스템과 통합
sys.path.append(os.path.join(os.path.dirname(__file__), 'ai_orchestra'))
try:
    from orchestrator import SmartOrchestrator
    from node_system import NodeType, NodeFactory
    from process_engine import ProcessBuilder
    from metrics_system import MetricsCollector
except ImportError:
    pass  # 의존성 없어도 기본 기능은 작동

class ProjectOrchestrator:
    def __init__(self):
        self.repo = "your-github/your-repo"  # TODO: 수정 필요!
        self.ais = {
            "gemini": {
                "cmd": "gemini -p",
                "role": "아키텍처 설계"
            },
            "codex": {
                "cmd": "codex exec",
                "role": "백엔드 구현"
            },
            "claude": {
                "cmd": "claude -p",  
                "role": "코드 통합"
            }
        }
    
    # ... (나머지 코드는 StockIQ 예시 참조)

def main():
    import sys
    if len(sys.argv) < 2:
        print("사용법: python3 multi_ai_orchestrator.py [이슈번호]")
        return
    
    issue_number = int(sys.argv[1])
    orchestrator = ProjectOrchestrator()
    orchestrator.process_github_issue(issue_number)

if __name__ == "__main__":
    main()
EOF

# PM 스크립트 템플릿
cat > "$TARGET_DIR/project_pm.sh" << 'EOF'
#!/bin/bash

# Project PM 작업 스크립트
# TODO: 프로젝트명과 레포지토리 수정 필요

PROJECT_NAME="YourProject"
GITHUB_REPO="your-github/your-repo"

echo "=========================================="
echo "🎯 $PROJECT_NAME PM 모드"
echo "=========================================="

case "$1" in
    "status")
        echo "📋 현재 [AI] 이슈:"
        gh issue list -R $GITHUB_REPO --state open --search "[AI]"
        ;;
    "create")
        shift
        TITLE="$1"
        BODY="$2"
        echo "📝 새 이슈 생성..."
        gh issue create --title "[AI] $TITLE" --body "$BODY" -R $GITHUB_REPO
        ;;
    "run")
        shift
        ISSUE_NUMBER="$1"
        echo "🚀 Issue #$ISSUE_NUMBER 실행..."
        python3 multi_ai_orchestrator.py $ISSUE_NUMBER
        ;;
    *)
        echo "사용법:"
        echo "  ./project_pm.sh status"
        echo "  ./project_pm.sh create '제목' '내용'"
        echo "  ./project_pm.sh run [번호]"
        ;;
esac
EOF

# 4. 권한 설정
chmod +x "$TARGET_DIR/multi_ai_orchestrator.py"
chmod +x "$TARGET_DIR/project_pm.sh"

# 5. 설정 확인
echo ""
echo -e "${BLUE}🔍 설정 확인...${NC}"

# AI CLI 확인
echo -e "${YELLOW}AI CLI 도구 확인:${NC}"
for cmd in gemini codex claude cursor chatgpt; do
    if which $cmd > /dev/null 2>&1; then
        echo -e "  ✅ $cmd"
    else
        echo -e "  ⚠️  $cmd (설치 필요)"
    fi
done

# GitHub CLI 확인
echo -e "${YELLOW}GitHub CLI 확인:${NC}"
if which gh > /dev/null 2>&1; then
    echo -e "  ✅ gh"
else
    echo -e "  ❌ gh (필수! brew install gh)"
fi

# 6. 완료
echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}✅ 이식 완료!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "${YELLOW}📋 다음 단계:${NC}"
echo "1. $TARGET_DIR/multi_ai_orchestrator.py 수정"
echo "   - self.repo = 'your-github/your-repo' 변경"
echo "   - AI 역할 조정"
echo ""
echo "2. $TARGET_DIR/project_pm.sh 수정"
echo "   - GITHUB_REPO 변경"
echo "   - 프로젝트명 변경"
echo ""
echo "3. 테스트 실행"
echo "   cd $TARGET_DIR"
echo "   ./project_pm.sh status"
echo ""
echo -e "${BLUE}문제 발생시: https://github.com/ihw33/ai-orchestra-v02/issues${NC}"
EOF