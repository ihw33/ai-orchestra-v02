"""
Base adapter interface for AI Orchestra v02
"""

from abc import ABC, abstractmethod
from typing import Optional
from dataclasses import dataclass
from controllers.tmux_controller import HandshakeResult


@dataclass
class AdapterConfig:
    """어댑터 설정"""
    name: str
    timeout_ack: float = 5.0
    timeout_run: float = 10.0
    timeout_eot: float = 30.0
    retry_enabled: bool = True
    max_retries: int = 3


class BaseAdapter(ABC):
    """어댑터 베이스 클래스"""
    
    def __init__(self, config: AdapterConfig):
        self.config = config
    
    @abstractmethod
    def send(self, message: str) -> None:
        """메시지 전송"""
        pass
    
    @abstractmethod
    def receive(self, timeout: Optional[float] = None) -> str:
        """메시지 수신"""
        pass
    
    @abstractmethod
    def execute_with_handshake(self, exec_line: str, task_id: str) -> HandshakeResult:
        """EXEC 명령 실행 with 3-way handshake"""
        pass
    
    def parse_exec(self, exec_line: str) -> dict:
        """EXEC 명령 파싱"""
        params = {}
        parts = exec_line.split()
        
        # 첫 단어는 동사 (IMPLEMENT, TEST 등)
        if parts:
            params['verb'] = parts[0]
        
        # 나머지는 key=value 형식
        for part in parts[1:]:
            if '=' in part:
                key, value = part.split('=', 1)
                params[key] = value
        
        return params
    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name={self.config.name})"