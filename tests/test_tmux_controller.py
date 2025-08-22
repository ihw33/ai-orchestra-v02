import pytest
from unittest.mock import MagicMock, patch
from controllers.tmux_controller import TmuxController, HandshakeResult


def test_exec_handshake_success(mocker):
    """성공적인 핸드셰이크 테스트"""
    # send-keys는 눈감고, capture-pane만 시뮬레이션
    mocker.patch("subprocess.run")
    mocker.patch(
        "subprocess.run",
        side_effect=[
            MagicMock(returncode=0),  # send_keys command
            MagicMock(returncode=0),  # send_keys Enter
            MagicMock(returncode=0, stdout=""),  # 첫 캡처
            MagicMock(returncode=0, stdout="@@ACK id=t1\n"),  # ACK 캡처
            MagicMock(returncode=0, stdout="@@ACK id=t1\n@@RUN id=t1 ts=1\n"),  # RUN 캡처
            MagicMock(returncode=0, stdout="@@ACK id=t1\n@@RUN id=t1 ts=1\n@@EOT id=t1 status=OK\n"),  # EOT 캡처
        ]
    )
    
    ctl = TmuxController(pane_id="%3", poll_interval=0.0)
    result = ctl.execute_with_handshake(
        "echo hello", 
        task_id="t1", 
        timeout_ack=1, 
        timeout_run=1, 
        timeout_eot=1
    )
    assert result.success
    assert result.status == "OK"
    assert result.task_id == "t1"


def test_exec_handshake_no_ack(mocker):
    """ACK 없음 테스트"""
    mocker.patch("subprocess.run")
    mocker.patch.object(
        TmuxController,
        'capture_tail',
        return_value="no ack here\n"
    )
    
    ctl = TmuxController(pane_id="%3", poll_interval=0.0)
    result = ctl.execute_with_handshake(
        "echo hello",
        task_id="t1",
        timeout_ack=0.1,
        timeout_run=0.1,
        timeout_eot=0.1
    )
    assert not result.success
    assert "NO_ACK" in result.error


def test_send_keys_error(mocker):
    """send_keys 실패 테스트"""
    import subprocess
    mocker.patch(
        "subprocess.run",
        side_effect=subprocess.CalledProcessError(1, "tmux")
    )
    
    ctl = TmuxController(pane_id="%3")
    with pytest.raises(RuntimeError):
        ctl.send_keys("test")