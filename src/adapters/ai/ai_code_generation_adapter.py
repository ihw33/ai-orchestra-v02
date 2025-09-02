"""
AI Code Generation Adapter
AI가 실제로 코드를 작성하고 커밋하는 구현
"""

import subprocess
import json
import re
import tempfile
import time
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from ports.ai_code_generation_port import (
    AICodeGenerationPort,
    CodeGenerationWorkflowPort,
    CodeGenerationRequest,
    GeneratedCode,
    CodeGenerationResult,
    CodeGenerationType
)
# from adapters.ai.claude_command_adapter import ClaudeCommandAdapter
# from adapters.github.branch_strategy_adapter import GitHubBranchStrategyAdapter
# from adapters.github.pr_adapter import GitHubPRAdapter
from ports.pr_creator_port import PRCreationRequest
from ports.ai_command_port import AIType

class AICodeGenerationAdapter(AICodeGenerationPort, CodeGenerationWorkflowPort):
    """AI 코드 생성 Adapter"""
    
    def __init__(self, repo: str = "ihw33/ai-orchestra-v02"):
        self.repo = repo
        # self.claude_adapter = ClaudeCommandAdapter()
        # self.branch_adapter = GitHubBranchStrategyAdapter(repo)
        # self.pr_adapter = GitHubPRAdapter(repo)
        self.golden_sets = self._load_golden_sets()
    
    def _load_golden_sets(self) -> Dict:
        """Golden Set 예제 로드"""
        return {
            'adapter': {
                'pattern': 'Port/Adapter 패턴',
                'example': 'src/adapters/github/pr_adapter.py'
            },
            'port': {
                'pattern': 'Port 인터페이스',
                'example': 'src/ports/pr_creator_port.py'
            },
            'workflow': {
                'pattern': '워크플로우',
                'example': 'src/workflows/code_review_workflow.py'
            }
        }
    
    # === AICodeGenerationPort 구현 ===
    
    def analyze_task(self, task_id: int) -> CodeGenerationRequest:
        """Task 분석하여 코드 생성 요청 생성"""
        
        # Task 정보 가져오기
        task_info = self._get_task_info(task_id)
        if not task_info:
            return None
        
        title = task_info.get('title', '')
        body = task_info.get('body', '')
        
        # 생성 유형 판단
        generation_type = self._determine_generation_type(title, body)
        
        # 요구사항 추출
        requirements = self._extract_requirements(body)
        
        # 대상 파일 찾기
        target_files = self._find_target_files(body)
        
        # Golden Set 예제 선택
        examples = self._select_golden_sets(generation_type, title)
        
        return CodeGenerationRequest(
            task_id=task_id,
            task_description=f"{title}\n\n{body}",
            generation_type=generation_type,
            target_files=target_files,
            requirements=requirements,
            examples=examples
        )
    
    def prepare_context(self, request: CodeGenerationRequest) -> Dict:
        """코드 생성을 위한 컨텍스트 준비"""
        
        context = {
            'task_id': request.task_id,
            'project_structure': self._get_project_structure(),
            'related_files': {},
            'golden_examples': {},
            'patterns': [],
            'dependencies': []
        }
        
        # 관련 파일 읽기
        if request.target_files:
            for file_path in request.target_files:
                if os.path.exists(file_path):
                    with open(file_path, 'r') as f:
                        context['related_files'][file_path] = f.read()
        
        # Golden Set 예제 읽기
        if request.examples:
            for example_path in request.examples:
                if os.path.exists(example_path):
                    with open(example_path, 'r') as f:
                        context['golden_examples'][example_path] = f.read()[:1000]  # 일부만
        
        # 패턴 추가
        if request.generation_type == CodeGenerationType.NEW_FILE:
            if 'adapter' in request.task_description.lower():
                context['patterns'].append('Port/Adapter 패턴 사용')
            if 'port' in request.task_description.lower():
                context['patterns'].append('인터페이스 정의')
        
        # 의존성 확인
        context['dependencies'] = self._check_dependencies(request)
        
        return context
    
    def generate_code(self, request: CodeGenerationRequest, 
                     context: Dict) -> List[GeneratedCode]:
        """AI를 사용한 코드 생성"""
        
        # AI 선택
        ai_name = self.select_ai_for_task(request)
        
        # 프롬프트 생성
        prompt = self.prepare_ai_prompt(request, context)
        
        # AI 실행
        print(f"🤖 {ai_name}가 코드 생성 중...")
        output = self.execute_ai_generation(ai_name, prompt)
        
        # 출력 파싱
        generated_codes = self.parse_ai_output(output)
        
        return generated_codes
    
    def validate_generated_code(self, code: List[GeneratedCode]) -> Tuple[bool, List[str]]:
        """생성된 코드 검증"""
        
        errors = []
        
        for generated in code:
            # 구문 검증 (Python인 경우)
            if generated.language == 'python':
                validation = self._validate_python_syntax(generated.content)
                if not validation[0]:
                    errors.append(f"{generated.file_path}: {validation[1]}")
            
            # 패턴 검증
            if 'adapter' in generated.file_path.lower():
                if 'Port' not in generated.content:
                    errors.append(f"{generated.file_path}: Port 인터페이스 import 누락")
            
            # 파일 크기 검증
            if len(generated.content) > 50000:
                errors.append(f"{generated.file_path}: 파일이 너무 큼")
        
        return len(errors) == 0, errors
    
    def apply_code_changes(self, code: List[GeneratedCode], 
                          branch_name: str) -> bool:
        """코드 변경사항 적용"""
        
        try:
            # 현재 브랜치 저장
            current_branch = subprocess.run(
                'git branch --show-current',
                shell=True, capture_output=True, text=True
            ).stdout.strip()
            
            # 작업 브랜치로 체크아웃
            subprocess.run(f'git checkout {branch_name}', shell=True, check=True)
            
            # 각 파일 적용
            for generated in code:
                if generated.action == 'create':
                    # 디렉토리 생성
                    os.makedirs(os.path.dirname(generated.file_path), exist_ok=True)
                    # 파일 생성
                    with open(generated.file_path, 'w') as f:
                        f.write(generated.content)
                    print(f"✅ Created: {generated.file_path}")
                    
                elif generated.action == 'modify':
                    # 파일 수정
                    with open(generated.file_path, 'w') as f:
                        f.write(generated.content)
                    print(f"✅ Modified: {generated.file_path}")
            
            return True
            
        except Exception as e:
            print(f"❌ 코드 적용 실패: {e}")
            # 원래 브랜치로 복구
            subprocess.run(f'git checkout {current_branch}', shell=True)
            return False
    
    def commit_and_push(self, branch_name: str, message: str) -> Optional[str]:
        """커밋 및 푸시"""
        
        try:
            # 변경사항 스테이징
            subprocess.run('git add .', shell=True, check=True)
            
            # 커밋
            commit_result = subprocess.run(
                f'git commit -m "{message}"',
                shell=True, capture_output=True, text=True
            )
            
            if commit_result.returncode != 0:
                print("변경사항이 없습니다")
                return None
            
            # 커밋 SHA 추출
            sha_result = subprocess.run(
                'git rev-parse HEAD',
                shell=True, capture_output=True, text=True
            )
            commit_sha = sha_result.stdout.strip()
            
            # 푸시
            push_result = subprocess.run(
                f'git push origin {branch_name}',
                shell=True, capture_output=True, text=True
            )
            
            if push_result.returncode == 0:
                print(f"✅ Pushed: {commit_sha[:8]}")
                return commit_sha
            else:
                print(f"❌ Push 실패: {push_result.stderr}")
                return None
                
        except Exception as e:
            print(f"❌ 커밋 실패: {e}")
            return None
    
    def create_pr_for_code(self, branch_name: str, task_id: int) -> Optional[int]:
        """생성된 코드로 PR 생성"""
        
        # Task 정보 가져오기
        task_info = self._get_task_info(task_id)
        if not task_info:
            return None
        
        # 부모 Story 찾기
        parent_story = self._find_parent_story(task_id)
        base_branch = 'main'
        
        if parent_story:
            # Story 브랜치가 있으면 그걸로
            story_branch = f"story/{parent_story}-feature"
            if self._branch_exists(story_branch):
                base_branch = story_branch
        
        # PR 생성
        pr_request = PRCreationRequest(
            title=f"[Task #{task_id}] {task_info['title']}",
            body=f"""## 🤖 AI가 생성한 코드

Task: #{task_id}

### 생성/수정된 파일
- 브랜치: `{branch_name}`
- 베이스: `{base_branch}`

### AI 정보
- 생성 시간: {datetime.now().strftime('%Y-%m-%d %H:%M')}

### 다음 단계
1. 코드 리뷰
2. 테스트 실행
3. 병합

Closes #{task_id}""",
            base_branch=base_branch,
            head_branch=branch_name,
            labels=['ai-generated', 'task']
        )
        
        pr = self.pr_adapter.create_pr(pr_request)
        
        if pr:
            print(f"✅ PR 생성: #{pr.number}")
            return pr.number
        
        return None
    
    # === CodeGenerationWorkflowPort 구현 ===
    
    def execute_code_generation_workflow(self, task_id: int) -> CodeGenerationResult:
        """전체 코드 생성 워크플로우 실행"""
        
        start_time = time.time()
        result = CodeGenerationResult(
            success=False,
            task_id=task_id,
            generated_files=[],
            errors=[]
        )
        
        print(f"\n🚀 Task #{task_id} 코드 생성 시작")
        
        # 1. Task 분석
        request = self.analyze_task(task_id)
        if not request:
            result.errors.append("Task 분석 실패")
            return result
        
        # 2. 컨텍스트 준비
        context = self.prepare_context(request)
        
        # 3. 브랜치 생성
        branch_name = self.branch_adapter.generate_branch_name('task', task_id, 'ai-generated')
        if not self.branch_adapter.create_branch(branch_name, 'main'):
            result.errors.append("브랜치 생성 실패")
            return result
        
        result.branch_name = branch_name
        print(f"📌 브랜치 생성: {branch_name}")
        
        # 4. 코드 생성
        generated_codes = self.generate_code(request, context)
        if not generated_codes:
            result.errors.append("코드 생성 실패")
            return result
        
        result.generated_files = generated_codes
        
        # 5. 코드 검증
        valid, errors = self.validate_generated_code(generated_codes)
        if not valid:
            result.errors.extend(errors)
            print(f"⚠️ 검증 실패: {errors}")
            # 계속 진행 (경고만)
        
        # 6. 코드 적용
        if not self.apply_code_changes(generated_codes, branch_name):
            result.errors.append("코드 적용 실패")
            return result
        
        # 7. 커밋 & 푸시
        commit_message = f"🤖 [Task #{task_id}] AI가 생성한 코드\n\n생성: {len(generated_codes)}개 파일"
        commit_sha = self.commit_and_push(branch_name, commit_message)
        
        if commit_sha:
            result.commit_sha = commit_sha
        else:
            result.errors.append("커밋/푸시 실패")
            return result
        
        # 8. PR 생성
        pr_number = self.create_pr_for_code(branch_name, task_id)
        if pr_number:
            result.pr_number = pr_number
            result.success = True
        else:
            result.errors.append("PR 생성 실패")
        
        # 실행 시간 기록
        result.execution_time = int(time.time() - start_time)
        
        print(f"\n✅ 워크플로우 완료 ({result.execution_time}초)")
        print(f"   생성 파일: {len(result.generated_files)}개")
        print(f"   PR: #{result.pr_number}")
        
        return result
    
    def select_ai_for_task(self, request: CodeGenerationRequest) -> str:
        """Task에 적합한 AI 선택"""
        
        task_lower = request.task_description.lower()
        
        # 키워드 기반 선택
        if any(word in task_lower for word in ['backend', 'api', 'database', '백엔드']):
            return 'codex'
        elif any(word in task_lower for word in ['design', 'architecture', '설계', '구조']):
            return 'gemini'
        else:
            return 'claude'  # 기본값
    
    def prepare_ai_prompt(self, request: CodeGenerationRequest, 
                         context: Dict) -> str:
        """AI 프롬프트 생성"""
        
        prompt = f"""Task #{request.task_id} 코드 생성

요구사항:
{request.requirements or request.task_description}

생성 유형: {request.generation_type.value}
"""
        
        # 대상 파일
        if request.target_files:
            prompt += f"\n대상 파일:\n"
            for file in request.target_files:
                prompt += f"- {file}\n"
        
        # 프로젝트 구조
        if context.get('project_structure'):
            prompt += f"\n프로젝트 구조:\n{context['project_structure'][:500]}\n"
        
        # Golden Set 예제
        if context.get('golden_examples'):
            prompt += f"\n참고 예제:\n"
            for path, content in list(context['golden_examples'].items())[:1]:
                prompt += f"파일: {path}\n```python\n{content[:500]}...\n```\n"
        
        # 패턴 적용
        if context.get('patterns'):
            prompt += f"\n적용할 패턴:\n"
            for pattern in context['patterns']:
                prompt += f"- {pattern}\n"
        
        # 지시사항
        prompt += """
지시사항:
1. 완전한 코드를 생성하세요
2. 주석은 최소화하세요
3. Port/Adapter 패턴을 준수하세요
4. 파일 경로를 명시하세요
5. 다음 형식으로 출력하세요:

```file:경로/파일명.py
코드 내용
```
"""
        
        return prompt
    
    def execute_ai_generation(self, ai_name: str, prompt: str) -> str:
        """AI 실행하여 코드 생성"""
        
        output = ""
        
        if ai_name == 'claude':
            # Claude는 /SC Implement 사용
            sc_prompt = f"/SC Implement\n\n{prompt}"
            output = self._execute_claude_sc(sc_prompt)
            
        elif ai_name == 'gemini':
            output = self._execute_gemini(prompt)
            
        elif ai_name == 'codex':
            output = self._execute_codex(prompt)
        
        return output
    
    def parse_ai_output(self, output: str) -> List[GeneratedCode]:
        """AI 출력 파싱"""
        
        generated_codes = []
        
        # 코드 블록 패턴: ```file:경로/파일명
        pattern = r'```(?:file:)?([^\n]+)\n([\s\S]*?)```'
        matches = re.findall(pattern, output)
        
        for file_info, content in matches:
            # 파일 경로 추출
            file_path = file_info.strip()
            if file_path.startswith('file:'):
                file_path = file_path[5:]
            
            # 언어 감지
            language = 'python'
            if file_path.endswith('.js'):
                language = 'javascript'
            elif file_path.endswith('.go'):
                language = 'go'
            
            # 액션 결정
            action = 'create'
            if os.path.exists(file_path):
                action = 'modify'
            
            generated_codes.append(GeneratedCode(
                file_path=file_path,
                content=content,
                language=language,
                action=action
            ))
        
        # 코드 블록이 없으면 전체를 하나의 파일로
        if not generated_codes and '```' not in output:
            # 기본 파일명 생성
            file_path = f"src/generated/code_{datetime.now().strftime('%Y%m%d_%H%M%S')}.py"
            generated_codes.append(GeneratedCode(
                file_path=file_path,
                content=output,
                language='python',
                action='create'
            ))
        
        return generated_codes
    
    def handle_generation_failure(self, task_id: int, error: str) -> Dict:
        """생성 실패 처리"""
        
        # 이슈에 실패 댓글
        self._post_issue_comment(
            task_id,
            f"❌ 코드 생성 실패\n\n에러: {error}\n\n다시 시도하거나 수동으로 작성이 필요합니다."
        )
        
        return {
            'task_id': task_id,
            'error': error,
            'action_taken': 'commented_on_issue'
        }
    
    # === Helper Methods ===
    
    def _get_task_info(self, task_id: int) -> Optional[Dict]:
        """Task 정보 조회"""
        cmd = f'gh issue view {task_id} -R {self.repo} --json number,title,body,labels'
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        
        if result.returncode == 0:
            return json.loads(result.stdout)
        return None
    
    def _determine_generation_type(self, title: str, body: str) -> CodeGenerationType:
        """생성 유형 판단"""
        text = f"{title} {body}".lower()
        
        if 'test' in text:
            return CodeGenerationType.TEST
        elif 'bug' in text or 'fix' in text:
            return CodeGenerationType.BUG_FIX
        elif 'refactor' in text:
            return CodeGenerationType.REFACTOR
        elif 'document' in text or 'doc' in text:
            return CodeGenerationType.DOCUMENTATION
        elif 'modify' in text or 'update' in text:
            return CodeGenerationType.MODIFY_FILE
        else:
            return CodeGenerationType.NEW_FILE
    
    def _extract_requirements(self, body: str) -> str:
        """요구사항 추출"""
        # 요구사항 섹션 찾기
        patterns = [
            r'## 요구사항\n([\s\S]*?)(?:\n##|$)',
            r'## Requirements\n([\s\S]*?)(?:\n##|$)',
            r'### 구현 내용\n([\s\S]*?)(?:\n###|$)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, body)
            if match:
                return match.group(1).strip()
        
        return body[:500]  # 본문 일부
    
    def _find_target_files(self, body: str) -> List[str]:
        """대상 파일 찾기"""
        files = []
        
        # 파일 경로 패턴
        pattern = r'(?:src/|tests/|docs/)[^\s\)]+\.(?:py|js|md)'
        matches = re.findall(pattern, body)
        files.extend(matches)
        
        return list(set(files))
    
    def _select_golden_sets(self, generation_type: CodeGenerationType, 
                           title: str) -> List[str]:
        """Golden Set 예제 선택"""
        examples = []
        
        title_lower = title.lower()
        
        if 'adapter' in title_lower:
            examples.append(self.golden_sets['adapter']['example'])
        elif 'port' in title_lower:
            examples.append(self.golden_sets['port']['example'])
        elif 'workflow' in title_lower:
            examples.append(self.golden_sets['workflow']['example'])
        
        return examples
    
    def _get_project_structure(self) -> str:
        """프로젝트 구조 가져오기"""
        cmd = 'find src -type f -name "*.py" | head -20'
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        return result.stdout
    
    def _check_dependencies(self, request: CodeGenerationRequest) -> List[str]:
        """의존성 확인"""
        deps = []
        
        # requirements.txt 확인
        if os.path.exists('requirements.txt'):
            with open('requirements.txt', 'r') as f:
                deps = [line.strip() for line in f.readlines()[:10]]
        
        return deps
    
    def _validate_python_syntax(self, code: str) -> Tuple[bool, str]:
        """Python 구문 검증"""
        try:
            compile(code, '<string>', 'exec')
            return True, ""
        except SyntaxError as e:
            return False, str(e)
    
    def _find_parent_story(self, task_id: int) -> Optional[int]:
        """Task의 부모 Story 찾기"""
        task_info = self._get_task_info(task_id)
        if task_info:
            body = task_info.get('body', '')
            match = re.search(r'(?:Story|Parent).*?#(\d+)', body, re.IGNORECASE)
            if match:
                return int(match.group(1))
        return None
    
    def _branch_exists(self, branch_name: str) -> bool:
        """브랜치 존재 확인"""
        cmd = f'git branch -r | grep "origin/{branch_name}"'
        result = subprocess.run(cmd, shell=True, capture_output=True)
        return result.returncode == 0
    
    def _execute_claude_sc(self, prompt: str) -> str:
        """Claude SuperClaude 실행"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write(prompt)
            prompt_file = f.name
        
        try:
            cmd = f'claude -p < {prompt_file}'
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=180)
            return result.stdout if result.returncode == 0 else ""
        finally:
            if os.path.exists(prompt_file):
                os.remove(prompt_file)
    
    def _execute_gemini(self, prompt: str) -> str:
        """Gemini 실행"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write(prompt)
            prompt_file = f.name
        
        try:
            cmd = f'gemini -p < {prompt_file}'
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=180)
            return result.stdout if result.returncode == 0 else ""
        finally:
            if os.path.exists(prompt_file):
                os.remove(prompt_file)
    
    def _execute_codex(self, prompt: str) -> str:
        """Codex 실행"""
        try:
            cmd = f'codex exec "{prompt[:1000]}"'  # 프롬프트 길이 제한
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=180)
            return result.stdout if result.returncode == 0 else ""
        except:
            return ""
    
    def _post_issue_comment(self, issue_number: int, comment: str):
        """이슈에 댓글 작성"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write(comment)
            comment_file = f.name
        
        try:
            cmd = f'gh issue comment {issue_number} -R {self.repo} --body-file {comment_file}'
            subprocess.run(cmd, shell=True)
        finally:
            if os.path.exists(comment_file):
                os.remove(comment_file)


# 사용 예시
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        task_id = int(sys.argv[1])
        adapter = AICodeGenerationAdapter()
        
        print(f"Task #{task_id} 코드 생성 테스트")
        result = adapter.execute_code_generation_workflow(task_id)
        
        if result.success:
            print(f"✅ 성공! PR: #{result.pr_number}")
        else:
            print(f"❌ 실패: {result.errors}")
    else:
        print("사용법: python ai_code_generation_adapter.py <task_id>")