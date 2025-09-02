#!/usr/bin/env python3
"""
Relay Pipeline System (수정 버전) - 순차 실행 + GitHub 업데이트
"""

import sys
import subprocess
import json
import time
from typing import Dict, List, Optional
from datetime import datetime

class RelayPipeline:
    """순차적 AI 실행 파이프라인"""
    
    def __init__(self):
        self.repo = "ihw33/ai-orchestra-v02"
        self.results = []
        
    def get_issue_content(self, issue_number: int) -> Optional[Dict]:
        """GitHub 이슈 내용 가져오기"""
        try:
            cmd = f"gh issue view {issue_number} -R {self.repo} --json title,body,labels"
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                return json.loads(result.stdout)
        except Exception as e:
            print(f"❌ 이슈 로드 실패: {e}")
        return None
    
    def execute_ai(self, ai_name: str, prompt: str, context: str = "") -> Dict:
        """AI 실행 및 결과 반환"""
        full_prompt = f"{context}\n\n{prompt}" if context else prompt
        
        print(f"\n🤖 {ai_name.upper()} 실행 중...")
        
        # AI별 명령어 매핑
        commands = {
            'gemini': f'gemini -p "{full_prompt}"',
            'claude': f'claude -p "{full_prompt}"',
            'codex': f'codex exec "{full_prompt}"'
        }
        
        if ai_name not in commands:
            return {"ai": ai_name, "output": "지원하지 않는 AI", "success": False}
        
        try:
            result = subprocess.run(
                commands[ai_name],
                shell=True,
                capture_output=True,
                text=True,
                timeout=120
            )
            
            if result.returncode == 0:
                print(f"✅ {ai_name} 완료")
                return {
                    "ai": ai_name,
                    "output": result.stdout,
                    "success": True,
                    "timestamp": datetime.now().isoformat()
                }
            else:
                print(f"❌ {ai_name} 실패: {result.stderr}")
                return {
                    "ai": ai_name,
                    "output": result.stderr,
                    "success": False,
                    "timestamp": datetime.now().isoformat()
                }
        except subprocess.TimeoutExpired:
            print(f"⏱️ {ai_name} 시간 초과")
            return {
                "ai": ai_name,
                "output": "실행 시간 초과 (2분)",
                "success": False,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            print(f"❌ {ai_name} 오류: {e}")
            return {
                "ai": ai_name,
                "output": str(e),
                "success": False,
                "timestamp": datetime.now().isoformat()
            }
    
    def update_github_issue(self, issue_number: int, results: List[Dict]):
        """결과를 GitHub 이슈에 업데이트"""
        print(f"\n📝 GitHub 이슈 #{issue_number} 업데이트 중...")
        
        # 결과 포맷팅
        comment = "## 🔄 Relay Pipeline 실행 결과\\n\\n"
        comment += f"실행 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\\n\\n"
        
        for i, result in enumerate(results, 1):
            status = "✅" if result['success'] else "❌"
            comment += f"### {i}. {result['ai'].upper()} {status}\\n"
            comment += "```\\n"
            comment += result['output'][:1000]  # 최대 1000자
            if len(result['output']) > 1000:
                comment += "\\n... (출력 생략) ..."
            comment += "\\n```\\n\\n"
        
        # 전체 성공/실패 판단
        success_count = sum(1 for r in results if r['success'])
        total_count = len(results)
        
        if success_count == total_count:
            comment += "### ✅ 모든 작업 완료\\n"
        else:
            comment += f"### ⚠️ 부분 완료 ({success_count}/{total_count})\\n"
        
        # GitHub에 코멘트 추가
        try:
            # 이스케이프 처리
            comment_escaped = comment.replace('"', '\\"').replace('\n', '\\n')
            cmd = f'gh issue comment {issue_number} -R {self.repo} -b "{comment_escaped}"'
            
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            
            if result.returncode == 0:
                print("✅ GitHub 업데이트 완료")
                return True
            else:
                print(f"❌ GitHub 업데이트 실패: {result.stderr}")
                return False
        except Exception as e:
            print(f"❌ 업데이트 오류: {e}")
            return False
    
    def run_pipeline(self, issue_number: int, ai_sequence: List[str] = None):
        """파이프라인 실행"""
        print("=" * 60)
        print(f"🚀 Relay Pipeline - 이슈 #{issue_number}")
        print("=" * 60)
        
        # 이슈 내용 가져오기
        issue = self.get_issue_content(issue_number)
        if not issue:
            print("❌ 이슈를 찾을 수 없습니다")
            return False
        
        print(f"\n📋 이슈: {issue['title']}")
        
        # 기본 AI 순서
        if not ai_sequence:
            ai_sequence = ['gemini', 'claude', 'codex']
        
        # 순차 실행
        context = ""
        results = []
        
        for ai_name in ai_sequence:
            # 이전 결과를 컨텍스트로 전달
            if results:
                last_result = results[-1]
                if last_result['success']:
                    context = f"이전 {last_result['ai']}의 분석:\\n{last_result['output'][:500]}"
            
            # AI 실행
            prompt = f"이슈 #{issue_number}: {issue['title']}\\n\\n{issue.get('body', '')}"
            result = self.execute_ai(ai_name, prompt, context)
            results.append(result)
            
            # 실패 시 중단 옵션 (현재는 계속 진행)
            # if not result['success']:
            #     break
        
        # GitHub 업데이트
        self.update_github_issue(issue_number, results)
        
        # 완료 라벨 추가
        if all(r['success'] for r in results):
            subprocess.run(
                f"gh issue edit {issue_number} -R {self.repo} --add-label relay-completed",
                shell=True
            )
        
        return True

def print_help():
    """도움말 출력"""
    print("""
Relay Pipeline System - 순차 AI 실행

사용법:
  python3 fixed_relay_pipeline.py <이슈번호>
  python3 fixed_relay_pipeline.py --help
  
예시:
  python3 fixed_relay_pipeline.py 63
  
옵션:
  --help    이 도움말 표시
  
설명:
  지정된 GitHub 이슈를 여러 AI가 순차적으로 처리합니다.
  각 AI는 이전 AI의 결과를 참고하여 작업합니다.
  모든 결과는 GitHub 이슈에 코멘트로 기록됩니다.
    """)

def main():
    if len(sys.argv) < 2:
        print("❌ 사용법: python3 fixed_relay_pipeline.py <이슈번호>")
        print("   도움말: python3 fixed_relay_pipeline.py --help")
        sys.exit(1)
    
    if sys.argv[1] == '--help':
        print_help()
        sys.exit(0)
    
    try:
        issue_number = int(sys.argv[1])
        pipeline = RelayPipeline()
        pipeline.run_pipeline(issue_number)
    except ValueError:
        print(f"❌ 올바른 이슈 번호가 아닙니다: {sys.argv[1]}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ 실행 오류: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()