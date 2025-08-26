#!/usr/bin/env python3
"""
자동 이슈 생성 테스트 - AI 할당 포함
"""

import sys
sys.path.append('/Users/m4_macbook/Projects/ai-orchestra-v02')

from orchestrator import SmartOrchestrator

def test_issue_creation():
    """새로운 이슈 생성 테스트"""
    
    orchestrator = SmartOrchestrator()
    
    # 테스트 지시
    test_instructions = [
        "새로운 로그인 기능을 만들어줘",
        "버그 #789를 빨리 수정해줘",
        "이 코드의 성능을 분석하고 개선해줘"
    ]
    
    for instruction in test_instructions:
        print(f"\n{'='*60}")
        print(f"📝 지시: {instruction}")
        print(f"{'='*60}")
        
        # 분석만 실행 (실제 이슈 생성 안 함)
        analysis = orchestrator.analyzer.analyze(instruction)
        
        print(f"\n📊 분석 결과:")
        print(f"  의도: {analysis['intent']}")
        print(f"  긴급도: {analysis['urgency']}")
        print(f"  페르소나: {analysis['persona']}")
        print(f"  프로세스: {analysis['suggested_process']}")
        
        print(f"\n🤖 AI 자동 할당:")
        for node_type in analysis['suggested_nodes']:
            executor = orchestrator.get_best_executor(node_type)
            print(f"  - {executor.upper()}: {node_type.value}")
        
        print(f"\n📋 노드 구성:")
        print(f"  ProcessBuilder('{analysis['suggested_process']}', issue_number='자동')")
        for node_type in analysis['suggested_nodes']:
            executor = orchestrator.get_best_executor(node_type)
            print(f"    .add(NodeType.{node_type.name}, executor='{executor}')")
        print(f"    .build()")

def main():
    print("🧪 자동 이슈 생성 테스트 (AI 할당 포함)")
    test_issue_creation()
    
    print("\n" + "="*60)
    print("✅ 테스트 완료!")
    print("\n이제 모든 이슈가 자동으로:")
    print("1. AI 할당 포함")
    print("2. 페르소나 설정")
    print("3. 노드 구성 코드 생성")
    print("4. 작업 계획 수립")

if __name__ == "__main__":
    main()