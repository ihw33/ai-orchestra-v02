#!/usr/bin/env python3
"""
AI Orchestra v02 - Mock version for testing without tmux
"""

import argparse
import sys
import time
from core.idempotency import check_duplicate, save_result, get_cached_result

def main():
    parser = argparse.ArgumentParser(
        description="AI Orchestra v02 - Mock version for testing"
    )
    parser.add_argument("--pane", required=True)
    parser.add_argument("--task", required=True)
    parser.add_argument("--cmd", required=True)
    parser.add_argument("--timeout-ack", type=float, default=5.0)
    parser.add_argument("--timeout-run", type=float, default=10.0)
    parser.add_argument("--timeout-eot", type=float, default=30.0)
    parser.add_argument("--skip-idempotency", action="store_true")
    
    args = parser.parse_args()
    
    # 멱등성 체크
    if not args.skip_idempotency and check_duplicate(args.task):
        cached = get_cached_result(args.task)
        print(f"✅ Task {args.task} already completed (cached)")
        if cached:
            print(f"   Result: {cached}")
        sys.exit(0)
    
    # Mock 동작: 명령에 토큰이 있는지 확인
    cmd = args.cmd
    has_ack = "@@ACK" in cmd and f"id={args.task}" in cmd
    has_run = "@@RUN" in cmd and f"id={args.task}" in cmd
    has_eot = "@@EOT" in cmd and f"id={args.task}" in cmd
    
    # 타임아웃 시뮬레이션
    if not has_ack:
        time.sleep(args.timeout_ack)
        print(f"❌ EOT FAILED (NO_ACK|snapshot=mock output)", file=sys.stderr)
        sys.exit(1)
    
    if not has_run:
        time.sleep(args.timeout_run)
        print(f"❌ EOT FAILED (NO_RUN|snapshot=mock output)", file=sys.stderr)
        sys.exit(1)
    
    if not has_eot:
        time.sleep(args.timeout_eot)
        print(f"❌ EOT FAILED (NO_EOT|snapshot=mock output)", file=sys.stderr)
        sys.exit(1)
    
    # 성공
    print(f"✅ EOT OK (OK)")
    if not args.skip_idempotency:
        save_result(args.task, "OK")
    sys.exit(0)

if __name__ == "__main__":
    main()