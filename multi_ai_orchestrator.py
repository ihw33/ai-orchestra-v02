#!/usr/bin/env python3
"""
Multi-AI Orchestrator
GitHub Issue → Multiple AIs → Automatic Review → Final Report
"""

import subprocess
import json
import time
from datetime import datetime
from typing import Dict, List, Any
import os

class MultiAIOrchestrator:
    def __init__(self):
        self.ais = {
            "gemini": {
                "cmd": "gemini -p",
                "role": "아키텍처 설계 & 코드 리뷰"
            },
            "claude": {
                "cmd": "claude -p",  
                "role": "구현 & 최적화"
            },
            "codex": {
                "cmd": "codex -p",
                "role": "코드 생성 & 리팩토링"
            }
        }
        
    def process_github_issue(self, issue_number: int, repo: str = "ihw33/ai-orchestra-v02"):
        """GitHub 이슈를 읽고 여러 AI에게 동시에 작업 지시"""
        
        # 1. 이슈 내용 가져오기
        print(f"📋 Issue #{issue_number} 처리 시작...")
        issue_body = self._get_issue_body(issue_number, repo)
        
        # 2. 각 AI에게 동시에 작업 지시 (병렬 처리)
        results = {}
        processes = {}
        
        for ai_name, ai_config in self.ais.items():
            prompt = self._create_ai_prompt(ai_name, ai_config["role"], issue_body)
            print(f"🤖 {ai_name.upper()} 작업 시작...")
            
            # 백그라운드로 실행
            process = subprocess.Popen(
                f'{ai_config["cmd"]} "{prompt}"',
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            processes[ai_name] = process
        
        # 3. 모든 AI 응답 수집
        for ai_name, process in processes.items():
            stdout, stderr = process.communicate()
            results[ai_name] = {
                "output": stdout.strip(),
                "error": stderr.strip() if stderr else None,
                "timestamp": datetime.now().isoformat()
            }
            print(f"✅ {ai_name.upper()} 완료")
        
        # 4. 결과를 GitHub 이슈에 코멘트로 추가
        self._post_results_to_issue(issue_number, repo, results)
        
        # 5. 전체 리뷰 요청 (다른 AI에게)
        review = self._request_final_review(results)
        
        # 6. 최종 리뷰도 이슈에 추가
        self._post_review_to_issue(issue_number, repo, review)
        
        return results, review
    
    def _get_issue_body(self, issue_number: int, repo: str) -> str:
        """GitHub 이슈 내용 가져오기"""
        cmd = f"gh issue view {issue_number} -R {repo} --json body -q .body"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        return result.stdout.strip()
    
    def _create_ai_prompt(self, ai_name: str, role: str, issue_body: str) -> str:
        """각 AI용 프롬프트 생성"""
        return f"""당신은 {ai_name}입니다.
역할: {role}

다음 이슈를 분석하고 해결책을 제시하세요:
{issue_body}

응답 형식:
1. 문제 분석
2. 해결 방안
3. 구현 코드 (있다면)
4. 추가 제안사항"""
    
    def _post_results_to_issue(self, issue_number: int, repo: str, results: Dict):
        """AI 응답들을 이슈 코멘트로 추가"""
        comment = "## 🤖 Multi-AI Analysis Results\\n\\n"
        
        for ai_name, result in results.items():
            comment += f"### {ai_name.upper()} ({self.ais[ai_name]['role']})\\n"
            comment += f"```\\n{result['output'][:1000]}...\\n```\\n"
            comment += f"*Completed at: {result['timestamp']}*\\n\\n"
        
        # GitHub CLI로 코멘트 추가
        cmd = f'gh issue comment {issue_number} -R {repo} -b "{comment}"'
        subprocess.run(cmd, shell=True)
        print(f"💬 Issue #{issue_number}에 AI 응답 추가 완료")
    
    def _request_final_review(self, results: Dict) -> str:
        """전체 결과를 다른 AI에게 리뷰 요청"""
        review_prompt = f"""다음은 여러 AI의 분석 결과입니다. 
전체적인 리뷰와 최종 권장사항을 제시해주세요:

{json.dumps(results, indent=2, ensure_ascii=False)}

리뷰 포인트:
1. 각 AI 제안의 장단점
2. 통합 솔루션 제안
3. 우선순위 권장사항"""
        
        # Claude에게 최종 리뷰 요청
        process = subprocess.Popen(
            f'claude -p "{review_prompt}"',
            shell=True,
            stdout=subprocess.PIPE,
            text=True
        )
        review, _ = process.communicate()
        return review.strip()
    
    def _post_review_to_issue(self, issue_number: int, repo: str, review: str):
        """최종 리뷰를 이슈에 추가"""
        comment = f"""## 🎯 Final Review by Claude

{review}

---
*Automated by Multi-AI Orchestrator*"""
        
        cmd = f'gh issue comment {issue_number} -R {repo} -b "{comment}"'
        subprocess.run(cmd, shell=True)
        print(f"📝 최종 리뷰 추가 완료")

class AutomatedWorkflow:
    """GitHub Webhook과 연동되는 자동 워크플로우"""
    
    def __init__(self):
        self.orchestrator = MultiAIOrchestrator()
        self.watch_labels = ["ai-review", "multi-ai", "needs-analysis"]
    
    def watch_issues(self, repo: str = "ihw33/ai-orchestra-v02"):
        """특정 라벨이 붙은 이슈 자동 처리"""
        while True:
            # 라벨이 붙은 이슈 확인
            for label in self.watch_labels:
                cmd = f"gh issue list -R {repo} -l {label} --json number,state -q '.[] | select(.state==\"OPEN\") | .number'"
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                
                if result.stdout:
                    issue_numbers = result.stdout.strip().split('\n')
                    for issue_num in issue_numbers:
                        if issue_num:
                            print(f"🎯 Processing Issue #{issue_num} with label '{label}'")
                            self.orchestrator.process_github_issue(int(issue_num), repo)
                            
                            # 처리 완료 라벨 추가
                            subprocess.run(
                                f"gh issue edit {issue_num} -R {repo} --add-label ai-processed",
                                shell=True
                            )
            
            # 30초마다 체크
            time.sleep(30)
    
    def handle_webhook(self, payload: dict):
        """GitHub Webhook 이벤트 처리"""
        if payload.get("action") == "labeled":
            label = payload["label"]["name"]
            if label in self.watch_labels:
                issue_number = payload["issue"]["number"]
                repo = payload["repository"]["full_name"]
                
                print(f"🔔 Webhook: Issue #{issue_number} labeled with '{label}'")
                self.orchestrator.process_github_issue(issue_number, repo)

# CLI 실행
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "watch":
            # 자동 감시 모드
            workflow = AutomatedWorkflow()
            print("👀 Watching for issues with AI labels...")
            workflow.watch_issues()
        elif sys.argv[1].isdigit():
            # 특정 이슈 처리
            orchestrator = MultiAIOrchestrator()
            orchestrator.process_github_issue(int(sys.argv[1]))
    else:
        print("""
Multi-AI Orchestrator
Usage:
  python multi_ai_orchestrator.py <issue_number>  # 특정 이슈 처리
  python multi_ai_orchestrator.py watch           # 자동 감시 모드
        """)