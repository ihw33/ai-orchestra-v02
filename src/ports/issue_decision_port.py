"""
Issue Decision Port - 이슈 생성 판단 인터페이스
대화 내용을 분석하여 이슈 생성 필요 여부를 결정
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

class IssueType(Enum):
    """이슈 유형"""
    AI_TASK = "ai-task"          # AI가 작업
    BUG = "bug"                   # 버그 수정
    FEATURE = "feature"           # 새 기능
    ENHANCEMENT = "enhancement"   # 개선
    QUESTION = "question"         # 질문
    DISCUSSION = "discussion"     # 논의

class Confidence(Enum):
    """판단 확신도"""
    HIGH = "high"           # 90% 이상 - 묻지 않고 진행
    MEDIUM = "medium"       # 60-90% - 상황에 따라 확인
    LOW = "low"            # 60% 미만 - 반드시 확인

@dataclass
class DecisionResult:
    """이슈 생성 판단 결과"""
    should_create: bool
    confidence: Confidence
    issue_type: Optional[IssueType]
    reason: str
    suggested_title: Optional[str] = None
    suggested_labels: Optional[List[str]] = None
    needs_confirmation: bool = False
    confirmation_message: Optional[str] = None

class IssueDecisionPort(ABC):
    """이슈 생성 판단 인터페이스"""
    
    @abstractmethod
    def analyze_conversation(self, message: str, context: Dict) -> DecisionResult:
        """대화 분석하여 이슈 생성 필요 여부 판단"""
        pass
    
    @abstractmethod
    def generate_confirmation_prompt(self, decision: DecisionResult) -> str:
        """사용자 확인이 필요한 경우 확인 메시지 생성"""
        pass
    
    @abstractmethod
    def classify_intent(self, message: str) -> Tuple[str, float]:
        """사용자 의도 분류 (intent, confidence)"""
        pass
    
    @abstractmethod
    def extract_requirements(self, message: str) -> Dict:
        """메시지에서 요구사항 추출"""
        pass

class IssueCreatorPort(ABC):
    """이슈 생성 인터페이스"""
    
    @abstractmethod
    def create_issue(self, title: str, body: str, labels: List[str]) -> Dict:
        """이슈 생성"""
        pass
    
    @abstractmethod
    def update_issue(self, issue_number: int, updates: Dict) -> Dict:
        """이슈 업데이트"""
        pass
    
    @abstractmethod
    def close_issue(self, issue_number: int, reason: str) -> Dict:
        """이슈 종료"""
        pass
    
    @abstractmethod
    def format_issue_body(self, requirements: Dict, persona_style: Optional[str] = None) -> str:
        """이슈 본문 포맷팅"""
        pass