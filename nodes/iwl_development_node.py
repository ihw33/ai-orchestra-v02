#!/usr/bin/env python3
"""
IWL Development Node
GitHub 이슈를 파싱하여 작업을 분해하고 적합한 페르소나를 선정하여 작업을 할당하는 노드
"""

import json
import os
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# 프로젝트 루트를 Python path에 추가
sys.path.append(str(Path(__file__).parent.parent))

from core.protocol import WorkflowRequest, WorkflowResult
from personas.persona_loader import PersonaLoader
from personas.subagent_selector import SubagentSelector


class IWLDevelopmentNode:
    """IWL 개발을 위한 특화된 노드"""
    
    def __init__(self):
        self.persona_loader = PersonaLoader()
        self.subagent_selector = SubagentSelector()
        self.iwl_repo = "ihw33/iwl-v5-rebuild"
        
        # IWL 특화 키워드 맵핑
        self.iwl_keywords = {
            'frontend': ['ui', 'component', 'react', 'nextjs', 'interface', 'design'],
            'backend': ['api', 'server', 'database', 'auth', 'supabase'],
            'ai': ['ai', 'ml', 'llm', 'openai', 'claude', 'gemini', 'learning'],
            'learning': ['curriculum', 'course', 'lesson', 'progress', 'gamification'],
            'analytics': ['kpi', 'metrics', 'tracking', 'dashboard', 'reporting'],
            'payment': ['stripe', 'billing', 'subscription', 'payment'],
            'infrastructure': ['docker', 'deployment', 'ci/cd', 'monitoring']
        }
        
    def parse_github_issue(self, issue_id: str) -> Dict:
        """GitHub 이슈 정보를 파싱"""
        try:
            # GitHub CLI로 이슈 정보 가져오기
            cmd = f"gh issue view {issue_id} -R {self.iwl_repo} --json title,body,labels,assignees"
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            
            if result.returncode != 0:
                raise Exception(f"GitHub 이슈 조회 실패: {result.stderr}")
                
            issue_data = json.loads(result.stdout)
            return {
                'id': issue_id,
                'title': issue_data.get('title', ''),
                'body': issue_data.get('body', ''),
                'labels': [label['name'] for label in issue_data.get('labels', [])],
                'assignees': [user['login'] for user in issue_data.get('assignees', [])]
            }
            
        except Exception as e:
            print(f"이슈 파싱 오류: {e}")
            return {}
    
    def analyze_task_type(self, title: str, body: str, labels: List[str]) -> str:
        """작업 유형을 분석하여 카테고리 결정"""
        content = f"{title} {body}".lower()
        
        # 라벨 우선 확인
        for label in labels:
            if 'frontend' in label.lower():
                return 'frontend'
            elif 'backend' in label.lower():
                return 'backend'
            elif 'ai' in label.lower() or 'ml' in label.lower():
                return 'ai'
        
        # 키워드 기반 분석
        for category, keywords in self.iwl_keywords.items():
            for keyword in keywords:
                if keyword in content:
                    return category
        
        return 'general'
    
    def break_down_task(self, issue: Dict) -> List[Dict]:
        """작업을 세부 단위로 분해"""
        title = issue.get('title', '')
        body = issue.get('body', '')
        task_type = self.analyze_task_type(title, body, issue.get('labels', []))
        
        # IWL 특화 작업 분해 템플릿
        task_templates = {
            'frontend': [
                {'name': 'UI 컴포넌트 설계', 'persona': 'ui-ux-designer', 'priority': 1},
                {'name': 'React 컴포넌트 구현', 'persona': 'frontend-developer', 'priority': 2},
                {'name': 'Tailwind CSS 스타일링', 'persona': 'frontend-developer', 'priority': 3},
                {'name': '반응형 테스트', 'persona': 'qa-engineer', 'priority': 4}
            ],
            'backend': [
                {'name': 'API 엔드포인트 설계', 'persona': 'backend-architect', 'priority': 1},
                {'name': '데이터베이스 스키마 업데이트', 'persona': 'data-engineer', 'priority': 2},
                {'name': 'API 구현', 'persona': 'backend-developer', 'priority': 3},
                {'name': 'API 테스트', 'persona': 'qa-engineer', 'priority': 4}
            ],
            'ai': [
                {'name': 'AI 모델 선정', 'persona': 'ai-architect', 'priority': 1},
                {'name': 'API 통합 구현', 'persona': 'ai-engineer', 'priority': 2},
                {'name': '성능 최적화', 'persona': 'ai-engineer', 'priority': 3},
                {'name': 'AI 응답 품질 테스트', 'persona': 'qa-engineer', 'priority': 4}
            ],
            'learning': [
                {'name': '학습 알고리즘 설계', 'persona': 'learning-specialist', 'priority': 1},
                {'name': '콘텐츠 구조 정의', 'persona': 'content-designer', 'priority': 2},
                {'name': '진도 추적 시스템', 'persona': 'backend-developer', 'priority': 3},
                {'name': '학습 효과 측정', 'persona': 'data-analyst', 'priority': 4}
            ]
        }
        
        base_tasks = task_templates.get(task_type, [
            {'name': '요구사항 분석', 'persona': 'business-analyst', 'priority': 1},
            {'name': '기술 구현', 'persona': 'senior-developer', 'priority': 2},
            {'name': '품질 검증', 'persona': 'qa-engineer', 'priority': 3}
        ])
        
        # 실제 작업명에 이슈 제목 반영
        tasks = []
        for task in base_tasks:
            tasks.append({
                'name': f"{task['name']} - {title}",
                'description': body[:200] + "..." if len(body) > 200 else body,
                'persona': task['persona'],
                'priority': task['priority'],
                'estimated_hours': self._estimate_hours(task['name']),
                'dependencies': []
            })
        
        return tasks
    
    def select_personas(self, tasks: List[Dict]) -> Dict[str, Dict]:
        """각 작업에 적합한 페르소나 선정"""
        selected_personas = {}
        
        for task in tasks:
            persona_type = task['persona']
            
            # 페르소나 로드 (가용성 및 워크로드 고려)
            personas = self.persona_loader.get_personas_by_type(persona_type)
            if not personas:
                # 대체 페르소나 찾기
                personas = self.persona_loader.get_available_personas()
            
            if personas:
                # 가장 적합한 페르소나 선택 (경험, 가용성, 워크로드 기준)
                best_persona = self._select_best_persona(personas, task)
                selected_personas[task['name']] = {
                    'persona': best_persona,
                    'task': task,
                    'estimated_start': self._calculate_start_time(task['priority']),
                    'estimated_completion': self._calculate_completion_time(
                        task['estimated_hours'], task['priority']
                    )
                }
        
        return selected_personas
    
    def create_work_assignments(self, issue: Dict, personas: Dict[str, Dict]) -> List[Dict]:
        """작업 할당서 생성"""
        assignments = []
        
        for task_name, assignment in personas.items():
            persona = assignment['persona']
            task = assignment['task']
            
            assignment_doc = {
                'issue_id': issue['id'],
                'issue_title': issue['title'],
                'task_name': task_name,
                'task_description': task['description'],
                'persona_id': persona.get('id'),
                'persona_name': persona.get('name'),
                'persona_role': persona.get('role'),
                'priority': task['priority'],
                'estimated_hours': task['estimated_hours'],
                'estimated_start': assignment['estimated_start'],
                'estimated_completion': assignment['estimated_completion'],
                'status': 'assigned',
                'created_at': datetime.now().isoformat(),
                'repository': self.iwl_repo
            }
            
            assignments.append(assignment_doc)
        
        return assignments
    
    def monitor_progress(self, assignments: List[Dict]) -> Dict:
        """작업 진행 상황 모니터링"""
        progress_summary = {
            'total_tasks': len(assignments),
            'completed': 0,
            'in_progress': 0,
            'pending': 0,
            'blocked': 0,
            'overall_progress': 0.0,
            'estimated_completion': None,
            'tasks': assignments
        }
        
        for assignment in assignments:
            status = assignment.get('status', 'pending')
            if status == 'completed':
                progress_summary['completed'] += 1
            elif status == 'in_progress':
                progress_summary['in_progress'] += 1
            elif status == 'blocked':
                progress_summary['blocked'] += 1
            else:
                progress_summary['pending'] += 1
        
        if progress_summary['total_tasks'] > 0:
            progress_summary['overall_progress'] = (
                progress_summary['completed'] / progress_summary['total_tasks'] * 100
            )
        
        return progress_summary
    
    def create_pr_when_complete(self, issue_id: str, assignments: List[Dict]) -> Optional[str]:
        """작업 완료 시 PR 자동 생성"""
        progress = self.monitor_progress(assignments)
        
        if progress['completed'] == progress['total_tasks']:
            # 모든 작업이 완료되면 PR 생성
            branch_name = f"iwl-issue-{issue_id}"
            pr_title = f"[IWL] Issue #{issue_id} Implementation"
            
            pr_body = self._generate_pr_body(issue_id, assignments, progress)
            
            try:
                # PR 생성 명령
                cmd = f"""gh pr create \\
                    --title "{pr_title}" \\
                    --body "{pr_body}" \\
                    --head {branch_name} \\
                    --base master \\
                    -R {self.iwl_repo}"""
                
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                
                if result.returncode == 0:
                    pr_url = result.stdout.strip()
                    return pr_url
                else:
                    print(f"PR 생성 실패: {result.stderr}")
            
            except Exception as e:
                print(f"PR 생성 오류: {e}")
        
        return None
    
    def execute(self, request: WorkflowRequest) -> WorkflowResult:
        """메인 실행 로직"""
        try:
            issue_id = request.parameters.get('issue_id')
            if not issue_id:
                return WorkflowResult(
                    success=False,
                    message="issue_id 파라미터가 필요합니다",
                    data={}
                )
            
            # 1. GitHub 이슈 파싱
            issue = self.parse_github_issue(issue_id)
            if not issue:
                return WorkflowResult(
                    success=False,
                    message=f"이슈 #{issue_id}를 찾을 수 없습니다",
                    data={}
                )
            
            # 2. 작업 분해
            tasks = self.break_down_task(issue)
            
            # 3. 페르소나 선정
            personas = self.select_personas(tasks)
            
            # 4. 작업 할당서 생성
            assignments = self.create_work_assignments(issue, personas)
            
            # 5. 진행 상황 초기화
            progress = self.monitor_progress(assignments)
            
            # 6. 결과 저장
            self._save_assignments(issue_id, assignments)
            
            return WorkflowResult(
                success=True,
                message=f"이슈 #{issue_id} 작업 분해 및 할당 완료",
                data={
                    'issue': issue,
                    'tasks': tasks,
                    'assignments': assignments,
                    'progress': progress
                }
            )
            
        except Exception as e:
            return WorkflowResult(
                success=False,
                message=f"IWL 개발 노드 실행 오류: {str(e)}",
                data={}
            )
    
    def _estimate_hours(self, task_name: str) -> int:
        """작업 시간 추정"""
        if '설계' in task_name or 'design' in task_name.lower():
            return 8
        elif '구현' in task_name or 'implement' in task_name.lower():
            return 16
        elif '테스트' in task_name or 'test' in task_name.lower():
            return 4
        else:
            return 8
    
    def _select_best_persona(self, personas: List[Dict], task: Dict) -> Dict:
        """가장 적합한 페르소나 선택"""
        # 간단한 스코어링 시스템
        best_persona = None
        best_score = -1
        
        for persona in personas:
            score = 0
            
            # 가용성 점수
            if persona.get('availability', True):
                score += 10
            
            # 스킬 매칭 점수
            required_skills = self._extract_required_skills(task)
            persona_skills = persona.get('skills', {})
            
            for skill in required_skills:
                if skill in persona_skills:
                    score += persona_skills[skill]
            
            # 경험 점수
            experience = persona.get('experience', [])
            for exp in experience:
                if any(keyword in exp.get('project', '').lower() for keyword in ['iwl', 'learning']):
                    score += exp.get('rating', 0) * 2
            
            if score > best_score:
                best_score = score
                best_persona = persona
        
        return best_persona or personas[0]  # 기본값으로 첫 번째 페르소나
    
    def _extract_required_skills(self, task: Dict) -> List[str]:
        """작업에서 필요한 스킬 추출"""
        task_text = f"{task['name']} {task.get('description', '')}".lower()
        
        skills = []
        if 'react' in task_text:
            skills.append('react')
        if 'api' in task_text:
            skills.append('api')
        if 'database' in task_text:
            skills.append('database')
        if 'ai' in task_text:
            skills.append('ai')
        if 'design' in task_text:
            skills.append('design')
        
        return skills
    
    def _calculate_start_time(self, priority: int) -> str:
        """시작 시간 계산"""
        from datetime import datetime, timedelta
        
        delay_hours = (priority - 1) * 8  # 우선순위에 따른 지연
        start_time = datetime.now() + timedelta(hours=delay_hours)
        return start_time.isoformat()
    
    def _calculate_completion_time(self, estimated_hours: int, priority: int) -> str:
        """완료 예상 시간 계산"""
        from datetime import datetime, timedelta
        
        delay_hours = (priority - 1) * 8
        completion_time = datetime.now() + timedelta(hours=delay_hours + estimated_hours)
        return completion_time.isoformat()
    
    def _generate_pr_body(self, issue_id: str, assignments: List[Dict], progress: Dict) -> str:
        """PR 본문 생성"""
        body = f"""## Summary
이슈 #{issue_id}에 대한 구현이 완료되었습니다.

## 완료된 작업
"""
        
        for assignment in assignments:
            if assignment.get('status') == 'completed':
                body += f"- {assignment['task_name']} (담당: {assignment['persona_name']})\n"
        
        body += f"""
## 진행 상황
- 총 작업: {progress['total_tasks']}
- 완료: {progress['completed']}
- 전체 진도: {progress['overall_progress']:.1f}%

## 테스트
- [ ] 단위 테스트 통과
- [ ] 통합 테스트 통과
- [ ] 사용자 테스트 완료

## 검토 요청
@ihw33 리뷰 부탁드립니다.

🤖 Generated with [IWL Orchestra System](https://github.com/ihw33/ai-orchestra-v02)
"""
        return body
    
    def _save_assignments(self, issue_id: str, assignments: List[Dict]):
        """할당 정보 저장"""
        assignments_dir = Path(__file__).parent.parent / "pipeline_results"
        assignments_dir.mkdir(exist_ok=True)
        
        filename = assignments_dir / f"iwl_assignments_{issue_id}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump({
                'issue_id': issue_id,
                'assignments': assignments,
                'created_at': datetime.now().isoformat(),
                'total_tasks': len(assignments)
            }, f, ensure_ascii=False, indent=2)


def main():
    """CLI 인터페이스"""
    import argparse
    
    parser = argparse.ArgumentParser(description='IWL Development Node')
    parser.add_argument('--issue-id', required=True, help='GitHub 이슈 ID')
    parser.add_argument('--monitor', action='store_true', help='진행 상황 모니터링')
    
    args = parser.parse_args()
    
    node = IWLDevelopmentNode()
    
    if args.monitor:
        # 진행 상황 모니터링
        assignments_file = Path(__file__).parent.parent / "pipeline_results" / f"iwl_assignments_{args.issue_id}.json"
        if assignments_file.exists():
            with open(assignments_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                assignments = data['assignments']
                progress = node.monitor_progress(assignments)
                print(json.dumps(progress, ensure_ascii=False, indent=2))
        else:
            print(f"할당 파일을 찾을 수 없습니다: {assignments_file}")
    else:
        # 작업 분해 및 할당
        request = WorkflowRequest(
            workflow_id="iwl_development",
            parameters={'issue_id': args.issue_id}
        )
        
        result = node.execute(request)
        print(json.dumps({
            'success': result.success,
            'message': result.message,
            'data': result.data
        }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()