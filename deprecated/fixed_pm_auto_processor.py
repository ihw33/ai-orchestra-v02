#!/usr/bin/env python3
"""
PM 자동 처리기 (수정 버전) - 단발성 실행
"""

import subprocess
import json
import time
import sys
from typing import Dict, Optional

class PMAutoProcessor:
    """이슈 자동 처리기 - 단발성 실행"""
    
    def __init__(self):
        self.repo = "ihw33/ai-orchestra-v02"
        
    def get_latest_issue(self) -> Optional[Dict]:
        """최신 이슈 가져오기"""
        try:
            cmd = f"gh issue list -R {self.repo} --limit 1 --json number,title,body,labels --state open"
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                issues = json.loads(result.stdout)
                if issues:
                    return issues[0]
        except Exception as e:
            print(f"❌ 이슈 가져오기 실패: {e}")
        
        return None
    
    def process_issue(self, issue: Dict) -> bool:
        """이슈 자동 처리 - [AI] 태그가 있는 것만"""
        issue_number = issue['number']
        title = issue['title']
        body = issue.get('body', '')
        labels = [label.get('name', '') for label in issue.get('labels', [])]
        
        print(f"\n🔍 이슈 #{issue_number} 확인")
        print(f"   제목: {title}")
        
        # AI 작업이 필요한 이슈인지 확인
        if '[AI]' in title or 'ai-task' in labels:
            print(f"   ✅ AI 작업 필요 - 처리 시작")
            
            # 이미 처리됨 표시가 있는지 확인
            if 'ai-processed' in labels:
                print(f"   ⚠️ 이미 처리된 이슈")
                return False
            
            # multi_ai_orchestrator 실행
            try:
                print(f"\n🚀 Multi-AI Orchestrator 실행 중...")
                cmd = f"python3 multi_ai_orchestrator.py {issue_number}"
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=300)
                
                if result.returncode == 0:
                    print(f"✅ 성공적으로 처리됨")
                    
                    # 처리 완료 라벨 추가
                    subprocess.run(
                        f"gh issue edit {issue_number} -R {self.repo} --add-label ai-processed",
                        shell=True
                    )
                    return True
                else:
                    print(f"❌ 처리 실패: {result.stderr}")
                    
                    # 실패 코멘트 추가
                    error_comment = f"❌ 자동 처리 실패:\\n```\\n{result.stderr}\\n```"
                    subprocess.run(
                        f'gh issue comment {issue_number} -R {self.repo} -b "{error_comment}"',
                        shell=True
                    )
                    return False
                    
            except subprocess.TimeoutExpired:
                print(f"⏱️ 시간 초과 (5분)")
                return False
            except Exception as e:
                print(f"❌ 실행 오류: {e}")
                return False
        else:
            print(f"   ℹ️ AI 작업 불필요")
            return False
    
    def process_once(self) -> bool:
        """한 번만 실행 (무한 루프 제거)"""
        print("=" * 60)
        print("🤖 PM Auto Processor - 단발성 실행 모드")
        print("=" * 60)
        
        issue = self.get_latest_issue()
        if issue:
            return self.process_issue(issue)
        else:
            print("📭 처리할 이슈 없음")
            return False
    
    def monitor_mode(self, interval: int = 30):
        """모니터링 모드 (선택적)"""
        print("=" * 60)
        print(f"🔄 PM Auto Processor - 모니터링 모드 ({interval}초 간격)")
        print("=" * 60)
        
        processed_issues = set()
        
        try:
            while True:
                issue = self.get_latest_issue()
                if issue:
                    issue_num = issue['number']
                    if issue_num not in processed_issues:
                        if self.process_issue(issue):
                            processed_issues.add(issue_num)
                
                print(f"\n⏳ {interval}초 대기...")
                time.sleep(interval)
                
        except KeyboardInterrupt:
            print("\n\n👋 모니터링 종료")

def main():
    processor = PMAutoProcessor()
    
    if len(sys.argv) > 1:
        if sys.argv[1] == '--monitor':
            # 모니터링 모드
            interval = int(sys.argv[2]) if len(sys.argv) > 2 else 30
            processor.monitor_mode(interval)
        elif sys.argv[1] == '--help':
            print("""
PM Auto Processor - 사용법

단발성 실행:
  python3 fixed_pm_auto_processor.py
  
모니터링 모드:
  python3 fixed_pm_auto_processor.py --monitor [간격(초)]
  
예시:
  python3 fixed_pm_auto_processor.py              # 한 번만 실행
  python3 fixed_pm_auto_processor.py --monitor    # 30초마다 체크
  python3 fixed_pm_auto_processor.py --monitor 60 # 60초마다 체크
            """)
        else:
            # 특정 이슈 번호 처리
            issue_num = int(sys.argv[1])
            cmd = f"gh issue view {issue_num} -R ihw33/ai-orchestra-v02 --json number,title,body,labels"
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            if result.returncode == 0:
                issue = json.loads(result.stdout)
                processor.process_issue(issue)
    else:
        # 기본: 단발성 실행
        processor.process_once()

if __name__ == "__main__":
    main()