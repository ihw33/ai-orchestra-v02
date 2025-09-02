#!/usr/bin/env python3
"""
iTerm2 Python API - 세션 활성화 후 전송
중요: async_activate()를 먼저 호출해야 함!
"""

import iterm2
import asyncio

async def main(connection):
    """세션 활성화 후 메시지 전송"""
    
    app = await iterm2.async_get_app(connection)
    window = app.current_window
    
    if not window:
        print("❌ iTerm2 창을 찾을 수 없습니다")
        return
    
    tab = window.current_tab
    sessions = tab.sessions
    
    print(f"📋 찾은 세션 수: {len(sessions)}")
    
    # Session 2 (Gemini) 찾기
    if len(sessions) < 2:
        print("❌ Session 2를 찾을 수 없습니다")
        return
    
    gemini_session = sessions[1]  # Session 2 (0-indexed)
    
    # 세션 정보 확인
    title = await gemini_session.async_get_variable("autoName")
    print(f"🎯 대상 세션: {title}")
    
    # ⭐️ 중요: 세션을 먼저 활성화!
    print("\n1️⃣ Session 2 활성화 중...")
    await gemini_session.async_activate()
    await asyncio.sleep(0.5)  # 활성화 대기
    
    # 이제 메시지 전송
    print("2️⃣ 활성화된 세션에 메시지 전송:")
    
    messages = [
        "# ACTIVATED SESSION TEST",
        "Please output these 3 lines:",
        "@@ACK id=ACTIVE",
        "@@RUN id=ACTIVE",
        "@@EOT id=ACTIVE status=OK answer=2"
    ]
    
    for msg in messages:
        # suppress_broadcast=True로 이 세션에만 전송
        await gemini_session.async_send_text(msg + "\n", suppress_broadcast=True)
        print(f"  ✅ {msg}")
        await asyncio.sleep(0.3)
    
    print("\n✨ 완료! Gemini 세션을 확인하세요.")
    print("\n💡 핵심 차이점:")
    print("   - async_activate()로 세션 활성화")
    print("   - suppress_broadcast=True로 단일 세션 전송")

if __name__ == "__main__":
    iterm2.run_until_complete(main)