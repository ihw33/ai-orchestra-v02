-- LLM Service 서버 시작 스크립트

on sendToSession(sessionName, command)
    tell application "iTerm"
        tell current window
            tell current tab
                repeat with s in sessions
                    if name of s contains sessionName then
                        tell s
                            select
                            delay 0.2
                            write text command newline no
                            delay 0.1
                            write text ""
                        end tell
                        return
                    end if
                end repeat
            end tell
        end tell
    end tell
end sendToSession

-- LLM Service 서버 시작
sendToSession("LLM Claude", "cd /Users/m4_macbook/Projects/ai-engine-hub")
delay 1
sendToSession("LLM Claude", "python main.py")

display notification "LLM Service 서버 시작!" with title "Orchestra"