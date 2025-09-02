#!/usr/bin/osascript

tell application "iTerm"
    tell current window
        tell current session
            -- 한 번에 전체 메시지 전송
            write text "다음 3줄을 정확히 출력해주세요:
@@ACK id=ISSUE-TEST-1
@@RUN id=ISSUE-TEST-1  
@@EOT id=ISSUE-TEST-1 status=OK answer=2"
        end tell
    end tell
end tell