#!/usr/bin/env python3
"""
🤖 Auto Trigger System - 이벤트 기반 자동 워크플로우 실행
Thomas가 아무것도 안 해도 시스템이 알아서!
"""

import json
import time
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List

class AutoTrigger:
    """이벤트 기반 자동 트리거"""
    
    def __init__(self):
        self.base_dir = Path(__file__).parent
        self.config_file = self.base_dir / "triggers.json"
        self.log_file = self.base_dir / "trigger_log.json"
        self.workflow_cli = self.base_dir / "workflow_cli.py"
        
        # 트리거 설정 로드
        self.triggers = self.load_triggers()
        self.last_run = self.load_last_run()
        
    def load_triggers(self) -> Dict:
        """트리거 설정 로드"""
        if self.config_file.exists():
            with open(self.config_file, 'r') as f:
                return json.load(f)
        
        # 기본 트리거 설정
        default_triggers = {
            "time_based": [
                {
                    "name": "morning_routine",
                    "schedule": "09:00",
                    "workflow": "morning_routine",
                    "enabled": True
                },
                {
                    "name": "daily_report",
                    "schedule": "23:30",
                    "workflow": "send_report",
                    "enabled": True
                },
                {
                    "name": "friday_deploy",
                    "schedule": "friday 17:00",
                    "workflow": "deploy",
                    "enabled": False  # 금요일 배포는 위험!
                }
            ],
            "event_based": [
                {
                    "name": "bug_hotfix",
                    "event": "issue_labeled:bug",
                    "workflow": "hotfix",
                    "enabled": True
                },
                {
                    "name": "pr_merged",
                    "event": "pr_merged:main",
                    "workflow": "deploy",
                    "enabled": True
                }
            ],
            "condition_based": [
                {
                    "name": "low_coverage",
                    "condition": "test_coverage < 80",
                    "workflow": "add_tests",
                    "enabled": True
                },
                {
                    "name": "high_error_rate",
                    "condition": "error_rate > 5",
                    "workflow": "emergency_rollback",
                    "enabled": True
                }
            ]
        }
        
        # 기본 설정 저장
        with open(self.config_file, 'w') as f:
            json.dump(default_triggers, f, indent=2)
        
        return default_triggers
    
    def load_last_run(self) -> Dict:
        """마지막 실행 기록 로드"""
        if self.log_file.exists():
            with open(self.log_file, 'r') as f:
                return json.load(f)
        return {}
    
    def save_last_run(self, trigger_name: str):
        """실행 기록 저장"""
        self.last_run[trigger_name] = datetime.now().isoformat()
        with open(self.log_file, 'w') as f:
            json.dump(self.last_run, f, indent=2)
    
    def check_time_triggers(self):
        """시간 기반 트리거 체크"""
        now = datetime.now()
        current_time = now.strftime("%H:%M")
        current_day = now.strftime("%A").lower()
        
        for trigger in self.triggers.get("time_based", []):
            if not trigger["enabled"]:
                continue
                
            schedule = trigger["schedule"]
            
            # 특정 요일 체크
            if " " in schedule:
                day, time_str = schedule.split(" ")
                if day.lower() != current_day:
                    continue
                schedule = time_str
            
            # 시간 체크
            if schedule == current_time:
                # 오늘 이미 실행했는지 체크
                last_run_str = self.last_run.get(trigger["name"])
                if last_run_str:
                    last_run = datetime.fromisoformat(last_run_str)
                    if last_run.date() == now.date():
                        continue
                
                # 워크플로우 실행
                self.execute_workflow(trigger["name"], trigger["workflow"])
    
    def check_github_events(self):
        """GitHub 이벤트 체크"""
        # GitHub API를 통해 최근 이벤트 체크
        try:
            # 최근 이슈 체크
            cmd = "gh issue list -R ihw33/ai-orchestra-v02 --label bug --state open --json number,createdAt --limit 1"
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            
            if result.returncode == 0 and result.stdout:
                issues = json.loads(result.stdout)
                for issue in issues:
                    # 최근 5분 이내 생성된 버그 이슈
                    created = datetime.fromisoformat(issue['createdAt'].replace('Z', '+00:00'))
                    if (datetime.now(created.tzinfo) - created).seconds < 300:
                        self.execute_workflow("bug_hotfix", "hotfix")
        except:
            pass
    
    def check_conditions(self):
        """조건 기반 트리거 체크"""
        # 테스트 커버리지 체크 (시뮬레이션)
        test_coverage = self.get_test_coverage()
        if test_coverage < 80:
            for trigger in self.triggers.get("condition_based", []):
                if trigger["name"] == "low_coverage" and trigger["enabled"]:
                    self.execute_workflow(trigger["name"], trigger["workflow"])
    
    def get_test_coverage(self) -> float:
        """테스트 커버리지 가져오기 (시뮬레이션)"""
        # 실제로는 pytest-cov 등을 사용
        return 85.0  # 시뮬레이션 값
    
    def execute_workflow(self, trigger_name: str, workflow_name: str):
        """워크플로우 실행"""
        print(f"\n🤖 Auto Trigger: {trigger_name}")
        print(f"   → Executing: {workflow_name}")
        
        # workflow_cli.py 실행
        cmd = f"python3 {self.workflow_cli} {workflow_name}"
        subprocess.run(cmd, shell=True)
        
        # 실행 기록
        self.save_last_run(trigger_name)
        
        # 알림
        self.notify(f"✅ Auto executed: {workflow_name} (triggered by {trigger_name})")
    
    def notify(self, message: str):
        """알림 전송"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {message}")
        
        # 로그 파일에도 기록
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "message": message
        }
        
        log_file = self.base_dir / "trigger_notifications.log"
        with open(log_file, 'a') as f:
            f.write(json.dumps(log_entry) + "\n")
    
    def run_daemon(self):
        """백그라운드 데몬 모드"""
        print("🤖 Auto Trigger Daemon Started")
        print("=" * 40)
        print("Monitoring:")
        print("  • Time-based triggers")
        print("  • GitHub events")
        print("  • System conditions")
        print("\nPress Ctrl+C to stop")
        print("=" * 40)
        
        while True:
            try:
                # 매분마다 체크
                self.check_time_triggers()
                self.check_github_events()
                self.check_conditions()
                
                # 1분 대기
                time.sleep(60)
                
            except KeyboardInterrupt:
                print("\n👋 Auto Trigger stopped")
                break
    
    def status(self):
        """트리거 상태 표시"""
        print("\n📊 Auto Trigger Status")
        print("=" * 40)
        
        print("\n⏰ Time-based Triggers:")
        for trigger in self.triggers.get("time_based", []):
            status = "✅" if trigger["enabled"] else "❌"
            last = self.last_run.get(trigger["name"], "Never")
            print(f"  {status} {trigger['name']:20} - {trigger['schedule']:15} (Last: {last})")
        
        print("\n🎯 Event-based Triggers:")
        for trigger in self.triggers.get("event_based", []):
            status = "✅" if trigger["enabled"] else "❌"
            print(f"  {status} {trigger['name']:20} - {trigger['event']}")
        
        print("\n📈 Condition-based Triggers:")
        for trigger in self.triggers.get("condition_based", []):
            status = "✅" if trigger["enabled"] else "❌"
            print(f"  {status} {trigger['name']:20} - {trigger['condition']}")

def main():
    """메인 진입점"""
    import sys
    
    trigger = AutoTrigger()
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        if command == "daemon":
            trigger.run_daemon()
        elif command == "status":
            trigger.status()
        elif command == "check":
            print("🔍 Checking all triggers...")
            trigger.check_time_triggers()
            trigger.check_github_events()
            trigger.check_conditions()
            print("✅ Check complete")
        else:
            print("""
Auto Trigger System

Usage:
  auto_trigger.py         - Show this help
  auto_trigger.py daemon   - Run as daemon (background)
  auto_trigger.py status   - Show trigger status
  auto_trigger.py check    - Check all triggers once
""")
    else:
        trigger.status()

if __name__ == "__main__":
    main()