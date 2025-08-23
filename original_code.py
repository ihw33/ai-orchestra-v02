#!/usr/bin/env python3
"""
HybridCommunicator (final-minimal)
- 기본: -p 모드(단발성, 빠름)
- 세션 모드: 비활성(향후 필요 시 구현)
"""

import subprocess
import time
import json
from typing import Dict, Literal
from datetime import datetime
from pathlib import Path
import shlex

Mode = Literal["auto", "p_mode", "session"]

class HybridCommunicator:
    def __init__(self):
        self.ai_configs = {
            "claude": {"cmd": "claude", "timeout": 60},
            "gemini": {"cmd": "gemini", "timeout": 60},
            "codex": {"cmd": "codex", "timeout": 60},
        }
        self.performance_log = []
        self.mode_stats = {}

    def send_to_ai(self, ai_name: str, message: str, mode: Mode = "auto") -> Dict:
        start = time.time()
        result = {
            "ai": ai_name,
            "message": message[:100] + "..." if len(message) > 100 else message,
            "timestamp": datetime.now().isoformat(),
            "mode": None,
            "success": False,
            "response": None,
            "error": None,
            "execution_time": 0.0,
        }

        cfg = self.ai_configs.get(ai_name)
        if not cfg:
            result["error"] = f"Unknown AI: {ai_name}"
            return result

        if mode == "auto":
            mode = "p_mode"  # 기본값
        result["mode"] = mode

        try:
            if mode == "p_mode":
                payload = message.replace("\n", "\\n")
                cmd = f'{cfg["cmd"]} -p {shlex.quote(payload)}'
                proc = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=cfg["timeout"])
                if proc.returncode != 0:
                    raise RuntimeError(proc.stderr.strip() or f"{cfg['cmd']} failed")
                result["response"] = proc.stdout.strip()
                result["success"] = True
            else:
                raise NotImplementedError("Session mode disabled")
        except Exception as e:
            result["error"] = str(e)
        finally:
            result["execution_time"] = time.time() - start
            self._log_perf(result)
        return result

    def _log_perf(self, row: Dict):
        self.performance_log.append(row)
        try:
            with open("performance_log.jsonl", "a", encoding="utf-8") as f:
                json.dump(row, f, ensure_ascii=False)
                f.write("\n")
        except:
            pass

if __name__ == "__main__":
    import sys
    comm = HybridCommunicator()
    if len(sys.argv) > 2 and sys.argv[1] == "send":
        ai = sys.argv[2]
        msg = " ".join(sys.argv[3:])
        print(json.dumps(comm.send_to_ai(ai, msg), indent=2))
    else:
        print("Usage: python hybrid_communicator.py send <ai> <msg>")