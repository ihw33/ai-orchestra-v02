#!/usr/bin/env python3
"""
Cross-Link Issues Node
관련 이슈 간 자동 교차 링크 생성
"""

import asyncio
import json
import re
from typing import List, Dict, Optional
from datetime import datetime

class CrossLinkIssuesNode:
    """
    새로운 이슈와 관련 이슈들을 자동으로 교차 링크
    """
    
    def __init__(self):
        self.name = "CrossLinkIssues"
        self.description = "관련 이슈 자동 연결"
        
    async def execute(self, context: Dict) -> Dict:
        """
        이슈 교차 링크 실행
        
        Args:
            context: {
                "new_issue_id": str,
                "issue_body": str,
                "repo": str (default: "ihw33/ai-orchestra-v02")
            }
        """
        new_issue_id = context.get("new_issue_id")
        issue_body = context.get("issue_body", "")
        repo = context.get("repo", "ihw33/ai-orchestra-v02")
        
        if not new_issue_id:
            return {"error": "No issue ID provided"}
        
        # 이슈 본문에서 관련 이슈 추출
        related_issues = self.extract_related_issues(issue_body)
        
        if not related_issues:
            return {"message": "No related issues found", "linked": 0}
        
        # 교차 링크 생성
        linked_count = 0
        for issue_type, issue_ids in related_issues.items():
            for issue_id in issue_ids:
                await self.create_cross_link(
                    new_issue_id, 
                    issue_id, 
                    issue_type,
                    repo
                )
                linked_count += 1
        
        return {
            "linked_issues": linked_count,
            "details": related_issues,
            "timestamp": datetime.now().isoformat()
        }
    
    def extract_related_issues(self, issue_body: str) -> Dict[str, List[str]]:
        """
        이슈 본문에서 관련 이슈 번호 추출
        
        패턴:
        - Parent Issue: #34
        - Related: #13, #31, #32
        - Blocks: #45
        - Blocked by: #46
        """
        related = {
            "parent": [],
            "related": [],
            "blocks": [],
            "blocked_by": []
        }
        
        # Parent Issue 추출
        parent_match = re.search(r'Parent Issue:\s*#(\d+)', issue_body, re.IGNORECASE)
        if parent_match:
            related["parent"].append(parent_match.group(1))
        
        # Related 추출
        related_match = re.search(r'Related:\s*((?:#\d+(?:\s*,\s*)?)+)', issue_body, re.IGNORECASE)
        if related_match:
            related["related"] = re.findall(r'#(\d+)', related_match.group(1))
        
        # Blocks 추출
        blocks_match = re.search(r'Blocks:\s*((?:#\d+(?:\s*,\s*)?)+)', issue_body, re.IGNORECASE)
        if blocks_match:
            related["blocks"] = re.findall(r'#(\d+)', blocks_match.group(1))
        
        # Blocked by 추출
        blocked_match = re.search(r'Blocked by:\s*((?:#\d+(?:\s*,\s*)?)+)', issue_body, re.IGNORECASE)
        if blocked_match:
            related["blocked_by"] = re.findall(r'#(\d+)', blocked_match.group(1))
        
        return related
    
    async def create_cross_link(self, 
                                new_issue: str, 
                                target_issue: str, 
                                link_type: str,
                                repo: str):
        """
        두 이슈 간 교차 링크 생성
        """
        # 링크 타입별 이모지와 텍스트
        link_templates = {
            "parent": "📎 Child issue: #{new}",
            "related": "🔗 Related: #{new}",
            "blocks": "🚫 Blocked by: #{new}",
            "blocked_by": "⏳ Blocks: #{new}"
        }
        
        # 대상 이슈에 코멘트 추가
        template = link_templates.get(link_type, "🔗 Related: #{new}")
        comment = template.format(new=new_issue)
        
        cmd = f'gh issue comment {target_issue} -R {repo} --body "{comment}"'
        
        try:
            process = await asyncio.create_subprocess_shell(
                cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await process.communicate()
            
            if process.returncode == 0:
                print(f"✅ Linked #{new_issue} to #{target_issue} ({link_type})")
            else:
                print(f"❌ Failed to link: {stderr.decode()}")
                
        except Exception as e:
            print(f"❌ Error creating cross-link: {e}")
    
    async def add_summary_comment(self, issue_id: str, related: Dict, repo: str):
        """
        새 이슈에 관련 이슈 요약 코멘트 추가
        """
        lines = ["## 📋 Related Issues Summary\n"]
        
        if related["parent"]:
            lines.append(f"**Parent**: #{related['parent'][0]}")
        
        if related["related"]:
            refs = ", ".join([f"#{id}" for id in related["related"]])
            lines.append(f"**Related**: {refs}")
        
        if related["blocks"]:
            refs = ", ".join([f"#{id}" for id in related["blocks"]])
            lines.append(f"**This issue blocks**: {refs}")
        
        if related["blocked_by"]:
            refs = ", ".join([f"#{id}" for id in related["blocked_by"]])
            lines.append(f"**This issue is blocked by**: {refs}")
        
        comment = "\n".join(lines)
        
        cmd = f'gh issue comment {issue_id} -R {repo} --body "{comment}"'
        await asyncio.create_subprocess_shell(cmd)


# 테스트 실행
if __name__ == "__main__":
    async def test():
        node = CrossLinkIssuesNode()
        
        # 테스트 이슈 본문
        test_body = """
        ## 작업 개요
        KB System 데이터베이스 영속성 구현
        
        ## 관련 이슈
        - Parent Issue: #34
        - Related: #13, #31, #32
        - Blocks: #45
        - Blocked by: #46
        """
        
        result = await node.execute({
            "new_issue_id": "99",
            "issue_body": test_body,
            "repo": "ihw33/ai-orchestra-v02"
        })
        
        print(json.dumps(result, indent=2))
    
    asyncio.run(test())