-- 모든 세션에 Issue 보고 강제하기

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

-- Main Platform 보고 지시
sendToSession("Main Claude", "echo '⚠️ 중요: 모든 작업 완료 시 반드시 Issue #34에 보고하세요!'")
delay 1
sendToSession("Main Claude", "gh issue comment 34 -R ihw33/ai-orchestra-v02 --body '## Main Platform Phase 3 상태 보고' --body '- 현재 작업: [작업 내용]' --body '- 서버 상태: [포트 정보]' --body '- 완료 여부: [진행중/완료]'")

delay 2

-- KB System 보고 지시  
sendToSession("KB Claude", "echo '⚠️ 중요: 모든 작업 완료 시 반드시 Issue #34에 보고하세요!'")
delay 1
sendToSession("KB Claude", "gh issue comment 34 -R ihw33/ai-orchestra-v02 --body '## KB System Phase 3 상태 보고' --body '- 현재 작업: [작업 내용]' --body '- 서버 상태: [포트 정보]' --body '- 완료 여부: [진행중/완료]'")

delay 2

-- LLM Service 보고 지시
sendToSession("LLM Claude", "echo '⚠️ 중요: 서버 실행 상태를 Issue #34에 보고하세요!'")
delay 1
sendToSession("LLM Claude", "gh issue comment 34 -R ihw33/ai-orchestra-v02 --body '## LLM Service 서버 상태' --body '- 서버 포트: [실행 포트]' --body '- API 엔드포인트: [사용 가능한 엔드포인트]' --body '- 상태: [실행중/중지]'")

display notification "모든 세션에 보고 지시 완료!" with title "Orchestra"