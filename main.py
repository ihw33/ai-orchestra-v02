#!/usr/bin/env python3
"""
AI Orchestra v02 - Main CLI for smoke testing
"""

import argparse
import sys
from controllers.tmux_controller import TmuxController
from core.idempotency import check_duplicate, save_result, get_cached_result
from core.retry import retry_with_backoff


def main():
    parser = argparse.ArgumentParser(
        description="AI Orchestra v02 - Minimal exec with 3-step handshake"
    )
    parser.add_argument(
        "--pane", 
        required=True, 
        help="tmux pane id (e.g., %%3, session:window.pane)"
    )
    parser.add_argument(
        "--task", 
        required=True, 
        help="task id (idempotency key)"
    )
    parser.add_argument(
        "--cmd", 
        required=True, 
        help="command to execute"
    )
    parser.add_argument(
        "--timeout-ack", 
        type=float, 
        default=5.0,
        help="ACK timeout in seconds (default: 5)"
    )
    parser.add_argument(
        "--timeout-run", 
        type=float, 
        default=10.0,
        help="RUN timeout in seconds (default: 10)"
    )
    parser.add_argument(
        "--timeout-eot", 
        type=float, 
        default=30.0,
        help="EOT timeout in seconds (default: 30)"
    )
    parser.add_argument(
        "--skip-idempotency",
        action="store_true",
        help="Skip idempotency check"
    )
    
    args = parser.parse_args()
    
    # 멱등성 체크
    if not args.skip_idempotency and check_duplicate(args.task):
        cached = get_cached_result(args.task)
        print(f"✅ Task {args.task} already completed (cached)")
        if cached:
            print(f"   Result: {cached}")
        sys.exit(0)
    
    try:
        # tmux 컨트롤러 생성
        controller = TmuxController(args.pane)
        
        # 3단계 핸드셰이크로 실행
        result = controller.execute_with_handshake(
            command=args.cmd,
            task_id=args.task,
            timeout_ack=args.timeout_ack,
            timeout_run=args.timeout_run,
            timeout_eot=args.timeout_eot
        )
        
        # 결과 처리
        if result.success:
            print(f"✅ EOT OK ({result.status})")
            if not args.skip_idempotency:
                save_result(args.task, result.status)
            sys.exit(0)
        else:
            print(f"❌ EOT FAILED ({result.error})", file=sys.stderr)
            sys.exit(1)
            
    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()