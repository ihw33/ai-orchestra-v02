"""
Issue Hierarchy Policy Adapter
이슈 계층 구조 정책을 구현하는 Adapter
Epic > Story > Task 구조 관리
"""

import re
from typing import Dict, List, Optional
import sys
import os

# Port 인터페이스 import
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from ports.policy_port import (
    PolicyPort,
    IssueHierarchyPolicyPort,
    PolicyRule,
    PolicyDecision,
    PolicyType
)

class IssueHierarchyPolicyAdapter(IssueHierarchyPolicyPort, PolicyPort):
    """이슈 계층 구조 정책 Adapter"""
    
    def __init__(self):
        # 계층 구조 정의
        self.hierarchy = {
            'epic': {
                'level': 0,
                'children': ['story', 'spike'],
                'prefix': '[Epic]',
                'label_color': '6B46C1',  # 보라색
                'branch_prefix': 'epic/'
            },
            'story': {
                'level': 1,
                'children': ['task', 'bug'],
                'prefix': '[Story]',
                'label_color': '0052CC',  # 파란색
                'branch_prefix': 'story/'
            },
            'task': {
                'level': 2,
                'children': ['subtask'],
                'prefix': '[Task]',
                'label_color': '36B37E',  # 녹색
                'branch_prefix': 'task/'
            },
            'bug': {
                'level': 2,
                'children': [],
                'prefix': '[Bug]',
                'label_color': 'D73A4A',  # 빨간색
                'branch_prefix': 'bugfix/'
            },
            'spike': {
                'level': 1,
                'children': [],
                'prefix': '[Spike]',
                'label_color': 'FBCA04',  # 노란색
                'branch_prefix': 'spike/'
            }
        }
        
        # 정책 규칙들
        self.policy_rules = self._initialize_policy_rules()
    
    def _initialize_policy_rules(self) -> List[PolicyRule]:
        """정책 규칙 초기화"""
        return [
            PolicyRule(
                id='epic_creation',
                type=PolicyType.ISSUE_HIERARCHY,
                name='Epic 생성 규칙',
                description='Epic은 PM만 생성 가능',
                conditions={'issue_type': 'epic', 'creator_role': 'pm'},
                actions={'create': True, 'template': 'epic_template'},
                priority=10
            ),
            PolicyRule(
                id='story_from_epic',
                type=PolicyType.ISSUE_HIERARCHY,
                name='Story는 Epic에서 파생',
                description='모든 Story는 부모 Epic 필요',
                conditions={'issue_type': 'story', 'has_parent': True},
                actions={'validate_parent_type': 'epic'},
                priority=9
            ),
            PolicyRule(
                id='task_from_story',
                type=PolicyType.ISSUE_HIERARCHY,
                name='Task는 Story에서 파생',
                description='모든 Task는 부모 Story 필요',
                conditions={'issue_type': 'task', 'has_parent': True},
                actions={'validate_parent_type': 'story'},
                priority=8
            ),
            PolicyRule(
                id='ai_task_assignment',
                type=PolicyType.AI_ASSIGNMENT,
                name='AI 자동 할당',
                description='Task 유형별 AI 자동 할당',
                conditions={'issue_type': 'task'},
                actions={'auto_assign': True},
                priority=7
            )
        ]
    
    def determine_issue_type(self, title: str, body: str) -> str:
        """이슈 유형 결정"""
        
        # 제목에서 명시적 타입 확인
        title_lower = title.lower()
        for issue_type, config in self.hierarchy.items():
            if config['prefix'].lower() in title_lower:
                return issue_type
        
        # 내용 기반 추론
        combined = f"{title} {body}".lower()
        
        # Epic 패턴
        if any(word in combined for word in ['전체 시스템', '대규모', '아키텍처', '재구성']):
            return 'epic'
        
        # Story 패턴
        if any(word in combined for word in ['사용자 스토리', '기능', 'feature']):
            return 'story'
        
        # Bug 패턴
        if any(word in combined for word in ['버그', '오류', '에러', '수정', 'fix']):
            return 'bug'
        
        # Spike 패턴
        if any(word in combined for word in ['조사', '연구', 'poc', 'spike']):
            return 'spike'
        
        # 기본값
        return 'task'
    
    def validate_hierarchy(self, parent_type: str, child_type: str) -> bool:
        """계층 구조 유효성 검증"""
        
        if parent_type not in self.hierarchy:
            return False
        
        allowed_children = self.hierarchy[parent_type]['children']
        return child_type in allowed_children
    
    def generate_issue_template(self, issue_type: str, parent_id: Optional[int]) -> str:
        """이슈 유형별 템플릿 생성"""
        
        templates = {
            'epic': """## 목표
[대규모 기능/개선 목표 설명]

## Stories
- [ ] [Story 1] #
- [ ] [Story 2] #
- [ ] [Story 3] #

## 완료 조건
- 모든 Story 완료
- 통합 테스트 통과
- 문서 업데이트

## 마일스톤
Target: v0.4.0""",

            'story': f"""Parent Epic: #{parent_id if parent_id else 'TBD'}

## 사용자 스토리
As a [role]
I want [feature]
So that [benefit]

## Tasks
- [ ] [Task 1] #
- [ ] [Task 2] #
- [ ] [Task 3] #

## 인수 조건
- 기능 구현 완료
- 테스트 작성
- 문서 업데이트""",

            'task': f"""Parent Story: #{parent_id if parent_id else 'TBD'}

## 작업 내용
- [구체적인 구현 내용]

## 체크리스트
- [ ] 코드 구현
- [ ] 테스트 작성
- [ ] PR 생성

## 담당 AI
@ai-gemini / @ai-claude / @ai-codex""",

            'bug': f"""Parent Story: #{parent_id if parent_id else 'N/A'}

## 버그 설명
[버그 현상 설명]

## 재현 방법
1. 
2. 
3. 

## 기대 동작
[정상 동작 설명]

## 실제 동작
[현재 문제 동작]

## 환경
- OS: 
- 버전:""",

            'spike': """## 조사 목적
[조사/연구 목적]

## 조사 항목
- [ ] 항목 1
- [ ] 항목 2
- [ ] 항목 3

## 성공 기준
- 기술 검증 완료
- 보고서 작성
- 추천안 제시

## 타임박스
Duration: 2 days"""
        }
        
        return templates.get(issue_type, templates['task'])
    
    def suggest_labels(self, issue_type: str, content: str) -> List[str]:
        """이슈 내용 기반 라벨 제안"""
        
        labels = []
        
        # 기본 타입 라벨
        labels.append(issue_type)
        
        # 우선순위 판단
        if any(word in content.lower() for word in ['긴급', 'urgent', 'critical']):
            labels.append('p0')
        elif any(word in content.lower() for word in ['중요', 'important']):
            labels.append('p1')
        else:
            labels.append('p2')
        
        # AI 할당 판단
        if issue_type in ['task', 'bug']:
            if 'api' in content.lower() or 'backend' in content.lower():
                labels.append('ai-codex')
            elif 'ui' in content.lower() or 'frontend' in content.lower():
                labels.append('ai-claude')
            elif '분석' in content.lower() or 'analysis' in content.lower():
                labels.append('ai-gemini')
            else:
                labels.append('ai-team')
        
        # 기술 스택
        tech_labels = {
            'python': ['python', 'py'],
            'typescript': ['typescript', 'ts', 'tsx'],
            'react': ['react', 'component'],
            'api': ['api', 'rest', 'graphql'],
            'database': ['db', 'database', 'sql'],
            'test': ['test', 'testing', '테스트']
        }
        
        for label, keywords in tech_labels.items():
            if any(kw in content.lower() for kw in keywords):
                labels.append(label)
        
        return labels
    
    def evaluate_policy(self, policy_type: PolicyType, context: Dict) -> PolicyDecision:
        """정책 평가"""
        
        applicable_rules = [
            rule for rule in self.policy_rules 
            if rule.type == policy_type and rule.enabled
        ]
        
        # 우선순위로 정렬
        applicable_rules.sort(key=lambda x: x.priority, reverse=True)
        
        # 첫 번째 매칭 규칙 적용
        for rule in applicable_rules:
            if self._match_conditions(rule.conditions, context):
                return PolicyDecision(
                    policy_id=rule.id,
                    decision=f"Apply {rule.name}",
                    reasoning=rule.description,
                    confidence=0.9,
                    applied_rules=[rule]
                )
        
        return PolicyDecision(
            policy_id='default',
            decision='No specific policy',
            reasoning='No matching rules found',
            confidence=0.5,
            applied_rules=[]
        )
    
    def apply_policy(self, decision: PolicyDecision) -> Dict:
        """정책 적용"""
        
        results = {
            'success': True,
            'applied_rules': [],
            'actions_taken': []
        }
        
        for rule in decision.applied_rules:
            for action_key, action_value in rule.actions.items():
                results['actions_taken'].append({
                    'action': action_key,
                    'value': action_value
                })
            results['applied_rules'].append(rule.id)
        
        return results
    
    def _match_conditions(self, conditions: Dict, context: Dict) -> bool:
        """조건 매칭 확인"""
        for key, value in conditions.items():
            if key not in context or context[key] != value:
                return False
        return True
    
    def get_policy_rules(self, policy_type: PolicyType) -> List[PolicyRule]:
        """특정 유형의 정책 규칙 조회"""
        return [rule for rule in self.policy_rules if rule.type == policy_type]
    
    def add_policy_rule(self, rule: PolicyRule) -> bool:
        """새 정책 규칙 추가"""
        self.policy_rules.append(rule)
        return True
    
    def update_policy_rule(self, rule_id: str, updates: Dict) -> bool:
        """정책 규칙 수정"""
        for rule in self.policy_rules:
            if rule.id == rule_id:
                for key, value in updates.items():
                    if hasattr(rule, key):
                        setattr(rule, key, value)
                return True
        return False
    
    def validate_against_policy(self, policy_type: PolicyType, data: Dict) -> Dict:
        """정책 준수 검증"""
        
        violations = []
        warnings = []
        
        applicable_rules = self.get_policy_rules(policy_type)
        
        for rule in applicable_rules:
            if not self._validate_rule(rule, data):
                if rule.priority >= 8:
                    violations.append(f"Violation: {rule.name}")
                else:
                    warnings.append(f"Warning: {rule.name}")
        
        return {
            'valid': len(violations) == 0,
            'violations': violations,
            'warnings': warnings
        }
    
    def _validate_rule(self, rule: PolicyRule, data: Dict) -> bool:
        """개별 규칙 검증"""
        # 규칙별 검증 로직
        if rule.id == 'story_from_epic':
            return data.get('parent_type') == 'epic' if data.get('issue_type') == 'story' else True
        
        if rule.id == 'task_from_story':
            return data.get('parent_type') == 'story' if data.get('issue_type') == 'task' else True
        
        return True


# 사용 예시
if __name__ == "__main__":
    adapter = IssueHierarchyPolicyAdapter()
    
    # 이슈 유형 결정
    print("=== 이슈 유형 판단 ===")
    test_cases = [
        ("전체 시스템 재구성", "대규모 아키텍처 변경"),
        ("사용자 로그인 기능", "사용자가 로그인할 수 있도록"),
        ("버그: 로그인 안됨", "로그인 버튼 클릭 시 에러"),
        ("API 성능 조사", "현재 API 응답 시간 분석")
    ]
    
    for title, body in test_cases:
        issue_type = adapter.determine_issue_type(title, body)
        labels = adapter.suggest_labels(issue_type, f"{title} {body}")
        print(f"\n제목: {title}")
        print(f"유형: {issue_type}")
        print(f"라벨: {labels}")
    
    # 계층 검증
    print("\n=== 계층 구조 검증 ===")
    print(f"Epic → Story: {adapter.validate_hierarchy('epic', 'story')}")
    print(f"Story → Task: {adapter.validate_hierarchy('story', 'task')}")
    print(f"Epic → Task: {adapter.validate_hierarchy('epic', 'task')}")  # False
    
    # 템플릿 생성
    print("\n=== Story 템플릿 ===")
    print(adapter.generate_issue_template('story', 100))