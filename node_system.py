#!/usr/bin/env python3
"""
Node System - Atomic 작업 단위 정의 및 실행
"""

from enum import Enum
from dataclasses import dataclass
from typing import List, Dict, Any, Optional
from datetime import datetime
import subprocess
import json
import time
from evolution_logger import get_logger

class NodeType(Enum):
    """노드 타입 정의 - 실제 작업 기준"""
    # GitHub 작업
    CREATE_ISSUE = "create_issue"
    ADD_COMMENT = "add_comment"
    UPDATE_LABELS = "update_labels"
    CREATE_PR = "create_pr"
    MERGE_PR = "merge_pr"
    
    # 코드 작성
    WRITE_FUNCTION = "write_function"
    CREATE_CLASS = "create_class"
    FIX_BUG_LINE = "fix_bug_line"
    WRITE_TEST_CASE = "write_test_case"
    
    # 파일 조작
    CREATE_FILE = "create_file"
    UPDATE_FILE_SECTION = "update_file_section"
    DELETE_FILE = "delete_file"
    
    # 분석/리서치
    ANALYZE_CODE = "analyze_code"
    RESEARCH_TOPIC = "research_topic"
    FIND_PATTERN = "find_pattern"
    
    # 테스트
    RUN_TEST = "run_test"
    CHECK_COVERAGE = "check_coverage"
    VALIDATE_OUTPUT = "validate_output"
    ACTIONS_LOCAL_TEST = "actions_local_test"  # GitHub Actions 로컬 테스트
    
    # 리뷰/검토
    REVIEW_CODE = "review_code"
    SUGGEST_IMPROVEMENT = "suggest_improvement"
    
    # 배포/운영
    RUN_COMMAND = "run_command"
    CHECK_STATUS = "check_status"
    
    # 커뮤니케이션
    SEND_NOTIFICATION = "send_notification"
    CREATE_REPORT = "create_report"
    
    # 페르소나 (메타 노드)
    APPLY_PERSONA = "apply_persona"
    
    # MCP 서버 노드들
    MCP_MEMORY_STORE = "mcp_memory_store"         # 메모리 저장
    MCP_MEMORY_SEARCH = "mcp_memory_search"       # 메모리 검색
    MCP_CONTEXT7_RESOLVE = "mcp_context7_resolve" # 라이브러리 ID 해석
    MCP_CONTEXT7_DOCS = "mcp_context7_docs"       # 문서 조회

class NodeStatus(Enum):
    """노드 실행 상태"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"

class ExecutionMode(Enum):
    """실행 모드"""
    PARALLEL = "-p"  # 비대화형 병렬 실행
    INTERACTIVE = "interactive"  # 대화형
    DECISION = "decision"  # Thomas 승인 필요

@dataclass
class NodeState:
    """노드 상태 데이터"""
    id: str
    type: NodeType
    issue_number: str = None  # GitHub 이슈 번호 추가
    status: NodeStatus = NodeStatus.PENDING
    input_data: Dict = None
    output_data: Dict = None
    error_message: str = ""
    execution_time: float = 0
    assigned_ai: str = ""
    dependencies: List[str] = None
    
    def __post_init__(self):
        if self.input_data is None:
            self.input_data = {}
        if self.output_data is None:
            self.output_data = {}
        if self.dependencies is None:
            self.dependencies = []

class AtomicNode:
    """기본 노드 클래스"""
    
    def __init__(self, state: NodeState, executor: str = "claude", mode: ExecutionMode = ExecutionMode.PARALLEL):
        self.state = state
        self.executor = executor  # AI 실행자
        self.mode = mode
        self.start_time = None
        self.end_time = None
    
    def can_run(self) -> bool:
        """실행 가능 여부 체크"""
        return self.state.status == NodeStatus.PENDING and len(self.state.dependencies) == 0
    
    def validate_input(self) -> bool:
        """입력 검증"""
        # 노드 타입별 필수 입력 체크
        required_inputs = self.get_required_inputs()
        for key in required_inputs:
            if key not in self.state.input_data:
                self.state.error_message = f"Missing required input: {key}"
                return False
        return True
    
    def get_required_inputs(self) -> List[str]:
        """노드 타입별 필수 입력"""
        requirements = {
            NodeType.CREATE_ISSUE: ["title", "body"],
            NodeType.WRITE_FUNCTION: ["function_name", "parameters"],
            NodeType.FIX_BUG_LINE: ["file_path", "line_number"],
            NodeType.RUN_TEST: ["test_path"],
        }
        return requirements.get(self.state.type, [])
    
    def execute(self) -> Dict:
        """노드 실행"""
        self.start_time = time.time()
        self.state.status = NodeStatus.RUNNING
        logger = get_logger()  # Evolution Logger 가져오기
        
        try:
            # 입력 검증
            if not self.validate_input():
                self.state.status = NodeStatus.FAILED
                # 실패 로깅
                logger.on_node_complete(self.state.type.value, success=False)
                return {"error": self.state.error_message}
            
            # AI 실행자로 작업 수행
            result = self.execute_with_ai()
            
            # 성공 처리
            self.state.status = NodeStatus.COMPLETED
            self.state.output_data = result
            
            # 성공 로깅 및 진화 상태 업데이트
            evo_result = logger.on_node_complete(self.state.type.value, success=True)
            
            # 레벨업 알림
            if evo_result.get('level_up'):
                print(f"\n🎉 레벨업! {evo_result['form']} Lv.{evo_result['level']} ({evo_result['stage_name']})\n")
            
        except Exception as e:
            # 실패 처리
            self.state.status = NodeStatus.FAILED
            self.state.error_message = str(e)
            result = {"error": str(e)}
            # 실패 로깅
            logger.on_node_complete(self.state.type.value, success=False)
        
        finally:
            self.end_time = time.time()
            self.state.execution_time = self.end_time - self.start_time
        
        return result
    
    def execute_with_ai(self) -> Dict:
        """AI를 사용한 실제 작업 실행"""
        prompt = self.build_prompt()
        
        if self.mode == ExecutionMode.PARALLEL:
            # -p 모드 실행
            cmd = f"{self.executor} -p '{prompt}'"
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            return {"output": result.stdout, "error": result.stderr}
            
        elif self.mode == ExecutionMode.INTERACTIVE:
            # 대화형 실행
            print(f"💬 {self.executor}: {prompt}")
            # 실제로는 대화형 인터페이스 구현 필요
            return {"output": "Interactive mode placeholder"}
            
        elif self.mode == ExecutionMode.DECISION:
            # Thomas 승인 필요
            print(f"⚠️ Thomas 승인 필요: {prompt}")
            return {"output": "Waiting for approval"}
    
    def build_prompt(self) -> str:
        """노드 타입별 프롬프트 생성"""
        prompts = {
            NodeType.CREATE_ISSUE: f"Create GitHub issue: {self.state.input_data}",
            NodeType.WRITE_FUNCTION: f"Write function: {self.state.input_data}",
            NodeType.FIX_BUG_LINE: f"Fix bug at {self.state.input_data}",
            NodeType.ANALYZE_CODE: f"Analyze code: {self.state.input_data}",
        }
        return prompts.get(self.state.type, json.dumps(self.state.input_data))
    
    def rollback(self) -> bool:
        """실행 취소"""
        # 노드 타입별 롤백 로직
        print(f"Rolling back node {self.state.id}")
        self.state.status = NodeStatus.PENDING
        self.state.output_data = {}
        return True

class PersonaNode(AtomicNode):
    """페르소나 노드 - 다른 노드의 실행 방식 변경"""
    
    def __init__(self, persona_type: str):
        state = NodeState(
            id=f"persona_{persona_type}",
            type=NodeType.APPLY_PERSONA,
            input_data={"persona": persona_type}
        )
        super().__init__(state)
        self.persona_type = persona_type
        self.traits = self.get_persona_traits()
    
    def get_persona_traits(self) -> Dict:
        """페르소나별 특성"""
        personas = {
            "speedster": {
                "traits": ["빠른실행", "효율성", "단순화"],
                "prompt_modifier": "Complete this as quickly as possible",
                "time_multiplier": 0.5
            },
            "perfectionist": {
                "traits": ["디테일", "품질", "테스트"],
                "prompt_modifier": "Ensure perfect quality and handle all edge cases",
                "time_multiplier": 1.5
            },
            "critic": {
                "traits": ["비판적", "문제지적", "개선요구"],
                "prompt_modifier": "Find all potential issues and problems",
                "time_multiplier": 1.2
            },
            "minimalist": {
                "traits": ["간결", "핵심만", "제거"],
                "prompt_modifier": "Keep it minimal and remove unnecessary parts",
                "time_multiplier": 0.8
            }
        }
        return personas.get(self.persona_type, {})
    
    def apply_to_node(self, target_node: AtomicNode) -> AtomicNode:
        """다른 노드에 페르소나 적용"""
        # 프롬프트 수정
        original_prompt = target_node.build_prompt()
        modifier = self.traits.get("prompt_modifier", "")
        target_node.build_prompt = lambda: f"{modifier}\n{original_prompt}"
        
        # 시간 예측 조정
        time_mult = self.traits.get("time_multiplier", 1.0)
        # 예상 시간 조정 로직
        
        return target_node

# 노드 팩토리
class NodeFactory:
    """노드 생성 팩토리"""
    
    @staticmethod
    def create_node(node_type: NodeType, **kwargs) -> AtomicNode:
        """노드 타입에 따른 노드 생성"""
        state = NodeState(
            id=kwargs.get('id', f"{node_type.value}_{datetime.now().timestamp()}"),
            type=node_type,
            issue_number=kwargs.get('issue_number'),  # 이슈 번호 추가
            input_data=kwargs.get('input_data', {}),
            dependencies=kwargs.get('dependencies', [])
        )
        
        executor = kwargs.get('executor', 'claude')
        mode = kwargs.get('mode', ExecutionMode.PARALLEL)
        
        # 페르소나 노드는 특별 처리
        if node_type == NodeType.APPLY_PERSONA:
            return PersonaNode(kwargs.get('persona_type', 'neutral'))
        
        return AtomicNode(state, executor, mode)
    
    @staticmethod
    def create_from_instruction(instruction: str) -> List[AtomicNode]:
        """자연어 지시에서 노드 생성"""
        nodes = []
        
        # 키워드 기반 노드 매칭
        if "이슈" in instruction and "생성" in instruction:
            nodes.append(NodeFactory.create_node(NodeType.CREATE_ISSUE))
        
        if "버그" in instruction or "수정" in instruction:
            nodes.append(NodeFactory.create_node(NodeType.ANALYZE_CODE))
            nodes.append(NodeFactory.create_node(NodeType.FIX_BUG_LINE))
            nodes.append(NodeFactory.create_node(NodeType.RUN_TEST))
        
        if "분석" in instruction:
            nodes.append(NodeFactory.create_node(NodeType.ANALYZE_CODE))
            nodes.append(NodeFactory.create_node(NodeType.CREATE_REPORT))
        
        if any(keyword in instruction.lower() for keyword in ["workflow", "actions", "ci/cd", ".github"]):
            nodes.append(NodeFactory.create_node(
                NodeType.ACTIONS_LOCAL_TEST,
                executor='act',
                input_data={'workflow_path': '.github/workflows/'}
            ))
        
        return nodes

# 사용 예시
if __name__ == "__main__":
    # 1. 단일 노드 생성 및 실행
    print("=== 단일 노드 테스트 ===")
    node = NodeFactory.create_node(
        NodeType.CREATE_ISSUE,
        input_data={
            "title": "테스트 이슈",
            "body": "자동 생성된 이슈입니다"
        },
        executor="claude",
        mode=ExecutionMode.PARALLEL
    )
    
    if node.can_run():
        result = node.execute()
        print(f"실행 결과: {result}")
        print(f"실행 시간: {node.state.execution_time:.2f}초")
    
    # 2. 페르소나 적용
    print("\n=== 페르소나 적용 테스트 ===")
    persona = PersonaNode("speedster")
    fast_node = persona.apply_to_node(node)
    print(f"Speedster 페르소나 적용됨")
    
    # 3. 자연어에서 노드 생성
    print("\n=== 자연어 → 노드 변환 ===")
    instruction = "버그를 수정하고 테스트해줘"
    nodes = NodeFactory.create_from_instruction(instruction)
    print(f"생성된 노드: {[n.state.type.value for n in nodes]}")