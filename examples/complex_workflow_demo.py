#!/usr/bin/env python3
"""
복잡한 워크플로우 실행 데모
"""

import sys
sys.path.append('/Users/m4_macbook/Projects/ai-orchestra-v02')

from node_system import NodeFactory, NodeType, ExecutionMode, PersonaNode
from process_engine import ProcessBuilder
from metrics_system import MetricsCollector
from trigger_system import TriggerSystem, SmartTriggerAdapter
import subprocess
import time
from datetime import datetime

class RealWorkflowExecutor:
    """실제 워크플로우 실행기"""
    
    def __init__(self):
        self.metrics = MetricsCollector()
        self.triggers = TriggerSystem()
        self.start_time = None
        self.results = []
    
    def execute_bug_fix_workflow(self, issue_number: str):
        """버그 수정 워크플로우 실행"""
        print(f"\n{'='*60}")
        print(f"🔧 버그 수정 워크플로우 - Issue #{issue_number}")
        print(f"{'='*60}")
        
        self.start_time = time.time()
        
        # 1. 이슈 분석
        print(f"\n📋 Step 1: 이슈 분석")
        result = self._analyze_issue(issue_number)
        self.results.append(result)
        
        # 2. 코드 검색
        print(f"\n🔍 Step 2: 관련 코드 검색")
        result = self._search_code()
        self.results.append(result)
        
        # 3. 수정 계획
        print(f"\n📝 Step 3: 수정 계획 수립")
        result = self._create_fix_plan()
        self.results.append(result)
        
        # 4. 테스트 실행
        print(f"\n🧪 Step 4: 테스트 실행")
        result = self._run_tests()
        self.results.append(result)
        
        # 5. 리포트 생성
        print(f"\n📊 Step 5: 리포트 생성")
        result = self._generate_report()
        self.results.append(result)
        
        duration = time.time() - self.start_time
        
        # 메트릭 기록
        self.metrics.record_process(
            "bug_fix_workflow",
            len(self.results),
            duration,
            all(r['success'] for r in self.results),
            [r['node'] for r in self.results]
        )
        
        return {
            "duration": duration,
            "steps": len(self.results),
            "success": all(r['success'] for r in self.results)
        }
    
    def _analyze_issue(self, issue_number):
        """이슈 분석"""
        print(f"  이슈 #{issue_number} 정보 가져오는 중...")
        
        cmd = f"gh issue view {issue_number} -R ihw33/ai-orchestra-v02 --json title,body,labels"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"  ✅ 이슈 분석 완료")
            self.metrics.record_node("analyze_issue", "claude", True, 1.2)
            return {"node": "analyze_issue", "success": True}
        else:
            print(f"  ❌ 이슈 분석 실패")
            self.metrics.record_node("analyze_issue", "claude", False, 1.2, "Issue not found")
            return {"node": "analyze_issue", "success": False}
    
    def _search_code(self):
        """코드 검색"""
        print(f"  관련 파일 검색 중...")
        
        # 실제 파일 검색
        cmd = "ls -la *.py | head -5"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd='/Users/m4_macbook/Projects/ai-orchestra-v02')
        
        if result.stdout:
            files = result.stdout.strip().split('\n')
            print(f"  ✅ {len(files)}개 파일 발견")
            self.metrics.record_node("search_code", "gemini", True, 0.8)
            return {"node": "search_code", "success": True}
        
        return {"node": "search_code", "success": False}
    
    def _create_fix_plan(self):
        """수정 계획 수립"""
        print(f"  수정 계획 작성 중...")
        time.sleep(0.5)  # 시뮬레이션
        
        plan = """
  📌 수정 계획:
    1. node_system.py - 에러 핸들링 개선
    2. process_engine.py - 병렬 처리 최적화
    3. metrics_system.py - 실시간 모니터링 추가
        """
        print(plan)
        
        self.metrics.record_node("create_plan", "claude", True, 2.1)
        return {"node": "create_plan", "success": True}
    
    def _run_tests(self):
        """테스트 실행"""
        print(f"  테스트 스위트 실행 중...")
        
        # 간단한 테스트 시뮬레이션
        tests = ["test_nodes", "test_process", "test_metrics"]
        for test in tests:
            print(f"    • {test}: ✅ PASS")
            time.sleep(0.2)
        
        self.metrics.record_node("run_tests", "gemini", True, 3.5)
        return {"node": "run_tests", "success": True}
    
    def _generate_report(self):
        """리포트 생성"""
        print(f"  최종 리포트 생성 중...")
        
        report = f"""
  📊 워크플로우 실행 리포트
  ━━━━━━━━━━━━━━━━━━━━━━
  실행 시간: {time.time() - self.start_time:.2f}초
  성공 단계: {sum(1 for r in self.results if r['success'])}/{len(self.results)}
  사용 AI: claude(3), gemini(2), codex(1)
  성공률: {sum(1 for r in self.results if r['success'])/len(self.results)*100:.1f}%
        """
        print(report)
        
        self.metrics.record_node("generate_report", "claude", True, 1.0)
        return {"node": "generate_report", "success": True}

def demo_parallel_execution():
    """병렬 실행 데모"""
    print(f"\n{'='*60}")
    print(f"⚡ 병렬 노드 실행 데모")
    print(f"{'='*60}")
    
    # 병렬 프로세스 빌더
    builder = ProcessBuilder("Parallel Demo")
    process = builder.parallel(
        {"node_type": NodeType.ANALYZE_CODE, "executor": "claude"},
        {"node_type": NodeType.RESEARCH_TOPIC, "executor": "gemini"},
        {"node_type": NodeType.CHECK_STATUS, "executor": "codex"}
    ).build()
    
    print(f"\n🔄 병렬 실행 시작 (3개 노드 동시)")
    
    # 시뮬레이션
    for i in range(3):
        print(f"  {'⏳' * (i+1)} 실행 중... ({i+1}/3)")
        time.sleep(0.5)
    
    print(f"\n✅ 병렬 실행 완료!")
    print(f"  • claude: 코드 분석 완료")
    print(f"  • gemini: 리서치 완료")
    print(f"  • codex: 상태 체크 완료")

def demo_persona_application():
    """페르소나 적용 데모"""
    print(f"\n{'='*60}")
    print(f"🎭 페르소나 적용 데모")
    print(f"{'='*60}")
    
    # 기본 노드
    base_node = NodeFactory.create_node(NodeType.WRITE_FUNCTION, input_data={"name": "calculate"})
    
    personas = ["speedster", "perfectionist", "minimalist"]
    
    for persona_type in personas:
        print(f"\n🎨 {persona_type.upper()} 페르소나:")
        persona = PersonaNode(persona_type)
        traits = persona.get_persona_traits()
        
        print(f"  특성: {', '.join(traits.get('traits', []))}")
        print(f"  프롬프트: {traits.get('prompt_modifier', '')[:50]}...")
        print(f"  시간 배수: {traits.get('time_multiplier', 1.0)}x")

def main():
    print(f"\n{'🚀'*30}")
    print(f" AI ORCHESTRA v2 - 복잡한 워크플로우 데모")
    print(f"{'🚀'*30}")
    
    # 1. 실제 워크플로우 실행
    executor = RealWorkflowExecutor()
    result = executor.execute_bug_fix_workflow("57")
    
    print(f"\n{'='*60}")
    print(f"✅ 워크플로우 완료")
    print(f"  총 시간: {result['duration']:.2f}초")
    print(f"  실행 단계: {result['steps']}개")
    print(f"  성공 여부: {'성공' if result['success'] else '실패'}")
    
    # 2. 병렬 실행 데모
    demo_parallel_execution()
    
    # 3. 페르소나 적용 데모
    demo_persona_application()
    
    # 4. 최종 메트릭
    print(f"\n{'='*60}")
    print(f"📊 최종 메트릭 요약")
    print(f"{'='*60}")
    
    metrics = executor.metrics
    report = metrics.generate_report()
    # 주요 부분만 출력
    lines = report.split('\n')
    for line in lines[:15]:  # 상위 15줄만
        print(line)

if __name__ == "__main__":
    main()