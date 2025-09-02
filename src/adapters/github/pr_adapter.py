"""
GitHub PR Adapter
Pull Request 생성, 병합, 리뷰 관리 구현
"""

import subprocess
import json
import re
import tempfile
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime
import sys
import os

# Port 인터페이스 import
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from ports.pr_creator_port import (
    PRCreatorPort,
    PRMergePort,
    PRReviewPort,
    PullRequest,
    PRCreationRequest,
    MergeRequest,
    PRChain,
    PRState,
    MergeMethod,
    ReviewState
)

class GitHubPRAdapter(PRCreatorPort, PRMergePort, PRReviewPort):
    """GitHub PR 관리 Adapter"""
    
    def __init__(self, repo: str = "ihw33/ai-orchestra-v02"):
        self.repo = repo
        self.default_base = "main"
        
    # === PRCreatorPort 구현 ===
    
    def create_pr(self, request: PRCreationRequest) -> PullRequest:
        """PR 생성"""
        
        # PR 본문을 임시 파일로 저장
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write(request.body)
            body_file = f.name
        
        try:
            # gh pr create 명령 구성
            cmd = f'gh pr create -R {self.repo}'
            cmd += f' --title "{request.title}"'
            cmd += f' --body-file {body_file}'
            cmd += f' --base {request.base_branch}'
            cmd += f' --head {request.head_branch}'
            
            if request.draft:
                cmd += ' --draft'
            
            if request.reviewers:
                cmd += f' --reviewer {",".join(request.reviewers)}'
            
            if request.assignees:
                cmd += f' --assignee {",".join(request.assignees)}'
            
            if request.labels:
                cmd += f' --label {",".join(request.labels)}'
            
            if request.milestone:
                cmd += f' --milestone {request.milestone}'
            
            # PR 생성 실행
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            
            if result.returncode == 0:
                # PR 번호 추출
                output = result.stdout.strip()
                pr_number = self._extract_pr_number(output)
                
                if pr_number:
                    # 생성된 PR 정보 조회
                    return self.get_pr(pr_number)
                    
            # 실패 시 예외 발생
            raise Exception(f"PR 생성 실패: {result.stderr}")
            
        finally:
            # 임시 파일 삭제
            if os.path.exists(body_file):
                os.remove(body_file)
    
    def update_pr(self, pr_number: int, updates: Dict) -> bool:
        """PR 업데이트"""
        
        cmd = f'gh pr edit {pr_number} -R {self.repo}'
        
        if 'title' in updates:
            cmd += f' --title "{updates["title"]}"'
        
        if 'body' in updates:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
                f.write(updates['body'])
                body_file = f.name
            cmd += f' --body-file {body_file}'
        
        if 'labels' in updates:
            # 기존 라벨 제거하고 새로 설정
            cmd += f' --remove-label "*"'
            if updates['labels']:
                cmd += f' --add-label {",".join(updates["labels"])}'
        
        if 'reviewers' in updates:
            cmd += f' --add-reviewer {",".join(updates["reviewers"])}'
        
        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            return result.returncode == 0
        finally:
            if 'body' in updates and os.path.exists(body_file):
                os.remove(body_file)
    
    def get_pr(self, pr_number: int) -> Optional[PullRequest]:
        """PR 조회"""
        
        cmd = f'gh pr view {pr_number} -R {self.repo} --json number,title,body,state,baseRefName,headRefName,author,createdAt,updatedAt,mergedAt,mergeCommit,labels,files,additions,deletions'
        
        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            
            if result.returncode == 0:
                data = json.loads(result.stdout)
                
                # PR 상태 매핑
                state_map = {
                    'OPEN': PRState.OPEN,
                    'CLOSED': PRState.CLOSED,
                    'MERGED': PRState.MERGED
                }
                
                # 연결된 이슈 추출
                linked_issues = self._extract_linked_issues(data.get('body', ''))
                
                return PullRequest(
                    number=data['number'],
                    title=data['title'],
                    body=data.get('body', ''),
                    state=state_map.get(data['state'], PRState.OPEN),
                    base_branch=data['baseRefName'],
                    head_branch=data['headRefName'],
                    author=data['author']['login'],
                    created_at=datetime.fromisoformat(data['createdAt'].replace('Z', '')),
                    updated_at=datetime.fromisoformat(data['updatedAt'].replace('Z', '')),
                    merged_at=datetime.fromisoformat(data['mergedAt'].replace('Z', '')) if data.get('mergedAt') else None,
                    merge_commit_sha=data.get('mergeCommit', {}).get('oid'),
                    labels=[l['name'] for l in data.get('labels', [])],
                    linked_issues=linked_issues,
                    files_changed=len(data.get('files', [])),
                    additions=data.get('additions', 0),
                    deletions=data.get('deletions', 0)
                )
        except Exception as e:
            print(f"PR 조회 실패: {e}")
            return None
    
    def list_prs(self, state: Optional[PRState] = None, 
                 base: Optional[str] = None) -> List[PullRequest]:
        """PR 목록 조회"""
        
        cmd = f'gh pr list -R {self.repo} --json number,title,state,baseRefName'
        
        if state:
            state_filter = {
                PRState.OPEN: 'open',
                PRState.CLOSED: 'closed',
                PRState.MERGED: 'merged'
            }
            cmd += f' --state {state_filter[state]}'
        
        if base:
            cmd += f' --base {base}'
        
        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            
            if result.returncode == 0:
                data = json.loads(result.stdout)
                prs = []
                
                for item in data:
                    # 각 PR 상세 정보 조회
                    pr = self.get_pr(item['number'])
                    if pr:
                        prs.append(pr)
                
                return prs
        except:
            return []
    
    def close_pr(self, pr_number: int) -> bool:
        """PR 닫기"""
        
        cmd = f'gh pr close {pr_number} -R {self.repo}'
        
        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            return result.returncode == 0
        except:
            return False
    
    # === PRMergePort 구현 ===
    
    def merge_pr(self, request: MergeRequest) -> Dict:
        """PR 병합"""
        
        # 병합 가능 여부 확인
        can_merge, reason = self.can_merge(request.pr_number)
        if not can_merge:
            return {
                'success': False,
                'error': reason
            }
        
        # 병합 명령 구성
        cmd = f'gh pr merge {request.pr_number} -R {self.repo}'
        
        # 병합 방법 설정
        merge_method_map = {
            MergeMethod.MERGE: '--merge',
            MergeMethod.SQUASH: '--squash',
            MergeMethod.REBASE: '--rebase'
        }
        cmd += f' {merge_method_map[request.merge_method]}'
        
        # 브랜치 삭제 옵션
        if request.delete_branch:
            cmd += ' --delete-branch'
        
        # 커밋 메시지
        if request.commit_title:
            cmd += f' --subject "{request.commit_title}"'
        if request.commit_message:
            cmd += f' --body "{request.commit_message}"'
        
        # 자동 확인
        cmd += ' --auto'
        
        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            
            if result.returncode == 0:
                return {
                    'success': True,
                    'pr_number': request.pr_number,
                    'method': request.merge_method.value,
                    'output': result.stdout
                }
            else:
                return {
                    'success': False,
                    'error': result.stderr
                }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def can_merge(self, pr_number: int) -> Tuple[bool, str]:
        """병합 가능 여부 확인"""
        
        # PR 상태 확인
        pr = self.get_pr(pr_number)
        if not pr:
            return False, "PR을 찾을 수 없습니다"
        
        if pr.state != PRState.OPEN:
            return False, f"PR 상태가 OPEN이 아닙니다: {pr.state.value}"
        
        # 체크 상태 확인
        cmd = f'gh pr checks {pr_number} -R {self.repo} --json state'
        
        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            if result.returncode == 0:
                checks = json.loads(result.stdout)
                
                # 실패한 체크가 있는지 확인
                for check in checks:
                    if check.get('state') == 'FAILURE':
                        return False, "체크가 실패했습니다"
                    elif check.get('state') == 'PENDING':
                        return False, "체크가 진행 중입니다"
            
            return True, "병합 가능"
            
        except:
            # 체크 확인 실패 시에도 병합 시도 가능
            return True, "체크 확인 실패, 병합 시도 가능"
    
    def create_merge_chain(self, issue_number: int, issue_type: str) -> PRChain:
        """이슈 타입별 PR 체인 생성"""
        
        chain = PRChain()
        
        # 이슈 정보 가져오기
        issue_info = self._get_issue_info(issue_number)
        if not issue_info:
            return chain
        
        # 이슈 타입에 따른 브랜치 전략
        if issue_type.lower() == 'task':
            # Task → Story 브랜치로 PR
            task_branch = f"task/{issue_number}-{self._slugify(issue_info['title'])}"
            parent_story = self._find_parent_story(issue_number)
            
            if parent_story:
                story_branch = f"story/{parent_story}-feature"
                
                # Task PR 생성
                pr_request = PRCreationRequest(
                    title=f"[Task #{issue_number}] {issue_info['title']}",
                    body=f"Task #{issue_number} 구현\n\nParent Story: #{parent_story}",
                    base_branch=story_branch,
                    head_branch=task_branch,
                    labels=['task']
                )
                
                task_pr = self.create_pr(pr_request)
                if task_pr:
                    chain.task_pr = task_pr.number
        
        elif issue_type.lower() == 'story':
            # Story → Epic 브랜치로 PR
            story_branch = f"story/{issue_number}-{self._slugify(issue_info['title'])}"
            parent_epic = self._find_parent_epic(issue_number)
            
            if parent_epic:
                epic_branch = f"epic/{parent_epic}-feature"
                
                pr_request = PRCreationRequest(
                    title=f"[Story #{issue_number}] {issue_info['title']}",
                    body=f"Story #{issue_number} 구현\n\nParent Epic: #{parent_epic}",
                    base_branch=epic_branch,
                    head_branch=story_branch,
                    labels=['story']
                )
                
                story_pr = self.create_pr(pr_request)
                if story_pr:
                    chain.story_pr = story_pr.number
        
        elif issue_type.lower() == 'epic':
            # Epic → main으로 PR
            epic_branch = f"epic/{issue_number}-{self._slugify(issue_info['title'])}"
            
            pr_request = PRCreationRequest(
                title=f"[Epic #{issue_number}] {issue_info['title']}",
                body=f"Epic #{issue_number} 완료",
                base_branch='main',
                head_branch=epic_branch,
                labels=['epic']
            )
            
            epic_pr = self.create_pr(pr_request)
            if epic_pr:
                chain.epic_pr = epic_pr.number
        
        return chain
    
    def execute_chain_merge(self, chain: PRChain) -> Dict:
        """체인 병합 실행 (Task → Story → Epic → main)"""
        
        results = {
            'success': True,
            'merged': [],
            'failed': [],
            'errors': []
        }
        
        # 1. Task PR 병합
        if chain.task_pr:
            merge_request = MergeRequest(
                pr_number=chain.task_pr,
                merge_method=MergeMethod.SQUASH,
                delete_branch=True
            )
            
            result = self.merge_pr(merge_request)
            if result['success']:
                results['merged'].append(f"Task PR #{chain.task_pr}")
            else:
                results['failed'].append(f"Task PR #{chain.task_pr}")
                results['errors'].append(result['error'])
                results['success'] = False
                return results  # 실패 시 중단
        
        # 2. Story PR 병합
        if chain.story_pr:
            merge_request = MergeRequest(
                pr_number=chain.story_pr,
                merge_method=MergeMethod.SQUASH,
                delete_branch=True
            )
            
            result = self.merge_pr(merge_request)
            if result['success']:
                results['merged'].append(f"Story PR #{chain.story_pr}")
            else:
                results['failed'].append(f"Story PR #{chain.story_pr}")
                results['errors'].append(result['error'])
                results['success'] = False
                return results
        
        # 3. Epic PR 병합
        if chain.epic_pr:
            merge_request = MergeRequest(
                pr_number=chain.epic_pr,
                merge_method=MergeMethod.MERGE,  # Epic은 일반 머지
                delete_branch=True
            )
            
            result = self.merge_pr(merge_request)
            if result['success']:
                results['merged'].append(f"Epic PR #{chain.epic_pr}")
                chain.chain_complete = True
            else:
                results['failed'].append(f"Epic PR #{chain.epic_pr}")
                results['errors'].append(result['error'])
                results['success'] = False
        
        return results
    
    def rollback_merge(self, merge_commit_sha: str) -> bool:
        """병합 롤백"""
        
        cmd = f'git revert {merge_commit_sha} --no-edit'
        
        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            
            if result.returncode == 0:
                # 리버트 커밋 푸시
                push_result = subprocess.run('git push', shell=True, capture_output=True, text=True)
                return push_result.returncode == 0
                
            return False
        except:
            return False
    
    # === PRReviewPort 구현 ===
    
    def request_review(self, pr_number: int, reviewers: List[str]) -> bool:
        """리뷰 요청"""
        
        cmd = f'gh pr edit {pr_number} -R {self.repo} --add-reviewer {",".join(reviewers)}'
        
        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            return result.returncode == 0
        except:
            return False
    
    def approve_pr(self, pr_number: int, comment: Optional[str] = None) -> bool:
        """PR 승인"""
        
        cmd = f'gh pr review {pr_number} -R {self.repo} --approve'
        
        if comment:
            cmd += f' --body "{comment}"'
        
        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            return result.returncode == 0
        except:
            return False
    
    def request_changes(self, pr_number: int, comment: str) -> bool:
        """변경 요청"""
        
        cmd = f'gh pr review {pr_number} -R {self.repo} --request-changes --body "{comment}"'
        
        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            return result.returncode == 0
        except:
            return False
    
    def get_review_status(self, pr_number: int) -> Dict:
        """리뷰 상태 조회"""
        
        cmd = f'gh pr view {pr_number} -R {self.repo} --json reviews'
        
        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            
            if result.returncode == 0:
                data = json.loads(result.stdout)
                reviews = data.get('reviews', [])
                
                # 리뷰 상태 집계
                status = {
                    'total_reviews': len(reviews),
                    'approved': 0,
                    'changes_requested': 0,
                    'commented': 0,
                    'reviewers': []
                }
                
                for review in reviews:
                    state = review.get('state', '')
                    if state == 'APPROVED':
                        status['approved'] += 1
                    elif state == 'CHANGES_REQUESTED':
                        status['changes_requested'] += 1
                    else:
                        status['commented'] += 1
                    
                    reviewer = review.get('author', {}).get('login')
                    if reviewer and reviewer not in status['reviewers']:
                        status['reviewers'].append(reviewer)
                
                return status
        except:
            return {}
    
    def auto_assign_reviewers(self, pr_number: int) -> List[str]:
        """자동 리뷰어 할당"""
        
        # PR 정보 가져오기
        pr = self.get_pr(pr_number)
        if not pr:
            return []
        
        reviewers = []
        
        # 라벨 기반 리뷰어 할당
        if 'ai-gemini' in pr.labels:
            reviewers.append('gemini-reviewer')
        if 'ai-claude' in pr.labels:
            reviewers.append('claude-reviewer')
        if 'ai-codex' in pr.labels:
            reviewers.append('codex-reviewer')
        
        # 실제 리뷰 요청
        if reviewers:
            self.request_review(pr_number, reviewers)
        
        return reviewers
    
    # === Helper Methods ===
    
    def _extract_pr_number(self, output: str) -> Optional[int]:
        """출력에서 PR 번호 추출"""
        
        # 패턴: #123 또는 /pull/123
        patterns = [
            r'#(\d+)',
            r'/pull/(\d+)',
            r'pull request #(\d+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, output, re.IGNORECASE)
            if match:
                return int(match.group(1))
        
        return None
    
    def _extract_linked_issues(self, body: str) -> List[int]:
        """PR 본문에서 연결된 이슈 추출"""
        
        issues = []
        
        # 패턴: #123, fixes #123, closes #123, resolves #123
        patterns = [
            r'(?:fixes|closes|resolves|fix|close|resolve)\s+#(\d+)',
            r'#(\d+)'
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, body, re.IGNORECASE)
            for match in matches:
                issue_num = int(match)
                if issue_num not in issues:
                    issues.append(issue_num)
        
        return issues
    
    def _get_issue_info(self, issue_number: int) -> Optional[Dict]:
        """이슈 정보 조회"""
        
        cmd = f'gh issue view {issue_number} -R {self.repo} --json number,title,body,labels'
        
        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            if result.returncode == 0:
                return json.loads(result.stdout)
        except:
            pass
        
        return None
    
    def _find_parent_story(self, task_number: int) -> Optional[int]:
        """Task의 부모 Story 찾기"""
        
        issue = self._get_issue_info(task_number)
        if issue:
            body = issue.get('body', '')
            
            # Parent Story: #123 패턴 찾기
            match = re.search(r'Parent Story:\s*#(\d+)', body, re.IGNORECASE)
            if match:
                return int(match.group(1))
            
            # Story #123 패턴 찾기
            match = re.search(r'Story\s*#(\d+)', body, re.IGNORECASE)
            if match:
                return int(match.group(1))
        
        return None
    
    def _find_parent_epic(self, story_number: int) -> Optional[int]:
        """Story의 부모 Epic 찾기"""
        
        issue = self._get_issue_info(story_number)
        if issue:
            body = issue.get('body', '')
            
            # Parent Epic: #123 패턴 찾기
            match = re.search(r'Parent Epic:\s*#(\d+)', body, re.IGNORECASE)
            if match:
                return int(match.group(1))
            
            # Epic #123 패턴 찾기
            match = re.search(r'Epic\s*#(\d+)', body, re.IGNORECASE)
            if match:
                return int(match.group(1))
        
        return None
    
    def _slugify(self, text: str) -> str:
        """텍스트를 브랜치명에 적합한 형태로 변환"""
        
        # 소문자로 변환
        text = text.lower()
        
        # 특수문자를 하이픈으로 대체
        text = re.sub(r'[^\w\s-]', '', text)
        text = re.sub(r'[-\s]+', '-', text)
        
        # 앞뒤 하이픈 제거
        text = text.strip('-')
        
        # 최대 길이 제한
        return text[:50]


# 사용 예시
if __name__ == "__main__":
    adapter = GitHubPRAdapter()
    
    # PR 목록 조회
    print("=== Open PRs ===")
    prs = adapter.list_prs(state=PRState.OPEN)
    for pr in prs:
        print(f"#{pr.number}: {pr.title} ({pr.state.value})")
    
    # PR 생성 테스트
    # request = PRCreationRequest(
    #     title="[Test] PR Adapter 테스트",
    #     body="테스트 PR입니다",
    #     base_branch="main",
    #     head_branch="test-branch",
    #     draft=True
    # )
    # new_pr = adapter.create_pr(request)
    # print(f"Created PR: #{new_pr.number}")