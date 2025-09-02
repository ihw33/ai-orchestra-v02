"""
PM Claude의 동적 페르소나 할당 테스트 시나리오
사용자 요청에 따라 상황별로 어떻게 페르소나를 선택하는지 시연
"""

import sys
import os
import json
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from src.adapters.persona.persona_assignment_adapter import PMClaudePersonaAssignmentAdapter
from src.ports.persona_assignment_port import PersonaType

class PersonaAssignmentScenarios:
    """PM Claude의 페르소나 할당 시나리오"""
    
    def __init__(self):
        self.adapter = PMClaudePersonaAssignmentAdapter()
        self.scenario_results = []
    
    def run_scenario(self, scenario_name: str, task_description: str):
        """시나리오 실행"""
        print(f"\n{'='*60}")
        print(f"시나리오: {scenario_name}")
        print(f"{'='*60}")
        print(f"사용자 요청: {task_description}")
        print("-" * 40)
        
        # PM Claude의 분석 과정
        print("\n🤔 PM Claude 분석 중...")
        
        # 1. 요구사항 분석
        requirements = self.adapter.analyze_task_requirements(task_description)
        print(f"\n📊 분석 결과:")
        print(f"  - 복잡도: {requirements['complexity']}")
        print(f"  - 작업 유형: {requirements['type']}")
        print(f"  - 우선순위: {requirements['priority']}")
        print(f"  - 필요 스킬: {requirements['skills_needed']}")
        
        # 2. PM의 판단 과정 보여주기
        print(f"\n💭 PM Claude의 판단:")
        self._show_pm_reasoning(requirements, task_description)
        
        # 3. 페르소나 선택
        persona = self.adapter.select_persona(requirements)
        print(f"\n✅ 선택된 페르소나: {persona.name} ({persona.role})")
        print(f"   권한 레벨: {persona.decision_authority}%")
        print(f"   전문 분야: {', '.join(persona.skills)}")
        
        # 4. AI 할당
        assignment = self.adapter.assign_persona_to_ai(persona, task_id=100)
        print(f"\n🤖 할당된 AI: {assignment.ai_name}")
        print(f"📝 할당 이유: {assignment.reason}")
        
        # 5. 대안 페르소나들
        if assignment.alternatives:
            print(f"\n🔄 고려한 다른 옵션들:")
            for alt in assignment.alternatives:
                print(f"   - {alt.name}: {alt.role}")
        
        # 결과 저장
        self.scenario_results.append({
            'scenario': scenario_name,
            'task': task_description,
            'requirements': requirements,
            'selected_persona': persona.name,
            'assigned_ai': assignment.ai_name,
            'reason': assignment.reason
        })
        
        return persona, assignment
    
    def _show_pm_reasoning(self, requirements: dict, task: str):
        """PM의 판단 과정 설명"""
        
        task_lower = task.lower()
        
        # 긴급도 판단
        if requirements['priority'] == 'critical':
            print("  🚨 긴급! PM이 직접 관여 필요")
            return
        
        # 작업 유형별 판단
        if requirements['type'] == 'review':
            print("  👀 코드 리뷰 작업 → 리뷰어 필요")
        elif requirements['type'] == 'design':
            print("  📐 설계 작업 → 아키텍트 필요")
        elif requirements['type'] == 'api':
            print("  🔌 API 작업 → 백엔드 전문가 필요")
        elif requirements['type'] == 'ui':
            print("  🎨 UI 작업 → 프론트엔드 전문가 필요")
        
        # 복잡도별 판단
        if requirements['complexity'] == 'complex':
            print("  🧩 복잡한 작업 → 시니어 레벨 필요")
        elif requirements['complexity'] == 'simple':
            print("  ✨ 간단한 작업 → 주니어도 가능")
        
        # 특수 키워드 판단
        if 'port' in task_lower or 'adapter' in task_lower:
            print("  🏗️ 패턴 구현 → 아키텍처 이해 필요")
        if '도메인' in task or 'domain' in task_lower:
            print("  🎯 도메인 모델링 → 비즈니스 이해 필요")
        if '병렬' in task or 'parallel' in task_lower:
            print("  ⚡ 병렬 처리 → 성능 전문가 고려")
    
    def run_all_scenarios(self):
        """모든 시나리오 실행"""
        
        print("\n" + "="*70)
        print("🎭 PM Claude의 동적 페르소나 할당 시연")
        print("="*70)
        print("\n설명: 고정된 로직이 아닌, PM이 상황에 맞게 동적으로 판단합니다.")
        
        # 시나리오 정의
        scenarios = [
            # 1. 긴급 상황
            ("긴급 서버 장애", "긴급! 프로덕션 서버가 다운됐습니다. 즉시 복구 필요"),
            
            # 2. 복잡한 아키텍처
            ("DDD 아키텍처 설계", "도메인 기반 개발을 위한 복잡한 시스템 아키텍처 설계"),
            
            # 3. 간단한 버그 수정
            ("타이포 수정", "README.md 파일의 간단한 오타 수정"),
            
            # 4. API 개발
            ("REST API 구현", "사용자 인증을 위한 REST API 엔드포인트 구현"),
            
            # 5. 코드 리뷰
            ("PR 리뷰", "PR #35의 코드 리뷰 수행"),
            
            # 6. UI 개발
            ("대시보드 UI", "관리자 대시보드 UI 컴포넌트 개발"),
            
            # 7. 데이터베이스
            ("DB 최적화", "데이터베이스 쿼리 성능 최적화"),
            
            # 8. Port/Adapter 패턴
            ("어댑터 구현", "새로운 결제 시스템을 위한 Port/Adapter 패턴 구현"),
            
            # 9. 테스트
            ("통합 테스트", "전체 시스템 통합 테스트 작성"),
            
            # 10. 문서화
            ("API 문서", "API 사용 가이드 문서 작성")
        ]
        
        # 각 시나리오 실행
        for scenario_name, task in scenarios:
            self.run_scenario(scenario_name, task)
        
        # 요약
        self.print_summary()
    
    def print_summary(self):
        """전체 요약"""
        print("\n" + "="*70)
        print("📊 PM Claude의 페르소나 할당 요약")
        print("="*70)
        
        # AI별 할당 통계
        ai_stats = {}
        persona_stats = {}
        
        for result in self.scenario_results:
            ai = result['assigned_ai']
            persona = result['selected_persona']
            
            ai_stats[ai] = ai_stats.get(ai, 0) + 1
            persona_stats[persona] = persona_stats.get(persona, 0) + 1
        
        print("\n🤖 AI별 할당:")
        for ai, count in ai_stats.items():
            print(f"  - {ai}: {count}건")
        
        print("\n👥 페르소나별 할당:")
        for persona, count in persona_stats.items():
            print(f"  - {persona}: {count}건")
        
        print("\n💡 PM Claude의 판단 특징:")
        print("  1. 긴급 상황 → PM이 직접 개입")
        print("  2. 복잡한 설계 → 아키텍트 할당")
        print("  3. 구현 작업 → 개발자 할당")
        print("  4. 리뷰 작업 → 리뷰어 할당")
        print("  5. AI 선택도 작업 특성에 맞게 동적 결정")
        
        # JSON으로 저장
        output_file = f"persona_assignment_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(self.scenario_results, f, ensure_ascii=False, indent=2)
        print(f"\n📁 결과 저장: {output_file}")


# 실행
if __name__ == "__main__":
    tester = PersonaAssignmentScenarios()
    tester.run_all_scenarios()
    
    print("\n" + "="*70)
    print("✅ 테스트 완료!")
    print("="*70)
    print("\n핵심 포인트:")
    print("- PM Claude는 고정된 로직이 아닌 상황 판단으로 페르소나 선택")
    print("- 각 작업의 특성을 분석하여 가장 적합한 페르소나 매칭")
    print("- AI 선택도 페르소나와 작업 특성에 맞게 동적 결정")
    print("- 이것이 '아답터를 쓰지만 고정된 로직이 아닌' 동적 할당입니다")