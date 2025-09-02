-- 4개 Claude 오케스트레이션 (간결한 버전)

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

-- 간결한 지시사항 전송
sendToSession("Main Claude", "# Main Platform: RAG UI 구현 후 '✅ Main 완료 | localhost:3000' 보고")
delay 0.5
sendToSession("KB Claude", "# KB System: Vector API 구현 후 '✅ KB 완료 | localhost:8002' 보고")
delay 0.5
sendToSession("LLM Claude", "# LLM Service: 통합 API 구현 후 '✅ LLM 완료 | localhost:8003' 보고")

display notification "간결한 지시 전달 완료" with title "Orchestra"