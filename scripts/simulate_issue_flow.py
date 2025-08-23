#!/usr/bin/env python3
"""
GitHub Issue → Gemini → Comment 플로우 로컬 시뮬레이션
실제 GitHub Actions 없이 전체 플로우 테스트
"""

import sys
import os
import subprocess
import json
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
sys.path.insert(0, str(Path(__file__).parent.parent))

def main():
    print("=" * 70)
    print("🎭 GitHub Issue → EXEC → Gemini → Comment 시뮬레이션")
    print("=" * 70)
    
    # 1. 최근 이슈 정보 가져오기
    print("\n📋 Step 1: 최근 이슈 정보 가져오기...")
    result = subprocess.run(
        ["gh", "issue", "view", "28", "-R", "ihw33/ai-orchestra-v02", "--json", "number,title,body"],
        capture_output=True,
        text=True
    )
    
    if result.returncode != 0:
        print(f"❌ 이슈 정보를 가져올 수 없습니다: {result.stderr}")
        return 1
    
    issue = json.loads(result.stdout)
    issue_num = issue["number"]
    issue_title = issue["title"]
    
    print(f"   Issue #{issue_num}: {issue_title}")
    
    # 2. EXEC 메시지 생성
    print("\n🔧 Step 2: EXEC 메시지 생성...")
    
    # 제목에서 수식 추출 (간단한 파싱)
    import re
    expr_match = re.search(r'(\d+[+\-*/]\d+)', issue_title)
    if expr_match:
        expr = expr_match.group(1)
    else:
        expr = "1+1"  # 기본값
    
    task_id = f"ISSUE-{issue_num}"
    exec_msg = f'CALC expr="{expr}" target=gemini task={task_id}'
    
    print(f"   EXEC: {exec_msg}")
    
    # 3. Gemini pane 확인
    print("\n🔍 Step 3: Gemini tmux pane 확인...")
    pane_id = os.getenv("GEMINI_PANE", "gemini-cli:0.0")
    
    print(f"   대상 Pane: {pane_id}")
    
    # 사용 가능한 pane 목록 출력
    panes_result = subprocess.run(
        "tmux list-panes -a -F '#{session_name}:#{window_index}.#{pane_index} (#{pane_id}) [#{pane_current_command}]'",
        shell=True,
        capture_output=True,
        text=True
    )
    
    print("   사용 가능한 panes:")
    for line in panes_result.stdout.strip().split('\n'):
        if 'gemini' in line.lower() or 'cli' in line.lower():
            print(f"      → {line}")
    
    print(f"   선택된 Pane: {pane_id}")
    
    # 4. OrchestrEX로 실행
    print("\n🚀 Step 4: OrchestrEX 실행...")
    
    # Gemini 어댑터로 직접 실행
    from adapters.gemini_adapter import GeminiAdapter, GeminiConfig
    
    config = GeminiConfig(
        name="gemini",
        pane_id=pane_id,
        timeout_ack=5,
        timeout_run=10,
        timeout_eot=30
    )
    
    adapter = GeminiAdapter(config)
    
    print(f"   프롬프트를 Gemini에게 전송 중...")
    result = adapter.execute_with_handshake(exec_msg, task_id)
    
    if result.success:
        print(f"   ✅ 성공! Status: {result.status}")
        
        # 결과에서 답 추출
        if "RESULT=" in result.status:
            answer = result.status.split("RESULT=")[1]
        else:
            answer = "계산 완료"
        
        # 5. GitHub 이슈에 댓글 달기
        print("\n💬 Step 5: GitHub 이슈에 댓글 추가...")
        
        comment_body = f"""## 🤖 Gemini 계산 결과

**문제**: {expr}
**답**: **{answer}**

---
*EXEC: `{exec_msg}`*
*Task ID: {task_id}*
*🎯 3-Step Handshake 성공*"""
        
        comment_result = subprocess.run(
            ["gh", "issue", "comment", str(issue_num), "-R", "ihw33/ai-orchestra-v02", "--body", comment_body],
            capture_output=True,
            text=True
        )
        
        if comment_result.returncode == 0:
            print(f"   ✅ 댓글이 추가되었습니다!")
            print(f"   🔗 https://github.com/ihw33/ai-orchestra-v02/issues/{issue_num}")
        else:
            print(f"   ❌ 댓글 추가 실패: {comment_result.stderr}")
    else:
        print(f"   ❌ 실행 실패: {result.error}")
        
        # 실패 댓글
        print("\n💬 실패 댓글 추가 중...")
        error_comment = f"""## ⚠️ 계산 실패

Gemini와 통신할 수 없습니다.

**오류**: {result.error}
**상태**: {result.status}

---
*EXEC: `{exec_msg}`*
*Task ID: {task_id}*"""
        
        subprocess.run(
            ["gh", "issue", "comment", str(issue_num), "-R", "ihw33/ai-orchestra-v02", "--body", error_comment],
            capture_output=True,
            text=True
        )
    
    print("\n" + "=" * 70)
    print("시뮬레이션 완료!")
    print("=" * 70)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())