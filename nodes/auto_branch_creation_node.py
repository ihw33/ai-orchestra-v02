#!/usr/bin/env python3
"""
Auto Branch Creation Node
이슈 제목과 번호를 기반으로 브랜치 자동 생성
"""

import asyncio
import re
from typing import Dict, Optional
from datetime import datetime

class AutoBranchCreationNode:
    """
    이슈 정보를 기반으로 적절한 브랜치명을 생성하고 브랜치 생성
    """
    
    def __init__(self):
        self.name = "AutoBranchCreation"
        self.description = "브랜치 자동 생성 및 체크아웃"
        
    async def execute(self, context: Dict) -> Dict:
        """
        브랜치 생성 실행
        
        Args:
            context: {
                "issue_number": str,
                "issue_title": str,
                "issue_body": str (optional),
                "base_branch": str (default: "main")
            }
        """
        issue_number = context.get("issue_number")
        issue_title = context.get("issue_title", "")
        issue_body = context.get("issue_body", "")
        base_branch = context.get("base_branch", "main")
        
        if not issue_number:
            return {"error": "No issue number provided"}
        
        # 브랜치명 생성
        branch_name = self.generate_branch_name(issue_title, issue_number, issue_body)
        
        # 브랜치 생성
        result = await self.create_branch(branch_name, base_branch)
        
        if result["success"]:
            # 이슈에 브랜치 정보 코멘트 추가
            await self.add_branch_comment(issue_number, branch_name)
        
        return {
            "branch_name": branch_name,
            "base_branch": base_branch,
            "success": result["success"],
            "message": result.get("message", ""),
            "timestamp": datetime.now().isoformat()
        }
    
    def generate_branch_name(self, 
                           issue_title: str, 
                           issue_number: str,
                           issue_body: str = "") -> str:
        """
        이슈 정보를 기반으로 브랜치명 생성
        
        규칙:
        - feat/: 새 기능
        - fix/: 버그 수정
        - docs/: 문서
        - refactor/: 리팩토링
        - test/: 테스트
        - chore/: 기타 작업
        """
        # [AI] 태그 제거
        title_clean = re.sub(r'\[AI\]\s*', '', issue_title)
        
        # 브랜치 타입 결정
        prefix = self.determine_prefix(title_clean, issue_body)
        
        # 제목을 브랜치명으로 변환
        # 1. 특수문자 제거
        branch_name = re.sub(r'[^\w\s가-힣-]', '', title_clean.lower())
        
        # 2. 한글을 영어로 변환 (간단한 매핑)
        korean_to_english = {
            '구현': 'impl',
            '수정': 'fix',
            '개선': 'improve',
            '추가': 'add',
            '삭제': 'remove',
            '업데이트': 'update',
            '리팩토링': 'refactor',
            '테스트': 'test',
            '문서': 'docs',
            '설정': 'config',
            '데이터베이스': 'db',
            '영속성': 'persistence',
            '시스템': 'system',
            '서비스': 'service',
            '컴포넌트': 'component',
            '페이지': 'page',
            '모듈': 'module',
            '노드': 'node',
            '오케스트': 'orchestra',
            '통합': 'integration'
        }
        
        for korean, english in korean_to_english.items():
            branch_name = branch_name.replace(korean, english)
        
        # 3. 공백을 하이픈으로
        branch_name = re.sub(r'\s+', '-', branch_name)
        
        # 4. 연속된 하이픈 제거
        branch_name = re.sub(r'-+', '-', branch_name)
        
        # 5. 앞뒤 하이픈 제거
        branch_name = branch_name.strip('-')
        
        # 6. 길이 제한 (30자)
        if len(branch_name) > 30:
            branch_name = branch_name[:30].rstrip('-')
        
        # 7. 최종 브랜치명 조합
        return f"{prefix}/{branch_name}-{issue_number}"
    
    def determine_prefix(self, title: str, body: str) -> str:
        """
        이슈 제목과 본문을 분석하여 브랜치 접두사 결정
        """
        text = (title + " " + body).lower()
        
        # 키워드 기반 분류
        if any(word in text for word in ['버그', 'bug', 'fix', '수정', '오류', 'error']):
            return 'fix'
        elif any(word in text for word in ['문서', 'docs', 'document', 'readme']):
            return 'docs'
        elif any(word in text for word in ['테스트', 'test', 'spec']):
            return 'test'
        elif any(word in text for word in ['리팩토링', 'refactor', '개선', 'improve']):
            return 'refactor'
        elif any(word in text for word in ['설정', 'config', 'setup', 'chore']):
            return 'chore'
        else:
            return 'feat'  # 기본값은 feature
    
    async def create_branch(self, branch_name: str, base_branch: str) -> Dict:
        """
        Git 브랜치 생성
        """
        try:
            # 1. 최신 변경사항 가져오기
            fetch_cmd = f"git fetch origin {base_branch}"
            await self.run_command(fetch_cmd)
            
            # 2. base 브랜치로 체크아웃
            checkout_base = f"git checkout {base_branch}"
            await self.run_command(checkout_base)
            
            # 3. 최신 상태로 업데이트
            pull_cmd = f"git pull origin {base_branch}"
            await self.run_command(pull_cmd)
            
            # 4. 새 브랜치 생성 및 체크아웃
            create_cmd = f"git checkout -b {branch_name}"
            stdout, stderr, returncode = await self.run_command(create_cmd)
            
            if returncode == 0:
                print(f"✅ Branch created: {branch_name}")
                
                # 5. 원격에 푸시 (upstream 설정)
                push_cmd = f"git push -u origin {branch_name}"
                await self.run_command(push_cmd)
                
                return {"success": True, "message": f"Branch {branch_name} created and pushed"}
            else:
                # 브랜치가 이미 존재하는 경우
                if "already exists" in stderr:
                    checkout_cmd = f"git checkout {branch_name}"
                    await self.run_command(checkout_cmd)
                    return {"success": True, "message": f"Switched to existing branch {branch_name}"}
                else:
                    return {"success": False, "message": stderr}
                    
        except Exception as e:
            return {"success": False, "message": str(e)}
    
    async def run_command(self, cmd: str) -> tuple:
        """
        셸 커맨드 실행
        """
        process = await asyncio.create_subprocess_shell(
            cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await process.communicate()
        
        return (
            stdout.decode().strip(),
            stderr.decode().strip(),
            process.returncode
        )
    
    async def add_branch_comment(self, issue_number: str, branch_name: str):
        """
        이슈에 브랜치 정보 코멘트 추가
        """
        comment = f"""
## 🌿 Branch Created

브랜치가 자동으로 생성되었습니다:

```bash
git fetch origin
git checkout {branch_name}
```

또는 새로 클론하는 경우:

```bash
git clone -b {branch_name} https://github.com/ihw33/ai-orchestra-v02.git
```

작업 완료 후 PR을 생성해주세요.
"""
        
        cmd = f'gh issue comment {issue_number} --body "{comment}"'
        await self.run_command(cmd)


# 테스트 실행
if __name__ == "__main__":
    async def test():
        node = AutoBranchCreationNode()
        
        result = await node.execute({
            "issue_number": "99",
            "issue_title": "[AI] KB System 데이터베이스 영속성 구현",
            "issue_body": "Redis를 PostgreSQL로 전환하는 작업",
            "base_branch": "main"
        })
        
        print(f"Result: {result}")
    
    asyncio.run(test())