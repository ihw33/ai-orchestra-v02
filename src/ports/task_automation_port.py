"""
Task Automation Port - Task 자동 생성 및 AI 할당 인터페이스
Story에서 Task를 자동 생성하고 AI에게 할당
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

class TaskType(Enum):
    """Task 유형"""
    INTERFACE_DESIGN = "interface_design"  # Port 정의
    IMPLEMENTATION = "implementation"       # Adapter 구현
    TESTING = "testing"                   # 테스트
    DOCUMENTATION = "documentation"       # 문서화
    INTEGRATION = "integration"           # 통합

class AIAssignment(Enum):
    """AI 할당"""
    GEMINI = "gemini"    # 설계, 분석
    CLAUDE = "claude"    # 구현, 리뷰
    CODEX = "codex"      # 백엔드, API

@dataclass
class TaskTemplate:
    """Task 템플릿"""
    title: str
    description: str
    task_type: TaskType
    assigned_ai: AIAssignment
    estimated_hours: int
    dependencies: List[str] = None

@dataclass
class AutoTaskResult:
    """자동 Task 생성 결과"""
    story_id: int
    created_tasks: List[int]
    ai_assignments: Dict[int, str]  # task_id -> ai_name
    persona_assignments: Dict[int, str]  # task_id -> persona_id
    success: bool
    errors: List[str] = None

class TaskAutomationPort(ABC):
    """Task 자동화 인터페이스"""
    
    @abstractmethod
    def analyze_story(self, story_id: int) -> List[TaskTemplate]:
        """Story 분석하여 필요한 Task 도출"""
        pass
    
    @abstractmethod
    def create_tasks_from_story(self, story_id: int) -> AutoTaskResult:
        """Story에서 Task 자동 생성"""
        pass
    
    @abstractmethod
    def assign_ai_to_task(self, task_id: int, task_content: str) -> Tuple[str, str]:
        """Task에 적합한 AI와 페르소나 할당"""
        pass
    
    @abstractmethod
    def trigger_ai_execution(self, task_id: int, ai_name: str, 
                            persona_id: str) -> bool:
        """AI 실행 트리거"""
        pass
    
    @abstractmethod
    def monitor_task_progress(self, task_id: int) -> Dict:
        """Task 진행 상황 모니터링"""
        pass
    
    @abstractmethod
    def collect_ai_results(self, task_id: int) -> Dict:
        """AI 작업 결과 수집"""
        pass