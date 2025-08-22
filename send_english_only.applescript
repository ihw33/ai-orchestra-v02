#!/usr/bin/osascript

tell application "iTerm"
    activate
    tell current window
        tell current tab
            -- Session 2 선택
            select session 2
        end tell
    end tell
end tell

-- 약간의 지연
delay 0.5

tell application "System Events"
    tell process "iTerm2"
        -- 영문으로만 전송
        keystroke "Please output exactly these 3 lines:"
        key code 36 -- Enter
        delay 0.2
        keystroke "@@ACK id=ISSUE-TEST-1"
        key code 36 -- Enter
        delay 0.2
        keystroke "@@RUN id=ISSUE-TEST-1"
        key code 36 -- Enter
        delay 0.2
        keystroke "@@EOT id=ISSUE-TEST-1 status=OK answer=2"
        key code 36 -- Enter
    end tell
end tell

return "English message sent!"