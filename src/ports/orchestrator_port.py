"""
Orchestrator Port Interface
PM Claude가 정의한 인터페이스 - 구현은 AI 팀이 담당
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime


@dataclass
class Provenance:
    """모든 출력에 포함되어야 하는 메타데이터"""
    source: str  # 'ai' | 'rules' | 'human'
    model: Optional[str] = None  # 'claude' | 'gemini' | 'codex'
    prompt_hash: Optional[str] = None
    timestamp: datetime = None
    version: str = "v2.0"
    adr_reference: Optional[str] = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()


@dataclass
class Task:
    """실행할 작업"""
    id: str
    type: str  # 'analysis' | 'implementation' | 'test' | 'review'
    title: str
    description: str
    assigned_to: Optional[List[str]] = None
    
    
@dataclass
class Result:
    """작업 실행 결과"""
    task_id: str
    success: bool
    output: Any
    meta: Provenance
    errors: Optional[List[str]] = None


class OrchestratorPort(ABC):
    """
    오케스트레이터 포트 인터페이스
    이 인터페이스를 구현하는 Adapter들:
    - AIOrchestrationAdapter: 실제 AI CLI 호출
    - RulesOrchestrationAdapter: AI 없이 규칙 기반 실행
    - MockOrchestrationAdapter: 테스트용
    """
    
    @abstractmethod
    def process_issue(self, issue_number: int) -> Result:
        """GitHub 이슈를 처리"""
        pass
    
    @abstractmethod
    def execute_workflow(self, workflow_name: str, context: Dict) -> Result:
        """워크플로우 실행"""
        pass
    
    @abstractmethod
    def assign_task(self, task: Task) -> Result:
        """작업을 적절한 실행자에게 할당"""
        pass
    
    @abstractmethod
    def get_status(self, task_id: str) -> Dict:
        """작업 상태 조회"""
        pass


class ExecutorPort(ABC):
    """
    실행자 포트 인터페이스
    Node를 실제로 실행하는 주체
    """
    
    @abstractmethod
    def execute(self, command: str, context: Dict) -> Result:
        """명령 실행"""
        pass
    
    @abstractmethod
    def validate(self, result: Result) -> bool:
        """결과 검증"""
        pass
    
    @abstractmethod
    def get_capabilities(self) -> List[str]:
        """실행 가능한 작업 유형"""
        pass


# PM 주석: 이 파일은 인터페이스만 정의합니다.
# 실제 구현은 src/adapters/에서 AI 팀이 작성합니다.
# ADR-001 참조
