#!/usr/bin/env python3
"""
PM Orchestration Controller - PM 모니터링 시작/종료 관리
"""

import subprocess
import sys
import json
import os
import signal
from datetime import datetime

class PMOrchestrationController:
    """PM 오케스트레이션 컨트롤러"""
    
    def __init__(self):
        self.pid_file = "pm_orchestration.pid"
        self.state_file = "pm_orchestration_state.json"
        
    def start(self, issue_number=34, repo="ihw33/iwl-v5-rebuild"):
        """모니터링 시작"""
        # 이미 실행 중인지 확인
        if os.path.exists(self.pid_file):
            with open(self.pid_file, 'r') as f:
                pid = int(f.read())
            try:
                os.kill(pid, 0)  # 프로세스 존재 확인
                print(f"⚠️ PM Orchestration이 이미 실행 중입니다 (PID: {pid})")
                return
            except OSError:
                # 프로세스가 없으면 pid 파일 삭제
                os.remove(self.pid_file)
        
        print(f"🚀 PM Orchestration 시작")
        print(f"  - Issue: #{issue_number}")
        print(f"  - Repo: {repo}")
        
        # 백그라운드로 DAG 실행
        process = subprocess.Popen(
            [sys.executable, "dags/pm_orchestration_dag.py"],
            stdout=open("pm_orchestration.log", "a"),
            stderr=subprocess.STDOUT
        )
        
        # PID 저장
        with open(self.pid_file, 'w') as f:
            f.write(str(process.pid))
        
        print(f"✅ PM Orchestration 시작됨 (PID: {process.pid})")
        print(f"📝 로그: pm_orchestration.log")
        
    def stop(self):
        """모니터링 중지"""
        if not os.path.exists(self.pid_file):
            print("⚠️ PM Orchestration이 실행 중이지 않습니다")
            return
        
        with open(self.pid_file, 'r') as f:
            pid = int(f.read())
        
        try:
            os.kill(pid, signal.SIGTERM)
            os.remove(self.pid_file)
            print(f"✅ PM Orchestration 중지됨 (PID: {pid})")
            
            # 상태 파일 업데이트
            if os.path.exists(self.state_file):
                with open(self.state_file, 'r') as f:
                    state = json.load(f)
                state['status'] = 'stopped'
                state['stopped_at'] = str(datetime.now())
                with open(self.state_file, 'w') as f:
                    json.dump(state, f, indent=2)
                    
        except ProcessLookupError:
            print(f"⚠️ 프로세스를 찾을 수 없습니다 (PID: {pid})")
            os.remove(self.pid_file)
        except Exception as e:
            print(f"❌ 오류 발생: {e}")
    
    def status(self):
        """현재 상태 확인"""
        # 실행 상태 확인
        if os.path.exists(self.pid_file):
            with open(self.pid_file, 'r') as f:
                pid = int(f.read())
            try:
                os.kill(pid, 0)
                print(f"✅ PM Orchestration 실행 중 (PID: {pid})")
            except OSError:
                print("⚠️ PM Orchestration이 비정상 종료됨")
                os.remove(self.pid_file)
        else:
            print("❌ PM Orchestration이 실행 중이지 않습니다")
        
        # 상태 파일 확인
        if os.path.exists(self.state_file):
            with open(self.state_file, 'r') as f:
                state = json.load(f)
            print(f"\n📊 마지막 상태:")
            print(f"  - 시간: {state.get('timestamp')}")
            print(f"  - 상태: {state.get('status')}")
            print(f"  - 반복: {state.get('completion_conditions', {}).get('current_iteration', 0)}회")

def main():
    """메인 함수"""
    if len(sys.argv) < 2:
        print("사용법:")
        print("  python pm_orchestration_controller.py start [issue_number] [repo]")
        print("  python pm_orchestration_controller.py stop")
        print("  python pm_orchestration_controller.py status")
        sys.exit(1)
    
    controller = PMOrchestrationController()
    command = sys.argv[1]
    
    if command == "start":
        issue_number = int(sys.argv[2]) if len(sys.argv) > 2 else 34
        repo = sys.argv[3] if len(sys.argv) > 3 else "ihw33/iwl-v5-rebuild"
        controller.start(issue_number, repo)
    elif command == "stop":
        controller.stop()
    elif command == "status":
        controller.status()
    else:
        print(f"❌ 알 수 없는 명령어: {command}")

if __name__ == "__main__":
    main()