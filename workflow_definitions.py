#!/usr/bin/env python3
"""
워크플로우 정의 - DAG (Directed Acyclic Graph) 기반
각 워크플로우는 노드(작업 단위)와 엣지(연결)로 구성
"""

from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum

class NodeType(Enum):
    """작업 노드 타입"""
    ANALYZE = "analyze"          # 분석
    DESIGN = "design"           # 설계
    IMPLEMENT = "implement"     # 구현
    TEST = "test"              # 테스트
    REVIEW = "review"          # 리뷰
    DOCUMENT = "document"      # 문서화
    DEPLOY = "deploy"          # 배포
    MONITOR = "monitor"        # 모니터링
    RESEARCH = "research"      # 리서치
    VALIDATE = "validate"      # 검증

@dataclass
class WorkflowNode:
    """워크플로우 노드 정의"""
    id: str
    type: NodeType
    ai_assignment: str  # 담당 AI
    command: str        # 실행 명령
    parallel: bool = False  # 병렬 실행 가능 여부
    dependencies: List[str] = None  # 선행 노드들

@dataclass
class WorkflowProcess:
    """워크플로우 프로세스 (DAG)"""
    name: str
    description: str
    nodes: List[WorkflowNode]
    trigger_patterns: List[str]  # 이 프로세스를 트리거하는 패턴들
    required_confirmation: bool = True  # Thomas 컨펌 필요 여부

class WorkflowRegistry:
    """사전 정의된 워크플로우 모음"""
    
    def __init__(self):
        # 재사용 가능한 노드 블록 정의
        self.node_blocks = {
            # 기본 블록
            "analyze": WorkflowNode("analyze", NodeType.ANALYZE, "gemini", "요구사항 분석"),
            "design": WorkflowNode("design", NodeType.DESIGN, "claude", "설계"),
            "implement": WorkflowNode("implement", NodeType.IMPLEMENT, "codex", "구현"),
            "test": WorkflowNode("test", NodeType.TEST, "gemini", "테스트"),
            "review": WorkflowNode("review", NodeType.REVIEW, "claude", "리뷰"),
            "document": WorkflowNode("document", NodeType.DOCUMENT, "claude", "문서화"),
            "deploy": WorkflowNode("deploy", NodeType.DEPLOY, "codex", "배포"),
            "monitor": WorkflowNode("monitor", NodeType.MONITOR, "gemini", "모니터링"),
            
            # 병렬 블록
            "parallel_research": [
                WorkflowNode("research1", NodeType.RESEARCH, "gemini", "기술 조사", parallel=True),
                WorkflowNode("research2", NodeType.RESEARCH, "claude", "사례 분석", parallel=True),
                WorkflowNode("research3", NodeType.RESEARCH, "codex", "코드 예제", parallel=True)
            ],
            "parallel_review": [
                WorkflowNode("review1", NodeType.REVIEW, "gemini", "아키텍처 리뷰", parallel=True),
                WorkflowNode("review2", NodeType.REVIEW, "claude", "코드 품질 리뷰", parallel=True),
                WorkflowNode("review3", NodeType.TEST, "codex", "테스트 커버리지", parallel=True)
            ]
        }
        
        self.processes = {
            # 1. 기능 개발 프로세스
            "feature_development": WorkflowProcess(
                name="기능 개발 프로세스",
                description="새 기능을 분석-설계-구현-테스트하는 표준 프로세스",
                nodes=[
                    WorkflowNode("f1", NodeType.ANALYZE, "gemini", "Issue 분석 및 요구사항 정리"),
                    WorkflowNode("f2", NodeType.DESIGN, "claude", "아키텍처 설계", dependencies=["f1"]),
                    WorkflowNode("f3", NodeType.IMPLEMENT, "codex", "코드 구현", dependencies=["f2"]),
                    WorkflowNode("f4", NodeType.TEST, "gemini", "테스트 작성 및 실행", dependencies=["f3"]),
                    WorkflowNode("f5", NodeType.REVIEW, "claude", "코드 리뷰", dependencies=["f3", "f4"])
                ],
                trigger_patterns=["만들어", "구현", "개발", "추가", "feature", "새로운 기능"]
            ),
            
            # 2. 버그 수정 프로세스
            "bug_fix": WorkflowProcess(
                name="버그 수정 프로세스",
                description="버그를 분석-수정-테스트하는 프로세스",
                nodes=[
                    WorkflowNode("b1", NodeType.ANALYZE, "claude", "버그 원인 분석"),
                    WorkflowNode("b2", NodeType.IMPLEMENT, "codex", "버그 수정", dependencies=["b1"]),
                    WorkflowNode("b3", NodeType.TEST, "gemini", "수정 검증", dependencies=["b2"]),
                    WorkflowNode("b4", NodeType.DOCUMENT, "claude", "수정 내역 문서화", dependencies=["b3"])
                ],
                trigger_patterns=["수정", "고쳐", "버그", "에러", "오류", "fix", "bug"]
            ),
            
            # 3. 리서치 프로세스
            "research": WorkflowProcess(
                name="리서치 프로세스",
                description="조사-분석-정리를 병렬로 수행하는 프로세스",
                nodes=[
                    WorkflowNode("r1", NodeType.RESEARCH, "gemini", "기술 조사", parallel=True),
                    WorkflowNode("r2", NodeType.RESEARCH, "claude", "사례 분석", parallel=True),
                    WorkflowNode("r3", NodeType.RESEARCH, "codex", "코드 예제 수집", parallel=True),
                    WorkflowNode("r4", NodeType.DOCUMENT, "claude", "종합 정리", dependencies=["r1", "r2", "r3"])
                ],
                trigger_patterns=["분석", "조사", "리서치", "알아봐", "research", "찾아"]
            ),
            
            # 4. 코드 리뷰 프로세스
            "code_review": WorkflowProcess(
                name="코드 리뷰 프로세스",
                description="다각도 코드 리뷰 프로세스",
                nodes=[
                    WorkflowNode("cr1", NodeType.REVIEW, "gemini", "아키텍처 리뷰", parallel=True),
                    WorkflowNode("cr2", NodeType.REVIEW, "claude", "코드 품질 리뷰", parallel=True),
                    WorkflowNode("cr3", NodeType.TEST, "codex", "테스트 커버리지 확인", parallel=True),
                    WorkflowNode("cr4", NodeType.DOCUMENT, "claude", "리뷰 결과 종합", dependencies=["cr1", "cr2", "cr3"])
                ],
                trigger_patterns=["리뷰", "검토", "확인", "review", "check"]
            ),
            
            # 5. 배포 프로세스
            "deployment": WorkflowProcess(
                name="배포 프로세스",
                description="테스트-검증-배포-모니터링 프로세스",
                nodes=[
                    WorkflowNode("d1", NodeType.TEST, "gemini", "통합 테스트"),
                    WorkflowNode("d2", NodeType.VALIDATE, "claude", "배포 전 검증", dependencies=["d1"]),
                    WorkflowNode("d3", NodeType.DEPLOY, "codex", "프로덕션 배포", dependencies=["d2"]),
                    WorkflowNode("d4", NodeType.MONITOR, "gemini", "배포 후 모니터링", dependencies=["d3"])
                ],
                trigger_patterns=["배포", "디플로이", "deploy", "release", "출시"]
            ),
            
            # 6. 문서화 프로세스
            "documentation": WorkflowProcess(
                name="문서화 프로세스",
                description="코드 분석 후 문서 생성",
                nodes=[
                    WorkflowNode("doc1", NodeType.ANALYZE, "gemini", "코드 구조 분석"),
                    WorkflowNode("doc2", NodeType.DOCUMENT, "claude", "API 문서 작성", dependencies=["doc1"]),
                    WorkflowNode("doc3", NodeType.DOCUMENT, "codex", "사용 예제 작성", dependencies=["doc1"]),
                    WorkflowNode("doc4", NodeType.REVIEW, "claude", "문서 검토", dependencies=["doc2", "doc3"])
                ],
                trigger_patterns=["문서", "도큐", "설명", "document", "docs"]
            ),
            
            # 7. 성능 최적화 프로세스
            "optimization": WorkflowProcess(
                name="성능 최적화 프로세스",
                description="분석-최적화-검증 프로세스",
                nodes=[
                    WorkflowNode("o1", NodeType.ANALYZE, "gemini", "성능 병목 분석"),
                    WorkflowNode("o2", NodeType.IMPLEMENT, "codex", "최적화 구현", dependencies=["o1"]),
                    WorkflowNode("o3", NodeType.TEST, "gemini", "성능 테스트", dependencies=["o2"]),
                    WorkflowNode("o4", NodeType.VALIDATE, "claude", "개선 효과 검증", dependencies=["o3"])
                ],
                trigger_patterns=["최적화", "성능", "개선", "optimize", "performance"]
            )
        }
    
    def find_matching_process(self, user_message: str) -> List[WorkflowProcess]:
        """메시지에 맞는 프로세스 찾기"""
        matches = []
        message_lower = user_message.lower()
        
        for process_id, process in self.processes.items():
            for pattern in process.trigger_patterns:
                if pattern in message_lower:
                    matches.append((process_id, process))
                    break
        
        return matches
    
    def build_process_from_blocks(self, block_names: List[str]) -> WorkflowProcess:
        """노드 블록들을 조합하여 프로세스 생성"""
        nodes = []
        prev_node_id = None
        
        for i, block_name in enumerate(block_names):
            if block_name in self.node_blocks:
                block = self.node_blocks[block_name]
                
                # 블록이 리스트인 경우 (병렬 처리)
                if isinstance(block, list):
                    for node in block:
                        new_node = WorkflowNode(
                            id=f"{block_name}_{node.id}",
                            type=node.type,
                            ai_assignment=node.ai_assignment,
                            command=node.command,
                            parallel=True,
                            dependencies=[prev_node_id] if prev_node_id else []
                        )
                        nodes.append(new_node)
                    # 병렬 블록의 마지막 노드 ID 저장
                    prev_node_id = f"{block_name}_summary"
                    # 병렬 후 종합 노드 추가
                    summary_node = WorkflowNode(
                        id=prev_node_id,
                        type=NodeType.DOCUMENT,
                        ai_assignment="claude",
                        command="결과 종합",
                        dependencies=[f"{block_name}_{n.id}" for n in block]
                    )
                    nodes.append(summary_node)
                else:
                    # 단일 노드
                    new_node = WorkflowNode(
                        id=f"{block_name}_{i}",
                        type=block.type,
                        ai_assignment=block.ai_assignment,
                        command=block.command,
                        dependencies=[prev_node_id] if prev_node_id else []
                    )
                    nodes.append(new_node)
                    prev_node_id = new_node.id
        
        return WorkflowProcess(
            name="커스텀 조합 프로세스",
            description=f"블록 조합: {' → '.join(block_names)}",
            nodes=nodes,
            trigger_patterns=[],
            required_confirmation=True
        )
    
    def suggest_process_combination(self, user_message: str) -> str:
        """메시지 분석 후 노드 조합 제안"""
        suggestions = []
        
        # 키워드 기반 블록 추천
        if "버그" in user_message or "수정" in user_message:
            suggestions.append(["analyze", "implement", "test", "document"])
        if "기능" in user_message or "개발" in user_message:
            suggestions.append(["analyze", "design", "implement", "test", "review"])
        if "리서치" in user_message or "조사" in user_message:
            suggestions.append(["parallel_research", "document"])
        if "배포" in user_message:
            suggestions.append(["test", "review", "deploy", "monitor"])
        if "리뷰" in user_message:
            suggestions.append(["parallel_review", "document"])
        
        # 제안 텍스트 생성
        if suggestions:
            text = "🔧 추천 노드 조합:\n"
            for i, combo in enumerate(suggestions, 1):
                text += f"{i}. {' → '.join(combo)}\n"
            return text
        else:
            return "📝 기본 조합: analyze → implement → test → review"
    
    def create_custom_process(self, selected_nodes: List[Dict]) -> WorkflowProcess:
        """선택된 노드들로 커스텀 프로세스 생성"""
        nodes = []
        for i, node_info in enumerate(selected_nodes):
            node = WorkflowNode(
                id=f"custom_{i}",
                type=NodeType[node_info['type'].upper()],
                ai_assignment=node_info.get('ai', 'claude'),
                command=node_info.get('command', ''),
                parallel=node_info.get('parallel', False),
                dependencies=node_info.get('dependencies', [])
            )
            nodes.append(node)
        
        return WorkflowProcess(
            name="커스텀 워크플로우",
            description="사용자 정의 워크플로우",
            nodes=nodes,
            trigger_patterns=[],
            required_confirmation=True
        )
    
    def visualize_process(self, process: WorkflowProcess) -> str:
        """프로세스를 텍스트로 시각화"""
        viz = f"\n📋 {process.name}\n"
        viz += f"   {process.description}\n\n"
        
        for node in process.nodes:
            indent = "   "
            if node.dependencies:
                indent = "      → "
            
            parallel_mark = " [병렬]" if node.parallel else ""
            viz += f"{indent}{node.id}: {node.type.value} ({node.ai_assignment}){parallel_mark}\n"
            viz += f"         {node.command}\n"
            
            if node.dependencies:
                viz += f"         의존: {', '.join(node.dependencies)}\n"
            viz += "\n"
        
        return viz

# 사용 예시
if __name__ == "__main__":
    registry = WorkflowRegistry()
    
    # 테스트: "새 기능 만들어줘" 메시지
    test_message = "로그인 기능 만들어줘"
    matches = registry.find_matching_process(test_message)
    
    if matches:
        for process_id, process in matches:
            print(f"매칭된 프로세스: {process_id}")
            print(registry.visualize_process(process))