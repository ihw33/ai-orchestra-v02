#!/usr/bin/env python3
"""
PM 실시간 모니터링 시스템
다른 세션의 PM Claude가 작업 상황을 추적할 수 있게 함
"""

import json
import time
import os
from datetime import datetime
import subprocess
import threading

class PMMonitor:
    """PM 작업 모니터링"""
    
    def __init__(self):
        self.status_file = "/Users/m4_macbook/Projects/ai-orchestra-v02/pm_status.json"
        self.log_file = "/Users/m4_macbook/Projects/ai-orchestra-v02/pm_activity.log"
        self.running = True
        
    def update_status(self, task, status, details=""):
        """상태 업데이트"""
        data = {
            "timestamp": datetime.now().isoformat(),
            "task": task,
            "status": status,
            "details": details,
            "pm_id": os.getpid()
        }
        
        # 상태 파일 업데이트
        with open(self.status_file, 'w') as f:
            json.dump(data, f, indent=2)
        
        # 활동 로그 추가
        with open(self.log_file, 'a') as f:
            f.write(f"{data['timestamp']} | {task} | {status} | {details}\n")
        
        print(f"📡 상태 업데이트: {task} - {status}")
    
    def get_current_status(self):
        """현재 상태 조회"""
        if os.path.exists(self.status_file):
            with open(self.status_file, 'r') as f:
                return json.load(f)
        return None
    
    def watch_github_issues(self):
        """GitHub 이슈 실시간 모니터링"""
        print("\n🔍 GitHub 이슈 모니터링 시작...")
        
        while self.running:
            # 최신 이슈 체크
            cmd = "gh issue list -R ihw33/ai-orchestra-v02 --limit 1 --json number,title,state,updatedAt"
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            
            if result.returncode == 0 and result.stdout:
                issues = json.loads(result.stdout)
                if issues:
                    issue = issues[0]
                    self.update_status(
                        f"Issue #{issue['number']}",
                        issue['state'],
                        issue['title']
                    )
            
            time.sleep(10)  # 10초마다 체크
    
    def start_monitoring(self):
        """백그라운드 모니터링 시작"""
        thread = threading.Thread(target=self.watch_github_issues)
        thread.daemon = True
        thread.start()
        print("✅ 백그라운드 모니터링 시작됨")
    
    def stop_monitoring(self):
        """모니터링 중지"""
        self.running = False
        print("⏹ 모니터링 중지됨")

# 다른 PM이 사용할 명령어들
class PMCommands:
    """다른 PM Claude가 사용할 수 있는 명령어"""
    
    @staticmethod
    def check_status():
        """현재 작업 상태 확인"""
        monitor = PMMonitor()
        status = monitor.get_current_status()
        
        if status:
            print(f"\n📊 현재 PM 상태")
            print(f"  작업: {status['task']}")
            print(f"  상태: {status['status']}")
            print(f"  시간: {status['timestamp']}")
            print(f"  상세: {status['details']}")
        else:
            print("❌ 활성 작업 없음")
    
    @staticmethod
    def view_activity_log(lines=10):
        """최근 활동 로그 보기"""
        log_file = "/Users/m4_macbook/Projects/ai-orchestra-v02/pm_activity.log"
        
        if os.path.exists(log_file):
            print(f"\n📜 최근 활동 로그 (최근 {lines}개)")
            cmd = f"tail -n {lines} {log_file}"
            subprocess.run(cmd, shell=True)
        else:
            print("❌ 활동 로그 없음")
    
    @staticmethod
    def assign_task(task_description):
        """새 작업 할당"""
        monitor = PMMonitor()
        monitor.update_status(task_description, "ASSIGNED", "다른 PM에 의해 할당됨")
        print(f"✅ 작업 할당됨: {task_description}")
    
    @staticmethod
    def get_metrics_summary():
        """메트릭 요약 보기"""
        metrics_file = "/Users/m4_macbook/Projects/ai-orchestra-v02/metrics_lite.jsonl"
        
        if os.path.exists(metrics_file):
            total_lines = sum(1 for _ in open(metrics_file))
            print(f"\n📈 메트릭 요약")
            print(f"  전체 실행: {total_lines}개")
            
            # 최근 5개 실행 표시
            cmd = f"tail -n 5 {metrics_file}"
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            
            if result.stdout:
                print("\n  최근 실행:")
                for line in result.stdout.strip().split('\n'):
                    data = json.loads(line)
                    if 'node_type' in data:
                        print(f"    • {data['node_type']}: {'✅' if data['success'] else '❌'}")

if __name__ == "__main__":
    print("🎮 PM 모니터링 콘솔")
    print("="*50)
    
    import sys
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "status":
            PMCommands.check_status()
        elif command == "log":
            PMCommands.view_activity_log()
        elif command == "metrics":
            PMCommands.get_metrics_summary()
        elif command == "assign":
            if len(sys.argv) > 2:
                PMCommands.assign_task(" ".join(sys.argv[2:]))
            else:
                print("❌ 작업 설명이 필요합니다")
        elif command == "monitor":
            monitor = PMMonitor()
            monitor.start_monitoring()
            print("\n모니터링 중... (Ctrl+C로 중지)")
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                monitor.stop_monitoring()
        else:
            print(f"❌ 알 수 없는 명령: {command}")
    else:
        print("\n사용 가능한 명령:")
        print("  python3 pm_monitor.py status   - 현재 상태 확인")
        print("  python3 pm_monitor.py log      - 활동 로그 보기")
        print("  python3 pm_monitor.py metrics  - 메트릭 요약")
        print("  python3 pm_monitor.py assign [작업] - 작업 할당")
        print("  python3 pm_monitor.py monitor  - 실시간 모니터링")