#!/usr/bin/env python3
"""
로컬에서 Gemini 계산 테스트
GitHub Actions 없이 직접 실행 가능
"""

import sys
import os
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
sys.path.insert(0, str(Path(__file__).parent.parent))

def test_gemini_calc():
    """Gemini 계산 기능 테스트"""
    
    # 테스트 EXEC 메시지
    test_cases = [
        ('CALC expr="1+1" target=gemini task=TEST-001', "1+1", "2"),
        ('CALC expr="10-3" target=gemini task=TEST-002', "10-3", "7"),
        ('CALC expr="5*4" target=gemini task=TEST-003', "5*4", "20"),
    ]
    
    print("=" * 60)
    print("🧪 Gemini Calculator Local Test")
    print("=" * 60)
    
    # Gemini pane ID 확인
    pane_id = os.getenv("GEMINI_PANE", "%1")
    print(f"📍 Target Pane: {pane_id}")
    print(f"⚠️  Make sure Gemini CLI is running in tmux pane {pane_id}")
    print()
    
    for exec_msg, expr, expected in test_cases:
        print(f"📝 Test: {expr}")
        print(f"   EXEC: {exec_msg}")
        
        # exec_to_gemini.py 실행
        import subprocess
        result = subprocess.run(
            [
                sys.executable,
                "scripts/exec_to_gemini.py",
                "--exec", exec_msg,
                "--output", "/tmp/gemini_test_result.txt",
                "--pane", pane_id
            ],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            # 결과 읽기
            with open("/tmp/gemini_test_result.txt", "r") as f:
                actual = f.read().strip()
            
            if actual == expected:
                print(f"   ✅ Success: {actual}")
            else:
                print(f"   ❌ Failed: Expected {expected}, got {actual}")
        else:
            print(f"   ❌ Error: {result.stderr}")
        
        print()
    
    print("=" * 60)
    print("테스트 완료!")

if __name__ == "__main__":
    test_gemini_calc()