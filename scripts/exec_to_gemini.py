#!/usr/bin/env python3
"""
EXEC 메시지를 받아 Gemini에게 전달하고 결과를 받아오는 스크립트
"""

import argparse
import sys
import os
import re
import time
import subprocess
import base64
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.exec_parser import parse_exec
from core.protocol import format_ack, format_run, format_eot

# 프롬프트 템플릿
GEMINI_PROMPT_TEMPLATE = """다음 지시를 정확히 따라주세요:

1. 아래 3개의 토큰을 반드시 순서대로 출력하세요.
2. 추가 설명이나 코드 블록 없이 평문으로만 출력하세요.

@@ACK id={task_id}
@@RUN id={task_id}
@@EOT id={task_id} status=OK result={result}

계산할 식: {expression}

규칙:
- result= 뒤에는 계산 결과 숫자만 (예: result=2)
- 반드시 위 3줄을 순서대로 출력
- 추가 텍스트 없음
"""

def send_to_tmux(pane_id: str, text: str):
    """tmux pane에 텍스트 전송 (base64 인코딩으로 안전하게)"""
    try:
        # base64로 인코딩하여 특수문자 문제 방지
        b64 = base64.b64encode(text.encode()).decode()
        
        # tmux 버퍼에 로드하고 붙여넣기
        cmd = f"printf '%s' '{b64}' | base64 -d | tmux load-buffer -"
        subprocess.run(cmd, shell=True, check=True)
        
        # 버퍼 내용을 pane에 붙여넣기
        subprocess.run(f"tmux paste-buffer -t {pane_id}", shell=True, check=True)
        
        # Enter 키 전송
        subprocess.run(f"tmux send-keys -t {pane_id} Enter", shell=True, check=True)
        
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error sending to tmux: {e}", file=sys.stderr)
        return False

def capture_tmux_output(pane_id: str, lines: int = 200) -> str:
    """tmux pane의 출력 캡처"""
    try:
        result = subprocess.run(
            f"tmux capture-pane -t {pane_id} -p -S -{lines}",
            shell=True,
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Error capturing tmux output: {e}", file=sys.stderr)
        return ""

def wait_for_token(pane_id: str, pattern: str, timeout: int = 10) -> tuple[bool, str]:
    """특정 토큰이 나타날 때까지 대기"""
    deadline = time.time() + timeout
    regex = re.compile(pattern, re.MULTILINE)
    
    while time.time() < deadline:
        output = capture_tmux_output(pane_id)
        match = regex.search(output)
        if match:
            return True, match.group(0) if match.lastindex == 0 else match.groups()
        time.sleep(0.5)
    
    return False, None

def execute_calc_via_gemini(exec_msg: str, pane_id: str) -> str:
    """CALC 명령을 Gemini를 통해 실행"""
    import logging
    logging.basicConfig(level=logging.INFO, 
                       format='%(asctime)s - %(levelname)s - %(message)s')
    logger = logging.getLogger(__name__)
    
    # EXEC 파싱
    try:
        parsed = parse_exec(exec_msg)
    except Exception as e:
        logger.error(f"Failed to parse EXEC: {e}")
        raise ValueError(f"Invalid EXEC message: {exec_msg}")
    
    if parsed.verb != "CALC":
        raise ValueError(f"Expected CALC verb, got: {parsed.verb}")
    
    expr = parsed.params.get("expr", "").strip('"')
    task_id = parsed.params.get("task", parsed.params.get("task_id", "UNKNOWN"))
    
    # 수식 유효성 검사
    from core.exec_parser import ExecParser
    parser = ExecParser()
    valid, error = parser.validate_math_expression(expr)
    if not valid:
        logger.error(f"Invalid math expression: {error}")
        raise ValueError(f"Invalid math expression: {error}")
    
    # 프롬프트 생성
    prompt = GEMINI_PROMPT_TEMPLATE.format(
        task_id=task_id,
        expression=expr,
        result="{result}"  # 템플릿 유지
    )
    
    print(f"[INFO] Sending to Gemini pane {pane_id}:")
    print(f"  Task: {task_id}")
    print(f"  Expression: {expr}")
    
    # 1. 프롬프트 전송
    if not send_to_tmux(pane_id, prompt):
        raise RuntimeError("Failed to send prompt to Gemini")
    
    # 2. ACK 대기
    print("[INFO] Waiting for @@ACK...")
    success, _ = wait_for_token(pane_id, f"@@ACK\\s+id={re.escape(task_id)}", timeout=5)
    if not success:
        raise TimeoutError(f"ACK timeout for task {task_id}")
    print("[OK] ACK received")
    
    # 3. RUN 대기
    print("[INFO] Waiting for @@RUN...")
    success, _ = wait_for_token(pane_id, f"@@RUN\\s+id={re.escape(task_id)}", timeout=10)
    if not success:
        raise TimeoutError(f"RUN timeout for task {task_id}")
    print("[OK] RUN received")
    
    # 4. EOT 대기 및 결과 추출 (더 유연한 패턴)
    print("[INFO] Waiting for @@EOT...")
    # @ 1~2개, 공백 허용, answer/result 키 허용
    eot_pattern = (
        f"\\s*@{{1,2}}EOT\\s+id={re.escape(task_id)}\\s+"
        f"status\\s*=\\s*OK\\s+"
        f"(?:answer|result)\\s*=\\s*([\\d\\.\\-]+)"
    )
    success, match = wait_for_token(pane_id, eot_pattern, timeout=30)
    if not success:
        raise TimeoutError(f"EOT timeout for task {task_id}")
    
    result = match[0] if isinstance(match, tuple) else match.split("result=")[1].strip()
    print(f"[OK] EOT received with result: {result}")
    
    return result

def execute_calc_mock(exec_msg: str) -> str:
    """Mock 모드: 실제 Gemini 없이 안전하게 계산"""
    import ast
    import operator
    
    parsed = parse_exec(exec_msg)
    expr = parsed.params.get("expr", "").strip('"')
    
    # ast를 사용한 안전한 평가
    ops = {
        ast.Add: operator.add,
        ast.Sub: operator.sub,
        ast.Mult: operator.mul,
        ast.Div: operator.truediv,
        ast.USub: operator.neg,
    }
    
    def eval_expr(node):
        if isinstance(node, ast.Num):  # Python 3.7 이하
            return node.n
        elif isinstance(node, ast.Constant):  # Python 3.8+
            return node.value
        elif isinstance(node, ast.BinOp):
            return ops[type(node.op)](eval_expr(node.left), eval_expr(node.right))
        elif isinstance(node, ast.UnaryOp):
            return ops[type(node.op)](eval_expr(node.operand))
        else:
            raise ValueError(f"Unsupported operation: {type(node)}")
    
    try:
        tree = ast.parse(expr, mode='eval')
        result = eval_expr(tree.body)
        return str(result)
    except Exception as e:
        raise ValueError(f"Failed to evaluate expression: {e}")

def main():
    parser = argparse.ArgumentParser(description="Execute EXEC commands via Gemini")
    parser.add_argument("--exec", required=True, help="EXEC message")
    parser.add_argument("--output", required=True, help="Output file path")
    parser.add_argument("--pane", help="Tmux pane ID (default from env GEMINI_PANE)")
    parser.add_argument("--mock", action="store_true", help="Use mock mode (no real Gemini)")
    
    args = parser.parse_args()
    
    try:
        if args.mock or os.getenv("MOCK_GEMINI") == "true":
            # Mock 모드: 실제 Gemini 없이 계산
            print("[INFO] Running in MOCK mode")
            result = execute_calc_mock(args.exec)
        else:
            # 실제 Gemini 실행
            pane_id = args.pane or os.getenv("GEMINI_PANE", "gemini-cli:0.0")
            result = execute_calc_via_gemini(args.exec, pane_id)
        
        # 결과 저장
        with open(args.output, "w") as f:
            f.write(result)
        
        print(f"[SUCCESS] Result saved to {args.output}: {result}")
        return 0
        
    except Exception as e:
        print(f"[ERROR] {e}", file=sys.stderr)
        # 디버깅을 위한 상세 에러 출력
        import traceback
        traceback.print_exc(file=sys.stderr)
        return 1

if __name__ == "__main__":
    sys.exit(main())