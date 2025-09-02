"""
Orchestration Port - 오케스트레이션 시스템 인터페이스
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class ExecutionMode(Enum):
    """실행 모드"""
    SEQUENTIAL = "sequential"
    PARALLEL = "parallel"
    PIPELINE = "pipeline"
    DAG = "dag"


class TaskStatus(Enum):
    """태스크 상태"""
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class Task:
    """오케스트레이션 태스크"""
    id: str
    name: str
    executor: str  # AI name or adapter
    command: str
    params: Dict[str, Any] = None
    dependencies: List[str] = None  # Task IDs
    timeout: int = 300  # seconds
    retry_count: int = 0
    max_retries: int = 3
    
    def __post_init__(self):
        if self.dependencies is None:
            self.dependencies = []
        if self.params is None:
            self.params = {}


@dataclass
class TaskResult:
    """태스크 실행 결과"""
    task_id: str
    status: TaskStatus
    output: Any = None
    error: Optional[str] = None
    start_time: datetime = None
    end_time: datetime = None
    duration: float = None
    
    def __post_init__(self):
        if self.start_time and self.end_time:
            self.duration = (self.end_time - self.start_time).total_seconds()


@dataclass
class WorkflowDefinition:
    """워크플로우 정의"""
    name: str
    tasks: List[Task]
    mode: ExecutionMode = ExecutionMode.SEQUENTIAL
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


@dataclass
class WorkflowExecution:
    """워크플로우 실행 상태"""
    workflow_name: str
    execution_id: str
    status: TaskStatus
    task_results: Dict[str, TaskResult]
    start_time: datetime
    end_time: Optional[datetime] = None
    context: Dict[str, Any] = None
    
    @property
    def duration(self) -> Optional[float]:
        if self.start_time and self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        return None
    
    @property
    def success_rate(self) -> float:
        if not self.task_results:
            return 0.0
        success_count = sum(1 for r in self.task_results.values() 
                          if r.status == TaskStatus.SUCCESS)
        return success_count / len(self.task_results)


class OrchestrationPort(ABC):
    """오케스트레이션 포트 인터페이스"""
    
    @abstractmethod
    def create_workflow(self, definition: WorkflowDefinition) -> str:
        """워크플로우 생성"""
        pass
    
    @abstractmethod
    def execute_workflow(
        self, 
        workflow_name: str, 
        context: Dict[str, Any] = None
    ) -> WorkflowExecution:
        """워크플로우 실행"""
        pass
    
    @abstractmethod
    def execute_task(self, task: Task, context: Dict[str, Any] = None) -> TaskResult:
        """단일 태스크 실행"""
        pass
    
    @abstractmethod
    def get_workflow_status(self, execution_id: str) -> WorkflowExecution:
        """워크플로우 상태 조회"""
        pass
    
    @abstractmethod
    def cancel_workflow(self, execution_id: str) -> bool:
        """워크플로우 취소"""
        pass
    
    @abstractmethod
    def retry_task(self, execution_id: str, task_id: str) -> TaskResult:
        """태스크 재시도"""
        pass
    
    @abstractmethod
    def list_workflows(self) -> List[str]:
        """등록된 워크플로우 목록"""
        pass