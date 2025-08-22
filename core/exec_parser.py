"""
EXEC DSL 파서 - v1.0 사양 준수
"""

import re
from typing import Dict, Optional, Tuple
from dataclasses import dataclass


@dataclass
class ExecCommand:
    """파싱된 EXEC 명령"""
    verb: str
    params: Dict[str, str]
    payload: Optional[str] = None
    raw: str = ""


class ExecParser:
    """EXEC v1.0 파서
    
    문법:
        EXEC_LINE  ::= VERB PARAMS [PAYLOAD]
        VERB       ::= "TEST" | "IMPLEMENT" | "ANALYZE" | "REVIEW" | ...
        PARAMS     ::= KEY "=" VALUE { " " KEY "=" VALUE }
        KEY        ::= [a-zA-Z_][a-zA-Z0-9_]*
        VALUE      ::= [a-zA-Z0-9._-]+ | '"' [^"]* '"'
        PAYLOAD    ::= "--" NEWLINE MULTILINE_TEXT
    """
    
    # 허용된 VERB 목록
    ALLOWED_VERBS = {
        "TEST", "IMPLEMENT", "ANALYZE", "REVIEW",
        "DEPLOY", "MONITOR", "ROLLBACK", "REPORT",
        "TRIGGER", "SYNC", "CALC", "TRANSLATE", "SUMMARIZE"
    }
    
    # 파라미터 패턴: key=value 또는 key="quoted value"
    PARAM_PATTERN = re.compile(
        r'([a-zA-Z_][a-zA-Z0-9_]*)=("(?:[^"\\]|\\.)*"|[a-zA-Z0-9._-]+)'
    )
    
    def parse(self, exec_line: str) -> ExecCommand:
        """EXEC 명령 파싱
        
        Args:
            exec_line: EXEC DSL 명령 문자열
            
        Returns:
            파싱된 ExecCommand 객체
            
        Raises:
            ValueError: 문법 오류 시
        """
        if not exec_line or not exec_line.strip():
            raise ValueError("Empty EXEC command")
        
        lines = exec_line.strip().split('\n')
        first_line = lines[0].strip()
        
        # 페이로드 확인 (-- 이후 모든 내용)
        payload = None
        if len(lines) > 1 and lines[1].strip() == "--":
            payload = '\n'.join(lines[2:])
            # 첫 줄만 파싱
        elif '--' in first_line:
            # 같은 줄에 -- 있는 경우
            parts = first_line.split('--', 1)
            first_line = parts[0].strip()
            if len(parts) > 1:
                payload = parts[1].strip()
        
        # VERB 추출
        parts = first_line.split(None, 1)
        if not parts:
            raise ValueError("No VERB found in EXEC command")
        
        verb = parts[0].upper()
        if verb not in self.ALLOWED_VERBS:
            raise ValueError(f"Unknown VERB: {verb}")
        
        # 파라미터 파싱
        params = {}
        if len(parts) > 1:
            param_string = parts[1]
            for match in self.PARAM_PATTERN.finditer(param_string):
                key = match.group(1)
                value = match.group(2)
                # 따옴표 제거
                if value.startswith('"') and value.endswith('"'):
                    value = value[1:-1]
                    # 이스케이프 처리
                    value = value.replace('\\"', '"').replace('\\\\', '\\')
                params[key] = value
        
        return ExecCommand(
            verb=verb,
            params=params,
            payload=payload,
            raw=exec_line
        )
    
    def validate(self, command: ExecCommand) -> Tuple[bool, Optional[str]]:
        """명령 검증
        
        Returns:
            (유효 여부, 에러 메시지)
        """
        # 필수 파라미터 체크
        if 'task_id' not in command.params and command.verb != 'TRIGGER':
            return False, "Missing required parameter: task_id"
        
        # VERB별 검증
        if command.verb == 'TEST':
            if 'module' not in command.params:
                return False, "TEST requires 'module' parameter"
        elif command.verb == 'IMPLEMENT':
            if 'feature' not in command.params:
                return False, "IMPLEMENT requires 'feature' parameter"
        elif command.verb == 'DEPLOY':
            if 'target' not in command.params:
                return False, "DEPLOY requires 'target' parameter"
        elif command.verb == 'CALC':
            # 수식 유효성 검사
            if 'expr' not in command.params:
                return False, "CALC requires 'expr' parameter"
            
            expr = command.params['expr'].strip('"')
            valid, error = self.validate_math_expression(expr)
            if not valid:
                return False, f"Invalid math expression: {error}"
        
        return True, None
    
    def validate_math_expression(self, expr: str) -> Tuple[bool, Optional[str]]:
        """수학 표현식 유효성 검사
        
        Args:
            expr: 검사할 수식
            
        Returns:
            (유효 여부, 에러 메시지)
        """
        # 빈 문자열 체크
        if not expr or not expr.strip():
            return False, "Empty expression"
        
        # 길이 제한 (인젝션 방지)
        if len(expr) > 100:
            return False, "Expression too long (max 100 characters)"
        
        # 허용된 문자만 포함하는지 체크 (숫자, 연산자, 괄호, 공백)
        allowed_pattern = re.compile(r'^[0-9+\-*/().\s]+$')
        if not allowed_pattern.match(expr):
            return False, "Expression contains invalid characters"
        
        # 위험한 패턴 체크
        dangerous_patterns = [
            r'//+',  # 주석
            r'\*\*',  # 거듭제곱 (파이썬)
            r'[a-zA-Z_]',  # 변수나 함수 이름
            r'[;\[\]{}]',  # 위험한 구분자
        ]
        
        for pattern in dangerous_patterns:
            if re.search(pattern, expr):
                return False, f"Expression contains forbidden pattern: {pattern}"
        
        # 괄호 균형 체크
        open_count = expr.count('(')
        close_count = expr.count(')')
        if open_count != close_count:
            return False, "Unbalanced parentheses"
        
        # 연속된 연산자 체크
        if re.search(r'[+\-*/]{2,}', expr.replace('--', '').replace('++', '')):
            return False, "Consecutive operators detected"
        
        # 파이썬 ast를 사용한 안전한 평가 가능 여부 체크
        try:
            import ast
            # 수식을 AST로 파싱
            tree = ast.parse(expr, mode='eval')
            # 허용된 노드 타입만 있는지 체크
            allowed_nodes = (
                ast.Expression, ast.BinOp, ast.UnaryOp,
                ast.Add, ast.Sub, ast.Mult, ast.Div,
                ast.USub, ast.UAdd, ast.Constant, ast.Num
            )
            for node in ast.walk(tree):
                if not isinstance(node, allowed_nodes):
                    return False, f"Unsafe operation detected: {type(node).__name__}"
        except (SyntaxError, ValueError) as e:
            return False, f"Invalid syntax: {str(e)}"
        
        return True, None
    
    def format(self, command: ExecCommand) -> str:
        """ExecCommand를 EXEC DSL 문자열로 변환"""
        parts = [command.verb]
        
        # 파라미터 추가
        for key, value in command.params.items():
            # 공백이나 특수문자 있으면 따옴표
            if ' ' in value or '"' in value or '=' in value:
                value = '"' + value.replace('\\', '\\\\').replace('"', '\\"') + '"'
            parts.append(f"{key}={value}")
        
        result = ' '.join(parts)
        
        # 페이로드 추가
        if command.payload:
            result += '\n--\n' + command.payload
        
        return result


# 싱글톤 인스턴스
_parser = ExecParser()

def parse_exec(exec_line: str) -> ExecCommand:
    """전역 파서 함수"""
    return _parser.parse(exec_line)

def validate_exec(command: ExecCommand) -> Tuple[bool, Optional[str]]:
    """전역 검증 함수"""
    return _parser.validate(command)

def format_exec(command: ExecCommand) -> str:
    """전역 포맷 함수"""
    return _parser.format(command)