#!/usr/bin/env python3
"""
AI Orchestra 팀원별 KPI 추적 시스템
각 AI의 성과를 실시간으로 모니터링
"""
import json
import subprocess
from datetime import datetime, timedelta
from typing import Dict, List

class TeamKPITracker:
    def __init__(self):
        self.kpi_data = {
            "Gemini": {
                "role": "Frontend/UI Lead",
                "kpis": {
                    "response_time": [],  # 응답 시간
                    "task_completion": 0,  # 완료한 작업 수
                    "error_rate": 0,      # 에러율
                    "quality_score": 0,   # 품질 점수
                    "availability": 100   # 가용성 %
                }
            },
            "Codex": {
                "role": "Backend Engineer",
                "kpis": {
                    "response_time": [],
                    "task_completion": 0,
                    "error_rate": 0,
                    "code_quality": 0,    # 코드 품질
                    "availability": 100
                }
            },
            "Claude": {
                "role": "PM & QA",
                "kpis": {
                    "response_time": [],
                    "task_completion": 0,
                    "review_count": 0,    # 리뷰 수
                    "issue_detection": 0, # 발견한 이슈
                    "availability": 100
                }
            },
            "Cursor": {
                "role": "Architect",
                "kpis": {
                    "response_time": [],
                    "task_completion": 0,
                    "design_quality": 0,  # 설계 품질
                    "documentation": 0,   # 문서화
                    "availability": 100
                }
            }
        }
        self.start_time = datetime.now()
        
    def measure_response_time(self, ai_name: str, question: str) -> float:
        """AI 응답 시간 측정"""
        start = datetime.now()
        
        try:
            if ai_name == "Gemini":
                cmd = f"echo '{question}' | gemini 2>/dev/null | head -1"
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
            elif ai_name == "Codex":
                cmd = f"echo '{question}' | codex exec 2>&1 | grep -A 2 '] codex' | tail -1"
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=15)
            elif ai_name == "Claude":
                result = subprocess.run(["claude", "--version"], capture_output=True, text=True, timeout=5)
            else:
                return -1
                
            response_time = (datetime.now() - start).total_seconds()
            
            # KPI 업데이트
            if ai_name in self.kpi_data:
                self.kpi_data[ai_name]["kpis"]["response_time"].append(response_time)
                # 최근 10개만 유지
                if len(self.kpi_data[ai_name]["kpis"]["response_time"]) > 10:
                    self.kpi_data[ai_name]["kpis"]["response_time"].pop(0)
                    
            return response_time
            
        except subprocess.TimeoutExpired:
            # 타임아웃은 가용성 감소
            if ai_name in self.kpi_data:
                self.kpi_data[ai_name]["kpis"]["availability"] -= 5
            return -1
        except Exception as e:
            # 에러는 에러율 증가
            if ai_name in self.kpi_data:
                self.kpi_data[ai_name]["kpis"]["error_rate"] += 1
            return -1
    
    def update_task_completion(self, ai_name: str, completed: bool = True):
        """작업 완료 업데이트"""
        if ai_name in self.kpi_data and completed:
            self.kpi_data[ai_name]["kpis"]["task_completion"] += 1
    
    def calculate_performance_score(self, ai_name: str) -> float:
        """종합 성과 점수 계산 (100점 만점)"""
        if ai_name not in self.kpi_data:
            return 0
            
        kpis = self.kpi_data[ai_name]["kpis"]
        score = 0
        
        # 1. 가용성 (30점)
        score += kpis["availability"] * 0.3
        
        # 2. 응답 시간 (20점) - 평균 3초 이하면 만점
        if kpis["response_time"]:
            avg_response = sum(kpis["response_time"]) / len(kpis["response_time"])
            response_score = max(0, 20 - (avg_response - 3) * 4)
            score += response_score
        else:
            score += 10  # 데이터 없으면 기본 점수
            
        # 3. 작업 완료 (30점) - 10개 완료시 만점
        completion_score = min(30, kpis["task_completion"] * 3)
        score += completion_score
        
        # 4. 에러율 (20점) - 에러 없으면 만점
        error_rate = kpis.get("error_rate", 0)
        error_score = max(0, 20 - error_rate * 5)
        score += error_score
        
        return round(score, 1)
    
    def generate_kpi_report(self) -> Dict:
        """KPI 리포트 생성"""
        report = {
            "timestamp": datetime.now().isoformat(),
            "uptime_minutes": (datetime.now() - self.start_time).seconds // 60,
            "team_performance": {}
        }
        
        for ai_name, data in self.kpi_data.items():
            avg_response = 0
            if data["kpis"]["response_time"]:
                avg_response = sum(data["kpis"]["response_time"]) / len(data["kpis"]["response_time"])
                
            report["team_performance"][ai_name] = {
                "role": data["role"],
                "performance_score": self.calculate_performance_score(ai_name),
                "metrics": {
                    "avg_response_time": round(avg_response, 2),
                    "tasks_completed": data["kpis"]["task_completion"],
                    "error_count": data["kpis"].get("error_rate", 0),
                    "availability": f"{data['kpis']['availability']}%"
                }
            }
        
        # 팀 평균 점수
        scores = [self.calculate_performance_score(ai) for ai in self.kpi_data.keys()]
        report["team_average_score"] = round(sum(scores) / len(scores), 1)
        
        return report
    
    def print_kpi_dashboard(self):
        """KPI 대시보드 출력"""
        print("\n" + "="*60)
        print("📊 AI Orchestra Team KPI Dashboard")
        print("="*60)
        
        report = self.generate_kpi_report()
        
        # 팀 전체 성과
        print(f"\n🎯 팀 평균 성과: {report['team_average_score']}/100")
        print(f"⏱️ 운영 시간: {report['uptime_minutes']}분")
        
        # 개별 AI 성과
        print("\n📈 팀원별 KPI:")
        print("-"*60)
        
        for ai_name, perf in report["team_performance"].items():
            score = perf["performance_score"]
            
            # 성과에 따른 이모지
            if score >= 80:
                emoji = "🌟"
            elif score >= 60:
                emoji = "✅"
            elif score >= 40:
                emoji = "⚠️"
            else:
                emoji = "❌"
                
            print(f"\n{emoji} {ai_name} ({perf['role']})")
            print(f"  성과 점수: {score}/100")
            print(f"  평균 응답: {perf['metrics']['avg_response_time']}초")
            print(f"  완료 작업: {perf['metrics']['tasks_completed']}개")
            print(f"  에러 횟수: {perf['metrics']['error_count']}회")
            print(f"  가용성: {perf['metrics']['availability']}")
        
        # 개선 제안
        print("\n💡 개선 제안:")
        for ai_name, perf in report["team_performance"].items():
            score = perf["performance_score"]
            if score < 60:
                print(f"  • {ai_name}: 성과 개선 필요 (현재 {score}점)")
            if perf["metrics"]["avg_response_time"] > 5:
                print(f"  • {ai_name}: 응답 시간 개선 필요 ({perf['metrics']['avg_response_time']}초)")
            if perf["metrics"]["error_count"] > 3:
                print(f"  • {ai_name}: 에러율 높음 ({perf['metrics']['error_count']}회)")
    
    def save_kpi_report(self, filename="team_kpi_report.json"):
        """KPI 리포트 저장"""
        report = self.generate_kpi_report()
        with open(filename, "w") as f:
            json.dump(report, f, indent=2)
        return filename

def main():
    """메인 실행 함수"""
    print("🚀 Team KPI Tracker 시작...")
    
    tracker = TeamKPITracker()
    
    # 테스트 측정
    test_questions = [
        ("Gemini", "What is 1+1?"),
        ("Codex", "What is 2+2?"),
        ("Claude", "version check"),
        ("Gemini", "Hello?"),
    ]
    
    print("\n⏱️ 응답 시간 측정 중...")
    for ai_name, question in test_questions:
        response_time = tracker.measure_response_time(ai_name, question)
        if response_time > 0:
            print(f"  {ai_name}: {response_time:.2f}초")
            tracker.update_task_completion(ai_name, True)
        else:
            print(f"  {ai_name}: 응답 실패")
    
    # KPI 대시보드 표시
    tracker.print_kpi_dashboard()
    
    # 리포트 저장
    report_file = tracker.save_kpi_report()
    print(f"\n💾 KPI 리포트 저장됨: {report_file}")

if __name__ == "__main__":
    main()