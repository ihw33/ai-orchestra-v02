"""
Persona Assignment Adapter
PM Claude가 AI들에게 적절한 페르소나를 할당하는 구현
"""

import re
from typing import Dict, List, Optional, Tuple
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from ports.persona_assignment_port import (
    PersonaAssignmentPort,
    PersonaOrchestrationPort,
    PersonaBehaviorPort,
    Persona,
    PersonaAssignment,
    PersonaType,
    OrganizationStructure
)

class PMClaudePersonaAssignmentAdapter(PersonaAssignmentPort, PersonaOrchestrationPort, PersonaBehaviorPort):
    """PM Claude의 페르소나 할당 Adapter"""
    
    def __init__(self):
        self.organization = self._build_organization()
        self.persona_pool = self._initialize_personas()
        self.pm_decision_rules = self._define_pm_rules()
    
    def _build_organization(self) -> OrganizationStructure:
        """조직 구조 구축 - PM Claude가 설계"""
        
        # PM Claude의 조직 설계
        hierarchy = {
            PersonaType.CEO: [PersonaType.CTO, PersonaType.CPO],
            PersonaType.CTO: [PersonaType.PM, PersonaType.ENGINEERING_MANAGER],
            PersonaType.PM: [PersonaType.BACKEND_LEAD, PersonaType.FRONTEND_LEAD, PersonaType.QA_MANAGER],
            PersonaType.BACKEND_LEAD: [PersonaType.BACKEND_DEV, PersonaType.ARCHITECT],
            PersonaType.FRONTEND_LEAD: [PersonaType.FRONTEND_DEV, PersonaType.FULLSTACK_DEV],
            PersonaType.QA_MANAGER: [PersonaType.TESTER, PersonaType.REVIEWER]
        }
        
        teams = {
            'backend': [PersonaType.BACKEND_LEAD, PersonaType.BACKEND_DEV, PersonaType.ARCHITECT],
            'frontend': [PersonaType.FRONTEND_LEAD, PersonaType.FRONTEND_DEV],
            'qa': [PersonaType.QA_MANAGER, PersonaType.TESTER, PersonaType.REVIEWER],
            'management': [PersonaType.PM, PersonaType.ENGINEERING_MANAGER]
        }
        
        reporting_lines = {
            PersonaType.BACKEND_DEV: PersonaType.BACKEND_LEAD,
            PersonaType.FRONTEND_DEV: PersonaType.FRONTEND_LEAD,
            PersonaType.BACKEND_LEAD: PersonaType.PM,
            PersonaType.FRONTEND_LEAD: PersonaType.PM,
            PersonaType.PM: PersonaType.CTO,
            PersonaType.CTO: PersonaType.CEO
        }
        
        return OrganizationStructure(
            hierarchy=hierarchy,
            teams=teams,
            reporting_lines=reporting_lines
        )
    
    def _initialize_personas(self) -> Dict[PersonaType, Persona]:
        """페르소나 풀 초기화 - PM Claude가 정의"""
        
        return {
            # 나 (PM Claude)
            PersonaType.PM: Persona(
                type=PersonaType.PM,
                name="PM Claude",
                role="프로젝트 매니저 (나)",
                skills=["프로젝트 관리", "팀 조율", "의사결정", "페르소나 할당"],
                reporting_to=PersonaType.CTO,
                communication_style="명확하고 체계적",
                decision_authority=80  # 높은 권한
            ),
            
            # 개발팀
            PersonaType.BACKEND_LEAD: Persona(
                type=PersonaType.BACKEND_LEAD,
                name="Backend Lead",
                role="백엔드 팀 리드",
                skills=["API", "데이터베이스", "서버", "아키텍처"],
                reporting_to=PersonaType.PM,  # 나에게 보고
                communication_style="기술적이고 상세함",
                decision_authority=60
            ),
            
            PersonaType.FRONTEND_LEAD: Persona(
                type=PersonaType.FRONTEND_LEAD,
                name="Frontend Lead",
                role="프론트엔드 팀 리드",
                skills=["UI/UX", "React", "디자인", "사용성"],
                reporting_to=PersonaType.PM,  # 나에게 보고
                communication_style="사용자 중심적",
                decision_authority=60
            ),
            
            PersonaType.BACKEND_DEV: Persona(
                type=PersonaType.BACKEND_DEV,
                name="Backend Developer",
                role="백엔드 개발자",
                skills=["코딩", "API 구현", "데이터 처리"],
                reporting_to=PersonaType.BACKEND_LEAD,
                communication_style="코드 중심적",
                decision_authority=30
            ),
            
            PersonaType.REVIEWER: Persona(
                type=PersonaType.REVIEWER,
                name="Code Reviewer",
                role="코드 리뷰어",
                skills=["코드 리뷰", "품질 검사", "베스트 프랙티스"],
                reporting_to=PersonaType.QA_MANAGER,
                communication_style="분석적이고 비판적",
                decision_authority=40
            ),
            
            PersonaType.ARCHITECT: Persona(
                type=PersonaType.ARCHITECT,
                name="System Architect",
                role="시스템 아키텍트",
                skills=["시스템 설계", "패턴", "확장성", "도메인 모델링"],
                reporting_to=PersonaType.BACKEND_LEAD,
                communication_style="추상적이고 체계적",
                decision_authority=70
            )
        }
    
    def _define_pm_rules(self) -> Dict:
        """PM Claude의 페르소나 할당 규칙"""
        
        return {
            'task_complexity': {
                'simple': [PersonaType.BACKEND_DEV, PersonaType.FRONTEND_DEV],
                'medium': [PersonaType.BACKEND_LEAD, PersonaType.FRONTEND_LEAD],
                'complex': [PersonaType.ARCHITECT, PersonaType.PM]
            },
            'task_type': {
                'implementation': PersonaType.BACKEND_DEV,
                'design': PersonaType.ARCHITECT,
                'review': PersonaType.REVIEWER,
                'planning': PersonaType.PM,
                'testing': PersonaType.TESTER,
                'ui': PersonaType.FRONTEND_DEV,
                'api': PersonaType.BACKEND_DEV,
                'database': PersonaType.BACKEND_LEAD
            },
            'escalation_threshold': {
                'critical': PersonaType.PM,  # 나에게 에스컬레이션
                'high': PersonaType.BACKEND_LEAD,
                'medium': PersonaType.BACKEND_DEV,
                'low': PersonaType.BACKEND_DEV
            }
        }
    
    # === PersonaAssignmentPort 구현 ===
    
    def analyze_task_requirements(self, task_description: str) -> Dict:
        """Task 요구사항 분석 - PM Claude가 분석"""
        
        requirements = {
            'complexity': 'medium',
            'type': 'implementation',
            'priority': 'medium',
            'skills_needed': [],
            'estimated_effort': 'medium'
        }
        
        task_lower = task_description.lower()
        
        # 복잡도 판단 (PM의 경험 기반)
        if any(word in task_lower for word in ['복잡', 'complex', '아키텍처', 'architecture', '설계']):
            requirements['complexity'] = 'complex'
        elif any(word in task_lower for word in ['간단', 'simple', '수정', 'fix']):
            requirements['complexity'] = 'simple'
        
        # 작업 유형 판단
        if 'review' in task_lower or '리뷰' in task_lower:
            requirements['type'] = 'review'
        elif 'design' in task_lower or '설계' in task_lower:
            requirements['type'] = 'design'
        elif 'test' in task_lower or '테스트' in task_lower:
            requirements['type'] = 'testing'
        elif 'api' in task_lower:
            requirements['type'] = 'api'
        elif 'ui' in task_lower or 'frontend' in task_lower:
            requirements['type'] = 'ui'
        elif 'database' in task_lower or 'db' in task_lower:
            requirements['type'] = 'database'
        
        # 필요 스킬 추출
        if 'port' in task_lower or 'adapter' in task_lower:
            requirements['skills_needed'].append('패턴')
        if 'async' in task_lower or '비동기' in task_lower:
            requirements['skills_needed'].append('비동기')
        
        # 우선순위 (PM이 판단)
        if any(word in task_lower for word in ['urgent', '긴급', 'critical', '중요']):
            requirements['priority'] = 'critical'
        
        return requirements
    
    def select_persona(self, requirements: Dict) -> Persona:
        """요구사항에 맞는 페르소나 선택 - PM Claude의 결정"""
        
        # PM의 의사결정 로직
        
        # 1. 우선순위가 critical이면 나(PM)가 직접 관여
        if requirements['priority'] == 'critical':
            return self.persona_pool[PersonaType.PM]
        
        # 2. 작업 유형별 기본 할당
        task_type = requirements['type']
        if task_type in self.pm_decision_rules['task_type']:
            persona_type = self.pm_decision_rules['task_type'][task_type]
            return self.persona_pool.get(persona_type, self.persona_pool[PersonaType.BACKEND_DEV])
        
        # 3. 복잡도별 할당
        complexity = requirements['complexity']
        if complexity in self.pm_decision_rules['task_complexity']:
            candidates = self.pm_decision_rules['task_complexity'][complexity]
            # 첫 번째 적합한 페르소나 선택
            for candidate in candidates:
                if candidate in self.persona_pool:
                    return self.persona_pool[candidate]
        
        # 4. 기본값: Backend Developer
        return self.persona_pool[PersonaType.BACKEND_DEV]
    
    def assign_persona_to_ai(self, persona: Persona, task_id: int) -> PersonaAssignment:
        """AI에게 페르소나 할당 - PM Claude가 할당"""
        
        # AI 선택 (PM의 판단)
        ai_name = self._select_ai_for_persona(persona)
        
        # 대안 페르소나들 (PM이 고려한 옵션들)
        alternatives = self._get_alternative_personas(persona)
        
        # 할당 이유 (PM의 판단 근거)
        reason = self._generate_assignment_reason(persona, task_id)
        
        return PersonaAssignment(
            task_id=task_id,
            persona=persona,
            ai_name=ai_name,
            reason=reason,
            alternatives=alternatives
        )
    
    def get_persona_hierarchy(self) -> OrganizationStructure:
        """조직 계층 구조 조회"""
        return self.organization
    
    def escalate_to_superior(self, current_persona: Persona) -> Persona:
        """상위 페르소나로 에스컬레이션 - PM이 결정"""
        
        # 보고 라인 따라 에스컬레이션
        if current_persona.reporting_to:
            return self.persona_pool.get(
                current_persona.reporting_to,
                self.persona_pool[PersonaType.PM]  # 최종적으로 나에게
            )
        
        # 이미 최상위면 PM(나)
        return self.persona_pool[PersonaType.PM]
    
    def delegate_to_subordinate(self, current_persona: Persona, 
                               task_type: str) -> Persona:
        """하위 페르소나로 위임 - PM이 결정"""
        
        # 현재 페르소나의 부하 찾기
        subordinates = []
        for sub_type, sub_persona in self.persona_pool.items():
            if sub_persona.reporting_to == current_persona.type:
                subordinates.append(sub_persona)
        
        # 작업에 적합한 부하 선택
        for sub in subordinates:
            if task_type.lower() in [s.lower() for s in sub.skills]:
                return sub
        
        # 기본값
        return subordinates[0] if subordinates else current_persona
    
    # === PersonaOrchestrationPort 구현 ===
    
    def orchestrate_team_work(self, epic_id: int) -> Dict:
        """팀 단위 작업 오케스트레이션 - PM Claude가 지휘"""
        
        orchestration = {
            'epic_id': epic_id,
            'teams_involved': [],
            'assignments': [],
            'pm_decisions': []
        }
        
        # PM(나)의 결정: 어느 팀이 참여할지
        orchestration['teams_involved'] = ['backend', 'frontend', 'qa']
        
        # 각 팀에 리더 할당
        for team in orchestration['teams_involved']:
            if team == 'backend':
                leader = self.persona_pool[PersonaType.BACKEND_LEAD]
            elif team == 'frontend':
                leader = self.persona_pool[PersonaType.FRONTEND_LEAD]
            elif team == 'qa':
                leader = self.persona_pool[PersonaType.QA_MANAGER]
            else:
                leader = self.persona_pool[PersonaType.PM]
            
            orchestration['assignments'].append({
                'team': team,
                'leader': leader.name,
                'role': leader.role
            })
        
        # PM의 결정 사항 기록
        orchestration['pm_decisions'] = [
            "백엔드팀이 API 구현 담당",
            "프론트엔드팀이 UI 구현 담당",
            "QA팀이 전체 검증 담당",
            "주간 단위로 진행 상황 체크"
        ]
        
        return orchestration
    
    def coordinate_personas(self, personas: List[Persona], 
                          task: str) -> Dict:
        """여러 페르소나 간 조율 - PM Claude가 조율"""
        
        coordination = {
            'task': task,
            'leader': 'PM Claude',  # 나
            'participants': [],
            'workflow': [],
            'communication_plan': []
        }
        
        # 참여자 정리
        for persona in personas:
            coordination['participants'].append({
                'name': persona.name,
                'role': persona.role,
                'responsibility': self._assign_responsibility(persona, task)
            })
        
        # 워크플로우 정의 (PM이 결정)
        coordination['workflow'] = [
            f"{personas[0].name}: 초기 설계",
            f"{personas[1].name if len(personas) > 1 else personas[0].name}: 구현",
            f"{personas[-1].name}: 검토 및 피드백",
            "PM Claude: 최종 승인"
        ]
        
        # 커뮤니케이션 계획
        coordination['communication_plan'] = [
            "일일 스탠드업 미팅",
            "이슈 댓글로 진행 상황 공유",
            "병합 전 PM 리뷰 필수"
        ]
        
        return coordination
    
    def resolve_persona_conflict(self, persona1: Persona, 
                                persona2: Persona, issue: str) -> str:
        """페르소나 간 충돌 해결 - PM Claude가 중재"""
        
        # PM의 중재 로직
        
        # 1. 권한 기반 해결
        if persona1.decision_authority > persona2.decision_authority:
            return f"PM 결정: {persona1.name}의 의견을 따릅니다. (권한 우선)"
        elif persona2.decision_authority > persona1.decision_authority:
            return f"PM 결정: {persona2.name}의 의견을 따릅니다. (권한 우선)"
        
        # 2. 전문성 기반 해결
        if 'backend' in issue.lower() and PersonaType.BACKEND_LEAD in [persona1.type, persona2.type]:
            return "PM 결정: 백엔드 리드의 의견을 따릅니다. (전문성 우선)"
        
        # 3. PM(나)의 최종 결정
        return f"PM 결정: 두 의견을 종합하여 새로운 방향을 제시합니다. 상세 내용은 별도 논의."
    
    def generate_team_report(self, team_name: str) -> Dict:
        """팀 리포트 생성 - PM이 작성"""
        
        report = {
            'team': team_name,
            'prepared_by': 'PM Claude',
            'summary': '',
            'achievements': [],
            'issues': [],
            'next_steps': []
        }
        
        # PM의 팀 평가
        if team_name == 'backend':
            report['summary'] = "백엔드팀은 API 구현을 완료했습니다."
            report['achievements'] = ["API 엔드포인트 10개 구현", "데이터베이스 스키마 설계"]
            report['issues'] = ["성능 최적화 필요"]
            report['next_steps'] = ["부하 테스트 실시", "캐싱 전략 수립"]
            
        elif team_name == 'frontend':
            report['summary'] = "프론트엔드팀은 UI 컴포넌트를 개발 중입니다."
            report['achievements'] = ["컴포넌트 5개 완성", "반응형 디자인 적용"]
            report['issues'] = ["디자인 시스템 미비"]
            report['next_steps'] = ["디자인 시스템 구축", "접근성 개선"]
        
        return report
    
    # === PersonaBehaviorPort 구현 ===
    
    def get_persona_prompt(self, persona: Persona, context: Dict) -> str:
        """페르소나별 프롬프트 생성"""
        
        prompt = f"""당신은 {persona.name}입니다.
역할: {persona.role}
전문 분야: {', '.join(persona.skills)}
커뮤니케이션 스타일: {persona.communication_style}

현재 작업: {context.get('task', '')}

지시사항:
1. 당신의 역할에 맞게 행동하세요
2. {persona.communication_style}하게 소통하세요
3. 결정 권한은 {persona.decision_authority}% 수준입니다
"""
        
        # PM인 경우 특별 지시
        if persona.type == PersonaType.PM:
            prompt += """
4. 팀 전체를 조율하고 관리하세요
5. 최종 의사결정을 내리세요
6. 다른 AI들에게 작업을 할당하세요
"""
        
        return prompt
    
    def apply_communication_style(self, persona: Persona, 
                                 message: str) -> str:
        """페르소나 커뮤니케이션 스타일 적용"""
        
        if persona.type == PersonaType.PM:
            # PM(나)의 스타일: 명확하고 체계적
            return f"""## PM Claude 보고

{message}

### 다음 단계
- 진행 상황 모니터링
- 필요시 개입
- 최종 검토

*- PM Claude*"""
        
        elif persona.type == PersonaType.BACKEND_LEAD:
            # 백엔드 리드: 기술적
            return f"[기술 리뷰] {message}\n\n기술적 관점에서 검토가 필요합니다."
        
        elif persona.type == PersonaType.REVIEWER:
            # 리뷰어: 비판적
            return f"코드 리뷰 의견:\n{message}\n\n개선이 필요한 부분을 지적했습니다."
        
        return message
    
    def make_decision(self, persona: Persona, options: List[str]) -> str:
        """페르소나 권한에 따른 의사결정"""
        
        # 결정 권한 확인
        if persona.decision_authority >= 80:
            # 높은 권한: 독립적 결정
            return f"{persona.name} 결정: {options[0]} (권한: {persona.decision_authority}%)"
        elif persona.decision_authority >= 50:
            # 중간 권한: 조건부 결정
            return f"{persona.name} 제안: {options[0]} (상위 승인 필요)"
        else:
            # 낮은 권한: 보고만
            return f"{persona.name} 보고: 옵션들을 검토했습니다. 상위 결정 대기"
    
    def generate_persona_response(self, persona: Persona, 
                                 situation: str) -> str:
        """페르소나별 응답 생성"""
        
        if persona.type == PersonaType.PM:
            return f"PM으로서 {situation}에 대해 팀 전체 조율이 필요합니다."
        elif persona.type == PersonaType.ARCHITECT:
            return f"아키텍처 관점에서 {situation}의 시스템 영향도를 분석합니다."
        elif persona.type == PersonaType.BACKEND_DEV:
            return f"구현 관점에서 {situation}을 코드로 해결하겠습니다."
        else:
            return f"{persona.role}로서 {situation}을 처리하겠습니다."
    
    # === Helper Methods ===
    
    def _select_ai_for_persona(self, persona: Persona) -> str:
        """페르소나에 적합한 AI 선택 - PM의 판단"""
        
        # PM의 AI 할당 전략
        if persona.type in [PersonaType.ARCHITECT, PersonaType.PM]:
            return 'claude'  # 복잡한 사고가 필요한 역할
        elif persona.type in [PersonaType.BACKEND_DEV, PersonaType.BACKEND_LEAD]:
            return 'codex'  # 백엔드 구현
        elif persona.type in [PersonaType.FRONTEND_DEV, PersonaType.FRONTEND_LEAD]:
            return 'gemini'  # 프론트엔드/디자인
        else:
            return 'claude'  # 기본값
    
    def _get_alternative_personas(self, persona: Persona) -> List[Persona]:
        """대안 페르소나들 - PM이 고려한 다른 옵션"""
        
        alternatives = []
        
        # 같은 팀의 다른 멤버들
        for team_name, team_members in self.organization.teams.items():
            if persona.type in team_members:
                for member_type in team_members:
                    if member_type != persona.type and member_type in self.persona_pool:
                        alternatives.append(self.persona_pool[member_type])
        
        return alternatives[:2]  # 최대 2개
    
    def _generate_assignment_reason(self, persona: Persona, task_id: int) -> str:
        """할당 이유 생성 - PM의 판단 근거"""
        
        reasons = [
            f"{persona.name}의 전문 분야가 이 작업에 적합",
            f"결정 권한 {persona.decision_authority}% 수준이 적절",
            f"{persona.role}이 이 유형의 작업을 담당"
        ]
        
        if persona.type == PersonaType.PM:
            reasons.append("중요도가 높아 PM이 직접 관여 필요")
        
        return ". ".join(reasons)
    
    def _assign_responsibility(self, persona: Persona, task: str) -> str:
        """책임 할당 - PM이 결정"""
        
        if 'design' in task.lower():
            return "설계 및 구조 정의"
        elif 'implement' in task.lower():
            return "코드 구현"
        elif 'review' in task.lower():
            return "검토 및 피드백"
        else:
            return "작업 수행"


# 사용 예시
if __name__ == "__main__":
    adapter = PMClaudePersonaAssignmentAdapter()
    
    # 테스트: Task 분석 및 페르소나 할당
    test_tasks = [
        "복잡한 시스템 아키텍처 설계",
        "간단한 버그 수정",
        "API 엔드포인트 구현",
        "코드 리뷰 수행"
    ]
    
    print("=== PM Claude의 페르소나 할당 ===\n")
    
    for task in test_tasks:
        # 요구사항 분석
        requirements = adapter.analyze_task_requirements(task)
        
        # 페르소나 선택
        persona = adapter.select_persona(requirements)
        
        # AI에게 할당
        assignment = adapter.assign_persona_to_ai(persona, task_id=1)
        
        print(f"Task: {task}")
        print(f"  → 페르소나: {persona.name} ({persona.role})")
        print(f"  → AI: {assignment.ai_name}")
        print(f"  → 이유: {assignment.reason}")
        print()