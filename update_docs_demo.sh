#!/bin/bash

# 문서 자동 업데이트 데모

DOC_FILE="PROJECT_STATUS.md"

# 1. 기존 문서 생성 (없으면)
if [ ! -f "$DOC_FILE" ]; then
    echo "# 📋 프로젝트 상태" > $DOC_FILE
    echo "" >> $DOC_FILE
    echo "## 진행 상황" >> $DOC_FILE
    echo "- [ ] 초기 설정" >> $DOC_FILE
    echo "- [ ] 코드 작성" >> $DOC_FILE
    echo "- [ ] 테스트" >> $DOC_FILE
    echo "" >> $DOC_FILE
    echo "## 작업 로그" >> $DOC_FILE
    echo "" >> $DOC_FILE
fi

echo "📄 기존 문서:"
cat $DOC_FILE
echo "---"

# 2. Gemini가 체크박스 업데이트
echo -e "\n🤖 Gemini: 초기 설정 완료 체크..."
sed -i '' 's/- \[ \] 초기 설정/- \[x\] 초기 설정/' $DOC_FILE

# 3. Codex가 새 섹션 추가
echo "🤖 Codex: 코드 섹션 추가..."
echo "" >> $DOC_FILE
echo "### 생성된 코드 ($(date '+%H:%M:%S'))" >> $DOC_FILE
echo '```python' >> $DOC_FILE
echo "def auto_generated():" >> $DOC_FILE
echo "    return 'By Codex at $(date)'" >> $DOC_FILE
echo '```' >> $DOC_FILE

# 4. Claude가 작업 로그 업데이트
echo "🤖 Claude: 로그 업데이트..."
# 작업 로그 섹션 찾아서 추가
sed -i '' '/## 작업 로그/a\
- '"$(date '+%Y-%m-%d %H:%M')"': AI 팀 자동 업데이트 완료' $DOC_FILE

# 5. 버전 정보 업데이트
echo "" >> $DOC_FILE
echo "---" >> $DOC_FILE
echo "*최종 업데이트: $(date '+%Y-%m-%d %H:%M:%S')*" >> $DOC_FILE

echo -e "\n✅ 업데이트된 문서:"
cat $DOC_FILE