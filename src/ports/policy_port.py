"""
Policy Port - 정책 관리 인터페이스
모든 정책 결정과 적용을 위한 추상화
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum

class PolicyType(Enum):
    """정책 유형"""
    ISSUE_HIERARCHY = "issue_hierarchy"      # 이슈 계층 구조
    BRANCHING = "branching"                  # 브랜치 전략
    LABELING = "labeling"                    # 라벨 체계
    PR_RULES = "pr_rules"                    # PR 규칙
    AI_ASSIGNMENT = "ai_assignment"          # AI 할당 규칙

@dataclass
class PolicyRule:
    """정책 규칙"""
    id: str
    type: PolicyType
    name: str
    description: str
    conditions: Dict[str, Any]  # 적용 조건
    actions: Dict[str, Any]      # 실행 액션
    priority: int = 0            # 우선순위 (충돌 시)
    enabled: bool = True

@dataclass
class PolicyDecision:
    """정책 결정 결과"""
    policy_id: str
    decision: str
    reasoning: str
    confidence: float
    applied_rules: List[PolicyRule]
    metadata: Optional[Dict] = None

class PolicyPort(ABC):
    """정책 관리 인터페이스"""
    
    @abstractmethod
    def evaluate_policy(self, policy_type: PolicyType, context: Dict) -> PolicyDecision:
        """정책 평가 - 주어진 컨텍스트에서 어떤 정책 적용할지 결정"""
        pass
    
    @abstractmethod
    def apply_policy(self, decision: PolicyDecision) -> Dict:
        """정책 적용 - 결정된 정책을 실제로 실행"""
        pass
    
    @abstractmethod
    def get_policy_rules(self, policy_type: PolicyType) -> List[PolicyRule]:
        """특정 유형의 모든 정책 규칙 조회"""
        pass
    
    @abstractmethod
    def add_policy_rule(self, rule: PolicyRule) -> bool:
        """새로운 정책 규칙 추가"""
        pass
    
    @abstractmethod
    def update_policy_rule(self, rule_id: str, updates: Dict) -> bool:
        """기존 정책 규칙 수정"""
        pass
    
    @abstractmethod
    def validate_against_policy(self, policy_type: PolicyType, data: Dict) -> Dict:
        """데이터가 정책을 준수하는지 검증"""
        pass

class IssueHierarchyPolicyPort(ABC):
    """이슈 계층 구조 정책 인터페이스"""
    
    @abstractmethod
    def determine_issue_type(self, title: str, body: str) -> str:
        """이슈 유형 결정 (Epic/Story/Task/Bug)"""
        pass
    
    @abstractmethod
    def validate_hierarchy(self, parent_type: str, child_type: str) -> bool:
        """계층 구조 유효성 검증"""
        pass
    
    @abstractmethod
    def generate_issue_template(self, issue_type: str, parent_id: Optional[int]) -> str:
        """이슈 유형별 템플릿 생성"""
        pass
    
    @abstractmethod
    def suggest_labels(self, issue_type: str, content: str) -> List[str]:
        """이슈 내용 기반 라벨 제안"""
        pass

class BranchingPolicyPort(ABC):
    """브랜치 전략 정책 인터페이스"""
    
    @abstractmethod
    def generate_branch_name(self, issue_type: str, issue_id: int, title: str) -> str:
        """이슈 기반 브랜치명 생성"""
        pass
    
    @abstractmethod
    def determine_base_branch(self, issue_type: str, parent_issue: Optional[Dict]) -> str:
        """베이스 브랜치 결정"""
        pass
    
    @abstractmethod
    def validate_branch_name(self, branch_name: str) -> bool:
        """브랜치명 유효성 검증"""
        pass
    
    @abstractmethod
    def get_merge_strategy(self, source_branch: str, target_branch: str) -> str:
        """병합 전략 결정 (merge/squash/rebase)"""
        pass

class PRPolicyPort(ABC):
    """PR 정책 인터페이스"""
    
    @abstractmethod
    def generate_pr_title(self, issue: Dict, branch: str) -> str:
        """PR 제목 생성"""
        pass
    
    @abstractmethod
    def generate_pr_body(self, issue: Dict, commits: List[str]) -> str:
        """PR 본문 생성"""
        pass
    
    @abstractmethod
    def determine_reviewers(self, pr_type: str, files_changed: List[str]) -> List[str]:
        """리뷰어 자동 결정"""
        pass
    
    @abstractmethod
    def validate_pr_requirements(self, pr_data: Dict) -> Dict:
        """PR 요구사항 검증 (테스트, 문서 등)"""
        pass