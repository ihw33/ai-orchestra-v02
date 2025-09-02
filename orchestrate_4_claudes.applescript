-- 4개 Claude 세션 동시 제어 스크립트
-- iTerm2에서 4분할된 세션에 각각 명령을 전송

on sendToSession(sessionName, command)
    tell application "iTerm"
        tell current window
            tell current tab
                -- 세션 이름으로 찾기
                repeat with s in sessions
                    if name of s contains sessionName then
                        tell s
                            -- 세션 선택
                            select
                            delay 0.2
                            -- 텍스트 입력 (엔터 없이)
                            write text command newline no
                            delay 0.1
                            -- 별도로 엔터 전송
                            write text ""
                        end tell
                        return
                    end if
                end repeat
            end tell
        end tell
    end tell
end sendToSession

-- Master Issue 번호 (필요시 변경)
set issueNumber to "34"

-- 각 세션에 명령 전송 (프로젝트 폴더 이동 포함)
sendToSession("Session Configuration", "cd /Users/m4_macbook/Projects/ai-orchestra-v02 && echo '🎯 PM Claude: Master Issue #" & issueNumber & " 관리 중...'")
sendToSession("Main Claude", "cd /Users/m4_macbook/Projects/iwl-v5-rebuild && claude -p 'Master Issue #" & issueNumber & " 확인하고 Main Platform 작업 진행'")
sendToSession("KB Claude", "cd /Users/m4_macbook/Projects/iwl-kb-system && claude -p 'Master Issue #" & issueNumber & " 확인하고 Knowledge Base 작업 진행'")
sendToSession("LLM Claude", "cd /Users/m4_macbook/Projects/ai-engine-hub && claude -p 'Master Issue #" & issueNumber & " 확인하고 LLM Service 작업 진행'")

-- 완료 메시지
display notification "4개 Claude 세션에 작업 지시 완료!" with title "Orchestra"