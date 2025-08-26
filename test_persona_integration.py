#!/usr/bin/env python3
"""
페르소나 시스템 통합 테스트
"""

from unified_orchestrator import UnifiedOrchestrator

def test_persona_mode():
    """[AI] 태그가 있는 이슈 테스트"""
    print("="*50)
    print("🧪 페르소나 모드 테스트")
    print("="*50)
    
    orchestrator = UnifiedOrchestrator()
    
    # 테스트 이슈 번호 (실제 [AI] 태그가 있는 이슈)
    test_issue = 75  # [AI] Node-DAG-Executor 및 페르소나 시스템 통합
    
    print(f"\n테스트 이슈: #{test_issue}")
    result = orchestrator.process_github_issue(test_issue)
    
    print("\n결과:")
    print(f"- 성공: {result.get('success')}")
    print(f"- 모드: {result.get('mode', 'default')}")
    print(f"- 메시지: {result.get('message', '')}")

def test_default_mode():
    """[AI] 태그가 없는 일반 이슈 테스트"""
    print("\n" + "="*50)
    print("🧪 기본 모드 테스트")
    print("="*50)
    
    orchestrator = UnifiedOrchestrator()
    
    # [AI] 태그가 없는 이슈
    test_issue = 56  # 일반 이슈
    
    print(f"\n테스트 이슈: #{test_issue}")
    result = orchestrator.process_github_issue(test_issue)
    
    print("\n결과:")
    print(f"- 성공: {result.get('success')}")
    print(f"- 패턴: {result.get('pattern', 'none')}")

if __name__ == "__main__":
    print("🚀 페르소나 시스템 통합 테스트 시작")
    print("\n")
    
    # 페르소나 모드 테스트
    test_persona_mode()
    
    # 기본 모드 테스트
    test_default_mode()
    
    print("\n✅ 테스트 완료!")