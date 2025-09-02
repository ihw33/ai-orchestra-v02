#!/usr/bin/env python3
"""
Issue #101을 ai_code_generation_adapter로 자동 실행
PR까지 자동 생성되는지 테스트
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from src.adapters.ai.ai_code_generation_adapter import AICodeGenerationAdapter

def test_auto_pr():
    """Issue #101 자동 PR 생성 테스트"""
    
    print("🤖 AI Code Generation Adapter로 Issue #101 실행")
    print("="*60)
    
    adapter = AICodeGenerationAdapter(repo="ihw33/ai-orchestra-v02")
    
    # Issue #101로 워크플로우 실행
    result = adapter.execute_code_generation_workflow(task_id=101)
    
    if result.success:
        print(f"\n✅ 성공!")
        print(f"  - 브랜치: {result.branch_name}")
        print(f"  - 커밋: {result.commit_sha[:8]}")
        print(f"  - PR: #{result.pr_number}")
        print(f"  - 파일: {len(result.generated_files)}개")
    else:
        print(f"\n❌ 실패:")
        for error in result.errors:
            print(f"  - {error}")
    
    return result

if __name__ == "__main__":
    # 주의: 이미 string_utils.py가 있어서 충돌 가능
    print("⚠️  주의: 이미 구현된 파일이 있을 수 있습니다")
    print("실행하시겠습니까? (실제로는 실행하지 않습니다)")
    
    # 시뮬레이션만
    print("\n📝 어댑터 사용 시 자동으로:")
    print("1. Task 분석")
    print("2. 브랜치 생성 (task/101-ai-generated)")
    print("3. AI로 코드 생성")
    print("4. 파일 생성/수정")
    print("5. 커밋 & 푸시")
    print("6. PR 자동 생성 ✨")
    print("\n이것이 자동화의 힘입니다!")