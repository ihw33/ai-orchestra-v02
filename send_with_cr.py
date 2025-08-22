#!/usr/bin/env python3
"""
다양한 Enter 방식 테스트
"""

import iterm2
import asyncio

async def main(connection):
    """여러 가지 Enter 전송 방법 테스트"""
    
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
    
    print("🎯 Gemini 세션 테스트")
    print("=" * 50)
    
    # 세션 활성화
    await gemini_session.async_activate()
    await asyncio.sleep(0.5)
    
    # 방법 1: 텍스트와 \n 분리
    print("\n1️⃣ 방법 1: 텍스트 후 별도 Enter")
    await gemini_session.async_send_text("METHOD1_TEST")
    await asyncio.sleep(0.5)
    await gemini_session.async_send_text("\n")
    print("  ✅ 전송: METHOD1_TEST + Enter")
    
    await asyncio.sleep(1)
    
    # 방법 2: \r 사용
    print("\n2️⃣ 방법 2: Carriage Return (\\r)")
    await gemini_session.async_send_text("METHOD2_TEST\r")
    print("  ✅ 전송: METHOD2_TEST + \\r")
    
    await asyncio.sleep(1)
    
    # 방법 3: \r\n 사용
    print("\n3️⃣ 방법 3: CRLF (\\r\\n)")
    await gemini_session.async_send_text("METHOD3_TEST\r\n")
    print("  ✅ 전송: METHOD3_TEST + \\r\\n")
    
    await asyncio.sleep(1)
    
    # 방법 4: 특수 키 코드
    print("\n4️⃣ 방법 4: Control 문자")
    await gemini_session.async_send_text("METHOD4_TEST")
    await asyncio.sleep(0.5)
    # Control-M (Enter)
    await gemini_session.async_send_text("\x0d")
    print("  ✅ 전송: METHOD4_TEST + Control-M")
    
    await asyncio.sleep(1)
    
    # 방법 5: 빈 줄 추가
    print("\n5️⃣ 방법 5: 더블 Enter")
    await gemini_session.async_send_text("METHOD5_TEST\n\n")
    print("  ✅ 전송: METHOD5_TEST + \\n\\n")
    
    print("\n✨ 테스트 완료!")
    print("\n🔍 어느 방법이 작동했는지 확인하세요:")
    print("   - METHOD1_TEST (텍스트 후 별도 Enter)")
    print("   - METHOD2_TEST (\\r)")
    print("   - METHOD3_TEST (\\r\\n)")
    print("   - METHOD4_TEST (Control-M)")
    print("   - METHOD5_TEST (더블 Enter)")

if __name__ == "__main__":
    iterm2.run_until_complete(main)