#!/usr/bin/env python3
"""
서브에이전트 자동 선택 시스템
작업 유형과 페르소나에 따라 최적의 서브에이전트를 자동으로 선택
"""

import re
from typing import Optional, Dict, Tuple

class SubagentSelector:
    """서브에이전트 자동 선택기"""
    
    def __init__(self):
        # 키워드 → 서브에이전트 매핑
        self.keyword_mapping = {
            # Backend/Architecture
            r'(api|API|백엔드|backend|서버|server|데이터베이스|db|DB)': 'backend-architect',
            
            # UI/UX
            r'(UI|UX|디자인|design|인터페이스|interface|화면|프론트|frontend)': 'ui-ux-designer',
            
            # Business/Analytics
            r'(분석|analysis|KPI|메트릭|metric|비즈니스|business|성장|growth)': 'business-analyst',
            
            # AI/ML
            r'(AI|인공지능|LLM|GPT|RAG|머신러닝|ML|프롬프트|prompt)': 'ai-engineer',
            
            # Search/Research
            r'(검색|search|리서치|research|조사|investigate|경쟁|competitor)': 'search-specialist',
            
            # Documentation
            r'(문서|document|API스펙|swagger|openapi|SDK|readme)': 'api-documenter',
            
            # IWL specific
            r'(IWL|IdeaWorkLab|아이디어워크랩)': 'iwl-code-reviewer',
            
            # Prompt optimization
            r'(프롬프트최적화|prompt.?engineer|프롬프트개선)': 'prompt-engineer'
        }
        
        # 페르소나 → 서브에이전트 매핑
        self.persona_mapping = {
            # Backend Team
            'backend_lead_01': 'backend-architect',
            '김정호': 'backend-architect',
            'backend_lead': 'backend-architect',
            'senior_api': 'backend-architect',
            'db_architect': 'backend-architect',
            
            # Frontend Team
            'frontend_lead_01': 'ui-ux-designer',
            'Maria': 'ui-ux-designer',
            'maria_silva': 'ui-ux-designer',
            'frontend_lead': 'ui-ux-designer',
            'ui_dev': 'ui-ux-designer',
            
            # QA Team
            'qa_lead_01': 'search-specialist',
            '박민수': 'search-specialist',
            'qa_lead': 'search-specialist',
            
            # Business/Product
            'product_manager': 'business-analyst',
            'data_analyst': 'business-analyst',
            'business_analyst': 'business-analyst',
            
            # AI/ML Team
            'ml_engineer': 'ai-engineer',
            'ai_specialist': 'ai-engineer',
            'prompt_engineer': 'prompt-engineer',
            
            # Documentation
            'tech_writer': 'api-documenter',
            'documentation_lead': 'api-documenter'
        }
    
    def select(self, task: str, persona: Optional[str] = None) -> Tuple[str, str]:
        """
        작업과 페르소나에 따라 최적 서브에이전트 선택
        
        Returns:
            (subagent_type, reason): 선택된 에이전트와 이유
        """
        
        # 1. 페르소나 기반 선택 (우선순위 높음)
        if persona:
            # 페르소나 이름 정규화
            normalized_persona = persona.lower().replace(' ', '_')
            
            # 직접 매핑 확인
            if normalized_persona in self.persona_mapping:
                return (
                    self.persona_mapping[normalized_persona],
                    f"페르소나 '{persona}'에 최적화된 에이전트"
                )
            
            # 부분 매칭
            for key, agent in self.persona_mapping.items():
                if key in normalized_persona or normalized_persona in key:
                    return (
                        agent,
                        f"페르소나 '{persona}'와 연관된 에이전트"
                    )
        
        # 2. 작업 키워드 기반 선택
        task_lower = task.lower()
        
        for pattern, agent in self.keyword_mapping.items():
            if re.search(pattern, task_lower, re.IGNORECASE):
                keywords = re.findall(pattern, task_lower, re.IGNORECASE)
                return (
                    agent,
                    f"키워드 '{', '.join(keywords)}'에 적합한 에이전트"
                )
        
        # 3. 기본값
        return ('general-purpose', '특정 패턴 없음 - 범용 에이전트 사용')
    
    def get_agent_description(self, agent_type: str) -> str:
        """서브에이전트 설명 반환"""
        descriptions = {
            'backend-architect': 'RESTful API, 마이크로서비스, 데이터베이스 설계 전문',
            'ui-ux-designer': '인터페이스 디자인, 사용자 경험, 디자인 시스템 전문',
            'business-analyst': '메트릭 분석, KPI 추적, 비즈니스 인사이트 도출',
            'ai-engineer': 'LLM 통합, RAG 시스템, AI 파이프라인 구축',
            'search-specialist': '고급 검색, 정보 수집, 경쟁 분석',
            'api-documenter': 'OpenAPI 스펙, SDK 생성, 개발자 문서화',
            'iwl-code-reviewer': 'IdeaWorkLab 프로젝트 전문 코드 리뷰',
            'prompt-engineer': 'AI 프롬프트 최적화, 성능 개선',
            'general-purpose': '복잡한 다단계 작업 처리, 범용 문제 해결'
        }
        return descriptions.get(agent_type, '일반 작업 처리')
    
    def suggest_team(self, task: str) -> Dict[str, str]:
        """작업에 적합한 팀 구성 제안"""
        
        task_lower = task.lower()
        
        # API 개발 팀
        if any(word in task_lower for word in ['api', '백엔드', 'backend']):
            return {
                '설계': 'backend-architect',
                '구현': 'general-purpose',
                '문서화': 'api-documenter'
            }
        
        # UI 개발 팀
        elif any(word in task_lower for word in ['ui', 'ux', '디자인', 'frontend']):
            return {
                '디자인': 'ui-ux-designer',
                '구현': 'general-purpose',
                '리뷰': 'search-specialist'
            }
        
        # 분석 팀
        elif any(word in task_lower for word in ['분석', 'analysis', 'metric']):
            return {
                '데이터수집': 'search-specialist',
                '분석': 'business-analyst',
                '시각화': 'ui-ux-designer'
            }
        
        # AI/ML 팀
        elif any(word in task_lower for word in ['ai', 'llm', 'rag']):
            return {
                '설계': 'ai-engineer',
                '프롬프트': 'prompt-engineer',
                '테스트': 'search-specialist'
            }
        
        # 기본 팀
        return {
            '기획': 'business-analyst',
            '구현': 'general-purpose',
            '검증': 'search-specialist'
        }


def auto_select_subagent(task: str, persona: Optional[str] = None) -> str:
    """간편 사용을 위한 헬퍼 함수"""
    selector = SubagentSelector()
    agent_type, reason = selector.select(task, persona)
    
    print(f"📌 작업: {task[:50]}...")
    print(f"🤖 선택된 에이전트: {agent_type}")
    print(f"💡 이유: {reason}")
    print(f"📝 설명: {selector.get_agent_description(agent_type)}")
    
    return agent_type


def test_selector():
    """선택기 테스트"""
    print("="*50)
    print("🧪 서브에이전트 선택기 테스트")
    print("="*50)
    
    selector = SubagentSelector()
    
    # 테스트 케이스
    test_cases = [
        ("API 설계해줘", "김정호"),
        ("대시보드 UI 디자인", "Maria Silva"),
        ("버그 검색 및 수정", "박민수"),
        ("KPI 메트릭 분석", None),
        ("RAG 시스템 구축", None),
        ("API 문서 작성", None),
        ("일반적인 작업", None)
    ]
    
    for task, persona in test_cases:
        print(f"\n📋 작업: {task}")
        if persona:
            print(f"👤 페르소나: {persona}")
        
        agent, reason = selector.select(task, persona)
        print(f"→ 에이전트: {agent}")
        print(f"→ 이유: {reason}")
        
        # 팀 구성 제안
        team = selector.suggest_team(task)
        if len(team) > 1:
            print(f"→ 팀 제안: {team}")


if __name__ == "__main__":
    test_selector()