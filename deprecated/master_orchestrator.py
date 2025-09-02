#!/usr/bin/env python3
"""마스터 오케스트레이터 - 모든 것을 통합하는 중앙 제어 시스템"""

import re
import sys
import json
from datetime import datetime
from typing import Dict, Optional
from node_executor import NodeExecutor
from workflow_runner import WorkflowRunner

class MasterOrchestrator:
    def __init__(self):
        self.node_executor = NodeExecutor()
        self.workflow_runner = WorkflowRunner()
        
        # 패턴 매칭 규칙 (정규식 → 워크플로우)
        self.pattern_rules = {
            r"분석|검토|평가|타당성|조사|리서치": "SOLUTION_ADOPTION",
            r"구현|개발|만들|생성|코딩|프로그래밍": "FEATURE_DEVELOPMENT",
            r"버그|오류|에러|수정|고치|문제": "BUGFIX_WORKFLOW",
            r"문서|설명|가이드|README|도큐": "DOCUMENTATION_PIPELINE",
            r"테스트|검증|확인|체크": "FEATURE_DEVELOPMENT",
            r"병렬|동시|멀티": "PARALLEL_ANALYSIS"
        }
        
        # 실행 히스토리
        self.history = []
    
    def process_request(self, request: str, context: Dict = None) -> Dict:
        """사용자 요청 처리 - 전체 플로우 자동화"""
        print("="*60)
        print(f"🤖 AI Orchestra v02 - Master Orchestrator")
        print(f"📝 요청: {request}")
        print("="*60)
        
        # 실행 기록
        execution = {
            "timestamp": datetime.now().isoformat(),
            "request": request,
            "context": context
        }
        
        # 1. 패턴 자동 감지
        pattern = self.detect_pattern(request)
        execution["pattern"] = pattern
        print(f"\n🎯 감지된 패턴: {pattern}")
        
        # 2. 컨텍스트 준비
        if not context:
            context = {}
        context["request"] = request
        context["pattern"] = pattern
        
        # 3. 워크플로우 실행
        print(f"\n🚀 워크플로우 실행: {pattern}")
        results = self.workflow_runner.run(pattern, context)
        execution["results"] = results
        
        # 4. 실행 기록 저장
        self.history.append(execution)
        self.save_history()
        
        print("\n" + "="*60)
        print("✨ 작업 완료!")
        print("="*60)
        
        return execution
    
    def detect_pattern(self, request: str) -> str:
        """패턴 자동 감지 - 요청에서 적절한 워크플로우 찾기"""
        request_lower = request.lower()
        
        # 패턴 매칭
        for regex, pattern in self.pattern_rules.items():
            if re.search(regex, request_lower):
                return pattern
        
        # 기본 패턴
        return "ANALYSIS_PIPELINE"
    
    def interactive_mode(self):
        """대화형 모드 - 지속적인 요청 처리"""
        print("🎮 AI Orchestra v02 - Interactive Mode")
        print("Commands: 'help', 'list', 'history', 'exit'")
        print("-"*60)
        
        while True:
            try:
                request = input("\n🤖 > ").strip()
                
                if not request:
                    continue
                
                # 특수 명령어 처리
                if request.lower() == 'exit' or request.lower() == 'quit':
                    print("👋 Goodbye!")
                    break
                
                elif request.lower() == 'help':
                    self.show_help()
                
                elif request.lower() == 'list':
                    self.workflow_runner.list_workflows()
                
                elif request.lower() == 'history':
                    self.show_history()
                
                elif request.startswith('node '):
                    # 단일 노드 실행
                    parts = request.split(' ', 2)
                    if len(parts) >= 2:
                        node_name = parts[1]
                        params = json.loads(parts[2]) if len(parts) > 2 else {}
                        result = self.node_executor.execute(node_name, params)
                        print(f"Result: {result}")
                
                elif request.startswith('workflow '):
                    # 특정 워크플로우 실행
                    parts = request.split(' ', 2)
                    if len(parts) >= 2:
                        workflow_name = parts[1]
                        context = json.loads(parts[2]) if len(parts) > 2 else {}
                        self.workflow_runner.run(workflow_name, context)
                
                else:
                    # 일반 요청 처리
                    self.process_request(request)
                    
            except KeyboardInterrupt:
                print("\n👋 Interrupted. Type 'exit' to quit.")
            except Exception as e:
                print(f"❌ Error: {e}")
    
    def show_help(self):
        """도움말 표시"""
        print("""
📚 AI Orchestra v02 - Help
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        
일반 사용:
  그냥 원하는 작업을 입력하세요.
  예: "Claude Code 백업 시스템 분석해줘"
      "버그 수정이 필요해"
      "API 문서를 작성해줘"

특수 명령어:
  help                          - 이 도움말 표시
  list                          - 사용 가능한 워크플로우 목록
  history                       - 실행 히스토리 보기
  node NODE_NAME [params]       - 단일 노드 실행
  workflow WORKFLOW_NAME [ctx]  - 특정 워크플로우 실행
  exit / quit                   - 종료

패턴 매칭:
  분석/검토/평가    → SOLUTION_ADOPTION
  구현/개발/만들    → FEATURE_DEVELOPMENT  
  버그/오류/수정    → BUGFIX_WORKFLOW
  문서/설명/가이드  → DOCUMENTATION_PIPELINE
  병렬/동시        → PARALLEL_ANALYSIS
        """)
    
    def show_history(self):
        """실행 히스토리 표시"""
        if not self.history:
            print("📭 No execution history yet.")
            return
        
        print("\n📜 Execution History")
        print("━"*60)
        for i, execution in enumerate(self.history[-5:], 1):  # 최근 5개만
            print(f"\n{i}. {execution['timestamp']}")
            print(f"   Request: {execution['request']}")
            print(f"   Pattern: {execution['pattern']}")
            if execution.get('results'):
                print(f"   Results: {len(execution['results'])} steps completed")
    
    def save_history(self):
        """히스토리를 파일로 저장"""
        try:
            with open('.orchestrator_history.json', 'w') as f:
                json.dump(self.history[-100:], f, indent=2, default=str)  # 최근 100개만
        except:
            pass  # 저장 실패 무시
    
    def load_history(self):
        """히스토리 로드"""
        try:
            with open('.orchestrator_history.json', 'r') as f:
                self.history = json.load(f)
        except:
            self.history = []


def main():
    """메인 실행 함수"""
    orchestrator = MasterOrchestrator()
    orchestrator.load_history()
    
    # CLI 모드
    if len(sys.argv) > 1:
        # 명령어 파싱
        command = sys.argv[1]
        
        if command in ['--help', '-h']:
            orchestrator.show_help()
        
        elif command in ['--list', '-l']:
            orchestrator.workflow_runner.list_workflows()
        
        elif command in ['--interactive', '-i']:
            orchestrator.interactive_mode()
        
        else:
            # 일반 요청으로 처리
            request = " ".join(sys.argv[1:])
            
            # 컨텍스트 확인 (마지막 인자가 JSON인 경우)
            context = {}
            if request.endswith('}'):
                # JSON 컨텍스트 분리 시도
                try:
                    import re
                    match = re.search(r'(\{.*\})$', request)
                    if match:
                        context = json.loads(match.group(1))
                        request = request[:match.start()].strip()
                except:
                    pass
            
            orchestrator.process_request(request, context)
    
    else:
        # 대화형 모드
        orchestrator.interactive_mode()


if __name__ == "__main__":
    main()