"""
EXEC DSL 파서 테스트
"""

import pytest
from core.exec_parser import ExecParser, ExecCommand, parse_exec, validate_exec, format_exec


class TestExecParser:
    """EXEC 파서 테스트"""
    
    def setup_method(self):
        self.parser = ExecParser()
    
    def test_parse_simple_command(self):
        """단순 명령 파싱"""
        cmd = self.parser.parse("TEST module=auth")
        assert cmd.verb == "TEST"
        assert cmd.params == {"module": "auth"}
        assert cmd.payload is None
    
    def test_parse_multiple_params(self):
        """다중 파라미터 파싱"""
        cmd = self.parser.parse("IMPLEMENT feature=login language=python framework=fastapi")
        assert cmd.verb == "IMPLEMENT"
        assert cmd.params == {
            "feature": "login",
            "language": "python",
            "framework": "fastapi"
        }
    
    def test_parse_quoted_values(self):
        """따옴표 값 파싱"""
        cmd = self.parser.parse('ANALYZE task="code review" scope="security audit"')
        assert cmd.verb == "ANALYZE"
        assert cmd.params == {
            "task": "code review",
            "scope": "security audit"
        }
    
    def test_parse_with_payload(self):
        """페이로드 포함 파싱"""
        exec_line = """TEST module=auth
--
def test_login():
    assert login("user", "pass") == True"""
        
        cmd = self.parser.parse(exec_line)
        assert cmd.verb == "TEST"
        assert cmd.params == {"module": "auth"}
        assert "def test_login" in cmd.payload
    
    def test_parse_inline_payload(self):
        """인라인 페이로드 파싱"""
        cmd = self.parser.parse("REVIEW pr=123 -- quick fix")
        assert cmd.verb == "REVIEW"
        assert cmd.params == {"pr": "123"}
        assert cmd.payload == "quick fix"
    
    def test_parse_escaped_quotes(self):
        """이스케이프된 따옴표 파싱"""
        cmd = self.parser.parse('TEST name="say \\"hello\\""')
        assert cmd.params["name"] == 'say "hello"'
    
    def test_parse_empty_command_raises(self):
        """빈 명령 에러"""
        with pytest.raises(ValueError, match="Empty EXEC command"):
            self.parser.parse("")
        
        with pytest.raises(ValueError, match="Empty EXEC command"):
            self.parser.parse("   ")
    
    def test_parse_unknown_verb_raises(self):
        """알 수 없는 VERB 에러"""
        with pytest.raises(ValueError, match="Unknown VERB: INVALID"):
            self.parser.parse("INVALID module=test")
    
    def test_verb_case_insensitive(self):
        """VERB 대소문자 무시"""
        cmd = self.parser.parse("test module=auth")
        assert cmd.verb == "TEST"
        
        cmd = self.parser.parse("ImPlEmEnT feature=login")
        assert cmd.verb == "IMPLEMENT"
    
    def test_validate_missing_task_id(self):
        """task_id 누락 검증"""
        cmd = ExecCommand(verb="TEST", params={"module": "auth"})
        valid, error = self.parser.validate(cmd)
        assert valid is False
        assert "task_id" in error
    
    def test_validate_test_missing_module(self):
        """TEST 명령 module 누락"""
        cmd = ExecCommand(verb="TEST", params={"task_id": "T001"})
        valid, error = self.parser.validate(cmd)
        assert valid is False
        assert "module" in error
    
    def test_validate_implement_missing_feature(self):
        """IMPLEMENT 명령 feature 누락"""
        cmd = ExecCommand(verb="IMPLEMENT", params={"task_id": "I001"})
        valid, error = self.parser.validate(cmd)
        assert valid is False
        assert "feature" in error
    
    def test_validate_trigger_no_task_id_required(self):
        """TRIGGER는 task_id 불필요"""
        cmd = ExecCommand(verb="TRIGGER", params={"routine": "daily"})
        valid, error = self.parser.validate(cmd)
        assert valid is True
        assert error is None
    
    def test_format_simple_command(self):
        """명령 포맷팅"""
        cmd = ExecCommand(
            verb="TEST",
            params={"task_id": "T001", "module": "auth"}
        )
        formatted = self.parser.format(cmd)
        assert formatted == "TEST task_id=T001 module=auth"
    
    def test_format_with_quotes(self):
        """따옴표 필요한 값 포맷팅"""
        cmd = ExecCommand(
            verb="ANALYZE",
            params={"task_id": "A001", "scope": "code review"}
        )
        formatted = self.parser.format(cmd)
        assert 'scope="code review"' in formatted
    
    def test_format_with_payload(self):
        """페이로드 포함 포맷팅"""
        cmd = ExecCommand(
            verb="TEST",
            params={"task_id": "T001", "module": "auth"},
            payload="def test():\n    pass"
        )
        formatted = self.parser.format(cmd)
        assert "TEST task_id=T001 module=auth" in formatted
        assert "\n--\n" in formatted
        assert "def test():" in formatted
    
    def test_roundtrip(self):
        """파싱-포맷 왕복 테스트"""
        original = 'IMPLEMENT task_id=I001 feature="user login" language=python'
        cmd = self.parser.parse(original)
        formatted = self.parser.format(cmd)
        cmd2 = self.parser.parse(formatted)
        
        assert cmd.verb == cmd2.verb
        assert cmd.params == cmd2.params
    
    def test_global_functions(self):
        """전역 함수 테스트"""
        cmd = parse_exec("TEST task_id=T001 module=auth")
        assert cmd.verb == "TEST"
        
        valid, error = validate_exec(cmd)
        assert valid is True
        
        formatted = format_exec(cmd)
        assert "TEST task_id=T001 module=auth" == formatted