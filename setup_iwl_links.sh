#!/bin/bash

# IWL 프로젝트에 AI Orchestra 심볼릭 링크 생성 스크립트

echo "🔗 Setting up AI Orchestra links for IWL projects..."

# AI Orchestra 경로
ORCHESTRA_PATH="/Users/m4_macbook/Projects/ai-orchestra-v02"

# IWL 프로젝트들
IWL_PROJECTS=(
    "/Users/m4_macbook/Projects/iwl-v5-rebuild"
    "/Users/m4_macbook/Projects/iwl-kb-system"
    "/Users/m4_macbook/Projects/iwl-mcp-server"
)

# 각 IWL 프로젝트에 orchestra 디렉토리 생성 및 링크
for PROJECT in "${IWL_PROJECTS[@]}"; do
    echo "📁 Setting up: $PROJECT"
    
    # orchestra 디렉토리 생성
    mkdir -p "$PROJECT/.orchestra"
    
    # 심볼릭 링크 생성
    ln -sf "$ORCHESTRA_PATH/nodes" "$PROJECT/.orchestra/nodes"
    ln -sf "$ORCHESTRA_PATH/dags" "$PROJECT/.orchestra/dags"
    ln -sf "$ORCHESTRA_PATH/executors" "$PROJECT/.orchestra/executors"
    ln -sf "$ORCHESTRA_PATH/generators" "$PROJECT/.orchestra/generators"
    ln -sf "$ORCHESTRA_PATH/personas" "$PROJECT/.orchestra/personas"
    ln -sf "$ORCHESTRA_PATH/core" "$PROJECT/.orchestra/core"
    ln -sf "$ORCHESTRA_PATH/trigger_orchestration.sh" "$PROJECT/.orchestra/trigger.sh"
    
    # 사용 가이드 복사
    cp "$ORCHESTRA_PATH/docs/AI_ORCHESTRA_USAGE_GUIDE.md" "$PROJECT/.orchestra/USAGE.md"
    
    echo "   ✅ Links created in $PROJECT/.orchestra/"
done

echo ""
echo "✅ Setup complete!"
echo ""
echo "📝 Usage in IWL projects:"
echo "   cd iwl-v5-rebuild"
echo "   ./.orchestra/trigger.sh 81"
echo ""
echo "   # Or directly:"
echo "   python .orchestra/executors/iwl_executor.py --issue-id 81"