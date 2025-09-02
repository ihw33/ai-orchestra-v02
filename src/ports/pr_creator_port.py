"""
PR Creator Port - Pull Request 관리 인터페이스
PR 생성, 병합, 리뷰 관리를 위한 추상화
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

class PRState(Enum):
    """PR 상태"""
    DRAFT = "draft"
    OPEN = "open"
    CLOSED = "closed"
    MERGED = "merged"

class MergeMethod(Enum):
    """병합 방법"""
    MERGE = "merge"           # 일반 머지
    SQUASH = "squash"        # 스쿼시 머지
    REBASE = "rebase"        # 리베이스 머지

class ReviewState(Enum):
    """리뷰 상태"""
    PENDING = "pending"
    APPROVED = "approved"
    CHANGES_REQUESTED = "changes_requested"
    DISMISSED = "dismissed"

@dataclass
class PullRequest:
    """PR 데이터"""
    number: int
    title: str
    body: str
    state: PRState
    base_branch: str
    head_branch: str
    author: str
    created_at: datetime
    updated_at: datetime
    merged_at: Optional[datetime] = None
    merge_commit_sha: Optional[str] = None
    reviewers: List[str] = None
    labels: List[str] = None
    linked_issues: List[int] = None
    files_changed: int = 0
    additions: int = 0
    deletions: int = 0
    
@dataclass
class PRCreationRequest:
    """PR 생성 요청"""
    title: str
    body: str
    base_branch: str
    head_branch: str
    draft: bool = False
    reviewers: List[str] = None
    assignees: List[str] = None
    labels: List[str] = None
    milestone: Optional[int] = None
    linked_issues: List[int] = None

@dataclass
class MergeRequest:
    """병합 요청"""
    pr_number: int
    merge_method: MergeMethod
    commit_title: Optional[str] = None
    commit_message: Optional[str] = None
    delete_branch: bool = True
    wait_for_checks: bool = True

@dataclass
class PRChain:
    """PR 체인 (Task→Story→Epic→main)"""
    task_pr: Optional[int] = None
    story_pr: Optional[int] = None
    epic_pr: Optional[int] = None
    chain_complete: bool = False
    
class PRCreatorPort(ABC):
    """PR 생성 관리 인터페이스"""
    
    @abstractmethod
    def create_pr(self, request: PRCreationRequest) -> PullRequest:
        """PR 생성"""
        pass
    
    @abstractmethod
    def update_pr(self, pr_number: int, updates: Dict) -> bool:
        """PR 업데이트"""
        pass
    
    @abstractmethod
    def get_pr(self, pr_number: int) -> Optional[PullRequest]:
        """PR 조회"""
        pass
    
    @abstractmethod
    def list_prs(self, state: Optional[PRState] = None, 
                 base: Optional[str] = None) -> List[PullRequest]:
        """PR 목록 조회"""
        pass
    
    @abstractmethod
    def close_pr(self, pr_number: int) -> bool:
        """PR 닫기"""
        pass

class PRMergePort(ABC):
    """PR 병합 관리 인터페이스"""
    
    @abstractmethod
    def merge_pr(self, request: MergeRequest) -> Dict:
        """PR 병합"""
        pass
    
    @abstractmethod
    def can_merge(self, pr_number: int) -> Tuple[bool, str]:
        """병합 가능 여부 확인"""
        pass
    
    @abstractmethod
    def create_merge_chain(self, issue_number: int, issue_type: str) -> PRChain:
        """이슈 타입별 PR 체인 생성 (Task→Story→Epic→main)"""
        pass
    
    @abstractmethod
    def execute_chain_merge(self, chain: PRChain) -> Dict:
        """체인 병합 실행"""
        pass
    
    @abstractmethod
    def rollback_merge(self, merge_commit_sha: str) -> bool:
        """병합 롤백"""
        pass

class PRReviewPort(ABC):
    """PR 리뷰 관리 인터페이스"""
    
    @abstractmethod
    def request_review(self, pr_number: int, reviewers: List[str]) -> bool:
        """리뷰 요청"""
        pass
    
    @abstractmethod
    def approve_pr(self, pr_number: int, comment: Optional[str] = None) -> bool:
        """PR 승인"""
        pass
    
    @abstractmethod
    def request_changes(self, pr_number: int, comment: str) -> bool:
        """변경 요청"""
        pass
    
    @abstractmethod
    def get_review_status(self, pr_number: int) -> Dict:
        """리뷰 상태 조회"""
        pass
    
    @abstractmethod
    def auto_assign_reviewers(self, pr_number: int) -> List[str]:
        """자동 리뷰어 할당"""
        pass

class BranchStrategyPort(ABC):
    """브랜치 전략 관리 인터페이스"""
    
    @abstractmethod
    def create_branch(self, branch_name: str, base_branch: str) -> bool:
        """브랜치 생성"""
        pass
    
    @abstractmethod
    def delete_branch(self, branch_name: str, force: bool = False) -> bool:
        """브랜치 삭제"""
        pass
    
    @abstractmethod
    def generate_branch_name(self, issue_type: str, issue_number: int, 
                           title: str) -> str:
        """이슈 기반 브랜치명 생성"""
        pass
    
    @abstractmethod
    def determine_base_branch(self, issue_type: str, 
                            parent_issue: Optional[int]) -> str:
        """베이스 브랜치 결정"""
        pass
    
    @abstractmethod
    def protect_branch(self, branch_name: str, rules: Dict) -> bool:
        """브랜치 보호 규칙 설정"""
        pass
    
    @abstractmethod
    def get_branch_hierarchy(self) -> Dict:
        """브랜치 계층 구조 조회"""
        pass