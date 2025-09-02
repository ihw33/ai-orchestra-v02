#!/usr/bin/env python3
"""
강제로 Enter 키 이벤트 전송
"""

import iterm2
import asyncio
import subprocess

async def main(connection):
    """Enter를 확실히 전송"""
    
    app = await iterm2.async_get_app(connection)
    window = app.current_window
    
    if not window:
        print("❌ iTerm2 창을 찾을 수 없습니다")
        return
    
    tab = window.current_tab
    sessions = tab.sessions
    
    if len(sessions) < 2:
        print("❌ Session 2를 찾을 수 없습니다")
        return
    
    gemini_session = sessions[1]  # Session 2
    
    print("🎯 Enter 키 강제 전송 테스트")
    print("=" * 50)
    
    # 세션 활성화
    print("\n1️⃣ Session 2 활성화...")
    await gemini_session.async_activate()
    await asyncio.sleep(1)
    
    # 간단한 메시지
    print("2️⃣ 메시지 전송...")
    await gemini_session.async_send_text("FORCE_ENTER_TEST")
    print("  ✅ 텍스트 전송: FORCE_ENTER_TEST")
    
    await asyncio.sleep(0.5)
    
    # AppleScript로 강제 Enter
    print("3️⃣ AppleScript로 Enter 키 전송...")
    script = '''
    tell application "System Events"
        tell process "iTerm2"
            key code 36
        end tell
    end tell
    '''
    subprocess.run(['osascript', '-e', script])
    print("  ✅ Enter 키 전송")
    
    await asyncio.sleep(1)
    
    # 추가 테스트: 3줄 형식
    print("\n4️⃣ 3줄 형식 테스트...")
    messages = [
        "@@ACK id=FORCE",
        "@@RUN id=FORCE",
        "@@EOT id=FORCE status=OK"
    ]
    
    for msg in messages:
        await gemini_session.async_send_text(msg)
        await asyncio.sleep(0.3)
        # 각 줄마다 AppleScript Enter
        subprocess.run(['osascript', '-e', 
                       'tell application "System Events" to key code 36'])
        print(f"  ✅ {msg} + Enter")
    
    print("\n✨ 완료!")
    print("\n🔍 확인 사항:")
    print("   1. FORCE_ENTER_TEST가 실행되었는지")
    print("   2. 3줄 형식이 각각 실행되었는지")

if __name__ == "__main__":
    iterm2.run_until_complete(main)