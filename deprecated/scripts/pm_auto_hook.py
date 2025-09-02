#!/usr/bin/env python3
"""
PM Auto Hook - 자동 복구 시스템
새 세션 시작 시 자동으로 PM 모드 활성화
"""

import os
import subprocess
import sys

def auto_detect_pm_mode():
    """폴더와 역할을 자동 감지하여 PM 모드 활성화"""
    
    current_dir = os.getcwd()
    
    # ai-orchestra-v02 프로젝트인지 확인
    if "ai-orchestra-v02" not in current_dir:
        return False
    
    print("="*60)
    print("🤖 PM Claude 자동 복구 시스템 활성화")
    print("="*60)
    
    # 1. 핵심 워크플로우 명령어만 표시 (문서 읽기 X)
    print("\n📌 즉시 사용 가능한 명령어:")
    print("-" * 40)
    
    commands = {
        "병렬 처리": "python3 multi_ai_orchestrator.py [ISSUE#]",
        "순차 처리": "python3 relay_pipeline_system.py [ISSUE#]", 
        "Gemini 직접": "gemini -p '작업 내용'",
        "Codex 직접": "codex -p '작업 내용'",
        "Claude 직접": "claude -p '작업 내용'",
        "Issue 생성": "gh issue create --title '제목' --body '내용'",
        "PR 생성": "gh pr create --title '제목' --body '내용'"
    }
    
    for name, cmd in commands.items():
        print(f"  {name:12} → {cmd}")
    
    # 2. 현재 상태만 간단히 확인 (3개 이슈만)
    print("\n📊 현재 오픈 이슈 (상위 3개):")
    print("-" * 40)
    result = subprocess.run(
        "gh issue list -R ihw33/ai-orchestra-v02 --state open --limit 3",
        shell=True, capture_output=True, text=True
    )
    if result.stdout:
        print(result.stdout)
    
    # 3. 실행 중인 백그라운드 작업 확인
    print("\n🔄 실행 중인 자동 워크플로우:")
    print("-" * 40)
    result = subprocess.run(
        "ps aux | grep -E 'orchestrator|pipeline|relay' | grep -v grep",
        shell=True, capture_output=True, text=True
    )
    if result.stdout:
        print(result.stdout)
    else:
        print("  (현재 실행 중인 워크플로우 없음)")
    
    # 4. 빠른 시작 제안
    print("\n🚀 빠른 시작:")
    print("-" * 40)
    print("1. 새 이슈 처리: python3 multi_ai_orchestrator.py $(gh issue list --limit 1 --json number -q '.[0].number')")
    print("2. 특정 작업: gemini -p '작업 내용' | gh issue comment ISSUE# -F -")
    print("3. 상태 확인: gh issue list --state open")
    
    print("\n✅ PM 모드 준비 완료!")
    print("="*60)
    
    return True

def inject_hook_to_workflow():
    """기존 워크플로우에 자동 훅 삽입"""
    
    workflows = [
        "multi_ai_orchestrator.py",
        "relay_pipeline_system.py"
    ]
    
    hook_code = """
# PM 자동 복구 훅
import pm_auto_hook
pm_auto_hook.auto_detect_pm_mode()
"""
    
    for workflow_file in workflows:
        if os.path.exists(workflow_file):
            # 파일 읽기
            with open(workflow_file, 'r') as f:
                content = f.read()
            
            # 이미 훅이 있는지 확인
            if "pm_auto_hook" not in content:
                # import 구문 뒤에 훅 추가
                lines = content.split('\n')
                import_end = 0
                for i, line in enumerate(lines):
                    if line.startswith('import ') or line.startswith('from '):
                        import_end = i
                
                # 훅 삽입
                lines.insert(import_end + 1, hook_code)
                
                # 파일 다시 쓰기
                with open(workflow_file, 'w') as f:
                    f.write('\n'.join(lines))
                
                print(f"✅ {workflow_file}에 PM 훅 추가됨")

if __name__ == "__main__":
    # 직접 실행 시
    auto_detect_pm_mode()
    
    # 훅 설치 옵션
    if len(sys.argv) > 1 and sys.argv[1] == "--install":
        inject_hook_to_workflow()
        print("\n✅ 모든 워크플로우에 PM 훅 설치 완료!")