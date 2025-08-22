import re
from dataclasses import dataclass
from typing import Optional

# ANSI 컬러 코드 제거 패턴
ANSI_ESCAPE = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')

# 토큰 정규식 패턴
ACK_RE = re.compile(r"^\s*@@ACK id=(?P<id>\S+)\s*$")
RUN_RE = re.compile(r"^\s*@@RUN id=(?P<id>\S+)(?:\s+ts=(?P<ts>\S+))?\s*$")
EOT_RE = re.compile(r"^\s*@@EOT id=(?P<id>\S+)\s+status=(?P<status>OK|FAIL)(?:\s+.*)?$")


def strip_ansi_codes(text: str) -> str:
    """ANSI 컬러 코드 제거"""
    return ANSI_ESCAPE.sub('', text)


def format_ack(task_id: str) -> str:
    """ACK 토큰 생성"""
    return f"@@ACK id={task_id}"


def format_run(task_id: str, ts: Optional[str] = None) -> str:
    """RUN 토큰 생성"""
    return f"@@RUN id={task_id}" + (f" ts={ts}" if ts else "")


def format_eot(task_id: str, status: str = "OK", **meta) -> str:
    """EOT 토큰 생성"""
    return f"@@EOT id={task_id} status={status}" + (
        "" if not meta else " " + " ".join(f"{k}={v}" for k, v in meta.items())
    )


@dataclass
class Ack:
    id: str


@dataclass
class Run:
    id: str
    ts: Optional[str] = None


@dataclass
class Eot:
    id: str
    status: str = "OK"


def parse_ack(line: str) -> Optional[Ack]:
    """ACK 토큰 파싱 (ANSI 코드 자동 제거)"""
    clean_line = strip_ansi_codes(line)
    m = ACK_RE.match(clean_line)
    return Ack(m["id"]) if m else None


def parse_run(line: str) -> Optional[Run]:
    """RUN 토큰 파싱 (ANSI 코드 자동 제거)"""
    clean_line = strip_ansi_codes(line)
    m = RUN_RE.match(clean_line)
    return Run(m["id"], m["ts"]) if m else None


def parse_eot(line: str) -> Optional[Eot]:
    """EOT 토큰 파싱 (ANSI 코드 자동 제거)"""
    clean_line = strip_ansi_codes(line)
    m = EOT_RE.match(clean_line)
    return Eot(m["id"], m["status"]) if m else None