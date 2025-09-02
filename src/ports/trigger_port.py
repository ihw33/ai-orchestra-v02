"""
Trigger Port - 트리거 시스템 인터페이스
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class TriggerType(Enum):
    """트리거 타입"""
    KEYWORD = "keyword"
    EVENT = "event"
    TIME = "time"
    CONDITION = "condition"
    PATTERN = "pattern"
    GITHUB_EVENT = "github_event"


@dataclass
class TriggerCondition:
    """트리거 조건"""
    type: TriggerType
    pattern: Optional[str] = None
    keywords: Optional[List[str]] = None
    event_name: Optional[str] = None
    schedule: Optional[str] = None  # cron expression
    custom_check: Optional[Callable] = None


@dataclass
class TriggerContext:
    """트리거 컨텍스트"""
    source: str  # 'github', 'manual', 'schedule', etc.
    data: Dict[str, Any]
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()


@dataclass
class TriggerAction:
    """트리거 액션"""
    name: str
    handler: str  # 'adapter.method' format
    params: Dict[str, Any] = None
    async_execution: bool = False


@dataclass
class TriggerResult:
    """트리거 실행 결과"""
    trigger_name: str
    success: bool
    executed_actions: List[str]
    results: Dict[str, Any]
    error: Optional[str] = None
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()


class TriggerPort(ABC):
    """트리거 시스템 포트 인터페이스"""
    
    @abstractmethod
    def register_trigger(
        self, 
        name: str, 
        condition: TriggerCondition, 
        action: TriggerAction
    ) -> bool:
        """트리거 등록"""
        pass
    
    @abstractmethod
    def unregister_trigger(self, name: str) -> bool:
        """트리거 해제"""
        pass
    
    @abstractmethod
    def check_triggers(self, context: TriggerContext) -> List[str]:
        """조건에 맞는 트리거 확인"""
        pass
    
    @abstractmethod
    def execute_trigger(self, name: str, context: TriggerContext) -> TriggerResult:
        """트리거 실행"""
        pass
    
    @abstractmethod
    def get_trigger_history(self, name: str = None) -> List[TriggerResult]:
        """트리거 실행 이력 조회"""
        pass
    
    @abstractmethod
    def enable_trigger(self, name: str) -> bool:
        """트리거 활성화"""
        pass
    
    @abstractmethod
    def disable_trigger(self, name: str) -> bool:
        """트리거 비활성화"""
        pass