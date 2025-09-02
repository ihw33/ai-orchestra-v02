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

-- 약간의 지연 후 System Events로 키 입력
delay 0.5

tell application "System Events"
    tell process "iTerm2"
        -- 텍스트를 타이핑
        keystroke "다음 3줄을 정확히 출력해주세요:"
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

return "Keystrokes sent to Gemini session!"