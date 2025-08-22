from typing import Any, Dict


class IdempotencyManager:
    """멱등성 관리자 - 중복 실행 방지"""
    
    def __init__(self):
        self._cache: Dict[str, Any] = {}
    
    def exists(self, key: str) -> bool:
        """키가 이미 존재하는지 확인"""
        return key in self._cache
    
    def get(self, key: str) -> Any:
        """저장된 결과 가져오기"""
        return self._cache.get(key)
    
    def save(self, key: str, value: Any) -> None:
        """결과 저장"""
        self._cache[key] = value
    
    def clear(self) -> None:
        """캐시 초기화 (테스트용)"""
        self._cache.clear()


# 편의를 위한 전역 인스턴스
_default_manager = IdempotencyManager()


def check_duplicate(key: str) -> bool:
    """중복 체크 헬퍼"""
    return _default_manager.exists(key)


def save_result(key: str, value: Any) -> None:
    """결과 저장 헬퍼"""
    _default_manager.save(key, value)


def get_cached_result(key: str) -> Any:
    """캐시된 결과 가져오기"""
    return _default_manager.get(key)