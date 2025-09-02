"""
PM Processor Adapter - PM 자동 처리 어댑터
"""

import subprocess
import json
from typing import Dict, Optional, List
from datetime import datetime
import logging

from src.ports.pm_processor_port import (
    PMProcessorPort, Issue, ProcessingResult
)
from src.adapters.ai.transparent_reporting_adapter import TransparentReportingAdapter
from src.adapters.github.github_reporter_adapter import GitHubReporterAdapter


logger = logging.getLogger(__name__)


class PMProcessorAdapter(PMProcessorPort):
    """PM 프로세서 어댑터 구현"""
    
    def __init__(self, repo: str = "ihw33/ai-orchestra-v02"):
        self.repo = repo
        self.ai_adapter = TransparentReportingAdapter()
        self.github_adapter = GitHubReporterAdapter(repo)
        
    def get_latest_issues(self, limit: int = 1) -> List[Issue]:
        """GitHub에서 최신 이슈 가져오기"""
        try:
            cmd = f"gh issue list -R {self.repo} --limit {limit} --json number,title,body,labels,state,createdAt,assignees --state open"
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                issues_data = json.loads(result.stdout)
                issues = []
                
                for data in issues_data:
                    issue = Issue(
                        number=data['number'],
                        title=data['title'],
                        body=data.get('body', ''),
                        labels=[label.get('name', '') for label in data.get('labels', [])],
                        state=data['state'],
                        created_at=datetime.fromisoformat(data['createdAt'].replace('Z', '+00:00')),
                        assignees=[a.get('login', '') for a in data.get('assignees', [])]
                    )
                    issues.append(issue)
                
                return issues
                
        except Exception as e:
            logger.error(f"이슈 가져오기 실패: {e}")
            return []
    
    def process_issue(self, issue: Issue) -> ProcessingResult:
        """이슈 처리 - AI 태스크 실행"""
        
        # 이미 처리된 이슈는 건너뛰기
        if issue.is_processed:
            return ProcessingResult(
                success=False,
                issue_number=issue.number,
                message="이미 처리된 이슈입니다",
                error="Already processed"
            )
        
        # AI가 필요하지 않은 이슈는 건너뛰기
        if not issue.needs_ai:
            return ProcessingResult(
                success=False,
                issue_number=issue.number,
                message="AI 처리가 필요하지 않은 이슈입니다",
                error="No AI needed"
            )
        
        try:
            # AI 실행
            ai_responses = {}
            task_description = f"Issue #{issue.number}: {issue.title}\\n{issue.body}"
            
            # 각 AI에게 작업 할당
            ai_configs = [
                {"name": "gemini", "profile": "architect"},
                {"name": "claude", "profile": "developer"},
                {"name": "codex", "profile": "backend"}
            ]
            
            for config in ai_configs:
                response = self.ai_adapter.execute_with_reporting(
                    ai_name=config['name'],
                    task=task_description,
                    profile=config.get('profile')
                )
                ai_responses[config['name']] = response
            
            # 결과를 GitHub에 기록
            comment = self._format_ai_responses(ai_responses)
            self.post_comment(issue.number, comment)
            
            # 처리 완료 표시
            self.mark_as_processed(issue.number)
            
            return ProcessingResult(
                success=True,
                issue_number=issue.number,
                message="AI 처리 완료",
                ai_responses=ai_responses
            )
            
        except Exception as e:
            logger.error(f"이슈 처리 실패: {e}")
            return ProcessingResult(
                success=False,
                issue_number=issue.number,
                message=f"처리 중 오류 발생: {str(e)}",
                error=str(e)
            )
    
    def mark_as_processed(self, issue_number: int) -> bool:
        """이슈에 처리됨 라벨 추가"""
        try:
            cmd = f"gh issue edit {issue_number} -R {self.repo} --add-label 'ai-processed'"
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
            return result.returncode == 0
        except Exception as e:
            logger.error(f"라벨 추가 실패: {e}")
            return False
    
    def post_comment(self, issue_number: int, comment: str) -> bool:
        """이슈에 코멘트 추가"""
        try:
            cmd = f"gh issue comment {issue_number} -R {self.repo} --body '{comment}'"
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
            return result.returncode == 0
        except Exception as e:
            logger.error(f"코멘트 추가 실패: {e}")
            return False
    
    def _format_ai_responses(self, responses: Dict[str, str]) -> str:
        """AI 응답 포맷팅"""
        comment = "## 🤖 AI 처리 결과\\n\\n"
        
        for ai_name, response in responses.items():
            comment += f"### {ai_name.capitalize()}\\n"
            comment += f"{response}\\n\\n"
        
        comment += f"---\\n_처리 시간: {datetime.now().isoformat()}_"
        return comment