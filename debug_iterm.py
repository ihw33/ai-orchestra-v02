#!/usr/bin/env python3
"""
iTerm2 API 디버깅 - 왜 메시지가 안 가는지 확인
"""

import iterm2
import asyncio

async def main(connection):
    """디버깅"""
    
    app = await iterm2.async_get_app(connection)
    window = app.current_window
    
    if not window:
        print("❌ 창 없음")
        return
    
    tab = window.current_tab
    sessions = tab.sessions
    
    print(f"📋 세션 수: {len(sessions)}")
    
    # Session 2 확인
    if len(sessions) >= 2:
        session2 = sessions[1]
        
        # 세션 상태 확인
        name = await session2.async_get_variable("jobName")
        title = await session2.async_get_variable("autoName")
        unique_id = session2.session_id
        
        print(f"\n🎯 Session 2 정보:")
        print(f"  - ID: {unique_id}")
        print(f"  - Name: {name}")
        print(f"  - Title: {title}")
        
        # 여러 방법으로 전송 시도
        print("\n📨 전송 테스트:")
        
        # 방법 1: async_send_text
        print("  1) async_send_text 시도...")
        try:
            await session2.async_send_text("TEST1_ASYNC_SEND\n")
            print("     ✅ 성공")
        except Exception as e:
            print(f"     ❌ 실패: {e}")
        
        await asyncio.sleep(1)
        
        # 방법 2: async_inject
        print("  2) async_inject 시도...")
        try:
            await session2.async_inject(b"TEST2_INJECT\n")
            print("     ✅ 성공")
        except Exception as e:
            print(f"     ❌ 실패: {e}")
        
        await asyncio.sleep(1)
        
        # 방법 3: write 명령
        print("  3) write 명령 시도...")
        try:
            await session2.async_send_text("write TEST3_WRITE\n")
            print("     ✅ 성공")
        except Exception as e:
            print(f"     ❌ 실패: {e}")
        
        print("\n🔍 Session 2를 확인하세요. 어떤 메시지가 도착했나요?")
        print("   - TEST1_ASYNC_SEND")
        print("   - TEST2_INJECT")
        print("   - TEST3_WRITE")
    
    else:
        print("❌ Session 2가 없습니다")

if __name__ == "__main__":
    iterm2.run_until_complete(main)