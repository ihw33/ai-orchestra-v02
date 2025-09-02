#!/usr/bin/env python3
"""
iTerm2 Python API를 사용한 직접 통신
먼저 설치 필요: pip3 install iterm2
"""

import asyncio
import iterm2

async def main():
    # iTerm2 연결
    connection = await iterm2.Connection.async_create()
    app = await iterm2.async_get_app(connection)
    
    # 현재 창 가져오기
    window = app.current_window
    if not window:
        print("❌ iTerm2 창을 찾을 수 없습니다")
        return
    
    # 현재 탭의 세션들 확인
    tab = window.current_tab
    sessions = tab.sessions
    
    print(f"📋 찾은 세션 수: {len(sessions)}")
    
    # 두 번째 세션 (Gemini) 찾기
    if len(sessions) >= 2:
        gemini_session = sessions[1]  # 0-indexed, 두 번째 세션
        
        print(f"🎯 Gemini 세션 찾음: {gemini_session.session_id}")
        
        # 메시지 전송
        test_message = """Please output exactly these 3 lines:
@@ACK id=ITERM-API-TEST
@@RUN id=ITERM-API-TEST
@@EOT id=ITERM-API-TEST status=OK answer=2"""
        
        await gemini_session.async_send_text(test_message + "\n")
        print(f"✅ 메시지 전송 완료!")
        
        # 응답 대기
        await asyncio.sleep(2)
        
        # 세션 내용 읽기 시도
        try:
            contents = await gemini_session.async_get_contents()
            print(f"📖 세션 응답 확인 중...")
        except:
            print("📖 세션 내용 읽기는 권한이 필요합니다")
    else:
        print("❌ Gemini 세션을 찾을 수 없습니다")

# 비동기 실행
try:
    import iterm2
    print("🚀 iTerm2 API로 직접 통신 시작")
    iterm2.run_until_complete(main)
except ImportError:
    print("❌ iterm2 모듈이 없습니다. 설치가 필요합니다:")
    print("   pip3 install iterm2")
    print("\n대신 간단한 방법 시도:")
    
    import subprocess
    # 간단한 echo 명령으로 테스트
    cmd = '''
    osascript -e 'tell application "iTerm"
        tell current window
            tell current tab
                tell session 2
                    write text "echo TEST-ECHO"
                end tell
            end tell
        end tell
    end tell'
    '''
    subprocess.run(cmd, shell=True)
    print("✅ echo 테스트 전송")