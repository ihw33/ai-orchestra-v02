#!/usr/bin/env python3
"""
Session 2 포커스 유지하며 전송
"""

import subprocess
import time

def ensure_session2_focus():
    """Session 2에 포커스 확실히 주기"""
    script = '''
    tell application "iTerm"
        activate
        tell current window
            tell current tab
                select session 2
                tell session 2
                    -- 세션 활성화
                    select
                end tell
            end tell
        end tell
    end tell
    '''
    subprocess.run(['osascript', '-e', script])
    time.sleep(0.5)

def send_simple_text(text):
    """단순 텍스트 전송"""
    # 포커스 확인
    ensure_session2_focus()
    
    # 텍스트 전송
    script = f'''
    tell application "System Events"
        tell process "iTerm2"
            set frontmost to true
            keystroke "{text}"
            key code 36
        end tell
    end tell
    '''
    subprocess.run(['osascript', '-e', script])
    print(f"📨 전송: {text}")

def main():
    print("🚀 Session 2 포커스 유지하며 전송")
    print("=" * 50)
    
    # 초기 포커스
    ensure_session2_focus()
    
    # 하나씩 전송 (각각 포커스 재확인)
    messages = [
        "MESSAGE 1",
        "MESSAGE 2",
        "MESSAGE 3",
        "MESSAGE 4"
    ]
    
    print("\n📨 메시지 전송 (각각 포커스 재확인):")
    for msg in messages:
        send_simple_text(msg)
        time.sleep(1)  # 충분한 대기
    
    print("\n✨ 완료! 4개 메시지가 모두 도착했는지 확인하세요.")

if __name__ == "__main__":
    main()