#!/usr/bin/osascript

tell application "iTerm"
    tell current window
        tell current tab
            -- 세션 목록 확인
            set sessionList to sessions
            
            -- 두 번째 세션(분할된 pane)에 전송
            if (count of sessionList) ≥ 2 then
                tell item 2 of sessionList
                    write text "다음 3줄을 정확히 출력해주세요:
@@ACK id=ISSUE-TEST-1
@@RUN id=ISSUE-TEST-1  
@@EOT id=ISSUE-TEST-1 status=OK answer=2"
                end tell
                return "Message sent to Gemini pane!"
            else
                return "No split pane found"
            end if
        end tell
    end tell
end tell