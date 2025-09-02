"""
GitHub Reporter Adapter
GitHub Issue 댓글로 보고하는 Adapter 구현
"""

import subprocess
import json
from typing import Dict, List, Optional, Any
from datetime import datetime
import sys
import os

# Port 인터페이스 import
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from ports.reporter_port import (
    ReporterPort, 
    ReportFormatterPort,
    Report, 
    ReportResult, 
    ReportType
)

class GitHubReporterAdapter(ReporterPort):
    """GitHub Issue 댓글 보고 Adapter"""
    
    def __init__(self, repo: str = "ihw33/ai-orchestra-v02"):
        self.repo = repo
        self.formatter = GitHubMarkdownFormatter()
    
    def report_progress(self, target_id: str, progress: Dict) -> ReportResult:
        """진행 상황을 GitHub 댓글로 보고"""
        
        # 보고서 생성
        report = Report(
            id=f"progress_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            type=ReportType.PROGRESS,
            target_id=target_id,
            title="진행 상황 보고",
            content=self.formatter.format_progress(progress),
            metadata=progress
        )
        
        # GitHub에 포스팅
        return self._post_to_github(target_id, report)
    
    def report_completion(self, target_id: str, results: Dict) -> ReportResult:
        """완료 보고를 GitHub 댓글로 포스팅"""
        
        report = Report(
            id=f"completion_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            type=ReportType.COMPLETION,
            target_id=target_id,
            title="작업 완료 보고",
            content=self.formatter.format_completion(results),
            metadata=results
        )
        
        return self._post_to_github(target_id, report)
    
    def report_error(self, target_id: str, error: Dict) -> ReportResult:
        """에러를 GitHub 댓글로 보고"""
        
        report = Report(
            id=f"error_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            type=ReportType.ERROR,
            target_id=target_id,
            title="에러 보고",
            content=self.formatter.format_error(error),
            metadata=error
        )
        
        return self._post_to_github(target_id, report)
    
    def generate_summary(self, target_id: str, data: Dict) -> Report:
        """요약 보고서 생성"""
        
        # 데이터 분석
        completed_tasks = data.get('completed', [])
        pending_tasks = data.get('pending', [])
        errors = data.get('errors', [])
        
        # 요약 생성
        summary_content = f"""
## 📊 작업 요약

### 완료된 작업 ({len(completed_tasks)}개)
{self._format_task_list(completed_tasks)}

### 대기 중 작업 ({len(pending_tasks)}개)
{self._format_task_list(pending_tasks)}

### 발생한 에러 ({len(errors)}개)
{self._format_error_list(errors)}

### 통계
- 전체 진행률: {data.get('progress', 0)}%
- 소요 시간: {data.get('duration', 'N/A')}
"""
        
        return Report(
            id=f"summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            type=ReportType.SUMMARY,
            target_id=target_id,
            title="작업 요약",
            content=summary_content,
            metadata=data
        )
    
    def should_report(self, event_type: str, context: Dict) -> bool:
        """보고 필요 여부 판단"""
        
        # 보고 규칙
        report_rules = {
            'task_completed': True,
            'milestone_reached': True,
            'error_occurred': True,
            'progress_update': context.get('progress', 0) % 25 == 0,  # 25% 단위
            'ai_execution': True,
            'escalation': True
        }
        
        return report_rules.get(event_type, False)
    
    def _post_to_github(self, issue_number: str, report: Report) -> ReportResult:
        """GitHub에 실제 포스팅"""
        
        # 댓글 내용 준비
        comment = f"## {report.title}\n\n{report.content}"
        
        # Provenance 추가
        comment += f"\n\n---\n*Report ID: {report.id} | "
        comment += f"Type: {report.type.value} | "
        comment += f"Time: {report.timestamp.strftime('%Y-%m-%d %H:%M:%S')}*"
        
        # GitHub CLI로 포스팅
        try:
            # 임시 파일을 사용하여 multi-line 텍스트 전달
            import tempfile
            with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
                f.write(comment)
                temp_file = f.name
            
            cmd = f'gh issue comment {issue_number} -R {self.repo} --body-file {temp_file}'
            
            result = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                text=True,
                timeout=10
            )
            
            # 임시 파일 삭제
            import os
            os.remove(temp_file)
            
            if result.returncode == 0:
                # URL 추출 (stdout에서)
                url = result.stdout.strip() if result.stdout else None
                
                return ReportResult(
                    success=True,
                    report_id=report.id,
                    url=url
                )
            else:
                return ReportResult(
                    success=False,
                    report_id=report.id,
                    errors=[result.stderr]
                )
                
        except Exception as e:
            return ReportResult(
                success=False,
                report_id=report.id,
                errors=[str(e)]
            )
    
    def _format_task_list(self, tasks: List) -> str:
        """작업 목록 포맷팅"""
        if not tasks:
            return "- 없음"
        return "\n".join([f"- ✅ {task}" for task in tasks])
    
    def _format_error_list(self, errors: List) -> str:
        """에러 목록 포맷팅"""
        if not errors:
            return "- 없음"
        return "\n".join([f"- ❌ {error}" for error in errors])


class GitHubMarkdownFormatter(ReportFormatterPort):
    """GitHub Markdown 포맷터"""
    
    def format_progress(self, data: Dict) -> str:
        """진행 상황 Markdown 포맷팅"""
        
        content = "### 🔄 진행 상황\n\n"
        
        # 현재 작업
        if 'current_task' in data:
            content += f"**현재 작업**: {data['current_task']}\n\n"
        
        # 진행률
        if 'progress' in data:
            progress = data['progress']
            bar = self._create_progress_bar(progress)
            content += f"**진행률**: {bar} {progress}%\n\n"
        
        # 상세 내용
        if 'details' in data:
            content += "**상세 내용**:\n"
            for key, value in data['details'].items():
                content += f"- {key}: {value}\n"
        
        return content
    
    def format_completion(self, data: Dict) -> str:
        """완료 보고 Markdown 포맷팅"""
        
        content = "### ✅ 작업 완료\n\n"
        
        # 완료된 작업들
        if 'completed_tasks' in data:
            content += "**완료된 작업**:\n"
            for task in data['completed_tasks']:
                content += f"- ✅ {task}\n"
            content += "\n"
        
        # 생성된 파일들
        if 'created_files' in data:
            content += "**생성/수정된 파일**:\n"
            for file in data['created_files']:
                content += f"- `{file}`\n"
            content += "\n"
        
        # 테스트 결과
        if 'test_results' in data:
            content += "**테스트 결과**:\n"
            content += f"```\n{data['test_results']}\n```\n\n"
        
        # 다음 단계
        if 'next_steps' in data:
            content += "**다음 단계**:\n"
            for step in data['next_steps']:
                content += f"- {step}\n"
        
        return content
    
    def format_error(self, data: Dict) -> str:
        """에러 보고 Markdown 포맷팅"""
        
        content = "### ❌ 에러 발생\n\n"
        
        # 에러 메시지
        if 'error_message' in data:
            content += f"**에러**: {data['error_message']}\n\n"
        
        # 스택 트레이스
        if 'stack_trace' in data:
            content += "**스택 트레이스**:\n"
            content += f"```\n{data['stack_trace']}\n```\n\n"
        
        # 해결 시도
        if 'attempted_solutions' in data:
            content += "**시도한 해결 방법**:\n"
            for solution in data['attempted_solutions']:
                content += f"- {solution}\n"
            content += "\n"
        
        # 에스컬레이션 필요
        if data.get('needs_escalation', False):
            content += "⚠️ **에스컬레이션 필요**: PM 검토 요청\n"
        
        return content
    
    def _create_progress_bar(self, progress: int) -> str:
        """진행률 바 생성"""
        filled = int(progress / 10)
        empty = 10 - filled
        return "█" * filled + "░" * empty


# 사용 예시
if __name__ == "__main__":
    reporter = GitHubReporterAdapter()
    
    # 진행 상황 보고
    progress_data = {
        'current_task': 'Golden Set 시스템 구현',
        'progress': 75,
        'details': {
            'Port 정의': '완료',
            'Adapter 구현': '진행 중',
            '테스트': '대기'
        }
    }
    
    result = reporter.report_progress("82", progress_data)
    print(f"보고 결과: {result.success}")
    if result.url:
        print(f"URL: {result.url}")