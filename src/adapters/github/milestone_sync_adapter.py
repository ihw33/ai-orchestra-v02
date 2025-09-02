"""
Milestone Sync Adapter
GitHub 마일스톤과 이슈 간 양방향 동기화
"""

import subprocess
import json
import re
from typing import Dict, List, Optional, Any
from datetime import datetime
import sys
import os

# Port 인터페이스 import
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from ports.milestone_port import (
    MilestonePort,
    MilestoneSyncPort,
    Milestone,
    MilestoneState,
    SyncResult
)

class GitHubMilestoneSyncAdapter(MilestonePort, MilestoneSyncPort):
    """GitHub 마일스톤 동기화 Adapter"""
    
    def __init__(self, repo: str = "ihw33/ai-orchestra-v02"):
        self.repo = repo
        self.sync_rules = self._initialize_sync_rules()
    
    def _initialize_sync_rules(self) -> Dict:
        """동기화 규칙 초기화"""
        return {
            'milestone_to_epic': {
                # 마일스톤 → Epic 매핑 규칙
                'v0.4.0': 'GitHub 워크플로우 자동화',
                'v0.5.0': 'AI 협업 고도화',
                'v1.0.0': 'Production Ready'
            },
            'auto_create_structure': {
                # 마일스톤에서 자동 생성할 구조
                'pattern': '[Epic] {milestone_title}',
                'stories': [
                    '[Story] 핵심 기능 구현',
                    '[Story] 테스트 및 검증',
                    '[Story] 문서화'
                ]
            },
            'sync_fields': [
                'title', 'description', 'due_date', 'state'
            ]
        }
    
    def create_milestone(self, title: str, description: str, 
                        due_date: Optional[datetime]) -> Milestone:
        """마일스톤 생성"""
        
        due_str = due_date.strftime('%Y-%m-%d') if due_date else ""
        
        cmd = f'gh api repos/{self.repo}/milestones --method POST'
        cmd += f' -f title="{title}"'
        cmd += f' -f description="{description}"'
        if due_str:
            cmd += f' -f due_on="{due_str}T00:00:00Z"'
        
        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            
            if result.returncode == 0:
                data = json.loads(result.stdout)
                return Milestone(
                    id=str(data['id']),
                    number=data['number'],
                    title=data['title'],
                    description=data.get('description', ''),
                    due_date=datetime.fromisoformat(data['due_on'].replace('Z', '')) if data.get('due_on') else None,
                    state=MilestoneState.ACTIVE if data['state'] == 'open' else MilestoneState.COMPLETED,
                    progress_percentage=0,
                    issues=[],
                    epics=[],
                    metadata={'url': data['html_url']}
                )
        except Exception as e:
            print(f"마일스톤 생성 실패: {e}")
            return None
    
    def update_milestone(self, milestone_number: int, updates: Dict) -> bool:
        """마일스톤 업데이트"""
        
        cmd = f'gh api repos/{self.repo}/milestones/{milestone_number} --method PATCH'
        
        if 'title' in updates:
            cmd += f' -f title="{updates["title"]}"'
        if 'description' in updates:
            cmd += f' -f description="{updates["description"]}"'
        if 'due_date' in updates:
            due_str = updates['due_date'].strftime('%Y-%m-%d') if updates['due_date'] else ""
            cmd += f' -f due_on="{due_str}T00:00:00Z"'
        if 'state' in updates:
            state = 'open' if updates['state'] == MilestoneState.ACTIVE else 'closed'
            cmd += f' -f state="{state}"'
        
        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            return result.returncode == 0
        except:
            return False
    
    def get_milestone(self, milestone_number: int) -> Optional[Milestone]:
        """마일스톤 조회"""
        
        cmd = f'gh api repos/{self.repo}/milestones/{milestone_number}'
        
        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            if result.returncode == 0:
                data = json.loads(result.stdout)
                
                # 연결된 이슈 조회
                issues = self._get_milestone_issues(milestone_number)
                
                return Milestone(
                    id=str(data['id']),
                    number=data['number'],
                    title=data['title'],
                    description=data.get('description', ''),
                    due_date=datetime.fromisoformat(data['due_on'].replace('Z', '')) if data.get('due_on') else None,
                    state=MilestoneState.ACTIVE if data['state'] == 'open' else MilestoneState.COMPLETED,
                    progress_percentage=self._calculate_progress_from_issues(issues),
                    issues=[i['number'] for i in issues],
                    epics=self._extract_epics(issues),
                    metadata={'url': data['html_url']}
                )
        except:
            return None
    
    def list_milestones(self, state: Optional[MilestoneState] = None) -> List[Milestone]:
        """마일스톤 목록 조회"""
        
        state_param = 'open' if state == MilestoneState.ACTIVE else 'closed' if state == MilestoneState.COMPLETED else 'all'
        cmd = f'gh api repos/{self.repo}/milestones?state={state_param}'
        
        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            if result.returncode == 0:
                data = json.loads(result.stdout)
                milestones = []
                
                for item in data:
                    issues = self._get_milestone_issues(item['number'])
                    milestones.append(Milestone(
                        id=str(item['id']),
                        number=item['number'],
                        title=item['title'],
                        description=item.get('description', ''),
                        due_date=datetime.fromisoformat(item['due_on'].replace('Z', '')) if item.get('due_on') else None,
                        state=MilestoneState.ACTIVE if item['state'] == 'open' else MilestoneState.COMPLETED,
                        progress_percentage=self._calculate_progress_from_issues(issues),
                        issues=[i['number'] for i in issues],
                        epics=self._extract_epics(issues),
                        metadata={'url': item['html_url']}
                    ))
                
                return milestones
        except:
            return []
    
    def calculate_progress(self, milestone_number: int) -> int:
        """마일스톤 진행률 계산"""
        
        issues = self._get_milestone_issues(milestone_number)
        return self._calculate_progress_from_issues(issues)
    
    def sync_milestone_to_issues(self, milestone_number: int) -> SyncResult:
        """마일스톤 → 이슈 동기화"""
        
        milestone = self.get_milestone(milestone_number)
        if not milestone:
            return SyncResult(
                success=False,
                milestone_to_issues={},
                issues_to_milestone={},
                created_issues=[],
                updated_issues=[],
                conflicts=['Milestone not found']
            )
        
        created_issues = []
        updated_issues = []
        
        # 마일스톤에 Epic이 없으면 자동 생성
        if not milestone.epics:
            epic_title = f"[Epic] {milestone.title}"
            epic_body = f"""## 마일스톤: {milestone.title}

{milestone.description}

## 목표
- 마일스톤 완료일: {milestone.due_date.strftime('%Y-%m-%d') if milestone.due_date else 'TBD'}

## Stories
(자동 생성 예정)

## 완료 조건
- 모든 Story 완료
- 통합 테스트 통과"""
            
            # Epic 생성
            epic_result = self._create_issue(epic_title, epic_body, ['epic'], milestone_number)
            if epic_result:
                created_issues.append(epic_result['number'])
                
                # Story 자동 생성
                for story_template in self.sync_rules['auto_create_structure']['stories']:
                    story_title = story_template.replace('{milestone_title}', milestone.title)
                    story_body = f"Parent Epic: #{epic_result['number']}\n\n자동 생성된 Story"
                    story_result = self._create_issue(story_title, story_body, ['story'], milestone_number)
                    if story_result:
                        created_issues.append(story_result['number'])
        
        # 기존 이슈들 업데이트
        existing_issues = self._get_unassigned_issues()
        for issue in existing_issues:
            if self._should_assign_to_milestone(issue, milestone):
                if self._assign_issue_to_milestone(issue['number'], milestone_number):
                    updated_issues.append(issue['number'])
        
        return SyncResult(
            success=True,
            milestone_to_issues={milestone.title: milestone.issues + created_issues},
            issues_to_milestone={i: milestone.title for i in milestone.issues + created_issues},
            created_issues=created_issues,
            updated_issues=updated_issues,
            conflicts=[]
        )
    
    def sync_issues_to_milestone(self, issue_numbers: List[int]) -> SyncResult:
        """이슈 → 마일스톤 동기화"""
        
        issues_to_milestone = {}
        updated_count = 0
        
        for issue_num in issue_numbers:
            issue = self._get_issue(issue_num)
            if issue:
                # 이슈 내용에서 마일스톤 추론
                suggested_milestone = self._suggest_milestone_for_issue(issue)
                if suggested_milestone:
                    if self._assign_issue_to_milestone(issue_num, suggested_milestone['number']):
                        issues_to_milestone[issue_num] = suggested_milestone['title']
                        updated_count += 1
        
        return SyncResult(
            success=True,
            milestone_to_issues={},
            issues_to_milestone=issues_to_milestone,
            created_issues=[],
            updated_issues=list(issues_to_milestone.keys()),
            conflicts=[]
        )
    
    def bidirectional_sync(self, milestone_number: int) -> SyncResult:
        """양방향 동기화"""
        
        # 1. 마일스톤 → 이슈
        milestone_to_issues = self.sync_milestone_to_issues(milestone_number)
        
        # 2. 이슈 → 마일스톤 (마일스톤의 이슈들 체크)
        milestone = self.get_milestone(milestone_number)
        if milestone:
            issues_to_milestone = self.sync_issues_to_milestone(milestone.issues)
            
            # 결과 병합
            return SyncResult(
                success=milestone_to_issues.success and issues_to_milestone.success,
                milestone_to_issues=milestone_to_issues.milestone_to_issues,
                issues_to_milestone=issues_to_milestone.issues_to_milestone,
                created_issues=milestone_to_issues.created_issues,
                updated_issues=milestone_to_issues.updated_issues + issues_to_milestone.updated_issues,
                conflicts=milestone_to_issues.conflicts + issues_to_milestone.conflicts
            )
        
        return milestone_to_issues
    
    def detect_conflicts(self, milestone_number: int) -> List[str]:
        """충돌 감지"""
        
        conflicts = []
        milestone = self.get_milestone(milestone_number)
        
        if milestone:
            # 중복 Epic 확인
            epic_titles = {}
            for epic_num in milestone.epics:
                epic = self._get_issue(epic_num)
                if epic:
                    title = epic['title']
                    if title in epic_titles:
                        conflicts.append(f"중복 Epic: {title} (#{epic_num}, #{epic_titles[title]})")
                    else:
                        epic_titles[title] = epic_num
            
            # 날짜 충돌 확인
            if milestone.due_date:
                for issue_num in milestone.issues:
                    issue = self._get_issue(issue_num)
                    # 이슈에 due date가 있고 마일스톤보다 늦으면 충돌
                    # (GitHub API에서 이슈 due date 지원 시)
                    pass
        
        return conflicts
    
    def resolve_conflicts(self, conflicts: List[str], strategy: str) -> bool:
        """충돌 해결"""
        
        if strategy == 'merge':
            # 중복 제거 및 병합
            for conflict in conflicts:
                if '중복 Epic' in conflict:
                    # 중복 Epic 병합 로직
                    pass
        elif strategy == 'keep_latest':
            # 최신 것만 유지
            pass
        
        return True
    
    # === Helper Methods ===
    
    def _get_milestone_issues(self, milestone_number: int) -> List[Dict]:
        """마일스톤에 연결된 이슈 조회"""
        
        cmd = f'gh issue list -R {self.repo} --milestone {milestone_number} --json number,title,state,labels --limit 100'
        
        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            if result.returncode == 0:
                return json.loads(result.stdout)
        except:
            pass
        
        return []
    
    def _calculate_progress_from_issues(self, issues: List[Dict]) -> int:
        """이슈 기반 진행률 계산"""
        
        if not issues:
            return 0
        
        closed_count = sum(1 for i in issues if i.get('state') == 'CLOSED')
        return int((closed_count / len(issues)) * 100)
    
    def _extract_epics(self, issues: List[Dict]) -> List[int]:
        """이슈 목록에서 Epic 추출"""
        
        epics = []
        for issue in issues:
            labels = [l['name'] for l in issue.get('labels', [])]
            if 'epic' in labels or '[Epic]' in issue.get('title', ''):
                epics.append(issue['number'])
        
        return epics
    
    def _create_issue(self, title: str, body: str, labels: List[str], milestone_number: int) -> Optional[Dict]:
        """이슈 생성"""
        
        from src.adapters.github.smart_issue_creator_adapter import GitHubIssueCreatorAdapter
        
        creator = GitHubIssueCreatorAdapter(self.repo)
        result = creator.create_issue(title, body, labels)
        
        if result['success']:
            # 마일스톤 할당
            issue_number = result['issue_number']
            self._assign_issue_to_milestone(issue_number, milestone_number)
            return {'number': int(issue_number)}
        
        return None
    
    def _get_issue(self, issue_number: int) -> Optional[Dict]:
        """이슈 조회"""
        
        cmd = f'gh issue view {issue_number} -R {self.repo} --json number,title,body,labels,milestone'
        
        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            if result.returncode == 0:
                return json.loads(result.stdout)
        except:
            pass
        
        return None
    
    def _get_unassigned_issues(self) -> List[Dict]:
        """마일스톤 미할당 이슈 조회"""
        
        cmd = f'gh issue list -R {self.repo} --no-milestone --json number,title,labels --limit 50'
        
        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            if result.returncode == 0:
                return json.loads(result.stdout)
        except:
            pass
        
        return []
    
    def _should_assign_to_milestone(self, issue: Dict, milestone: Milestone) -> bool:
        """이슈를 마일스톤에 할당해야 하는지 판단"""
        
        # 규칙 기반 판단
        issue_title = issue.get('title', '').lower()
        milestone_title = milestone.title.lower()
        
        # 키워드 매칭
        if 'github' in milestone_title and 'github' in issue_title:
            return True
        if 'ai' in milestone_title and 'ai' in issue_title:
            return True
        
        return False
    
    def _suggest_milestone_for_issue(self, issue: Dict) -> Optional[Dict]:
        """이슈에 적합한 마일스톤 제안"""
        
        milestones = self.list_milestones(MilestoneState.ACTIVE)
        issue_title = issue.get('title', '').lower()
        
        for milestone in milestones:
            if self._should_assign_to_milestone(issue, milestone):
                return {'number': milestone.number, 'title': milestone.title}
        
        return None
    
    def _assign_issue_to_milestone(self, issue_number: int, milestone_number: int) -> bool:
        """이슈를 마일스톤에 할당"""
        
        cmd = f'gh issue edit {issue_number} -R {self.repo} --milestone {milestone_number}'
        
        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            return result.returncode == 0
        except:
            return False


# 사용 예시
if __name__ == "__main__":
    adapter = GitHubMilestoneSyncAdapter()
    
    # 마일스톤 목록 조회
    print("=== 현재 마일스톤 ===")
    milestones = adapter.list_milestones(MilestoneState.ACTIVE)
    for m in milestones:
        print(f"#{m.number}: {m.title} (진행률: {m.progress_percentage}%)")
        print(f"  이슈: {len(m.issues)}개, Epic: {len(m.epics)}개")
    
    # 양방향 동기화 테스트
    if milestones:
        print(f"\n=== 마일스톤 #{milestones[0].number} 동기화 ===")
        result = adapter.bidirectional_sync(milestones[0].number)
        print(f"성공: {result.success}")
        print(f"생성된 이슈: {result.created_issues}")
        print(f"업데이트된 이슈: {result.updated_issues}")