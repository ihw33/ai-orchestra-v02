import pytest
from core.idempotency import (
    IdempotencyManager,
    check_duplicate,
    save_result,
    get_cached_result
)


def test_idempotency_manager():
    """멱등성 관리자 기본 동작 테스트"""
    manager = IdempotencyManager()
    
    # 처음엔 없음
    assert not manager.exists("task1")
    assert manager.get("task1") is None
    
    # 저장
    manager.save("task1", "result1")
    
    # 이제 있음
    assert manager.exists("task1")
    assert manager.get("task1") == "result1"
    
    # 덮어쓰기
    manager.save("task1", "result2")
    assert manager.get("task1") == "result2"
    
    # 초기화
    manager.clear()
    assert not manager.exists("task1")


def test_global_helpers():
    """전역 헬퍼 함수 테스트"""
    task_id = "test_global_123"
    
    # 중복 체크
    assert not check_duplicate(task_id)
    
    # 결과 저장
    save_result(task_id, {"status": "OK", "data": "test"})
    
    # 이제 중복
    assert check_duplicate(task_id)
    
    # 캐시된 결과 가져오기
    cached = get_cached_result(task_id)
    assert cached == {"status": "OK", "data": "test"}