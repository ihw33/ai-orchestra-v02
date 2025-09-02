"""
PM Processor Port - PM 자동 처리 인터페이스
"""

from abc import ABC, abstractmethod
from typing import Dict, Optional, List
from dataclasses import dataclass
from datetime import datetime


@dataclass
class Issue:
    """이슈 도메인 모델"""
    number: int
    title: str
    body: str
    labels: List[str]
    state: str
    created_at: datetime
    assignees: List[str] = None
    
    @property
    def needs_ai(self) -> bool:
        """AI 처리가 필요한지 확인"""
        return '[AI]' in self.title or 'ai-task' in self.labels
    
    @property
    def is_processed(self) -> bool:
        """이미 처리되었는지 확인"""
        return 'ai-processed' in self.labels


@dataclass
class ProcessingResult:
    """처리 결과"""
    success: bool
    issue_number: int
    message: str
    ai_responses: Dict[str, str] = None
    error: str = None
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()


class PMProcessorPort(ABC):
    """PM 프로세서 포트 인터페이스"""
    
    @abstractmethod
    def get_latest_issues(self, limit: int = 1) -> List[Issue]:
        """최신 이슈 가져오기"""
        pass
    
    @abstractmethod
    def process_issue(self, issue: Issue) -> ProcessingResult:
        """이슈 처리"""
        pass
    
    @abstractmethod
    def mark_as_processed(self, issue_number: int) -> bool:
        """이슈를 처리됨으로 표시"""
        pass
    
    @abstractmethod
    def post_comment(self, issue_number: int, comment: str) -> bool:
        """이슈에 코멘트 추가"""
        pass