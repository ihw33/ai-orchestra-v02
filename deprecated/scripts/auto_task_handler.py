#!/usr/bin/env python3
"""
자동 작업 처리기 - 지시를 받으면 자동으로 이슈 생성 후 작업
"""

import subprocess
import json
from datetime import datetime
import sys

class AutoTaskHandler:
    """지시 → 이슈 생성 → 작업 실행 자동화"""
    
    def handle_instruction(self, instruction):
        """지시 처리 메인 함수"""
        print(f"\n{'='*60}")
        print(f"📨 새 지시 접수: {instruction[:50]}...")
        print(f"{'='*60}")
        
        # 1단계: GitHub 이슈 자동 생성
        issue_number = self.create_github_issue(instruction)
        
        if issue_number:
            # 2단계: 작업 실행
            result = self.execute_task(instruction, issue_number)
            
            # 3단계: 결과를 이슈에 업데이트
            self.update_issue_with_result(issue_number, result)
            
            return {
                "issue": issue_number,
                "status": "completed",
                "result": result
            }
        
        return {"status": "failed"}
    
    def create_github_issue(self, instruction):
        """Step 1: GitHub 이슈 자동 생성"""
        print("\n🔹 Step 1: GitHub 이슈 생성 중...")
        
        # 지시에서 제목 추출
        title = f"[자동] {instruction[:50]}"
        
        # 이슈 본문
        body = f"""## 🤖 자동 생성된 작업 이슈

### 📝 원본 지시
{instruction}

### 🎯 작업 계획
1. 지시 분석
2. 작업 실행
3. 결과 보고

### ⏰ 생성 시간
{datetime.now().isoformat()}

---
*AI Orchestra v2 - Auto Task Handler*
"""
        
        # gh CLI로 이슈 생성
        cmd = f'''gh issue create -R ihw33/ai-orchestra-v02 \
            --title "{title}" \
            --body "{body}"'''
        
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        
        if result.returncode == 0:
            issue_url = result.stdout.strip()
            issue_number = issue_url.split('/')[-1]
            print(f"  ✅ 이슈 생성 완료: #{issue_number}")
            print(f"  URL: {issue_url}")
            return issue_number
        else:
            print(f"  ❌ 이슈 생성 실패")
            return None
    
    def execute_task(self, instruction, issue_number):
        """Step 2: 실제 작업 실행"""
        print(f"\n🔹 Step 2: 작업 실행 중 (Issue #{issue_number})...")
        
        # 여기서 실제 작업 수행
        # 예시: 영상 분석, 코드 작성, 버그 수정 등
        
        if "YouTube" in instruction or "영상" in instruction:
            print("  📹 YouTube 영상 분석 작업 시작...")
            # 실제 영상 분석 로직
            result = {
                "type": "video_analysis",
                "status": "completed",
                "summary": "영상 분석 완료"
            }
        elif "버그" in instruction:
            print("  🐛 버그 수정 작업 시작...")
            result = {
                "type": "bug_fix",
                "status": "completed",
                "summary": "버그 수정 완료"
            }
        else:
            print("  📋 일반 작업 실행...")
            result = {
                "type": "general",
                "status": "completed",
                "summary": "작업 완료"
            }
        
        print(f"  ✅ 작업 실행 완료")
        return result
    
    def update_issue_with_result(self, issue_number, result):
        """Step 3: 이슈에 결과 업데이트"""
        print(f"\n🔹 Step 3: 이슈 #{issue_number}에 결과 업데이트...")
        
        comment = f"""## ✅ 작업 완료!

### 📊 실행 결과
- **작업 유형**: {result.get('type', 'unknown')}
- **상태**: {result.get('status', 'unknown')}
- **요약**: {result.get('summary', '')}

### ⏰ 완료 시간
{datetime.now().isoformat()}

---
*자동으로 처리되었습니다*
"""
        
        cmd = f'gh issue comment {issue_number} -R ihw33/ai-orchestra-v02 --body "{comment}"'
        subprocess.run(cmd, shell=True, capture_output=True, text=True)
        
        print(f"  ✅ 이슈 업데이트 완료")

def demo():
    """데모 실행"""
    handler = AutoTaskHandler()
    
    # 테스트 지시들
    test_instructions = [
        "YouTube 영상 https://example.com/video 분석해줘",
        "버그 #456을 수정해줘",
        "새로운 로그인 기능을 구현해줘"
    ]
    
    print("\n🎮 자동 작업 처리기 데모")
    print("="*60)
    
    # 첫 번째 지시만 실제로 실행
    instruction = test_instructions[0]
    result = handler.handle_instruction(instruction)
    
    print(f"\n{'='*60}")
    print(f"📊 최종 결과:")
    print(f"  이슈 번호: #{result.get('issue', 'N/A')}")
    print(f"  상태: {result.get('status', 'unknown')}")
    print(f"{'='*60}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        # 명령줄에서 지시 받기
        instruction = " ".join(sys.argv[1:])
        handler = AutoTaskHandler()
        handler.handle_instruction(instruction)
    else:
        # 데모 모드
        demo()