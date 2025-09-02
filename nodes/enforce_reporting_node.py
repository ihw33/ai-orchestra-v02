"""
보고 강제 노드 - 각 Claude 세션에 Issue 보고를 강제하는 노드
"""
import subprocess
import json
import time
from typing import Dict, List, Optional
from datetime import datetime

class EnforceReportingNode:
    def __init__(self, issue_number: str = "34", repo: str = "ihw33/ai-orchestra-v02"):
        self.issue_number = issue_number
        self.repo = repo
        self.sessions = {
            "Main Claude": "Main Platform",
            "KB Claude": "KB System", 
            "LLM Claude": "LLM Service"
        }
        
    def send_to_session(self, session_name: str, command: str) -> bool:
        """AppleScript로 특정 세션에 명령 전송"""
        applescript = f'''
        tell application "iTerm"
            tell current window
                tell current tab
                    repeat with s in sessions
                        if name of s contains "{session_name}" then
                            tell s
                                select
                                delay 0.2
                                write text "{command}" newline no
                                delay 0.1
                                write text ""
                            end tell
                            return true
                        end if
                    end repeat
                end tell
            end tell
        end tell
        return false
        '''
        
        try:
            result = subprocess.run(
                ['osascript', '-e', applescript],
                capture_output=True,
                text=True,
                timeout=10
            )
            return result.returncode == 0
        except Exception as e:
            print(f"Error sending to {session_name}: {e}")
            return False
    
    def enforce_reporting(self, phase: str = "Phase 3") -> Dict:
        """모든 세션에 보고 가이드 제공 (부드럽게)"""
        results = {}
        timestamp = datetime.now().isoformat()
        
        for session_name, service_name in self.sessions.items():
            # 친절한 안내 메시지
            guide_cmd = f"echo '💡 {service_name} - 작업 완료 시 Issue #{self.issue_number}에 상태를 공유해주세요'"
            self.send_to_session(session_name, guide_cmd)
            time.sleep(0.5)
            
            # 보고 템플릿은 필요할 때만 제공 (옵션)
            # report_template = self.generate_report_template(service_name, phase)
            # self.send_to_session(session_name, report_template)
            # time.sleep(1)
            
            results[service_name] = {
                "enforced_at": timestamp,
                "session": session_name,
                "phase": phase
            }
        
        return {
            "status": "enforced",
            "timestamp": timestamp,
            "sessions_notified": len(results),
            "details": results
        }
    
    def generate_report_template(self, service_name: str, phase: str) -> str:
        """간결한 보고 템플릿 생성 (최소 정보만)"""
        # 짧고 간결한 보고 형식
        template = f'''gh issue comment {self.issue_number} -R {self.repo} --body "✅ {service_name} {phase} 완료 | 포트: [PORT] | 상태: 실행중"'''
        
        return f"echo '# 간단 보고 예시: {template}'"
    
    def check_compliance(self) -> Dict:
        """보고 준수 여부 확인"""
        try:
            # Issue 코멘트 확인
            cmd = f"gh issue view {self.issue_number} -R {self.repo} --json comments -q '.comments[-5:] | length'"
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            
            recent_comments = int(result.stdout.strip()) if result.stdout.strip() else 0
            
            return {
                "recent_comments_count": recent_comments,
                "compliance": recent_comments >= 3,  # 최소 3개 서비스가 보고해야 함
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {
                "error": str(e),
                "compliance": False,
                "timestamp": datetime.now().isoformat()
            }
    
    def execute(self, context: Dict = None) -> Dict:
        """노드 실행"""
        phase = context.get("phase", "Phase 3") if context else "Phase 3"
        
        # 1. 보고 강제
        enforcement_result = self.enforce_reporting(phase)
        
        # 2. 10초 대기
        time.sleep(10)
        
        # 3. 준수 여부 확인
        compliance_result = self.check_compliance()
        
        return {
            "enforcement": enforcement_result,
            "compliance": compliance_result,
            "success": compliance_result.get("compliance", False)
        }

# 단독 실행 시
if __name__ == "__main__":
    node = EnforceReportingNode()
    result = node.execute({"phase": "Phase 3"})
    print(json.dumps(result, indent=2))