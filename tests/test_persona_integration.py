
#!/usr/bin/env python3
"""페르소나 적용 테스트"""

from orchestrator import InstructionAnalyzer

def test_persona_detection():
    """다양한 이슈로 페르소나 감지 테스트"""
    
    test_cases = [
        ("버그 긴급 수정 필요!", "speedster", "high"),
        ("완벽한 테스트 커버리지로 기능 구현", "perfectionist", "perfect"),
        ("이 코드의 문제점을 찾아주세요", "critic", "normal"),
        ("간단하게 로그인 기능만", "minimalist", "normal"),
        ("새로운 대시보드 개발", None, "normal")
    ]
    
    analyzer = InstructionAnalyzer()
    
    for instruction, expected_persona, expected_urgency in test_cases:
        result = analyzer.analyze(instruction)
        print(f"\n📝 지시: {instruction}")
        print(f"   페르소나: {result['persona']} (예상: {expected_persona})")
        print(f"   긴급도: {result['urgency']} (예상: {expected_urgency})")
        
        # AI 프롬프트 생성 시뮬레이션
        if result['persona']:
            print(f"   → AI에게: '{result['persona']}' 스타일로 작업 지시")

if __name__ == "__main__":
    test_persona_detection()
