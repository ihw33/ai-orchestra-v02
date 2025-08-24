#!/usr/bin/env python3
"""
🧠 Intelligence Banner - 시스템 성장 지표 표시
시스템이 얼마나 똑똑해지고 있는지 실시간 추적
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict

class IntelligenceBanner:
    """시스템 지능 지표 관리"""
    
    def __init__(self):
        self.base_dir = Path(__file__).parent
        self.stats_file = self.base_dir / "system_intelligence.json"
        self.stats = self.load_stats()
        
    def load_stats(self) -> Dict:
        """통계 로드"""
        if self.stats_file.exists():
            with open(self.stats_file, 'r') as f:
                return json.load(f)
        
        # 초기 상태
        return {
            "iq_level": 5,
            "modules": 10,
            "workflows": 4,
            "patterns_learned": 0,
            "automation_rate": 30,
            "avg_processing_time": 120,  # 초
            "total_tasks_completed": 0,
            "memory_usage": 5,  # %
            "created_at": datetime.now().isoformat(),
            "last_updated": datetime.now().isoformat()
        }
    
    def save_stats(self):
        """통계 저장"""
        self.stats["last_updated"] = datetime.now().isoformat()
        with open(self.stats_file, 'w') as f:
            json.dump(self.stats, f, indent=2)
    
    def update_stats(self, **kwargs):
        """통계 업데이트"""
        for key, value in kwargs.items():
            if key in self.stats:
                self.stats[key] = value
        self.save_stats()
    
    def learn_pattern(self):
        """패턴 학습 시 호출"""
        self.stats["patterns_learned"] += 1
        self.stats["iq_level"] = min(100, 5 + (self.stats["patterns_learned"] // 10))
        self.save_stats()
    
    def complete_task(self, time_taken: float):
        """작업 완료 시 호출"""
        self.stats["total_tasks_completed"] += 1
        
        # 평균 처리 시간 업데이트
        total = self.stats["total_tasks_completed"]
        avg = self.stats["avg_processing_time"]
        self.stats["avg_processing_time"] = ((avg * (total - 1)) + time_taken) / total
        
        # 자동화율 계산
        if time_taken < 10:  # 10초 이내면 자동화 성공
            self.stats["automation_rate"] = min(100, self.stats["automation_rate"] + 1)
        
        self.save_stats()
    
    def get_banner(self) -> str:
        """배너 문자열 생성"""
        iq = self.stats["iq_level"]
        modules = self.stats["modules"]
        patterns = self.stats["patterns_learned"]
        auto_rate = self.stats["automation_rate"]
        
        # IQ 레벨에 따른 이모지
        if iq < 10:
            brain = "🐣"  # 초보
        elif iq < 30:
            brain = "🧠"  # 성장 중
        elif iq < 50:
            brain = "🎓"  # 학습 중
        elif iq < 80:
            brain = "🚀"  # 고급
        else:
            brain = "🌟"  # 마스터
        
        banner = f"""╔════════════════════════════════════════════════════════════╗
║ {brain} AI Orchestra IQ: Level {iq} | 📚 {modules} 모듈 | 🧬 {patterns} 패턴  ║
║ ⚡ 자동화율: {auto_rate}% | 🎯 다음 레벨: {self.get_next_level_info()}     ║
╚════════════════════════════════════════════════════════════╝"""
        
        return banner
    
    def get_next_level_info(self) -> str:
        """다음 레벨까지 정보"""
        current_iq = self.stats["iq_level"]
        next_level = ((current_iq // 10) + 1) * 10
        patterns_needed = (next_level - 5) * 10 - self.stats["patterns_learned"]
        
        if patterns_needed > 0:
            return f"{patterns_needed} 패턴"
        else:
            return "Max Level!"
    
    def get_detailed_stats(self) -> str:
        """상세 통계"""
        created = datetime.fromisoformat(self.stats["created_at"])
        days_active = (datetime.now() - created).days
        
        return f"""
📊 System Intelligence Report
════════════════════════════════════════

🧠 Intelligence Level
  • IQ: Level {self.stats['iq_level']}/100
  • Patterns Learned: {self.stats['patterns_learned']}
  • Learning Rate: {self.stats['patterns_learned'] / max(1, days_active):.1f} patterns/day

📦 System Capacity
  • Modules: {self.stats['modules']}
  • Workflows: {self.stats['workflows']}
  • Memory Usage: {self.stats['memory_usage']}%

⚡ Performance
  • Automation Rate: {self.stats['automation_rate']}%
  • Avg Processing: {self.stats['avg_processing_time']:.1f}s
  • Tasks Completed: {self.stats['total_tasks_completed']}

📈 Growth Trajectory
  • Days Active: {days_active}
  • Daily Improvement: {(self.stats['automation_rate'] / max(1, days_active)):.1f}%
  • Projected IQ (30 days): {min(100, self.stats['iq_level'] + 30)}
"""
    
    def simulate_growth(self):
        """성장 시뮬레이션 (테스트용)"""
        import random
        
        # 랜덤 패턴 학습
        for _ in range(random.randint(1, 3)):
            self.learn_pattern()
        
        # 랜덤 작업 완료
        for _ in range(random.randint(2, 5)):
            self.complete_task(random.uniform(0.5, 30))
        
        # 모듈 추가
        if random.random() > 0.7:
            self.stats["modules"] += 1
        
        self.save_stats()
        print("📈 Growth simulated!")

def main():
    """메인 진입점"""
    import sys
    
    banner = IntelligenceBanner()
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        if command == "show":
            print(banner.get_banner())
        elif command == "stats":
            print(banner.get_detailed_stats())
        elif command == "simulate":
            banner.simulate_growth()
            print(banner.get_banner())
        elif command == "learn":
            banner.learn_pattern()
            print(f"✅ Pattern learned! IQ: {banner.stats['iq_level']}")
        else:
            print("""
Intelligence Banner

Usage:
  intelligence_banner.py show     - Show banner
  intelligence_banner.py stats    - Show detailed stats
  intelligence_banner.py simulate - Simulate growth
  intelligence_banner.py learn    - Learn a pattern
""")
    else:
        print(banner.get_banner())
        print("\nUse 'intelligence_banner.py stats' for details")

if __name__ == "__main__":
    main()