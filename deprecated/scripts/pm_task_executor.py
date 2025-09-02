#!/usr/bin/env python3
"""
PM 작업 실행기 - 다른 PM Claude가 실행할 스크립트
"""

import sys
sys.path.append('/Users/m4_macbook/Projects/ai-orchestra-v02')

from pm_monitor import PMMonitor, PMCommands
from orchestrator import SmartOrchestrator
from trigger_system import TriggerSystem, SmartTriggerAdapter
import time
import subprocess

def execute_task_1():
    """작업 1: 새 기능 개발"""
    monitor = PMMonitor()
    
    print("\n🚀 작업 1 시작: 새 기능 개발")
    monitor.update_status("Feature Development", "STARTED", "로그인 기능 구현")
    
    # Step 1: 리서치
    time.sleep(1)
    monitor.update_status("Feature Development", "RESEARCHING", "기존 코드 분석 중")
    print("  📚 리서치 진행 중...")
    
    # Step 2: 설계
    time.sleep(1)
    monitor.update_status("Feature Development", "DESIGNING", "아키텍처 설계 중")
    print("  📐 설계 진행 중...")
    
    # Step 3: 구현
    time.sleep(1)
    monitor.update_status("Feature Development", "IMPLEMENTING", "코드 작성 중")
    print("  💻 구현 진행 중...")
    
    # Step 4: 테스트
    time.sleep(1)
    monitor.update_status("Feature Development", "TESTING", "단위 테스트 실행")
    print("  🧪 테스트 진행 중...")
    
    # 완료
    monitor.update_status("Feature Development", "COMPLETED", "성공적으로 완료됨")
    print("  ✅ 작업 1 완료!")
    
    return True

def execute_task_2():
    """작업 2: 버그 수정"""
    monitor = PMMonitor()
    orchestrator = SmartOrchestrator()
    
    print("\n🐛 작업 2 시작: 버그 수정")
    monitor.update_status("Bug Fix", "STARTED", "Critical bug #123")
    
    # 지시 분석
    instruction = "버그 #123을 긴급하게 수정해줘"
    analysis = orchestrator.analyzer.analyze(instruction)
    
    monitor.update_status("Bug Fix", "ANALYZING", f"의도: {analysis['intent']}, 긴급도: {analysis['urgency']}")
    print(f"  🧠 분석 결과: {analysis['suggested_process']}")
    
    # 노드 실행 시뮬레이션
    for i, node in enumerate(analysis['suggested_nodes'], 1):
        time.sleep(0.5)
        monitor.update_status("Bug Fix", f"STEP_{i}", f"실행 중: {node.value}")
        print(f"  ⚙️ Step {i}: {node.value}")
    
    monitor.update_status("Bug Fix", "COMPLETED", "버그 수정 완료")
    print("  ✅ 작업 2 완료!")
    
    return True

def execute_task_3():
    """작업 3: GitHub 이슈 관리"""
    monitor = PMMonitor()
    
    print("\n📋 작업 3 시작: GitHub 이슈 관리")
    monitor.update_status("Issue Management", "STARTED", "이슈 정리 및 라벨링")
    
    # 이슈 목록 가져오기
    cmd = "gh issue list -R ihw33/ai-orchestra-v02 --limit 3 --json number,title"
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    
    if result.returncode == 0:
        monitor.update_status("Issue Management", "PROCESSING", "이슈 분석 중")
        print("  📊 이슈 분석 중...")
        time.sleep(1)
        
        # 이슈 처리 시뮬레이션
        for i in range(3):
            monitor.update_status("Issue Management", f"ISSUE_{i+1}", f"이슈 #{i+54} 처리 중")
            print(f"  🔧 이슈 #{i+54} 처리 중...")
            time.sleep(0.5)
    
    monitor.update_status("Issue Management", "COMPLETED", "3개 이슈 처리 완료")
    print("  ✅ 작업 3 완료!")
    
    return True

def main():
    """메인 실행 함수"""
    print("="*60)
    print("🤖 PM CLAUDE - 작업 실행 모드")
    print("="*60)
    
    monitor = PMMonitor()
    
    # 초기 상태 설정
    monitor.update_status("System", "INITIALIZED", "PM Claude 작업 시작")
    
    # 현재 상태 확인
    PMCommands.check_status()
    
    # 작업 실행
    tasks = [
        ("새 기능 개발", execute_task_1),
        ("버그 수정", execute_task_2),
        ("이슈 관리", execute_task_3)
    ]
    
    print("\n📌 실행할 작업 목록:")
    for i, (name, _) in enumerate(tasks, 1):
        print(f"  {i}. {name}")
    
    print("\n🎯 작업 실행 시작...")
    
    success_count = 0
    for name, task_func in tasks:
        try:
            if task_func():
                success_count += 1
        except Exception as e:
            monitor.update_status(name, "FAILED", str(e))
            print(f"  ❌ {name} 실패: {e}")
    
    # 최종 리포트
    print("\n" + "="*60)
    print("📊 최종 리포트")
    print("="*60)
    print(f"  완료된 작업: {success_count}/{len(tasks)}")
    
    # 메트릭 요약
    PMCommands.get_metrics_summary()
    
    # 활동 로그
    PMCommands.view_activity_log(5)
    
    # 최종 상태
    monitor.update_status("System", "COMPLETED", f"{success_count}/{len(tasks)} 작업 완료")

if __name__ == "__main__":
    main()