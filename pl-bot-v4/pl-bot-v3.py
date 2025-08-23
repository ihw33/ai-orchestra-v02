#!/usr/bin/env python3
"""
PL Bot v3.0 - Progress Leader Bot with KPI Tracking
원래 역할 유지 + 작업 추적 + 프로세스 리마인드
"""
import subprocess
import time
import json
from datetime import datetime, timedelta
from pathlib import Path
import sys
sys.path.append('/Users/m4_macbook/Projects/ai-orchestra-dashboard')
from smart_prompt_sender import SmartPromptSender

class PLBotV3:
    def __init__(self):
        # 원래 기능 유지
        self.team = {
            "Gemini": {"status": "active", "last_response": None, "task": None, "last_reminder": None},
            "Codex": {"status": "active", "last_response": None, "task": None, "last_reminder": None},
            "Cursor": {"status": "active", "last_response": None, "task": None, "last_reminder": None},
            "Claude": {"status": "active", "last_response": None, "task": None, "last_reminder": None}
        }
        
        # 새 기능: 작업 추적
        self.active_tasks = {}
        self.process_violations = []
        self.kpi_metrics = {
            "tasks_assigned": 0,
            "tasks_completed": 0,
            "communications_sent": 0,
            "communications_success": 0,
            "reminders_sent": 0
        }
        
        # 프로세스 체크리스트
        self.process_checklist = {
            "branch_created": False,
            "commits_made": False,
            "pr_created": False,
            "review_requested": False,
            "tests_passed": False
        }
        
        self.sender = SmartPromptSender()
        
    def check_ai_response(self, ai_name):
        """기존 AI 응답 체크 - Allow 요청 감지"""
        try:
            if ai_name == "Gemini":
                result = subprocess.run(
                    ["gemini", "--version"], 
                    capture_output=True, 
                    text=True, 
                    timeout=5
                )
            elif ai_name == "Codex":
                result = subprocess.run(
                    ["codex", "--version"], 
                    capture_output=True, 
                    text=True, 
                    timeout=5
                )
            elif ai_name == "Claude":
                return "active"
            elif ai_name == "Cursor":
                result = subprocess.run(
                    ["ps", "aux"], 
                    capture_output=True, 
                    text=True
                )
                return "active" if "Cursor" in result.stdout else "inactive"
                
            return "active"
        except subprocess.TimeoutExpired:
            return "timeout"
        except Exception:
            return "inactive"
            
    def track_task(self, ai_name: str, task: str):
        """새 작업 추적"""
        self.active_tasks[ai_name] = {
            "task": task,
            "assigned_at": datetime.now().isoformat(),
            "status": "in_progress"
        }
        self.kpi_metrics["tasks_assigned"] += 1
        self.team[ai_name]["task"] = task
        
    def send_reminder(self, ai_name: str, message: str):
        """프로세스 리마인드"""
        now = datetime.now()
        last_reminder = self.team[ai_name].get("last_reminder")
        
        # 5분에 한번만 리마인드
        if last_reminder and (now - datetime.fromisoformat(last_reminder)).seconds < 300:
            return
            
        print(f"\n🔔 리마인드 → {ai_name}: {message}")
        
        # AppleScript로 실제 리마인드
        tab_map = {"Gemini": 2, "Codex": 3, "Claude": 4, "Cursor": 5}
        if ai_name in tab_map:
            script = f'''
            tell application "iTerm2"
                tell current window
                    tell tab {tab_map[ai_name]}
                        select
                        tell current session
                            write text "# 리마인드: {message}"
                        end tell
                    end tell
                end tell
            end tell
            '''
            subprocess.run(['osascript', '-e', script])
            
        self.team[ai_name]["last_reminder"] = now.isoformat()
        self.kpi_metrics["reminders_sent"] += 1
        
    def check_process_compliance(self):
        """프로세스 준수 체크"""
        violations = []
        
        # GitHub 체크
        try:
            # 현재 브랜치 확인
            result = subprocess.run(
                ["git", "branch", "--show-current"],
                capture_output=True,
                text=True
            )
            current_branch = result.stdout.strip()
            
            if current_branch == "main" or current_branch == "master":
                violations.append("⚠️ 작업이 main 브랜치에서 진행 중")
                self.process_checklist["branch_created"] = False
            else:
                self.process_checklist["branch_created"] = True
                
            # 커밋 확인
            result = subprocess.run(
                ["git", "log", "--oneline", "-1"],
                capture_output=True,
                text=True
            )
            if "🤖" in result.stdout:
                self.process_checklist["commits_made"] = True
                
        except Exception as e:
            violations.append(f"Git 체크 실패: {e}")
            
        # 누군가 작업 중인데 PR이 없으면
        if self.active_tasks and not self.process_checklist["pr_created"]:
            violations.append("📝 활성 작업이 있지만 PR이 생성되지 않음")
            
        return violations
        
    def generate_kpi_report(self):
        """KPI 리포트 생성"""
        runtime = datetime.now()
        
        # 성공률 계산
        comm_success_rate = 0
        if self.kpi_metrics["communications_sent"] > 0:
            comm_success_rate = (
                self.kpi_metrics["communications_success"] / 
                self.kpi_metrics["communications_sent"] * 100
            )
            
        task_completion_rate = 0
        if self.kpi_metrics["tasks_assigned"] > 0:
            task_completion_rate = (
                self.kpi_metrics["tasks_completed"] / 
                self.kpi_metrics["tasks_assigned"] * 100
            )
            
        report = {
            "timestamp": runtime.isoformat(),
            "team_status": self.team,
            "active_tasks": self.active_tasks,
            "kpi_summary": {
                "tasks_assigned": self.kpi_metrics["tasks_assigned"],
                "tasks_completed": self.kpi_metrics["tasks_completed"],
                "task_completion_rate": task_completion_rate,
                "communication_success_rate": comm_success_rate,
                "reminders_sent": self.kpi_metrics["reminders_sent"],
                "process_violations": len(self.process_violations)
            },
            "process_checklist": self.process_checklist,
            "violations": self.process_violations[-5:]  # 최근 5개
        }
        
        # 파일로 저장
        with open("pl-bot-kpi-report.json", "w") as f:
            json.dump(report, f, indent=2)
            
        return report
        
    def monitor_once(self):
        """한 번 모니터링 실행"""
        print("\n" + "="*50)
        print(f"🤖 PL Bot v3.0 모니터링 - {datetime.now().strftime('%H:%M:%S')}")
        print("="*50)
        
        # 1. AI 상태 체크 (원래 기능)
        for ai_name in self.team:
            status = self.check_ai_response(ai_name)
            self.team[ai_name]["status"] = status
            self.team[ai_name]["last_response"] = str(datetime.now())
            
            if status == "active":
                print(f"✅ {ai_name}: 정상 작동", end="")
                if self.team[ai_name]["task"]:
                    print(f" - 작업 중: {self.team[ai_name]['task'][:30]}...")
                else:
                    print()
            elif status == "timeout":
                print(f"⏱️ {ai_name}: 타임아웃")
                self.send_reminder(ai_name, "응답이 없습니다. 상태를 확인해주세요.")
            else:
                print(f"❌ {ai_name}: 비활성")
                
        # 2. 프로세스 체크 (새 기능)
        violations = self.check_process_compliance()
        if violations:
            print("\n⚠️ 프로세스 위반 감지:")
            for v in violations:
                print(f"  {v}")
                self.process_violations.append({
                    "time": datetime.now().isoformat(),
                    "violation": v
                })
                
        # 3. 작업 리마인드
        for ai_name, task_info in self.active_tasks.items():
            if task_info["status"] == "in_progress":
                # 30분 이상 진행 중이면 리마인드
                assigned_time = datetime.fromisoformat(task_info["assigned_at"])
                if (datetime.now() - assigned_time).seconds > 1800:
                    self.send_reminder(
                        ai_name, 
                        f"작업 진행 상황을 업데이트해주세요: {task_info['task'][:30]}"
                    )
                    
        # 4. KPI 리포트 생성
        self.generate_kpi_report()
        
        # 5. 요약 출력
        print(f"\n📊 KPI 요약:")
        print(f"  • 할당된 작업: {self.kpi_metrics['tasks_assigned']}")
        print(f"  • 완료된 작업: {self.kpi_metrics['tasks_completed']}")
        print(f"  • 리마인드 전송: {self.kpi_metrics['reminders_sent']}")
        print(f"  • 프로세스 위반: {len(self.process_violations)}")
        
    def run(self):
        """메인 실행 루프"""
        print("🚀 PL Bot v3.0 시작")
        print("   - 원래 기능: Allow 감지, 타임아웃 체크")
        print("   - 새 기능: 작업 추적, 프로세스 리마인드, KPI 측정")
        print("   - 30초마다 체크\n")
        
        while True:
            try:
                self.monitor_once()
                time.sleep(30)
            except KeyboardInterrupt:
                print("\n👋 PL Bot 종료")
                break
            except Exception as e:
                print(f"❌ 에러 발생: {e}")
                time.sleep(5)

if __name__ == "__main__":
    bot = PLBotV3()
    
    # 테스트: 작업 할당
    bot.track_task("Gemini", "Frontend 컴포넌트 개발")
    bot.track_task("Codex", "API 엔드포인트 구현")
    bot.track_task("Claude", "KPI 시스템 개선")
    
    bot.run()