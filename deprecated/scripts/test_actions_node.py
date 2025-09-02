#!/usr/bin/env python3
"""
GitHub Actions 로컬 테스트 노드 통합 테스트
"""

from node_system import NodeFactory, NodeType
from workflow_definitions import WorkflowRegistry

def test_actions_node_creation():
    """Actions 테스트 노드 생성 테스트"""
    print("="*60)
    print("🧪 ACTIONS_LOCAL_TEST 노드 생성 테스트")
    print("="*60)
    
    # 1. 직접 노드 생성
    print("\n1️⃣ 직접 노드 생성:")
    node = NodeFactory.create_node(
        NodeType.ACTIONS_LOCAL_TEST,
        executor='act',
        input_data={'workflow_path': '.github/workflows/'}
    )
    print(f"  노드 타입: {node.state.type}")
    print(f"  실행자: {node.executor}")
    print(f"  입력 데이터: {node.state.input_data}")
    
    # 2. 자연어에서 노드 생성
    print("\n2️⃣ 자연어에서 노드 생성:")
    instructions = [
        "workflow 수정했어",
        "GitHub Actions 테스트해줘",
        "CI/CD 확인해봐"
    ]
    
    for instruction in instructions:
        print(f"\n  지시: '{instruction}'")
        nodes = NodeFactory.create_from_instruction(instruction)
        for node in nodes:
            if node.state.type == NodeType.ACTIONS_LOCAL_TEST:
                print(f"  ✅ ACTIONS_LOCAL_TEST 노드 생성됨!")
                break
        else:
            print(f"  ❌ 노드 생성 안됨")

def test_workflow_process():
    """워크플로우 프로세스 테스트"""
    print("\n" + "="*60)
    print("🔄 Actions 워크플로우 프로세스 테스트")
    print("="*60)
    
    registry = WorkflowRegistry()
    
    # Actions 워크플로우 확인
    if "actions_workflow" in registry.processes:
        workflow = registry.processes["actions_workflow"]
        print(f"\n📋 워크플로우: {workflow.name}")
        print(f"📝 설명: {workflow.description}")
        print(f"🔍 트리거 패턴: {workflow.trigger_patterns}")
        print(f"🤖 자동 실행: {not workflow.required_confirmation}")
        
        print("\n📌 노드 순서:")
        for i, node in enumerate(workflow.nodes, 1):
            deps = f" (의존: {', '.join(node.dependencies)})" if node.dependencies else ""
            print(f"  {i}. [{node.type.value}] {node.command} - {node.ai_assignment}{deps}")
    else:
        print("❌ actions_workflow 프로세스를 찾을 수 없습니다.")

def test_trigger_detection():
    """트리거 키워드 감지 테스트"""
    print("\n" + "="*60)
    print("🎯 트리거 키워드 감지 테스트")
    print("="*60)
    
    registry = WorkflowRegistry()
    workflow = registry.processes.get("actions_workflow")
    
    test_messages = [
        "workflow 파일 수정했어",
        "Actions 로컬에서 테스트해줘",
        ".github/workflows 변경했어",
        "CI/CD 파이프라인 확인",
        "일반적인 작업입니다"  # 트리거 안됨
    ]
    
    for msg in test_messages:
        triggered = any(pattern in msg.lower() for pattern in workflow.trigger_patterns)
        status = "✅ 트리거" if triggered else "❌ 무시"
        print(f"{status}: '{msg}'")

if __name__ == "__main__":
    test_actions_node_creation()
    test_workflow_process()
    test_trigger_detection()
    
    print("\n" + "="*60)
    print("✅ 테스트 완료!")
    print("="*60)