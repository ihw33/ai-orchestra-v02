#!/usr/bin/env python3
"""
PM-Thomas Review Session System
검토 세션을 위한 대화형 시스템
"""

import os
import sys
import json
import time
from datetime import datetime
from enum import Enum
from typing import List, Dict, Optional
from pathlib import Path
import subprocess

class SessionMode(Enum):
    ACCEPT = "accept"      # 빠른 승인 (1-2분)
    PLAN = "plan"         # 전략 수립 (5-10분)
    STEP = "step"         # 단계별 검토 (단계당 2-3분)

class ReviewItem:
    def __init__(self, item_type: str, title: str, status: str, details: Dict):
        self.type = item_type
        self.title = title
        self.status = status
        self.details = details
        self.decision = None
        self.notes = ""

class ReviewSession:
    def __init__(self, mode: SessionMode = SessionMode.ACCEPT):
        self.mode = mode
        self.start_time = datetime.now()
        self.decisions = []
        self.review_items = []
        self.session_log = []
        
    def load_pending_items(self):
        """GitHub에서 검토 대기 항목 로드"""
        try:
            # 오픈 PR 확인
            pr_output = subprocess.run(
                ["gh", "pr", "list", "-R", "ihw33/ai-orchestra-v02", "--state", "open", "--json", "number,title,labels"],
                capture_output=True, text=True
            ).stdout
            
            # 오픈 이슈 확인
            issue_output = subprocess.run(
                ["gh", "issue", "list", "-R", "ihw33/ai-orchestra-v02", "--state", "open", "--limit", "10", "--json", "number,title,labels"],
                capture_output=True, text=True
            ).stdout
            
            if pr_output:
                prs = json.loads(pr_output)
                for pr in prs:
                    self.review_items.append(ReviewItem(
                        "PR", 
                        f"PR #{pr['number']}: {pr['title']}", 
                        "pending",
                        pr
                    ))
            
            if issue_output:
                issues = json.loads(issue_output)[:5]  # 최근 5개만
                for issue in issues:
                    if any(label['name'] in ['needs-review', 'blocker'] for label in issue.get('labels', [])):
                        self.review_items.append(ReviewItem(
                            "Issue",
                            f"Issue #{issue['number']}: {issue['title']}",
                            "pending",
                            issue
                        ))
                        
        except Exception as e:
            print(f"⚠️  항목 로드 중 오류: {e}")
    
    def start(self):
        """세션 시작"""
        self.load_pending_items()
        
        print(f"""
╔════════════════════════════════════════════════════════════╗
║            PM-THOMAS REVIEW SESSION                        ║
║                                                            ║
║  Mode: {self.mode.value.upper():20}                       ║
║  Time: {datetime.now().strftime('%Y-%m-%d %H:%M'):20}     ║
║  Items: {len(self.review_items):3} pending                ║
╚════════════════════════════════════════════════════════════╝
        """)
        
        if self.mode == SessionMode.ACCEPT:
            return self.quick_review()
        elif self.mode == SessionMode.PLAN:
            return self.strategic_review()
        elif self.mode == SessionMode.STEP:
            return self.step_by_step_review()
    
    def quick_review(self):
        """빠른 검토 모드 (1-2분)"""
        print("\n🚀 QUICK REVIEW MODE - 빠른 승인\n")
        
        if not self.review_items:
            print("✅ 검토할 항목이 없습니다.")
            return
        
        print(f"📋 검토 대기 항목 ({len(self.review_items)}개):")
        for i, item in enumerate(self.review_items, 1):
            print(f"  {i}. {item.title}")
        
        print(f"""
╔════════════════════════════════════════════════════════════╗
║  [A] Accept All - 모두 승인                               ║
║  [R] Reject All - 모두 거부                               ║
║  [S] Select - 선택적 승인                                 ║
║  [D] Details - 상세 보기                                  ║
║  [X] Exit - 종료                                          ║
╚════════════════════════════════════════════════════════════╝
        """)
        
        choice = input("\n선택 >>> ").strip().upper()
        
        if choice == 'A':
            for item in self.review_items:
                item.decision = "ACCEPTED"
            print("✅ 모든 항목이 승인되었습니다.")
            self.execute_decisions()
            
        elif choice == 'S':
            for i, item in enumerate(self.review_items, 1):
                response = input(f"{i}. {item.title} [Y/n/s(kip)] >>> ").strip().lower()
                if response in ['', 'y']:
                    item.decision = "ACCEPTED"
                elif response == 'n':
                    item.decision = "REJECTED"
                else:
                    item.decision = "SKIPPED"
            self.execute_decisions()
            
        elif choice == 'D':
            self.show_details()
            return self.quick_review()
    
    def strategic_review(self):
        """전략 수립 모드 (5-10분)"""
        print("\n📊 STRATEGIC PLANNING MODE - 전략 수립\n")
        
        # 현재 상황 분석
        stats = self.get_statistics()
        print(f"""
현재 상황:
  ✅ 완료: {stats['completed']} 작업
  🔄 진행중: {stats['in_progress']} 작업
  🚨 블로커: {stats['blockers']} 개
  📋 대기중: {stats['pending']} 개
        """)
        
        # 주요 결정 사항
        decisions = [
            "다음 스프린트 우선순위 설정",
            "블로커 해결 방안 결정",
            "리소스 재배치",
            "마일스톤 조정"
        ]
        
        print("\n💡 주요 결정 사항:")
        for i, decision in enumerate(decisions, 1):
            print(f"  {i}. {decision}")
        
        print(f"""
╔════════════════════════════════════════════════════════════╗
║  전략적 옵션:                                              ║
║                                                            ║
║  [1] Fast Track - 빠른 출시 중심                          ║
║      (기능 축소, 핵심만 구현)                             ║
║                                                            ║
║  [2] Quality First - 품질 중심                            ║
║      (충분한 테스트, 리팩토링 포함)                      ║
║                                                            ║
║  [3] Balanced - 균형 접근                                 ║
║      (핵심 기능 + 필수 테스트)                           ║
║                                                            ║
║  [C] Custom - 커스텀 전략 수립                           ║
╚════════════════════════════════════════════════════════════╝
        """)
        
        strategy = input("\n전략 선택 >>> ").strip()
        
        if strategy in ['1', '2', '3']:
            self.apply_strategy(strategy)
        elif strategy.upper() == 'C':
            self.custom_strategy()
    
    def step_by_step_review(self):
        """단계별 상세 검토 모드"""
        print("\n🔍 STEP-BY-STEP MODE - 단계별 검토\n")
        
        if not self.review_items:
            print("✅ 검토할 항목이 없습니다.")
            return
        
        for i, item in enumerate(self.review_items, 1):
            print(f"""
════════════════════════════════════════════════════════════
Step {i}/{len(self.review_items)}
{item.title}
Type: {item.type} | Status: {item.status}
────────────────────────────────────────────────────────────
            """)
            
            # 상세 정보 표시
            if item.type == "PR":
                self.show_pr_details(item)
            elif item.type == "Issue":
                self.show_issue_details(item)
            
            print(f"""
[A] Approve/Accept   [R] Reject   [M] Modify
[S] Skip            [D] Delegate  [X] Exit
            """)
            
            action = input(f"Action for Step {i} >>> ").strip().upper()
            
            if action == 'A':
                item.decision = "APPROVED"
                item.notes = input("Notes (optional) >>> ").strip()
            elif action == 'R':
                item.decision = "REJECTED"
                item.notes = input("Reason >>> ").strip()
            elif action == 'M':
                item.decision = "MODIFY"
                item.notes = input("Modifications needed >>> ").strip()
            elif action == 'X':
                break
                
        self.execute_decisions()
    
    def show_pr_details(self, item: ReviewItem):
        """PR 상세 정보 표시"""
        pr_num = item.details.get('number')
        if pr_num:
            # PR diff 요약 가져오기
            try:
                diff_stats = subprocess.run(
                    ["gh", "pr", "diff", str(pr_num), "-R", "ihw33/ai-orchestra-v02", "--stat"],
                    capture_output=True, text=True
                ).stdout
                print("Changes:")
                print(diff_stats[:500] if diff_stats else "  No changes found")
            except:
                print("  Unable to fetch PR details")
    
    def show_issue_details(self, item: ReviewItem):
        """Issue 상세 정보 표시"""
        labels = item.details.get('labels', [])
        if labels:
            label_names = [l['name'] for l in labels]
            print(f"Labels: {', '.join(label_names)}")
    
    def execute_decisions(self):
        """결정사항 실행"""
        print("\n🚀 결정사항 실행 중...\n")
        
        for item in self.review_items:
            if item.decision == "ACCEPTED" or item.decision == "APPROVED":
                print(f"✅ {item.title} - 승인됨")
                if item.type == "PR":
                    self.approve_pr(item)
            elif item.decision == "REJECTED":
                print(f"❌ {item.title} - 거부됨: {item.notes}")
                if item.type == "PR":
                    self.reject_pr(item)
            elif item.decision == "MODIFY":
                print(f"📝 {item.title} - 수정 필요: {item.notes}")
                self.request_changes(item)
    
    def approve_pr(self, item: ReviewItem):
        """PR 승인 처리"""
        pr_num = item.details.get('number')
        if pr_num:
            try:
                subprocess.run([
                    "gh", "pr", "review", str(pr_num), 
                    "-R", "ihw33/ai-orchestra-v02",
                    "--approve", "-b", f"Approved in review session: {item.notes}"
                ])
            except:
                pass
    
    def reject_pr(self, item: ReviewItem):
        """PR 거부 처리"""
        pr_num = item.details.get('number')
        if pr_num:
            try:
                subprocess.run([
                    "gh", "pr", "comment", str(pr_num),
                    "-R", "ihw33/ai-orchestra-v02",
                    "--body", f"❌ Rejected in review session: {item.notes}"
                ])
            except:
                pass
    
    def request_changes(self, item: ReviewItem):
        """변경 요청"""
        num = item.details.get('number')
        if num:
            try:
                subprocess.run([
                    "gh", "issue", "comment" if item.type == "Issue" else "pr comment",
                    str(num), "-R", "ihw33/ai-orchestra-v02",
                    "--body", f"📝 Changes requested: {item.notes}"
                ])
            except:
                pass
    
    def get_statistics(self) -> Dict:
        """통계 정보 가져오기"""
        # 실제로는 GitHub API에서 가져옴
        return {
            'completed': 12,
            'in_progress': 5,
            'blockers': 2,
            'pending': len(self.review_items)
        }
    
    def apply_strategy(self, strategy: str):
        """전략 적용"""
        strategies = {
            '1': "Fast Track - 핵심 기능 우선",
            '2': "Quality First - 품질 중심",
            '3': "Balanced - 균형 접근"
        }
        
        print(f"\n✅ 전략 선택됨: {strategies.get(strategy)}")
        print("이 전략이 모든 AI 에이전트에게 전달됩니다.")
        
        # 전략을 파일로 저장
        with open("current_strategy.txt", "w") as f:
            f.write(strategies.get(strategy))
    
    def show_details(self):
        """상세 정보 표시"""
        for i, item in enumerate(self.review_items, 1):
            print(f"\n{i}. {item.title}")
            print(f"   Type: {item.type}")
            print(f"   Status: {item.status}")
            if item.type == "PR":
                self.show_pr_details(item)
            elif item.type == "Issue":
                self.show_issue_details(item)
    
    def custom_strategy(self):
        """커스텀 전략 수립"""
        print("\n📝 커스텀 전략 수립")
        
        priorities = []
        print("우선순위를 입력하세요 (빈 줄로 종료):")
        while True:
            priority = input(f"  {len(priorities)+1}. ").strip()
            if not priority:
                break
            priorities.append(priority)
        
        if priorities:
            print(f"\n✅ 커스텀 전략 저장됨:")
            for i, p in enumerate(priorities, 1):
                print(f"  {i}. {p}")
            
            with open("custom_strategy.txt", "w") as f:
                f.write("\n".join(priorities))

def main():
    """메인 실행 함수"""
    import argparse
    
    parser = argparse.ArgumentParser(description="PM-Thomas Review Session")
    parser.add_argument(
        "--mode", 
        choices=["accept", "plan", "step"],
        default="accept",
        help="Review mode"
    )
    
    args = parser.parse_args()
    
    mode_map = {
        "accept": SessionMode.ACCEPT,
        "plan": SessionMode.PLAN,
        "step": SessionMode.STEP
    }
    
    session = ReviewSession(mode_map[args.mode])
    session.start()
    
    # 세션 종료
    duration = (datetime.now() - session.start_time).total_seconds() / 60
    print(f"\n✅ 세션 종료 (소요 시간: {duration:.1f}분)")

if __name__ == "__main__":
    main()