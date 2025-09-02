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
        -- 간단한 계산 요청
        keystroke "Calculate 1+1 and output the result in this exact format:"
        delay 0.3
        key code 36
        delay 0.3
        
        keystroke "@@ACK id=CALC-1"
        delay 0.3
        key code 36
        delay 0.3
        
        keystroke "@@RUN id=CALC-1"
        delay 0.3
        key code 36
        delay 0.3
        
        keystroke "@@EOT id=CALC-1 status=OK answer=[your calculation result here]"
        delay 0.3
        key code 36
        delay 0.3
        
        keystroke "Replace [your calculation result here] with the actual answer to 1+1"
        delay 0.3
        key code 36
    end tell
end tell

return "Calculation request sent!"