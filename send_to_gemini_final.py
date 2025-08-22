#!/usr/bin/env python3
"""
iTerm2 Python API를 사용한 Gemini 통신 - 최종 버전
Session 1이 Gemini임을 확인
"""

import iterm2
import asyncio

async def main(connection):
    """Gemini (Session 1)에 3줄 형식 메시지 전송"""
    
    app = await iterm2.async_get_app(connection)
    window = app.current_window
    
    if not window:
        print("❌ iTerm2 창을 찾을 수 없습니다")
        return
    
    tab = window.current_tab
    sessions = tab.sessions
    
    if len(sessions) < 1:
        print("❌ 세션을 찾을 수 없습니다")
        return
    
    # Session 1이 Gemini
    gemini_session = sessions[0]
    
    print("🚀 Gemini (Session 1)와 통신 시작")
    print("=" * 50)
    
    # PR #29 테스트: 3줄 형식 출력 요청
    messages = [
        "Please output exactly these 3 lines:",
        "@@ACK id=FINAL-TEST",
        "@@RUN id=FINAL-TEST",
        "@@EOT id=FINAL-TEST status=OK answer=2"
    ]
    
    print("\n📨 Gemini에 메시지 전송:")
    for msg in messages:
        await gemini_session.async_send_text(msg + "\n")
        print(f"  ✅ {msg}")
        await asyncio.sleep(0.3)
    
    print("\n✨ 전송 완료!")
    print("\n💡 Gemini가 3줄을 정확히 출력하는지 확인하세요:")
    print("   - @@ACK id=FINAL-TEST")
    print("   - @@RUN id=FINAL-TEST")
    print("   - @@EOT id=FINAL-TEST status=OK answer=2")

if __name__ == "__main__":
    iterm2.run_until_complete(main)