"""
AI Command Port - AI별 특수 명령어 및 기능 인터페이스
Claude 서브에이전트, SuperClaude, 기타 AI 특수 기능 관리
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum

class AIType(Enum):
    """AI 유형"""
    CLAUDE = "claude"
    GEMINI = "gemini"
    CODEX = "codex"
    CURSOR = "cursor"

class CommandType(Enum):
    """명령어 유형"""
    SUBAGENT = "subagent"          # Claude 서브에이전트
    SUPERCLAUDE = "superclaude"    # /SC 명령어
    NATIVE = "native"               # 기본 명령어
    CUSTOM = "custom"               # 커스텀 명령어

@dataclass
class AICommand:
    """AI 명령어"""
    command: str
    description: str
    ai_type: AIType
    command_type: CommandType
    parameters: Optional[Dict] = None
    triggers: List[str] = None  # 자동 트리거 키워드

@dataclass
class AICapability:
    """AI 능력/기능"""
    ai_type: AIType
    subagents: List[str]  # 사용 가능한 서브에이전트
    commands: List[AICommand]  # 사용 가능한 명령어
    auto_triggers: Dict[str, str]  # 키워드 → 기능 매핑

@dataclass
class CommandResult:
    """명령어 실행 결과"""
    success: bool
    output: str
    used_command: str
    used_subagent: Optional[str] = None
    metadata: Dict = None

class AICommandPort(ABC):
    """AI 명령어 관리 인터페이스"""
    
    @abstractmethod
    def get_ai_capabilities(self, ai_type: AIType) -> AICapability:
        """AI의 능력/기능 조회"""
        pass
    
    @abstractmethod
    def select_best_command(self, ai_type: AIType, task_description: str) -> AICommand:
        """작업에 가장 적합한 명령어 선택"""
        pass
    
    @abstractmethod
    def format_command_with_context(self, command: AICommand, context: Dict) -> str:
        """컨텍스트를 포함한 명령어 포맷"""
        pass
    
    @abstractmethod
    def execute_with_command(self, ai_type: AIType, command: AICommand, 
                            prompt: str) -> CommandResult:
        """특수 명령어로 AI 실행"""
        pass
    
    @abstractmethod
    def detect_auto_triggers(self, prompt: str, ai_type: AIType) -> List[str]:
        """프롬프트에서 자동 트리거 감지"""
        pass

class SubagentSelectorPort(ABC):
    """서브에이전트 선택 인터페이스"""
    
    @abstractmethod
    def select_subagent(self, task_description: str) -> str:
        """작업에 적합한 서브에이전트 선택"""
        pass
    
    @abstractmethod
    def get_subagent_capabilities(self, subagent_name: str) -> Dict:
        """서브에이전트 능력 조회"""
        pass
    
    @abstractmethod
    def chain_subagents(self, tasks: List[str]) -> List[str]:
        """여러 작업에 대한 서브에이전트 체인 구성"""
        pass

class SuperClaudePort(ABC):
    """SuperClaude 명령어 인터페이스"""
    
    @abstractmethod
    def get_sc_commands(self) -> Dict[str, str]:
        """모든 /SC 명령어 목록"""
        pass
    
    @abstractmethod
    def select_sc_command(self, task_type: str) -> str:
        """작업 유형에 맞는 /SC 명령어 선택"""
        pass
    
    @abstractmethod
    def format_sc_prompt(self, command: str, content: str) -> str:
        """/SC 명령어 포함 프롬프트 포맷"""
        pass
    
    @abstractmethod
    def parse_sc_output(self, output: str) -> Dict:
        """/SC 출력 파싱"""
        pass