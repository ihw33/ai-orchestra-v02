#!/usr/bin/env python3
"""
진짜 KPI 추적 시스템
실제 AI 통신과 GitHub 작업을 추적
"""

import json
import subprocess
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional
import sys
sys.path.append('/Users/m4_macbook/Projects/ai-orchestra-dashboard')

from smart_prompt_sender import SmartPromptSender

class RealKPITracker:
    """실제 작동하는 KPI 추적기"""
    
    def __init__(self):
        self.sender = SmartPromptSender()
        self.kpi_data = {
            "start_time": datetime.now().isoformat(),
            "communications": [],
            "github_actions": [],
            "errors": []
        }
        
    def send_task_to_ai(self, ai_name: str, tab_number: int, task: str) -> bool:
        """실제로 AI에게 작업 전송"""
        print(f"\n📤 {ai_name}(Tab {tab_number})에게 작업 전송 중...")
        
        # 시작 시간 기록
        start = time.time()
        
        # AppleScript로 메시지 전송
        script = f'''
        tell application "iTerm2"
            tell current window
                tell tab {tab_number}
                    select
                    tell current session
                        write text "{task}"
                    end tell
                end tell
            end tell
        end tell
        '''
        
        try:
            result = subprocess.run(
                ['osascript', '-e', script],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            success = result.returncode == 0
            elapsed = time.time() - start
            
            # KPI 기록
            self.kpi_data["communications"].append({
                "ai": ai_name,
                "tab": tab_number,
                "task": task[:100],
                "success": success,
                "response_time": elapsed,
                "timestamp": datetime.now().isoformat(),
                "error": result.stderr if not success else None
            })
            
            if success:
                print(f"✅ {ai_name}: 전송 성공 ({elapsed:.2f}초)")
            else:
                print(f"❌ {ai_name}: 전송 실패 - {result.stderr}")
                
            return success
            
        except subprocess.TimeoutExpired:
            self.kpi_data["errors"].append({
                "ai": ai_name,
                "type": "timeout",
                "timestamp": datetime.now().isoformat()
            })
            print(f"⏱️ {ai_name}: 타임아웃")
            return False
            
    def check_github_pr(self, pr_number: int) -> Dict:
        """실제 PR 상태 확인"""
        print(f"\n🔍 PR #{pr_number} 상태 확인 중...")
        
        cmd = f"gh pr view {pr_number} -R ihw33/ai-orchestra-dashboard --json state,mergeable,reviews"
        
        try:
            result = subprocess.run(
                cmd.split(),
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                pr_data = json.loads(result.stdout)
                
                self.kpi_data["github_actions"].append({
                    "type": "pr_check",
                    "pr_number": pr_number,
                    "state": pr_data.get("state"),
                    "mergeable": pr_data.get("mergeable"),
                    "reviews": len(pr_data.get("reviews", [])),
                    "timestamp": datetime.now().isoformat()
                })
                
                print(f"✅ PR 상태: {pr_data.get('state')}")
                return pr_data
            else:
                print(f"❌ PR 확인 실패")
                return {}
                
        except Exception as e:
            self.kpi_data["errors"].append({
                "type": "github_error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            })
            return {}
            
    def generate_real_report(self) -> Dict:
        """실제 데이터 기반 리포트"""
        runtime = (datetime.now() - datetime.fromisoformat(self.kpi_data["start_time"])).total_seconds()
        
        # 통신 통계
        total_comms = len(self.kpi_data["communications"])
        successful_comms = sum(1 for c in self.kpi_data["communications"] if c["success"])
        
        # AI별 통계
        ai_stats = {}
        for comm in self.kpi_data["communications"]:
            ai = comm["ai"]
            if ai not in ai_stats:
                ai_stats[ai] = {"total": 0, "success": 0, "total_time": 0}
            ai_stats[ai]["total"] += 1
            if comm["success"]:
                ai_stats[ai]["success"] += 1
                ai_stats[ai]["total_time"] += comm["response_time"]
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "runtime_seconds": runtime,
            "summary": {
                "total_communications": total_comms,
                "successful_communications": successful_comms,
                "success_rate": (successful_comms / total_comms * 100) if total_comms > 0 else 0,
                "github_actions": len(self.kpi_data["github_actions"]),
                "errors": len(self.kpi_data["errors"])
            },
            "ai_performance": ai_stats,
            "raw_data": self.kpi_data
        }
        
        return report
        
    def save_report(self, filepath: str = "real_kpi_report.json"):
        """리포트 저장"""
        report = self.generate_real_report()
        
        with open(filepath, 'w') as f:
            json.dump(report, f, indent=2)
            
        print(f"\n📊 리포트 저장: {filepath}")
        print(f"  • 총 통신: {report['summary']['total_communications']}")
        print(f"  • 성공률: {report['summary']['success_rate']:.1f}%")
        print(f"  • GitHub 작업: {report['summary']['github_actions']}")
        print(f"  • 에러: {report['summary']['errors']}")
        
        return filepath

# 실제 테스트
if __name__ == "__main__":
    tracker = RealKPITracker()
    
    # 실제 AI들에게 작업 전송
    tasks = [
        ("Gemini", 2, "echo 'Gemini가 작업을 시작합니다'"),
        ("Codex", 3, "echo 'Codex가 백엔드를 점검합니다'"),
        ("Tab 4 Claude", 4, "ls -la /Users/m4_macbook/Projects/ai-orchestra-dashboard/round5/")
    ]
    
    for ai_name, tab, task in tasks:
        tracker.send_task_to_ai(ai_name, tab, task)
        time.sleep(1)  # 과부하 방지
    
    # GitHub PR 확인
    tracker.check_github_pr(61)
    
    # 리포트 생성
    tracker.save_report("round5/real_kpi_report.json")