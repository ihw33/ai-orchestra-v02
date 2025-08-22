import random
import time
from typing import Callable, Any, Tuple, Type


def exponential_backoff_with_jitter(
    attempt: int, 
    base_ms: int = 500, 
    max_ms: int = 30000
) -> float:
    """
    지수 백오프 + 지터 계산
    
    Args:
        attempt: 재시도 횟수 (0부터 시작)
        base_ms: 기본 대기 시간 (밀리초)
        max_ms: 최대 대기 시간 (밀리초)
    
    Returns:
        대기 시간 (초)
    """
    wait_ms = min(base_ms * (2 ** attempt), max_ms)
    jitter = random.uniform(0, wait_ms * 0.1)  # 10% 지터
    return (wait_ms + jitter) / 1000.0


def retry_with_backoff(
    func: Callable,
    *args,
    max_attempts: int = 3,
    exceptions: Tuple[Type[Exception], ...] = (Exception,),
    **kwargs
) -> Any:
    """
    재시도 메커니즘 with 백오프
    
    Args:
        func: 실행할 함수
        max_attempts: 최대 재시도 횟수
        exceptions: 재시도할 예외 타입들
        
    Returns:
        함수 실행 결과
    """
    last_exception = None
    
    for attempt in range(max_attempts):
        try:
            return func(*args, **kwargs)
        except exceptions as e:
            last_exception = e
            if attempt < max_attempts - 1:
                wait_time = exponential_backoff_with_jitter(attempt)
                time.sleep(wait_time)
            else:
                raise
    
    # Should not reach here, but for safety
    if last_exception:
        raise last_exception