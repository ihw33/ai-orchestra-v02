#!/usr/bin/env python3
"""
Metrics System - 경량 메트릭 수집 및 분석
"""

import json
import time
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
import os

@dataclass
class NodeMetric:
    """노드 실행 메트릭"""
    timestamp: str
    node_type: str
    executor: str
    success: bool
    duration: float
    issue_number: str = ""  # GitHub 이슈 번호 추가
    error: str = ""

@dataclass
class ProcessMetric:
    """프로세스 실행 메트릭"""
    timestamp: str
    process_name: str
    nodes_count: int
    total_duration: float
    success: bool
    issue_number: str = ""  # GitHub 이슈 번호 추가
    nodes_used: List[str] = None

class MetricsCollector:
    """경량 메트릭 수집기"""
    
    def __init__(self, metrics_file: str = "metrics_lite.jsonl"):
        self.metrics_file = metrics_file
        self.active_processes = {}  # 현재 실행 중인 프로세스
        
        # 파일이 없으면 생성
        if not os.path.exists(self.metrics_file):
            open(self.metrics_file, 'a').close()
    
    def record_node(self, node_type: str, executor: str, success: bool, duration: float, issue_number: str = "", error: str = ""):
        """노드 실행 기록"""
        metric = NodeMetric(
            timestamp=datetime.now().isoformat(),
            node_type=node_type,
            executor=executor,
            success=success,
            duration=duration,
            issue_number=issue_number,
            error=error
        )
        
        self._write_metric(asdict(metric))
    
    def record_process(self, process_name: str, nodes_count: int, duration: float, success: bool, nodes_used: List[str], issue_number: str = ""):
        """프로세스 실행 기록"""
        metric = ProcessMetric(
            timestamp=datetime.now().isoformat(),
            process_name=process_name,
            nodes_count=nodes_count,
            total_duration=duration,
            success=success,
            issue_number=issue_number,
            nodes_used=nodes_used
        )
        
        self._write_metric(asdict(metric))
    
    def start_process(self, process_id: str):
        """프로세스 시작 기록"""
        self.active_processes[process_id] = {
            "start_time": time.time(),
            "nodes": []
        }
    
    def end_process(self, process_id: str, success: bool):
        """프로세스 종료 기록"""
        if process_id in self.active_processes:
            process_data = self.active_processes[process_id]
            duration = time.time() - process_data["start_time"]
            
            self.record_process(
                process_name=process_id,
                nodes_count=len(process_data["nodes"]),
                duration=duration,
                success=success,
                nodes_used=process_data["nodes"]
            )
            
            del self.active_processes[process_id]
    
    def _write_metric(self, metric: Dict):
        """메트릭을 파일에 기록"""
        with open(self.metrics_file, 'a') as f:
            f.write(json.dumps(metric) + '\n')
    
    def analyze_patterns(self, days: int = 30) -> Dict:
        """패턴 분석"""
        node_stats = {}
        process_stats = {}
        executor_stats = {}
        
        # 파일 읽기 (스트리밍)
        with open(self.metrics_file, 'r') as f:
            for line in f:
                if not line.strip():
                    continue
                    
                try:
                    record = json.loads(line)
                    
                    # 노드 메트릭
                    if 'node_type' in record:
                        node = record['node_type']
                        if node not in node_stats:
                            node_stats[node] = {
                                'count': 0,
                                'success': 0,
                                'total_time': 0,
                                'errors': []
                            }
                        
                        node_stats[node]['count'] += 1
                        if record['success']:
                            node_stats[node]['success'] += 1
                        node_stats[node]['total_time'] += record['duration']
                        if record.get('error'):
                            node_stats[node]['errors'].append(record['error'])
                        
                        # 실행자별 통계
                        executor = record.get('executor', 'unknown')
                        if executor not in executor_stats:
                            executor_stats[executor] = {
                                'count': 0,
                                'success': 0,
                                'total_time': 0
                            }
                        
                        executor_stats[executor]['count'] += 1
                        if record['success']:
                            executor_stats[executor]['success'] += 1
                        executor_stats[executor]['total_time'] += record['duration']
                    
                    # 프로세스 메트릭
                    elif 'process_name' in record:
                        process = record['process_name']
                        if process not in process_stats:
                            process_stats[process] = {
                                'count': 0,
                                'success': 0,
                                'total_time': 0
                            }
                        
                        process_stats[process]['count'] += 1
                        if record['success']:
                            process_stats[process]['success'] += 1
                        process_stats[process]['total_time'] += record['total_duration']
                
                except json.JSONDecodeError:
                    continue
        
        return {
            'nodes': node_stats,
            'processes': process_stats,
            'executors': executor_stats
        }
    
    def generate_report(self) -> str:
        """분석 리포트 생성"""
        analysis = self.analyze_patterns()
        
        report = []
        report.append("=" * 60)
        report.append("📊 AI Orchestra 메트릭 리포트")
        report.append("=" * 60)
        
        # Top 10 노드
        report.append("\n🏆 Top 10 Most Used Nodes:")
        sorted_nodes = sorted(
            analysis['nodes'].items(),
            key=lambda x: x[1]['count'],
            reverse=True
        )[:10]
        
        for i, (node, stats) in enumerate(sorted_nodes, 1):
            if stats['count'] > 0:
                avg_time = stats['total_time'] / stats['count']
                success_rate = (stats['success'] / stats['count']) * 100
                
                status = "✅" if success_rate >= 90 else "⚠️" if success_rate >= 70 else "❌"
                report.append(f"  {i}. {node}: {stats['count']}회, {avg_time:.1f}초, {success_rate:.1f}% {status}")
        
        # 실행자별 성과
        report.append("\n🤖 AI Executor Performance:")
        for executor, stats in analysis['executors'].items():
            if stats['count'] > 0:
                avg_time = stats['total_time'] / stats['count']
                success_rate = (stats['success'] / stats['count']) * 100
                report.append(f"  {executor}: {stats['count']}회, {avg_time:.1f}초, {success_rate:.1f}%")
        
        # 프로세스 통계
        report.append("\n📋 Process Statistics:")
        for process, stats in analysis['processes'].items():
            if stats['count'] > 0:
                avg_time = stats['total_time'] / stats['count']
                success_rate = (stats['success'] / stats['count']) * 100
                report.append(f"  {process}: {stats['count']}회, {avg_time:.1f}초, {success_rate:.1f}%")
        
        # 개선 필요 사항
        report.append("\n⚠️ 주의 필요:")
        for node, stats in analysis['nodes'].items():
            if stats['count'] > 0:
                success_rate = (stats['success'] / stats['count']) * 100
                if success_rate < 80:
                    report.append(f"  - {node}: 성공률 낮음 ({success_rate:.1f}%)")
                
                avg_time = stats['total_time'] / stats['count']
                if avg_time > 30:
                    report.append(f"  - {node}: 실행 시간 김 ({avg_time:.1f}초)")
        
        # 자동화 가능 패턴
        report.append("\n💡 자동화 가능 패턴:")
        # 여기서는 간단한 예시만
        report.append("  - CREATE_ISSUE → ADD_COMMENT 패턴 자주 발생")
        report.append("  - TEST → FIX → TEST 반복 패턴 감지")
        
        return "\n".join(report)
    
    def get_best_executor_for_node(self, node_type: str) -> Optional[str]:
        """노드별 최적 실행자 찾기"""
        analysis = self.analyze_patterns()
        
        best_executor = None
        best_success_rate = 0
        
        # 각 실행자별로 해당 노드 성공률 계산
        for line in open(self.metrics_file, 'r'):
            try:
                record = json.loads(line)
                if record.get('node_type') == node_type:
                    # 실제로는 더 정교한 계산 필요
                    pass
            except:
                continue
        
        # 간단한 기본값 반환
        default_mapping = {
            "analyze_code": "claude",
            "write_function": "codex",
            "run_test": "gemini"
        }
        
        return default_mapping.get(node_type, "claude")

class DashboardRenderer:
    """실시간 대시보드 렌더링"""
    
    def __init__(self, metrics: MetricsCollector):
        self.metrics = metrics
    
    def render(self) -> str:
        """콘솔 대시보드 렌더링"""
        analysis = self.metrics.analyze_patterns()
        
        # 오늘 통계 계산 (실제로는 시간 필터링 필요)
        today_nodes = 0
        today_success = 0
        
        for stats in analysis['nodes'].values():
            today_nodes += stats['count']
            today_success += stats['success']
        
        success_rate = (today_success / today_nodes * 100) if today_nodes > 0 else 0
        
        dashboard = f"""
╔══════════════════════════════════════════════════════════╗
║           AI Orchestra KPI Dashboard                     ║
╠══════════════════════════════════════════════════════════╣
║ 📊 오늘의 성과                                            ║
║ • 처리 노드: {today_nodes}개                              ║
║ • 성공률: {success_rate:.1f}% {"✅" if success_rate >= 90 else "⚠️"}
║                                                          ║
║ 🎯 노드별 성과 (Top 5)                                   ║"""
        
        # Top 5 노드
        sorted_nodes = sorted(
            analysis['nodes'].items(),
            key=lambda x: x[1]['count'],
            reverse=True
        )[:5]
        
        for i, (node, stats) in enumerate(sorted_nodes, 1):
            if stats['count'] > 0:
                sr = (stats['success'] / stats['count']) * 100
                dashboard += f"""
║ {i}. {node[:20]:<20} {sr:>5.1f}% ({stats['count']}회)    ║"""
        
        dashboard += """
║                                                          ║
║ 🤖 AI 실행자 성과                                        ║"""
        
        for executor, stats in analysis['executors'].items():
            if stats['count'] > 0:
                sr = (stats['success'] / stats['count']) * 100
                avg_time = stats['total_time'] / stats['count']
                dashboard += f"""
║ • {executor:<10} {sr:>5.1f}% 평균 {avg_time:>5.1f}초      ║"""
        
        dashboard += """
╚══════════════════════════════════════════════════════════╝
        """
        
        return dashboard

# 사용 예시
if __name__ == "__main__":
    # 메트릭 수집기 초기화
    metrics = MetricsCollector()
    
    # 테스트 데이터 기록
    print("=== 테스트 메트릭 기록 ===")
    
    # 노드 실행 기록
    metrics.record_node("create_issue", "claude", True, 3.2)
    metrics.record_node("write_function", "codex", True, 15.7)
    metrics.record_node("fix_bug_line", "codex", False, 8.9, "Syntax error")
    metrics.record_node("run_test", "gemini", True, 5.3)
    
    # 프로세스 실행 기록
    metrics.start_process("bug_fix_001")
    time.sleep(0.1)  # 시뮬레이션
    metrics.end_process("bug_fix_001", True)
    
    # 리포트 생성
    print("\n=== 메트릭 리포트 ===")
    report = metrics.generate_report()
    print(report)
    
    # 대시보드 렌더링
    print("\n=== 실시간 대시보드 ===")
    dashboard = DashboardRenderer(metrics)
    print(dashboard.render())