#!/usr/bin/env python3
"""
SuperClaude 명령어 통합 테스트
페르소나별로 SC 명령어가 자동으로 포함되는지 확인
"""

from personas.persona_loader import PersonaLoader

def test_sc_commands():
    print("="*60)
    print("🚀 SuperClaude 명령어 통합 테스트")
    print("="*60)
    
    loader = PersonaLoader()
    
    # 테스트 케이스
    test_cases = [
        {
            "persona": "backend_lead_01",  # 김정호
            "task": "API 설계 부탁드립니다",
            "expected_sc": "/SC API"
        },
        {
            "persona": "frontend_lead_01",  # Maria Silva
            "task": "대시보드 디자인 검토",
            "expected_sc": "/SC Design"
        },
        {
            "persona": "qa_lead_01",  # 박민수
            "task": "테스트 커버리지 확인",
            "expected_sc": "/SC Test"
        },
        {
            "persona": "backend_lead_01",
            "task": "데이터베이스 최적화 필요",
            "expected_sc": "/SC Database"
        }
    ]
    
    for i, test in enumerate(test_cases, 1):
        print(f"\n📌 테스트 {i}: {test['persona']} - {test['task']}")
        print("-"*50)
        
        prompt = loader.generate_prompt(
            persona_id=test['persona'],
            task=test['task']
        )
        
        # SC 명령어 확인
        first_line = prompt.split('\n')[0]
        print(f"첫 줄: {first_line}")
        
        if test['expected_sc'] in first_line:
            print(f"✅ 성공: {test['expected_sc']} 포함됨")
        else:
            print(f"❌ 실패: {test['expected_sc']} 없음")
        
        # 페르소나 정보 확인
        persona = loader.get_persona(test['persona'])
        if persona:
            print(f"👤 페르소나: {persona['profile']['name']}")
            print(f"📋 SC 명령어들: {', '.join(persona.get('superclaude_commands', []))}")

if __name__ == "__main__":
    test_sc_commands()
    print("\n" + "="*60)
    print("✅ 테스트 완료!")
    print("="*60)