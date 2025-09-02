#!/usr/bin/env python3
"""워크플로우 실행기 - DAG 패턴을 실행"""

import time
import sys
import json
from typing import List, Tuple, Dict, Any
from node_executor import NodeExecutor

class WorkflowRunner:
    def __init__(self):
        self.executor = NodeExecutor()
        self.workflows = {
            "ANALYSIS_PIPELINE": [
                ("CREATE_ISSUE", {"title": "[AI] 분석 작업"}),
                ("KEYWORD_ENRICHMENT", {}),
                ("AI_ANALYSIS", {"ai": "gemini"}),
                ("GENERATE_REPORT", {})
            ],
            "SOLUTION_ADOPTION": [
                ("CREATE_ISSUE", {"title": "[AI] 솔루션 도입 분석"}),
                ("PARSE_SOLUTION", {"ai": "gemini"}),
                ("ANALYZE_FEATURES", {"ai": "claude"}),
                ("EVALUATE_FIT", {"ai": "codex"}),
                ("ADOPTION_REPORT", {})
            ],
            "FEATURE_DEVELOPMENT": [
                ("CREATE_ISSUE", {"title": "[AI] 기능 개발"}),
                ("KEYWORD_ENRICHMENT", {}),
                ("AI_ANALYSIS", {"ai": "gemini", "prompt": "기능 요구사항 분석"}),
                ("AI_IMPLEMENTATION", {"ai": "claude"}),
                ("AI_TESTING", {"ai": "codex"}),
                ("GENERATE_REPORT", {})
            ],
            "BUGFIX_WORKFLOW": [
                ("CREATE_ISSUE", {"title": "[AI] 버그 수정", "labels": "bug,urgent"}),
                ("AI_ANALYSIS", {"ai": "gemini", "prompt": "버그 원인 분석"}),
                ("AI_IMPLEMENTATION", {"ai": "claude", "prompt": "버그 수정"}),
                ("AI_TESTING", {"ai": "codex", "prompt": "수정 검증"}),
                ("GENERATE_REPORT", {})
            ],
            "DOCUMENTATION_PIPELINE": [
                ("CREATE_ISSUE", {"title": "[AI] 문서화 작업"}),
                ("KEYWORD_ENRICHMENT", {}),
                ("AI_ANALYSIS", {"ai": "gemini", "prompt": "문서 구조 설계"}),
                ("AI_IMPLEMENTATION", {"ai": "claude", "prompt": "문서 작성"}),
                ("GENERATE_REPORT", {})
            ],
            "PARALLEL_ANALYSIS": [
                ("CREATE_ISSUE", {"title": "[AI] 병렬 분석"}),
                # 병렬 실행을 위한 특별 표시
                ("PARALLEL_START", {}),
                ("AI_ANALYSIS", {"ai": "gemini", "prompt": "구조 분석"}),
                ("AI_ANALYSIS", {"ai": "claude", "prompt": "기능 분석"}),
                ("AI_ANALYSIS", {"ai": "codex", "prompt": "코드 분석"}),
                ("PARALLEL_END", {}),
                ("GENERATE_REPORT", {})
            ]
        }
        
        # 커스텀 워크플로우 저장소
        self.custom_workflows = {}
    
    def run(self, workflow_name: str, context: Dict = None) -> List[Any]:
        """워크플로우 실행"""
        # 워크플로우 찾기
        if workflow_name in self.workflows:
            workflow = self.workflows[workflow_name]
        elif workflow_name in self.custom_workflows:
            workflow = self.custom_workflows[workflow_name]
        else:
            print(f"❌ Unknown workflow: {workflow_name}")
            print(f"Available workflows: {', '.join(self.workflows.keys())}")
            return []
        
        print(f"🚀 Starting workflow: {workflow_name}")
        results = []
        issue_num = None
        parallel_mode = False
        parallel_results = []
        
        for i, (node_name, params) in enumerate(workflow):
            # 병렬 처리 제어
            if node_name == "PARALLEL_START":
                parallel_mode = True
                print("⚡ Entering parallel execution mode")
                continue
            elif node_name == "PARALLEL_END":
                parallel_mode = False
                print("⚡ Exiting parallel execution mode")
                # 병렬 결과를 results에 추가
                results.extend(parallel_results)
                parallel_results = []
                continue
            
            print(f"\n[{i+1}/{len(workflow)}] Executing {node_name}...")
            
            # 컨텍스트 병합
            if context:
                params = {**params, **context}
            
            # 이슈 번호 전달
            if issue_num:
                params['issue_num'] = issue_num
            
            # 이전 결과 전달
            if results and not parallel_mode:
                params['previous_result'] = results[-1]
                params['results'] = results  # 전체 결과도 전달
            
            # 노드 실행
            if parallel_mode:
                # 병렬 모드에서는 결과만 수집 (실제로는 순차 실행)
                result = self.executor.execute(node_name, params)
                parallel_results.append(result)
            else:
                result = self.executor.execute(node_name, params)
                results.append(result)
                
                # CREATE_ISSUE 노드에서 이슈 번호 추출
                if node_name == "CREATE_ISSUE" and result:
                    issue_num = result
                    print(f"📋 Issue number: #{issue_num}")
            
            print(f"✅ {node_name} completed")
            
            # 짧은 대기 (API 제한 방지)
            if not parallel_mode:
                time.sleep(0.5)
        
        print(f"\n✨ Workflow {workflow_name} completed!")
        return results
    
    def create_custom_workflow(self, name: str, nodes: List[Tuple[str, Dict]]):
        """커스텀 워크플로우 생성"""
        self.custom_workflows[name] = nodes
        print(f"✅ Custom workflow '{name}' created with {len(nodes)} nodes")
    
    def list_workflows(self):
        """사용 가능한 워크플로우 목록"""
        print("📋 Available workflows:")
        print("\n🔹 Built-in workflows:")
        for name, workflow in self.workflows.items():
            node_names = [n for n, _ in workflow if not n.startswith("PARALLEL")]
            print(f"  - {name}: {' → '.join(node_names[:3])}...")
        
        if self.custom_workflows:
            print("\n🔹 Custom workflows:")
            for name in self.custom_workflows:
                print(f"  - {name}")
    
    def compose_workflow(self, *node_names) -> List[Tuple[str, Dict]]:
        """노드들을 조합하여 워크플로우 생성"""
        workflow = []
        for node_name in node_names:
            workflow.append((node_name, {}))
        return workflow


if __name__ == "__main__":
    runner = WorkflowRunner()
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "list":
            # 워크플로우 목록 보기
            runner.list_workflows()
        
        elif command == "compose":
            # 노드 조합하여 실행
            if len(sys.argv) > 2:
                nodes = sys.argv[2:]
                workflow = runner.compose_workflow(*nodes)
                runner.create_custom_workflow("COMPOSED", workflow)
                runner.run("COMPOSED")
            else:
                print("Usage: python3 workflow_runner.py compose NODE1 NODE2 ...")
        
        else:
            # 워크플로우 실행
            workflow_name = command
            
            # 추가 컨텍스트 파싱
            context = {}
            if len(sys.argv) > 2:
                try:
                    context = json.loads(sys.argv[2])
                except json.JSONDecodeError:
                    context = {"request": sys.argv[2]}
            
            runner.run(workflow_name, context)
    else:
        print("Usage:")
        print("  python3 workflow_runner.py WORKFLOW_NAME [CONTEXT_JSON]")
        print("  python3 workflow_runner.py list")
        print("  python3 workflow_runner.py compose NODE1 NODE2 ...")
        print("\nExample:")
        print("  python3 workflow_runner.py ANALYSIS_PIPELINE")
        print('  python3 workflow_runner.py SOLUTION_ADOPTION \'{"request":"백업 시스템 분석"}\'')