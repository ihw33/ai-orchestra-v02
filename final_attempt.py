#!/usr/bin/env python3
"""
마지막 시도: 다양한 제출 키 테스트
"""

import iterm2
import asyncio

async def main(connection):
    """여러 제출 방법 테스트"""
    
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
    
    gemini_session = sessions[1]
    
    print("🎯 다양한 제출 키 테스트")
    print("=" * 50)
    
    # 세션 활성화
    await gemini_session.async_activate()
    await asyncio.sleep(0.5)
    
    # 테스트 1: Ctrl+J (Line Feed)
    print("\n1️⃣ Ctrl+J (Line Feed) 테스트")
    await gemini_session.async_send_text("TEST_CTRL_J")
    await asyncio.sleep(0.3)
    await gemini_session.async_send_text("\x0a")  # Ctrl+J
    print("  ✅ 전송: TEST_CTRL_J + Ctrl+J")
    
    await asyncio.sleep(1)
    
    # 테스트 2: Ctrl+D (EOF)
    print("\n2️⃣ Ctrl+D (EOF) 테스트")
    await gemini_session.async_send_text("TEST_CTRL_D")
    await asyncio.sleep(0.3)
    await gemini_session.async_send_text("\x04")  # Ctrl+D
    print("  ✅ 전송: TEST_CTRL_D + Ctrl+D")
    
    await asyncio.sleep(1)
    
    # 테스트 3: Tab + Enter 조합
    print("\n3️⃣ Tab 완성 후 Enter")
    await gemini_session.async_send_text("TEST_TAB")
    await asyncio.sleep(0.3)
    await gemini_session.async_send_text("\t\n")  # Tab + Enter
    print("  ✅ 전송: TEST_TAB + Tab + Enter")
    
    await asyncio.sleep(1)
    
    # 테스트 4: 실제 PR #29 목적 - 3줄 한 번에
    print("\n4️⃣ PR #29 테스트: 멀티라인 한 번에")
    full_message = """@@ACK id=FINAL
@@RUN id=FINAL
@@EOT id=FINAL status=OK answer=2"""
    
    await gemini_session.async_send_text(full_message)
    await asyncio.sleep(0.3)
    await gemini_session.async_send_text("\n")
    print("  ✅ 전송: 3줄 메시지 + Enter")
    
    print("\n✨ 테스트 완료!")
    print("\n💡 확인 사항:")
    print("   - TEST_CTRL_J: Line Feed로 실행되었는지")
    print("   - TEST_CTRL_D: EOF로 실행되었는지")
    print("   - TEST_TAB: Tab 완성 후 실행되었는지")
    print("   - 3줄 메시지: 멀티라인이 처리되었는지")
    
    print("\n📌 프롬프트에만 있다면:")
    print("   → tmux 또는 다른 방법 필요")
    print("   → 하지만 텍스트 전송은 100% 확실함!")

if __name__ == "__main__":
    iterm2.run_until_complete(main)