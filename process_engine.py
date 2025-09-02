#!/usr/bin/env python3
"""
Process Engine - 노드들을 조합하여 워크플로우 실행
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum
import asyncio
import json
from datetime import datetime

from node_system import AtomicNode, NodeFactory, NodeType, NodeStatus, ExecutionMode

class ProcessStatus(Enum):
    """프로세스 상태"""
    READY = "ready"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"

@dataclass
class ProcessState:
    """프로세스 상태 관리"""
    id: str
    name: str
    issue_number: str = None  # GitHub 이슈 번호 추가
    status: ProcessStatus = ProcessStatus.READY
    nodes: List[AtomicNode] = None
    edges: Dict[str, List[str]] = None  # node_id -> [next_node_ids]
    current_nodes: List[str] = None
    completed_nodes: List[str] = None
    context: Dict = None  # 프로세스 전체 공유 데이터
    start_time: datetime = None
    end_time: datetime = None
    
    def __post_init__(self):
        if self.nodes is None:
            self.nodes = []
        if self.edges is None:
            self.edges = {}
        if self.current_nodes is None:
            self.current_nodes = []
        if self.completed_nodes is None:
            self.completed_nodes = []
        if self.context is None:
            self.context = {}

class WorkflowProcess:
    """워크플로우 프로세스 - 노드들의 DAG"""
    
    def __init__(self, name: str, process_id: str = None, issue_number: str = None):
        self.state = ProcessState(
            id=process_id or f"process_{datetime.now().timestamp()}",
            name=name,
            issue_number=issue_number
        )
        self.node_map = {}  # id -> node 매핑
    
    def add_node(self, node: AtomicNode) -> str:
        """노드 추가"""
        self.state.nodes.append(node)
        self.node_map[node.state.id] = node
        return node.state.id
    
    def connect_nodes(self, from_id: str, to_id: str, condition: Dict = None):
        """노드 연결"""
        if from_id not in self.state.edges:
            self.state.edges[from_id] = []
        
        edge_info = {"to": to_id}
        if condition:
            edge_info["condition"] = condition
        
        self.state.edges[from_id].append(to_id)
    
    def get_start_nodes(self) -> List[AtomicNode]:
        """시작 노드 찾기 (의존성 없는 노드)"""
        all_targets = set()
        for targets in self.state.edges.values():
            all_targets.update(targets)
        
        start_nodes = []
        for node in self.state.nodes:
            if node.state.id not in all_targets:
                start_nodes.append(node)
        
        return start_nodes
    
    async def execute_async(self) -> Dict:
        """비동기 실행 (병렬 처리 지원)"""
        self.state.status = ProcessStatus.RUNNING
        self.state.start_time = datetime.now()
        
        try:
            # 시작 노드들 찾기
            current_batch = self.get_start_nodes()
            
            while current_batch:
                # 현재 배치 병렬 실행
                tasks = []
                for node in current_batch:
                    if node.can_run():
                        tasks.append(self._execute_node_async(node))
                
                # 모든 노드 완료 대기
                results = await asyncio.gather(*tasks)
                
                # 다음 실행 가능한 노드들 찾기
                current_batch = self._get_next_batch()
            
            self.state.status = ProcessStatus.COMPLETED
            
        except Exception as e:
            self.state.status = ProcessStatus.FAILED
            raise e
        
        finally:
            self.state.end_time = datetime.now()
        
        return self.get_results()
    
    async def _execute_node_async(self, node: AtomicNode) -> Dict:
        """노드 비동기 실행"""
        # 실제로는 asyncio를 사용한 비동기 실행
        # 여기서는 동기 실행을 비동기로 래핑
        return await asyncio.to_thread(node.execute)
    
    def execute(self) -> Dict:
        """동기 실행"""
        self.state.status = ProcessStatus.RUNNING
        self.state.start_time = datetime.now()
        
        try:
            # 시작 노드들부터 순차 실행
            executed = set()
            to_execute = [n.state.id for n in self.get_start_nodes()]
            
            while to_execute:
                node_id = to_execute.pop(0)
                if node_id in executed:
                    continue
                
                node = self.node_map[node_id]
                
                # 의존성 체크
                if self._check_dependencies(node):
                    # 노드 실행
                    result = node.execute()
                    executed.add(node_id)
                    self.state.completed_nodes.append(node_id)
                    
                    # 다음 노드 추가
                    if node_id in self.state.edges:
                        to_execute.extend(self.state.edges[node_id])
                else:
                    # 의존성 미충족 - 나중에 다시 시도
                    to_execute.append(node_id)
            
            self.state.status = ProcessStatus.COMPLETED
            
        except Exception as e:
            self.state.status = ProcessStatus.FAILED
            raise e
        
        finally:
            self.state.end_time = datetime.now()
        
        return self.get_results()
    
    def _check_dependencies(self, node: AtomicNode) -> bool:
        """노드 의존성 체크"""
        for dep_id in node.state.dependencies:
            if dep_id not in self.state.completed_nodes:
                return False
        return True
    
    def _get_next_batch(self) -> List[AtomicNode]:
        """다음 실행 가능한 노드 배치"""
        next_batch = []
        
        for node in self.state.nodes:
            if node.state.id not in self.state.completed_nodes and \
               self._check_dependencies(node):
                next_batch.append(node)
        
        return next_batch
    
    def pause(self):
        """일시 정지"""
        self.state.status = ProcessStatus.PAUSED
    
    def resume(self):
        """재개"""
        if self.state.status == ProcessStatus.PAUSED:
            self.state.status = ProcessStatus.RUNNING
    
    def get_results(self) -> Dict:
        """결과 수집"""
        results = {
            "process_id": self.state.id,
            "name": self.state.name,
            "status": self.state.status.value,
            "duration": None,
            "nodes": {}
        }
        
        if self.state.start_time and self.state.end_time:
            duration = (self.state.end_time - self.state.start_time).total_seconds()
            results["duration"] = duration
        
        for node in self.state.nodes:
            results["nodes"][node.state.id] = {
                "type": node.state.type.value,
                "status": node.state.status.value,
                "output": node.state.output_data,
                "execution_time": node.state.execution_time
            }
        
        return results

class ProcessBuilder:
    """프로세스 빌더 - 쉽게 프로세스 구성"""
    
    def __init__(self, name: str, issue_number: str = None):
        self.process = WorkflowProcess(name, issue_number=issue_number)
        self.last_node_id = None
    
    def add(self, node_type: NodeType, **kwargs) -> 'ProcessBuilder':
        """노드 추가 (체이닝)"""
        node = NodeFactory.create_node(node_type, **kwargs)
        node_id = self.process.add_node(node)
        
        # 이전 노드와 자동 연결
        if self.last_node_id:
            self.process.connect_nodes(self.last_node_id, node_id)
        
        self.last_node_id = node_id
        return self
    
    def parallel(self, *nodes) -> 'ProcessBuilder':
        """병렬 노드 추가"""
        parallel_ids = []
        
        for node_info in nodes:
            if isinstance(node_info, dict):
                node = NodeFactory.create_node(**node_info)
            else:
                node = node_info
            
            node_id = self.process.add_node(node)
            parallel_ids.append(node_id)
            
            # 이전 노드와 모두 연결
            if self.last_node_id:
                self.process.connect_nodes(self.last_node_id, node_id)
        
        # 병렬 노드들을 리스트로 저장
        self.last_node_id = parallel_ids
        return self
    
    def build(self) -> WorkflowProcess:
        """프로세스 빌드"""
        return self.process

# 사전 정의된 프로세스 템플릿
class ProcessTemplates:
    """자주 사용하는 프로세스 템플릿"""
    
    @staticmethod
    def bug_fix_process(issue_number: str = None) -> WorkflowProcess:
        """버그 수정 프로세스"""
        return ProcessBuilder("Bug Fix Process", issue_number=issue_number) \
            .add(NodeType.ANALYZE_CODE, executor="claude") \
            .add(NodeType.FIX_BUG_LINE, executor="codex") \
            .add(NodeType.WRITE_TEST_CASE, executor="gemini") \
            .add(NodeType.RUN_TEST, executor="gemini") \
            .add(NodeType.CREATE_PR, executor="claude") \
            .build()
    
    @staticmethod
    def feature_development(issue_number: str = None) -> WorkflowProcess:
        """기능 개발 프로세스"""
        builder = ProcessBuilder("Feature Development", issue_number=issue_number)
        
        # 설계 단계
        builder.add(NodeType.ANALYZE_CODE, executor="claude", mode=ExecutionMode.PARALLEL)
        
        # 병렬 구현
        builder.parallel(
            {"type": NodeType.WRITE_FUNCTION, "executor": "codex"},
            {"type": NodeType.CREATE_CLASS, "executor": "codex"},
            {"type": NodeType.WRITE_TEST_CASE, "executor": "gemini"}
        )
        
        # 테스트 및 리뷰
        builder.add(NodeType.RUN_TEST, executor="gemini")
        builder.add(NodeType.REVIEW_CODE, executor="claude")
        builder.add(NodeType.CREATE_PR, executor="claude")
        
        return builder.build()
    
    @staticmethod
    def research_process(issue_number: str = None) -> WorkflowProcess:
        """리서치 프로세스"""
        builder = ProcessBuilder("Research Process", issue_number=issue_number)
        
        # 병렬 리서치
        builder.parallel(
            {"type": NodeType.RESEARCH_TOPIC, "executor": "claude"},
            {"type": NodeType.RESEARCH_TOPIC, "executor": "gemini"},
            {"type": NodeType.RESEARCH_TOPIC, "executor": "codex"}
        )
        
        # 분석 및 보고
        builder.add(NodeType.ANALYZE_CODE, executor="claude")
        builder.add(NodeType.CREATE_REPORT, executor="claude")
        
        return builder.build()

# 사용 예시
if __name__ == "__main__":
    import asyncio
    
    # 1. 간단한 프로세스 생성
    print("=== 버그 수정 프로세스 ===")
    bug_fix = ProcessTemplates.bug_fix_process()
    
    # 동기 실행
    results = bug_fix.execute()
    print(f"프로세스 상태: {results['status']}")
    print(f"실행 시간: {results.get('duration', 0):.2f}초")
    
    # 2. 빌더로 커스텀 프로세스 생성
    print("\n=== 커스텀 프로세스 ===")
    custom = ProcessBuilder("Custom Process") \
        .add(NodeType.CREATE_ISSUE, input_data={"title": "Test"}) \
        .add(NodeType.ANALYZE_CODE) \
        .parallel(
            {"type": NodeType.WRITE_FUNCTION, "executor": "codex"},
            {"type": NodeType.WRITE_TEST_CASE, "executor": "gemini"}
        ) \
        .add(NodeType.RUN_TEST) \
        .build()
    
    # 비동기 실행 예시
    async def run_async():
        results = await custom.execute_async()
        print(f"비동기 실행 완료: {results['status']}")
    
    # asyncio.run(run_async())