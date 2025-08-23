#!/usr/bin/osascript

on run
    tell application "Terminal"
        -- Gemini가 실행 중인 창을 찾기
        set geminiWindow to window 1
        
        -- 메시지 전송
        set messageToSend to "다음 3줄을 정확히 출력해주세요:
@@ACK id=ISSUE-TEST-1
@@RUN id=ISSUE-TEST-1  
@@EOT id=ISSUE-TEST-1 status=OK answer=2"
        
        -- 텍스트를 클립보드에 복사
        set the clipboard to messageToSend
        
        -- Terminal 창 활성화
        activate
        
        -- 붙여넣기 (Cmd+V)
        tell application "System Events"
            keystroke "v" using command down
            delay 0.5
            -- Enter 키 전송
            keystroke return
        end tell
    end tell
    
    return "Message sent to Gemini!"
end run