#!/usr/bin/env python3
"""
AppleScript를 직접 사용해서 iTerm2 Session 2에 메시지 전송
"""

import subprocess
import time

def send_via_applescript(session_index, message):
    """AppleScript로 특정 세션에 메시지 전송"""
    
    # AppleScript 생성
    script = f'''
    tell application "iTerm"
        tell current window
            tell current tab
                -- Session {session_index} 선택 및 포커스
                select session {session_index}
                delay 0.5
                
                -- 키보드 입력 시뮬레이션
                tell application "System Events"
                    tell process "iTerm2"
                        -- 메시지 타이핑
                        keystroke "{message}"
                        -- Enter 키
                        key code 36
                    end tell
                end tell
            end tell
        end tell
    end tell
    '''
    
    try:
        result = subprocess.run(['osascript', '-e', script], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ 전송 성공: {message}")
            return True
        else:
            print(f"❌ 전송 실패: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ 오류: {e}")
        return False

def main():
    print("🚀 AppleScript로 Gemini (Session 2)에 직접 전송")
    print("=" * 50)
    
    # Session 2 선택하고 포커스
    print("\n1️⃣ Session 2 선택...")
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
    
    # 테스트 메시지들
    messages = [
        "# Direct AppleScript Test",
        "Calculate: 1+1",
        "Format: @@ACK, @@RUN, @@EOT with answer=2"
    ]
    
    print("\n2️⃣ 메시지 전송:")
    for msg in messages:
        send_via_applescript(2, msg)
        time.sleep(1)
    
    print("\n✨ 완료! Session 2 (Gemini)를 확인하세요.")
    print("\n💡 만약 여전히 안 되면:")
    print("   1. iTerm2 재시작")
    print("   2. System Preferences → Security & Privacy → Accessibility")
    print("      → Terminal/iTerm2에 권한 부여 확인")

if __name__ == "__main__":
    main()