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
        -- 더 긴 메시지를 천천히 전송
        keystroke "I need you to output exactly these three lines without any additional text or explanation. Just copy these lines exactly as shown below:"
        delay 0.5
        key code 36 -- Enter
        delay 0.5
        
        keystroke "@@ACK id=ISSUE-TEST-1"
        delay 0.5
        key code 36 -- Enter
        delay 0.5
        
        keystroke "@@RUN id=ISSUE-TEST-1"
        delay 0.5
        key code 36 -- Enter
        delay 0.5
        
        keystroke "@@EOT id=ISSUE-TEST-1 status=OK answer=2"
        delay 0.5
        key code 36 -- Enter
        delay 0.5
        
        keystroke "Please output only the three lines above starting with @@ symbols. Nothing else."
        delay 0.5
        key code 36 -- Enter
    end tell
end tell

return "Long message sent with delays!"