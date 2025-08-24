#!/bin/bash
# GitHub 라벨 정리 및 재구성 스크립트

REPO="ihw33/ai-orchestra-v02"

echo "🏷️ GitHub 라벨 정리 시작..."

# 기존 라벨 삭제 (필요없는 것들)
echo "🗑️ 기존 라벨 정리 중..."
gh label delete "bug" -R $REPO --yes 2>/dev/null
gh label delete "documentation" -R $REPO --yes 2>/dev/null
gh label delete "duplicate" -R $REPO --yes 2>/dev/null
gh label delete "enhancement" -R $REPO --yes 2>/dev/null
gh label delete "good first issue" -R $REPO --yes 2>/dev/null
gh label delete "help wanted" -R $REPO --yes 2>/dev/null
gh label delete "invalid" -R $REPO --yes 2>/dev/null
gh label delete "question" -R $REPO --yes 2>/dev/null
gh label delete "wontfix" -R $REPO --yes 2>/dev/null
gh label delete "tests" -R $REPO --yes 2>/dev/null
gh label delete "area:controllers" -R $REPO --yes 2>/dev/null
gh label delete "area:protocol" -R $REPO --yes 2>/dev/null
gh label delete "area:tmux" -R $REPO --yes 2>/dev/null

echo "✨ 새로운 라벨 체계 생성 중..."

# 🔴 우선순위 (Priority)
gh label create "🔴 P0: Critical" -R $REPO --color "FF0000" --description "즉시 처리 필요" --force
gh label create "🟠 P1: High" -R $REPO --color "FF8C00" --description "오늘 내 처리" --force
gh label create "🟡 P2: Medium" -R $REPO --color "FFD700" --description "이번 주 내" --force
gh label create "🟢 P3: Low" -R $REPO --color "32CD32" --description "여유 있을 때" --force

# 📌 상태 (Status)
gh label create "✅ approved" -R $REPO --color "0E8A16" --description "Thomas 승인됨" --force
gh label create "⏸️ on-hold" -R $REPO --color "FFA500" --description "보류 중" --force
gh label create "❌ rejected" -R $REPO --color "B60205" --description "거절됨" --force
gh label create "⏳ pending" -R $REPO --color "C5DEF5" --description "검토 대기 중" --force
gh label create "🚀 in-progress" -R $REPO --color "5319E7" --description "작업 진행 중" --force
gh label create "✨ completed" -R $REPO --color "0E8A16" --description "완료됨" --force

# 🎯 타입 (Type)
gh label create "🎮 feature" -R $REPO --color "A2EEEF" --description "새 기능" --force
gh label create "🐛 bug" -R $REPO --color "D73A4A" --description "버그 수정" --force
gh label create "📚 docs" -R $REPO --color "0075CA" --description "문서화" --force
gh label create "🔧 refactor" -R $REPO --color "FEF2C0" --description "리팩토링" --force
gh label create "🧪 test" -R $REPO --color "FBCA04" --description "테스트" --force
gh label create "🎨 ui/ux" -R $REPO --color "FF69B4" --description "UI/UX 개선" --force

# 👥 담당 AI (Assignee)
gh label create "💬 chatgpt" -R $REPO --color "10A37F" --description "ChatGPT 담당" --force
gh label create "📝 codex" -R $REPO --color "FF6B6B" --description "Codex 담당" --force
gh label create "🤖 claude" -R $REPO --color "8B5CF6" --description "Claude 담당" --force
gh label create "💎 gemini" -R $REPO --color "4285F4" --description "Gemini 담당" --force
gh label create "🎯 pm" -R $REPO --color "FFD93D" --description "PM Claude 담당" --force

# 🏁 프로젝트 단계 (Phase)
gh label create "📱 mobile" -R $REPO --color "1E90FF" --description "모바일 관련" --force
gh label create "🎮 tycoon" -R $REPO --color "9370DB" --description "Project Tycoon" --force
gh label create "📊 dashboard" -R $REPO --color "20B2AA" --description "대시보드" --force
gh label create "🔄 automation" -R $REPO --color "FF1493" --description "자동화" --force

# 🔥 특별 라벨
gh label create "🚨 urgent" -R $REPO --color "FF0000" --description "긴급!" --force
gh label create "💡 idea" -R $REPO --color "FFFF00" --description "아이디어" --force
gh label create "❓ question" -R $REPO --color "CC317C" --description "질문/논의 필요" --force
gh label create "🎉 milestone" -R $REPO --color "00FF00" --description "마일스톤" --force

echo "✅ 라벨 정리 완료!"
echo ""
echo "📊 새로운 라벨 체계:"
echo "  🔴🟠🟡🟢 - 우선순위"
echo "  ✅⏸️❌⏳🚀✨ - 상태"
echo "  🎮🐛📚🔧🧪🎨 - 타입"
echo "  💬📝🤖💎🎯 - 담당 AI"
echo "  📱🎮📊🔄 - 프로젝트"