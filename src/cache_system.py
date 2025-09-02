"""캐시 시스템 구현"""
import time
from typing import Any, Optional
from threading import Lock

class CacheSystem:
    def __init__(self, max_size: int = 1000):
        self._cache = {}
        self._access_times = {}
        self._ttl_map = {}
        self.max_size = max_size
        self._lock = Lock()
    
    def get(self, key: str) -> Optional[Any]:
        """값 조회"""
        with self._lock:
            if key in self._cache:
                # TTL 체크
                if self._check_ttl(key):
                    self._access_times[key] = time.time()
                    return self._cache[key]
                else:
                    self.delete(key)
            return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None):
        """값 설정"""
        with self._lock:
            if len(self._cache) >= self.max_size:
                self._evict_lru()
            
            self._cache[key] = value
            self._access_times[key] = time.time()
            
            if ttl:
                self._ttl_map[key] = time.time() + ttl
    
    def delete(self, key: str) -> bool:
        """값 삭제"""
        with self._lock:
            if key in self._cache:
                del self._cache[key]
                del self._access_times[key]
                if key in self._ttl_map:
                    del self._ttl_map[key]
                return True
            return False
    
    def _check_ttl(self, key: str) -> bool:
        """TTL 확인"""
        if key in self._ttl_map:
            return time.time() < self._ttl_map[key]
        return True
    
    def _evict_lru(self):
        """LRU 제거"""
        if self._access_times:
            lru_key = min(self._access_times, key=self._access_times.get)
            self.delete(lru_key)
