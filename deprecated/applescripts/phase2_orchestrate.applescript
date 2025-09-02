-- Phase 2: 통합 및 연결 작업 지시
-- 각 Claude에게 다음 단계 작업 전달

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

-- Phase 2 작업 지시
sendToSession("Session Configuration", "echo '🎯 Phase 2: 통합 작업 시작'")
sendToSession("Main Claude", "cd /Users/m4_macbook/Projects/iwl-v5-rebuild && claude -p 'npm install 실행하고 .env.local 설정 후 개발 서버 실행. Supabase 연결 테스트까지 완료해줘'")
sendToSession("KB Claude", "cd /Users/m4_macbook/Projects/iwl-kb-system && claude -p 'Python venv 설정하고 FastAPI 서버 실행. 기본 CRUD API 엔드포인트 구현해줘'")
sendToSession("LLM Claude", "cd /Users/m4_macbook/Projects/ai-engine-hub && claude -p 'LLM 통합 API 구조 설계. OpenAI, Claude, Gemini API 래퍼 구현 시작'")

display notification "Phase 2 작업 지시 완료!" with title "Orchestra"