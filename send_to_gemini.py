#!/usr/bin/env python3
"""
iTerm2에 메시지를 전송하는 Python 스크립트
"""

import subprocess
import time
import sys

def send_to_iterm_via_osascript(message):
    """osascript를 통해 iTerm2에 메시지 전송"""
    script = f'''
    tell application "iTerm"
        tell current window
            tell current tab
                tell session 2
                    write text "{message}"
                end tell
            end tell
        end tell
    end tell
    '''
    
    try:
        result = subprocess.run(['osascript', '-e', script], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ 메시지 전송 성공: {message}")
            return True
        else:
            print(f"❌ 전송 실패: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        return False

def send_via_pyautogui():
    """pyautogui를 사용한 대안 (설치 필요)"""
    try:
        import pyautogui
        
        # iTerm 활성화
        subprocess.run(['osascript', '-e', 
                       'tell application "iTerm" to activate'])
        time.sleep(1)
        
        # Session 2 선택
        subprocess.run(['osascript', '-e', '''
        tell application "iTerm"
            tell current window
                tell current tab
                    select session 2
                end tell
            end tell
        end tell
        '''])
        time.sleep(0.5)
        
        # 메시지 타이핑
        message = "Output exactly: @@ACK id=TEST-1, @@RUN id=TEST-1, @@EOT id=TEST-1 status=OK answer=2"
        pyautogui.typewrite(message, interval=0.01)
        pyautogui.press('enter')
        
        print("✅ pyautogui로 메시지 전송 완료")
        return True
    except ImportError:
        print("❌ pyautogui가 설치되지 않았습니다. pip install pyautogui 실행 필요")
        return False
    except Exception as e:
        print(f"❌ pyautogui 오류: {e}")
        return False

def main():
    print("🚀 Gemini에 메시지 전송 시작")
    
    # 방법 1: osascript 직접 사용
    messages = [
        "Test message from Python",
        "Output these 3 lines:",
        "@@ACK id=PYTHON-TEST",
        "@@RUN id=PYTHON-TEST",
        "@@EOT id=PYTHON-TEST status=OK answer=2"
    ]
    
    for msg in messages:
        if send_to_iterm_via_osascript(msg):
            time.sleep(0.5)  # 각 메시지 사이 대기
        else:
            print(f"메시지 전송 실패: {msg}")
            
            # 대안 시도
            print("\n🔄 pyautogui 방법 시도 중...")
            send_via_pyautogui()
            break
    
    print("\n✨ 전송 완료! Gemini 세션을 확인하세요.")

if __name__ == "__main__":
    main()