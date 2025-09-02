#!/usr/bin/env python3
"""
캐싱 시스템 - API 응답 및 AI 결과 캐싱
메모리 + 파일 기반 하이브리드 캐싱
"""

import json
import os
import time
import hashlib
from typing import Any, Optional, Dict
from datetime import datetime, timedelta
import pickle
from functools import lru_cache, wraps
import threading

class CacheManager:
    """통합 캐시 매니저"""
    
    def __init__(self, cache_dir: str = "cache", max_memory_items: int = 100):
        self.cache_dir = cache_dir
        self.max_memory_items = max_memory_items
        self.memory_cache = {}
        self.cache_stats = {
            'hits': 0,
            'misses': 0,
            'evictions': 0
        }
        self.lock = threading.Lock()
        
        # 캐시 디렉토리 생성
        if not os.path.exists(cache_dir):
            os.makedirs(cache_dir)
    
    def _generate_key(self, *args, **kwargs) -> str:
        """캐시 키 생성"""
        key_data = str(args) + str(sorted(kwargs.items()))
        return hashlib.md5(key_data.encode()).hexdigest()
    
    def get(self, key: str, default: Any = None) -> Any:
        """캐시에서 값 가져오기"""
        with self.lock:
            # 1. 메모리 캐시 확인
            if key in self.memory_cache:
                item = self.memory_cache[key]
                if not self._is_expired(item):
                    self.cache_stats['hits'] += 1
                    item['last_accessed'] = time.time()
                    return item['value']
                else:
                    del self.memory_cache[key]
            
            # 2. 파일 캐시 확인
            file_path = os.path.join(self.cache_dir, f"{key}.cache")
            if os.path.exists(file_path):
                try:
                    with open(file_path, 'rb') as f:
                        item = pickle.load(f)
                    if not self._is_expired(item):
                        self.cache_stats['hits'] += 1
                        # 메모리 캐시에 추가
                        self._add_to_memory(key, item)
                        return item['value']
                    else:
                        os.remove(file_path)
                except:
                    pass
            
            self.cache_stats['misses'] += 1
            return default
    
    def set(self, key: str, value: Any, ttl: int = 3600):
        """캐시에 값 저장 (TTL: Time To Live in seconds)"""
        with self.lock:
            item = {
                'value': value,
                'created': time.time(),
                'ttl': ttl,
                'last_accessed': time.time()
            }
            
            # 메모리 캐시에 추가
            self._add_to_memory(key, item)
            
            # 파일 캐시에도 저장
            file_path = os.path.join(self.cache_dir, f"{key}.cache")
            try:
                with open(file_path, 'wb') as f:
                    pickle.dump(item, f)
            except:
                pass
    
    def _add_to_memory(self, key: str, item: Dict):
        """메모리 캐시에 추가 (LRU 정책)"""
        if len(self.memory_cache) >= self.max_memory_items:
            # 가장 오래 접근하지 않은 항목 제거
            oldest_key = min(
                self.memory_cache.keys(),
                key=lambda k: self.memory_cache[k].get('last_accessed', 0)
            )
            del self.memory_cache[oldest_key]
            self.cache_stats['evictions'] += 1
        
        self.memory_cache[key] = item
    
    def _is_expired(self, item: Dict) -> bool:
        """캐시 항목 만료 확인"""
        if 'ttl' not in item or 'created' not in item:
            return True
        return time.time() - item['created'] > item['ttl']
    
    def clear(self):
        """캐시 전체 삭제"""
        with self.lock:
            self.memory_cache.clear()
            for file in os.listdir(self.cache_dir):
                if file.endswith('.cache'):
                    try:
                        os.remove(os.path.join(self.cache_dir, file))
                    except:
                        pass
    
    def get_stats(self) -> Dict:
        """캐시 통계 반환"""
        total = self.cache_stats['hits'] + self.cache_stats['misses']
        hit_rate = (self.cache_stats['hits'] / total * 100) if total > 0 else 0
        
        return {
            **self.cache_stats,
            'hit_rate': f"{hit_rate:.1f}%",
            'memory_items': len(self.memory_cache),
            'disk_items': len([f for f in os.listdir(self.cache_dir) if f.endswith('.cache')])
        }

# 전역 캐시 매니저
cache = CacheManager()

def cached(ttl: int = 3600):
    """캐싱 데코레이터"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # 캐시 키 생성
            cache_key = f"{func.__name__}_{cache._generate_key(*args, **kwargs)}"
            
            # 캐시 확인
            result = cache.get(cache_key)
            if result is not None:
                print(f"💾 Cache hit for {func.__name__}")
                return result
            
            # 함수 실행
            result = func(*args, **kwargs)
            
            # 캐시 저장
            cache.set(cache_key, result, ttl)
            return result
        
        return wrapper
    return decorator

class GitHubCache:
    """GitHub API 전용 캐시"""
    
    def __init__(self, ttl: int = 300):  # 5분 기본 TTL
        self.ttl = ttl
        self.cache = CacheManager(cache_dir="cache/github")
    
    @cached(ttl=300)
    def get_issue(self, issue_number: int, repo: str) -> Optional[Dict]:
        """이슈 정보 캐싱"""
        import subprocess
        import json
        
        try:
            cmd = f"gh issue view {issue_number} -R {repo} --json title,body,labels,state"
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                return json.loads(result.stdout)
        except:
            pass
        return None
    
    @cached(ttl=60)
    def list_issues(self, repo: str, state: str = "open", limit: int = 10) -> list:
        """이슈 목록 캐싱"""
        import subprocess
        import json
        
        try:
            cmd = f"gh issue list -R {repo} --state {state} --limit {limit} --json number,title,state"
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                return json.loads(result.stdout)
        except:
            pass
        return []

class AIResponseCache:
    """AI 응답 전용 캐시"""
    
    def __init__(self, ttl: int = 1800):  # 30분 기본 TTL
        self.ttl = ttl
        self.cache = CacheManager(cache_dir="cache/ai")
    
    def get_cached_response(self, ai_name: str, prompt: str) -> Optional[str]:
        """캐시된 AI 응답 가져오기"""
        cache_key = f"{ai_name}_{hashlib.md5(prompt.encode()).hexdigest()}"
        return self.cache.get(cache_key)
    
    def cache_response(self, ai_name: str, prompt: str, response: str):
        """AI 응답 캐싱"""
        cache_key = f"{ai_name}_{hashlib.md5(prompt.encode()).hexdigest()}"
        self.cache.set(cache_key, response, self.ttl)

# 사용 예제
if __name__ == "__main__":
    # 일반 캐싱
    @cached(ttl=10)
    def expensive_function(x):
        print(f"Computing {x}...")
        time.sleep(2)
        return x * 2
    
    print("첫 호출:", expensive_function(5))  # 계산
    print("두 번째 호출:", expensive_function(5))  # 캐시에서
    
    # GitHub 캐싱
    gh_cache = GitHubCache()
    # issue = gh_cache.get_issue(1, "ihw33/ai-orchestra-v02")
    
    # AI 캐싱
    ai_cache = AIResponseCache()
    ai_cache.cache_response("gemini", "test prompt", "test response")
    print("Cached:", ai_cache.get_cached_response("gemini", "test prompt"))
    
    # 통계
    print("\n📊 Cache Stats:")
    print(json.dumps(cache.get_stats(), indent=2))