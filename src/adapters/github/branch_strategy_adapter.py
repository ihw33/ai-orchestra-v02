"""
Branch Strategy Adapter
브랜치 생성, 삭제, 전략 관리 구현
"""

import subprocess
import json
import re
from typing import Dict, List, Optional
import sys
import os

# Port 인터페이스 import
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from ports.pr_creator_port import BranchStrategyPort

class GitHubBranchStrategyAdapter(BranchStrategyPort):
    """GitHub 브랜치 전략 Adapter"""
    
    def __init__(self, repo: str = "ihw33/ai-orchestra-v02"):
        self.repo = repo
        self.branch_patterns = self._define_branch_patterns()
        self.protection_rules = self._define_protection_rules()
    
    def _define_branch_patterns(self) -> Dict:
        """브랜치 네이밍 패턴 정의"""
        return {
            'task': 'task/{issue_number}-{title}',
            'story': 'story/{issue_number}-{title}',
            'epic': 'epic/{issue_number}-{title}',
            'feature': 'feature/{issue_number}-{title}',
            'bugfix': 'bugfix/{issue_number}-{title}',
            'hotfix': 'hotfix/{issue_number}-{title}',
            'spike': 'spike/{issue_number}-{title}'
        }
    
    def _define_protection_rules(self) -> Dict:
        """브랜치 보호 규칙 정의"""
        return {
            'main': {
                'required_reviews': 2,
                'dismiss_stale_reviews': True,
                'require_code_owner_reviews': True,
                'require_up_to_date': True,
                'required_checks': ['ci', 'tests'],
                'enforce_admins': False
            },
            'epic/*': {
                'required_reviews': 1,
                'dismiss_stale_reviews': True,
                'require_up_to_date': True,
                'required_checks': ['tests']
            },
            'story/*': {
                'required_reviews': 1,
                'require_up_to_date': False
            }
        }
    
    def create_branch(self, branch_name: str, base_branch: str) -> bool:
        """브랜치 생성"""
        
        try:
            # 현재 브랜치 저장
            current_branch_cmd = 'git branch --show-current'
            current_result = subprocess.run(current_branch_cmd, shell=True, capture_output=True, text=True)
            current_branch = current_result.stdout.strip()
            
            # base 브랜치로 체크아웃
            checkout_cmd = f'git checkout {base_branch}'
            checkout_result = subprocess.run(checkout_cmd, shell=True, capture_output=True, text=True)
            
            if checkout_result.returncode != 0:
                # 원격에서 가져오기
                fetch_cmd = f'git fetch origin {base_branch}'
                subprocess.run(fetch_cmd, shell=True, capture_output=True, text=True)
                
                # 원격 브랜치 기반으로 체크아웃
                checkout_cmd = f'git checkout -b {base_branch} origin/{base_branch}'
                checkout_result = subprocess.run(checkout_cmd, shell=True, capture_output=True, text=True)
                
                if checkout_result.returncode != 0:
                    return False
            
            # 최신 상태로 업데이트
            pull_cmd = 'git pull'
            subprocess.run(pull_cmd, shell=True, capture_output=True, text=True)
            
            # 새 브랜치 생성
            create_cmd = f'git checkout -b {branch_name}'
            create_result = subprocess.run(create_cmd, shell=True, capture_output=True, text=True)
            
            if create_result.returncode == 0:
                # 원격에 푸시
                push_cmd = f'git push -u origin {branch_name}'
                push_result = subprocess.run(push_cmd, shell=True, capture_output=True, text=True)
                
                # 원래 브랜치로 돌아가기
                if current_branch:
                    subprocess.run(f'git checkout {current_branch}', shell=True, capture_output=True, text=True)
                
                return push_result.returncode == 0
            
            return False
            
        except Exception as e:
            print(f"브랜치 생성 실패: {e}")
            return False
    
    def delete_branch(self, branch_name: str, force: bool = False) -> bool:
        """브랜치 삭제"""
        
        try:
            # 로컬 브랜치 삭제
            delete_flag = '-D' if force else '-d'
            local_cmd = f'git branch {delete_flag} {branch_name}'
            local_result = subprocess.run(local_cmd, shell=True, capture_output=True, text=True)
            
            # 원격 브랜치 삭제
            remote_cmd = f'git push origin --delete {branch_name}'
            remote_result = subprocess.run(remote_cmd, shell=True, capture_output=True, text=True)
            
            return local_result.returncode == 0 or remote_result.returncode == 0
            
        except Exception as e:
            print(f"브랜치 삭제 실패: {e}")
            return False
    
    def generate_branch_name(self, issue_type: str, issue_number: int, 
                           title: str) -> str:
        """이슈 기반 브랜치명 생성"""
        
        # 이슈 타입별 패턴 선택
        pattern = self.branch_patterns.get(issue_type.lower(), 'feature/{issue_number}-{title}')
        
        # 제목을 브랜치명에 적합하게 변환
        slug_title = self._slugify(title)
        
        # 패턴에 값 대입
        branch_name = pattern.format(
            issue_number=issue_number,
            title=slug_title
        )
        
        return branch_name
    
    def determine_base_branch(self, issue_type: str, 
                            parent_issue: Optional[int]) -> str:
        """베이스 브랜치 결정"""
        
        issue_type_lower = issue_type.lower()
        
        # Task의 경우
        if issue_type_lower == 'task':
            if parent_issue:
                # 부모 Story의 브랜치 찾기
                parent_branch = self._find_branch_for_issue(parent_issue, 'story')
                if parent_branch:
                    return parent_branch
            return 'develop'  # 기본값
        
        # Story의 경우
        elif issue_type_lower == 'story':
            if parent_issue:
                # 부모 Epic의 브랜치 찾기
                parent_branch = self._find_branch_for_issue(parent_issue, 'epic')
                if parent_branch:
                    return parent_branch
            return 'develop'
        
        # Epic의 경우
        elif issue_type_lower == 'epic':
            return 'main'
        
        # Feature/Bugfix의 경우
        elif issue_type_lower in ['feature', 'bugfix']:
            return 'develop'
        
        # Hotfix의 경우
        elif issue_type_lower == 'hotfix':
            return 'main'
        
        # 기본값
        return 'develop'
    
    def protect_branch(self, branch_name: str, rules: Dict) -> bool:
        """브랜치 보호 규칙 설정"""
        
        try:
            # GitHub API를 통한 브랜치 보호 설정
            # gh api를 사용하여 보호 규칙 적용
            
            protection_data = {
                "required_status_checks": {
                    "strict": rules.get('require_up_to_date', False),
                    "contexts": rules.get('required_checks', [])
                },
                "enforce_admins": rules.get('enforce_admins', False),
                "required_pull_request_reviews": {
                    "required_approving_review_count": rules.get('required_reviews', 1),
                    "dismiss_stale_reviews": rules.get('dismiss_stale_reviews', False),
                    "require_code_owner_reviews": rules.get('require_code_owner_reviews', False)
                },
                "restrictions": None
            }
            
            # JSON 데이터를 파일로 저장
            import tempfile
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
                json.dump(protection_data, f)
                data_file = f.name
            
            # API 호출
            cmd = f'gh api repos/{self.repo}/branches/{branch_name}/protection --method PUT --input {data_file}'
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            
            # 임시 파일 삭제
            os.remove(data_file)
            
            return result.returncode == 0
            
        except Exception as e:
            print(f"브랜치 보호 설정 실패: {e}")
            return False
    
    def get_branch_hierarchy(self) -> Dict:
        """브랜치 계층 구조 조회"""
        
        hierarchy = {
            'main': {
                'epics': [],
                'protected': True
            },
            'develop': {
                'features': [],
                'stories': [],
                'protected': False
            },
            'epics': {},
            'stories': {},
            'tasks': {}
        }
        
        try:
            # 모든 브랜치 목록 가져오기
            cmd = 'git branch -r'
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            
            if result.returncode == 0:
                branches = result.stdout.strip().split('\n')
                
                for branch in branches:
                    branch = branch.strip()
                    if '->' in branch:  # HEAD -> origin/main 같은 경우 제외
                        continue
                    
                    # origin/ 제거
                    branch_name = branch.replace('origin/', '')
                    
                    # 브랜치 타입별 분류
                    if branch_name.startswith('epic/'):
                        issue_num = self._extract_issue_number(branch_name)
                        hierarchy['epics'][branch_name] = {
                            'issue': issue_num,
                            'stories': []
                        }
                    elif branch_name.startswith('story/'):
                        issue_num = self._extract_issue_number(branch_name)
                        hierarchy['stories'][branch_name] = {
                            'issue': issue_num,
                            'tasks': []
                        }
                    elif branch_name.startswith('task/'):
                        issue_num = self._extract_issue_number(branch_name)
                        hierarchy['tasks'][branch_name] = {
                            'issue': issue_num
                        }
                    elif branch_name.startswith('feature/'):
                        hierarchy['develop']['features'].append(branch_name)
            
            # 관계 매핑 (이슈 정보 기반)
            self._map_branch_relationships(hierarchy)
            
            return hierarchy
            
        except Exception as e:
            print(f"브랜치 계층 조회 실패: {e}")
            return hierarchy
    
    # === Helper Methods ===
    
    def _slugify(self, text: str) -> str:
        """텍스트를 브랜치명에 적합한 형태로 변환"""
        
        # 한글 제거 및 영문만 남기기
        text = re.sub(r'[가-힣]', '', text)
        
        # 소문자로 변환
        text = text.lower()
        
        # 특수문자를 하이픈으로 대체
        text = re.sub(r'[^\w\s-]', '', text)
        text = re.sub(r'[-\s]+', '-', text)
        
        # 앞뒤 하이픈 제거
        text = text.strip('-')
        
        # 빈 문자열인 경우 기본값
        if not text:
            text = 'branch'
        
        # 최대 길이 제한
        return text[:30]
    
    def _find_branch_for_issue(self, issue_number: int, branch_type: str) -> Optional[str]:
        """이슈 번호로 브랜치 찾기"""
        
        pattern = f'{branch_type}/{issue_number}-'
        
        try:
            # 원격 브랜치 목록에서 찾기
            cmd = f'git branch -r | grep "{pattern}"'
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            
            if result.returncode == 0 and result.stdout:
                # 첫 번째 매칭 브랜치 반환
                branch = result.stdout.strip().split('\n')[0]
                branch = branch.replace('origin/', '').strip()
                return branch
                
        except:
            pass
        
        return None
    
    def _extract_issue_number(self, branch_name: str) -> Optional[int]:
        """브랜치명에서 이슈 번호 추출"""
        
        match = re.search(r'/(\d+)-', branch_name)
        if match:
            return int(match.group(1))
        return None
    
    def _map_branch_relationships(self, hierarchy: Dict):
        """브랜치 간 관계 매핑"""
        
        # Story-Task 관계
        for task_branch, task_info in hierarchy['tasks'].items():
            if task_info['issue']:
                # 이슈 정보로 부모 Story 찾기
                parent_story = self._find_parent_story_from_issue(task_info['issue'])
                if parent_story:
                    story_branch = self._find_branch_for_issue(parent_story, 'story')
                    if story_branch and story_branch in hierarchy['stories']:
                        hierarchy['stories'][story_branch]['tasks'].append(task_branch)
        
        # Epic-Story 관계
        for story_branch, story_info in hierarchy['stories'].items():
            if story_info['issue']:
                # 이슈 정보로 부모 Epic 찾기
                parent_epic = self._find_parent_epic_from_issue(story_info['issue'])
                if parent_epic:
                    epic_branch = self._find_branch_for_issue(parent_epic, 'epic')
                    if epic_branch and epic_branch in hierarchy['epics']:
                        hierarchy['epics'][epic_branch]['stories'].append(story_branch)
    
    def _find_parent_story_from_issue(self, task_number: int) -> Optional[int]:
        """Task 이슈에서 부모 Story 번호 찾기"""
        
        cmd = f'gh issue view {task_number} -R {self.repo} --json body'
        
        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            if result.returncode == 0:
                data = json.loads(result.stdout)
                body = data.get('body', '')
                
                # Parent Story 패턴 찾기
                match = re.search(r'(?:Parent Story|Story):\s*#(\d+)', body, re.IGNORECASE)
                if match:
                    return int(match.group(1))
        except:
            pass
        
        return None
    
    def _find_parent_epic_from_issue(self, story_number: int) -> Optional[int]:
        """Story 이슈에서 부모 Epic 번호 찾기"""
        
        cmd = f'gh issue view {story_number} -R {self.repo} --json body'
        
        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            if result.returncode == 0:
                data = json.loads(result.stdout)
                body = data.get('body', '')
                
                # Parent Epic 패턴 찾기
                match = re.search(r'(?:Parent Epic|Epic):\s*#(\d+)', body, re.IGNORECASE)
                if match:
                    return int(match.group(1))
        except:
            pass
        
        return None


# 사용 예시
if __name__ == "__main__":
    adapter = GitHubBranchStrategyAdapter()
    
    # 브랜치명 생성 테스트
    print("=== 브랜치명 생성 ===")
    branch_name = adapter.generate_branch_name('task', 93, 'GitHubPRAdapter 구현')
    print(f"Task 브랜치: {branch_name}")
    
    branch_name = adapter.generate_branch_name('story', 90, 'PR 자동 관리 시스템')
    print(f"Story 브랜치: {branch_name}")
    
    # 베이스 브랜치 결정
    print("\n=== 베이스 브랜치 ===")
    base = adapter.determine_base_branch('task', 90)
    print(f"Task의 베이스: {base}")
    
    base = adapter.determine_base_branch('epic', None)
    print(f"Epic의 베이스: {base}")
    
    # 브랜치 계층 구조
    print("\n=== 브랜치 계층 ===")
    hierarchy = adapter.get_branch_hierarchy()
    print(f"Epic 브랜치: {len(hierarchy['epics'])}개")
    print(f"Story 브랜치: {len(hierarchy['stories'])}개")
    print(f"Task 브랜치: {len(hierarchy['tasks'])}개")