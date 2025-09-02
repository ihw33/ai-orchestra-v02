"""
Persona Assignment Port - 페르소나 할당 인터페이스
AI에게 적절한 페르소나를 할당하는 시스템
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

class PersonaType(Enum):
    """페르소나 유형"""
    # 경영진
    CEO = "ceo"
    CTO = "cto"
    CPO = "cpo"
    
    # 관리자
    PM = "project_manager"
    ENGINEERING_MANAGER = "engineering_manager"
    QA_MANAGER = "qa_manager"
    DESIGN_DIRECTOR = "design_director"
    
    # 팀 리드
    BACKEND_LEAD = "backend_lead"
    FRONTEND_LEAD = "frontend_lead"
    DEVOPS_LEAD = "devops_lead"
    DATA_LEAD = "data_lead"
    
    # 개발자
    BACKEND_DEV = "backend_developer"
    FRONTEND_DEV = "frontend_developer"
    FULLSTACK_DEV = "fullstack_developer"
    
    # 전문가
    ARCHITECT = "architect"
    SECURITY_EXPERT = "security_expert"
    PERFORMANCE_EXPERT = "performance_expert"
    
    # 테스터 (확장됨)
    REVIEWER = "reviewer"
    TESTER = "tester"
    DEVIL_ADVOCATE = "devil_advocate"  # 문제점 찾기 전문가
    CHAOS_ENGINEER = "chaos_engineer"  # 카오스 엔지니어링
    PENETRATION_TESTER = "penetration_tester"  # 보안 침투 테스터
    PERFORMANCE_TESTER = "performance_tester"  # 성능 테스터
    
    # 기타
    DOCUMENTER = "documenter"

@dataclass
class Persona:
    """페르소나 정의"""
    type: PersonaType
    name: str
    role: str
    skills: List[str]
    reporting_to: Optional[PersonaType]  # 상사
    communication_style: str
    decision_authority: int  # 0-100 결정 권한
    
@dataclass
class PersonaAssignment:
    """페르소나 할당"""
    task_id: int
    persona: Persona
    ai_name: str  # claude, gemini, codex
    reason: str  # 할당 이유
    alternatives: List[Persona]  # 대안 페르소나들

@dataclass
class OrganizationStructure:
    """조직 구조"""
    hierarchy: Dict[PersonaType, List[PersonaType]]  # 상하 관계
    teams: Dict[str, List[PersonaType]]  # 팀 구성
    reporting_lines: Dict[PersonaType, PersonaType]  # 보고 라인

class PersonaAssignmentPort(ABC):
    """페르소나 할당 인터페이스"""
    
    @abstractmethod
    def analyze_task_requirements(self, task_description: str) -> Dict:
        """Task 요구사항 분석"""
        pass
    
    @abstractmethod
    def select_persona(self, requirements: Dict) -> Persona:
        """요구사항에 맞는 페르소나 선택"""
        pass
    
    @abstractmethod
    def assign_persona_to_ai(self, persona: Persona, task_id: int) -> PersonaAssignment:
        """AI에게 페르소나 할당"""
        pass
    
    @abstractmethod
    def get_persona_hierarchy(self) -> OrganizationStructure:
        """조직 계층 구조 조회"""
        pass
    
    @abstractmethod
    def escalate_to_superior(self, current_persona: Persona) -> Persona:
        """상위 페르소나로 에스컬레이션"""
        pass
    
    @abstractmethod
    def delegate_to_subordinate(self, current_persona: Persona, 
                               task_type: str) -> Persona:
        """하위 페르소나로 위임"""
        pass

class PersonaOrchestrationPort(ABC):
    """페르소나 오케스트레이션 인터페이스"""
    
    @abstractmethod
    def orchestrate_team_work(self, epic_id: int) -> Dict:
        """팀 단위 작업 오케스트레이션"""
        pass
    
    @abstractmethod
    def coordinate_personas(self, personas: List[Persona], 
                          task: str) -> Dict:
        """여러 페르소나 간 조율"""
        pass
    
    @abstractmethod
    def resolve_persona_conflict(self, persona1: Persona, 
                                persona2: Persona, issue: str) -> str:
        """페르소나 간 충돌 해결"""
        pass
    
    @abstractmethod
    def generate_team_report(self, team_name: str) -> Dict:
        """팀 리포트 생성"""
        pass

class PersonaBehaviorPort(ABC):
    """페르소나 행동 인터페이스"""
    
    @abstractmethod
    def get_persona_prompt(self, persona: Persona, context: Dict) -> str:
        """페르소나별 프롬프트 생성"""
        pass
    
    @abstractmethod
    def apply_communication_style(self, persona: Persona, 
                                 message: str) -> str:
        """페르소나 커뮤니케이션 스타일 적용"""
        pass
    
    @abstractmethod
    def make_decision(self, persona: Persona, options: List[str]) -> str:
        """페르소나 권한에 따른 의사결정"""
        pass
    
    @abstractmethod
    def generate_persona_response(self, persona: Persona, 
                                 situation: str) -> str:
        """페르소나별 응답 생성"""
        pass