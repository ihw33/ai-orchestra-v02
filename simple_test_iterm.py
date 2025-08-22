#!/usr/bin/env python3
"""
매우 간단한 테스트 - 한 단어만
"""

import iterm2
import asyncio

async def main(connection):
    app = await iterm2.async_get_app(connection)
    window = app.current_window
    
    if not window:
        print("❌ 창 없음")
        return
    
    tab = window.current_tab
    sessions = tab.sessions
    
    if len(sessions) < 2:
        print("❌ Session 2 없음")
        return
    
    # Session 2 (Gemini)
    gemini = sessions[1]
    
    print("🎯 간단한 테스트")
    
    # 활성화
    await gemini.async_activate()
    await asyncio.sleep(1)
    
    # 1. 한 단어 테스트
    print("\n1️⃣ 한 단어: hello")
    await gemini.async_send_text("hello\n")
    
    await asyncio.sleep(2)
    
    # 2. 계산 요청
    print("2️⃣ 계산: 1+1")  
    await gemini.async_send_text("1+1\n")
    
    await asyncio.sleep(2)
    
    # 3. echo 테스트
    print("3️⃣ Echo: echo TEST")
    await gemini.async_send_text("echo TEST\n")
    
    print("\n✅ 완료. Gemini 응답 확인하세요.")

if __name__ == "__main__":
    iterm2.run_until_complete(main)