"""
지시 전 확인 노드 - Claude 세션에 명령 전송 전 상태 확인 및 사용자 승인
"""
import subprocess
import time
from typing import Dict, List, Optional
from datetime import datetime

class CheckBeforeInstructionNode:
    def __init__(self):
        self.sessions = ["Main Claude", "KB Claude", "LLM Claude"]
        
    def check_session_activity(self) -> Dict:
        """각 세션의 현재 활동 상태 확인"""
        activity_status = {}
        
        for session in self.sessions:
            # 각 프로젝트의 최근 파일 변경 확인
            if "Main" in session:
                path = "/Users/m4_macbook/Projects/iwl-v5-rebuild"
                recent_change = self._check_recent_changes(path)
                activity_status["Main Platform"] = recent_change
            elif "KB" in session:
                path = "/Users/m4_macbook/Projects/iwl-kb-system"
                recent_change = self._check_recent_changes(path)
                activity_status["KB System"] = recent_change
            elif "LLM" in session:
                path = "/Users/m4_macbook/Projects/ai-engine-hub"
                recent_change = self._check_recent_changes(path)
                activity_status["LLM Service"] = recent_change
                
        return activity_status
    
    def _check_recent_changes(self, path: str) -> Dict:
        """최근 5분 이내 파일 변경 확인"""
        try:
            # 최근 5분 이내 변경된 파일 찾기
            cmd = f"find {path} -type f -mmin -5 2>/dev/null | head -5"
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            
            recent_files = result.stdout.strip().split('\n') if result.stdout else []
            
            if recent_files and recent_files[0]:
                return {
                    "status": "ACTIVE",
                    "recent_files": recent_files[:3],
                    "message": "작업 중 - 파일 수정 감지"
                }
            else:
                return {
                    "status": "IDLE",
                    "message": "대기 중 - 최근 활동 없음"
                }
        except Exception as e:
            return {
                "status": "UNKNOWN",
                "error": str(e)
            }
    
    def prepare_instruction_request(self, planned_instructions: Dict) -> Dict:
        """사용자에게 지시 승인 요청 준비"""
        activity = self.check_session_activity()
        
        request = {
            "timestamp": datetime.now().isoformat(),
            "current_activity": activity,
            "planned_instructions": planned_instructions,
            "recommendation": self._generate_recommendation(activity)
        }
        
        return request
    
    def _generate_recommendation(self, activity: Dict) -> str:
        """활동 상태에 따른 권고사항 생성"""
        active_count = sum(1 for v in activity.values() if v.get("status") == "ACTIVE")
        
        if active_count >= 2:
            return "⚠️ 여러 세션이 작업 중입니다. 완료 대기 권장"
        elif active_count == 1:
            return "💡 1개 세션이 작업 중. 다른 세션에만 지시 가능"
        else:
            return "✅ 모든 세션이 대기 중. 새 지시 가능"
    
    def execute(self, context: Dict = None) -> Dict:
        """노드 실행"""
        # 1. 현재 상태 확인
        activity_status = self.check_session_activity()
        
        # 2. 계획된 지시사항 확인
        planned = context.get("planned_instructions", {}) if context else {}
        
        # 3. 승인 요청 준비
        request = self.prepare_instruction_request(planned)
        
        # 4. 사용자 확인 필요 플래그
        needs_confirmation = any(
            v.get("status") == "ACTIVE" 
            for v in activity_status.values()
        )
        
        return {
            "activity_check": activity_status,
            "approval_request": request,
            "needs_user_confirmation": needs_confirmation,
            "timestamp": datetime.now().isoformat()
        }

# 프로세스 통합을 위한 함수
def check_before_any_instruction() -> bool:
    """지시 전 확인 프로세스"""
    node = CheckBeforeInstructionNode()
    result = node.execute()
    
    if result["needs_user_confirmation"]:
        print("\n⚠️ 확인 필요:")
        for service, status in result["activity_check"].items():
            print(f"  - {service}: {status['message']}")
        print("\n지시를 진행하시겠습니까? (y/n)")
        # 실제로는 사용자 입력 대기
        return False
    
    return True