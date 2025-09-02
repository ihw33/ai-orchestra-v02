#!/usr/bin/env python3
"""
iTerm2 세션 구조 정확히 파악하기
"""

import iterm2
import asyncio

async def main(connection):
    """모든 창과 탭, 세션 정보 출력"""
    
    app = await iterm2.async_get_app(connection)
    
    print("🔍 iTerm2 전체 세션 구조 분석")
    print("=" * 60)
    
    # 모든 창 확인
    windows = app.windows
    for w_idx, window in enumerate(windows):
        print(f"\n📱 Window {w_idx + 1}:")
        
        # 각 창의 탭들
        for t_idx, tab in enumerate(window.tabs):
            print(f"  📑 Tab {t_idx + 1}:")
            
            # 각 탭의 세션들
            for s_idx, session in enumerate(tab.sessions):
                name = await session.async_get_variable("jobName")
                title = await session.async_get_variable("autoName")
                path = await session.async_get_variable("path")
                
                # 현재 활성 세션인지 확인
                is_active = (session == tab.current_session)
                active_mark = " ⭐️ (ACTIVE)" if is_active else ""
                
                print(f"    🖥  Session {s_idx + 1}{active_mark}:")
                print(f"       Name: {name or 'None'}")
                print(f"       Title: {title or 'None'}")
                print(f"       Path: {path or 'None'}")
    
    print("\n" + "=" * 60)
    print("💡 Gemini가 실행 중인 세션을 알려주세요.")
    print("   예: Window 1, Tab 1, Session 2")

if __name__ == "__main__":
    iterm2.run_until_complete(main)