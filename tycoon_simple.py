#!/usr/bin/env python3
"""
🎮 TYCOON DASHBOARD (Simple Version)
터미널에서 바로 실행 가능한 텍스트 버전
"""

import os
import sys
import time
import random
import subprocess
import json
from datetime import datetime

class SimpleTycoon:
    def __init__(self):
        self.score = 8470
        self.day = 42
        self.budget = 15000
        self.team_morale = 85
        
        # GitHub 데이터
        self.pr_merged = 5
        self.pr_total = 8
        self.issues_closed = 12
        self.issues_total = 15
        
        # 팀원
        self.team = {
            "Emma": {"role": "CPO", "status": "PR #49 리뷰", "progress": 80},
            "Rajiv": {"role": "Eng", "status": "Coding", "progress": 100},
            "Anna": {"role": "QA", "status": "Testing", "progress": 70},
            "Yui": {"role": "UI", "status": "Design", "progress": 65},
            "Olaf": {"role": "Ops", "status": "Deploy준비", "progress": 90}
        }
        
        self.decisions = []
        self.events = []
    
    def clear_screen(self):
        """화면 지우기"""
        os.system('clear' if os.name == 'posix' else 'cls')
    
    def get_github_data(self):
        """GitHub 데이터 가져오기"""
        try:
            cmd = "gh pr list -R ihw33/ai-orchestra-v02 --state open --json number,title --limit 3 2>/dev/null"
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            if result.returncode == 0 and result.stdout:
                prs = json.loads(result.stdout)
                for pr in prs[:3]:
                    self.decisions.append({
                        "type": "PR",
                        "number": pr['number'],
                        "title": pr['title'][:30]
                    })
        except:
            # 실패시 샘플 데이터
            self.decisions = [
                {"type": "PR", "number": 49, "title": "Dashboard Feature"},
                {"type": "Issue", "number": 47, "title": "Bug Fix Required"}
            ]
    
    def display(self):
        """대시보드 표시"""
        self.clear_screen()
        
        print("╔══════════════════════════════════════════════════════════╗")
        print(f"║  🎮 TYCOON DASHBOARD │ Day {self.day} │ 💰 ${self.budget:,} │ ⭐ {self.score:,}  ║")
        print("╠══════════════════════════════════════════════════════════╣")
        
        # 스프린트 상태
        print("║ 📊 Today's Sprint Match                                  ║")
        pr_pct = int(self.pr_merged / self.pr_total * 100) if self.pr_total else 0
        print(f"║   • PR Merged: {self.pr_merged}/{self.pr_total} ({pr_pct}%)                               ║")
        issue_pct = int(self.issues_closed / self.issues_total * 100) if self.issues_total else 0
        print(f"║   • Issues: {self.issues_closed}/{self.issues_total} ({issue_pct}%)                                  ║")
        morale_bar = "😊" * (self.team_morale // 20)
        print(f"║   • Morale: {morale_bar} ({self.team_morale}%)                         ║")
        
        print("╠══════════════════════════════════════════════════════════╣")
        
        # 팀 상태
        print("║ 👥 Team Status                                           ║")
        for name, info in self.team.items():
            bar = "█" * (info['progress'] // 10) + "░" * (10 - info['progress'] // 10)
            print(f"║   {name:6} [{bar}] {info['progress']:3}% - {info['status']:15}    ║")
        
        print("╠══════════════════════════════════════════════════════════╣")
        
        # 결정사항
        print("║ 🎯 Decisions Required                                    ║")
        for i, decision in enumerate(self.decisions[:3], 1):
            print(f"║   [{i}] {decision['type']} #{decision['number']}: {decision['title']:25} ║")
        
        print("╠══════════════════════════════════════════════════════════╣")
        print("║ Commands:                                                ║")
        print("║   [1-3] Approve decision  [A] Approve all               ║")
        print("║   [T] Simulate time       [U] Update GitHub             ║")
        print("║   [S] Show stats          [Q] Quit                      ║")
        print("╚══════════════════════════════════════════════════════════╝")
        
        if self.events:
            print("\n📰 Latest Event:", self.events[-1])
    
    def handle_decision(self, num):
        """결정 처리"""
        if 0 < num <= len(self.decisions):
            decision = self.decisions[num-1]
            self.score += 50
            self.budget -= random.randint(100, 500)
            self.team_morale = min(100, self.team_morale + 5)
            
            # 팀원 진행률 업데이트
            member = random.choice(list(self.team.keys()))
            self.team[member]['progress'] = min(100, self.team[member]['progress'] + 10)
            
            self.events.append(f"✅ Approved {decision['type']} #{decision['number']}")
            self.decisions.pop(num-1)
            
            # 새 결정사항 추가
            if len(self.decisions) < 3:
                self.decisions.append({
                    "type": random.choice(["PR", "Issue", "Budget"]),
                    "number": random.randint(50, 100),
                    "title": random.choice(["New Feature", "Bug Fix", "Refactor", "Testing"])
                })
            
            return True
        return False
    
    def simulate_time(self):
        """시간 경과"""
        self.day += 1
        self.budget += random.randint(-500, 1000)
        
        # 랜덤 이벤트
        events = [
            f"🎯 {random.choice(list(self.team.keys()))} finished a task!",
            "⚠️ Bug found in production!",
            "🏆 Customer satisfaction increased!",
            "☕ Team coffee break (+5 morale)",
            "📈 GitHub stars +10!"
        ]
        self.events.append(random.choice(events))
        
        # 팀 진행률 변경
        for member in self.team:
            change = random.randint(-5, 15)
            self.team[member]['progress'] = max(0, min(100, self.team[member]['progress'] + change))
        
        # PR/Issue 진행
        if random.random() > 0.5:
            self.pr_merged = min(self.pr_total, self.pr_merged + 1)
        if random.random() > 0.5:
            self.issues_closed = min(self.issues_total, self.issues_closed + 1)
    
    def show_stats(self):
        """통계 표시"""
        print("\n📊 DETAILED STATS")
        print("═" * 40)
        print(f"Total Score: {self.score:,}")
        print(f"Days Played: {self.day}")
        print(f"Budget Remaining: ${self.budget:,}")
        print(f"Team Morale: {self.team_morale}%")
        print(f"Productivity: {sum(m['progress'] for m in self.team.values()) / len(self.team):.1f}%")
        print("\nTeam Performance:")
        for name, info in self.team.items():
            print(f"  • {name}: {info['progress']}% - {info['status']}")
        print("\nPress Enter to continue...")
        input()
    
    def run(self):
        """메인 게임 루프"""
        print("🎮 Loading Tycoon Dashboard...")
        self.get_github_data()
        time.sleep(1)
        
        while True:
            self.display()
            
            choice = input("\nYour command: ").strip().upper()
            
            if choice == 'Q':
                print(f"\n👋 Final Score: {self.score:,} | Days: {self.day}")
                break
            elif choice == 'A':
                for i in range(len(self.decisions)):
                    self.handle_decision(1)
                self.events.append("🎉 All decisions approved!")
            elif choice == 'T':
                self.simulate_time()
            elif choice == 'U':
                self.get_github_data()
                self.events.append("🔄 GitHub data updated!")
            elif choice == 'S':
                self.show_stats()
            elif choice.isdigit():
                if self.handle_decision(int(choice)):
                    pass
                else:
                    self.events.append("❌ Invalid decision number")
            else:
                self.events.append("❓ Unknown command")
            
            time.sleep(0.5)

if __name__ == "__main__":
    game = SimpleTycoon()
    try:
        game.run()
    except KeyboardInterrupt:
        print(f"\n\n👋 Game interrupted! Final Score: {game.score:,}")