#!/bin/bash

# AI Orchestra 로컬 트리거 스크립트
# GitHub Actions 없이 로컬에서 테스트

set -e

echo "🚀 AI Orchestra - Local Trigger"
echo "================================"

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 인자 확인
if [ $# -lt 1 ]; then
    echo -e "${RED}Usage: $0 <issue_number> [workflow_type]${NC}"
    echo "  workflow_type: feature_development (default), bug_fix, enhancement, refactor"
    exit 1
fi

ISSUE_NUMBER=$1
WORKFLOW_TYPE=${2:-feature_development}

echo -e "${BLUE}📋 Issue: #${ISSUE_NUMBER}${NC}"
echo -e "${BLUE}🔄 Workflow: ${WORKFLOW_TYPE}${NC}"
echo ""

# 1. 이슈 정보 가져오기
echo -e "${YELLOW}1️⃣ Fetching issue information...${NC}"
ISSUE_INFO=$(gh issue view ${ISSUE_NUMBER} --json title,body,labels)
ISSUE_TITLE=$(echo ${ISSUE_INFO} | jq -r '.title')
ISSUE_BODY=$(echo ${ISSUE_INFO} | jq -r '.body')

echo "   Title: ${ISSUE_TITLE}"
echo ""

# 2. Enhanced Workflow 실행
echo -e "${YELLOW}2️⃣ Running Enhanced AI Workflow...${NC}"
python dags/enhanced_ai_task_dag.py \
    --issue "${ISSUE_NUMBER}" \
    --title "${ISSUE_TITLE}" \
    --body "${ISSUE_BODY}" \
    --repo "ihw33/ai-orchestra-v02"

# 3. IWL Executor 실행 (IWL 관련 이슈인 경우)
if [[ "${ISSUE_TITLE}" == *"IWL"* ]] || [[ "${ISSUE_BODY}" == *"IWL"* ]]; then
    echo ""
    echo -e "${YELLOW}3️⃣ Running IWL Executor...${NC}"
    python executors/iwl_executor.py \
        --issue-id ${ISSUE_NUMBER} \
        --workflow ${WORKFLOW_TYPE}
fi

# 4. 상태 확인
echo ""
echo -e "${YELLOW}4️⃣ Checking status...${NC}"
python executors/iwl_executor.py --status

echo ""
echo -e "${GREEN}✅ Orchestration completed!${NC}"
echo ""

# 5. 다음 단계 안내
echo -e "${BLUE}📝 Next Steps:${NC}"
echo "  1. Check the created branch:"
echo "     git fetch origin"
echo "     git branch -r | grep ${ISSUE_NUMBER}"
echo ""
echo "  2. Review issue comments:"
echo "     gh issue view ${ISSUE_NUMBER}"
echo ""
echo "  3. Create PR when ready:"
echo "     gh pr create --fill"