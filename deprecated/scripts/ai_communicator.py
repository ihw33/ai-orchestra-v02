#!/usr/bin/env python3
"""
통합 AI 통신 모듈 - 모든 AI 통신을 하나로
gemini, codex, claude 통신 통합
"""

import subprocess
import json
import time
from typing import Dict, Optional, Any
from datetime import datetime

class AICommunicator:
    """통합 AI 통신 인터페이스"""
    
    def __init__(self):
        # AI 설정
        self.ai_configs = {
            'gemini': {
                'command': 'gemini -p',
                'timeout': 120,
                'retry': 3
            },
            'claude': {
                'command': 'claude -p',
                'timeout': 180,
                'retry': 2
            },
            'codex': {
                'command': 'codex exec',
                'timeout': 150,
                'retry': 2
            }
        }
        
        # 실행 통계
        self.stats = {
            'total_calls': 0,
            'success': 0,
            'failed': 0,
            'timeouts': 0
        }
    
    def execute(self, ai_name: str, prompt: str, context: str = "") -> Dict:
        """AI 실행 (재시도 로직 포함)"""
        if ai_name not in self.ai_configs:
            return {
                'success': False,
                'error': f'Unknown AI: {ai_name}',
                'ai': ai_name
            }
        
        config = self.ai_configs[ai_name]
        full_prompt = f"{context}\n\n{prompt}" if context else prompt
        
        # 재시도 로직
        for attempt in range(config['retry']):
            result = self._execute_once(ai_name, full_prompt, config['timeout'])
            
            if result['success']:
                self.stats['success'] += 1
                return result
            
            if attempt < config['retry'] - 1:
                print(f"  ⚠️ Retry {attempt + 1}/{config['retry']} for {ai_name}")
                time.sleep(2 ** attempt)  # 지수 백오프
        
        self.stats['failed'] += 1
        return result
    
    def _execute_once(self, ai_name: str, prompt: str, timeout: int) -> Dict:
        """단일 AI 실행"""
        self.stats['total_calls'] += 1
        
        config = self.ai_configs[ai_name]
        cmd = f'{config["command"]} "{prompt}"'
        
        print(f"🤖 Executing {ai_name}...")
        
        try:
            result = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            
            if result.returncode == 0:
                print(f"✅ {ai_name} completed")
                return {
                    'success': True,
                    'output': result.stdout,
                    'ai': ai_name,
                    'timestamp': datetime.now().isoformat()
                }
            else:
                print(f"❌ {ai_name} failed")
                return {
                    'success': False,
                    'error': result.stderr or 'Unknown error',
                    'ai': ai_name,
                    'timestamp': datetime.now().isoformat()
                }
                
        except subprocess.TimeoutExpired:
            print(f"⏱️ {ai_name} timeout")
            self.stats['timeouts'] += 1
            return {
                'success': False,
                'error': f'Timeout after {timeout} seconds',
                'ai': ai_name,
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            print(f"❌ {ai_name} exception: {e}")
            return {
                'success': False,
                'error': str(e),
                'ai': ai_name,
                'timestamp': datetime.now().isoformat()
            }
    
    def execute_parallel(self, ai_list: list, prompt: str) -> Dict[str, Dict]:
        """병렬 AI 실행"""
        from concurrent.futures import ThreadPoolExecutor, as_completed
        
        results = {}
        
        with ThreadPoolExecutor(max_workers=len(ai_list)) as executor:
            futures = {
                executor.submit(self.execute, ai, prompt): ai 
                for ai in ai_list if ai in self.ai_configs
            }
            
            for future in as_completed(futures):
                ai_name = futures[future]
                try:
                    results[ai_name] = future.result()
                except Exception as e:
                    results[ai_name] = {
                        'success': False,
                        'error': str(e),
                        'ai': ai_name
                    }
        
        return results
    
    def execute_sequential(self, ai_list: list, prompt: str) -> Dict[str, Dict]:
        """순차 AI 실행 (컨텍스트 전달)"""
        results = {}
        context = ""
        
        for ai_name in ai_list:
            if ai_name in self.ai_configs:
                result = self.execute(ai_name, prompt, context)
                results[ai_name] = result
                
                # 성공한 경우 다음 AI에 컨텍스트 전달
                if result['success']:
                    context = f"Previous {ai_name} output:\n{result['output'][:500]}\n"
        
        return results
    
    def get_stats(self) -> Dict:
        """통계 반환"""
        return {
            **self.stats,
            'success_rate': self.stats['success'] / max(self.stats['total_calls'], 1) * 100
        }
    
    def reset_stats(self):
        """통계 초기화"""
        self.stats = {
            'total_calls': 0,
            'success': 0,
            'failed': 0,
            'timeouts': 0
        }

# 편의 함수들
def ask_gemini(prompt: str) -> str:
    """Gemini에게 질문 (간단한 인터페이스)"""
    comm = AICommunicator()
    result = comm.execute('gemini', prompt)
    return result.get('output', result.get('error', 'Failed'))

def ask_claude(prompt: str) -> str:
    """Claude에게 질문 (간단한 인터페이스)"""
    comm = AICommunicator()
    result = comm.execute('claude', prompt)
    return result.get('output', result.get('error', 'Failed'))

def ask_codex(prompt: str) -> str:
    """Codex에게 질문 (간단한 인터페이스)"""
    comm = AICommunicator()
    result = comm.execute('codex', prompt)
    return result.get('output', result.get('error', 'Failed'))

def ask_all(prompt: str, parallel: bool = True) -> Dict[str, str]:
    """모든 AI에게 질문"""
    comm = AICommunicator()
    
    if parallel:
        results = comm.execute_parallel(['gemini', 'claude', 'codex'], prompt)
    else:
        results = comm.execute_sequential(['gemini', 'claude', 'codex'], prompt)
    
    return {
        ai: result.get('output', result.get('error', 'Failed'))
        for ai, result in results.items()
    }

if __name__ == "__main__":
    # 테스트
    import sys
    
    if len(sys.argv) > 1:
        prompt = " ".join(sys.argv[1:])
        print(f"\n📝 Testing with: {prompt}\n")
        
        # 모든 AI에게 병렬로 질문
        results = ask_all(prompt)
        
        for ai, output in results.items():
            print(f"\n=== {ai.upper()} ===")
            print(output[:500])
            print("...")
    else:
        print("Usage: python3 ai_communicator.py 'your prompt here'")