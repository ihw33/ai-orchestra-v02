#!/usr/bin/env python3
"""
HybridCommunicator
- Default: -p (prompt) mode, single-shot execution
- Session mode: not implemented (explicit error with guidance)
- Logs: persisted immediately with flush + fsync
- Large messages: stdin support for >1MB payloads and CLI --stdin
- Config: load via from_config_file() classmethod (JSON)
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
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

    # 1MB threshold for switching to stdin when invoking the AI binary
    LARGE_MESSAGE_THRESHOLD_BYTES: int = 1_048_576

    def __init__(
        self,
        configs: Optional[Dict[str, AIConfig]] = None,
        log_path: Optional[str | Path] = "performance_log.jsonl",
    ) -> None:
        self.configs: Dict[str, AIConfig] = dict(configs or self.DEFAULTS)
        self.log_path: Optional[Path] = Path(log_path) if log_path else None
        self.performance_log: List[Dict[str, Any]] = []

    @classmethod
    def from_config_file(
        cls,
        path: str | Path,
        log_path: Optional[str | Path] = "performance_log.jsonl",
    ) -> "HybridCommunicator":
        """
        Load AI configurations from a JSON file.

        Expected JSON structure:
        {
          "claude": {"cmd": "claude", "timeout": 60},
          "gemini": {"cmd": "gemini"},
          "custom": {"cmd": "/path/to/bin", "timeout": 120}
        }
        """
        p = Path(path)
        if not p.exists():
            raise FileNotFoundError(f"Config file not found: {p}")
        if p.suffix.lower() != ".json":
            raise ValueError(f"Unsupported config format '{p.suffix}'. Use a .json file.")

        try:
            data = json.loads(p.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise ValueError(f"Invalid JSON in config file: {p}") from exc

        if not isinstance(data, dict):
            raise ValueError("Config file must contain a JSON object mapping AI names to configs")

        configs: Dict[str, AIConfig] = {}
        for name, cfg in data.items():
            if not isinstance(cfg, dict):
                raise ValueError(f"Config for '{name}' must be an object with 'cmd' and optional 'timeout'")
            cmd = cfg.get("cmd")
            if not cmd or not isinstance(cmd, str):
                raise ValueError(f"Config for '{name}' missing valid 'cmd' string")
            timeout = cfg.get("timeout", 60)
            if not isinstance(timeout, int) or timeout <= 0:
                raise ValueError(f"Config for '{name}' has invalid 'timeout' (must be positive integer)")
            configs[name] = AIConfig(cmd=cmd, timeout=timeout)

        return cls(configs=configs, log_path=log_path)

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
                raise NotImplementedError(
                    "Session mode is not implemented in HybridCommunicator. "
                    "Use single-shot prompt mode instead (pass --mode p_mode or keep the default 'auto')."
                )

            use_stdin = len(message.encode("utf-8")) > self.LARGE_MESSAGE_THRESHOLD_BYTES
            cmd = self._build_p_command(cfg.cmd, message, use_stdin=use_stdin)
            stdout = self._run(cmd, timeout=cfg.timeout, input_text=message if use_stdin else None)
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

    def _build_p_command(self, binary: str, payload: str, use_stdin: bool = False) -> List[str]:
        # Use "-p -" to signal reading the prompt from stdin when payload is large.
        return [binary, "-p", "-"] if use_stdin else [binary, "-p", payload]

    def _run(self, cmd: List[str], timeout: int, input_text: Optional[str] = None) -> str:
        try:
            proc = subprocess.run(
                cmd,
                input=input_text,
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
        # Keep in-memory for programmatic access
        self.performance_log.append(row)
        if not self.log_path:
            return
        # Persist immediately to disk with flush + fsync
        try:
            with self.log_path.open("a", encoding="utf-8") as f:
                json.dump(row, f, ensure_ascii=False)
                f.write("\n")
                f.flush()
                os.fsync(f.fileno())
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
    # Allow zero args when using --stdin
    send.add_argument("msg", nargs="*", help="Message to send")
    send.add_argument("--mode", choices=["auto", "p_mode", "session"], default="auto")
    send.add_argument(
        "--stdin",
        action="store_true",
        help="Read the message from STDIN (recommended for payloads >1MB)",
    )
    send.add_argument(
        "--config",
        type=str,
        default=None,
        help="Path to JSON config file for AI binaries/timeouts",
    )

    args = parser.parse_args(argv)

    comm = HybridCommunicator.from_config_file(args.config) if args.config else HybridCommunicator()

    if args.stdin:
        message = sys.stdin.read()
    else:
        if not args.msg:
            send.error("No message provided. Pass text as arguments or use --stdin.")
        message = " ".join(args.msg)

    result = comm.send_to_ai(args.ai, message, mode=args.mode)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())