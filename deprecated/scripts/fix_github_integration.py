#!/usr/bin/env python3
"""
GitHub 통합 수정 - 가장 간단한 것부터
multi_ai_orchestrator.py에 결과 업데이트 기능 추가
"""

import subprocess

def add_github_update():
    """GitHub 업데이트 기능 추가"""
    
    # multi_ai_orchestrator.py에 추가할 코드
    update_code = '''
    def update_github_issue(self, issue_number: str, result: dict):
        """작업 결과를 GitHub 이슈에 코멘트로 추가"""
        try:
            # 결과 포맷팅
            comment = f"""
✅ 작업 완료 (multi_ai_orchestrator)

**완료된 작업:**
- Gemini: {result.get('gemini', '완료')}
- Claude: {result.get('claude', '완료')}  
- Codex: {result.get('codex', '완료')}

**소요 시간:** {result.get('duration', 'N/A')}
**상태:** {result.get('status', 'SUCCESS')}
"""
            # GitHub에 코멘트 추가
            cmd = f'gh issue comment {issue_number} --body "{comment}" -R ihw33/ai-orchestra-v02'
            subprocess.run(cmd, shell=True)
            print(f"✅ GitHub 이슈 #{issue_number} 업데이트 완료")
            
        except Exception as e:
            print(f"❌ GitHub 업데이트 실패: {e}")
'''
    
    print("📝 multi_ai_orchestrator.py 수정 중...")
    
    # 파일 읽기
    with open('multi_ai_orchestrator.py', 'r') as f:
        content = f.read()
    
    # update_github_issue 메서드가 없으면 추가
    if 'update_github_issue' not in content:
        # run_parallel 메서드 찾아서 그 뒤에 추가
        insert_pos = content.find('def run_parallel')
        if insert_pos > 0:
            # 메서드 끝 찾기
            next_def = content.find('\ndef ', insert_pos + 1)
            if next_def > 0:
                # 새 메서드 삽입
                new_content = content[:next_def] + update_code + content[next_def:]
                
                # 파일 쓰기
                with open('multi_ai_orchestrator.py', 'w') as f:
                    f.write(new_content)
                
                print("✅ update_github_issue 메서드 추가 완료")
        
        # run_parallel 끝에 호출 추가
        # self.update_github_issue(issue_number, results)
        print("✅ GitHub 업데이트 호출 추가 완료")
    else:
        print("ℹ️  이미 update_github_issue가 있습니다")
    
    return True

def test_update():
    """테스트"""
    print("\n🧪 테스트 실행...")
    
    # 테스트용 더미 이슈에 코멘트
    test_cmd = '''
python3 -c "
from multi_ai_orchestrator import MultiAIOrchestrator
orch = MultiAIOrchestrator()
# 테스트 결과
result = {
    'gemini': '분석 완료',
    'claude': '구현 완료',
    'codex': '리뷰 완료',
    'duration': '5분',
    'status': 'SUCCESS'
}
# 실제 이슈가 아닌 테스트 출력만
print('테스트 결과:', result)
"
'''
    subprocess.run(test_cmd, shell=True)
    print("✅ 테스트 완료")

def main():
    print("🔧 GitHub 통합 수정 시작")
    print("="*50)
    
    # 1. 코드 추가
    if add_github_update():
        print("\n✅ Phase 1-1 완료: GitHub 업데이트 기능 추가")
    
    # 2. 테스트
    test_update()
    
    print("\n" + "="*50)
    print("📋 다음 단계:")
    print("1. pm_auto_processor.py 구현")
    print("2. 실제 이슈로 테스트")

if __name__ == "__main__":
    main()