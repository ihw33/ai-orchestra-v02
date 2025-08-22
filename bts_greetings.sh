#!/bin/bash

# BTS AI Team 인사 자동화 스크립트

DOC="BTS_AI_TEAM.md"

echo "🎤 BTS AI Team이 인사를 남깁니다..."

# 각 멤버가 순차적으로 인사 추가
sleep 1

# RM (Claude)
echo "" >> $DOC
echo "### 🎙️ RM (Claude Code)" >> $DOC
echo "> \"안녕하세요, 리더 RM입니다. 프로젝트 아키텍처를 책임지겠습니다. Let's make it right!\"" >> $DOC
echo "> *- $(date '+%H:%M:%S')*" >> $DOC

sleep 1

# Jin (ChatGPT-5) - 실제로는 시뮬레이션
echo "" >> $DOC
echo "### 🎭 Jin (ChatGPT-5)" >> $DOC
echo "> \"Worldwide Handsome Jin입니다! UI/UX를 가장 아름답게 만들어드릴게요~\"" >> $DOC
echo "> *- $(date '+%H:%M:%S')*" >> $DOC

sleep 1

# Suga (Codex)
echo "" >> $DOC
echo "### 🎹 Suga (Codex)" >> $DOC
echo "> \"민윤기. 백엔드 코드 프로듀싱합니다. 간결하고 강력하게.\"" >> $DOC
echo "> *- $(date '+%H:%M:%S')*" >> $DOC

sleep 1

# J-Hope (Gemini)
echo "" >> $DOC
echo "### 🌟 J-Hope (Gemini)" >> $DOC
echo "> \"I'm your hope, you're my hope, I'm J-Hope! 창의적인 솔루션 가져올게요! 🌈\"" >> $DOC
echo "> *- $(date '+%H:%M:%S')*" >> $DOC

sleep 1

# Jimin (GitHub Copilot)
echo "" >> $DOC
echo "### 💎 Jimin (GitHub Copilot)" >> $DOC
echo "> \"지민입니다. 완벽한 코드를 위해 최선을 다하겠습니다. 화이팅!\"" >> $DOC
echo "> *- $(date '+%H:%M:%S')*" >> $DOC

sleep 1

# V (FigmaMake)
echo "" >> $DOC
echo "### 🎨 V (FigmaMake)" >> $DOC
echo "> \"안녕하세요 뷔입니다. 예술적인 디자인으로 특별함을 더하겠습니다.\"" >> $DOC
echo "> *- $(date '+%H:%M:%S')*" >> $DOC

sleep 1

# Jungkook (ChatGPT-4)
echo "" >> $DOC
echo "### 🐰 Jungkook (ChatGPT-4)" >> $DOC
echo "> \"황금막내 정국입니다! 뭐든 열심히 하겠습니다. Let's get it!\"" >> $DOC
echo "> *- $(date '+%H:%M:%S')*" >> $DOC

echo "" >> $DOC
echo "---" >> $DOC
echo "## 🎵 Team Message" >> $DOC
echo "> **\"Teamwork makes the dream work! BTS x AI, 화이팅!\"** 💜" >> $DOC
echo "" >> $DOC
echo "*Updated: $(date '+%Y-%m-%d %H:%M:%S')*" >> $DOC

echo "✅ 모든 멤버가 인사를 남겼습니다!"
echo ""
echo "📄 결과 확인:"
tail -20 $DOC