#!/usr/bin/env python3
"""
안전하게 한 글자씩 전송
"""

import subprocess
import time

def send_char_by_char(text):
    """한 글자씩 안전하게 전송"""
    
    for char in text:
        if char == ' ':
            # 스페이스는 space 키
            subprocess.run(['osascript', '-e', 
                          'tell application "System Events" to key code 49'])
        elif char == '\n':
            # 엔터는 return 키
            subprocess.run(['osascript', '-e', 
                          'tell application "System Events" to key code 36'])
        else:
            # 일반 문자
            script = f'''
            tell application "System Events"
                keystroke "{char}"
            end tell
            '''
            subprocess.run(['osascript', '-e', script])
        
        time.sleep(0.01)  # 각 문자 사이 짧은 대기

def main():
    print("🚀 Session 2 선택 후 안전하게 전송")
    
    # 1. Session 2 선택
    print("1️⃣ Session 2 선택...")
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
    
    time.sleep(1)
    
    # 2. 짧은 테스트 메시지
    print("2️⃣ 짧은 메시지 전송...")
    messages = [
        "TEST MESSAGE",
        "@@ACK TEST",
        "@@RUN TEST", 
        "@@EOT TEST OK"
    ]
    
    for msg in messages:
        print(f"  📨 전송: {msg}")
        send_char_by_char(msg)
        send_char_by_char("\n")  # Enter
        time.sleep(0.5)
    
    print("\n✨ 완료! Gemini 세션을 확인하세요.")

if __name__ == "__main__":
    main()