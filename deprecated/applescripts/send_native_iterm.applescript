#!/usr/bin/osascript

tell application "iTerm"
    tell current window
        tell current tab
            tell session 2
                -- iTerm의 네이티브 write text 명령 사용
                write text "Please output: @@ACK id=T1 and @@RUN id=T1 and @@EOT id=T1 status=OK answer=2"
            end tell
        end tell
    end tell
end tell

return "Native iTerm command sent!"