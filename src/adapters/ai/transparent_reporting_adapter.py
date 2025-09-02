#!/usr/bin/env python3
"""
투명한 보고 어댑터
AI의 성공/실패를 그대로 보고하고 PM이 최종 정리
폴백이나 대체 작업 없이 있는 그대로 보여줌
"""

import subprocess
import json
import time
from datetime import datetime
from typing import Dict, List

class TransparentReportingAdapter:
    """AI 결과를 투명하게 보고하는 어댑터"""
    
    def __init__(self):
        self.repo = "ihw33/ai-orchestra-v02"
        self.execution_results = []
    
    def execute_with_reporting(self, ai_name: str, task: str, profile: str = None) -> str:
        """PMProcessorAdapter와의 호환성을 위한 메소드"""
        # issue_number를 task에서 추출
        import re
        match = re.search(r'Issue #(\d+)', task)
        issue_number = int(match.group(1)) if match else 0
        
        # execute_ai_and_report_as_is 호출
        result = self.execute_ai_and_report_as_is(issue_number, ai_name, task)
        
        # 결과를 문자열로 변환
        if result.get('success'):
            return result.get('output', '작업 완료')
        else:
            return f"실패: {result.get('error', '알 수 없는 오류')}"
    
    def execute_ai_and_report_as_is(self, issue_number: int, ai_type: str, task: str) -> Dict:
        """AI 실행하고 결과를 그대로 보고"""
        
        print(f"\n🤖 {ai_type} 실행 중...")
        
        # AI별 실행 명령 - 이슈 전체 내용을 AI에게 전달
        # gh issue view로 이슈 내용을 가져와서 AI에게 파이프로 전달
        # 각 AI에게 자신의 체크리스트를 찾아서 수행하도록 지시
        ai_prompts = {
            'gemini': '아키텍처 설계 - Gemini 체크리스트 확인하고 Port와 Domain 파일 생성',
            'claude': '핵심 구현 - Claude 체크리스트 확인하고 Adapter 파일 생성',
            'codex': '백엔드/인프라 - Codex 체크리스트 확인하고 Store와 테스트 파일 생성'
        }
        
        commands = {
            'gemini': f'echo "{ai_prompts["gemini"]}" && gh issue view {issue_number} -R {self.repo} | gemini -p architect',
            'claude': f'echo "{ai_prompts["claude"]}" && gh issue view {issue_number} -R {self.repo} | claude -p developer', 
            'codex': f'echo "{ai_prompts["codex"]}" && gh issue view {issue_number} -R {self.repo} | codex exec'
        }
        
        if ai_type not in commands:
            return {'error': 'Unknown AI type'}
        
        # AI 실행 (타임아웃 있음)
        start_time = datetime.now()
        try:
            # AI 출력을 그대로 GitHub에 파이프
            cmd = f'{commands[ai_type]} 2>&1 | head -100 | gh issue comment {issue_number} -R {self.repo} --body-file -'
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
            
            execution_time = (datetime.now() - start_time).total_seconds()
            
            # 실행 결과 기록 (성공/실패 무관)
            execution_record = {
                'ai': ai_type,
                'task': task,
                'success': result.returncode == 0,
                'execution_time': execution_time,
                'timestamp': datetime.now().isoformat()
            }
            
            if result.returncode == 0:
                print(f"  ✅ {ai_type} 실행 완료 (성공 여부는 댓글 확인)")
            else:
                print(f"  ⚠️ {ai_type} 실행 실패 또는 비정상 종료")
                # 실패해도 그대로 보고
                self._report_failure_as_is(issue_number, ai_type, task, "실행 실패")
            
            self.execution_results.append(execution_record)
            return execution_record
            
        except subprocess.TimeoutExpired:
            print(f"  ⏱️ {ai_type} 타임아웃 (30초)")
            # 타임아웃도 그대로 보고
            self._report_failure_as_is(issue_number, ai_type, task, "타임아웃")
            
            execution_record = {
                'ai': ai_type,
                'task': task,
                'success': False,
                'error': 'timeout',
                'execution_time': 30,
                'timestamp': datetime.now().isoformat()
            }
            
            self.execution_results.append(execution_record)
            return execution_record
    
    def _report_failure_as_is(self, issue_number: int, ai_type: str, task: str, reason: str):
        """실패를 그대로 보고"""
        
        failure_report = f"""## {self._get_ai_emoji(ai_type)} {ai_type.title()} 실행 결과

### 요청된 작업
{task}

### 실행 결과
**{reason}**

### 상태
- 실행 시간: {datetime.now().strftime('%H:%M:%S')}
- 결과: 실패 또는 타임아웃
- 작업 미완료

---
**실제 상황**: {ai_type}가 작업을 완료하지 못함
**다음 단계**: PM이 판단 후 재시도 또는 다른 AI 할당
"""
        
        # 실패도 그대로 GitHub에 보고
        cmd = f'''echo "{failure_report}" | gh issue comment {issue_number} -R {self.repo} --body-file -'''
        subprocess.run(cmd, shell=True)
    
    def generate_pm_final_report(self, issue_number: int) -> str:
        """PM 최종 보고 (있는 그대로)"""
        
        print("\n📊 PM 최종 보고 생성 중...")
        
        report = f"""## 📊 PM 최종 보고 (Issue #{issue_number})

### 실행 결과 요약
"""
        
        for result in self.execution_results:
            status = "✅" if result.get('success') else "❌"
            ai_name = result['ai'].title()
            task = result['task']
            
            if result.get('success'):
                report += f"- {ai_name}: {task} - 실행 완료 {status}\n"
            else:
                error = result.get('error', '실행 실패')
                report += f"- {ai_name}: {task} - {error} {status}\n"
        
        # 페르소나 적용 검증 (별도 체크)
        persona_check = self._check_persona_application(issue_number)
        
        report += f"""
### 페르소나 적용 확인
{persona_check}

### 작업 품질 평가
"""
        
        # 각 AI의 실제 수행 내용 평가
        for result in self.execution_results:
            if not result.get('success'):
                report += f"- {result['ai'].title()}: 작업 미수행\n"
            else:
                # 댓글 내용 분석해서 실제 작업 확인
                actual_work = self._analyze_actual_work(issue_number, result['ai'])
                report += f"- {result['ai'].title()}: {actual_work}\n"
        
        report += f"""
### 다음 단계 제안
"""
        
        # 실패한 작업들에 대한 제안
        failed = [r for r in self.execution_results if not r.get('success')]
        if failed:
            report += "#### 재시도 필요:\n"
            for f in failed:
                report += f"- {f['ai'].title()}: {f['task']}\n"
        
        report += f"""
---
**보고 시간**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**보고자**: PM Claude
**원칙**: 있는 그대로 투명하게 보고
"""
        
        return report
    
    def _check_persona_application(self, issue_number: int) -> str:
        """페르소나 적용 여부 체크"""
        
        # 실제로 댓글들을 읽어서 페르소나 적용 확인
        cmd = f"gh issue view {issue_number} -R {self.repo} --json comments -q '.comments[-3:][].body' 2>/dev/null"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        
        if result.returncode == 0 and result.stdout:
            # 김정호 페르소나 체크
            if "김정호" in result.stdout or "측정할 수 없으면" in result.stdout:
                return "- Codex: 김정호 페르소나 적용 ✅"
            else:
                return "- Codex: 김정호 페르소나 미적용 ❌"
        
        return "- 페르소나 확인 불가"
    
    def _analyze_actual_work(self, issue_number: int, ai_type: str) -> str:
        """실제로 무슨 작업을 했는지 분석"""
        
        # 간단한 휴리스틱 분석
        cmd = f"gh issue view {issue_number} -R {self.repo} --json comments -q '.comments[-1].body' 2>/dev/null | head -20"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        
        if result.stdout:
            content = result.stdout.lower()
            
            # 실제 작업 판단
            if "```" in content and ("python" in content or "javascript" in content):
                return "코드 구현 완료"
            elif "api" in content and ("endpoint" in content or "route" in content):
                return "API 설계 완료"
            elif "rg -n" in content or "ls -la" in content:
                return "파일 검색만 수행 (구현 안 함)"
            elif "아키텍처" in content or "architecture" in content:
                return "아키텍처 설계 완료"
            else:
                return "작업 내용 불명확"
        
        return "작업 확인 불가"
    
    def _get_ai_emoji(self, ai_type: str) -> str:
        """AI별 이모지"""
        emojis = {
            'gemini': '🔷',
            'claude': '🔵',
            'codex': '🔶'
        }
        return emojis.get(ai_type, '🤖')
    
    def post_pm_report(self, issue_number: int):
        """PM 보고를 GitHub에 게시"""
        
        report = self.generate_pm_final_report(issue_number)
        
        # PM 보고 게시
        cmd = f'''echo "{report}" | gh issue comment {issue_number} -R {self.repo} --body-file -'''
        result = subprocess.run(cmd, shell=True)
        
        if result.returncode == 0:
            print("✅ PM 최종 보고 완료")
        else:
            print("⚠️ PM 보고 게시 실패")


# 테스트
if __name__ == "__main__":
    print("🎯 투명한 보고 어댑터 테스트")
    print("="*70)
    print("AI 결과를 있는 그대로 보고합니다")
    print("폴백이나 대체 작업 없음!")
    print("="*70)
    
    adapter = TransparentReportingAdapter()
    issue_number = 108
    
    # 각 AI 실행 (결과 그대로)
    tasks = [
        ('gemini', '실시간 알림 아키텍처 설계'),
        ('codex', '알림 API 구현'),
        ('claude', 'WebSocket 서버 구현')
    ]
    
    for ai_type, task in tasks:
        print(f"\n{ai_type.upper()} 실행:")
        result = adapter.execute_ai_and_report_as_is(issue_number, ai_type, task)
        print(f"  결과: {result}")
        time.sleep(2)
    
    # PM 최종 보고
    print("\n" + "="*70)
    print("PM 최종 보고:")
    print("="*70)
    adapter.post_pm_report(issue_number)
    
    print("\n✨ 완료!")
    print("모든 결과가 있는 그대로 보고되었습니다.")
    print("실패는 실패로, 성공은 성공으로!")