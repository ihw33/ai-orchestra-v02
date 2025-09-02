#\!/usr/bin/env python3
"""AI 실행 테스트"""

import subprocess
import json

def test_direct_ai():
    """직접 AI 실행 테스트"""
    
    # 1. 간단한 테스트
    test_commands = [
        ('gemini -p "한 줄로 응답: 1+1은?"', 'gemini'),
        ('claude -p "한 줄로 응답: 2+2는?"', 'claude'),
    ]
    
    for cmd, name in test_commands:
        print(f"\n🧪 테스트: {name}")
        print(f"명령: {cmd}")
        
        try:
            result = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                print(f"✅ 성공: {result.stdout[:100]}")
            else:
                print(f"❌ 실패: {result.stderr}")
                
        except subprocess.TimeoutExpired:
            print(f"⏰ 타임아웃")
        except Exception as e:
            print(f"❌ 에러: {e}")

if __name__ == "__main__":
    test_direct_ai()
