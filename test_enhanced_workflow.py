#!/usr/bin/env python3
"""
Enhanced Workflow Test
개선된 워크플로우 통합 테스트
"""

import asyncio
import json
from datetime import datetime

# 노드들 import
from nodes.cross_link_issues_node import CrossLinkIssuesNode
from nodes.auto_branch_creation_node import AutoBranchCreationNode
from nodes.progress_reporting_node import ProgressReportingNode
from dags.enhanced_ai_task_dag import EnhancedAITaskDAG

async def test_full_workflow():
    """
    전체 워크플로우 테스트
    """
    print("=" * 60)
    print("🧪 Enhanced AI Task Workflow Test")
    print("=" * 60)
    
    # 테스트 이슈 데이터
    test_issue = {
        "issue_number": "99",
        "issue_title": "[AI] KB System 데이터베이스 영속성 구현",
        "issue_body": """
## 📋 작업 개요
KB System의 데이터를 Redis에서 PostgreSQL로 마이그레이션

## 🔗 관련 이슈
- Parent Issue: #34
- Related: #13, #31, #32
- Blocks: #45
- Blocked by: #46

## 📦 구현 범위
### Backend
- [ ] Database: `prisma/schema.prisma`
- [ ] Services: `services/kb-persistence.ts`
- [ ] API Routes: `app/api/kb/route.ts`

## 🤖 AI 역할 분담
### Gemini (설계/분석)
- 데이터베이스 스키마 설계
- 마이그레이션 전략 수립

### Claude (구현)
- Prisma 스키마 작성
- 서비스 로직 구현

### Codex (백엔드/인프라)
- API 엔드포인트 구현
- 마이그레이션 스크립트 작성

```
ai_metadata:
  priority: high
  estimated_hours: 8
  requires_human_review: true
  auto_merge: false
  branch_name: feat/kb-persistence
```
""",
        "repo": "ihw33/ai-orchestra-v02"
    }
    
    print(f"\n📝 Test Issue: #{test_issue['issue_number']}")
    print(f"   Title: {test_issue['issue_title']}")
    print()
    
    # 워크플로우 실행
    dag = EnhancedAITaskDAG()
    
    try:
        result = await dag.execute(test_issue)
        
        print("\n" + "=" * 60)
        print("✅ Workflow Test Completed Successfully!")
        print("=" * 60)
        
        print("\n📊 Results Summary:")
        print(json.dumps(result, indent=2, default=str))
        
        return True
        
    except Exception as e:
        print(f"\n❌ Test Failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_individual_nodes():
    """
    개별 노드 테스트
    """
    print("\n" + "=" * 60)
    print("🔬 Testing Individual Nodes")
    print("=" * 60)
    
    # 1. Cross-link 테스트
    print("\n1️⃣ Testing Cross-Link Node...")
    cross_link_node = CrossLinkIssuesNode()
    
    # 관련 이슈 추출 테스트
    test_body = """
    - Parent Issue: #34
    - Related: #13, #31, #32
    - Blocks: #45
    """
    
    related = cross_link_node.extract_related_issues(test_body)
    print(f"   Extracted related issues: {related}")
    assert related["parent"] == ["34"]
    assert related["related"] == ["13", "31", "32"]
    assert related["blocks"] == ["45"]
    print("   ✅ Cross-link node test passed")
    
    # 2. Branch naming 테스트
    print("\n2️⃣ Testing Branch Creation Node...")
    branch_node = AutoBranchCreationNode()
    
    # 브랜치명 생성 테스트
    branch_name = branch_node.generate_branch_name(
        "[AI] KB System 데이터베이스 영속성 구현",
        "99"
    )
    print(f"   Generated branch name: {branch_name}")
    assert branch_name.startswith("feat/")
    assert "99" in branch_name
    print("   ✅ Branch creation node test passed")
    
    # 3. Progress reporting 테스트
    print("\n3️⃣ Testing Progress Reporting Node...")
    progress_node = ProgressReportingNode()
    
    # 보고서 생성 테스트
    report = await progress_node.generate_progress_report(
        "Test Task",
        "in_progress",
        "Testing progress reporting",
        [
            {"task": "Setup", "done": True},
            {"task": "Implementation", "done": False}
        ],
        "claude"
    )
    print("   Generated report preview:")
    print("   " + report.split('\n')[0])  # 첫 줄만 출력
    assert "Progress Update" in report
    assert "claude" in report.lower()
    print("   ✅ Progress reporting node test passed")
    
    print("\n" + "=" * 60)
    print("✅ All Individual Node Tests Passed!")
    print("=" * 60)

async def main():
    """
    메인 테스트 실행
    """
    print("\n🚀 Starting Enhanced Workflow Tests")
    print(f"   Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # 개별 노드 테스트
    await test_individual_nodes()
    
    # 전체 워크플로우 테스트 (실제 GitHub 작업은 스킵)
    print("\n⏭️  Skipping full workflow test (requires GitHub access)")
    print("   To run full test: python test_enhanced_workflow.py --full")
    
    print("\n" + "=" * 60)
    print("🎉 All Tests Completed Successfully!")
    print("=" * 60)

if __name__ == "__main__":
    import sys
    
    if "--full" in sys.argv:
        # 전체 테스트 (GitHub 액세스 필요)
        asyncio.run(test_full_workflow())
    else:
        # 기본: 개별 노드 테스트만
        asyncio.run(main())