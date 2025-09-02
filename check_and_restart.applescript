-- 작업 상태 확인 및 재시작 스크립트

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

-- 각 세션 상태 확인 및 재시작
sendToSession("Session Configuration", "echo '🔍 PM: 작업 상태 확인 중...'")

-- Main Claude 재시작
sendToSession("Main Claude", "echo '⚠️ Main Platform Phase 2 재시작' && cd /Users/m4_macbook/Projects/iwl-v5-rebuild && claude -p 'Phase 2 작업 재개: npm install 실행, .env.local 설정, 개발 서버 실행 후 Issue #34에 보고'")

-- KB Claude 재시작  
sendToSession("KB Claude", "echo '⚠️ KB System Phase 2 재시작' && cd /Users/m4_macbook/Projects/iwl-kb-system && claude -p 'Phase 2 작업 재개: Python venv 설정, FastAPI 서버 실행, CRUD API 구현 후 Issue #34에 보고'")

-- LLM Claude 시작 (처음부터)
sendToSession("LLM Claude", "echo '🚀 LLM Service 작업 시작' && cd /Users/m4_macbook/Projects/ai-engine-hub && claude -p 'LLM Service 초기 구축: 프로젝트 구조 생성, API 래퍼 설계, Issue #34에 진행 상황 보고'")

display notification "모든 Claude 재시작 완료!" with title "Orchestra"