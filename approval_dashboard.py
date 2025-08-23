#!/usr/bin/env python3
"""
🎯 Thomas 승인 대시보드 - 긴급 임시 버전
실행: python approval_dashboard.py
"""

import subprocess
import json
import os
import sys
from datetime import datetime

class ApprovalDashboard:
    def __init__(self):
        self.repo = "ihw33/ai-orchestra-v02"
        self.clear_screen()
        
    def clear_screen(self):
        os.system('clear' if os.name == 'posix' else 'cls')
    
    def get_open_issues(self):
        """열린 이슈 가져오기"""
        try:
            cmd = f"gh issue list -R {self.repo} --state open --json number,title,body,labels --limit 10"
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            if result.returncode == 0:
                return json.loads(result.stdout)
            return []
        except:
            return []
    
    def get_open_prs(self):
        """열린 PR 가져오기"""
        try:
            cmd = f"gh pr list -R {self.repo} --state open --json number,title,body --limit 10"
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            if result.returncode == 0:
                return json.loads(result.stdout)
            return []
        except:
            return []
    
    def display_dashboard(self):
        """대시보드 표시"""
        self.clear_screen()
        print("╔══════════════════════════════════════════════════════════════════════╗")
        print("║                    🎯 THOMAS 승인 대시보드                            ║")
        print(f"║                    {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}                           ║")
        print("╠══════════════════════════════════════════════════════════════════════╣")
        print("║                                                                        ║")
        
        # 이슈 표시
        issues = self.get_open_issues()
        prs = self.get_open_prs()
        
        items = []
        for issue in issues[:3]:
            items.append({
                'type': 'Issue',
                'number': issue['number'],
                'title': issue['title'][:50],
                'body': (issue.get('body', '') or '')[:60]
            })
        
        for pr in prs[:3]:
            items.append({
                'type': 'PR',
                'number': pr['number'],
                'title': pr['title'][:50],
                'body': (pr.get('body', '') or '')[:60]
            })
        
        if not items:
            print("║              📭 승인 대기 중인 항목이 없습니다                        ║")
        else:
            for idx, item in enumerate(items[:6], 1):
                print(f"║ [{idx}] {item['type']} #{item['number']}: {item['title']:<45}║")
                summary = item['body'].replace('\n', ' ')[:50]
                print(f"║     {summary:<65}║")
                print("║                                                                        ║")
        
        print("║────────────────────────────────────────────────────────────────────────║")
        print("║ 명령: [1-6] 선택 | [R]efresh | [Q]uit                                 ║")
        print("║       선택 후: [A]pprove | [H]old | [D]ecline | [C]omment | [B]ack    ║")
        print("╚══════════════════════════════════════════════════════════════════════╝")
        
        return items
    
    def handle_item_action(self, item):
        """개별 항목 처리"""
        self.clear_screen()
        print(f"\n{'='*70}")
        print(f"{item['type']} #{item['number']}: {item['title']}")
        print(f"{'='*70}")
        print(f"\n{item['body'][:200]}...\n")
        
        # GitHub 링크 표시
        if item['type'] == 'PR':
            url = f"https://github.com/{self.repo}/pull/{item['number']}"
        else:
            url = f"https://github.com/{self.repo}/issues/{item['number']}"
        print(f"🔗 GitHub에서 보기: {url}\n")
        
        print("액션을 선택하세요:")
        print("[A] ✅ 승인  [H] ⏸️ 보류  [D] ❌ 거절  [C] 💬 코멘트")
        print("[V] 👁️ 브라우저에서 보기  [B] 뒤로")
        
        action = input("\n선택: ").strip().lower()
        
        if action == 'a':
            self.approve_item(item)
        elif action == 'h':
            self.hold_item(item)
        elif action == 'd':
            self.decline_item(item)
        elif action == 'c':
            self.comment_item(item)
        elif action == 'b':
            return
        else:
            print("잘못된 선택입니다.")
    
    def approve_item(self, item):
        """승인 처리"""
        print(f"\n✅ {item['type']} #{item['number']}를 승인합니다...")
        
        if item['type'] == 'PR':
            cmd = f"gh pr review {item['number']} -R {self.repo} --approve -b '✅ 승인되었습니다.'"
            subprocess.run(cmd, shell=True)
            print(f"PR #{item['number']} 승인 완료!")
            
            # 머지 여부 확인
            merge = input("바로 머지하시겠습니까? (y/n): ").strip().lower()
            if merge == 'y':
                cmd = f"gh pr merge {item['number']} -R {self.repo} --squash"
                subprocess.run(cmd, shell=True)
                print(f"PR #{item['number']} 머지 완료!")
        else:
            cmd = f"gh issue comment {item['number']} -R {self.repo} -b '✅ 승인되었습니다. 작업을 진행해주세요.'"
            subprocess.run(cmd, shell=True)
            
            # 라벨 추가
            cmd = f"gh issue edit {item['number']} -R {self.repo} --add-label approved"
            subprocess.run(cmd, shell=True, capture_output=True)
            print(f"Issue #{item['number']} 승인 완료!")
        
        input("\n계속하려면 Enter를 누르세요...")
    
    def hold_item(self, item):
        """보류 처리"""
        print(f"\n⏸️ {item['type']} #{item['number']}를 보류합니다...")
        
        reason = input("보류 사유 (선택사항): ").strip()
        comment = f"⏸️ 보류되었습니다."
        if reason:
            comment += f"\n사유: {reason}"
        
        target = 'pr' if item['type'] == 'PR' else 'issue'
        cmd = f"gh {target} comment {item['number']} -R {self.repo} -b '{comment}'"
        subprocess.run(cmd, shell=True)
        
        # 라벨 추가
        cmd = f"gh {target} edit {item['number']} -R {self.repo} --add-label on-hold"
        subprocess.run(cmd, shell=True, capture_output=True)
        
        print(f"{item['type']} #{item['number']} 보류 완료!")
        input("\n계속하려면 Enter를 누르세요...")
    
    def decline_item(self, item):
        """거절 처리"""
        print(f"\n❌ {item['type']} #{item['number']}를 거절합니다...")
        
        reason = input("거절 사유 (필수): ").strip()
        if not reason:
            print("거절 사유를 입력해야 합니다.")
            return
        
        comment = f"❌ 거절되었습니다.\n사유: {reason}"
        
        target = 'pr' if item['type'] == 'PR' else 'issue'
        cmd = f"gh {target} comment {item['number']} -R {self.repo} -b '{comment}'"
        subprocess.run(cmd, shell=True)
        
        if item['type'] == 'PR':
            cmd = f"gh pr close {item['number']} -R {self.repo}"
        else:
            cmd = f"gh issue close {item['number']} -R {self.repo}"
        subprocess.run(cmd, shell=True)
        
        print(f"{item['type']} #{item['number']} 거절 및 닫기 완료!")
        input("\n계속하려면 Enter를 누르세요...")
    
    def comment_item(self, item):
        """코멘트 추가"""
        print(f"\n💬 {item['type']} #{item['number']}에 코멘트를 추가합니다...")
        
        comment = input("코멘트 내용: ").strip()
        if comment:
            target = 'pr' if item['type'] == 'PR' else 'issue'
            cmd = f"gh {target} comment {item['number']} -R {self.repo} -b '💬 {comment}'"
            subprocess.run(cmd, shell=True)
            print("코멘트 추가 완료!")
        
        input("\n계속하려면 Enter를 누르세요...")
    
    def run(self):
        """메인 루프"""
        while True:
            items = self.display_dashboard()
            
            choice = input("\n선택: ").strip().lower()
            
            if choice == 'q':
                print("\n👋 대시보드를 종료합니다.")
                break
            elif choice == 'r':
                print("\n🔄 새로고침 중...")
                continue
            elif choice.isdigit():
                idx = int(choice) - 1
                if 0 <= idx < len(items):
                    self.handle_item_action(items[idx])
                else:
                    print("잘못된 번호입니다.")
                    input("계속하려면 Enter를 누르세요...")

def main():
    print("🚀 승인 대시보드를 시작합니다...")
    print("GitHub CLI 확인 중...")
    
    # gh 설치 확인
    result = subprocess.run("gh --version", shell=True, capture_output=True)
    if result.returncode != 0:
        print("❌ GitHub CLI가 설치되지 않았습니다.")
        print("설치: brew install gh")
        sys.exit(1)
    
    # 로그인 확인
    result = subprocess.run("gh auth status", shell=True, capture_output=True)
    if result.returncode != 0:
        print("❌ GitHub에 로그인되지 않았습니다.")
        print("로그인: gh auth login")
        sys.exit(1)
    
    dashboard = ApprovalDashboard()
    dashboard.run()

if __name__ == "__main__":
    main()