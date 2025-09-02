#!/usr/bin/osascript

on run
    tell application "iTerm"
        -- 현재 창과 세션 확인
        set currentWindow to current window
        
        -- Gemini가 실행 중인 세션 찾기 (보통 두 번째 탭)
        tell currentWindow
            -- 두 번째 탭의 현재 세션 선택
            select tab 2
            set targetSession to current session of tab 2
            
            -- 메시지 전송
            tell targetSession
                write text "다음 3줄을 정확히 출력해주세요:"
                delay 0.5
                write text "@@ACK id=ISSUE-TEST-1"
                delay 0.5
                write text "@@RUN id=ISSUE-TEST-1"
                delay 0.5
                write text "@@EOT id=ISSUE-TEST-1 status=OK answer=2"
                delay 0.5
                write text ""  -- Enter 키
            end tell
        end tell
    end tell
    
    return "Message sent to iTerm2 Gemini session!"
end run