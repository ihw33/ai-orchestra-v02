#!/usr/bin/env python3
"""
Context7 Node Executor - Context7 고도화 노드 실행기
"""

from typing import Dict, Any
import logging
from node_system import NodeType, NodeState, NodeStatus
from context7_auto_loader import Context7AutoLoader
from evolution_logger import get_logger

class Context7NodeExecutor:
    """Context7 고도화 노드 실행기"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.auto_loader = Context7AutoLoader()
        self.evolution_logger = get_logger()
    
    def execute_context7_node(self, node: NodeState) -> Dict[str, Any]:
        """Context7 관련 노드 실행"""
        try:
            if node.type == NodeType.SEARCH_DOCS_REALTIME:
                return self._search_docs_realtime(node.input_data)
            elif node.type == NodeType.AUTO_LOAD_PROJECT_DOCS:
                return self._auto_load_project_docs(node.input_data)
            elif node.type == NodeType.VALIDATE_API_USAGE:
                return self._validate_api_usage(node.input_data)
            else:
                return {"success": False, "error": f"Unknown Context7 node: {node.type}"}
        except Exception as e:
            self.logger.error(f"Context7 노드 실행 실패: {e}")
            return {"success": False, "error": str(e)}
    
    def _search_docs_realtime(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """실시간 문서 검색"""
        library = data.get("library", "")
        api_name = data.get("api_name", "")
        
        self.logger.info(f"🔍 Context7 실시간 검색: {library} - {api_name}")
        
        # 문서 가져오기
        docs = self.auto_loader.get_docs_for_code_generation(library)
        
        if docs:
            # API 사용법 제안
            usage = self.auto_loader.suggest_api_usage(library, api_name)
            
            # Evolution Logger에 보너스 경험치
            self.evolution_logger.on_node_complete("USE_LATEST_DOCS", success=True)
            
            return {
                "success": True,
                "library": library,
                "api_name": api_name,
                "documentation": docs,
                "usage_suggestion": usage,
                "bonus_exp": 5
            }
        
        return {
            "success": False,
            "error": f"문서를 찾을 수 없음: {library}"
        }
    
    def _auto_load_project_docs(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """프로젝트 문서 자동 로드"""
        project_path = data.get("project_path", ".")
        
        self.logger.info(f"📚 프로젝트 문서 자동 로드: {project_path}")
        
        # 모든 의존성 문서 로드
        results = self.auto_loader.auto_load_all_docs(project_path)
        
        # 성공한 라이브러리당 경험치
        for _ in results["loaded"]:
            self.evolution_logger.on_node_complete("AUTO_DOCS_LOAD", success=True)
        
        return {
            "success": True,
            "loaded_libraries": results["loaded"],
            "failed_libraries": results["failed"],
            "total": results["total_libraries"],
            "bonus_exp": len(results["loaded"]) * 3
        }
    
    def _validate_api_usage(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """API 사용 검증"""
        code = data.get("code", "")
        library = data.get("library", "")
        
        self.logger.info(f"✅ API 사용 검증: {library}")
        
        # 문서 가져오기
        docs = self.auto_loader.get_docs_for_code_generation(library)
        
        if not docs:
            return {
                "success": False,
                "error": f"문서를 찾을 수 없어 검증 불가: {library}"
            }
        
        # 간단한 검증 (실제로는 더 복잡한 로직 필요)
        docs_text = str(docs)
        issues = []
        suggestions = []
        
        # 코드에서 사용된 API 추출 (간단한 예시)
        import re
        api_calls = re.findall(r'(\w+)\s*\(', code)
        
        for api in api_calls:
            if api not in docs_text and api not in ['if', 'for', 'while', 'function', 'const', 'let', 'var']:
                issues.append(f"⚠️ '{api}'는 {library} 문서에서 찾을 수 없습니다")
                # 비슷한 API 제안 (간단한 구현)
                if 'use' + api.capitalize() in docs_text:
                    suggestions.append(f"💡 'use{api.capitalize()}' 사용을 고려해보세요")
        
        # Breaking changes 확인
        if data.get("old_version") and data.get("new_version"):
            warnings = self.auto_loader.check_breaking_changes(
                data["old_version"],
                data["new_version"],
                library
            )
            issues.extend(warnings)
        
        # 검증 결과에 따른 경험치
        if not issues:
            self.evolution_logger.on_node_complete("VALIDATE_SUCCESS", success=True)
            exp_change = 8
        else:
            self.evolution_logger.on_node_complete("VALIDATE_ISSUES", success=True)
            exp_change = 3
        
        return {
            "success": True,
            "valid": len(issues) == 0,
            "issues": issues,
            "suggestions": suggestions,
            "exp_change": exp_change
        }
    
    def create_smart_workflow(self, task: str) -> list:
        """작업에 따른 스마트 워크플로우 생성"""
        workflow = []
        
        # 1. 프로젝트 문서 자동 로드
        workflow.append({
            "node_type": NodeType.AUTO_LOAD_PROJECT_DOCS,
            "description": "프로젝트 의존성 문서 자동 로드",
            "input": {"project_path": "."}
        })
        
        # 2. 작업에 따른 추가 노드
        if "react" in task.lower() or "component" in task.lower():
            workflow.append({
                "node_type": NodeType.SEARCH_DOCS_REALTIME,
                "description": "React 최신 문서 검색",
                "input": {"library": "react", "api_name": "useState"}
            })
        
        if "api" in task.lower() or "backend" in task.lower():
            workflow.append({
                "node_type": NodeType.SEARCH_DOCS_REALTIME,
                "description": "Express/Fastify 문서 검색",
                "input": {"library": "express", "api_name": "router"}
            })
        
        # 3. 코드 생성 후 검증
        workflow.append({
            "node_type": NodeType.VALIDATE_API_USAGE,
            "description": "생성된 코드 API 사용 검증",
            "input": {"library": "auto", "code": "generated_code_here"}
        })
        
        return workflow


# 테스트
if __name__ == "__main__":
    import logging
    logging.basicConfig(level=logging.INFO)
    
    executor = Context7NodeExecutor()
    
    print("🧪 Context7 노드 실행기 테스트")
    print("=" * 50)
    
    # 1. 실시간 문서 검색 테스트
    search_node = NodeState(
        id="test_search",
        type=NodeType.SEARCH_DOCS_REALTIME,
        input_data={
            "library": "react",
            "api_name": "useState"
        }
    )
    
    result = executor.execute_context7_node(search_node)
    print(f"실시간 검색 결과: {result.get('success')}")
    
    # 2. 프로젝트 문서 자동 로드
    load_node = NodeState(
        id="test_load",
        type=NodeType.AUTO_LOAD_PROJECT_DOCS,
        input_data={
            "project_path": "/Users/m4_macbook/Projects/personal-journal-hub"
        }
    )
    
    result2 = executor.execute_context7_node(load_node)
    print(f"자동 로드 결과: {result2.get('total', 0)}개 라이브러리")
    
    # 3. 스마트 워크플로우 생성
    workflow = executor.create_smart_workflow("React 컴포넌트 만들어줘")
    print(f"\n생성된 워크플로우:")
    for step in workflow:
        print(f"  - {step['description']}")