#!/usr/bin/env python3
"""
Progress Reporting Node
작업 진행 상황을 실시간으로 이슈에 보고
"""

import asyncio
import json
from typing import Dict, List, Optional
from datetime import datetime
from enum import Enum

class TaskStatus(Enum):
    PENDING = "⏳ Pending"
    IN_PROGRESS = "🔄 In Progress"
    COMPLETED = "✅ Completed"
    FAILED = "❌ Failed"
    BLOCKED = "🚫 Blocked"

class ProgressReportingNode:
    """
    작업 진행 상황을 GitHub 이슈에 실시간 보고
    """
    
    def __init__(self):
        self.name = "ProgressReporting"
        self.description = "작업 진행 상황 실시간 보고"
        self.current_tasks = {}
        
    async def execute(self, context: Dict) -> Dict:
        """
        진행 상황 보고 실행
        
        Args:
            context: {
                "issue_number": str,
                "task_name": str,
                "status": str (pending|in_progress|completed|failed|blocked),
                "details": str (optional),
                "checklist": List[Dict] (optional),
                "ai_agent": str (optional: gemini|claude|codex)
            }
        """
        issue_number = context.get("issue_number")
        task_name = context.get("task_name")
        status = context.get("status", "pending")
        details = context.get("details", "")
        checklist = context.get("checklist", [])
        ai_agent = context.get("ai_agent", "system")
        
        if not issue_number or not task_name:
            return {"error": "Issue number and task name required"}
        
        # 상태 업데이트
        self.current_tasks[task_name] = {
            "status": status,
            "updated_at": datetime.now().isoformat(),
            "ai_agent": ai_agent
        }
        
        # 진행 상황 보고 생성
        report = await self.generate_progress_report(
            task_name, status, details, checklist, ai_agent
        )
        
        # 이슈에 코멘트 추가
        await self.post_progress_comment(issue_number, report)
        
        # 작업 완료 시 요약 보고서 생성
        if status == "completed":
            summary = await self.generate_completion_summary(issue_number)
            if summary:
                await self.post_progress_comment(issue_number, summary)
        
        return {
            "reported": True,
            "task": task_name,
            "status": status,
            "timestamp": datetime.now().isoformat()
        }
    
    async def generate_progress_report(self, 
                                      task_name: str,
                                      status: str,
                                      details: str,
                                      checklist: List[Dict],
                                      ai_agent: str) -> str:
        """
        진행 상황 보고서 생성
        """
        # 상태별 이모지 매핑
        status_emoji = {
            "pending": "⏳",
            "in_progress": "🔄",
            "completed": "✅",
            "failed": "❌",
            "blocked": "🚫"
        }
        
        emoji = status_emoji.get(status, "📝")
        
        # AI 에이전트별 아이콘
        agent_icons = {
            "gemini": "🔷",
            "claude": "🔵",
            "codex": "🔶",
            "system": "⚙️"
        }
        
        agent_icon = agent_icons.get(ai_agent, "🤖")
        
        # 보고서 생성
        lines = [
            f"## {emoji} Progress Update: {task_name}",
            f"",
            f"**Status**: {status.replace('_', ' ').title()}",
            f"**Agent**: {agent_icon} {ai_agent.capitalize()}",
            f"**Time**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        ]
        
        if details:
            lines.extend([
                "",
                "**Details**:",
                f"{details}"
            ])
        
        if checklist:
            lines.extend([
                "",
                "**Checklist**:"
            ])
            for item in checklist:
                check = "✅" if item.get("done") else "⬜"
                lines.append(f"- {check} {item.get('task', '')}")
        
        # 다음 단계 안내 (상태별)
        if status == "in_progress":
            lines.extend([
                "",
                "🚀 **Currently working on this task...**"
            ])
        elif status == "completed":
            lines.extend([
                "",
                "🎉 **Task completed successfully!**"
            ])
        elif status == "failed":
            lines.extend([
                "",
                "⚠️ **Task failed. Review required.**"
            ])
        elif status == "blocked":
            lines.extend([
                "",
                "🔴 **Task is blocked. Intervention needed.**"
            ])
        
        return "\n".join(lines)
    
    async def generate_completion_summary(self, issue_number: str) -> Optional[str]:
        """
        모든 작업 완료 시 요약 보고서 생성
        """
        # 모든 작업이 완료되었는지 확인
        all_completed = all(
            task["status"] == "completed" 
            for task in self.current_tasks.values()
        )
        
        if not all_completed:
            return None
        
        lines = [
            "## 🎊 All Tasks Completed!",
            "",
            "### Summary of completed tasks:"
        ]
        
        for task_name, task_info in self.current_tasks.items():
            agent = task_info.get("ai_agent", "system")
            lines.append(f"- ✅ **{task_name}** (by {agent})")
        
        lines.extend([
            "",
            "### Next Steps:",
            "1. Review the implementation",
            "2. Run tests to verify",
            "3. Create PR if all tests pass",
            "",
            f"_Completed at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}_"
        ])
        
        return "\n".join(lines)
    
    async def post_progress_comment(self, issue_number: str, comment: str):
        """
        GitHub 이슈에 진행 상황 코멘트 게시
        """
        # 특수문자 이스케이프
        escaped_comment = comment.replace('"', '\\"').replace('\n', '\\n')
        
        cmd = f'gh issue comment {issue_number} --body "{escaped_comment}"'
        
        try:
            process = await asyncio.create_subprocess_shell(
                cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await process.communicate()
            
            if process.returncode == 0:
                print(f"✅ Progress reported to issue #{issue_number}")
            else:
                print(f"❌ Failed to report: {stderr.decode()}")
                
        except Exception as e:
            print(f"❌ Error posting comment: {e}")
    
    async def update_issue_checklist(self, issue_number: str, checklist: List[Dict]):
        """
        이슈 본문의 체크리스트 업데이트
        """
        # 이슈 본문 가져오기
        get_body_cmd = f"gh issue view {issue_number} --json body -q .body"
        
        process = await asyncio.create_subprocess_shell(
            get_body_cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, _ = await process.communicate()
        
        current_body = stdout.decode()
        
        # 체크리스트 업데이트
        for item in checklist:
            task_name = item.get("task", "")
            is_done = item.get("done", False)
            
            if is_done:
                # 미완료를 완료로
                current_body = current_body.replace(f"- [ ] {task_name}", f"- [x] {task_name}")
            else:
                # 완료를 미완료로 (필요시)
                current_body = current_body.replace(f"- [x] {task_name}", f"- [ ] {task_name}")
        
        # 이슈 업데이트
        update_cmd = f'gh issue edit {issue_number} --body "{current_body}"'
        await asyncio.create_subprocess_shell(update_cmd)


# 통합 진행 상황 관리자
class IntegratedProgressManager:
    """
    여러 AI 에이전트의 진행 상황을 통합 관리
    """
    
    def __init__(self):
        self.reporter = ProgressReportingNode()
        self.agents_status = {}
        
    async def track_ai_progress(self, issue_number: str):
        """
        AI 에이전트들의 진행 상황 추적
        """
        agents = ["gemini", "claude", "codex"]
        
        # 초기 상태 보고
        for agent in agents:
            await self.reporter.execute({
                "issue_number": issue_number,
                "task_name": f"{agent}_task",
                "status": "pending",
                "ai_agent": agent,
                "details": f"Waiting for {agent} to start..."
            })
        
        # 진행 상황 시뮬레이션 (실제로는 AI 에이전트가 직접 보고)
        await asyncio.sleep(2)
        
        # Gemini 시작
        await self.reporter.execute({
            "issue_number": issue_number,
            "task_name": "gemini_task",
            "status": "in_progress",
            "ai_agent": "gemini",
            "details": "Analyzing architecture and creating design..."
        })
        
        # Claude 시작
        await self.reporter.execute({
            "issue_number": issue_number,
            "task_name": "claude_task",
            "status": "in_progress",
            "ai_agent": "claude",
            "details": "Implementing core features..."
        })


# 테스트 실행
if __name__ == "__main__":
    async def test():
        reporter = ProgressReportingNode()
        
        # 작업 시작 보고
        await reporter.execute({
            "issue_number": "99",
            "task_name": "Database Migration",
            "status": "in_progress",
            "details": "Migrating from Redis to PostgreSQL",
            "checklist": [
                {"task": "Create PostgreSQL schema", "done": True},
                {"task": "Migrate data", "done": False},
                {"task": "Update connection strings", "done": False}
            ],
            "ai_agent": "codex"
        })
        
        await asyncio.sleep(2)
        
        # 작업 완료 보고
        await reporter.execute({
            "issue_number": "99",
            "task_name": "Database Migration",
            "status": "completed",
            "details": "Successfully migrated all data",
            "ai_agent": "codex"
        })
    
    asyncio.run(test())