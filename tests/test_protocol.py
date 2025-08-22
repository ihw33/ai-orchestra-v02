import pytest
from core.protocol import (
    format_ack, format_run, format_eot,
    parse_ack, parse_run, parse_eot
)


def test_format_and_parse_ack():
    s = format_ack("t1")
    assert s == "@@ACK id=t1"
    a = parse_ack(s)
    assert a and a.id == "t1"


def test_format_and_parse_run():
    s = format_run("t2", ts="123")
    assert s == "@@RUN id=t2 ts=123"
    r = parse_run(s)
    assert r and r.id == "t2" and r.ts == "123"


def test_format_and_parse_eot_ok():
    s = format_eot("t3", status="OK", dur_ms=120)
    assert "@@EOT id=t3 status=OK" in s
    assert "dur_ms=120" in s
    e = parse_eot(s)
    assert e and e.id == "t3" and e.status == "OK"


def test_parse_invalid_tokens():
    """잘못된 토큰 파싱 테스트"""
    assert parse_ack("@@RUN id=test") is None
    assert parse_run("@@ACK id=test") is None
    assert parse_eot("invalid") is None
    assert parse_ack("") is None