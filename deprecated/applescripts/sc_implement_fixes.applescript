-- /SC Implement로 각 Claude에게 문제 해결 지시

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

-- Main Platform: 보안 및 코드 품질 개선
sendToSession("Main Claude", "/SC Implement 다음 문제를 즉시 해결하세요: 1) 1,897개 console.log 제거 2) API 인증 미들웨어 추가 (Supabase Auth 활용) 3) Rate Limiting 구현 (@upstash/ratelimit) 4) 환경변수로 프로덕션/개발 분리 5) 완료 후 Issue #34 보고")

delay 2

-- KB System: 누락된 구현 완성
sendToSession("KB Claude", "/SC Implement KB System 완전 재구현: 1) src/ 디렉토리에 실제 API 구현 2) ChromaDB 벡터 스토어 구현 3) FAISS 또는 Annoy로 검색 최적화 4) CRUD API 완성 5) 테스트 코드 작성 6) 완료 후 Issue #34 보고")

delay 2

-- LLM Service: 의존성 및 성능 개선  
sendToSession("LLM Claude", "/SC Implement LLM Service 문제 해결: 1) pip install fastapi uvicorn pydantic redis 실행 2) 캐싱 전략 구현 (Redis 활용) 3) 서비스 간 통신 프로토콜 정의 4) 구조화된 에러 핸들링 5) API 문서 업데이트 6) 완료 후 Issue #34 보고")

display notification "SC Implement 명령 전송 완료!" with title "Orchestra"