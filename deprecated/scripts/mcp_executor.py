#!/usr/bin/env python3
"""
MCP Executor - MCP 서버들을 Node-DAG 시스템에 통합
"""

import subprocess
import json
import time
import logging
from typing import Dict, Any, Optional
from concurrent.futures import ThreadPoolExecutor
from node_system import NodeType, NodeStatus, NodeState

class MCPExecutor:
    """MCP 서버 실행 및 관리"""
    
    def __init__(self):
        self.active_servers = {}
        self.executor_pool = ThreadPoolExecutor(max_workers=2)
        self.logger = logging.getLogger(__name__)
        
    def execute_mcp_node(self, node: NodeState) -> Dict[str, Any]:
        """MCP 노드 실행"""
        try:
            if node.type == NodeType.MCP_MEMORY_STORE:
                return self._execute_memory_store(node.input_data)
            elif node.type == NodeType.MCP_MEMORY_SEARCH:
                return self._execute_memory_search(node.input_data)
            elif node.type == NodeType.MCP_CONTEXT7_RESOLVE:
                return self._execute_context7_resolve(node.input_data)
            elif node.type == NodeType.MCP_CONTEXT7_DOCS:
                return self._execute_context7_docs(node.input_data)
            else:
                return {"success": False, "error": f"Unsupported MCP node: {node.type}"}
                
        except Exception as e:
            self.logger.error(f"MCP 노드 실행 실패: {e}")
            return {"success": False, "error": str(e)}
    
    def _execute_memory_store(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Memory MCP에 데이터 저장"""
        self.logger.info("🧠 Memory MCP - 데이터 저장 시작")
        
        # Memory 서버 시작
        server = subprocess.Popen(
            ['npx', '-y', '@modelcontextprotocol/server-memory'],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # 저장할 엔티티 구성
        entities = data.get('entities', [{
            'name': data.get('name', 'Unknown'),
            'entityType': data.get('entityType', 'general'),
            'observations': data.get('observations', [])
        }])
        
        message = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": "create_entities",
                "arguments": {
                    "entities": entities
                }
            }
        }
        
        try:
            # 서버에 메시지 전송
            stdout, stderr = server.communicate(
                input=json.dumps(message) + '\n',
                timeout=10
            )
            
            # 응답 파싱
            for line in stdout.strip().split('\n'):
                if line.strip() and line.startswith('{"'):
                    response = json.loads(line)
                    if 'result' in response:
                        self.logger.info("✅ Memory 저장 성공")
                        return {
                            "success": True,
                            "stored_entities": entities,
                            "response": response
                        }
                        
        except Exception as e:
            self.logger.error(f"Memory 저장 실패: {e}")
            
        finally:
            if server.poll() is None:
                server.terminate()
        
        return {"success": False, "error": "Memory 저장 실패"}
    
    def _execute_memory_search(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Memory MCP에서 데이터 검색"""
        self.logger.info("🔍 Memory MCP - 데이터 검색 시작")
        
        server = subprocess.Popen(
            ['npx', '-y', '@modelcontextprotocol/server-memory'],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        query = data.get('query', '')
        message = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": "search_nodes",
                "arguments": {
                    "query": query
                }
            }
        }
        
        try:
            stdout, stderr = server.communicate(
                input=json.dumps(message) + '\n',
                timeout=10
            )
            
            for line in stdout.strip().split('\n'):
                if line.strip() and line.startswith('{"'):
                    response = json.loads(line)
                    if 'result' in response:
                        self.logger.info(f"✅ Memory 검색 성공: '{query}'")
                        return {
                            "success": True,
                            "query": query,
                            "results": response.get('result', {})
                        }
                        
        except Exception as e:
            self.logger.error(f"Memory 검색 실패: {e}")
            
        finally:
            if server.poll() is None:
                server.terminate()
        
        return {"success": False, "error": "Memory 검색 실패"}
    
    def _execute_context7_resolve(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Context7에서 라이브러리 ID 해석"""
        self.logger.info("📚 Context7 MCP - 라이브러리 ID 해석 시작")
        
        server = subprocess.Popen(
            ['npx', '-y', '@upstash/context7-mcp'],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        library_name = data.get('library_name', 'react')
        message = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": "resolve-library-id",
                "arguments": {
                    "libraryName": library_name
                }
            }
        }
        
        try:
            stdout, stderr = server.communicate(
                input=json.dumps(message) + '\n',
                timeout=15
            )
            
            for line in stdout.strip().split('\n'):
                if line.strip() and line.startswith('{"'):
                    response = json.loads(line)
                    if 'result' in response:
                        self.logger.info(f"✅ Context7 라이브러리 해석 성공: {library_name}")
                        return {
                            "success": True,
                            "library_name": library_name,
                            "libraries": response.get('result', {})
                        }
                        
        except Exception as e:
            self.logger.error(f"Context7 라이브러리 해석 실패: {e}")
            
        finally:
            if server.poll() is None:
                server.terminate()
        
        return {"success": False, "error": "Context7 라이브러리 해석 실패"}
    
    def _execute_context7_docs(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Context7에서 문서 조회"""
        self.logger.info("📖 Context7 MCP - 문서 조회 시작")
        
        server = subprocess.Popen(
            ['npx', '-y', '@upstash/context7-mcp'],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        library_id = data.get('library_id', '/facebook/react')
        topic = data.get('topic', 'hooks')
        tokens = data.get('tokens', 5000)
        
        message = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": "get-library-docs",
                "arguments": {
                    "context7CompatibleLibraryID": library_id,
                    "topic": topic,
                    "tokens": tokens
                }
            }
        }
        
        try:
            stdout, stderr = server.communicate(
                input=json.dumps(message) + '\n',
                timeout=20
            )
            
            for line in stdout.strip().split('\n'):
                if line.strip() and line.startswith('{"'):
                    response = json.loads(line)
                    if 'result' in response:
                        self.logger.info(f"✅ Context7 문서 조회 성공: {library_id}/{topic}")
                        return {
                            "success": True,
                            "library_id": library_id,
                            "topic": topic,
                            "documentation": response.get('result', {})
                        }
                        
        except Exception as e:
            self.logger.error(f"Context7 문서 조회 실패: {e}")
            
        finally:
            if server.poll() is None:
                server.terminate()
        
        return {"success": False, "error": "Context7 문서 조회 실패"}

# 테스트 실행
if __name__ == "__main__":
    import logging
    logging.basicConfig(level=logging.INFO)
    
    executor = MCPExecutor()
    
    # Memory 저장 테스트
    memory_node = NodeState(
        id="test_memory_1",
        type=NodeType.MCP_MEMORY_STORE,
        input_data={
            "name": "AI_Orchestra_Integration_Test",
            "entityType": "integration",
            "observations": ["MCP 노드 통합 테스트", "Memory + Context7 연동"]
        }
    )
    
    print("🧪 MCP 노드 통합 테스트 시작...")
    result = executor.execute_mcp_node(memory_node)
    print(f"결과: {result}")
    
    # Context7 해석 테스트
    context7_node = NodeState(
        id="test_context7_1", 
        type=NodeType.MCP_CONTEXT7_RESOLVE,
        input_data={"library_name": "next.js"}
    )
    
    result2 = executor.execute_mcp_node(context7_node)
    print(f"Context7 결과: {result2.get('success', False)}")
    
    print("✅ MCP 노드 통합 완료!")