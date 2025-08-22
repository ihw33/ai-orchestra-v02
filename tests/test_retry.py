import pytest
from core.retry import exponential_backoff_with_jitter, retry_with_backoff


def test_backoff_range():
    """백오프 시간이 범위 내에 있는지 테스트"""
    waits = [exponential_backoff_with_jitter(i) for i in range(5)]
    assert min(waits) > 0
    assert max(waits) <= 30.0  # max_ms=30000


def test_retry_with_success():
    """재시도 후 성공하는 경우"""
    calls = {"n": 0}
    
    def flaky_func():
        calls["n"] += 1
        if calls["n"] < 2:
            raise RuntimeError("boom")
        return "ok"
    
    result = retry_with_backoff(
        flaky_func, 
        max_attempts=3, 
        exceptions=(RuntimeError,)
    )
    assert result == "ok"
    assert calls["n"] == 2


def test_retry_exhausted():
    """최대 재시도 횟수 초과"""
    def always_fail():
        raise ValueError("always fail")
    
    with pytest.raises(ValueError):
        retry_with_backoff(
            always_fail,
            max_attempts=3,
            exceptions=(ValueError,)
        )