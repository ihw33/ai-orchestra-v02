#!/usr/bin/env python3
"""
Orchestrator - 자연어 지시를 분석하여 노드/프로세스 자동 조합 및 실행
PM의 핵심 두뇌 역할
"""

import re
import json
from typing import List, Dict, Any, Optional
from datetime import datetime
import subprocess

from node_system import NodeType, NodeFactory, PersonaNode, ExecutionMode
from process_engine import WorkflowProcess, ProcessBuilder, ProcessTemplates
from metrics_system import MetricsCollector
from trigger_system import TriggerSystem

class InstructionAnalyzer:
    """자연어 지시 분석기"""
    
    def __init__(self):
        # 의도 매핑
        self.intent_patterns = {
            "create": ["만들", "생성", "추가", "새로"],
            "fix": ["수정", "고치", "버그", "에러", "오류"],
            "analyze": ["분석", "조사", "파악", "확인", "알아"],
            "deploy": ["배포", "릴리즈", "출시"],
            "test": ["테스트", "검증", "확인"],
            "review": ["리뷰", "검토", "확인"]
        }
        
        # 긴급도 키워드
        self.urgency_keywords = {
            "high": ["급해", "빨리", "즉시", "ASAP", "긴급"],
            "low": ["천천히", "여유", "나중에"],
            "perfect": ["완벽", "꼼꼼", "제대로", "철저"]
        }
    
    def analyze(self, instruction: str) -> Dict:
        """지시 분석"""
        result = {
            "original": instruction,
            "intent": self.detect_intent(instruction),
            "urgency": self.detect_urgency(instruction),
            "entities": self.extract_entities(instruction),
            "suggested_nodes": [],
            "suggested_process": None,
            "persona": self.suggest_persona(instruction)
        }
        
        # 노드 제안
        result["suggested_nodes"] = self.suggest_nodes(result["intent"], instruction)
        
        # 프로세스 제안
        result["suggested_process"] = self.suggest_process(result["intent"], result["urgency"])
        
        return result
    
    def detect_intent(self, text: str) -> str:
        """의도 파악"""
        text_lower = text.lower()
        
        for intent, keywords in self.intent_patterns.items():
            if any(kw in text_lower for kw in keywords):
                return intent
        
        return "unknown"
    
    def detect_urgency(self, text: str) -> str:
        """긴급도 파악"""
        text_lower = text.lower()
        
        for urgency, keywords in self.urgency_keywords.items():
            if any(kw in text_lower for kw in keywords):
                return urgency
        
        return "normal"
    
    def extract_entities(self, text: str) -> Dict:
        """엔티티 추출 (이슈 번호, 파일명 등)"""
        entities = {}
        
        # 이슈 번호
        issue_match = re.search(r'#(\d+)', text)
        if issue_match:
            entities["issue_number"] = issue_match.group(1)
        
        # 파일명
        file_match = re.search(r'(\w+\.\w+)', text)
        if file_match:
            entities["file_name"] = file_match.group(1)
        
        return entities
    
    def suggest_nodes(self, intent: str, instruction: str) -> List[NodeType]:
        """의도에 따른 노드 제안"""
        node_suggestions = {
            "create": [NodeType.CREATE_FILE, NodeType.WRITE_FUNCTION, NodeType.CREATE_ISSUE],
            "fix": [NodeType.ANALYZE_CODE, NodeType.FIX_BUG_LINE, NodeType.RUN_TEST],
            "analyze": [NodeType.ANALYZE_CODE, NodeType.FIND_PATTERN, NodeType.CREATE_REPORT],
            "deploy": [NodeType.RUN_TEST, NodeType.CHECK_STATUS, NodeType.RUN_COMMAND],
            "test": [NodeType.WRITE_TEST_CASE, NodeType.RUN_TEST, NodeType.CHECK_COVERAGE],
            "review": [NodeType.REVIEW_CODE, NodeType.SUGGEST_IMPROVEMENT, NodeType.ADD_COMMENT]
        }
        
        return node_suggestions.get(intent, [])
    
    def suggest_process(self, intent: str, urgency: str) -> str:
        """의도와 긴급도에 따른 프로세스 제안"""
        if intent == "fix":
            if urgency == "high":
                return "bug_fix_quick"
            else:
                return "bug_fix_thorough"
        
        elif intent == "create":
            if urgency == "perfect":
                return "feature_development_complete"
            else:
                return "feature_development"
        
        elif intent == "analyze":
            return "research_process"
        
        return "standard_process"
    
    def suggest_persona(self, instruction: str) -> str:
        """지시에 따른 페르소나 제안"""
        instruction_lower = instruction.lower()
        
        if any(word in instruction_lower for word in ["빨리", "급해"]):
            return "speedster"
        elif any(word in instruction_lower for word in ["완벽", "꼼꼼"]):
            return "perfectionist"
        elif any(word in instruction_lower for word in ["문제", "이슈", "버그"]):
            return "critic"
        elif any(word in instruction_lower for word in ["간단", "최소"]):
            return "minimalist"
        
        return None

class SmartOrchestrator:
    """스마트 오케스트레이터 - PM의 핵심"""
    
    def __init__(self):
        self.analyzer = InstructionAnalyzer()
        self.metrics = MetricsCollector()
        self.triggers = TriggerSystem()
        self.execution_history = []
        self.learning_patterns = {}
    
    def process_instruction(self, instruction: str, auto_execute: bool = False, issue_number: str = None) -> Dict:
        """지시 처리 메인 함수"""
        
        # 1. GitHub 이슈 생성 (issue_number가 없을 때만)
        if not issue_number:
            issue_number = self.create_github_issue(instruction)
            if not issue_number:
                return {"status": "failed", "error": "GitHub 이슈 생성 실패"}
            print(f"✅ GitHub Issue #{issue_number} 생성됨")
        
        # 2. 지시 분석
        analysis = self.analyzer.analyze(instruction)
        print(f"\n📋 분석 결과 (Issue #{issue_number}):")
        print(f"  의도: {analysis['intent']}")
        print(f"  긴급도: {analysis['urgency']}")
        print(f"  제안 노드: {[n.value for n in analysis['suggested_nodes']]}")
        print(f"  제안 프로세스: {analysis['suggested_process']}")
        
        # 3. 과거 패턴 확인
        similar_pattern = self.find_similar_pattern(instruction)
        if similar_pattern:
            print(f"\n💡 유사 패턴 발견:")
            print(f"  이전 작업: {similar_pattern['instruction']}")
            print(f"  성공률: {similar_pattern['success_rate']}%")
            
            # Thomas 확인
            if not auto_execute:
                response = input("  같은 방식으로 진행할까요? (y/n): ")
                if response.lower() == 'y':
                    return self.execute_pattern(similar_pattern)
        
        # 4. 프로세스 생성 (이슈 번호 포함)
        process = self.create_process(analysis, issue_number)
        
        # 4. Thomas 승인 (중요한 경우)
        if analysis['urgency'] in ['high', 'perfect'] and not auto_execute:
            print(f"\n⚠️ Thomas 승인 필요:")
            print(f"  프로세스: {process.state.name}")
            print(f"  노드 수: {len(process.state.nodes)}")
            response = input("  진행하시겠습니까? (y/n): ")
            if response.lower() != 'y':
                return {"status": "cancelled"}
        
        # 5. 실행
        result = self.execute_process(process)
        
        # 6. GitHub 이슈에 결과 보고
        self.report_to_github_issue(issue_number, result)
        
        # 7. 학습
        self.learn_from_execution(instruction, process, result)
        
        result['issue_number'] = issue_number
        return result
    
    def create_process(self, analysis: Dict, issue_number: str = None) -> WorkflowProcess:
        """분석 결과로 프로세스 생성"""
        
        # 템플릿 사용
        if analysis['suggested_process'] == "bug_fix_quick":
            process = ProcessTemplates.bug_fix_process(issue_number)
        elif analysis['suggested_process'] == "feature_development":
            process = ProcessTemplates.feature_development(issue_number)
        elif analysis['suggested_process'] == "research_process":
            process = ProcessTemplates.research_process(issue_number)
        else:
            # 커스텀 프로세스 생성
            process = self.create_custom_process(analysis, issue_number)
        
        # 페르소나 적용
        if analysis['persona']:
            self.apply_persona_to_process(process, analysis['persona'])
        
        return process
    
    def create_custom_process(self, analysis: Dict, issue_number: str = None) -> WorkflowProcess:
        """커스텀 프로세스 동적 생성"""
        builder = ProcessBuilder(f"Custom Process - {analysis['intent']}", issue_number=issue_number)
        
        # 제안된 노드들로 프로세스 구성
        for node_type in analysis['suggested_nodes']:
            # AI 할당 (노드 타입별 최적 AI)
            executor = self.get_best_executor(node_type)
            
            # 긴급도에 따른 모드 결정
            if analysis['urgency'] == 'high':
                mode = ExecutionMode.PARALLEL
            else:
                mode = ExecutionMode.INTERACTIVE if node_type == NodeType.REVIEW_CODE else ExecutionMode.PARALLEL
            
            builder.add(node_type, executor=executor, mode=mode)
        
        return builder.build()
    
    def get_best_executor(self, node_type: NodeType) -> str:
        """노드 타입별 최적 AI 선택"""
        # 과거 성공률 기반 또는 기본 매핑
        best_executors = {
            NodeType.ANALYZE_CODE: "claude",
            NodeType.WRITE_FUNCTION: "codex",
            NodeType.FIX_BUG_LINE: "codex",
            NodeType.RUN_TEST: "gemini",
            NodeType.CREATE_REPORT: "claude",
            NodeType.REVIEW_CODE: "claude"
        }
        
        return best_executors.get(node_type, "claude")
    
    def apply_persona_to_process(self, process: WorkflowProcess, persona_type: str):
        """프로세스에 페르소나 적용"""
        persona = PersonaNode(persona_type)
        
        # 모든 노드에 페르소나 적용
        for node in process.state.nodes:
            persona.apply_to_node(node)
    
    def execute_process(self, process: WorkflowProcess) -> Dict:
        """프로세스 실행 및 모니터링"""
        print(f"\n🚀 프로세스 실행 시작: {process.state.name}")
        
        # 메트릭 기록 시작
        self.metrics.start_process(process.state.id)
        
        try:
            # 실행
            result = process.execute()
            
            # 성공 기록
            self.metrics.end_process(process.state.id, success=True)
            print(f"✅ 프로세스 완료")
            
        except Exception as e:
            # 실패 기록
            self.metrics.end_process(process.state.id, success=False)
            print(f"❌ 프로세스 실패: {e}")
            result = {"status": "failed", "error": str(e)}
        
        # 결과 저장
        self.execution_history.append({
            "timestamp": datetime.now().isoformat(),
            "process": process.state.name,
            "result": result
        })
        
        return result
    
    def find_similar_pattern(self, instruction: str) -> Optional[Dict]:
        """유사한 과거 패턴 찾기"""
        # 간단한 유사도 매칭 (실제로는 더 정교한 알고리즘 필요)
        for pattern in self.learning_patterns.values():
            if self.calculate_similarity(instruction, pattern['instruction']) > 0.7:
                return pattern
        
        return None
    
    def calculate_similarity(self, text1: str, text2: str) -> float:
        """텍스트 유사도 계산 (간단한 버전)"""
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union)
    
    def learn_from_execution(self, instruction: str, process: WorkflowProcess, result: Dict):
        """실행 결과에서 학습"""
        pattern_key = f"{self.analyzer.detect_intent(instruction)}_{datetime.now().date()}"
        
        success = result.get('status') != 'failed'
        
        if pattern_key not in self.learning_patterns:
            self.learning_patterns[pattern_key] = {
                "instruction": instruction,
                "process": process.state.name,
                "executions": 0,
                "successes": 0,
                "nodes_used": [n.state.type.value for n in process.state.nodes]
            }
        
        pattern = self.learning_patterns[pattern_key]
        pattern["executions"] += 1
        if success:
            pattern["successes"] += 1
        
        pattern["success_rate"] = (pattern["successes"] / pattern["executions"]) * 100
    
    def execute_pattern(self, pattern: Dict) -> Dict:
        """저장된 패턴 실행"""
        # 패턴에서 프로세스 재생성
        builder = ProcessBuilder(f"Pattern - {pattern['process']}")
        
        for node_type_str in pattern['nodes_used']:
            node_type = NodeType(node_type_str)
            builder.add(node_type, executor=self.get_best_executor(node_type))
        
        process = builder.build()
        return self.execute_process(process)
    
    def create_github_issue(self, instruction: str) -> str:
        """GitHub 이슈 생성"""
        import subprocess
        from datetime import datetime
        
        # 먼저 지시 분석
        analysis = self.analyzer.analyze(instruction)
        
        title = f"[AI Orchestra] {instruction[:50]}"
        
        # AI 할당 자동 생성
        ai_assignments = []
        for node_type in analysis['suggested_nodes']:
            executor = self.get_best_executor(node_type)
            ai_assignments.append(f"- **{executor.upper()}**: {node_type.value}")
        
        # 페르소나 추가
        persona_text = ""
        if analysis['persona']:
            persona_text = f"\n### 🎭 페르소나\n- 적용: **{analysis['persona']}**"
        
        body = f"""## 🤖 자동 생성 작업

### 📝 지시사항
{instruction}

### 🤖 담당 AI 자동 할당
{chr(10).join(ai_assignments)}
{persona_text}

### 📋 노드 구성
```python
ProcessBuilder('{analysis['suggested_process']}', issue_number='자동생성')
{chr(10).join(f"    .add(NodeType.{n.name}, executor='{self.get_best_executor(n)}')" for n in analysis['suggested_nodes'])}
    .build()
```

### 🎯 작업 계획
- 의도: {analysis['intent']}
- 긴급도: {analysis['urgency']}
- 프로세스: {analysis['suggested_process']}

### ⏰ 생성 시간
{datetime.now().isoformat()}

---
*AI Orchestra v2 - SmartOrchestrator*"""
        
        cmd = f'''gh issue create -R ihw33/ai-orchestra-v02 \
            --title "{title}" \
            --body "{body}"'''
        
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        
        if result.returncode == 0:
            issue_url = result.stdout.strip()
            issue_number = issue_url.split('/')[-1]
            return issue_number
        
        return None
    
    def report_to_github_issue(self, issue_number: str, result: Dict):
        """GitHub 이슈에 결과 보고"""
        import subprocess
        from datetime import datetime
        
        status = "✅ 성공" if result.get('status') != 'failed' else "❌ 실패"
        
        comment = f"""## {status} 작업 완료 리포트

### 📊 실행 결과
- **프로세스**: {result.get('name', 'Unknown')}
- **상태**: {result.get('status', 'unknown')}
- **실행 시간**: {result.get('duration', 0):.2f}초
- **노드 수**: {len(result.get('nodes', {}))}

### 🤖 노드별 실행 결과
"""
        
        for node_id, node_result in result.get('nodes', {}).items():
            node_status = "✅" if node_result['status'] == 'completed' else "❌"
            comment += f"- {node_status} {node_result['type']}: {node_result['status']}\n"
        
        comment += f"""
### ⏰ 완료 시간
{datetime.now().isoformat()}

---
*AI Orchestra v2 자동 보고*"""
        
        cmd = f'gh issue comment {issue_number} -R ihw33/ai-orchestra-v02 --body "{comment}"'
        subprocess.run(cmd, shell=True, capture_output=True, text=True)

# PM 의사결정 규칙
class PMDecisionRules:
    """PM의 의사결정 규칙 - 명시적 정의"""
    
    @staticmethod
    def should_stop_work() -> Dict:
        """작업 중단 여부 결정"""
        checklist = {
            "핵심_개념_정의": True,
            "구체적_예시": True,
            "문서화_완료": True,
            "다음_단계_명확": True
        }
        
        if all(checklist.values()):
            return {
                "decision": "STOP",
                "message": "여기까지가 적절한 것 같습니다.",
                "next_options": [
                    "여기서 마무리",
                    "POC 구현",
                    "다른 작업으로 전환"
                ]
            }
        
        return {"decision": "CONTINUE"}
    
    @staticmethod
    def select_process_type(context: Dict) -> str:
        """상황에 따른 프로세스 선택"""
        if context.get("deadline") == "urgent":
            return "quick_process"
        elif context.get("importance") == "critical":
            return "thorough_process"
        elif context.get("uncertainty") == "high":
            return "research_process"
        else:
            return "standard_process"

# 사용 예시
if __name__ == "__main__":
    # 오케스트레이터 초기화
    orchestrator = SmartOrchestrator()
    
    # 테스트 지시들
    test_instructions = [
        "버그 #123을 빨리 수정해줘",
        "로그인 기능을 완벽하게 만들어줘",
        "이 코드가 왜 느린지 분석해줘",
        "테스트 커버리지를 확인하고 개선해줘"
    ]
    
    print("=== AI Orchestra 스마트 오케스트레이터 ===\n")
    
    for instruction in test_instructions:
        print(f"\n{'='*50}")
        print(f"📝 지시: {instruction}")
        print(f"{'='*50}")
        
        # 자동 처리 (데모 모드)
        result = orchestrator.process_instruction(instruction, auto_execute=True)
        
        print(f"\n결과: {result.get('status', 'unknown')}")
    
    # PM 의사결정 체크
    print(f"\n{'='*50}")
    print("🤔 PM 의사결정 체크")
    decision = PMDecisionRules.should_stop_work()
    print(f"결정: {decision['decision']}")
    if decision['decision'] == 'STOP':
        print(f"메시지: {decision['message']}")
        print(f"다음 옵션: {decision['next_options']}")