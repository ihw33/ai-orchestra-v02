"""
Label Management Port - 라벨 관리 인터페이스
GitHub 라벨 생성, 업데이트, 매핑 관리
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Set
from dataclasses import dataclass
from enum import Enum

class LabelCategory(Enum):
    """라벨 카테고리"""
    ISSUE_TYPE = "issue_type"      # epic, story, task
    AI_ASSIGNMENT = "ai"           # ai-gemini, ai-claude, ai-codex
    PRIORITY = "priority"          # p0, p1, p2
    STATUS = "status"              # in-progress, blocked, review
    WORKFLOW = "workflow"          # automated, manual
    
@dataclass
class Label:
    """라벨 데이터"""
    name: str
    color: str
    description: str
    category: LabelCategory
    auto_create: bool = True  # 자동 생성 여부

@dataclass
class LabelRule:
    """라벨 적용 규칙"""
    pattern: str  # 제목/본문 패턴
    labels: List[str]  # 적용할 라벨들
    confidence: float  # 확신도

class LabelManagementPort(ABC):
    """라벨 관리 인터페이스"""
    
    @abstractmethod
    def ensure_label_exists(self, label_name: str) -> bool:
        """라벨이 존재하는지 확인하고 없으면 생성"""
        pass
    
    @abstractmethod
    def create_label(self, label: Label) -> bool:
        """라벨 생성"""
        pass
    
    @abstractmethod
    def update_label(self, old_name: str, new_label: Label) -> bool:
        """라벨 업데이트"""
        pass
    
    @abstractmethod
    def delete_label(self, label_name: str) -> bool:
        """라벨 삭제"""
        pass
    
    @abstractmethod
    def get_all_labels(self) -> List[Label]:
        """모든 라벨 조회"""
        pass
    
    @abstractmethod
    def suggest_labels(self, issue_title: str, issue_body: str) -> List[str]:
        """이슈 내용 기반 라벨 제안"""
        pass
    
    @abstractmethod
    def apply_labels(self, issue_number: int, labels: List[str]) -> bool:
        """이슈에 라벨 적용"""
        pass
    
    @abstractmethod
    def sync_labels(self) -> Dict:
        """프로젝트 표준 라벨과 동기화"""
        pass