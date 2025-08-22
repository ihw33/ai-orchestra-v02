"""
고급 시나리오 테스트 - 순서 역전, 노이즈, 특수문자 등
"""

import pytest
from unittest.mock import MagicMock, patch
from controllers.tmux_controller import TmuxController, HandshakeResult
from core.protocol import parse_ack, parse_run, parse_eot


class TestOutOfOrderTokens:
    """토큰 순서가 잘못된 경우 테스트"""
    
    def test_run_before_ack(self, mocker):
        """RUN이 ACK보다 먼저 오는 경우"""
        mocker.patch("subprocess.run")
        
        # RUN이 먼저 오므로 ACK를 못 찾고 타임아웃
        # poll_interval=0.0이고 timeout=0.5이므로 충분한 개수 필요
        output = "@@RUN id=t1\n"
        
        # side_effect 대신 return_value 사용 (항상 같은 값 반환)
        mocker.patch.object(
            TmuxController, 
            'capture_tail',
            return_value=output
        )
        
        ctl = TmuxController("%3", poll_interval=0.0)
        result = ctl.execute_with_handshake(
            "echo test",
            task_id="t1",
            timeout_ack=0.5,
            timeout_run=0.5,
            timeout_eot=0.5
        )
        
        # ACK를 기다리다 타임아웃
        assert not result.success
        assert "NO_ACK" in result.error
    
    def test_duplicate_tokens(self, mocker):
        """중복 토큰이 있는 경우"""
        mocker.patch("subprocess.run")
        
        # ACK 2번, RUN 2번, EOT 1번
        outputs = [
            "@@ACK id=t1\n@@ACK id=t1\n",
            "@@ACK id=t1\n@@ACK id=t1\n@@RUN id=t1\n",
            "@@ACK id=t1\n@@ACK id=t1\n@@RUN id=t1\n@@RUN id=t1\n",
            "@@ACK id=t1\n@@ACK id=t1\n@@RUN id=t1\n@@RUN id=t1\n@@EOT id=t1 status=OK\n"
        ]
        
        mocker.patch.object(
            TmuxController,
            'capture_tail',
            side_effect=outputs
        )
        
        ctl = TmuxController("%3", poll_interval=0.0)
        result = ctl.execute_with_handshake(
            "echo test",
            task_id="t1",
            timeout_ack=1,
            timeout_run=1,
            timeout_eot=1
        )
        
        # 중복이 있어도 첫 번째 유효 토큰으로 성공해야 함
        assert result.success
        assert result.status == "OK"


class TestNoisyOutput:
    """노이즈가 섞인 출력 테스트"""
    
    def test_tokens_with_noise(self, mocker):
        """토큰 사이에 노이즈가 있는 경우"""
        mocker.patch("subprocess.run")
        
        # 노이즈가 섞인 출력
        noisy_output = """
        [DEBUG] Starting process...
        [INFO] Connection established
        @@ACK id=t1
        [DEBUG] Processing request...
        Some random output here
        @@RUN id=t1 ts=123456
        [WARN] High memory usage
        @@EOT id=t1 status=OK dur_ms=500
        [INFO] Process completed
        """
        
        mocker.patch.object(
            TmuxController,
            'capture_tail',
            return_value=noisy_output
        )
        
        ctl = TmuxController("%3", poll_interval=0.0)
        result = ctl.execute_with_handshake(
            "echo test",
            task_id="t1",
            timeout_ack=1,
            timeout_run=1,
            timeout_eot=1
        )
        
        # 노이즈가 있어도 토큰을 찾아 성공해야 함
        assert result.success
        assert result.status == "OK"
    
    def test_colored_output(self, mocker):
        """컬러 코드가 포함된 출력"""
        mocker.patch("subprocess.run")
        
        # ANSI 컬러 코드가 포함된 출력
        colored_output = """
        \033[32m[SUCCESS]\033[0m Starting...
        \033[33m@@ACK id=t1\033[0m
        \033[34m[INFO]\033[0m Running...
        @@RUN id=t1
        \033[31m[ERROR]\033[0m But not really an error
        @@EOT id=t1 status=OK
        """
        
        mocker.patch.object(
            TmuxController,
            'capture_tail',
            return_value=colored_output
        )
        
        ctl = TmuxController("%3", poll_interval=0.0)
        result = ctl.execute_with_handshake(
            "echo test",
            task_id="t1",
            timeout_ack=1,
            timeout_run=1,
            timeout_eot=1
        )
        
        # 컬러 코드가 있어도 성공해야 함
        assert result.success


class TestSpecialCharacters:
    """특수문자 처리 테스트"""
    
    def test_safe_send_detection(self):
        """특수문자 감지 테스트"""
        ctl = TmuxController("%3")
        
        # 특수문자가 있는 경우
        assert ctl._needs_safe_send('echo "hello world"')
        assert ctl._needs_safe_send("echo 'test'")
        assert ctl._needs_safe_send("echo `date`")
        assert ctl._needs_safe_send("echo $HOME")
        assert ctl._needs_safe_send("echo hello\nworld")
        assert ctl._needs_safe_send("rm -rf /tmp/* && echo done")
        
        # 특수문자가 없는 경우
        assert not ctl._needs_safe_send("echo hello")
        assert not ctl._needs_safe_send("ls -la")
    
    def test_multiline_command(self, mocker):
        """여러 줄 명령어 테스트"""
        mocker.patch("subprocess.run")
        
        multiline_cmd = """echo "Line 1"
echo "Line 2"
echo "@@ACK id=multi"
echo "@@RUN id=multi"
echo "@@EOT id=multi status=OK"
"""
        
        # base64 인코딩된 명령이 전송되는지 확인
        run_mock = mocker.patch("subprocess.run")
        
        ctl = TmuxController("%3")
        ctl.send_keys(multiline_cmd)
        
        # base64 명령이 사용되었는지 확인
        calls = run_mock.call_args_list
        cmd_sent = str(calls[0])
        assert "base64" in cmd_sent or multiline_cmd in cmd_sent


class TestTimeoutSnapshot:
    """타임아웃 시 스냅샷 테스트"""
    
    def test_timeout_with_snapshot(self, mocker):
        """타임아웃 시 스냅샷이 포함되는지"""
        mocker.patch("subprocess.run")
        
        # ACK 없는 출력
        output = """
        Starting process...
        Waiting for input...
        Processing...
        Still processing...
        No tokens here!
        """
        
        mocker.patch.object(
            TmuxController,
            'capture_tail',
            return_value=output
        )
        
        ctl = TmuxController("%3", poll_interval=0.0)
        result = ctl.execute_with_handshake(
            "echo test",
            task_id="t1",
            timeout_ack=0.1,
            timeout_run=0.1,
            timeout_eot=0.1
        )
        
        # 실패하고 스냅샷이 포함되어야 함
        assert not result.success
        assert "NO_ACK" in result.error
        assert "snapshot=" in result.error


class TestCaptureOptimization:
    """캡처 최적화 테스트"""
    
    def test_capture_tail_performance(self, mocker):
        """capture_tail이 제한된 줄만 캡처하는지"""
        # 매우 긴 출력 시뮬레이션
        long_output = "\n".join([f"Line {i}" for i in range(10000)])
        
        run_mock = mocker.patch(
            "subprocess.run",
            return_value=MagicMock(
                stdout=long_output[-200:],  # 마지막 200줄만
                returncode=0
            )
        )
        
        ctl = TmuxController("%3")
        result = ctl.capture_tail(200)
        
        # capture-pane에 -S -200 옵션이 전달되었는지 확인
        run_mock.assert_called_once()
        args = run_mock.call_args[0][0]
        assert "-S" in args
        assert "-200" in args
    
    def test_capture_output_full(self, mocker):
        """capture_output이 전체를 캡처하는지"""
        full_output = "Full output test"
        
        run_mock = mocker.patch(
            "subprocess.run",
            return_value=MagicMock(
                stdout=full_output,
                returncode=0
            )
        )
        
        ctl = TmuxController("%3")
        result = ctl.capture_output()  # last_lines=None
        
        # -S 옵션이 없어야 함
        run_mock.assert_called_once()
        args = run_mock.call_args[0][0]
        assert "-S" not in args