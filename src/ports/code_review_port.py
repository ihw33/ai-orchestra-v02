"""
Code Review Port - 코드 리뷰 워크플로우 인터페이스
AI 기반 자동 코드 리뷰 시스템
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
from datetime import datetime

class ReviewStatus(Enum):
    """리뷰 상태"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    APPROVED = "approved"
    CHANGES_REQUESTED = "changes_requested"
    DISMISSED = "dismissed"

class ReviewSeverity(Enum):
    """리뷰 지적 심각도"""
    CRITICAL = "critical"      # 반드시 수정
    MAJOR = "major"            # 중요 개선사항
    MINOR = "minor"            # 사소한 개선
    SUGGESTION = "suggestion"  # 제안사항

class ReviewCategory(Enum):
    """리뷰 카테고리"""
    SECURITY = "security"              # 보안 취약점
    PERFORMANCE = "performance"        # 성능 이슈
    CODE_QUALITY = "code_quality"      # 코드 품질
    ARCHITECTURE = "architecture"      # 아키텍처
    TESTING = "testing"                # 테스트
    DOCUMENTATION = "documentation"    # 문서화
    STYLE = "style"                    # 코드 스타일

@dataclass
class ReviewComment:
    """리뷰 코멘트"""
    file_path: str
    line_number: int
    comment: str
    severity: ReviewSeverity
    category: ReviewCategory
    suggested_fix: Optional[str] = None
    code_snippet: Optional[str] = None

@dataclass
class ReviewResult:
    """리뷰 결과"""
    pr_number: int
    reviewer: str  # AI 또는 사람
    status: ReviewStatus
    comments: List[ReviewComment]
    summary: str
    score: Optional[int] = None  # 0-100
    reviewed_at: Optional[datetime] = None
    time_taken: Optional[int] = None  # 초 단위

@dataclass
class ReviewChecklist:
    """리뷰 체크리스트"""
    security_checks: List[str]
    performance_checks: List[str]
    quality_checks: List[str]
    architecture_checks: List[str]
    test_checks: List[str]

@dataclass
class ReviewRequest:
    """리뷰 요청"""
    pr_number: int
    requester: str
    reviewer: str  # AI 이름 또는 사람
    focus_areas: List[ReviewCategory]  # 집중 검토 영역
    use_superclaude: bool = False  # /SC Review 사용 여부
    use_subagent: bool = True  # 서브에이전트 사용 여부
    checklist: Optional[ReviewChecklist] = None

class CodeReviewPort(ABC):
    """코드 리뷰 인터페이스"""
    
    @abstractmethod
    def request_review(self, request: ReviewRequest) -> bool:
        """코드 리뷰 요청"""
        pass
    
    @abstractmethod
    def perform_review(self, pr_number: int, reviewer: str) -> ReviewResult:
        """코드 리뷰 수행"""
        pass
    
    @abstractmethod
    def get_review_checklist(self, pr_type: str) -> ReviewChecklist:
        """PR 타입별 리뷰 체크리스트"""
        pass
    
    @abstractmethod
    def analyze_code_changes(self, pr_number: int) -> Dict:
        """코드 변경사항 분석"""
        pass
    
    @abstractmethod
    def generate_review_comments(self, analysis: Dict) -> List[ReviewComment]:
        """리뷰 코멘트 생성"""
        pass
    
    @abstractmethod
    def post_review_comments(self, pr_number: int, comments: List[ReviewComment]) -> bool:
        """리뷰 코멘트 게시"""
        pass
    
    @abstractmethod
    def approve_pr(self, pr_number: int, comment: str) -> bool:
        """PR 승인"""
        pass
    
    @abstractmethod
    def request_changes(self, pr_number: int, comments: List[ReviewComment]) -> bool:
        """변경 요청"""
        pass

class ReviewAutomationPort(ABC):
    """리뷰 자동화 인터페이스"""
    
    @abstractmethod
    def auto_assign_reviewer(self, pr_number: int) -> str:
        """자동 리뷰어 할당"""
        pass
    
    @abstractmethod
    def should_auto_review(self, pr_number: int) -> bool:
        """자동 리뷰 필요 여부 판단"""
        pass
    
    @abstractmethod
    def trigger_review_workflow(self, pr_number: int) -> Dict:
        """리뷰 워크플로우 트리거"""
        pass
    
    @abstractmethod
    def handle_review_feedback(self, pr_number: int, feedback: ReviewResult) -> Dict:
        """리뷰 피드백 처리"""
        pass
    
    @abstractmethod
    def track_review_metrics(self, pr_number: int) -> Dict:
        """리뷰 메트릭 추적"""
        pass

class ReviewAIIntegrationPort(ABC):
    """AI 리뷰어 통합 인터페이스"""
    
    @abstractmethod
    def select_ai_reviewer(self, pr_content: Dict) -> Tuple[str, str]:
        """AI 리뷰어 선택 (AI 이름, 명령어/서브에이전트)"""
        pass
    
    @abstractmethod
    def format_review_prompt(self, pr_data: Dict, reviewer_type: str) -> str:
        """리뷰 프롬프트 생성"""
        pass
    
    @abstractmethod
    def execute_ai_review(self, reviewer: str, prompt: str, 
                         use_sc: bool = False) -> ReviewResult:
        """AI 리뷰 실행"""
        pass
    
    @abstractmethod
    def parse_ai_review_output(self, output: str, reviewer: str) -> ReviewResult:
        """AI 리뷰 출력 파싱"""
        pass
    
    @abstractmethod
    def cross_check_reviews(self, reviews: List[ReviewResult]) -> ReviewResult:
        """여러 AI 리뷰 교차 검증"""
        pass