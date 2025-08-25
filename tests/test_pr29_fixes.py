#!/usr/bin/env python3
"""
PR #29 수정사항 테스트 스크립트
"""

import sys
import os
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
sys.path.insert(0, str(Path(__file__).parent))

def test_math_validation():
    """수식 유효성 검사 테스트"""
    from core.exec_parser import ExecParser
    
    parser = ExecParser()
    
    # 유효한 수식들
    valid_expressions = [
        "1+1",
        "2*3",
        "10/2",
        "(5+3)*2",
        "3.14 * 2",
        "100 - 50",
    ]
    
    # 무효한 수식들
    invalid_expressions = [
        "import os",  # 위험한 코드
        "1+1; print('hack')",  # 인젝션 시도
        "2**3",  # 거듭제곱 (허용 안함)
        "eval('1+1')",  # 함수 호출
        "x + 1",  # 변수
        "1//2",  # 정수 나눗셈
        "(1+2",  # 괄호 불균형
        "1++2",  # 연속 연산자
    ]
    
    print("=" * 50)
    print("수식 유효성 검사 테스트")
    print("=" * 50)
    
    print("\n✅ 유효한 수식:")
    for expr in valid_expressions:
        valid, error = parser.validate_math_expression(expr)
        status = "OK" if valid else f"FAIL: {error}"
        print(f"  {expr:20} -> {status}")
    
    print("\n❌ 무효한 수식:")
    for expr in invalid_expressions:
        valid, error = parser.validate_math_expression(expr)
        status = f"차단됨: {error}" if not valid else "ERROR: 통과됨!"
        print(f"  {expr:20} -> {status}")

def test_mock_calculation():
    """Mock 모드 계산 테스트"""
    from scripts.exec_to_gemini import execute_calc_mock
    from core.exec_parser import ExecCommand
    
    print("\n" + "=" * 50)
    print("Mock 모드 계산 테스트")
    print("=" * 50)
    
    test_cases = [
        ("CALC expr=\"1+1\" task_id=TEST-1", "2"),
        ("CALC expr=\"10*5\" task_id=TEST-2", "50"),
        ("CALC expr=\"100/4\" task_id=TEST-3", "25.0"),
        ("CALC expr=\"(5+3)*2\" task_id=TEST-4", "16"),
        ("CALC expr=\"3.14*2\" task_id=TEST-5", "6.28"),
    ]
    
    for exec_msg, expected in test_cases:
        try:
            result = execute_calc_mock(exec_msg)
            # 부동소수점 비교를 위해 float으로 변환
            result_float = float(result)
            expected_float = float(expected)
            status = "✅ OK" if abs(result_float - expected_float) < 0.01 else f"❌ FAIL (got {result})"
            print(f"  {exec_msg[:30]:30} -> {status}")
        except Exception as e:
            print(f"  {exec_msg[:30]:30} -> ❌ ERROR: {e}")

def test_eot_pattern():
    """개선된 EOT 패턴 테스트"""
    import re
    
    print("\n" + "=" * 50)
    print("EOT 패턴 매칭 테스트")
    print("=" * 50)
    
    # 테스트할 EOT 문자열들
    test_strings = [
        "@@EOT id=TEST-1 status=OK result=2",  # 표준
        "@EOT id=TEST-1 status=OK result=2",   # @ 하나
        "  @@EOT id=TEST-1 status=OK result=2",  # 앞 공백
        "@@EOT id=TEST-1 status = OK result = 2",  # = 주변 공백
        "@@EOT id=TEST-1 status=OK answer=2",  # answer 키
        "@EOT id=TEST-1 status = OK answer = 2",  # 모든 변형 조합
    ]
    
    # 개선된 패턴
    task_id = "TEST-1"
    eot_pattern = (
        f"\\s*@{{1,2}}EOT\\s+id={re.escape(task_id)}\\s+"
        f"status\\s*=\\s*OK\\s+"
        f"(?:answer|result)\\s*=\\s*([\\d\\.\\-]+)"
    )
    regex = re.compile(eot_pattern)
    
    for test_str in test_strings:
        match = regex.search(test_str)
        if match:
            print(f"  ✅ 매칭됨: {test_str[:40]:40} -> 값: {match.group(1)}")
        else:
            print(f"  ❌ 실패: {test_str[:40]}")

def test_gemini_adapter():
    """Gemini 어댑터 개선사항 테스트"""
    print("\n" + "=" * 50)
    print("Gemini 어댑터 테스트")
    print("=" * 50)
    
    from adapters.gemini_adapter import GeminiAdapter, GeminiConfig
    
    try:
        # Mock 설정으로 어댑터 생성 테스트
        config = GeminiConfig(
            name="test-gemini",
            timeout_ack=5,
            timeout_run=10,
            timeout_eot=30,
            pane_id="test-pane"
        )
        
        print("  ✅ GeminiConfig 생성 성공")
        print(f"     - pane_id: {config.pane_id}")
        print(f"     - timeout_ack: {config.timeout_ack}")
        print(f"     - timeout_run: {config.timeout_run}")
        print(f"     - timeout_eot: {config.timeout_eot}")
        
        # 실제 tmux 없이는 어댑터 생성이 실패할 것임
        # 이는 예상된 동작
        try:
            adapter = GeminiAdapter(config)
            print("  ⚠️  실제 tmux 세션이 있는 것으로 보임")
        except RuntimeError as e:
            print(f"  ✅ tmux 세션 없음 감지 (예상된 동작)")
            
    except Exception as e:
        print(f"  ❌ 예상치 못한 오류: {e}")

def main():
    """메인 테스트 실행"""
    print("\n🧪 PR #29 수정사항 테스트 시작\n")
    
    # 각 테스트 실행
    test_math_validation()
    test_mock_calculation()
    test_eot_pattern()
    test_gemini_adapter()
    
    print("\n" + "=" * 50)
    print("✅ 모든 테스트 완료!")
    print("=" * 50)
    print("\n다음 단계:")
    print("1. 변경사항을 커밋하고 PR에 푸시")
    print("2. GitHub Actions가 자동으로 실행되는지 확인")
    print("3. 이슈를 생성하여 실제 동작 테스트")

if __name__ == "__main__":
    main()