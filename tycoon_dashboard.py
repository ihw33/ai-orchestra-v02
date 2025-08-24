#!/usr/bin/env python3
"""
🎮 TYCOON DASHBOARD - 실시간 GitHub 프로젝트 관리 게임
Football Manager + Tycoon 스타일 터미널 대시보드
"""

import os
import sys
import time
import random
import curses
from datetime import datetime
import subprocess
import json
import shlex

class TycoonDashboard:
    """터미널 기반 타이쿤 대시보드"""
    
    def __init__(self):
        self.score = 8470
        self.day = 42
        self.budget = 15000
        self.team_morale = 85
        self.pr_merged = 5
        self.pr_total = 8
        self.issues_closed = 12
        self.issues_total = 15
        
        # 팀원 상태
        self.team = {
            "Emma": {"role": "CPO", "status": "PR #49 리뷰중", "progress": 80, "mood": "😊"},
            "Rajiv": {"role": "Eng", "status": "3 commits", "progress": 100, "mood": "🔥"},
            "Anna": {"role": "QA", "status": "Testing...", "progress": 70, "mood": "🎯"},
            "Yui": {"role": "UI", "status": "디자인 중", "progress": 65, "mood": "🎨"},
            "Olaf": {"role": "Ops", "status": "배포 준비", "progress": 90, "mood": "⚡"}
        }
        
        # 대기중인 결정사항
        self.decisions = [
            {"id": 1, "type": "PR", "title": "PR #49: Approve?", "priority": "Critical"},
            {"id": 2, "type": "Issue", "title": "Issue #47: Assign team?", "priority": "High"},
            {"id": 3, "type": "Budget", "title": "Budget alert: -$2,000 today", "priority": "Medium"}
        ]
        
        # 이벤트 로그
        self.events = []
        self.add_event("🎮 Game started! Welcome to Tycoon Dashboard!")
        
    def add_event(self, message):
        """이벤트 추가"""
        timestamp = datetime.now().strftime("%H:%M")
        self.events.append(f"[{timestamp}] {message}")
        if len(self.events) > 5:
            self.events.pop(0)
    
    def get_github_data(self):
        """실제 GitHub 데이터 가져오기"""
        try:
            # PR 목록
            cmd = ["gh", "pr", "list", "-R", "ihw33/ai-orchestra-v02", "--json", "number,title,state", "--limit", "5"]
            result = subprocess.run(cmd, capture_output=True, text=True, stderr=subprocess.DEVNULL)
            if result.returncode == 0 and result.stdout:
                prs = json.loads(result.stdout)
                self.pr_total = len(prs)
                self.pr_merged = len([p for p in prs if p.get('state') == 'MERGED'])
            
            # Issue 목록
            cmd = ["gh", "issue", "list", "-R", "ihw33/ai-orchestra-v02", "--json", "number,title,state", "--limit", "10"]
            result = subprocess.run(cmd, capture_output=True, text=True, stderr=subprocess.DEVNULL)
            if result.returncode == 0 and result.stdout:
                issues = json.loads(result.stdout)
                self.issues_total = len(issues)
                self.issues_closed = len([i for i in issues if i.get('state') == 'CLOSED'])
        except (subprocess.SubprocessError, json.JSONDecodeError) as e:
            # 실패 시 기본값 사용, 에러는 로깅만
            pass
    
    def draw_dashboard(self, stdscr):
        """대시보드 그리기"""
        stdscr.clear()
        h, w = stdscr.getmaxyx()
        
        # 색상 설정
        curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_YELLOW, curses.COLOR_BLACK)
        curses.init_pair(3, curses.COLOR_RED, curses.COLOR_BLACK)
        curses.init_pair(4, curses.COLOR_CYAN, curses.COLOR_BLACK)
        
        y = 0
        
        # 헤더
        header = f"🎮 TYCOON DASHBOARD | Day {self.day} | 💰 ${self.budget:,} | ⭐ {self.score:,}"
        stdscr.addstr(y, 2, "╔" + "═" * (len(header) + 4) + "╗")
        y += 1
        stdscr.addstr(y, 2, "║ " + header + " ║", curses.color_pair(4) | curses.A_BOLD)
        y += 1
        stdscr.addstr(y, 2, "╠" + "═" * (len(header) + 4) + "╣")
        y += 1
        
        # 오늘의 스프린트
        stdscr.addstr(y, 2, "║ 📊 Today's Sprint Match                          ║")
        y += 1
        
        pr_percent = (self.pr_merged / self.pr_total * 100) if self.pr_total > 0 else 0
        stdscr.addstr(y, 2, f"║ ├─ PR Merged: {self.pr_merged}/{self.pr_total} ({pr_percent:.1f}%)                    ║")
        y += 1
        
        issue_percent = (self.issues_closed / self.issues_total * 100) if self.issues_total > 0 else 0
        stdscr.addstr(y, 2, f"║ ├─ Issues Closed: {self.issues_closed}/{self.issues_total} ({issue_percent:.1f}%)              ║")
        y += 1
        
        morale_bar = "😊" * (self.team_morale // 20)
        stdscr.addstr(y, 2, f"║ └─ Team Morale: {morale_bar} ({self.team_morale}%)             ║")
        y += 1
        
        stdscr.addstr(y, 2, "╠" + "═" * (len(header) + 4) + "╣")
        y += 1
        
        # 팀 상태
        stdscr.addstr(y, 2, "║ 👥 Team Status (실시간)                          ║")
        y += 1
        
        for name, info in self.team.items():
            progress_bar = "█" * (info['progress'] // 10) + "░" * (10 - info['progress'] // 10)
            line = f"║ {name:6} [{progress_bar}] {info['progress']:3}% {info['mood']} {info['status'][:15]:15} ║"
            
            if info['progress'] >= 90:
                stdscr.addstr(y, 2, line, curses.color_pair(1))
            elif info['progress'] >= 70:
                stdscr.addstr(y, 2, line, curses.color_pair(2))
            else:
                stdscr.addstr(y, 2, line)
            y += 1
        
        stdscr.addstr(y, 2, "╠" + "═" * (len(header) + 4) + "╣")
        y += 1
        
        # 결정 필요 사항
        stdscr.addstr(y, 2, "║ 🎯 Manager Decision Required                     ║", curses.A_BOLD)
        y += 1
        
        for decision in self.decisions[:3]:
            priority_color = curses.color_pair(3) if decision['priority'] == 'Critical' else curses.color_pair(2) if decision['priority'] == 'High' else curses.color_pair(1)
            line = f"║ [{decision['id']}] {decision['title']:35} ║"
            stdscr.addstr(y, 2, line, priority_color)
            y += 1
        
        stdscr.addstr(y, 2, "║                                                  ║")
        y += 1
        stdscr.addstr(y, 2, "║ [A]pprove All | [R]eview | [U]pdate | [Q]uit    ║", curses.A_BOLD)
        y += 1
        stdscr.addstr(y, 2, "╠" + "═" * (len(header) + 4) + "╣")
        y += 1
        
        # 이벤트 로그
        stdscr.addstr(y, 2, "║ 📰 Event Feed                                    ║")
        y += 1
        
        for event in self.events[-3:]:
            line = f"║ {event[:48]:48} ║"
            stdscr.addstr(y, 2, line)
            y += 1
        
        stdscr.addstr(y, 2, "╚" + "═" * (len(header) + 4) + "╝")
        y += 2
        
        # 입력 프롬프트
        stdscr.addstr(y, 2, "Command: ", curses.A_BOLD)
        
        return y, 11  # 커서 위치 반환
    
    def handle_input(self, key):
        """입력 처리"""
        if key == ord('a') or key == ord('A'):
            self.approve_all()
            return "Approved all decisions! 🎯"
        elif key == ord('r') or key == ord('R'):
            self.review_details()
            return "Opening review mode... 🔍"
        elif key == ord('u') or key == ord('U'):
            self.get_github_data()
            return "Updated GitHub data! 🔄"
        elif key == ord('q') or key == ord('Q'):
            return "quit"
        elif key == ord('1'):
            self.handle_decision(1)
            return "PR #49 approved! ✅"
        elif key == ord('2'):
            self.handle_decision(2)
            return "Issue #47 assigned to Rajiv! 👨‍💻"
        elif key == ord('3'):
            self.handle_decision(3)
            return "Budget reviewed! 💰"
        else:
            return None
    
    def approve_all(self):
        """모든 결정 승인"""
        # 리스트 복사본으로 작업하여 순회 중 수정 문제 방지
        decisions_to_approve = self.decisions.copy()
        for decision in decisions_to_approve:
            self.handle_decision(decision['id'])
        self.score += 100
        self.team_morale = min(100, self.team_morale + 5)
        self.add_event("🎉 All decisions approved!")
    
    def handle_decision(self, decision_id):
        """개별 결정 처리"""
        decision = next((d for d in self.decisions if d['id'] == decision_id), None)
        if decision:
            self.decisions.remove(decision)
            self.score += 50
            self.add_event(f"✅ {decision['title']} resolved!")
            
            # 새로운 결정 추가 (시뮬레이션)
            new_decisions = [
                {"id": len(self.decisions) + 4, "type": "PR", "title": f"PR #{random.randint(50, 100)}: Review needed", "priority": "Medium"},
                {"id": len(self.decisions) + 5, "type": "Issue", "title": f"Issue #{random.randint(48, 80)}: New feature", "priority": "Low"},
            ]
            if len(self.decisions) < 3:
                self.decisions.append(random.choice(new_decisions))
    
    def review_details(self):
        """상세 리뷰 (확장 가능)"""
        pass
    
    def simulate_time(self):
        """시간 경과 시뮬레이션"""
        # 랜덤 이벤트
        if random.random() < 0.3:
            events = [
                f"🎯 {random.choice(list(self.team.keys()))} completed a task!",
                f"⚠️ Bug detected in production!",
                f"🏆 PR #{random.randint(100, 200)} merged!",
                f"☕ Team morale +5 (coffee break)",
                f"📊 Daily standup completed"
            ]
            self.add_event(random.choice(events))
        
        # 팀원 진행률 업데이트
        for name in self.team:
            if random.random() < 0.2:
                self.team[name]['progress'] = min(100, self.team[name]['progress'] + random.randint(5, 15))
    
    def run(self, stdscr):
        """메인 루프"""
        curses.curs_set(0)  # 커서 숨기기
        stdscr.nodelay(1)   # 비동기 입력
        stdscr.timeout(100) # 100ms 타임아웃
        
        message = "Welcome to Tycoon Dashboard! Press 'h' for help."
        last_update = time.time()
        
        while True:
            # 대시보드 그리기
            y, x = self.draw_dashboard(stdscr)
            
            # 메시지 표시
            if message:
                stdscr.addstr(y - 2, x, message[:40], curses.A_BOLD)
            
            stdscr.refresh()
            
            # 입력 처리
            key = stdscr.getch()
            if key != -1:
                result = self.handle_input(key)
                if result == "quit":
                    break
                elif result:
                    message = result
            
            # 시간 시뮬레이션 (1초마다)
            if time.time() - last_update > 1:
                self.simulate_time()
                self.day += 0.01  # 천천히 날짜 증가
                last_update = time.time()
            
            time.sleep(0.05)  # CPU 사용량 감소

def main():
    """메인 실행"""
    print("🎮 Starting Tycoon Dashboard...")
    print("Loading GitHub data...")
    
    dashboard = TycoonDashboard()
    dashboard.get_github_data()
    
    try:
        curses.wrapper(dashboard.run)
    except KeyboardInterrupt:
        pass
    
    print("\n👋 Thanks for playing Tycoon Dashboard!")
    print(f"Final Score: {dashboard.score:,}")
    print(f"Days Survived: {int(dashboard.day)}")

if __name__ == "__main__":
    main()