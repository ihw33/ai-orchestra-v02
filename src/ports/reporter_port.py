"""
Reporter Port - 보고 시스템 인터페이스
모든 보고 활동의 경계 정의
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

class ReportType(Enum):
    """보고 유형"""
    PROGRESS = "progress"       # 진행 상황
    COMPLETION = "completion"    # 완료 보고
    ERROR = "error"             # 에러 보고
    SUMMARY = "summary"         # 요약 보고
    ESCALATION = "escalation"   # 에스컬레이션

@dataclass
class Report:
    """보고서 데이터 모델"""
    id: str
    type: ReportType
    target_id: str  # Issue 번호 또는 작업 ID
    title: str
    content: str
    metadata: Dict[str, Any]
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()

@dataclass
class ReportResult:
    """보고 결과"""
    success: bool
    report_id: str
    url: Optional[str] = None  # GitHub 댓글 URL 등
    errors: Optional[List[str]] = None

class ReporterPort(ABC):
    """보고 시스템 Port 인터페이스"""
    
    @abstractmethod
    def report_progress(self, target_id: str, progress: Dict) -> ReportResult:
        """진행 상황 보고"""
        pass
    
    @abstractmethod
    def report_completion(self, target_id: str, results: Dict) -> ReportResult:
        """작업 완료 보고"""
        pass
    
    @abstractmethod
    def report_error(self, target_id: str, error: Dict) -> ReportResult:
        """에러 보고"""
        pass
    
    @abstractmethod
    def generate_summary(self, target_id: str, data: Dict) -> Report:
        """요약 보고서 생성"""
        pass
    
    @abstractmethod
    def should_report(self, event_type: str, context: Dict) -> bool:
        """보고 필요 여부 판단"""
        pass

class ReportFormatterPort(ABC):
    """보고서 포맷터 인터페이스"""
    
    @abstractmethod
    def format_progress(self, data: Dict) -> str:
        """진행 상황 포맷팅"""
        pass
    
    @abstractmethod
    def format_completion(self, data: Dict) -> str:
        """완료 보고 포맷팅"""
        pass
    
    @abstractmethod
    def format_error(self, data: Dict) -> str:
        """에러 보고 포맷팅"""
        pass