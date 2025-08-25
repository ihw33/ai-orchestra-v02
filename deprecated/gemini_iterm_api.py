#!/usr/bin/env python3
"""
iTerm2 Python API를 사용한 Gemini 통신
"""

import iterm2
import asyncio
import sys

async def send_to_gemini(connection):
    """Gemini 세션에 메시지 전송"""
    
    app = await iterm2.async_get_app(connection)
    window = app.current_window
    
    if not window:
        print("❌ iTerm2 창을 찾을 수 없습니다")
        return
    
    # 현재 탭의 모든 세션 확인
    tab = window.current_tab
    sessions = tab.sessions
    
    print(f"📋 찾은 세션 수: {len(sessions)}")
    
    # 세션 정보 상세 출력
    for i, session in enumerate(sessions):
        name = await session.async_get_variable("jobName")
        title = await session.async_get_variable("autoName")
        pid = await session.async_get_variable("processId")
        print(f"  세션 {i+1}: {name or 'Unknown'} | Title: {title} | PID: {pid}")
    
    # 사용자에게 세션 선택 요청
    print("\n어느 세션이 Gemini인가요? (1, 2, 또는 3)")
    
    # 모든 세션에 테스트 - 실제로는 선택적으로
    for i, session in enumerate(sessions):
        print(f"\n🎯 세션 {i+1}에 테스트 메시지 전송:")
        
        # 간단한 테스트 메시지
        test_msg = f"[Test Session {i+1}] Echo this: SESSION_{i+1}_OK"
        await session.async_send_text(test_msg + "\n")
        print(f"  ✅ 전송: {test_msg}")
        await asyncio.sleep(0.5)
    
    print("\n각 세션을 확인하고 Gemini가 어느 세션인지 알려주세요.")
    
    # 실제 Gemini 세션은 Session 1!
    if len(sessions) >= 1:
        gemini_session = sessions[0]  # Session 1 (0-indexed)
        
        print(f"\n🎯 Session 1 (실제 Gemini)에 3줄 형식 전송:")
        
        # 테스트 메시지들
        messages = [
            "# Test from iTerm2 Python API",
            "Please output these 3 lines:",
            "@@ACK id=API-TEST",
            "@@RUN id=API-TEST",
            "@@EOT id=API-TEST status=OK answer=2"
        ]
        
        print("\n📨 메시지 전송 중...")
        for msg in messages:
            await gemini_session.async_send_text(msg + "\n")
            print(f"  ✅ {msg}")
            await asyncio.sleep(0.3)  # 각 메시지 사이 대기
        
        print("\n✨ 전송 완료! Gemini 응답을 확인하세요.")
        
        # 세션 출력 모니터링 (선택적)
        try:
            # 2초 대기 후 화면 내용 캡처 시도
            await asyncio.sleep(2)
            
            # 스크린 내용 가져오기
            contents = await gemini_session.async_get_contents()
            if contents:
                print("\n📖 세션 마지막 라인:")
                # 마지막 몇 줄 출력
                lines = contents.string.split('\n')
                for line in lines[-5:]:
                    if line.strip():
                        print(f"  > {line}")
        except Exception as e:
            print(f"\n📖 세션 내용 읽기 실패 (권한 문제일 수 있음): {e}")
    
    else:
        print("❌ Gemini 세션을 찾을 수 없습니다 (Session 2가 없음)")

async def main(connection):
    """메인 함수"""
    print("🚀 iTerm2 Python API로 Gemini 통신 시작")
    print("=" * 50)
    
    # Gemini에 메시지 전송
    await send_to_gemini(connection)

if __name__ == "__main__":
    # iTerm2 Python API 실행
    iterm2.run_until_complete(main)