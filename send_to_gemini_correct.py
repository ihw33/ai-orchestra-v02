#!/usr/bin/env python3
"""
Session 2 (test-gemini)에 정확히 전송
"""

import iterm2
import asyncio

async def main(connection):
    """Gemini (Session 2)에 메시지 전송"""
    
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
    
    # Session 2가 test-gemini (Gemini)
    gemini_session = sessions[1]  # 0-indexed, 두 번째 세션
    
    print("🚀 Gemini (Session 2: test-gemini)와 통신")
    print("=" * 50)
    
    # 한 줄로 전송하고 Enter
    message = "Output exactly: @@ACK id=TEST2, @@RUN id=TEST2, @@EOT id=TEST2 status=OK"
    
    print(f"\n📨 전송: {message}")
    
    # 메시지 전송 (write text는 자동으로 Enter를 추가함)
    await gemini_session.async_send_text(message + "\n")
    
    print("✅ 전송 완료! (Enter 포함)")
    
    # 잠시 대기
    await asyncio.sleep(1)
    
    # 3줄 형식도 테스트
    print("\n📨 3줄 형식 전송:")
    lines = [
        "Please output these 3 lines:",
        "@@ACK id=GEMINI-TEST",
        "@@RUN id=GEMINI-TEST",
        "@@EOT id=GEMINI-TEST status=OK answer=2"
    ]
    
    for line in lines:
        await gemini_session.async_send_text(line + "\n")
        print(f"  ✅ {line}")
        await asyncio.sleep(0.2)
    
    print("\n✨ 완료! Gemini 세션 (Session 2)을 확인하세요.")

if __name__ == "__main__":
    iterm2.run_until_complete(main)