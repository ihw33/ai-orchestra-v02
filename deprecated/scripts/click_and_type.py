#!/usr/bin/env python3
"""
마우스 클릭으로 Session 2를 직접 클릭 후 타이핑
"""

import subprocess
import time

def get_session2_position():
    """Session 2의 대략적인 위치 계산"""
    # iTerm 창 활성화
    subprocess.run(['osascript', '-e', 'tell application "iTerm" to activate'])
    time.sleep(1)
    
    # Session 2는 보통 화면 오른쪽 상단
    # 이 좌표는 조정이 필요할 수 있음
    return (800, 300)  # x, y 좌표

def click_at(x, y):
    """특정 좌표 클릭"""
    script = f'''
    tell application "System Events"
        click at {{{x}, {y}}}
    end tell
    '''
    subprocess.run(['osascript', '-e', script])

def main():
    print("🚀 마우스 클릭으로 Session 2 선택 후 메시지 전송")
    print("=" * 50)
    
    # iTerm 활성화
    subprocess.run(['osascript', '-e', 'tell application "iTerm" to activate'])
    time.sleep(1)
    
    print("1️⃣ Session 2 영역 클릭 (화면 오른쪽 상단)...")
    x, y = get_session2_position()
    click_at(x, y)
    time.sleep(1)
    
    print("2️⃣ 메시지 타이핑...")
    
    # 간단한 테스트
    test_messages = [
        "CLICK_TEST_1",
        "CLICK_TEST_2",
        "@@ACK id=CLICK",
        "@@RUN id=CLICK",
        "@@EOT id=CLICK status=OK"
    ]
    
    for msg in test_messages:
        # 메시지 타이핑
        for char in msg:
            script = f'''
            tell application "System Events"
                keystroke "{char}"
            end tell
            '''
            subprocess.run(['osascript', '-e', script])
            time.sleep(0.01)
        
        # Enter
        subprocess.run(['osascript', '-e', 
                       'tell application "System Events" to key code 36'])
        
        print(f"  ✅ {msg}")
        time.sleep(0.5)
    
    print("\n✨ 완료!")
    print("\n💡 만약 클릭 위치가 맞지 않으면:")
    print("   - get_session2_position()의 좌표를 조정하세요")
    print("   - 또는 수동으로 Session 2를 클릭한 후")
    print("   - 2️⃣ 부분만 실행하세요")

if __name__ == "__main__":
    main()