#!/usr/bin/env python3
"""
실시간 테스트 데모
직접 실행해서 확인할 수 있는 테스트
"""

import subprocess
import time
import json

def test_scenario_1():
    """시나리오 1: 자동 처리기 테스트"""
    print("\n" + "="*60)
    print("🧪 테스트 시나리오 1: PM Auto Processor")
    print("="*60)
    
    print("\n이 테스트는 두 개의 터미널이 필요합니다:")
    print("\n📌 터미널 1에서 실행:")
    print("   python3 pm_auto_processor.py")
    print("\n📌 터미널 2에서 실행:")
    print("   python3 test_live_demo.py --create-issue")
    
    print("\n준비되셨나요? (Enter를 누르면 계속)")
    input()
    
    return True

def test_scenario_2():
    """시나리오 2: 직접 워크플로우 실행"""
    print("\n" + "="*60)
    print("🧪 테스트 시나리오 2: 직접 실행")
    print("="*60)
    
    print("\n현재 열린 이슈 목록:")
    subprocess.run("gh issue list -R ihw33/ai-orchestra-v02 --state open --limit 5", shell=True)
    
    print("\n테스트할 이슈 번호를 입력하세요 (예: 63): ")
    issue_num = input().strip()
    
    if issue_num:
        print(f"\n이슈 #{issue_num} 처리 중...")
        print("\n실행할 명령어:")
        print(f"   python3 multi_ai_orchestrator.py {issue_num}")
        print("\n실행하시겠습니까? (y/n): ")
        
        if input().strip().lower() == 'y':
            print("\n🚀 실행 중...")
            # 실제로는 시뮬레이션만
            print("   (시뮬레이션 모드 - 실제 실행하려면 위 명령어를 직접 실행하세요)")
            time.sleep(2)
            print("   ✅ 시뮬레이션 완료")
    
    return True

def create_test_issue():
    """테스트용 이슈 생성"""
    print("\n📝 테스트 이슈 생성 중...")
    
    test_issue_body = """
## 테스트 이슈입니다

이 이슈는 PM Auto Processor 테스트용입니다.

### 테스트 항목
- [ ] 자동 감지
- [ ] 워크플로우 선택
- [ ] GitHub 코멘트

**키워드**: 기능, 테스트
"""
    
    cmd = f'''gh issue create \
        --title "[테스트] PM Auto Processor 동작 확인" \
        --body "{test_issue_body}" \
        -R ihw33/ai-orchestra-v02'''
    
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    
    if result.returncode == 0:
        print("✅ 테스트 이슈 생성 완료!")
        print(f"   URL: {result.stdout.strip()}")
        
        # 이슈 번호 추출
        issue_url = result.stdout.strip()
        issue_num = issue_url.split('/')[-1]
        print(f"   이슈 번호: #{issue_num}")
        
        print("\n💡 이제 터미널 1의 pm_auto_processor.py가")
        print("   이 이슈를 자동으로 감지하고 처리해야 합니다!")
        
        return issue_num
    else:
        print("❌ 이슈 생성 실패")
        return None

def interactive_test():
    """대화형 테스트"""
    print("\n" + "="*60)
    print("🎮 실시간 테스트 데모")
    print("="*60)
    
    print("\n무엇을 테스트하시겠습니까?")
    print("1. PM Auto Processor (자동 감지)")
    print("2. 직접 워크플로우 실행")
    print("3. 테스트 이슈 생성")
    print("4. 모든 프로세스 확인")
    print("0. 종료")
    
    while True:
        print("\n선택 (0-4): ", end="")
        choice = input().strip()
        
        if choice == '1':
            test_scenario_1()
        elif choice == '2':
            test_scenario_2()
        elif choice == '3':
            create_test_issue()
        elif choice == '4':
            print("\n📊 실행 중인 프로세스:")
            subprocess.run("ps aux | grep -E 'orchestrator|processor|pipeline' | grep -v grep", shell=True)
        elif choice == '0':
            print("\n👋 테스트 종료")
            break
        else:
            print("잘못된 선택입니다")

def main():
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == '--create-issue':
            create_test_issue()
        elif sys.argv[1] == '--quick':
            # 빠른 테스트
            print("🚀 빠른 테스트 모드")
            print("\n1. 현재 이슈 확인:")
            subprocess.run("gh issue list -R ihw33/ai-orchestra-v02 --state open --limit 3", shell=True)
            
            print("\n2. 프로세스 확인:")
            subprocess.run("ps aux | grep -E 'pm_auto|orchestrator' | grep -v grep", shell=True)
    else:
        interactive_test()

if __name__ == "__main__":
    main()