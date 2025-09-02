#!/usr/bin/env python3
"""
재귀적 노드 생성기 - AI가 새로운 노드를 자동으로 생성
진정한 자기 성장 시스템의 핵심 컴포넌트
"""

import json
import subprocess
from pathlib import Path
from typing import Dict, Optional
from datetime import datetime


class RecursiveNodeGenerator:
    """새로운 작업 유형을 만나면 자동으로 노드 생성"""
    
    def __init__(self):
        self.nodes_dir = Path(__file__).parent.parent / "nodes"
        self.patterns_file = Path(__file__).parent.parent / "learned_patterns.json"
        self.load_patterns()
    
    def load_patterns(self):
        """학습된 패턴 로드"""
        if self.patterns_file.exists():
            with open(self.patterns_file, 'r') as f:
                self.patterns = json.load(f)
        else:
            self.patterns = {}
    
    def analyze_issue(self, issue_body: str) -> Dict:
        """이슈를 분석하여 필요한 노드 타입 결정"""
        # AI를 사용하여 이슈 분석
        analysis_prompt = f"""
        이슈 내용: {issue_body}
        
        이 작업에 필요한 노드를 분석하세요:
        1. 작업 유형 (예: API 구현, UI 컴포넌트, 데이터 처리)
        2. 필요한 기능 (예: 파일 생성, 코드 수정, 테스트)
        3. 입출력 형식
        """
        
        # AI 호출 (예: Claude API)
        result = self.call_ai_for_analysis(analysis_prompt)
        return result
    
    def generate_node_code(self, task_type: str, requirements: Dict) -> str:
        """AI를 사용하여 새로운 노드 코드 생성"""
        code_prompt = f"""
        다음 요구사항에 맞는 Python 노드 클래스를 생성하세요:
        
        작업 유형: {task_type}
        요구사항: {json.dumps(requirements, indent=2)}
        
        템플릿:
        ```python
        class {task_type.title().replace(' ', '')}Node:
            def __init__(self):
                self.name = "{task_type}"
                
            def execute(self, input_data):
                # 구현 로직
                pass
                
            def validate(self, result):
                # 검증 로직
                pass
        ```
        """
        
        # AI 호출하여 코드 생성
        generated_code = self.call_ai_for_code_generation(code_prompt)
        return generated_code
    
    def save_new_node(self, node_name: str, code: str) -> Path:
        """생성된 노드를 파일로 저장"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_name = f"{node_name}_{timestamp}.py"
        file_path = self.nodes_dir / file_name
        
        # 코드 검증
        if self.validate_code(code):
            with open(file_path, 'w') as f:
                f.write(code)
            print(f"✅ 새 노드 생성: {file_path}")
            
            # 패턴 저장
            self.save_pattern(node_name, code)
            return file_path
        else:
            raise ValueError("생성된 코드가 유효하지 않습니다")
    
    def validate_code(self, code: str) -> bool:
        """생성된 코드의 문법 검증"""
        try:
            compile(code, '<string>', 'exec')
            return True
        except SyntaxError:
            return False
    
    def save_pattern(self, node_name: str, code: str):
        """성공한 패턴을 저장하여 학습"""
        self.patterns[node_name] = {
            "code": code,
            "created_at": datetime.now().isoformat(),
            "usage_count": 0,
            "success_rate": 0.0
        }
        
        with open(self.patterns_file, 'w') as f:
            json.dump(self.patterns, f, indent=2)
    
    def call_ai_for_analysis(self, prompt: str) -> Dict:
        """AI를 호출하여 이슈 분석 (실제 구현 필요)"""
        # Claude/GPT API 호출 로직
        cmd = f'claude -p "analysis" "{prompt}"'
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        try:
            return json.loads(result.stdout)
        except:
            return {"type": "unknown", "requirements": {}}
    
    def call_ai_for_code_generation(self, prompt: str) -> str:
        """AI를 호출하여 코드 생성 (실제 구현 필요)"""
        cmd = f'claude -p "code_gen" "{prompt}"'
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        return result.stdout
    
    def learn_from_execution(self, node_name: str, success: bool):
        """실행 결과로부터 학습"""
        if node_name in self.patterns:
            self.patterns[node_name]["usage_count"] += 1
            if success:
                current_rate = self.patterns[node_name]["success_rate"]
                count = self.patterns[node_name]["usage_count"]
                # 성공률 업데이트
                self.patterns[node_name]["success_rate"] = (
                    (current_rate * (count - 1) + 1.0) / count
                )
            
            # 패턴 저장
            with open(self.patterns_file, 'w') as f:
                json.dump(self.patterns, f, indent=2)


def main():
    """사용 예시"""
    generator = RecursiveNodeGenerator()
    
    # 새로운 이슈 접수
    issue = "YouTube 동영상을 분석하여 요약하는 기능 구현"
    
    # 1. 이슈 분석
    analysis = generator.analyze_issue(issue)
    
    # 2. 기존 노드 확인
    existing_nodes = [f.stem for f in generator.nodes_dir.glob("*.py")]
    
    if analysis["type"] not in existing_nodes:
        print(f"🔄 새로운 노드 타입 발견: {analysis['type']}")
        
        # 3. 노드 코드 생성
        code = generator.generate_node_code(
            analysis["type"],
            analysis["requirements"]
        )
        
        # 4. 노드 저장
        generator.save_new_node(analysis["type"], code)
        
        print("✨ 시스템이 스스로 진화했습니다!")
    else:
        print(f"기존 노드 사용: {analysis['type']}")


if __name__ == "__main__":
    main()