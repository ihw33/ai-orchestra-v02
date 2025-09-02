#!/usr/bin/env python3
"""
PM Orchestration DAG - PM 자동 모니터링 및 지시 워크플로우
"""

from datetime import datetime
import time
import sys
import json
import os
sys.path.append('/Users/m4_macbook/Projects/ai-orchestra-v02')

from nodes.pm_monitor_node import PM_MONITOR
from evolution_logger import EvolutionLogger

class PMOrchestrationDAG:
    """PM 오케스트레이션 DAG"""
    
    def __init__(self):
        self.name = "PM_ORCHESTRATION"
        self.evolution_logger = EvolutionLogger()
        self.monitor_interval = 300  # 5분
        self.state_file = "pm_orchestration_state.json"
        self.completion_conditions = {
            "all_tasks_completed": False,
            "issue_closed": False,
            "max_iterations": 100,
            "current_iteration": 0
        }
        
    def check_completion(self, result):
        """완료 조건 확인"""
        progress = result.get('progress', {})
        
        # 모든 작업 완료 확인
        if (progress.get('main_platform') and 
            progress.get('kb_system') and 
            progress.get('llm_service') and
            not progress.get('pending_tasks')):
            self.completion_conditions['all_tasks_completed'] = True
            return True
            
        # 최대 반복 횟수 확인
        if self.completion_conditions['current_iteration'] >= self.completion_conditions['max_iterations']:
            print("⚠️ 최대 반복 횟수 도달")
            return True
            
        return False
    
    def save_state(self):
        """현재 상태 저장"""
        with open(self.state_file, 'w') as f:
            json.dump({
                'timestamp': str(datetime.now()),
                'completion_conditions': self.completion_conditions,
                'status': 'running'
            }, f, indent=2)
    
    def run_monitoring_cycle(self):
        """모니터링 사이클 실행"""
        print(f"🎯 PM Orchestration DAG 시작 - {datetime.now()}")
        print(f"📌 종료 조건: 모든 작업 완료 또는 최대 {self.completion_conditions['max_iterations']}회 반복")
        
        self.save_state()
        
        while True:
            try:
                self.completion_conditions['current_iteration'] += 1
                print(f"\n🔄 반복 #{self.completion_conditions['current_iteration']}")
                
                # PM Monitor 노드 실행
                result = PM_MONITOR.execute()
                
                # Evolution Logger에 기록
                self.evolution_logger.log_completion("PM_MONITOR")
                
                # 결과 출력
                print(f"✅ 모니터링 완료:")
                print(f"  - 완료 작업: {result['progress']['completed_tasks']}")
                print(f"  - 대기 작업: {result['progress']['pending_tasks']}")
                
                if result.get('next_instruction'):
                    print(f"  - 지시 전송 완료")
                    self.evolution_logger.log_completion("SEND_INSTRUCTION")
                
                # 완료 조건 확인
                if self.check_completion(result):
                    print(f"\n🎉 PM Orchestration 완료!")
                    print(f"  - 총 반복: {self.completion_conditions['current_iteration']}회")
                    print(f"  - 모든 작업 완료: {self.completion_conditions['all_tasks_completed']}")
                    
                    # 상태 파일 업데이트
                    with open(self.state_file, 'w') as f:
                        json.dump({
                            'timestamp': str(datetime.now()),
                            'completion_conditions': self.completion_conditions,
                            'status': 'completed'
                        }, f, indent=2)
                    break
                    
                # 대기
                print(f"⏰ 다음 확인: {self.monitor_interval}초 후...")
                time.sleep(self.monitor_interval)
                
            except KeyboardInterrupt:
                print("🛑 PM Orchestration 수동 중지")
                with open(self.state_file, 'w') as f:
                    json.dump({
                        'timestamp': str(datetime.now()),
                        'completion_conditions': self.completion_conditions,
                        'status': 'stopped'
                    }, f, indent=2)
                break
            except Exception as e:
                print(f"⚠️ 오류 발생: {e}")
                time.sleep(30)  # 오류 시 30초 대기
                
    def execute(self):
        """DAG 실행"""
        self.run_monitoring_cycle()

# DAG 인스턴스
pm_dag = PMOrchestrationDAG()

if __name__ == "__main__":
    pm_dag.execute()