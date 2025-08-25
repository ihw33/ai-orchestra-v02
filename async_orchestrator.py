#!/usr/bin/env python3
"""
비동기 오케스트레이터 - 성능 최적화 버전
asyncio를 사용한 진짜 비동기 처리
"""

import asyncio
import json
import time
from typing import Dict, List, Optional, Any
from datetime import datetime
import subprocess
from cache_manager import AIResponseCache, GitHubCache
from error_handler import ErrorHandler, log_info, log_error

class AsyncOrchestrator:
    """비동기 오케스트레이터"""
    
    def __init__(self):
        self.ai_cache = AIResponseCache()
        self.gh_cache = GitHubCache()
        self.error_handler = ErrorHandler("AsyncOrchestrator")
        
        # AI 설정
        self.ai_configs = {
            'gemini': {'command': 'gemini -p', 'timeout': 120},
            'claude': {'command': 'claude -p', 'timeout': 180},
            'codex': {'command': 'codex exec', 'timeout': 150}
        }
        
        # 성능 통계
        self.stats = {
            'total_time': 0,
            'ai_calls': 0,
            'cache_hits': 0,
            'parallel_executions': 0
        }
    
    async def execute_ai_async(self, ai_name: str, prompt: str) -> Dict:
        """비동기 AI 실행"""
        start_time = time.time()
        
        # 캐시 확인
        cached = self.ai_cache.get_cached_response(ai_name, prompt)
        if cached:
            self.stats['cache_hits'] += 1
            log_info(f"💾 Cache hit for {ai_name}")
            return {
                'success': True,
                'output': cached,
                'ai': ai_name,
                'cached': True,
                'time': 0
            }
        
        # AI 실행
        self.stats['ai_calls'] += 1
        config = self.ai_configs[ai_name]
        cmd = f'{config["command"]} "{prompt}"'
        
        try:
            # subprocess를 비동기로 실행
            proc = await asyncio.create_subprocess_shell(
                cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            # 타임아웃 설정
            try:
                stdout, stderr = await asyncio.wait_for(
                    proc.communicate(),
                    timeout=config['timeout']
                )
            except asyncio.TimeoutError:
                proc.kill()
                await proc.communicate()
                log_error(f"⏱️ {ai_name} timeout")
                return {
                    'success': False,
                    'error': 'Timeout',
                    'ai': ai_name,
                    'time': time.time() - start_time
                }
            
            if proc.returncode == 0:
                output = stdout.decode()
                # 캐시 저장
                self.ai_cache.cache_response(ai_name, prompt, output)
                log_info(f"✅ {ai_name} completed in {time.time() - start_time:.2f}s")
                return {
                    'success': True,
                    'output': output,
                    'ai': ai_name,
                    'cached': False,
                    'time': time.time() - start_time
                }
            else:
                log_error(f"❌ {ai_name} failed")
                return {
                    'success': False,
                    'error': stderr.decode(),
                    'ai': ai_name,
                    'time': time.time() - start_time
                }
                
        except Exception as e:
            log_error(f"❌ {ai_name} exception: {e}")
            return {
                'success': False,
                'error': str(e),
                'ai': ai_name,
                'time': time.time() - start_time
            }
    
    async def execute_parallel(self, ai_list: List[str], prompt: str) -> Dict[str, Dict]:
        """병렬 AI 실행 (진짜 비동기)"""
        start_time = time.time()
        self.stats['parallel_executions'] += 1
        
        log_info(f"🚀 Starting parallel execution for {len(ai_list)} AIs")
        
        # 모든 AI를 동시에 실행
        tasks = [
            self.execute_ai_async(ai, prompt)
            for ai in ai_list if ai in self.ai_configs
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 결과 정리
        final_results = {}
        for ai, result in zip(ai_list, results):
            if isinstance(result, Exception):
                final_results[ai] = {
                    'success': False,
                    'error': str(result),
                    'ai': ai
                }
            else:
                final_results[ai] = result
        
        total_time = time.time() - start_time
        self.stats['total_time'] += total_time
        
        log_info(f"⚡ Parallel execution completed in {total_time:.2f}s")
        return final_results
    
    async def execute_sequential(self, ai_list: List[str], prompt: str) -> Dict[str, Dict]:
        """순차 AI 실행 (컨텍스트 전달)"""
        start_time = time.time()
        results = {}
        context = ""
        
        for ai_name in ai_list:
            if ai_name in self.ai_configs:
                full_prompt = f"{context}\n\n{prompt}" if context else prompt
                result = await self.execute_ai_async(ai_name, full_prompt)
                results[ai_name] = result
                
                # 성공한 경우 컨텍스트 업데이트
                if result.get('success'):
                    context = f"Previous {ai_name} output:\n{result['output'][:500]}\n"
        
        total_time = time.time() - start_time
        log_info(f"📝 Sequential execution completed in {total_time:.2f}s")
        return results
    
    async def process_github_issue_async(self, issue_number: int, repo: str = "ihw33/ai-orchestra-v02"):
        """GitHub 이슈 비동기 처리"""
        log_info(f"📋 Processing issue #{issue_number}")
        
        # 캐시된 이슈 정보 사용
        issue = self.gh_cache.get_issue(issue_number, repo)
        if not issue:
            log_error(f"Issue #{issue_number} not found")
            return None
        
        prompt = f"Issue: {issue.get('title', '')}\n\n{issue.get('body', '')}"
        
        # 모든 AI에게 병렬로 요청
        results = await self.execute_parallel(['gemini', 'claude', 'codex'], prompt)
        
        # 결과 포스팅 (이 부분도 비동기로 개선 가능)
        await self.post_results_async(issue_number, repo, results)
        
        return results
    
    async def post_results_async(self, issue_number: int, repo: str, results: Dict):
        """결과를 GitHub에 비동기로 포스팅"""
        comment = "## 🚀 Async Orchestra Results\n\n"
        
        for ai_name, result in results.items():
            status = "✅" if result.get('success') else "❌"
            cached = "💾" if result.get('cached') else "🔄"
            time_taken = result.get('time', 0)
            
            comment += f"### {ai_name.upper()} {status} {cached}\n"
            comment += f"*Time: {time_taken:.2f}s*\n\n"
            
            if result.get('success'):
                output = result['output'][:500]
                comment += f"```\n{output}\n...\n```\n\n"
            else:
                comment += f"Error: {result.get('error', 'Unknown')}\n\n"
        
        # 통계 추가
        comment += f"\n---\n"
        comment += f"*Total AI calls: {self.stats['ai_calls']} | "
        comment += f"Cache hits: {self.stats['cache_hits']}*"
        
        # GitHub에 포스팅 (여전히 동기식이지만 개선 가능)
        escaped = comment.replace('"', '\\"').replace('\n', '\\n')
        cmd = f'gh issue comment {issue_number} -R {repo} -b "{escaped}"'
        
        proc = await asyncio.create_subprocess_shell(cmd)
        await proc.communicate()
        log_info(f"✅ Results posted to issue #{issue_number}")
    
    def get_stats(self) -> Dict:
        """성능 통계 반환"""
        avg_time = self.stats['total_time'] / max(self.stats['parallel_executions'], 1)
        cache_rate = (self.stats['cache_hits'] / max(self.stats['ai_calls'], 1)) * 100
        
        return {
            **self.stats,
            'avg_parallel_time': f"{avg_time:.2f}s",
            'cache_hit_rate': f"{cache_rate:.1f}%"
        }

async def benchmark_comparison():
    """동기 vs 비동기 성능 비교"""
    orchestrator = AsyncOrchestrator()
    prompt = "What is the best programming language?"
    
    print("🏃 Performance Benchmark\n")
    
    # 병렬 실행 (비동기)
    print("⚡ Async Parallel Execution:")
    start = time.time()
    results = await orchestrator.execute_parallel(['gemini', 'claude', 'codex'], prompt)
    async_time = time.time() - start
    print(f"Time: {async_time:.2f}s\n")
    
    # 순차 실행 (비교용)
    print("🐌 Sequential Execution:")
    start = time.time()
    results = await orchestrator.execute_sequential(['gemini', 'claude', 'codex'], prompt)
    seq_time = time.time() - start
    print(f"Time: {seq_time:.2f}s\n")
    
    # 결과
    print(f"🎯 Performance Improvement: {seq_time/async_time:.1f}x faster!")
    print(f"\n📊 Stats:")
    print(json.dumps(orchestrator.get_stats(), indent=2))

# 메인 실행
async def main():
    """메인 비동기 함수"""
    orchestrator = AsyncOrchestrator()
    
    # 테스트: 병렬 실행
    print("Testing async orchestrator...")
    results = await orchestrator.execute_parallel(
        ['gemini', 'claude', 'codex'],
        "Write a hello world in Python"
    )
    
    for ai, result in results.items():
        print(f"\n{ai}: {result.get('success', False)}")
        if result.get('success'):
            print(f"Output: {result['output'][:100]}...")
    
    print(f"\n📊 Performance Stats:")
    print(json.dumps(orchestrator.get_stats(), indent=2))

if __name__ == "__main__":
    # 벤치마크 실행
    # asyncio.run(benchmark_comparison())
    
    # 일반 테스트
    asyncio.run(main())