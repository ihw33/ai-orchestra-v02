"""
Gemini CLI 어댑터 - tmux를 통한 Gemini 제어
"""

import re
import time
import subprocess
import base64
from typing import Optional
from dataclasses import dataclass

from adapters.base import BaseAdapter, AdapterConfig
from core.types import HandshakeResult


@dataclass
class GeminiConfig(AdapterConfig):
    """Gemini 어댑터 설정"""
    pane_id: str = "%1"  # tmux pane ID


class GeminiAdapter(BaseAdapter):
    """Gemini CLI 어댑터
    
    tmux pane에서 실행 중인 Gemini CLI와 통신
    프롬프트 엔지니어링으로 @@ACK/@@RUN/@@EOT 출력 강제
    """
    
    # Gemini 프롬프트 템플릿
    CALC_PROMPT = """아래 세 줄을 정확히 복사해서 출력하세요. 단, result={placeholder} 부분만 계산 결과로 바꾸세요:

@@ACK id={task_id}
@@RUN id={task_id}
@@EOT id={task_id} status=OK result={placeholder}

계산할 식: {expression}
예시: 1+1이면 result=2로 바꿔서 출력"""
    
    GENERAL_PROMPT = """다음 3줄을 정확히 순서대로 출력하세요:

@@ACK id={task_id}
@@RUN id={task_id}
(작업 수행 후)
@@EOT id={task_id} status=OK

작업: {command}"""
    
    def __init__(self, config: GeminiConfig):
        super().__init__(config)
        self.pane_id = config.pane_id
        self.session_name = config.tmux_session if hasattr(config, 'tmux_session') else 'gemini-cli'
        
        # 로거 설정
        import logging
        self.logger = logging.getLogger(f"GeminiAdapter[{self.pane_id}]")
        self.logger.setLevel(logging.INFO)
        
        # 세션 확인 및 생성
        self.ensure_session()
        self.verify_pane_exists()
    
    def ensure_session(self):
        """tmux 세션이 없으면 자동 생성"""
        try:
            # 세션 존재 확인
            result = subprocess.run(
                f"tmux has-session -t {self.session_name} 2>/dev/null",
                shell=True,
                capture_output=True
            )
            
            if result.returncode != 0:
                self.logger.info(f"Creating tmux session: {self.session_name}")
                # 세션 생성
                subprocess.run(
                    f"tmux new-session -d -s {self.session_name}",
                    shell=True,
                    check=True
                )
                # Gemini CLI 시작
                time.sleep(0.5)
                subprocess.run(
                    f"tmux send-keys -t {self.session_name}:0.0 'gemini' Enter",
                    shell=True,
                    check=True
                )
                time.sleep(1.0)  # CLI 초기화 대기
                self.logger.info(f"Gemini CLI started in session {self.session_name}")
                
                # pane_id 업데이트 (세션:윈도우.pane 형식으로)
                if self.pane_id.startswith('%'):
                    self.pane_id = f"{self.session_name}:0.0"
        except Exception as e:
            self.logger.warning(f"Could not ensure session: {e}")
    
    def health_check(self) -> bool:
        """세션 및 Gemini CLI 상태 확인"""
        try:
            # pane 출력 캡처
            output = subprocess.check_output(
                f"tmux capture-pane -t {self.pane_id} -p -S -3",
                shell=True,
                text=True,
                stderr=subprocess.DEVNULL
            )
            # Gemini 프롬프트나 응답이 있는지 확인
            return bool(output and len(output.strip()) > 0)
        except Exception:
            return False
    
    def verify_pane_exists(self):
        """tmux pane 존재 확인"""
        try:
            # 세션:윈도우.pane 형식 또는 pane ID 형식 모두 지원
            if ":" in self.pane_id or "." in self.pane_id:
                # 세션 형식 확인 (예: gemini-cli:0.0)
                result = subprocess.run(
                    f"tmux list-panes -t {self.pane_id} 2>/dev/null",
                    shell=True,
                    capture_output=True
                )
            else:
                # pane ID 형식 확인 (예: %1)
                result = subprocess.run(
                    f"tmux list-panes -F '#{{pane_id}}' | grep -q {self.pane_id}",
                    shell=True,
                    capture_output=True
                )
            
            if result.returncode != 0:
                # 디버깅을 위해 사용 가능한 pane 목록 출력
                available = subprocess.run(
                    "tmux list-panes -a -F '#{session_name}:#{window_index}.#{pane_index} (#{pane_id})'",
                    shell=True,
                    capture_output=True,
                    text=True
                )
                self.logger.error(f"Available panes:\n{available.stdout}")
                raise RuntimeError(f"tmux pane {self.pane_id} not found")
        except Exception as e:
            raise RuntimeError(f"Failed to verify tmux pane: {e}")
    
    def send_to_pane(self, text: str, retry_count: int = 1) -> bool:
        """tmux pane에 텍스트 전송 (재시도 포함)"""
        for attempt in range(retry_count + 1):
            try:
                # 세션 상태 확인
                if attempt > 0:
                    self.ensure_session()
                    time.sleep(0.5 * (2 ** attempt))  # 지수 백오프
                
                # base64 인코딩으로 안전하게 전송
                b64 = base64.b64encode(text.encode()).decode()
                
                # tmux 버퍼에 로드
                cmd = f"printf '%s' '{b64}' | base64 -d | tmux load-buffer -"
                subprocess.run(cmd, shell=True, check=True)
                
                # 버퍼 내용을 pane에 붙여넣기
                subprocess.run(f"tmux paste-buffer -t {self.pane_id}", shell=True, check=True)
                
                # Enter 키 전송
                subprocess.run(f"tmux send-keys -t {self.pane_id} Enter", shell=True, check=True)
                
                return True
            except subprocess.CalledProcessError as e:
                if attempt == retry_count:
                    self.logger.error(f"Failed to send to tmux after {retry_count + 1} attempts: {e}")
                    return False
                self.logger.warning(f"Attempt {attempt + 1} failed, retrying...")
        return False
    
    def capture_output(self, lines: int = 200) -> str:
        """tmux pane 출력 캡처"""
        try:
            result = subprocess.run(
                f"tmux capture-pane -t {self.pane_id} -p -S -{lines}",
                shell=True,
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Failed to capture output: {e}")
            return ""
    
    def wait_for_pattern(self, pattern: str, timeout: float) -> Optional[re.Match]:
        """패턴이 나타날 때까지 대기"""
        regex = re.compile(pattern, re.MULTILINE)
        deadline = time.time() + timeout
        
        while time.time() < deadline:
            output = self.capture_output()
            match = regex.search(output)
            if match:
                return match
            time.sleep(0.5)
        
        return None
    
    def execute_with_handshake(self, exec_line: str, task_id: str) -> HandshakeResult:
        """EXEC 명령 실행 with 3-step handshake"""
        
        # EXEC 파싱
        from core.exec_parser import parse_exec
        parsed = parse_exec(exec_line)
        
        if not parsed:
            return HandshakeResult(
                success=False,
                status="INVALID_EXEC",
                error=f"Failed to parse: {exec_line}",
                task_id=task_id
            )
        
        # 프롬프트 생성
        verb = parsed.verb
        
        if verb == "CALC":
            expr = parsed.params.get("expr", "").strip('"')
            prompt = self.CALC_PROMPT.format(
                task_id=task_id,
                expression=expr,
                placeholder="{result}"
            )
        else:
            prompt = self.GENERAL_PROMPT.format(
                task_id=task_id,
                command=exec_line
            )
        
        self.logger.info(f"Executing {verb} for task {task_id}")
        
        # 1. 프롬프트 전송
        if not self.send_to_pane(prompt):
            return HandshakeResult(
                success=False,
                status="SEND_FAILED",
                error="Failed to send prompt to Gemini",
                task_id=task_id
            )
        
        # 2. ACK 대기
        self.logger.debug(f"Waiting for ACK (timeout={self.config.timeout_ack}s)")
        ack_pattern = f"@@ACK\\s+id={re.escape(task_id)}"
        if not self.wait_for_pattern(ack_pattern, self.config.timeout_ack):
            return HandshakeResult(
                success=False,
                status="ACK_TIMEOUT",
                error=f"No ACK received within {self.config.timeout_ack}s",
                task_id=task_id
            )
        self.logger.debug("ACK received")
        
        # 3. RUN 대기
        self.logger.debug(f"Waiting for RUN (timeout={self.config.timeout_run}s)")
        run_pattern = f"@@RUN\\s+id={re.escape(task_id)}"
        if not self.wait_for_pattern(run_pattern, self.config.timeout_run):
            return HandshakeResult(
                success=False,
                status="RUN_TIMEOUT",
                error=f"No RUN received within {self.config.timeout_run}s",
                task_id=task_id
            )
        self.logger.debug("RUN received")
        
        # 4. EOT 대기 및 결과 추출
        self.logger.debug(f"Waiting for EOT (timeout={self.config.timeout_eot}s)")
        
        if verb == "CALC":
            # CALC의 경우 result 값 추출 - 더 유연한 패턴
            # @ 1~2개, 공백 허용, answer/result 키 허용
            eot_pattern = (
                f"\\s*@{{1,2}}EOT\\s+id={re.escape(task_id)}\\s+"
                f"status\\s*=\\s*OK\\s+"
                f"(?:answer|result)\\s*=\\s*([\\d\\.\\-]+)\\s*"
            )
            match = self.wait_for_pattern(eot_pattern, self.config.timeout_eot)
            
            if match:
                result_value = match.group(1)
                self.logger.info(f"Task {task_id} completed with result: {result_value}")
                return HandshakeResult(
                    success=True,
                    status=f"OK:RESULT={result_value}",
                    task_id=task_id
                )
        else:
            # 일반 명령 - 더 유연한 패턴
            eot_pattern = f"\\s*@{{1,2}}EOT\\s+id={re.escape(task_id)}\\s+status\\s*=\\s*(\\w+)"
            match = self.wait_for_pattern(eot_pattern, self.config.timeout_eot)
            
            if match:
                status = match.group(1)
                self.logger.info(f"Task {task_id} completed with status: {status}")
                return HandshakeResult(
                    success=True,
                    status=status,
                    task_id=task_id
                )
        
        # EOT 타임아웃
        return HandshakeResult(
            success=False,
            status="EOT_TIMEOUT",
            error=f"No EOT received within {self.config.timeout_eot}s",
            task_id=task_id
        )
    
    def send(self, message: str) -> None:
        """메시지 전송 (BaseAdapter 인터페이스)"""
        if not self.send_to_pane(message):
            raise RuntimeError(f"Failed to send message to {self.pane_id}")
    
    def receive(self, timeout: Optional[float] = None) -> str:
        """메시지 수신 (BaseAdapter 인터페이스)"""
        return self.capture_output()
    
    def cleanup(self):
        """리소스 정리"""
        self.logger.info(f"Gemini adapter cleanup for pane {self.pane_id}")
        # tmux pane은 유지 (Gemini CLI 세션 보존)