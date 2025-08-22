"""
공통 타입 정의 - 순환 참조 방지
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class HandshakeResult:
    """3-Step Handshake 결과"""
    success: bool
    status: Optional[str] = None
    error: Optional[str] = None
    duration: Optional[float] = None
    task_id: Optional[str] = None
    
    def __bool__(self) -> bool:
        return self.success