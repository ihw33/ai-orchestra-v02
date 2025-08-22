import subprocess
import time
import shlex
import base64
from typing import Optional, Tuple
from dataclasses import dataclass

from core.protocol import parse_ack, parse_run, parse_eot


@dataclass
class HandshakeResult:
    """핸드셰이크 결과"""
    success: bool
    status: str
    task_id: str
    error: Optional[str] = None


class TmuxController:
    """tmux pane_id 기반 제어 (예: '%3'). 출력은 capture-pane로 가져옴."""
    
    def __init__(self, pane_id: str, poll_interval: float = 0.2):
        """
        Args:
            pane_id: tmux pane 식별자 (예: '%3', 'session:window.pane')
            poll_interval: 토큰 확인 간격 (초)
        """
        self.pane_id = pane_id
        self.poll_interval = poll_interval
    
    def send_keys(self, text: str, enter: bool = True, safe_mode: bool = True) -> None:
        """
        tmux pane에 텍스트 전송
        
        Args:
            text: 전송할 텍스트
            enter: Enter 키 추가 여부
            safe_mode: 특수문자 안전 처리 여부
        """
        try:
            if safe_mode and self._needs_safe_send(text):
                # 특수문자가 있으면 안전 모드로 전송
                self._safe_send(text)
            else:
                # 일반 전송
                subprocess.run(
                    ["tmux", "send-keys", "-t", self.pane_id, text],
                    check=True,
                    capture_output=True
                )
                if enter:
                    subprocess.run(
                        ["tmux", "send-keys", "-t", self.pane_id, "Enter"],
                        check=True,
                        capture_output=True
                    )
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Failed to send keys to tmux pane {self.pane_id}: {e}")
    
    def _needs_safe_send(self, text: str) -> bool:
        """특수문자 포함 여부 확인"""
        special_chars = ['"', "'", '`', '\\', '$', '\n', '\t', ';', '&', '|', '>', '<']
        return any(char in text for char in special_chars)
    
    def _safe_send(self, text: str) -> None:
        """특수문자를 안전하게 전송 (base64 인코딩)"""
        # base64로 인코딩
        b64 = base64.b64encode(text.encode()).decode()
        
        # tmux에서 디코드하여 실행
        # printf로 정확한 텍스트 출력
        cmd = f"printf '%s' '{b64}' | base64 -d | bash"
        
        subprocess.run(
            ["tmux", "send-keys", "-t", self.pane_id, cmd],
            check=True,
            capture_output=True
        )
        subprocess.run(
            ["tmux", "send-keys", "-t", self.pane_id, "Enter"],
            check=True,
            capture_output=True
        )
    
    def capture_output(self, last_lines: Optional[int] = None) -> str:
        """
        tmux pane의 현재 출력 캡처
        
        Args:
            last_lines: 캡처할 마지막 N줄 (None이면 전체)
        
        Returns:
            pane의 현재 내용
        """
        try:
            cmd = ["tmux", "capture-pane", "-t", self.pane_id, "-p"]
            
            # 마지막 N줄만 캡처 (성능 최적화)
            if last_lines:
                cmd.extend(["-S", f"-{last_lines}"])
            
            result = subprocess.run(
                cmd,
                check=True,
                capture_output=True,
                text=True
            )
            return result.stdout
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Failed to capture tmux pane {self.pane_id}: {e}")
    
    def capture_tail(self, lines: int = 200) -> str:
        """
        tmux pane의 마지막 N줄만 캡처 (성능 최적화)
        
        Args:
            lines: 캡처할 줄 수
            
        Returns:
            마지막 N줄
        """
        return self.capture_output(last_lines=lines)
    
    def wait_for_token(
        self, 
        task_id: str,
        token_type: str,
        timeout: float
    ) -> Tuple[bool, Optional[str]]:
        """
        특정 토큰 대기
        
        Args:
            task_id: 작업 ID
            token_type: 토큰 타입 (ACK, RUN, EOT)
            timeout: 타임아웃 (초)
            
        Returns:
            (성공 여부, 상태/에러 메시지)
        """
        deadline = time.time() + timeout
        seen_tokens = set()  # 중복 토큰 방지
        
        while time.time() < deadline:
            # 성능 최적화: 마지막 200줄만 캡처
            output = self.capture_tail(200)
            lines = output.splitlines()
            
            for line in lines:
                # 이미 본 토큰은 건너뛰기
                line_hash = hash(line)
                if line_hash in seen_tokens:
                    continue
                    
                if token_type == "ACK":
                    parsed = parse_ack(line)
                    if parsed and parsed.id == task_id:
                        seen_tokens.add(line_hash)
                        return True, "ACK_RECEIVED"
                        
                elif token_type == "RUN":
                    parsed = parse_run(line)
                    if parsed and parsed.id == task_id:
                        seen_tokens.add(line_hash)
                        return True, "RUN_RECEIVED"
                        
                elif token_type == "EOT":
                    parsed = parse_eot(line)
                    if parsed and parsed.id == task_id:
                        seen_tokens.add(line_hash)
                        return True, parsed.status
            
            time.sleep(self.poll_interval)
        
        # 타임아웃 시 디버깅용 스냅샷 추가
        snapshot = self.capture_tail(50)[-1024:]  # 마지막 1KB
        return False, f"NO_{token_type}|snapshot={snapshot}"
    
    def execute_with_handshake(
        self,
        command: str,
        task_id: str,
        timeout_ack: float = 5,
        timeout_run: float = 10,
        timeout_eot: float = 30
    ) -> HandshakeResult:
        """
        3단계 핸드셰이크로 명령 실행
        
        Args:
            command: 실행할 명령
            task_id: 작업 ID (멱등키로도 사용)
            timeout_ack: ACK 대기 타임아웃
            timeout_run: RUN 대기 타임아웃
            timeout_eot: EOT 대기 타임아웃
            
        Returns:
            HandshakeResult 객체
        """
        # 명령 전송
        self.send_keys(command)
        
        # 1. ACK 대기
        success, msg = self.wait_for_token(task_id, "ACK", timeout_ack)
        if not success:
            return HandshakeResult(
                success=False,
                status="FAILED",
                task_id=task_id,
                error=msg
            )
        
        # 2. RUN 대기
        success, msg = self.wait_for_token(task_id, "RUN", timeout_run)
        if not success:
            return HandshakeResult(
                success=False,
                status="FAILED",
                task_id=task_id,
                error=msg
            )
        
        # 3. EOT 대기
        success, status = self.wait_for_token(task_id, "EOT", timeout_eot)
        if not success:
            return HandshakeResult(
                success=False,
                status="TIMEOUT",
                task_id=task_id,
                error=status
            )
        
        return HandshakeResult(
            success=True,
            status=status,
            task_id=task_id
        )