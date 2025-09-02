#!/usr/bin/env python3
"""
통합 오케스트레이터 - 모든 오케스트레이션 기능을 하나로
multi_ai_orchestrator + master_orchestrator + 개선사항
"""

import os
import sys
import subprocess
import json
import time
import re
from typing import Dict, List, Optional, Any
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

# 에러 처리 모듈 임포트
from error_handler import (
    ErrorHandler, 
    retry_on_error, 
    handle_errors,
    SafeExecutor,
    AIExecutionError,
    GitHubAPIError,
    log_info, 
    log_warning, 
    log_error
)

# 페르소나 시스템 임포트
try:
    from personas.auto_persona_injector import IssueWorkflowIntegration
    PERSONA_ENABLED = True
except ImportError:
    PERSONA_ENABLED = False
    log_warning("페르소나 시스템을 찾을 수 없습니다. 기본 모드로 실행합니다.")

class UnifiedOrchestrator:
    """통합 오케스트레이터 - 모든 기능을 하나로"""
    
    def __init__(self):
        # 기본 설정
        self.repo = os.getenv('GITHUB_REPO', 'ihw33/ai-orchestra-v02')
        self.timeout = int(os.getenv('AI_TIMEOUT', '120'))
        
        # 페르소나 시스템 초기화
        if PERSONA_ENABLED:
            self.persona_integration = IssueWorkflowIntegration()
            log_info("✨ 페르소나 시스템 활성화됨")
        
        # AI 설정 (multi_ai_orchestrator에서)
        self.ais = {
            'gemini': {
                'command': 'gemini -p',
                'role': 'Architect & Analyzer',
                'timeout': 120
            },
            'claude': {
                'command': 'claude -p',
                'role': 'Implementation & Code Review',
                'timeout': 180
            },
            'codex': {
                'command': 'codex exec',
                'role': 'Backend & API Development',
                'timeout': 150
            }
        }
        
        # 패턴 매칭 규칙 (master_orchestrator에서)
        self.pattern_rules = {
            r'분석|검토|평가|타당성|조사|리서치': 'ANALYSIS_PIPELINE',
            r'구현|개발|만들|생성|코딩|프로그래밍': 'IMPLEMENTATION_PIPELINE',
            r'버그|오류|에러|수정|고치|문제|디버그': 'BUGFIX_WORKFLOW',
            r'테스트|검증|확인|체크': 'TEST_PIPELINE',
            r'문서|도큐|설명|가이드': 'DOCUMENTATION_PIPELINE',
            r'최적화|개선|성능|속도': 'OPTIMIZATION_PIPELINE'
        }
        
        # 워크플로우 정의
        self.workflows = {
            'ANALYSIS_PIPELINE': ['gemini', 'claude'],
            'IMPLEMENTATION_PIPELINE': ['gemini', 'codex', 'claude'],
            'BUGFIX_WORKFLOW': ['claude', 'codex'],
            'TEST_PIPELINE': ['codex', 'gemini'],
            'DOCUMENTATION_PIPELINE': ['gemini', 'claude'],
            'OPTIMIZATION_PIPELINE': ['codex', 'claude', 'gemini']
        }
        
        # 실행 통계
        self.stats = {
            'total_requests': 0,
            'successful': 0,
            'failed': 0,
            'ai_calls': {}
        }
        
        # 히스토리
        self.history = []
        self.load_history()
        
        # 스레드 풀 (병렬 실행용)
        self.executor = ThreadPoolExecutor(max_workers=3)
    
    # ==================== GitHub 이슈 처리 ====================
    
    def process_github_issue(self, issue_number: int, parallel: bool = True) -> Dict:
        """GitHub 이슈 처리 - 병렬 또는 순차"""
        print(f"\n🔍 Processing Issue #{issue_number}")
        
        # 이슈 내용 가져오기
        issue_content = self._get_issue_content(issue_number)
        if not issue_content:
            return {'success': False, 'error': 'Issue not found'}
        
        # 페르소나 모드 확인 ([AI] 태그가 있고 페르소나 시스템이 활성화된 경우)
        use_personas = False
        if PERSONA_ENABLED and '[AI]' in issue_content.get('title', ''):
            use_personas = True
            log_info("🎭 페르소나 모드로 실행합니다")
        
        if use_personas:
            # 페르소나 시스템으로 처리
            try:
                self.persona_integration.on_issue_created(issue_number)
                return {
                    'success': True,
                    'issue': issue_number,
                    'mode': 'persona',
                    'message': '페르소나 기반 AI 팀이 작업을 수행했습니다'
                }
            except Exception as e:
                log_error(f"페르소나 모드 실패: {e}")
                log_info("기본 모드로 폴백합니다")
                use_personas = False
        
        # 기본 모드 (페르소나 미사용 또는 실패 시)
        if not use_personas:
            # 패턴 감지
            pattern = self.detect_pattern(issue_content['title'] + ' ' + issue_content.get('body', ''))
            workflow = self.workflows.get(pattern, ['gemini', 'claude', 'codex'])
            
            print(f"📋 Pattern: {pattern}")
            print(f"🤖 Workflow: {' → '.join(workflow)}")
            
            # AI 실행
            if parallel:
                results = self._execute_parallel(workflow, issue_content)
            else:
                results = self._execute_sequential(workflow, issue_content)
        
        # 결과 GitHub에 포스팅
        self._post_results_to_issue(issue_number, results)
        
        # 통계 업데이트
        self.stats['total_requests'] += 1
        if all(r.get('success') for r in results.values()):
            self.stats['successful'] += 1
        else:
            self.stats['failed'] += 1
        
        return {
            'success': True,
            'issue': issue_number,
            'pattern': pattern,
            'results': results
        }
    
    def _get_issue_content(self, issue_number: int) -> Optional[Dict]:
        """GitHub 이슈 내용 가져오기"""
        try:
            cmd = f"gh issue view {issue_number} -R {self.repo} --json title,body,labels"
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                return json.loads(result.stdout)
        except Exception as e:
            print(f"❌ Error fetching issue: {e}")
        return None
    
    def _execute_parallel(self, workflow: List[str], issue_content: Dict) -> Dict:
        """병렬 AI 실행"""
        results = {}
        futures = {}
        
        with ThreadPoolExecutor(max_workers=len(workflow)) as executor:
            # 모든 AI 동시 실행
            for ai_name in workflow:
                if ai_name in self.ais:
                    prompt = self._create_prompt(ai_name, issue_content)
                    future = executor.submit(self._execute_ai, ai_name, prompt)
                    futures[future] = ai_name
            
            # 결과 수집
            for future in as_completed(futures):
                ai_name = futures[future]
                try:
                    results[ai_name] = future.result(timeout=self.timeout)
                except Exception as e:
                    results[ai_name] = {'success': False, 'error': str(e)}
        
        return results
    
    def _execute_sequential(self, workflow: List[str], issue_content: Dict) -> Dict:
        """순차 AI 실행 (이전 결과 참조)"""
        results = {}
        context = ""
        
        for ai_name in workflow:
            if ai_name in self.ais:
                # 이전 결과를 컨텍스트로 추가
                prompt = self._create_prompt(ai_name, issue_content, context)
                result = self._execute_ai(ai_name, prompt)
                results[ai_name] = result
                
                # 성공한 경우 컨텍스트 업데이트
                if result.get('success'):
                    context = f"Previous {ai_name} analysis:\\n{result['output'][:500]}\\n\\n"
        
        return results
    
    def _execute_ai(self, ai_name: str, prompt: str) -> Dict:
        """단일 AI 실행"""
        print(f"  🤖 Executing {ai_name}...")
        
        ai_config = self.ais[ai_name]
        cmd = f'{ai_config["command"]} "{prompt}"'
        
        try:
            result = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                text=True,
                timeout=ai_config.get('timeout', self.timeout)
            )
            
            # 통계 업데이트
            if ai_name not in self.stats['ai_calls']:
                self.stats['ai_calls'][ai_name] = 0
            self.stats['ai_calls'][ai_name] += 1
            
            if result.returncode == 0:
                print(f"  ✅ {ai_name} completed")
                return {
                    'success': True,
                    'output': result.stdout,
                    'timestamp': datetime.now().isoformat()
                }
            else:
                print(f"  ❌ {ai_name} failed")
                return {
                    'success': False,
                    'error': result.stderr,
                    'timestamp': datetime.now().isoformat()
                }
                
        except subprocess.TimeoutExpired:
            print(f"  ⏱️ {ai_name} timeout")
            return {'success': False, 'error': 'Timeout'}
        except Exception as e:
            print(f"  ❌ {ai_name} error: {e}")
            return {'success': False, 'error': str(e)}
    
    def _create_prompt(self, ai_name: str, issue_content: Dict, context: str = "") -> str:
        """AI별 프롬프트 생성"""
        role = self.ais[ai_name]['role']
        title = issue_content.get('title', '')
        body = issue_content.get('body', '')
        
        prompt = f"""Role: {role}
Task: {title}

{context}

Details:
{body}

Please provide your analysis and recommendations."""
        
        return prompt
    
    def _post_results_to_issue(self, issue_number: int, results: Dict):
        """결과를 GitHub 이슈에 포스팅"""
        comment = "## 🤖 AI Orchestra Results\\n\\n"
        
        for ai_name, result in results.items():
            status = "✅" if result.get('success') else "❌"
            comment += f"### {ai_name.upper()} {status}\\n"
            
            if result.get('success'):
                output = result['output'][:1000]
                comment += f"```\\n{output}\\n```\\n\\n"
            else:
                comment += f"Error: {result.get('error', 'Unknown')}\\n\\n"
        
        # 통계 추가
        comment += f"\\n---\\n"
        comment += f"*Executed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\\n"
        comment += f"*Total AI calls: {sum(self.stats['ai_calls'].values())}*"
        
        # GitHub에 코멘트
        try:
            escaped = comment.replace('"', '\\"').replace('\n', '\\n')
            cmd = f'gh issue comment {issue_number} -R {self.repo} -b "{escaped}"'
            subprocess.run(cmd, shell=True, capture_output=True, text=True)
            print(f"✅ Results posted to issue #{issue_number}")
        except Exception as e:
            print(f"❌ Failed to post results: {e}")
    
    # ==================== 패턴 매칭 & 워크플로우 ====================
    
    def detect_pattern(self, text: str) -> str:
        """텍스트에서 패턴 감지"""
        text_lower = text.lower()
        
        # 우선순위 기반 매칭
        for regex, pattern in self.pattern_rules.items():
            if re.search(regex, text_lower):
                return pattern
        
        return 'GENERAL_PIPELINE'
    
    def process_request(self, request: str, mode: str = 'auto') -> Dict:
        """일반 요청 처리 (GitHub 이슈 없이)"""
        print(f"\n📝 Processing: {request}")
        
        # 패턴 감지
        pattern = self.detect_pattern(request)
        workflow = self.workflows.get(pattern, ['gemini', 'claude'])
        
        print(f"🎯 Pattern: {pattern}")
        print(f"🤖 Workflow: {' → '.join(workflow)}")
        
        # 가상 이슈 내용 생성
        issue_content = {
            'title': request,
            'body': ''
        }
        
        # 실행 모드 결정
        if mode == 'parallel':
            results = self._execute_parallel(workflow, issue_content)
        elif mode == 'sequential':
            results = self._execute_sequential(workflow, issue_content)
        else:
            # 자동 결정: 3개 이상이면 병렬, 아니면 순차
            if len(workflow) >= 3:
                results = self._execute_parallel(workflow, issue_content)
            else:
                results = self._execute_sequential(workflow, issue_content)
        
        # 히스토리 저장
        self.history.append({
            'request': request,
            'pattern': pattern,
            'workflow': workflow,
            'results': results,
            'timestamp': datetime.now().isoformat()
        })
        self.save_history()
        
        return {
            'success': True,
            'request': request,
            'pattern': pattern,
            'results': results
        }
    
    # ==================== 대화형 모드 ====================
    
    def interactive_mode(self):
        """대화형 모드"""
        print("=" * 60)
        print("🤖 Unified Orchestrator - Interactive Mode")
        print("=" * 60)
        print("\nCommands:")
        print("  /help     - Show help")
        print("  /stats    - Show statistics")
        print("  /history  - Show history")
        print("  /issue N  - Process GitHub issue #N")
        print("  /exit     - Exit")
        print("\nOr type any request to process it.")
        print("-" * 60)
        
        while True:
            try:
                request = input("\n🎯 > ").strip()
                
                if not request:
                    continue
                
                if request == '/exit':
                    print("👋 Goodbye!")
                    break
                elif request == '/help':
                    self.show_help()
                elif request == '/stats':
                    self.show_stats()
                elif request == '/history':
                    self.show_history()
                elif request.startswith('/issue '):
                    issue_num = int(request.split()[1])
                    self.process_github_issue(issue_num)
                else:
                    self.process_request(request)
                    
            except KeyboardInterrupt:
                print("\n\n👋 Interrupted")
                break
            except Exception as e:
                print(f"❌ Error: {e}")
    
    def show_help(self):
        """도움말 표시"""
        print("""
📚 Unified Orchestrator Help

Patterns:
- Analysis: 분석, 검토, 평가
- Implementation: 구현, 개발, 생성
- Bugfix: 버그, 오류, 수정
- Test: 테스트, 검증
- Documentation: 문서, 가이드
- Optimization: 최적화, 개선

Usage:
  python3 unified_orchestrator.py                    # Interactive mode
  python3 unified_orchestrator.py --issue 63        # Process issue
  python3 unified_orchestrator.py "request"         # Direct request
  python3 unified_orchestrator.py --stats           # Show statistics
        """)
    
    def show_stats(self):
        """통계 표시"""
        print("\n📊 Statistics")
        print("-" * 40)
        print(f"Total Requests: {self.stats['total_requests']}")
        print(f"Successful: {self.stats['successful']}")
        print(f"Failed: {self.stats['failed']}")
        print("\nAI Calls:")
        for ai, count in self.stats['ai_calls'].items():
            print(f"  {ai}: {count}")
    
    def show_history(self):
        """히스토리 표시"""
        print("\n📜 Recent History")
        print("-" * 40)
        for item in self.history[-5:]:
            print(f"[{item['timestamp'][:19]}] {item['request'][:50]}")
            print(f"  Pattern: {item['pattern']}")
            print(f"  Success: {all(r.get('success') for r in item['results'].values())}")
    
    def save_history(self):
        """히스토리 저장"""
        try:
            with open('.orchestrator_history.json', 'w') as f:
                json.dump(self.history[-100:], f)  # 최근 100개만
        except:
            pass
    
    def load_history(self):
        """히스토리 로드"""
        try:
            if os.path.exists('.orchestrator_history.json'):
                with open('.orchestrator_history.json', 'r') as f:
                    self.history = json.load(f)
        except:
            self.history = []
    
    def cleanup(self):
        """리소스 정리"""
        self.executor.shutdown(wait=True)
        self.save_history()

def main():
    """메인 함수"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Unified AI Orchestrator')
    parser.add_argument('request', nargs='?', help='Direct request')
    parser.add_argument('--issue', type=int, help='Process GitHub issue')
    parser.add_argument('--parallel', action='store_true', help='Force parallel execution')
    parser.add_argument('--sequential', action='store_true', help='Force sequential execution')
    parser.add_argument('--stats', action='store_true', help='Show statistics')
    parser.add_argument('--help-extended', action='store_true', help='Show extended help')
    
    args = parser.parse_args()
    
    orchestrator = UnifiedOrchestrator()
    
    try:
        if args.help_extended:
            orchestrator.show_help()
        elif args.stats:
            orchestrator.show_stats()
        elif args.issue:
            orchestrator.process_github_issue(args.issue, parallel=not args.sequential)
        elif args.request:
            mode = 'parallel' if args.parallel else 'sequential' if args.sequential else 'auto'
            orchestrator.process_request(args.request, mode)
        else:
            orchestrator.interactive_mode()
    finally:
        orchestrator.cleanup()

if __name__ == "__main__":
    main()