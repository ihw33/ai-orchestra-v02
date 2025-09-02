"""
AI Orchestration Adapter
실제 AI CLI를 호출하는 Adapter 구현
"""

import subprocess
import json
import hashlib
from typing import Dict, List, Optional, Any
from datetime import datetime
import sys
import os

# Port 인터페이스 import
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from ports.orchestrator_port import OrchestratorPort, Task, Result, Provenance


class AIOrchestrationAdapter(OrchestratorPort):
    """
    AI CLI를 실제로 호출하는 Adapter
    페르소나 시스템의 문제를 해결하기 위한 구현
    """
    
    def __init__(self):
        self.ai_configs = {
            'gemini': {
                'command': 'gemini -p',
                'timeout': 120,
                'model': 'gemini'
            },
            'claude': {
                'command': 'claude -p', 
                'timeout': 180,
                'model': 'claude'
            },
            'codex': {
                'command': 'codex exec',
                'timeout': 120,
                'model': 'codex'
            }
        }
        
    def process_issue(self, issue_number: int) -> Result:
        """GitHub 이슈를 처리 - 실제 AI 실행"""
        
        # 1. 이슈 정보 가져오기
        issue_data = self._get_issue_data(issue_number)
        
        # 2. 작업 유형 분석
        task = self._analyze_issue(issue_data)
        
        # 3. AI 할당 및 실행
        result = self.assign_task(task)
        
        # 4. GitHub에 결과 포스팅
        self._post_to_github(issue_number, result)
        
        return result
    
    def execute_workflow(self, workflow_name: str, context: Dict) -> Result:
        """워크플로우 실행"""
        
        workflows = {
            'feature_development': ['gemini', 'codex', 'claude'],
            'bug_fix': ['claude', 'codex'],
            'analysis': ['gemini', 'claude']
        }
        
        ai_sequence = workflows.get(workflow_name, ['claude'])
        results = []
        
        for ai_name in ai_sequence:
            prompt = self._build_prompt(ai_name, context)
            result = self._execute_ai(ai_name, prompt)
            results.append(result)
            
            # 컨텍스트 업데이트 (다음 AI에게 전달)
            if result['success']:
                context['previous_output'] = result['output']
        
        return Result(
            task_id=context.get('task_id', 'workflow'),
            success=all(r['success'] for r in results),
            output=results,
            meta=Provenance(
                source='ai',
                model='multi',
                adr_reference='ADR-001'
            )
        )
    
    def assign_task(self, task: Task) -> Result:
        """작업을 적절한 AI에게 할당"""
        
        # 작업 유형별 AI 매핑
        ai_mapping = {
            'analysis': 'gemini',
            'implementation': 'codex',
            'review': 'claude',
            'test': 'claude'
        }
        
        ai_name = ai_mapping.get(task.type, 'claude')
        prompt = f"{task.title}\n\n{task.description}"
        
        # AI 실행
        result_data = self._execute_ai(ai_name, prompt)
        
        return Result(
            task_id=task.id,
            success=result_data['success'],
            output=result_data['output'],
            meta=Provenance(
                source='ai',
                model=ai_name,
                prompt_hash=self._hash_prompt(prompt),
                adr_reference='ADR-001'
            ),
            errors=[result_data['error']] if not result_data['success'] else None
        )
    
    def get_status(self, task_id: str) -> Dict:
        """작업 상태 조회"""
        # 실제 구현에서는 데이터베이스나 캐시에서 조회
        return {
            'task_id': task_id,
            'status': 'completed',
            'timestamp': datetime.now().isoformat()
        }
    
    def _execute_ai(self, ai_name: str, prompt: str) -> Dict:
        """실제 AI CLI 실행"""
        
        if ai_name not in self.ai_configs:
            return {
                'success': False,
                'output': None,
                'error': f'Unknown AI: {ai_name}'
            }
        
        config = self.ai_configs[ai_name]
        command = f'{config["command"]} "{prompt}"'
        
        print(f"🤖 실행 중: {ai_name}...")
        
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=config['timeout']
            )
            
            if result.returncode == 0:
                print(f"✅ {ai_name} 완료")
                return {
                    'success': True,
                    'output': result.stdout,
                    'error': None
                }
            else:
                print(f"❌ {ai_name} 실패")
                return {
                    'success': False,
                    'output': None,
                    'error': result.stderr
                }
                
        except subprocess.TimeoutExpired:
            print(f"⏰ {ai_name} 타임아웃")
            return {
                'success': False,
                'output': None,
                'error': f'Timeout after {config["timeout"]} seconds'
            }
        except Exception as e:
            print(f"❌ {ai_name} 에러: {str(e)}")
            return {
                'success': False,
                'output': None,
                'error': str(e)
            }
    
    def _get_issue_data(self, issue_number: int) -> Dict:
        """GitHub 이슈 정보 가져오기"""
        cmd = f"gh issue view {issue_number} -R ihw33/ai-orchestra-v02 --json title,body"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        
        if result.returncode == 0:
            return json.loads(result.stdout)
        else:
            return {'title': '', 'body': ''}
    
    def _analyze_issue(self, issue_data: Dict) -> Task:
        """이슈를 분석하여 Task로 변환"""
        title = issue_data.get('title', '')
        body = issue_data.get('body', '')
        
        # 작업 유형 결정
        task_type = 'implementation'  # 기본값
        if '분석' in title or 'analysis' in title.lower():
            task_type = 'analysis'
        elif '버그' in title or 'bug' in title.lower():
            task_type = 'bug_fix'
        elif '테스트' in title or 'test' in title.lower():
            task_type = 'test'
        
        return Task(
            id=f"task_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            type=task_type,
            title=title,
            description=body
        )
    
    def _build_prompt(self, ai_name: str, context: Dict) -> str:
        """AI별 프롬프트 생성"""
        base_prompt = context.get('prompt', '')
        
        if 'previous_output' in context:
            base_prompt = f"이전 결과:\n{context['previous_output'][:500]}\n\n{base_prompt}"
        
        return base_prompt
    
    def _hash_prompt(self, prompt: str) -> str:
        """프롬프트 해시 생성"""
        return hashlib.sha256(prompt.encode()).hexdigest()[:12]
    
    def _post_to_github(self, issue_number: int, result: Result):
        """결과를 GitHub에 포스팅"""
        
        comment = f"## 🤖 AI Adapter 실행 결과\n\n"
        
        if result.success:
            comment += "### ✅ 성공\n"
            comment += f"- Task ID: {result.task_id}\n"
            comment += f"- Model: {result.meta.model}\n"
            comment += f"- Timestamp: {result.meta.timestamp}\n\n"
            comment += "**출력:**\n```\n"
            comment += str(result.output)[:1000]
            comment += "\n```\n"
        else:
            comment += "### ❌ 실패\n"
            comment += f"- 에러: {result.errors}\n"
        
        comment += f"\n---\n*Provenance: {result.meta.source} | {result.meta.prompt_hash}*"
        
        # GitHub에 포스팅
        cmd = f'gh issue comment {issue_number} -R ihw33/ai-orchestra-v02 --body "{comment}"'
        subprocess.run(cmd, shell=True)


# 테스트 코드
if __name__ == "__main__":
    adapter = AIOrchestrationAdapter()
    
    # 간단한 테스트
    test_task = Task(
        id="test_001",
        type="analysis",
        title="테스트 작업",
        description="이것은 테스트입니다"
    )
    
    result = adapter.assign_task(test_task)
    print(f"테스트 결과: {result.success}")
    print(f"Provenance: {result.meta}")