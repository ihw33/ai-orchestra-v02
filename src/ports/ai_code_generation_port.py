"""
AI Code Generation Port - AI 코드 생성 워크플로우 인터페이스
AI가 실제로 코드를 작성하고 커밋하는 시스템
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

class CodeGenerationType(Enum):
    """코드 생성 유형"""
    NEW_FILE = "new_file"          # 새 파일 생성
    MODIFY_FILE = "modify_file"    # 기존 파일 수정
    REFACTOR = "refactor"          # 리팩터링
    BUG_FIX = "bug_fix"           # 버그 수정
    TEST = "test"                  # 테스트 코드
    DOCUMENTATION = "documentation" # 문서화

@dataclass
class CodeGenerationRequest:
    """코드 생성 요청"""
    task_id: int
    task_description: str
    generation_type: CodeGenerationType
    target_files: List[str] = None
    requirements: str = None
    constraints: List[str] = None
    examples: List[str] = None  # Golden Set 예제

@dataclass
class GeneratedCode:
    """생성된 코드"""
    file_path: str
    content: str
    language: str
    action: str  # create, modify, delete
    diff: Optional[str] = None  # 수정의 경우 diff

@dataclass
class CodeGenerationResult:
    """코드 생성 결과"""
    success: bool
    task_id: int
    generated_files: List[GeneratedCode]
    commit_sha: Optional[str] = None
    branch_name: Optional[str] = None
    pr_number: Optional[int] = None
    errors: List[str] = None
    ai_used: str = None
    execution_time: int = 0  # 초

class AICodeGenerationPort(ABC):
    """AI 코드 생성 인터페이스"""
    
    @abstractmethod
    def analyze_task(self, task_id: int) -> CodeGenerationRequest:
        """Task 분석하여 코드 생성 요청 생성"""
        pass
    
    @abstractmethod
    def prepare_context(self, request: CodeGenerationRequest) -> Dict:
        """코드 생성을 위한 컨텍스트 준비"""
        pass
    
    @abstractmethod
    def generate_code(self, request: CodeGenerationRequest, 
                     context: Dict) -> List[GeneratedCode]:
        """AI를 사용한 코드 생성"""
        pass
    
    @abstractmethod
    def validate_generated_code(self, code: List[GeneratedCode]) -> Tuple[bool, List[str]]:
        """생성된 코드 검증"""
        pass
    
    @abstractmethod
    def apply_code_changes(self, code: List[GeneratedCode], 
                          branch_name: str) -> bool:
        """코드 변경사항 적용"""
        pass
    
    @abstractmethod
    def commit_and_push(self, branch_name: str, message: str) -> Optional[str]:
        """커밋 및 푸시"""
        pass
    
    @abstractmethod
    def create_pr_for_code(self, branch_name: str, task_id: int) -> Optional[int]:
        """생성된 코드로 PR 생성"""
        pass

class CodeGenerationWorkflowPort(ABC):
    """코드 생성 워크플로우 인터페이스"""
    
    @abstractmethod
    def execute_code_generation_workflow(self, task_id: int) -> CodeGenerationResult:
        """전체 코드 생성 워크플로우 실행"""
        pass
    
    @abstractmethod
    def select_ai_for_task(self, request: CodeGenerationRequest) -> str:
        """Task에 적합한 AI 선택"""
        pass
    
    @abstractmethod
    def prepare_ai_prompt(self, request: CodeGenerationRequest, 
                         context: Dict) -> str:
        """AI 프롬프트 생성"""
        pass
    
    @abstractmethod
    def execute_ai_generation(self, ai_name: str, prompt: str) -> str:
        """AI 실행하여 코드 생성"""
        pass
    
    @abstractmethod
    def parse_ai_output(self, output: str) -> List[GeneratedCode]:
        """AI 출력 파싱"""
        pass
    
    @abstractmethod
    def handle_generation_failure(self, task_id: int, error: str) -> Dict:
        """생성 실패 처리"""
        pass