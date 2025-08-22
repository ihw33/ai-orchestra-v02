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
        -- 매우 천천히 한 글자씩 전송
        set messageText to "Calculate 1+1 and show result as: @@ACK then @@RUN then @@EOT status=OK answer=2"
        
        repeat with char in messageText
            keystroke char as string
            delay 0.05 -- 각 글자마다 0.05초 대기
        end repeat
        
        delay 0.5
        key code 36 -- Enter
    end tell
end tell

return "Message sent slowly!"