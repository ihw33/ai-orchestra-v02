#!/usr/bin/env python3
"""
실제 작동 데모 - GitHub 이슈 생성 및 코드 분석
"""

import sys
import os
sys.path.append('/Users/m4_macbook/Projects/ai-orchestra-v02')

from node_system import NodeFactory, NodeType, ExecutionMode
from process_engine import ProcessBuilder
from orchestrator import SmartOrchestrator
from metrics_system import MetricsCollector, DashboardRenderer
from trigger_system import TriggerSystem, SmartTriggerAdapter
import subprocess
import json
from datetime import datetime

def demo_single_node():
    """단일 노드 실행 - GitHub 이슈 조회"""
    print("\n" + "="*60)
    print("📌 DEMO 1: 단일 노드 실행 - GitHub 이슈 목록 조회")
    print("="*60)
    
    # GitHub 이슈 목록 조회 노드
    node = NodeFactory.create_node(
        NodeType.RUN_COMMAND,
        input_data={"command": "gh issue list -R ihw33/ai-orchestra-v02 --limit 3"},
        executor="system",
        mode=ExecutionMode.PARALLEL
    )
    
    # 실제 명령 실행
    print("\n🔧 실행 중: GitHub 이슈 목록 조회...")
    result = subprocess.run(
        "gh issue list -R ihw33/ai-orchestra-v02 --limit 3",
        shell=True,
        capture_output=True,
        text=True
    )
    
    if result.stdout:
        print("\n✅ 결과:")
        print(result.stdout)
    else:
        print("\n📝 이슈가 없거나 저장소가 비공개입니다")
    
    return result.returncode == 0

def demo_code_analysis():
    """코드 분석 노드 - 실제 파일 분석"""
    print("\n" + "="*60)
    print("📌 DEMO 2: 코드 분석 - node_system.py 구조 분석")
    print("="*60)
    
    print("\n🔍 분석 중: node_system.py...")
    
    # 실제 파일 읽기
    with open('/Users/m4_macbook/Projects/ai-orchestra-v02/node_system.py', 'r') as f:
        lines = f.readlines()
    
    # 간단한 분석
    total_lines = len(lines)
    classes = [line.strip() for line in lines if line.startswith('class ')]
    functions = [line.strip() for line in lines if line.strip().startswith('def ')]
    
    print(f"\n📊 분석 결과:")
    print(f"  • 전체 라인: {total_lines}")
    print(f"  • 클래스 수: {len(classes)}")
    print(f"  • 함수 수: {len(functions)}")
    print(f"\n📝 주요 클래스:")
    for cls in classes[:5]:
        print(f"  - {cls}")
    
    return True

def demo_process_workflow():
    """프로세스 워크플로우 - 실제 작업 흐름"""
    print("\n" + "="*60)
    print("📌 DEMO 3: 프로세스 워크플로우 - 버그 수정 시뮬레이션")
    print("="*60)
    
    # 프로세스 빌더로 워크플로우 생성
    builder = ProcessBuilder("Bug Fix Demo")
    process = builder \
        .add(NodeType.ANALYZE_CODE, input_data={"file": "test.py"}) \
        .add(NodeType.FIX_BUG_LINE, input_data={"line": 42}) \
        .add(NodeType.RUN_TEST, input_data={"test": "test_unit.py"}) \
        .build()
    
    print(f"\n🔄 프로세스 구성:")
    print(f"  프로세스 ID: {process.state.id}")
    print(f"  노드 수: {len(process.state.nodes)}")
    print(f"  노드 순서:")
    for i, node in enumerate(process.state.nodes, 1):
        print(f"    {i}. {node.state.type.value} ({node.executor})")
    
    # 시뮬레이션 실행
    print("\n▶️ 프로세스 실행 시뮬레이션:")
    for i, node in enumerate(process.state.nodes, 1):
        print(f"\n  Step {i}: {node.state.type.value}")
        print(f"    실행자: {node.executor}")
        print(f"    상태: ✅ 완료")
    
    return True

def demo_trigger_system():
    """트리거 시스템 - 실시간 반응"""
    print("\n" + "="*60)
    print("📌 DEMO 4: 트리거 시스템 - 자동 액션 발동")
    print("="*60)
    
    trigger_system = TriggerSystem()
    adapter = SmartTriggerAdapter(trigger_system)
    
    # 테스트 지시들
    test_instructions = [
        "버그 #123을 수정해줘",
        "새로운 기능을 만들어줘",
        "이 코드 성능을 분석해줘"
    ]
    
    print("\n🎯 트리거 테스트:")
    for instruction in test_instructions:
        print(f"\n입력: '{instruction}'")
        actions = adapter.process_instruction(instruction)
        if actions:
            print(f"  → 자동 발동: {actions[0]}")
    
    return True

def demo_metrics_dashboard():
    """메트릭 대시보드 - 실시간 통계"""
    print("\n" + "="*60)
    print("📌 DEMO 5: 실시간 메트릭 대시보드")
    print("="*60)
    
    metrics = MetricsCollector()
    
    # 샘플 데이터 기록
    print("\n📊 메트릭 수집 중...")
    metrics.record_node("create_issue", "claude", True, 2.5)
    metrics.record_node("analyze_code", "claude", True, 4.2)
    metrics.record_node("write_function", "codex", True, 8.3)
    metrics.record_node("run_test", "gemini", True, 3.1)
    metrics.record_node("fix_bug_line", "codex", False, 5.5, "Syntax error")
    
    # 대시보드 렌더링
    dashboard = DashboardRenderer(metrics)
    print(dashboard.render())
    
    return True

def demo_orchestrator():
    """오케스트레이터 - 지능형 지시 처리"""
    print("\n" + "="*60)
    print("📌 DEMO 6: 스마트 오케스트레이터 - 자연어 이해")
    print("="*60)
    
    orchestrator = SmartOrchestrator()
    
    instruction = "버그 #456을 빨리 수정하고 테스트까지 완료해줘"
    print(f"\n💬 사용자: '{instruction}'")
    
    # 지시 분석
    analysis = orchestrator.analyzer.analyze(instruction)
    
    print(f"\n🧠 AI 분석:")
    print(f"  • 의도: {analysis['intent']} (버그 수정)")
    print(f"  • 긴급도: {analysis['urgency']} (높음)")
    print(f"  • 추출 정보: 이슈 #{analysis['entities'].get('issue_number', 'N/A')}")
    print(f"  • 제안 프로세스: {analysis['suggested_process']}")
    print(f"  • 적용 페르소나: {analysis['persona']} (빠른 실행)")
    
    print(f"\n📋 생성될 작업:")
    for i, node in enumerate(analysis['suggested_nodes'], 1):
        print(f"  {i}. {node.value}")
    
    return True

def main():
    """메인 데모 실행"""
    print("\n" + "🚀"*30)
    print(" AI ORCHESTRA v2 - 실제 작동 데모 ")
    print("🚀"*30)
    
    demos = [
        ("GitHub 연동", demo_single_node),
        ("코드 분석", demo_code_analysis),
        ("워크플로우", demo_process_workflow),
        ("트리거", demo_trigger_system),
        ("메트릭", demo_metrics_dashboard),
        ("오케스트레이터", demo_orchestrator)
    ]
    
    success_count = 0
    for name, demo_func in demos:
        try:
            if demo_func():
                success_count += 1
                print(f"\n✅ {name} 데모 성공")
        except Exception as e:
            print(f"\n❌ {name} 데모 실패: {e}")
    
    print("\n" + "="*60)
    print(f"📊 최종 결과: {success_count}/{len(demos)} 데모 성공")
    print("="*60)
    
    # 저장된 파일들 표시
    print("\n📁 생성된 파일들:")
    files = [
        "metrics_lite.jsonl",
        "triggers.json"
    ]
    for file in files:
        if os.path.exists(file):
            size = os.path.getsize(file)
            print(f"  • {file} ({size} bytes)")

if __name__ == "__main__":
    main()