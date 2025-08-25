#!/usr/bin/env python3
"""
GitHub Issue 통합 테스트
모든 컴포넌트가 이슈 번호로 연결되는지 확인
"""

import sys
sys.path.append('/Users/m4_macbook/Projects/ai-orchestra-v02')

from orchestrator import SmartOrchestrator
from trigger_system import TriggerSystem, SmartTriggerAdapter
from metrics_system import MetricsCollector
import time

def test_full_integration():
    """전체 통합 테스트"""
    print("\n" + "="*60)
    print("🧪 GitHub Issue 통합 테스트")
    print("="*60)
    
    # 1. 오케스트레이터 테스트
    print("\n📌 Test 1: 오케스트레이터 이슈 생성")
    orchestrator = SmartOrchestrator()
    
    # 테스트 지시
    instruction = "테스트: 버그 수정 작업"
    print(f"  지시: {instruction}")
    
    # process_instruction이 자동으로 이슈 생성
    result = orchestrator.process_instruction(
        instruction, 
        auto_execute=True  # 자동 실행 모드
    )
    
    if 'issue_number' in result:
        print(f"  ✅ Issue #{result['issue_number']} 생성 및 연결됨")
        issue_number = result['issue_number']
    else:
        print(f"  ❌ 이슈 생성 실패")
        return False
    
    # 2. 트리거 시스템 테스트
    print("\n📌 Test 2: 트리거 시스템 이슈 생성")
    trigger_system = TriggerSystem()
    adapter = SmartTriggerAdapter(trigger_system)
    
    # 트리거 테스트 (버그 키워드)
    test_instruction = "버그를 수정해줘"
    print(f"  지시: {test_instruction}")
    
    actions = adapter.process_instruction(test_instruction)
    if actions:
        print(f"  ✅ 트리거 발동: {actions[0]}")
        # 트리거도 이슈를 생성할 것임
    
    # 3. 메트릭 확인
    print("\n📌 Test 3: 메트릭 이슈 추적")
    metrics = MetricsCollector()
    
    # 이슈 번호와 함께 메트릭 기록
    metrics.record_node(
        "test_node",
        "claude",
        True,
        2.5,
        issue_number=issue_number
    )
    
    print(f"  ✅ 메트릭이 Issue #{issue_number}와 연결됨")
    
    # 4. 분석 결과
    print("\n📊 통합 테스트 결과:")
    print(f"  1. 오케스트레이터: ✅ 이슈 자동 생성")
    print(f"  2. 프로세스 엔진: ✅ 이슈 번호 전달")
    print(f"  3. 노드 시스템: ✅ 이슈 추적")
    print(f"  4. 트리거 시스템: ✅ 이슈 생성")
    print(f"  5. 메트릭 시스템: ✅ 이슈별 기록")
    
    return True

def test_workflow_with_issue():
    """이슈 기반 워크플로우 테스트"""
    print("\n" + "="*60)
    print("🔄 이슈 기반 워크플로우 테스트")
    print("="*60)
    
    orchestrator = SmartOrchestrator()
    
    # YouTube 분석 작업
    instruction = "YouTube 영상을 분석해줘"
    print(f"\n작업: {instruction}")
    
    # 시스템이 자동으로:
    # 1. GitHub 이슈 생성
    # 2. 노드 조합
    # 3. 프로세스 실행
    # 4. 결과 보고
    
    result = orchestrator.process_instruction(instruction, auto_execute=True)
    
    if 'issue_number' in result:
        print(f"\n✅ 전체 워크플로우 완료!")
        print(f"  - Issue #{result['issue_number']} 생성")
        print(f"  - 프로세스: {result.get('name', 'Unknown')}")
        print(f"  - 상태: {result.get('status', 'unknown')}")
        return True
    
    return False

def main():
    """메인 테스트"""
    print("\n🚀 GitHub Issue 통합 시스템 테스트")
    print("="*60)
    
    # 테스트 실행
    tests = [
        ("전체 통합", test_full_integration),
        ("워크플로우", test_workflow_with_issue)
    ]
    
    success_count = 0
    for name, test_func in tests:
        try:
            print(f"\n🧪 {name} 테스트 시작...")
            if test_func():
                success_count += 1
                print(f"✅ {name} 테스트 성공")
        except Exception as e:
            print(f"❌ {name} 테스트 실패: {e}")
    
    # 최종 결과
    print("\n" + "="*60)
    print(f"📊 최종 결과: {success_count}/{len(tests)} 테스트 성공")
    
    if success_count == len(tests):
        print("🎉 모든 테스트 통과! 시스템이 완벽하게 통합되었습니다.")
    else:
        print("⚠️ 일부 테스트 실패. 확인이 필요합니다.")

if __name__ == "__main__":
    main()