"""
Task Automation Adapter
Story에서 자동으로 Task를 생성하고 AI에게 할당
"""

import subprocess
import json
import re
import tempfile
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import sys
import os

# Port 인터페이스 import
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from ports.task_automation_port import (
    TaskAutomationPort,
    TaskType,
    AIAssignment,
    TaskTemplate,
    AutoTaskResult
)

class GitHubTaskAutomationAdapter(TaskAutomationPort):
    """GitHub Task 자동화 Adapter"""
    
    def __init__(self, repo: str = "ihw33/ai-orchestra-v02"):
        self.repo = repo
        self.task_patterns = self._initialize_task_patterns()
        self.ai_skills = self._initialize_ai_skills()
    
    def _initialize_task_patterns(self) -> Dict:
        """Task 패턴 초기화"""
        return {
            'pr_automation': [
                TaskTemplate(
                    title="[Task] Port 인터페이스 정의",
                    description="PR 관리를 위한 Port 인터페이스 설계",
                    task_type=TaskType.INTERFACE_DESIGN,
                    assigned_ai=AIAssignment.GEMINI,
                    estimated_hours=2
                ),
                TaskTemplate(
                    title="[Task] GitHub Adapter 구현",
                    description="GitHub API를 사용한 Adapter 구현",
                    task_type=TaskType.IMPLEMENTATION,
                    assigned_ai=AIAssignment.CLAUDE,
                    estimated_hours=4
                ),
                TaskTemplate(
                    title="[Task] 브랜치 전략 자동화",
                    description="이슈 타입별 브랜치 자동 생성 및 관리",
                    task_type=TaskType.IMPLEMENTATION,
                    assigned_ai=AIAssignment.CODEX,
                    estimated_hours=3
                ),
                TaskTemplate(
                    title="[Task] 통합 테스트",
                    description="전체 PR 워크플로우 테스트",
                    task_type=TaskType.TESTING,
                    assigned_ai=AIAssignment.CLAUDE,
                    estimated_hours=2
                )
            ],
            'milestone_sync': [
                TaskTemplate(
                    title="[Task] 동기화 로직 구현",
                    description="양방향 동기화 알고리즘 구현",
                    task_type=TaskType.IMPLEMENTATION,
                    assigned_ai=AIAssignment.CODEX,
                    estimated_hours=3
                ),
                TaskTemplate(
                    title="[Task] 충돌 해결 전략",
                    description="동기화 충돌 감지 및 해결",
                    task_type=TaskType.IMPLEMENTATION,
                    assigned_ai=AIAssignment.CLAUDE,
                    estimated_hours=2
                )
            ],
            'ai_orchestration': [
                TaskTemplate(
                    title="[Task] AI 실행 엔진 구현",
                    description="각 AI CLI 실행 및 결과 수집",
                    task_type=TaskType.IMPLEMENTATION,
                    assigned_ai=AIAssignment.CLAUDE,
                    estimated_hours=4
                ),
                TaskTemplate(
                    title="[Task] 페르소나 시스템 통합",
                    description="페르소나별 스타일 적용",
                    task_type=TaskType.INTEGRATION,
                    assigned_ai=AIAssignment.GEMINI,
                    estimated_hours=3
                )
            ]
        }
    
    def _initialize_ai_skills(self) -> Dict:
        """AI별 전문 분야 정의"""
        return {
            AIAssignment.GEMINI: {
                'skills': ['설계', '분석', 'UX', '문서화', '기획'],
                'personas': ['strategist', 'architect', 'analyst']
            },
            AIAssignment.CLAUDE: {
                'skills': ['구현', '리팩터링', '테스트', '리뷰', '디버깅'],
                'personas': ['developer', 'reviewer', 'debugger']
            },
            AIAssignment.CODEX: {
                'skills': ['백엔드', 'API', '데이터베이스', '인프라', '자동화'],
                'personas': ['backend', 'devops', 'automation']
            }
        }
    
    def analyze_story(self, story_id: int) -> List[TaskTemplate]:
        """Story 분석하여 필요한 Task 도출"""
        
        # Story 정보 가져오기
        story = self._get_issue(story_id)
        if not story:
            return []
        
        # Story 제목과 본문에서 키워드 추출
        title = story.get('title', '').lower()
        body = story.get('body', '').lower()
        
        # 적합한 Task 패턴 찾기
        templates = []
        
        if 'pr' in title or 'pull request' in title or 'merge' in title:
            templates.extend(self.task_patterns['pr_automation'])
        elif 'milestone' in title or '마일스톤' in title or 'sync' in title:
            templates.extend(self.task_patterns['milestone_sync'])
        elif 'ai' in title or 'orchestrat' in title:
            templates.extend(self.task_patterns['ai_orchestration'])
        else:
            # 기본 Task 템플릿
            templates = [
                TaskTemplate(
                    title=f"[Task] {story.get('title', '')} - 설계",
                    description="기능 설계 및 인터페이스 정의",
                    task_type=TaskType.INTERFACE_DESIGN,
                    assigned_ai=AIAssignment.GEMINI,
                    estimated_hours=2
                ),
                TaskTemplate(
                    title=f"[Task] {story.get('title', '')} - 구현",
                    description="핵심 기능 구현",
                    task_type=TaskType.IMPLEMENTATION,
                    assigned_ai=AIAssignment.CLAUDE,
                    estimated_hours=4
                ),
                TaskTemplate(
                    title=f"[Task] {story.get('title', '')} - 테스트",
                    description="단위 테스트 및 통합 테스트",
                    task_type=TaskType.TESTING,
                    assigned_ai=AIAssignment.CLAUDE,
                    estimated_hours=2
                )
            ]
        
        return templates
    
    def create_tasks_from_story(self, story_id: int) -> AutoTaskResult:
        """Story에서 Task 자동 생성"""
        
        created_tasks = []
        ai_assignments = {}
        persona_assignments = {}
        errors = []
        
        # Story 분석
        templates = self.analyze_story(story_id)
        
        if not templates:
            return AutoTaskResult(
                story_id=story_id,
                created_tasks=[],
                ai_assignments={},
                persona_assignments={},
                success=False,
                errors=["No suitable task templates found"]
            )
        
        # 각 템플릿으로 Task 생성
        for template in templates:
            # Task 이슈 생성
            task_body = f"""## Story
#{story_id}

## 설명
{template.description}

## 담당 AI
- AI: {template.assigned_ai.value}
- 예상 시간: {template.estimated_hours}h
- Task 유형: {template.task_type.value}

## 완료 조건
- [ ] 구현 완료
- [ ] 테스트 통과
- [ ] PR 생성
- [ ] 리뷰 완료
"""
            
            # 라벨 준비
            labels = ['task', f'ai-{template.assigned_ai.value}']
            
            # GitHub 이슈 생성
            result = self._create_task_issue(
                title=template.title,
                body=task_body,
                labels=labels,
                parent_story=story_id
            )
            
            if result['success']:
                task_id = result['task_id']
                created_tasks.append(task_id)
                
                # AI 할당
                ai_name, persona_id = self.assign_ai_to_task(
                    task_id, 
                    f"{template.title}\n{template.description}"
                )
                ai_assignments[task_id] = ai_name
                persona_assignments[task_id] = persona_id
                
                # AI 실행 트리거
                triggered = self.trigger_ai_execution(
                    task_id, ai_name, persona_id
                )
                
                if not triggered:
                    errors.append(f"Failed to trigger AI for task #{task_id}")
            else:
                errors.append(f"Failed to create task: {template.title}")
        
        return AutoTaskResult(
            story_id=story_id,
            created_tasks=created_tasks,
            ai_assignments=ai_assignments,
            persona_assignments=persona_assignments,
            success=len(created_tasks) > 0,
            errors=errors if errors else None
        )
    
    def assign_ai_to_task(self, task_id: int, task_content: str) -> Tuple[str, str]:
        """Task에 적합한 AI와 페르소나 할당"""
        
        # Task 내용 분석
        content_lower = task_content.lower()
        
        # 키워드 기반 AI 선택
        if any(keyword in content_lower for keyword in ['설계', 'design', 'interface', '분석', 'ux']):
            ai = AIAssignment.GEMINI
        elif any(keyword in content_lower for keyword in ['백엔드', 'backend', 'api', 'database', '데이터베이스']):
            ai = AIAssignment.CODEX
        else:
            ai = AIAssignment.CLAUDE
        
        # 페르소나 선택
        ai_info = self.ai_skills[ai]
        
        if 'design' in content_lower or '설계' in content_lower:
            persona = 'architect'
        elif 'test' in content_lower or '테스트' in content_lower:
            persona = 'reviewer'
        elif 'backend' in content_lower or '백엔드' in content_lower:
            persona = 'backend'
        else:
            persona = ai_info['personas'][0]
        
        return ai.value, persona
    
    def trigger_ai_execution(self, task_id: int, ai_name: str, 
                            persona_id: str) -> bool:
        """AI 실행 트리거"""
        
        # Task 정보 가져오기
        task = self._get_issue(task_id)
        if not task:
            return False
        
        # AI 실행 명령 생성
        prompt = f"""Task #{task_id}: {task.get('title', '')}

{task.get('body', '')}

이 Task를 수행해주세요. 완료되면 이슈에 댓글로 결과를 보고해주세요."""
        
        # 임시 파일에 프롬프트 저장
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write(prompt)
            prompt_file = f.name
        
        # AI 실행 (비대화형 모드)
        ai_commands = {
            'gemini': f'gemini -p < {prompt_file}',
            'claude': f'claude -p < {prompt_file}',
            'codex': f'codex exec "{prompt}"'
        }
        
        command = ai_commands.get(ai_name)
        if not command:
            return False
        
        try:
            # AI 실행 및 결과를 이슈에 댓글로 작성
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=120
            )
            
            # 결과를 이슈에 댓글로 작성
            if result.returncode == 0:
                comment = f"""## 🤖 {ai_name.upper()} 작업 시작

페르소나: **{persona_id}**

Task를 분석하고 작업을 시작했습니다.

```
{result.stdout[:500]}...
```

작업이 진행 중입니다. 완료되면 다시 보고하겠습니다."""
                
                self._post_comment(task_id, comment)
                return True
                
        except subprocess.TimeoutExpired:
            comment = f"⏰ {ai_name} 실행 시간 초과 (2분)"
            self._post_comment(task_id, comment)
        except Exception as e:
            comment = f"❌ {ai_name} 실행 실패: {str(e)}"
            self._post_comment(task_id, comment)
        finally:
            # 임시 파일 삭제
            if os.path.exists(prompt_file):
                os.remove(prompt_file)
        
        return False
    
    def monitor_task_progress(self, task_id: int) -> Dict:
        """Task 진행 상황 모니터링"""
        
        # 이슈 상태 확인
        task = self._get_issue(task_id)
        if not task:
            return {'status': 'not_found'}
        
        # 댓글에서 AI 활동 확인
        comments = self._get_issue_comments(task_id)
        
        ai_comments = []
        for comment in comments:
            body = comment.get('body', '')
            if any(ai in body.lower() for ai in ['gemini', 'claude', 'codex', '🤖']):
                ai_comments.append({
                    'author': comment.get('author', {}).get('login', ''),
                    'created_at': comment.get('createdAt', ''),
                    'summary': body[:100] + '...' if len(body) > 100 else body
                })
        
        # PR 연결 확인
        linked_prs = self._get_linked_prs(task_id)
        
        return {
            'task_id': task_id,
            'state': task.get('state', ''),
            'ai_activities': len(ai_comments),
            'last_ai_comment': ai_comments[-1] if ai_comments else None,
            'linked_prs': linked_prs,
            'completion_percentage': self._estimate_completion(task, ai_comments, linked_prs)
        }
    
    def collect_ai_results(self, task_id: int) -> Dict:
        """AI 작업 결과 수집"""
        
        results = {
            'task_id': task_id,
            'ai_outputs': [],
            'generated_files': [],
            'pr_created': False,
            'tests_passed': False
        }
        
        # 댓글에서 AI 출력 수집
        comments = self._get_issue_comments(task_id)
        
        for comment in comments:
            body = comment.get('body', '')
            
            # AI 출력 패턴 찾기
            if '```' in body:
                # 코드 블록 추출
                code_blocks = re.findall(r'```[\s\S]*?```', body)
                for block in code_blocks:
                    results['ai_outputs'].append(block)
            
            # 파일 생성 패턴 찾기
            file_patterns = re.findall(r'Created file: (.*?)(?:\n|$)', body)
            results['generated_files'].extend(file_patterns)
            
            # PR 생성 확인
            if 'created PR' in body or 'PR #' in body:
                results['pr_created'] = True
            
            # 테스트 결과 확인
            if 'tests passed' in body or '✅' in body:
                results['tests_passed'] = True
        
        return results
    
    # === Helper Methods ===
    
    def _get_issue(self, issue_number: int) -> Optional[Dict]:
        """이슈 정보 가져오기"""
        
        cmd = f'gh issue view {issue_number} -R {self.repo} --json number,title,body,state,labels'
        
        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            if result.returncode == 0:
                return json.loads(result.stdout)
        except:
            pass
        
        return None
    
    def _create_task_issue(self, title: str, body: str, labels: List[str], 
                          parent_story: int) -> Dict:
        """Task 이슈 생성"""
        
        # 라벨이 존재하는지 확인하고 없으면 생성
        for label in labels:
            self._ensure_label_exists(label)
        
        # 이슈 생성
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write(body)
            body_file = f.name
        
        try:
            cmd = f'gh issue create -R {self.repo} --title "{title}" --body-file {body_file}'
            if labels:
                cmd += f' --label {",".join(labels)}'
            
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            
            if result.returncode == 0:
                # 이슈 번호 추출
                output = result.stdout.strip()
                if '#' in output:
                    issue_num = int(output.split('#')[1].split()[0])
                    
                    # Story 참조 추가
                    ref_comment = f"📌 Parent Story: #{parent_story}"
                    self._post_comment(issue_num, ref_comment)
                    
                    return {'success': True, 'task_id': issue_num}
            
            return {'success': False, 'error': result.stderr}
            
        finally:
            if os.path.exists(body_file):
                os.remove(body_file)
    
    def _ensure_label_exists(self, label: str):
        """라벨이 존재하는지 확인하고 없으면 생성"""
        
        # 라벨 색상 정의
        label_colors = {
            'task': '0366d6',
            'ai-gemini': 'FBCA04',
            'ai-claude': 'C5DEF5',
            'ai-codex': 'E99695'
        }
        
        # 라벨 존재 확인
        cmd = f'gh label list -R {self.repo} --json name'
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        
        if result.returncode == 0:
            labels = json.loads(result.stdout)
            existing = [l['name'] for l in labels]
            
            if label not in existing:
                # 라벨 생성
                color = label_colors.get(label, '808080')
                create_cmd = f'gh label create "{label}" -R {self.repo} --color "{color}"'
                subprocess.run(create_cmd, shell=True, capture_output=True, text=True)
    
    def _post_comment(self, issue_number: int, comment: str):
        """이슈에 댓글 작성"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write(comment)
            comment_file = f.name
        
        try:
            cmd = f'gh issue comment {issue_number} -R {self.repo} --body-file {comment_file}'
            subprocess.run(cmd, shell=True, capture_output=True, text=True)
        finally:
            if os.path.exists(comment_file):
                os.remove(comment_file)
    
    def _get_issue_comments(self, issue_number: int) -> List[Dict]:
        """이슈 댓글 가져오기"""
        
        cmd = f'gh api repos/{self.repo}/issues/{issue_number}/comments'
        
        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            if result.returncode == 0:
                return json.loads(result.stdout)
        except:
            pass
        
        return []
    
    def _get_linked_prs(self, issue_number: int) -> List[int]:
        """이슈에 연결된 PR 찾기"""
        
        # PR 목록에서 이슈 번호 참조 찾기
        cmd = f'gh pr list -R {self.repo} --search "#{issue_number}" --json number'
        
        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            if result.returncode == 0:
                prs = json.loads(result.stdout)
                return [pr['number'] for pr in prs]
        except:
            pass
        
        return []
    
    def _estimate_completion(self, task: Dict, ai_comments: List, linked_prs: List) -> int:
        """Task 완료율 추정"""
        
        completion = 0
        
        # 상태 체크 (30%)
        if task.get('state') == 'CLOSED':
            return 100
        
        # AI 활동 (30%)
        if ai_comments:
            completion += min(30, len(ai_comments) * 10)
        
        # PR 연결 (30%)
        if linked_prs:
            completion += 30
        
        # 체크리스트 (10%)
        body = task.get('body', '')
        total_checks = body.count('- [ ]') + body.count('- [x]')
        completed_checks = body.count('- [x]')
        if total_checks > 0:
            completion += int((completed_checks / total_checks) * 10)
        
        return min(100, completion)


# 사용 예시
if __name__ == "__main__":
    adapter = GitHubTaskAutomationAdapter()
    
    # Story #90에서 자동으로 Task 생성
    print("=== Story #90에서 Task 자동 생성 ===")
    result = adapter.create_tasks_from_story(90)
    
    if result.success:
        print(f"✅ {len(result.created_tasks)}개 Task 생성됨")
        for task_id, ai_name in result.ai_assignments.items():
            print(f"  - Task #{task_id} → {ai_name}")
    else:
        print(f"❌ 실패: {result.errors}")