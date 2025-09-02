-- P0 긴급 이슈 해결 지시

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

-- KB System: 데이터 영속성 긴급 수정
sendToSession("KB Claude", "/SC Implement P0 긴급 수정: 1) PostgreSQL 또는 Redis로 데이터 저장소 변경 2) src/database.py 생성 - SQLAlchemy 또는 Redis 클라이언트 설정 3) main.py의 documents = {} 제거하고 DB 연동 4) 완료 후 Issue #34 보고")

delay 2

-- Main Platform: JWT 인증 추가
sendToSession("Main Claude", "/SC Implement P0 보안 수정: 1) lib/auth/jwt.ts 생성 - JWT 검증 미들웨어 2) app/api/kb/* 모든 엔드포인트에 인증 적용 3) 환경변수에 JWT_SECRET 추가 4) 완료 후 Issue #34 보고")

delay 2

-- LLM Service: API 키 검증 추가
sendToSession("LLM Claude", "/SC Implement P0 보안 수정: 1) API 키 검증 미들웨어 추가 2) 모든 엔드포인트에 Bearer 토큰 필수화 3) 환경변수로 API_KEY 관리 4) 완료 후 Issue #34 보고")

display notification "P0 긴급 수정 지시 완료!" with title "Orchestra"