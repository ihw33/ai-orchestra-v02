#!/usr/bin/env python3
"""
수동으로 Session 2를 클릭한 후 실행하는 스크립트
"""

import subprocess
import time

def type_messages():
    """메시지만 타이핑 (세션 선택은 수동)"""
    
    print("📌 실행 전에:")
    print("   1. iTerm2에서 Session 2 (Gemini)를 마우스로 클릭하세요")
    print("   2. Gemini 프롬프트가 활성화된 것을 확인하세요")
    print("   3. 5초 안에 준비하세요!")
    print()
    
    for i in range(5, 0, -1):
        print(f"   {i}초...")
        time.sleep(1)
    
    print("\n🚀 메시지 전송 시작!")
    
    messages = [
        "MANUAL_TEST_1",
        "@@ACK id=MANUAL",
        "@@RUN id=MANUAL",
        "@@EOT id=MANUAL status=OK answer=2"
    ]
    
    for msg in messages:
        # 메시지 타이핑
        for char in msg:
            script = f'''
            tell application "System Events"
                keystroke "{char}"
            end tell
            '''
            subprocess.run(['osascript', '-e', script], capture_output=True)
            time.sleep(0.02)
        
        # Enter
        subprocess.run(['osascript', '-e', 
                       'tell application "System Events" to key code 36'],
                       capture_output=True)
        
        print(f"  ✅ {msg}")
        time.sleep(0.5)
    
    print("\n✨ 완료! Gemini 세션을 확인하세요.")

if __name__ == "__main__":
    type_messages()