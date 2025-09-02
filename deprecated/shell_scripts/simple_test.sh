#!/bin/bash

# 간단한 테스트 - Session 2에 직접 명령 전송

echo "🔍 iTerm2 Session 2에 테스트 메시지 전송"

# 1. 짧은 메시지 테스트
osascript <<EOF
tell application "iTerm"
    tell current window
        tell current tab
            tell session 2
                write text "TEST1"
            end tell
        end tell
    end tell
end tell
EOF

sleep 2

# 2. 3줄 형식 테스트 (짧게)
osascript <<EOF
tell application "iTerm"
    tell current window
        tell current tab
            tell session 2
                write text "@@ACK TEST"
            end tell
        end tell
    end tell
end tell
EOF

sleep 1

osascript <<EOF
tell application "iTerm"
    tell current window
        tell current tab
            tell session 2
                write text "@@RUN TEST"
            end tell
        end tell
    end tell
end tell
EOF

sleep 1

osascript <<EOF
tell application "iTerm"
    tell current window
        tell current tab
            tell session 2
                write text "@@EOT TEST OK"
            end tell
        end tell
    end tell
end tell
EOF

echo "✅ 테스트 메시지 전송 완료"
echo "Gemini 세션을 확인하세요"