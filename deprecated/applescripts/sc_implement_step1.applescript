-- 단계별 명확한 지시 (Step 1: 긴급 수정만)

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

-- Main Platform: console.log만 제거
sendToSession("Main Claude", "/SC Implement console.log를 모두 제거하고 환경변수 NODE_ENV에 따라 로그 출력 제어하기")

delay 2

-- KB System: 최소 API만 구현
sendToSession("KB Claude", "/SC Implement src/api/main.py 파일 생성하고 FastAPI로 기본 CRUD 엔드포인트 4개만 구현 (GET, POST, PUT, DELETE)")

delay 2

-- LLM Service: 의존성만 설치
sendToSession("LLM Claude", "/SC Implement cd /Users/m4_macbook/Projects/ai-engine-hub && pip install fastapi uvicorn && python main.py 실행")

display notification "Step 1: 긴급 수정 지시 완료" with title "Orchestra"