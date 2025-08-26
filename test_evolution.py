#!/usr/bin/env python3
"""
Evolution 시스템 통합 테스트
"""

from node_system import NodeFactory, NodeType, ExecutionMode
from evolution_logger import get_logger
import time

def test_evolution_integration():
    """통합 테스트"""
    print("🧪 Evolution 시스템 통합 테스트 시작\n")
    
    # 초기 상태 확인
    logger = get_logger()
    initial_status = logger.get_current_status()
    print(f"초기 상태: {initial_status['form']} Lv.{initial_status['level']} (exp: {initial_status['exp']})")
    
    # 다양한 노드 실행 시뮬레이션
    test_scenarios = [
        ("CREATE_ISSUE", {"title": "테스트 이슈", "body": "자동 테스트"}),
        ("WRITE_FUNCTION", {"function_name": "test_func", "parameters": ["a", "b"]}),
        ("FIX_BUG_LINE", {"file_path": "test.py", "line_number": 10}),
        ("RUN_TEST", {"test_path": "tests/"}),
        ("CREATE_PR", {"title": "테스트 PR", "body": "자동 생성"}),
        ("MCP_MEMORY_STORE", {"name": "테스트 메모리", "entityType": "test"}),
    ]
    
    print("\n노드 실행 시작:")
    print("-" * 50)
    
    for node_type_str, input_data in test_scenarios:
        # 노드 생성
        node = NodeFactory.create_node(
            NodeType[node_type_str],
            input_data=input_data,
            mode=ExecutionMode.PARALLEL
        )
        
        # 노드 실행 (실제로는 실행하지 않고 시뮬레이션)
        print(f"\n실행 중: {node_type_str}")
        
        # execute_with_ai를 오버라이드하여 실제 AI 호출 방지
        node.execute_with_ai = lambda: {"simulated": "success"}
        
        # 노드 실행
        result = node.execute()
        
        # 상태 업데이트 확인
        current_status = logger.get_current_status()
        print(f"  → 경험치: {current_status['exp']} (+{logger.exp_table.get(node_type_str, 3)})")
        print(f"  → 현재: {current_status['form']} Lv.{current_status['level']}")
        
        time.sleep(0.5)  # 시각적 효과를 위한 딜레이
    
    # 최종 상태
    print("\n" + "=" * 50)
    logger.show_progress()
    
    # 로그 파일 확인
    print("📝 최근 로그 (last 10):")
    print("-" * 50)
    with open("orchestra.log", "r") as f:
        lines = f.readlines()
        for line in lines[-10:]:
            print(line.strip())
    
    print("\n✅ 통합 테스트 완료!")
    return True

if __name__ == "__main__":
    test_evolution_integration()