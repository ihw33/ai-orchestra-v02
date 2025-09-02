#!/usr/bin/env python3
"""
재귀적 DAG 구성기 - AI가 새로운 워크플로우를 자동으로 구성
노드들을 조합하여 최적의 실행 순서 결정
"""

import json
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime


class RecursiveDAGComposer:
    """작업 요구사항에 맞춰 DAG를 자동으로 구성"""
    
    def __init__(self):
        self.dags_dir = Path(__file__).parent.parent / "dags"
        self.nodes_dir = Path(__file__).parent.parent / "nodes"
        self.dag_patterns_file = Path(__file__).parent.parent / "learned_dag_patterns.json"
        self.load_patterns()
    
    def load_patterns(self):
        """학습된 DAG 패턴 로드"""
        if self.dag_patterns_file.exists():
            with open(self.dag_patterns_file, 'r') as f:
                self.patterns = json.load(f)
        else:
            self.patterns = {
                "feature": ["analyze", "design", "implement", "test", "document"],
                "bugfix": ["reproduce", "diagnose", "fix", "test", "verify"],
                "refactor": ["analyze", "plan", "refactor", "test", "cleanup"]
            }
    
    def analyze_requirements(self, issue_body: str) -> Dict:
        """요구사항을 분석하여 필요한 노드 시퀀스 결정"""
        # 키워드 기반 작업 타입 판단
        issue_lower = issue_body.lower()
        
        if any(word in issue_lower for word in ["bug", "fix", "error", "broken"]):
            task_type = "bugfix"
        elif any(word in issue_lower for word in ["feature", "implement", "add", "create"]):
            task_type = "feature"
        elif any(word in issue_lower for word in ["refactor", "improve", "optimize"]):
            task_type = "refactor"
        else:
            task_type = "general"
        
        # AI를 사용하여 더 정교한 분석
        return self.ai_analyze_requirements(issue_body, task_type)
    
    def ai_analyze_requirements(self, issue_body: str, task_type: str) -> Dict:
        """AI를 사용하여 상세 요구사항 분석"""
        analysis = {
            "task_type": task_type,
            "required_nodes": [],
            "dependencies": {},
            "parallel_possible": []
        }
        
        # 작업 타입별 기본 노드 시퀀스
        if task_type in self.patterns:
            analysis["required_nodes"] = self.patterns[task_type].copy()
        
        # 이슈 내용에서 추가 노드 추출
        if "api" in issue_body.lower():
            analysis["required_nodes"].append("api_implementation")
        if "database" in issue_body.lower():
            analysis["required_nodes"].append("db_migration")
        if "ui" in issue_body.lower() or "frontend" in issue_body.lower():
            analysis["required_nodes"].append("ui_component")
        
        return analysis
    
    def compose_dag(self, analysis: Dict) -> str:
        """분석 결과를 바탕으로 DAG 코드 생성"""
        dag_name = f"{analysis['task_type']}_dag_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        dag_code = f'''#!/usr/bin/env python3
"""
자동 생성된 DAG: {dag_name}
작업 타입: {analysis['task_type']}
생성 시간: {datetime.now().isoformat()}
"""

from typing import Dict, Any
from pathlib import Path
import sys

# 부모 디렉토리를 경로에 추가
sys.path.append(str(Path(__file__).parent.parent))


class {dag_name.title().replace('_', '')}:
    """자동 생성된 DAG"""
    
    def __init__(self):
        self.name = "{dag_name}"
        self.nodes = []
        self.setup_nodes()
    
    def setup_nodes(self):
        """노드 구성"""
'''
        
        # 노드 임포트 및 초기화
        for node in analysis["required_nodes"]:
            node_class = f"{node.title().replace('_', '')}Node"
            dag_code += f'''        try:
            from nodes.{node}_node import {node_class}
            self.nodes.append({node_class}())
        except ImportError:
            print(f"노드 {{'{node}_node'}} 를 찾을 수 없습니다. 생성 중...")
            # 여기서 recursive_node_generator 호출하여 노드 생성
            pass
            
'''
        
        dag_code += '''    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """DAG 실행"""
        results = {}
        
        for node in self.nodes:
            try:
                print(f"실행 중: {node.name}")
                result = node.execute(context)
                results[node.name] = result
                context.update(result)  # 다음 노드를 위해 컨텍스트 업데이트
            except Exception as e:
                print(f"노드 {node.name} 실행 실패: {e}")
                results[node.name] = {"error": str(e)}
        
        return results
    
    def validate(self) -> bool:
        """DAG 유효성 검증"""
        return len(self.nodes) > 0


def main():
    """DAG 실행"""
    dag = ''' + f'''{dag_name.title().replace('_', '')}()
    
    context = {{
        "issue_id": "TBD",
        "task_type": "{analysis['task_type']}"
    }}
    
    results = dag.execute(context)
    print(f"DAG 실행 완료: {{results}}")


if __name__ == "__main__":
    main()
'''
        
        return dag_code
    
    def save_dag(self, dag_code: str, dag_name: str) -> Path:
        """생성된 DAG를 파일로 저장"""
        file_path = self.dags_dir / f"{dag_name}.py"
        
        with open(file_path, 'w') as f:
            f.write(dag_code)
        
        print(f"✅ 새 DAG 생성: {file_path}")
        
        # 패턴 학습
        self.learn_pattern(dag_name, dag_code)
        
        return file_path
    
    def learn_pattern(self, dag_name: str, dag_code: str):
        """성공한 DAG 패턴 학습"""
        # 코드에서 노드 시퀀스 추출
        import re
        nodes = re.findall(r'from nodes\.(\w+)_node', dag_code)
        
        if nodes:
            task_type = dag_name.split('_')[0]
            if task_type not in self.patterns:
                self.patterns[task_type] = nodes
            else:
                # 기존 패턴과 병합 (중복 제거)
                self.patterns[task_type] = list(set(self.patterns[task_type] + nodes))
            
            # 패턴 저장
            with open(self.dag_patterns_file, 'w') as f:
                json.dump(self.patterns, f, indent=2)
    
    def optimize_dag(self, dag_name: str, execution_metrics: Dict):
        """실행 메트릭을 바탕으로 DAG 최적화"""
        # 병렬 실행 가능한 노드 찾기
        # 불필요한 노드 제거
        # 실행 순서 최적화
        pass


def main():
    """사용 예시"""
    composer = RecursiveDAGComposer()
    
    # 새로운 이슈
    issue = """
    [AI] YouTube 동영상 분석 및 요약 기능 구현
    - YouTube URL에서 동영상 정보 추출
    - 자막 다운로드 및 분석
    - AI를 사용한 요약 생성
    - 결과를 데이터베이스에 저장
    """
    
    # 1. 요구사항 분석
    analysis = composer.analyze_requirements(issue)
    print(f"📊 분석 결과: {analysis}")
    
    # 2. DAG 구성
    dag_code = composer.compose_dag(analysis)
    
    # 3. DAG 저장
    dag_name = f"{analysis['task_type']}_youtube_analysis"
    composer.save_dag(dag_code, dag_name)
    
    print("✨ 새로운 워크플로우가 자동으로 생성되었습니다!")


if __name__ == "__main__":
    main()