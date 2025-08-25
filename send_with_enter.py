#!/usr/bin/env python3
"""
Enter를 확실히 누르기
"""

import subprocess
import time

def clear_and_send():
    """프롬프트 정리하고 새로 전송"""
    
    print("1️⃣ Session 2 선택 및 프롬프트 정리...")
    
    # Session 2 선택
    subprocess.run(['osascript', '-e', '''
    tell application "iTerm"
        activate
        tell current window
            tell current tab
                select session 2
            end tell
        end tell
    end tell
    '''])
    
    time.sleep(0.5)
    
    # Ctrl+C로 현재 입력 취소
    subprocess.run(['osascript', '-e', '''
    tell application "System Events"
        tell process "iTerm2"
            key code 8 using control down
        end tell
    end tell
    '''])
    
    time.sleep(0.5)
    
    # Enter 한 번 눌러서 프롬프트 새로 만들기
    subprocess.run(['osascript', '-e', '''
    tell application "System Events"
        tell process "iTerm2"
            key code 36
        end tell
    end tell
    '''])
    
    time.sleep(1)
    
    print("2️⃣ 새 메시지 전송 (Enter 확실히)...")
    
    # 간단한 메시지 전송
    messages = [
        "HELLO",
        "WORLD",
        "TEST",
        "END"
    ]
    
    for msg in messages:
        # 메시지 타이핑
        subprocess.run(['osascript', '-e', f'''
        tell application "System Events"
            tell process "iTerm2"
                keystroke "{msg}"
            end tell
        end tell
        '''])
        
        time.sleep(0.2)
        
        # Enter 확실히 누르기 (두 번)
        subprocess.run(['osascript', '-e', '''
        tell application "System Events"
            tell process "iTerm2"
                key code 36
                delay 0.1
                key code 36
            end tell
        end tell
        '''])
        
        print(f"  ✅ {msg} + Enter(x2)")
        time.sleep(1)
    
    print("\n✨ 완료! Gemini 세션에서 확인하세요:")
    print("   - HELLO")
    print("   - WORLD")
    print("   - TEST")
    print("   - END")

if __name__ == "__main__":
    clear_and_send()