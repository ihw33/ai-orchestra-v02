#!/usr/bin/osascript
(*
    Project Tycoon iTerm2 게임 세션 설정
    4개 패널로 분할하여 게임 대시보드 구성
*)

on run
    tell application "iTerm2"
        activate
        
        -- 새 윈도우 생성
        create window with default profile
        tell current window
            
            -- 1. 메인 대시보드 (왼쪽 상단)
            tell current session
                write text "cd /Users/m4_macbook/Projects/ai-orchestra-v02"
                write text "echo '🎮 PROJECT TYCOON - Main Dashboard'"
                write text "python project_tycoon.py"
                set name to "🎮 Tycoon"
            end tell
            
            -- 2. 실시간 로그 (오른쪽 상단)
            tell current tab
                set newSession to (split vertically with default profile)
                tell newSession
                    write text "cd /Users/m4_macbook/Projects/ai-orchestra-v02"
                    write text "echo '📊 REAL-TIME ACTIVITY FEED'"
                    write text "tail -f monitor_log.md"
                    set name to "📊 Activity"
                end tell
            end tell
            
            -- 3. PM 의사결정 큐 (왼쪽 하단)
            tell current tab
                tell session 1
                    set bottomLeft to (split horizontally with default profile)
                    tell bottomLeft
                        write text "cd /Users/m4_macbook/Projects/ai-orchestra-v02"
                        write text "echo '💬 PM DECISION QUEUE'"
                        write text "python review_session.py --mode accept"
                        set name to "💬 Decisions"
                    end tell
                end tell
            end tell
            
            -- 4. 팀 모니터링 (오른쪽 하단)
            tell current tab
                tell session 2
                    set bottomRight to (split horizontally with default profile)
                    tell bottomRight
                        write text "cd /Users/m4_macbook/Projects/ai-orchestra-v02"
                        write text "echo '👥 TEAM MONITORING'"
                        write text "watch -n 5 'gh issue list -R ihw33/ai-orchestra-v02 --state open --limit 10'"
                        set name to "👥 Teams"
                    end tell
                end tell
            end tell
            
        end tell
    end tell
    
    display notification "Project Tycoon 게임 환경이 준비되었습니다!" with title "🎮 Ready to Play"
    
end run