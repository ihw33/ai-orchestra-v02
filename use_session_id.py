#!/usr/bin/env python3
"""
Session ID를 직접 사용해서 전송
"""

import iterm2
import asyncio

async def main(connection):
    """Session ID로 직접 찾아서 전송"""
    
    app = await iterm2.async_get_app(connection)
    
    # 모든 세션 정보 수집
    print("🔍 모든 세션 검색 중...")
    
    all_sessions = []
    for window in app.windows:
        for tab in window.tabs:
            for session in tab.sessions:
                session_id = session.session_id
                name = await session.async_get_variable("jobName")
                title = await session.async_get_variable("autoName")
                all_sessions.append((session, session_id, name, title))
                print(f"  Found: {title} (ID: {session_id})")
    
    # test-gemini 세션 찾기
    gemini_session = None
    for session, sid, name, title in all_sessions:
        if "gemini" in (title or "").lower() or "gemini" in (name or "").lower():
            gemini_session = session
            print(f"\n✅ Gemini 세션 발견: {title} (ID: {sid})")
            break
    
    if not gemini_session:
        print("❌ Gemini 세션을 찾을 수 없습니다")
        return
    
    # 메시지 전송
    print("\n📨 Gemini 세션에 직접 전송:")
    
    messages = [
        "DIRECT_ID_TEST",
        "@@ACK id=DIRECT",
        "@@RUN id=DIRECT",
        "@@EOT id=DIRECT status=OK"
    ]
    
    for msg in messages:
        await gemini_session.async_send_text(msg + "\n")
        print(f"  ✅ {msg}")
        await asyncio.sleep(0.3)
    
    print("\n✨ 완료! Gemini 세션을 확인하세요.")

if __name__ == "__main__":
    iterm2.run_until_complete(main)