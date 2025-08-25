#!/usr/bin/env python3
"""
Orchestrator 테스트 - 간단한 데모 버전
"""

import sys
sys.path.append('/Users/m4_macbook/Projects/ai-orchestra-v02')

from orchestrator import SmartOrchestrator, PMDecisionRules

if __name__ == "__main__":
    # 오케스트레이터 초기화
    orchestrator = SmartOrchestrator()
    
    # 간단한 테스트
    print("=== AI Orchestra 스마트 오케스트레이터 테스트 ===\n")
    
    # 단일 지시 테스트
    instruction = "버그 #123을 빨리 수정해줘"
    print(f"📝 지시: {instruction}")
    print("="*50)
    
    # 분석만 수행 (실제 실행은 제외)
    analysis = orchestrator.analyzer.analyze(instruction)
    print(f"\n📋 분석 결과:")
    print(f"  의도: {analysis['intent']}")
    print(f"  긴급도: {analysis['urgency']}")
    print(f"  제안 노드: {[n.value for n in analysis['suggested_nodes']]}")
    print(f"  제안 프로세스: {analysis['suggested_process']}")
    print(f"  페르소나: {analysis['persona']}")
    
    # PM 의사결정 체크
    print(f"\n{'='*50}")
    print("🤔 PM 의사결정 체크")
    decision = PMDecisionRules.should_stop_work()
    print(f"결정: {decision['decision']}")
    if decision['decision'] == 'STOP':
        print(f"메시지: {decision['message']}")
        print(f"다음 옵션: {decision['next_options']}")
    
    print("\n✅ 테스트 완료")