"""
Claude Command Adapter
Claude 서브에이전트 및 SuperClaude 명령어 구현
"""

import subprocess
import re
import tempfile
from typing import Dict, List, Optional, Any
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from ports.ai_command_port import (
    AICommandPort,
    SubagentSelectorPort,
    SuperClaudePort,
    AIType,
    CommandType,
    AICommand,
    AICapability,
    CommandResult
)

class ClaudeCommandAdapter(AICommandPort, SubagentSelectorPort, SuperClaudePort):
    """Claude 명령어 및 서브에이전트 Adapter"""
    
    def __init__(self):
        self.sc_commands = self._init_superclaude_commands()
        self.subagents = self._init_subagents()
        self.keyword_triggers = self._init_keyword_triggers()
    
    def _init_superclaude_commands(self) -> Dict[str, str]:
        """SuperClaude 명령어 초기화"""
        return {
            '/SC Design': '시스템 및 UI/UX 디자인',
            '/SC Implement': '코드 구현',
            '/SC Test': '테스트 전략',
            '/SC Debug': '디버깅',
            '/SC Optimize': '성능 최적화',
            '/SC Security': '보안 분석',
            '/SC Document': '기술 문서화',
            '/SC Review': '코드 리뷰',
            '/SC Deploy': '배포 전략',
            '/SC Database': '데이터베이스 설계',
            '/SC API': 'API 개발',
            '/SC Mobile': '모바일 개발',
            '/SC Frontend': '프론트엔드 개발',
            '/SC Backend': '백엔드 개발',
            '/SC Data': '데이터 분석',
            '/SC Infrastructure': '클라우드 인프라'
        }
    
    def _init_subagents(self) -> Dict[str, Dict]:
        """서브에이전트 정의"""
        return {
            'code-reviewer': {
                'triggers': ['코드 리뷰', 'code review', 'PR review', '리뷰'],
                'description': '코드 품질 검토 및 개선 제안',
                'capabilities': ['품질 검사', '베스트 프랙티스', '보안 취약점']
            },
            'backend-architect': {
                'triggers': ['백엔드', 'backend', 'API', '서버', 'database'],
                'description': '백엔드 아키텍처 설계 및 구현',
                'capabilities': ['API 설계', 'DB 스키마', '마이크로서비스']
            },
            'ui-ux-designer': {
                'triggers': ['UI', 'UX', '디자인', 'frontend', '인터페이스'],
                'description': 'UI/UX 디자인 및 프론트엔드',
                'capabilities': ['와이어프레임', '디자인 시스템', '접근성']
            },
            'business-analyst': {
                'triggers': ['분석', 'KPI', '메트릭', '비즈니스', 'analytics'],
                'description': '비즈니스 분석 및 메트릭',
                'capabilities': ['성과 지표', '대시보드', '보고서']
            },
            'ai-engineer': {
                'triggers': ['AI', 'LLM', '머신러닝', 'ML', 'prompt'],
                'description': 'AI/LLM 시스템 개발',
                'capabilities': ['프롬프트 엔지니어링', 'RAG', 'Fine-tuning']
            },
            'search-specialist': {
                'triggers': ['검색', 'search', '조사', 'research'],
                'description': '심층 검색 및 조사',
                'capabilities': ['웹 검색', '문헌 조사', '경쟁 분석']
            },
            'api-documenter': {
                'triggers': ['API 문서', 'OpenAPI', 'Swagger', 'documentation'],
                'description': 'API 문서화',
                'capabilities': ['OpenAPI 스펙', 'SDK 생성', '예제 코드']
            },
            'prompt-engineer': {
                'triggers': ['프롬프트', 'prompt', '최적화'],
                'description': '프롬프트 최적화',
                'capabilities': ['프롬프트 패턴', '체인', '성능 개선']
            }
        }
    
    def _init_keyword_triggers(self) -> Dict[str, str]:
        """키워드 → 기능 매핑"""
        return {
            # 코드 리뷰 관련
            '코드 리뷰': 'code-reviewer',
            'code review': 'code-reviewer',
            'PR 리뷰': 'code-reviewer',
            '리뷰해': 'code-reviewer',
            
            # 구현 관련
            '구현해': '/SC Implement',
            '만들어': '/SC Implement',
            'implement': '/SC Implement',
            
            # 디버깅 관련
            '버그': '/SC Debug',
            '에러': '/SC Debug',
            '오류': '/SC Debug',
            'debug': '/SC Debug',
            
            # 테스트 관련
            '테스트': '/SC Test',
            'test': '/SC Test',
            '검증': '/SC Test',
            
            # API 관련
            'API': '/SC API',
            'REST': '/SC API',
            'GraphQL': '/SC API',
            
            # 문서화 관련
            '문서': '/SC Document',
            'document': '/SC Document',
            'README': '/SC Document'
        }
    
    # === AICommandPort 구현 ===
    
    def get_ai_capabilities(self, ai_type: AIType) -> AICapability:
        """AI 능력 조회"""
        
        if ai_type != AIType.CLAUDE:
            return AICapability(
                ai_type=ai_type,
                subagents=[],
                commands=[],
                auto_triggers={}
            )
        
        # Claude 명령어 목록 생성
        commands = []
        
        # SuperClaude 명령어
        for cmd, desc in self.sc_commands.items():
            commands.append(AICommand(
                command=cmd,
                description=desc,
                ai_type=AIType.CLAUDE,
                command_type=CommandType.SUPERCLAUDE
            ))
        
        # 서브에이전트
        subagent_names = list(self.subagents.keys())
        
        return AICapability(
            ai_type=AIType.CLAUDE,
            subagents=subagent_names,
            commands=commands,
            auto_triggers=self.keyword_triggers
        )
    
    def select_best_command(self, ai_type: AIType, task_description: str) -> AICommand:
        """작업에 적합한 명령어 선택"""
        
        task_lower = task_description.lower()
        
        # 1. 서브에이전트 트리거 확인
        for agent_name, agent_info in self.subagents.items():
            for trigger in agent_info['triggers']:
                if trigger in task_lower:
                    return AICommand(
                        command=agent_name,
                        description=agent_info['description'],
                        ai_type=AIType.CLAUDE,
                        command_type=CommandType.SUBAGENT,
                        triggers=agent_info['triggers']
                    )
        
        # 2. SuperClaude 명령어 확인
        for keyword, command in self.keyword_triggers.items():
            if keyword in task_lower and command.startswith('/SC'):
                return AICommand(
                    command=command,
                    description=self.sc_commands[command],
                    ai_type=AIType.CLAUDE,
                    command_type=CommandType.SUPERCLAUDE
                )
        
        # 3. 기본값: /SC Implement
        return AICommand(
            command='/SC Implement',
            description='코드 구현',
            ai_type=AIType.CLAUDE,
            command_type=CommandType.SUPERCLAUDE
        )
    
    def format_command_with_context(self, command: AICommand, context: Dict) -> str:
        """명령어와 컨텍스트 포맷"""
        
        formatted = ""
        
        if command.command_type == CommandType.SUPERCLAUDE:
            # SuperClaude 명령어 포맷
            formatted = f"{command.command}\n\n"
            formatted += f"작업: {context.get('task_description', '')}\n\n"
            
            if 'files' in context:
                formatted += "관련 파일:\n"
                for file in context['files']:
                    formatted += f"- {file}\n"
                formatted += "\n"
            
            if 'requirements' in context:
                formatted += "요구사항:\n"
                formatted += context['requirements'] + "\n"
        
        elif command.command_type == CommandType.SUBAGENT:
            # 서브에이전트 활성화
            formatted = f"@{command.command}\n\n"
            formatted += f"{context.get('task_description', '')}\n"
            
            # 서브에이전트별 특수 컨텍스트
            if command.command == 'code-reviewer':
                formatted += "\n코드 리뷰 체크리스트:\n"
                formatted += "- 코드 품질\n"
                formatted += "- 보안 취약점\n"
                formatted += "- 성능 이슈\n"
                formatted += "- 베스트 프랙티스\n"
        
        return formatted
    
    def execute_with_command(self, ai_type: AIType, command: AICommand, 
                            prompt: str) -> CommandResult:
        """특수 명령어로 실행"""
        
        if ai_type != AIType.CLAUDE:
            return CommandResult(
                success=False,
                output="이 어댑터는 Claude 전용입니다",
                used_command=""
            )
        
        # 명령어 포함 프롬프트 생성
        full_prompt = self.format_command_with_context(
            command,
            {'task_description': prompt}
        )
        
        # 임시 파일에 저장
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write(full_prompt)
            prompt_file = f.name
        
        try:
            # Claude 실행
            cmd = f'claude -p < {prompt_file}'
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=120)
            
            if result.returncode == 0:
                return CommandResult(
                    success=True,
                    output=result.stdout,
                    used_command=command.command,
                    used_subagent=command.command if command.command_type == CommandType.SUBAGENT else None,
                    metadata={'command_type': command.command_type.value}
                )
            else:
                return CommandResult(
                    success=False,
                    output=result.stderr,
                    used_command=command.command
                )
        
        except subprocess.TimeoutExpired:
            return CommandResult(
                success=False,
                output="실행 시간 초과",
                used_command=command.command
            )
        finally:
            if os.path.exists(prompt_file):
                os.remove(prompt_file)
    
    def detect_auto_triggers(self, prompt: str, ai_type: AIType) -> List[str]:
        """자동 트리거 감지"""
        
        if ai_type != AIType.CLAUDE:
            return []
        
        triggers = []
        prompt_lower = prompt.lower()
        
        for keyword, trigger in self.keyword_triggers.items():
            if keyword in prompt_lower:
                triggers.append(trigger)
        
        return list(set(triggers))  # 중복 제거
    
    # === SubagentSelectorPort 구현 ===
    
    def select_subagent(self, task_description: str) -> str:
        """서브에이전트 선택"""
        
        task_lower = task_description.lower()
        
        # 가장 많이 매칭되는 서브에이전트 선택
        best_agent = None
        max_matches = 0
        
        for agent_name, agent_info in self.subagents.items():
            matches = sum(1 for trigger in agent_info['triggers'] if trigger in task_lower)
            if matches > max_matches:
                max_matches = matches
                best_agent = agent_name
        
        return best_agent or 'code-reviewer'  # 기본값
    
    def get_subagent_capabilities(self, subagent_name: str) -> Dict:
        """서브에이전트 능력 조회"""
        
        return self.subagents.get(subagent_name, {})
    
    def chain_subagents(self, tasks: List[str]) -> List[str]:
        """서브에이전트 체인 구성"""
        
        chain = []
        for task in tasks:
            agent = self.select_subagent(task)
            chain.append(agent)
        
        return chain
    
    # === SuperClaudePort 구현 ===
    
    def get_sc_commands(self) -> Dict[str, str]:
        """SuperClaude 명령어 목록"""
        
        return self.sc_commands
    
    def select_sc_command(self, task_type: str) -> str:
        """작업 유형별 /SC 명령어 선택"""
        
        task_lower = task_type.lower()
        
        # 작업 유형 → 명령어 매핑
        type_mapping = {
            'review': '/SC Review',
            'implement': '/SC Implement',
            'test': '/SC Test',
            'debug': '/SC Debug',
            'design': '/SC Design',
            'api': '/SC API',
            'document': '/SC Document',
            'optimize': '/SC Optimize',
            'security': '/SC Security',
            'deploy': '/SC Deploy'
        }
        
        for key, cmd in type_mapping.items():
            if key in task_lower:
                return cmd
        
        return '/SC Implement'  # 기본값
    
    def format_sc_prompt(self, command: str, content: str) -> str:
        """/SC 프롬프트 포맷"""
        
        return f"{command}\n\n{content}"
    
    def parse_sc_output(self, output: str) -> Dict:
        """/SC 출력 파싱"""
        
        parsed = {
            'raw_output': output,
            'sections': {},
            'code_blocks': [],
            'recommendations': []
        }
        
        # 코드 블록 추출
        code_pattern = r'```[\s\S]*?```'
        code_blocks = re.findall(code_pattern, output)
        parsed['code_blocks'] = code_blocks
        
        # 섹션 추출 (## 제목)
        sections = re.split(r'^##\s+', output, flags=re.MULTILINE)
        for section in sections[1:]:  # 첫 번째는 빈 문자열
            lines = section.split('\n')
            if lines:
                title = lines[0].strip()
                content = '\n'.join(lines[1:])
                parsed['sections'][title] = content
        
        # 추천사항 추출 (- 로 시작하는 줄)
        rec_pattern = r'^-\s+(.+)$'
        recommendations = re.findall(rec_pattern, output, flags=re.MULTILINE)
        parsed['recommendations'] = recommendations
        
        return parsed


# 사용 예시
if __name__ == "__main__":
    adapter = ClaudeCommandAdapter()
    
    # 능력 조회
    print("=== Claude 능력 ===")
    capabilities = adapter.get_ai_capabilities(AIType.CLAUDE)
    print(f"서브에이전트: {capabilities.subagents}")
    print(f"명령어 수: {len(capabilities.commands)}")
    
    # 명령어 선택
    print("\n=== 명령어 선택 ===")
    
    test_tasks = [
        "이 코드를 리뷰해줘",
        "API를 구현해줘",
        "버그를 수정해줘",
        "테스트를 작성해줘"
    ]
    
    for task in test_tasks:
        command = adapter.select_best_command(AIType.CLAUDE, task)
        print(f"{task} → {command.command} ({command.command_type.value})")