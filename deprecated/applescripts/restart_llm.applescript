-- LLM Service Claude 재시작 스크립트

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

-- LLM Claude 강제 재시작
sendToSession("LLM Claude", "echo '🚨 LLM Service 긴급 시작!'")
delay 1
sendToSession("LLM Claude", "cd /Users/m4_macbook/Projects/ai-engine-hub")
delay 1
sendToSession("LLM Claude", "claude -p 'LLM Service 구축 시작: 1) 프로젝트 구조 생성 (src/, api/, models/ 폴더) 2) requirements.txt 생성 (openai, anthropic, google-generativeai) 3) main.py로 FastAPI 서버 구현 4) 3개 LLM API 래퍼 구현 5) Issue #34에 완료 보고 필수!'")

display notification "LLM Service Claude 재시작!" with title "Orchestra"