"""
Base adapter interface for AI Orchestra v02
"""

from abc import ABC, abstractmethod
from typing import Optional
from dataclasses import dataclass
from core.types import HandshakeResult
from core.exec_parser import parse_exec


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
        """EXEC 명령 파싱 - 공용 파서 사용"""
        command = parse_exec(exec_line)
        params = {'verb': command.verb}
        params.update(command.params)
        if command.payload:
            params['payload'] = command.payload
        return params
    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name={self.config.name})"