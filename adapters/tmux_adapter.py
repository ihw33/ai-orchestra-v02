"""
Tmux adapter for testing and simulation
"""

from typing import Optional
from .base import BaseAdapter, AdapterConfig
from controllers.tmux_controller import TmuxController
from core.types import HandshakeResult


class TmuxAdapter(BaseAdapter):
    """Tmux pane 기반 어댑터"""
    
    def __init__(self, config: AdapterConfig, pane_id: str):
        super().__init__(config)
        self.pane_id = pane_id
        self.controller = TmuxController(pane_id)
    
    def send(self, message: str) -> None:
        """tmux pane에 메시지 전송"""
        self.controller.send_keys(message)
    
    def receive(self, timeout: Optional[float] = None) -> str:
        """tmux pane에서 출력 캡처"""
        return self.controller.capture_tail(200)
    
    def execute_with_handshake(self, exec_line: str, task_id: str) -> HandshakeResult:
        """EXEC 실행 with handshake"""
        # EXEC 파싱
        params = self.parse_exec(exec_line)
        
        # 실제 명령 실행
        return self.controller.execute_with_handshake(
            command=exec_line,
            task_id=task_id,
            timeout_ack=self.config.timeout_ack,
            timeout_run=self.config.timeout_run,
            timeout_eot=self.config.timeout_eot
        )