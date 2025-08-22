#!/usr/bin/osascript

-- 메시지를 클립보드에 복사
set messageText to "Please output exactly these 3 lines:
@@ACK id=ISSUE-TEST-1
@@RUN id=ISSUE-TEST-1
@@EOT id=ISSUE-TEST-1 status=OK answer=2"

set the clipboard to messageText

-- iTerm 활성화 및 Session 2 선택
tell application "iTerm"
    activate
    tell current window
        tell current tab
            select session 2
        end tell
    end tell
end tell

delay 0.5

-- 붙여넣기 (Cmd+V)
tell application "System Events"
    tell process "iTerm2"
        keystroke "v" using command down
        delay 0.5
        key code 36 -- Enter
    end tell
end tell

return "Message pasted to Gemini session!"