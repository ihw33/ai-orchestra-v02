-- LLM Service에게 올바른 저장소로 보고하도록 지시

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

-- LLM Service에게 올바른 저장소로 보고 지시
sendToSession("LLM Claude", "echo '📌 중요: Issue #34는 ai-orchestra-v02 저장소에 있습니다!'")
delay 1
sendToSession("LLM Claude", "gh issue comment 34 -R ihw33/ai-orchestra-v02 --body '## LLM Service 완료 보고' --body '✅ Redis 캐싱 구현 완료' --body '✅ 서버 실행 중: localhost:8888' --body '✅ API 문서: http://localhost:8888/docs'")

display notification "LLM 보고 경로 수정" with title "Orchestra"