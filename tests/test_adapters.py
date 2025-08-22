"""
어댑터 시스템 테스트
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
from adapters import register_adapter, get_adapter, list_adapters
from adapters.base import BaseAdapter, AdapterConfig
from adapters.tmux_adapter import TmuxAdapter
from core.types import HandshakeResult


class TestAdapterRegistry:
    """어댑터 레지스트리 테스트"""
    
    def test_register_and_get_adapter(self):
        """어댑터 등록 및 조회"""
        # Mock 어댑터 클래스
        class MockAdapter(BaseAdapter):
            def send(self, message: str) -> None:
                pass
            
            def receive(self, timeout=None) -> str:
                return "mock response"
            
            def execute_with_handshake(self, exec_line, task_id):
                return HandshakeResult(success=True, status="OK")
        
        # 등록
        register_adapter("mock", MockAdapter)
        
        # 조회
        adapter_class = get_adapter("mock")
        assert adapter_class == MockAdapter
        
        # 목록 확인
        adapters = list_adapters()
        assert "mock" in adapters
    
    def test_get_nonexistent_adapter(self):
        """존재하지 않는 어댑터 조회"""
        adapter_class = get_adapter("nonexistent")
        assert adapter_class is None


class TestTmuxAdapter:
    """TmuxAdapter 테스트"""
    
    @patch('adapters.tmux_adapter.TmuxController')
    def test_tmux_adapter_initialization(self, mock_controller_class):
        """TmuxAdapter 초기화"""
        config = AdapterConfig(name="tmux")
        adapter = TmuxAdapter(config, "%3")
        
        assert adapter.pane_id == "%3"
        assert adapter.config.name == "tmux"
        mock_controller_class.assert_called_once_with("%3")
    
    @patch('adapters.tmux_adapter.TmuxController')
    def test_tmux_adapter_send(self, mock_controller_class):
        """TmuxAdapter send 메서드"""
        mock_controller = Mock()
        mock_controller_class.return_value = mock_controller
        
        config = AdapterConfig(name="tmux")
        adapter = TmuxAdapter(config, "%3")
        
        adapter.send("test message")
        mock_controller.send_keys.assert_called_once_with("test message")
    
    @patch('adapters.tmux_adapter.TmuxController')
    def test_tmux_adapter_receive(self, mock_controller_class):
        """TmuxAdapter receive 메서드"""
        mock_controller = Mock()
        mock_controller.capture_tail.return_value = "captured output"
        mock_controller_class.return_value = mock_controller
        
        config = AdapterConfig(name="tmux")
        adapter = TmuxAdapter(config, "%3")
        
        result = adapter.receive()
        assert result == "captured output"
        mock_controller.capture_tail.assert_called_once_with(200)
    
    @patch('adapters.tmux_adapter.TmuxController')
    def test_tmux_adapter_handshake_success(self, mock_controller_class):
        """TmuxAdapter 핸드셰이크 성공"""
        mock_controller = Mock()
        mock_result = HandshakeResult(
            success=True,
            status="SUCCESS",
            error=None
        )
        mock_controller.execute_with_handshake.return_value = mock_result
        mock_controller_class.return_value = mock_controller
        
        config = AdapterConfig(
            name="tmux",
            timeout_ack=5.0,
            timeout_run=10.0,
            timeout_eot=30.0
        )
        adapter = TmuxAdapter(config, "%3")
        
        result = adapter.execute_with_handshake(
            exec_line="TEST module=auth",
            task_id="TEST_001"
        )
        
        assert result.success is True
        assert result.status == "SUCCESS"
        
        mock_controller.execute_with_handshake.assert_called_once_with(
            command="TEST module=auth",
            task_id="TEST_001",
            timeout_ack=5.0,
            timeout_run=10.0,
            timeout_eot=30.0
        )
    
    @patch('adapters.tmux_adapter.TmuxController')
    def test_tmux_adapter_handshake_failure(self, mock_controller_class):
        """TmuxAdapter 핸드셰이크 실패"""
        mock_controller = Mock()
        mock_result = HandshakeResult(
            success=False,
            status="TIMEOUT",
            error="ACK timeout exceeded"
        )
        mock_controller.execute_with_handshake.return_value = mock_result
        mock_controller_class.return_value = mock_controller
        
        config = AdapterConfig(name="tmux")
        adapter = TmuxAdapter(config, "%3")
        
        result = adapter.execute_with_handshake(
            exec_line="TEST module=broken",
            task_id="TEST_002"
        )
        
        assert result.success is False
        assert result.error == "ACK timeout exceeded"
    
    def test_parse_exec_with_payload(self):
        """페이로드 포함 EXEC 파싱"""
        config = AdapterConfig(name="tmux")
        adapter = TmuxAdapter(config, "%3")
        
        exec_line = """ANALYZE type=security
--
def vulnerable():
    exec(user_input)"""
        
        params = adapter.parse_exec(exec_line)
        assert params['verb'] == 'ANALYZE'
        assert params['type'] == 'security'
        assert 'payload' in params
        assert 'vulnerable' in params['payload']