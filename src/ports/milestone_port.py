"""
Milestone Port - 마일스톤 관리 인터페이스
마일스톤과 이슈 간 양방향 동기화
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

class MilestoneState(Enum):
    """마일스톤 상태"""
    PLANNING = "planning"        # 계획 중
    ACTIVE = "active"           # 진행 중
    COMPLETED = "completed"     # 완료
    CANCELLED = "cancelled"     # 취소

@dataclass
class Milestone:
    """마일스톤 데이터"""
    id: str
    number: int
    title: str
    description: str
    due_date: Optional[datetime]
    state: MilestoneState
    progress_percentage: int
    issues: List[int]  # 연결된 이슈 번호들
    epics: List[int]   # 연결된 Epic들
    metadata: Dict[str, Any]

@dataclass
class SyncResult:
    """동기화 결과"""
    success: bool
    milestone_to_issues: Dict[str, List[int]]  # 마일스톤 → 이슈
    issues_to_milestone: Dict[int, str]        # 이슈 → 마일스톤
    created_issues: List[int]
    updated_issues: List[int]
    conflicts: List[str]

class MilestonePort(ABC):
    """마일스톤 관리 인터페이스"""
    
    @abstractmethod
    def create_milestone(self, title: str, description: str, 
                        due_date: Optional[datetime]) -> Milestone:
        """마일스톤 생성"""
        pass
    
    @abstractmethod
    def update_milestone(self, milestone_id: str, updates: Dict) -> bool:
        """마일스톤 업데이트"""
        pass
    
    @abstractmethod
    def get_milestone(self, milestone_id: str) -> Optional[Milestone]:
        """마일스톤 조회"""
        pass
    
    @abstractmethod
    def list_milestones(self, state: Optional[MilestoneState] = None) -> List[Milestone]:
        """마일스톤 목록 조회"""
        pass
    
    @abstractmethod
    def calculate_progress(self, milestone_id: str) -> int:
        """마일스톤 진행률 계산"""
        pass

class MilestoneSyncPort(ABC):
    """마일스톤-이슈 동기화 인터페이스"""
    
    @abstractmethod
    def sync_milestone_to_issues(self, milestone_id: str) -> SyncResult:
        """마일스톤 → 이슈 동기화 (마일스톤 기반으로 이슈 생성/업데이트)"""
        pass
    
    @abstractmethod
    def sync_issues_to_milestone(self, issue_ids: List[int]) -> SyncResult:
        """이슈 → 마일스톤 동기화 (이슈 변경사항을 마일스톤에 반영)"""
        pass
    
    @abstractmethod
    def bidirectional_sync(self, milestone_id: str) -> SyncResult:
        """양방향 동기화"""
        pass
    
    @abstractmethod
    def detect_conflicts(self, milestone_id: str) -> List[str]:
        """충돌 감지"""
        pass
    
    @abstractmethod
    def resolve_conflicts(self, conflicts: List[str], strategy: str) -> bool:
        """충돌 해결"""
        pass

class MilestoneTemplatePort(ABC):
    """마일스톤 템플릿 인터페이스"""
    
    @abstractmethod
    def create_from_template(self, template_name: str, context: Dict) -> Milestone:
        """템플릿으로부터 마일스톤 생성"""
        pass
    
    @abstractmethod
    def generate_epic_structure(self, milestone: Milestone) -> Dict:
        """마일스톤에서 Epic 구조 자동 생성"""
        pass
    
    @abstractmethod
    def suggest_issues(self, milestone: Milestone) -> List[Dict]:
        """마일스톤 기반 이슈 제안"""
        pass