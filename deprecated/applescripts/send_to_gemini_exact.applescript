#!/usr/bin/osascript

tell application "iTerm"
    tell current window
        tell current tab
            -- Session 2 (Gemini)에 직접 전송
            tell session 2
                write text "다음 3줄을 정확히 출력해주세요:
@@ACK id=ISSUE-TEST-1
@@RUN id=ISSUE-TEST-1  
@@EOT id=ISSUE-TEST-1 status=OK answer=2"
            end tell
        end tell
    end tell
end tell

return "Message sent to Gemini (Session 2)!"