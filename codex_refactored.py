#!/usr/bin/env python3
"""
HybridCommunicator
- Default: -p (prompt) mode, single-shot execution
- Session mode: not implemented (explicit error)
"""

from __future__ import annotations

import argparse
import json
import subprocess
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Literal, Optional

Mode = Literal["auto", "p_mode", "session"]


@dataclass(frozen=True)
class AIConfig:
    cmd: str
    timeout: int = 60


class HybridCommunicator:
    DEFAULTS: Dict[str, AIConfig] = {
        "claude": AIConfig("claude"),
        "gemini": AIConfig("gemini"),
        "codex": AIConfig("codex"),
    }

    def __init__(
        self,
        configs: Optional[Dict[str, AIConfig]] = None,
        log_path: Optional[str | Path] = "performance_log.jsonl",
    ) -> None:
        self.configs: Dict[str, AIConfig] = dict(configs or self.DEFAULTS)
        self.log_path: Optional[Path] = Path(log_path) if log_path else None
        self.performance_log: List[Dict[str, Any]] = []

    def send_to_ai(self, ai_name: str, message: str, mode: Mode = "auto") -> Dict[str, Any]:
        start = time.time()
        resolved_mode: Mode = "p_mode" if mode == "auto" else mode

        result: Dict[str, Any] = {
            "ai": ai_name,
            "message": self._shorten(message),
            "timestamp": datetime.now().isoformat(),
            "mode": resolved_mode,
            "success": False,
            "response": None,
            "error": None,
            "execution_time": 0.0,
        }

        try:
            cfg = self._get_config(ai_name)
            if resolved_mode != "p_mode":
                raise NotImplementedError("Only -p mode is supported")

            cmd = self._build_p_command(cfg.cmd, message)
            stdout = self._run(cmd, timeout=cfg.timeout)
            result["response"] = stdout.strip()
            result["success"] = True

        except Exception as exc:
            result["error"] = self._format_error(exc)
        finally:
            result["execution_time"] = round(time.time() - start, 4)
            self._record(result)

        return result

    # --- Helpers -------------------------------------------------------------

    def _get_config(self, ai_name: str) -> AIConfig:
        try:
            return self.configs[ai_name]
        except KeyError as exc:
            supported = ", ".join(sorted(self.configs.keys()))
            raise ValueError(f"Unknown AI '{ai_name}'. Supported: {supported}") from exc

    def _build_p_command(self, binary: str, payload: str) -> List[str]:
        # Pass args list to avoid shell quoting issues and keep newlines intact.
        return [binary, "-p", payload]

    def _run(self, cmd: List[str], timeout: int) -> str:
        try:
            proc = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True,
                timeout=timeout,
            )
            return proc.stdout
        except subprocess.TimeoutExpired as exc:
            raise TimeoutError(f"Command timed out after {timeout}s") from exc
        except FileNotFoundError as exc:
            raise FileNotFoundError(f"Command not found: {cmd[0]}") from exc
        except subprocess.CalledProcessError as exc:
            stderr = (exc.stderr or "").strip()
            stdout = (exc.stdout or "").strip()
            detail = stderr or stdout or f"exit code {exc.returncode}"
            raise RuntimeError(f"{cmd[0]} failed: {detail}") from exc

    def _shorten(self, text: str, limit: int = 120) -> str:
        return text if len(text) <= limit else text[:limit] + "..."

    def _record(self, row: Dict[str, Any]) -> None:
        self.performance_log.append(row)
        if not self.log_path:
            return
        try:
            with self.log_path.open("a", encoding="utf-8") as f:
                json.dump(row, f, ensure_ascii=False)
                f.write("\n")
        except Exception:
            # Logging must never break main flow.
            pass

    def _format_error(self, exc: Exception) -> str:
        return f"{exc.__class__.__name__}: {exc}"

    # Optional helper
    def supported(self) -> List[str]:
        return sorted(self.configs.keys())


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="HybridCommunicator CLI")
    sub = parser.add_subparsers(dest="command", required=True)

    send = sub.add_parser("send", help="Send a message to an AI in -p mode")
    send.add_argument("ai", choices=sorted(HybridCommunicator.DEFAULTS.keys()))
    send.add_argument("msg", nargs="+", help="Message to send")
    send.add_argument("--mode", choices=["auto", "p_mode", "session"], default="auto")

    args = parser.parse_args(argv)

    comm = HybridCommunicator()
    message = " ".join(args.msg)
    result = comm.send_to_ai(args.ai, message, mode=args.mode)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())