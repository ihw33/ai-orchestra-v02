#!/usr/bin/env python3
"""
Context7 통합 테스트
"""

import logging
from context7_node_executor import Context7NodeExecutor
from node_system import NodeType, NodeState
from evolution_logger import get_logger

def test_context7_integration():
    """Context7 고도화 기능 통합 테스트"""
    
    print("🧪 Context7 고도화 통합 테스트")
    print("=" * 50)
    
    executor = Context7NodeExecutor()
    evo_logger = get_logger()
    
    # 초기 경험치 확인
    initial_exp = evo_logger._get_total_exp()
    print(f"초기 경험치: {initial_exp}")
    
    # 1. 프로젝트 문서 자동 로드 테스트
    print("\n📚 Test 1: 프로젝트 문서 자동 로드")
    print("-" * 30)
    
    load_node = NodeState(
        id="test_auto_load",
        type=NodeType.AUTO_LOAD_PROJECT_DOCS,
        input_data={
            "project_path": "/Users/m4_macbook/Projects/personal-journal-hub"
        }
    )
    
    result = executor.execute_context7_node(load_node)
    print(f"로드된 라이브러리: {len(result.get('loaded_libraries', []))}개")
    print(f"실패한 라이브러리: {len(result.get('failed_libraries', []))}개")
    print(f"보너스 경험치: +{result.get('bonus_exp', 0)}")
    
    # 2. 실시간 문서 검색 테스트
    print("\n🔍 Test 2: 실시간 문서 검색")
    print("-" * 30)
    
    search_node = NodeState(
        id="test_search",
        type=NodeType.SEARCH_DOCS_REALTIME,
        input_data={
            "library": "react",
            "api_name": "useState"
        }
    )
    
    result2 = executor.execute_context7_node(search_node)
    if result2.get('success'):
        print(f"✅ React 문서 검색 성공")
        print(f"보너스 경험치: +{result2.get('bonus_exp', 0)}")
    else:
        print(f"❌ React 문서 검색 실패: {result2.get('error')}")
    
    # 3. API 사용 검증 테스트
    print("\n✅ Test 3: API 사용 검증")
    print("-" * 30)
    
    sample_code = """
    import React, { useState, useEffect } from 'react';
    
    function MyComponent() {
        const [count, setCount] = useState(0);
        const [data, setData] = useCustomHook();  // 가상의 훅
        
        useEffect(() => {
            console.log('Component mounted');
        }, []);
        
        return <div>{count}</div>;
    }
    """
    
    validate_node = NodeState(
        id="test_validate",
        type=NodeType.VALIDATE_API_USAGE,
        input_data={
            "code": sample_code,
            "library": "react",
            "old_version": "^17.0.0",
            "new_version": "^18.0.0"
        }
    )
    
    result3 = executor.execute_context7_node(validate_node)
    print(f"검증 결과: {'✅ 통과' if result3.get('valid') else '⚠️ 이슈 발견'}")
    if result3.get('issues'):
        print("발견된 이슈:")
        for issue in result3['issues'][:3]:
            print(f"  {issue}")
    print(f"경험치 변화: {'+' if result3.get('exp_change', 0) > 0 else ''}{result3.get('exp_change', 0)}")
    
    # 4. 스마트 워크플로우 생성 테스트
    print("\n🤖 Test 4: 스마트 워크플로우 생성")
    print("-" * 30)
    
    workflow = executor.create_smart_workflow("React 컴포넌트와 API 연동 기능 만들어줘")
    print("생성된 워크플로우:")
    for i, step in enumerate(workflow, 1):
        print(f"  {i}. {step['description']}")
    
    # 최종 경험치 확인
    final_exp = evo_logger._get_total_exp()
    exp_gained = final_exp - initial_exp
    
    print("\n" + "=" * 50)
    print(f"📊 테스트 완료!")
    print(f"획득한 경험치: +{exp_gained}")
    print(f"현재 총 경험치: {final_exp}")
    
    # Evolution 상태 표시
    evo_logger.show_progress()
    
    return True

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.WARNING,  # INFO 대신 WARNING으로 설정하여 로그 줄이기
        format='%(message)s'
    )
    
    test_context7_integration()