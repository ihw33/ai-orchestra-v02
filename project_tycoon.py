#!/usr/bin/env python3
"""
Project Tycoon - 게임화된 프로젝트 관리 시스템
Football Manager 스타일의 프로젝트 대시보드
"""

import os
import sys
import time
import random
import json
import subprocess
from datetime import datetime, timedelta
from dataclasses import dataclass
from typing import Dict, List, Optional
from enum import Enum
import curses

class TeamType(Enum):
    BACKEND = "Backend"
    FRONTEND = "Frontend"
    QA = "QA"
    DESIGN = "Design"
    DEVOPS = "DevOps"

@dataclass
class Team:
    name: TeamType
    progress: int = 0
    morale: int = 85
    velocity: int = 100
    members: int = 10
    
    # Football Manager 스타일 스탯
    speed: int = 75
    quality: int = 80
    creativity: int = 70
    teamwork: int = 85
    stamina: int = 80

@dataclass
class Decision:
    id: int
    title: str
    priority: str  # CRITICAL, HIGH, MEDIUM, LOW
    team: TeamType
    time_limit: int  # minutes
    reward: int  # budget
    xp: int
    description: str
    status: str = "pending"

class ProjectTycoon:
    def __init__(self):
        self.day = 1
        self.budget = 100000
        self.reputation = 750
        self.automation_rate = 70
        
        # 팀 초기화
        self.teams = {
            TeamType.BACKEND: Team(TeamType.BACKEND, 65, 85),
            TeamType.FRONTEND: Team(TeamType.FRONTEND, 45, 90),
            TeamType.QA: Team(TeamType.QA, 80, 75),
            TeamType.DESIGN: Team(TeamType.DESIGN, 70, 88),
            TeamType.DEVOPS: Team(TeamType.DEVOPS, 55, 82),
        }
        
        # 의사결정 큐
        self.decision_queue = []
        self.completed_decisions = []
        self.achievements = []
        
        # 게임 상태
        self.game_running = True
        self.current_decision = None
        self.daily_stats = {
            "decisions_made": 0,
            "tasks_completed": 0,
            "bugs_fixed": 0,
            "features_shipped": 0
        }
        
    def load_github_decisions(self):
        """GitHub에서 실제 이슈/PR 로드"""
        try:
            result = subprocess.run(
                ["gh", "issue", "list", "-R", "ihw33/ai-orchestra-v02", 
                 "--state", "open", "--json", "number,title,labels", "--limit", "10"],
                capture_output=True, text=True
            )
            
            if result.stdout:
                issues = json.loads(result.stdout)
                for issue in issues[:5]:  # 최대 5개
                    priority = "MEDIUM"
                    for label in issue.get('labels', []):
                        if 'critical' in label['name'].lower():
                            priority = "CRITICAL"
                        elif 'high' in label['name'].lower():
                            priority = "HIGH"
                    
                    decision = Decision(
                        id=issue['number'],
                        title=issue['title'],
                        priority=priority,
                        team=random.choice(list(TeamType)),
                        time_limit=random.randint(5, 30),
                        reward=random.randint(500, 5000),
                        xp=random.randint(10, 100),
                        description=f"Issue #{issue['number']}"
                    )
                    self.decision_queue.append(decision)
        except:
            # 실패시 샘플 데이터
            self.generate_sample_decisions()
    
    def generate_sample_decisions(self):
        """샘플 결정 생성"""
        samples = [
            ("Critical Security Patch", "CRITICAL", TeamType.BACKEND, 2000, 50),
            ("UI Redesign Review", "HIGH", TeamType.DESIGN, 1500, 30),
            ("Performance Test", "MEDIUM", TeamType.QA, 1000, 20),
            ("Deploy to Production", "HIGH", TeamType.DEVOPS, 3000, 40),
            ("Bug Fix #142", "LOW", TeamType.FRONTEND, 500, 10),
        ]
        
        for title, priority, team, reward, xp in samples:
            decision = Decision(
                id=random.randint(100, 999),
                title=title,
                priority=priority,
                team=team,
                time_limit=random.randint(5, 30),
                reward=reward,
                xp=xp,
                description=f"Auto-generated task"
            )
            self.decision_queue.append(decision)
    
    def draw_dashboard(self, stdscr):
        """메인 대시보드 그리기"""
        stdscr.clear()
        height, width = stdscr.getmaxyx()
        
        # 헤더
        header = f"PROJECT TYCOON | Day {self.day} | Budget: ${self.budget:,} | Rep: ⭐{self.reputation}"
        stdscr.addstr(0, (width - len(header)) // 2, header, curses.A_BOLD)
        stdscr.addstr(1, 0, "═" * width)
        
        # 팀 상태 (왼쪽)
        y = 3
        stdscr.addstr(y, 2, "📊 TEAM STATUS", curses.A_BOLD)
        y += 2
        
        for team in self.teams.values():
            progress_bar = self.create_progress_bar(team.progress, 20)
            morale_emoji = self.get_morale_emoji(team.morale)
            line = f"{team.name.value:10} {progress_bar} {team.progress}% {morale_emoji}"
            stdscr.addstr(y, 2, line)
            y += 1
        
        # 오늘의 목표 (오른쪽)
        y = 3
        x = width // 2
        stdscr.addstr(y, x, "🎯 TODAY'S OBJECTIVES", curses.A_BOLD)
        y += 2
        
        for i, decision in enumerate(self.decision_queue[:4]):
            priority_emoji = self.get_priority_emoji(decision.priority)
            line = f"{priority_emoji} {decision.title[:30]}"
            stdscr.addstr(y + i, x, line)
        
        # 성과 메트릭 (하단)
        y = height - 10
        stdscr.addstr(y, 2, "📈 PERFORMANCE", curses.A_BOLD)
        y += 1
        
        metrics = [
            f"Decisions: {self.daily_stats['decisions_made']}/30",
            f"Completed: {self.daily_stats['tasks_completed']}/50",
            f"Automation: {self.automation_rate}%",
            f"Team Avg: {self.calculate_team_average()}%"
        ]
        
        for metric in metrics:
            stdscr.addstr(y, 2, metric)
            y += 1
        
        # 현재 결정 (중앙)
        if self.current_decision:
            self.draw_decision_box(stdscr, self.current_decision)
        
        # 하단 메뉴
        menu = "[A]pprove [D]elegate [H]old [R]eject [Q]uit [N]ext"
        stdscr.addstr(height - 2, (width - len(menu)) // 2, menu)
        
        stdscr.refresh()
    
    def draw_decision_box(self, stdscr, decision):
        """결정 박스 그리기"""
        height, width = stdscr.getmaxyx()
        box_height = 10
        box_width = 60
        y = (height - box_height) // 2
        x = (width - box_width) // 2
        
        # 박스 테두리
        stdscr.addstr(y, x, "╔" + "═" * (box_width - 2) + "╗")
        for i in range(1, box_height - 1):
            stdscr.addstr(y + i, x, "║" + " " * (box_width - 2) + "║")
        stdscr.addstr(y + box_height - 1, x, "╚" + "═" * (box_width - 2) + "╝")
        
        # 내용
        priority_emoji = self.get_priority_emoji(decision.priority)
        stdscr.addstr(y + 1, x + 2, f"{priority_emoji} DECISION REQUIRED", curses.A_BOLD)
        stdscr.addstr(y + 3, x + 2, f"Task: {decision.title}")
        stdscr.addstr(y + 4, x + 2, f"Team: {decision.team.value}")
        stdscr.addstr(y + 5, x + 2, f"Reward: ${decision.reward} | XP: {decision.xp}")
        stdscr.addstr(y + 6, x + 2, f"Time Limit: {decision.time_limit} min")
        
        # PM 추천
        stdscr.addstr(y + 8, x + 2, "PM: 'Recommend approval - high priority'")
    
    def create_progress_bar(self, progress, width=20):
        """프로그레스 바 생성"""
        filled = int(progress / 100 * width)
        return "[" + "█" * filled + "░" * (width - filled) + "]"
    
    def get_morale_emoji(self, morale):
        """사기 이모지"""
        if morale >= 90:
            return "😄"
        elif morale >= 70:
            return "😊"
        elif morale >= 50:
            return "😐"
        elif morale >= 30:
            return "😟"
        else:
            return "😢"
    
    def get_priority_emoji(self, priority):
        """우선순위 이모지"""
        emojis = {
            "CRITICAL": "⚡",
            "HIGH": "🔥",
            "MEDIUM": "📌",
            "LOW": "📎"
        }
        return emojis.get(priority, "•")
    
    def calculate_team_average(self):
        """팀 평균 계산"""
        total = sum(team.progress for team in self.teams.values())
        return total // len(self.teams)
    
    def process_decision(self, action):
        """결정 처리"""
        if not self.current_decision:
            return
        
        decision = self.current_decision
        
        if action == 'a':  # Approve
            self.budget += decision.reward
            self.reputation += decision.xp // 10
            self.daily_stats["decisions_made"] += 1
            decision.status = "approved"
            
            # 팀 진행도 업데이트
            team = self.teams[decision.team]
            team.progress = min(100, team.progress + random.randint(5, 15))
            team.morale = min(100, team.morale + 2)
            
        elif action == 'd':  # Delegate
            decision.status = "delegated"
            self.automation_rate += 1
            
        elif action == 'h':  # Hold
            decision.status = "deferred"
            self.decision_queue.append(decision)
            
        elif action == 'r':  # Reject
            decision.status = "rejected"
            self.teams[decision.team].morale -= 5
        
        self.completed_decisions.append(decision)
        self.current_decision = None
    
    def get_next_decision(self):
        """다음 결정 가져오기"""
        if self.decision_queue:
            # 우선순위 정렬
            priority_order = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}
            self.decision_queue.sort(key=lambda d: priority_order.get(d.priority, 4))
            
            self.current_decision = self.decision_queue.pop(0)
            return self.current_decision
        return None
    
    def daily_update(self):
        """일일 업데이트"""
        self.day += 1
        
        # 팀 진행도 자동 증가
        for team in self.teams.values():
            if team.progress < 100:
                team.progress += random.randint(1, 5)
            
            # 사기 변화
            if random.random() < 0.3:
                team.morale += random.randint(-5, 5)
                team.morale = max(0, min(100, team.morale))
        
        # 새 결정 생성
        if len(self.decision_queue) < 5:
            self.generate_sample_decisions()
        
        # 일일 비용
        self.budget -= 1000
        
        # 업적 체크
        self.check_achievements()
    
    def check_achievements(self):
        """업적 확인"""
        if self.daily_stats["decisions_made"] >= 10:
            self.achievements.append("🏃 Speed Demon")
        
        if all(team.morale >= 80 for team in self.teams.values()):
            self.achievements.append("😊 Happy Teams")
        
        if self.automation_rate >= 90:
            self.achievements.append("🤖 Automation Master")
    
    def run(self, stdscr):
        """메인 게임 루프"""
        curses.curs_set(0)  # 커서 숨기기
        stdscr.nodelay(1)   # 비차단 입력
        
        # 초기 데이터 로드
        self.load_github_decisions()
        self.get_next_decision()
        
        last_update = time.time()
        
        while self.game_running:
            # 화면 그리기
            self.draw_dashboard(stdscr)
            
            # 입력 처리
            key = stdscr.getch()
            if key != -1:
                if chr(key).lower() == 'q':
                    self.game_running = False
                elif chr(key).lower() == 'n':
                    self.get_next_decision()
                elif chr(key).lower() in ['a', 'd', 'h', 'r']:
                    self.process_decision(chr(key).lower())
                    self.get_next_decision()
            
            # 30초마다 자동 업데이트
            if time.time() - last_update > 30:
                self.daily_update()
                last_update = time.time()
            
            time.sleep(0.1)

def main():
    """메인 실행"""
    game = ProjectTycoon()
    
    try:
        curses.wrapper(game.run)
    except KeyboardInterrupt:
        pass
    
    # 게임 종료시 통계
    print(f"\n🎮 Game Over - Day {game.day}")
    print(f"Final Budget: ${game.budget:,}")
    print(f"Reputation: ⭐{game.reputation}")
    print(f"Decisions Made: {len(game.completed_decisions)}")
    print(f"Achievements: {', '.join(game.achievements)}")

if __name__ == "__main__":
    main()