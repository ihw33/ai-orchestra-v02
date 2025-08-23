#!/usr/bin/osascript

tell application "iTerm"
    activate
    tell current window
        tell current tab
            select session 2
        end tell
    end tell
end tell

delay 1

tell application "System Events"
    tell process "iTerm2"
        -- 한 줄로 전체 메시지 전송 (줄바꿈 없이)
        keystroke "Output these exact 3 lines: @@ACK id=TEST-1 then @@RUN id=TEST-1 then @@EOT id=TEST-1 status=OK answer=2"
        delay 0.5
        -- 마지막에만 Enter
        key code 36
    end tell
end tell

return "One-line message sent!"