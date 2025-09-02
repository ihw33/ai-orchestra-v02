#!/usr/bin/env python3
"""
AI 인터페이스 - 실제 AI API 연결
Claude, GPT 등과 통신하여 코드 생성
"""

import json
import subprocess
import os
from typing import Dict, Optional, Any
from pathlib import Path


class AIInterface:
    """AI API 통합 인터페이스"""
    
    def __init__(self):
        # API 키 확인 (환경변수에서)
        self.claude_available = bool(os.getenv("ANTHROPIC_API_KEY"))
        self.gpt_available = bool(os.getenv("OPENAI_API_KEY"))
        self.gemini_available = bool(os.getenv("GOOGLE_AI_KEY"))
        
    def analyze_issue(self, issue_body: str) -> Dict[str, Any]:
        """이슈를 분석하여 필요한 노드 타입과 요구사항 추출"""
        
        prompt = f"""다음 GitHub 이슈를 분석하여 JSON 형식으로 응답하세요:

이슈 내용:
{issue_body}

분석 항목:
1. task_type: feature|bugfix|refactor|documentation|test
2. required_nodes: 필요한 노드 타입 리스트
3. complexity: low|medium|high
4. technologies: 관련 기술 스택
5. estimated_nodes: 예상 노드 개수

JSON 형식으로만 응답:
"""
        
        # Claude 우선, 없으면 다른 AI 사용
        if self.claude_available:
            result = self._call_claude(prompt, "json")
        elif self.gemini_available:
            result = self._call_gemini(prompt)
        elif self.gpt_available:
            result = self._call_gpt(prompt)
        else:
            # AI 없으면 기본 분석
            result = self._fallback_analysis(issue_body)
        
        return result
    
    def generate_node_code(self, node_type: str, requirements: Dict) -> str:
        """노드 코드 생성"""
        
        # 템플릿 로드
        template = self._get_node_template()
        
        prompt = f"""다음 요구사항에 맞는 Python 노드 클래스를 생성하세요:

노드 타입: {node_type}
요구사항: {json.dumps(requirements, indent=2, ensure_ascii=False)}

템플릿:
{template}

요구사항:
1. 완전한 Python 코드를 생성하세요
2. 에러 처리를 포함하세요
3. 로깅을 포함하세요
4. 타입 힌트를 사용하세요
5. 독스트링을 포함하세요

Python 코드만 응답하세요 (```python 태그 없이):
"""
        
        if self.claude_available:
            code = self._call_claude(prompt, "code")
        elif self.gemini_available:
            code = self._call_gemini_code(prompt)
        else:
            # 기본 템플릿 사용
            code = self._generate_basic_node(node_type, requirements)
        
        return code
    
    def _call_claude(self, prompt: str, output_type: str = "text") -> Any:
        """Claude API 호출 (CLI 사용)"""
        try:
            # claude CLI가 설치되어 있다고 가정
            cmd = ['claude', '-p', 'code_gen', prompt]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if output_type == "json":
                # JSON 파싱 시도
                try:
                    # Claude 응답에서 JSON 부분만 추출
                    response_text = result.stdout.strip()
                    # JSON 블록 찾기
                    if '```json' in response_text:
                        json_start = response_text.find('```json') + 7
                        json_end = response_text.find('```', json_start)
                        json_text = response_text[json_start:json_end].strip()
                    else:
                        json_text = response_text
                    
                    return json.loads(json_text)
                except:
                    return self._fallback_analysis("")
            else:
                return result.stdout.strip()
                
        except Exception as e:
            print(f"Claude API 호출 실패: {e}")
            return self._fallback_analysis("") if output_type == "json" else ""
    
    def _call_gemini(self, prompt: str) -> Dict:
        """Gemini API 호출"""
        try:
            cmd = ['gemini', '-p', prompt]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            # JSON 파싱 시도
            try:
                return json.loads(result.stdout.strip())
            except:
                return self._fallback_analysis("")
                
        except Exception:
            return self._fallback_analysis("")
    
    def _call_gemini_code(self, prompt: str) -> str:
        """Gemini로 코드 생성"""
        try:
            cmd = ['gemini', '-p', prompt]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            return result.stdout.strip()
        except:
            return ""
    
    def _call_gpt(self, prompt: str) -> Dict:
        """GPT API 호출 (구현 필요)"""
        # OpenAI API 직접 호출 또는 CLI 사용
        return self._fallback_analysis("")
    
    def _fallback_analysis(self, issue_body: str) -> Dict:
        """AI 없을 때 기본 분석"""
        issue_lower = issue_body.lower()
        
        # 키워드 기반 분석
        task_type = "feature"
        if any(word in issue_lower for word in ["bug", "fix", "error"]):
            task_type = "bugfix"
        elif any(word in issue_lower for word in ["refactor", "improve"]):
            task_type = "refactor"
        elif any(word in issue_lower for word in ["test", "spec"]):
            task_type = "test"
        elif any(word in issue_lower for word in ["docs", "document"]):
            task_type = "documentation"
        
        # 필요한 노드 추정
        required_nodes = []
        if "api" in issue_lower:
            required_nodes.append("api_handler")
        if "database" in issue_lower or "db" in issue_lower:
            required_nodes.append("db_migration")
        if "ui" in issue_lower or "frontend" in issue_lower:
            required_nodes.append("ui_component")
        if "test" in issue_lower:
            required_nodes.append("test_runner")
        
        # 기본 노드 추가
        if task_type == "feature":
            required_nodes.extend(["analyzer", "implementer", "tester"])
        elif task_type == "bugfix":
            required_nodes.extend(["bug_finder", "fixer", "verifier"])
        
        return {
            "task_type": task_type,
            "required_nodes": required_nodes,
            "complexity": "medium",
            "technologies": [],
            "estimated_nodes": len(required_nodes)
        }
    
    def _get_node_template(self) -> str:
        """노드 템플릿 반환"""
        return '''#!/usr/bin/env python3
"""
자동 생성된 노드
"""

from typing import Dict, Any, Optional
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class AutoGeneratedNode:
    """자동 생성된 노드 클래스"""
    
    def __init__(self):
        self.name = "auto_generated"
        self.description = "AI가 자동 생성한 노드"
        
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """노드 실행"""
        try:
            logger.info(f"노드 실행 시작: {self.name}")
            
            # TODO: 실제 로직 구현
            result = {
                "status": "success",
                "message": f"{self.name} 실행 완료"
            }
            
            logger.info(f"노드 실행 완료: {self.name}")
            return result
            
        except Exception as e:
            logger.error(f"노드 실행 실패: {e}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    def validate(self, input_data: Dict[str, Any]) -> bool:
        """입력 데이터 검증"""
        return True
'''
    
    def _generate_basic_node(self, node_type: str, requirements: Dict) -> str:
        """기본 노드 코드 생성"""
        class_name = f"{node_type.title().replace('_', '')}Node"
        
        code = f'''#!/usr/bin/env python3
"""
{node_type} 노드 - 자동 생성됨
"""

from typing import Dict, Any, Optional
import logging
import subprocess
from pathlib import Path

logger = logging.getLogger(__name__)


class {class_name}:
    """{node_type} 작업을 수행하는 노드"""
    
    def __init__(self):
        self.name = "{node_type}"
        self.description = "{requirements.get('description', 'Auto-generated node')}"
        self.requirements = {requirements}
        
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """노드 실행"""
        try:
            logger.info(f"실행 시작: {{self.name}}")
            
            # 컨텍스트에서 필요한 데이터 추출
            issue_id = context.get("issue_id")
            task_type = context.get("task_type")
            
'''
        
        # 노드 타입별 기본 로직 추가
        if "api" in node_type.lower():
            code += '''            # API 관련 작업
            api_endpoint = context.get("api_endpoint", "/api/default")
            
            # API 스펙 생성 또는 구현
            result = {
                "api_spec": f"Generated API spec for {api_endpoint}",
                "implementation": "API handler code here"
            }
'''
        elif "test" in node_type.lower():
            code += '''            # 테스트 실행
            test_command = context.get("test_command", "pytest")
            
            # 테스트 실행
            proc = subprocess.run(test_command, shell=True, capture_output=True, text=True)
            
            result = {
                "test_output": proc.stdout,
                "test_passed": proc.returncode == 0
            }
'''
        elif "db" in node_type.lower() or "database" in node_type.lower():
            code += '''            # 데이터베이스 작업
            db_operation = context.get("db_operation", "migrate")
            
            result = {
                "db_status": f"Database {db_operation} completed",
                "schema_changes": []
            }
'''
        else:
            code += '''            # 기본 작업 수행
            result = {
                "status": "completed",
                "output": f"{self.name} executed successfully"
            }
'''
        
        code += '''            
            logger.info(f"실행 완료: {self.name}")
            return result
            
        except Exception as e:
            logger.error(f"실행 실패: {e}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    def validate(self, input_data: Dict[str, Any]) -> bool:
        """입력 데이터 검증"""
        # 필수 필드 체크
        required_fields = ["issue_id", "task_type"]
        for field in required_fields:
            if field not in input_data:
                logger.warning(f"필수 필드 누락: {field}")
                return False
        return True
    
    def cleanup(self):
        """정리 작업"""
        logger.info(f"정리 작업: {self.name}")
        pass
'''
        
        return code


def test_ai_interface():
    """테스트 함수"""
    ai = AIInterface()
    
    # 이슈 분석 테스트
    issue = """
    [AI] YouTube 동영상 분석 기능 구현
    - YouTube URL에서 동영상 정보 추출
    - 자막 다운로드 및 분석
    - AI를 사용한 요약 생성
    """
    
    print("🔍 이슈 분석 중...")
    analysis = ai.analyze_issue(issue)
    print(f"분석 결과: {json.dumps(analysis, indent=2, ensure_ascii=False)}")
    
    # 노드 코드 생성 테스트
    if analysis.get("required_nodes"):
        node_type = analysis["required_nodes"][0]
        print(f"\n🔧 노드 생성 중: {node_type}")
        code = ai.generate_node_code(node_type, {"description": "YouTube 분석"})
        print(f"생성된 코드 (처음 20줄):")
        print("\n".join(code.split("\n")[:20]))


if __name__ == "__main__":
    test_ai_interface()