#!/usr/bin/env python3
"""
페르소나 통합 수정
multi_ai_orchestrator.py에 페르소나 자동 적용 추가
"""

def add_persona_to_orchestrator():
    """페르소나 통합 코드"""
    
    enhanced_prompt_code = '''
    def _create_ai_prompt(self, ai_name: str, role: str, issue_body: str) -> str:
        """각 AI용 프롬프트 생성 - 페르소나 포함"""
        
        # 1. 이슈 분석으로 페르소나 결정
        from orchestrator import InstructionAnalyzer
        analyzer = InstructionAnalyzer()
        
        # 이슈 내용에서 페르소나 추출
        analysis = analyzer.analyze(issue_body)
        persona = analysis.get('persona', 'balanced')
        
        # 2. 페르소나별 스타일 정의
        persona_styles = {
            'speedster': '빠르고 간결하게. 핵심만 구현. MVP 우선.',
            'perfectionist': '완벽하고 꼼꼼하게. 모든 엣지케이스 처리. 문서화 포함.',
            'critic': '비판적으로 분석. 문제점 우선 파악. 개선점 제시.',
            'minimalist': '최소한의 코드로. 단순하고 명확하게. KISS 원칙.',
            'balanced': '균형잡힌 접근. 실용적인 해결책.'
        }
        
        style = persona_styles.get(persona, persona_styles['balanced'])
        
        # 3. 긴급도 파악
        urgency = analysis.get('urgency', 'normal')
        urgency_note = ""
        if urgency == 'high':
            urgency_note = "⚡ 긴급! 빠른 해결 필요."
        elif urgency == 'perfect':
            urgency_note = "⭐ 완벽한 솔루션 필요."
        
        # 4. 강화된 프롬프트 생성
        return f"""당신은 {ai_name}입니다.
역할: {role}
페르소나: {persona} - {style}
{urgency_note}

다음 이슈를 분석하고 해결책을 제시하세요:
{issue_body}

작업 스타일:
- {style}
- 당신의 전문 분야({role})에 집중
- {persona} 페르소나로 응답

응답 형식:
1. 문제 분석 ({persona} 관점)
2. 해결 방안 ({urgency} 수준)
3. 구현 코드 (있다면)
4. 추가 제안사항"""
'''
    
    print("📝 페르소나 통합 코드 생성 완료")
    return enhanced_prompt_code

def create_test_with_persona():
    """페르소나 적용 테스트"""
    
    test_code = '''
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
        print(f"\\n📝 지시: {instruction}")
        print(f"   페르소나: {result['persona']} (예상: {expected_persona})")
        print(f"   긴급도: {result['urgency']} (예상: {expected_urgency})")
        
        # AI 프롬프트 생성 시뮬레이션
        if result['persona']:
            print(f"   → AI에게: '{result['persona']}' 스타일로 작업 지시")

if __name__ == "__main__":
    test_persona_detection()
'''
    
    return test_code

def main():
    print("🔧 페르소나 통합 수정")
    print("="*50)
    
    print("\n❌ 현재 문제:")
    print("- orchestrator.py: 페르소나 분석 기능 있음 ✓")
    print("- multi_ai_orchestrator.py: 페르소나 사용 안 함 ✗")
    
    print("\n✅ 해결 방안:")
    print("1. 이슈 내용 분석 → 페르소나 자동 결정")
    print("2. 각 AI 프롬프트에 페르소나 스타일 추가")
    print("3. 긴급도에 따른 작업 우선순위 설정")
    
    print("\n📋 수정할 코드:")
    enhanced_code = add_persona_to_orchestrator()
    print(enhanced_code[:500] + "...")
    
    print("\n🧪 테스트 코드 생성:")
    test_code = create_test_with_persona()
    
    # 테스트 파일 저장
    with open('test_persona_integration.py', 'w') as f:
        f.write(test_code)
    
    print("✅ test_persona_integration.py 생성 완료")
    
    print("\n" + "="*50)
    print("📌 적용 방법:")
    print("1. multi_ai_orchestrator.py의 _create_ai_prompt 메서드 교체")
    print("2. python3 test_persona_integration.py로 테스트")
    print("3. 실제 이슈로 테스트")

if __name__ == "__main__":
    main()