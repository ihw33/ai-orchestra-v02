#!/usr/bin/env python3
"""
Devil's Advocate 최예리의 코드 리뷰
Issue #101 코드의 모든 문제점 찾기
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from src.utils.string_utils import reverse_string, capitalize_words, remove_spaces

class DevilAdvocateReview:
    """최예리: 모든 문제점을 찾아냅니다"""
    
    def __init__(self):
        self.issues_found = []
        self.critical_issues = []
    
    def test_edge_cases(self):
        """엣지 케이스 테스트"""
        
        print("="*60)
        print("😈 Devil's Advocate 최예리의 비판적 코드 리뷰")
        print("="*60)
        print("\n'이거 정말 작동할까요? 증명해보세요'\n")
        
        # 1. None 입력 테스트
        print("🔍 Test 1: None 입력")
        try:
            reverse_string(None)
            print("❌ FAIL: None 입력시 TypeError 발생해야 함")
        except TypeError as e:
            print(f"✅ 예상대로 TypeError 발생: {e}")
            self.issues_found.append("None 입력 처리 안됨 - 타입 체크 필요")
        
        # 2. 빈 문자열
        print("\n🔍 Test 2: 빈 문자열")
        assert reverse_string("") == ""
        assert capitalize_words("") == ""
        assert remove_spaces("") == ""
        print("✅ 빈 문자열 처리 OK")
        
        # 3. 연속 공백 문제
        print("\n🔍 Test 3: 연속 공백")
        test = "hello    world"
        result = capitalize_words(test)
        print(f"입력: '{test}'")
        print(f"결과: '{result}'")
        if result != "Hello    World":
            self.issues_found.append("capitalize_words()가 연속 공백을 단일 공백으로 변환")
            print("❌ 연속 공백이 보존되지 않음!")
        
        # 4. 유니코드 문자
        print("\n🔍 Test 4: 유니코드 및 이모지")
        unicode_test = "안녕하세요 🚀 世界"
        print(f"입력: {unicode_test}")
        print(f"뒤집기: {reverse_string(unicode_test)}")
        print(f"대문자화: {capitalize_words(unicode_test)}")
        # 이모지가 있는 문자열에서 문제 발생 가능
        self.issues_found.append("유니코드 정규화 미처리 - NFD/NFC 문제 가능")
        
        # 5. 탭과 줄바꿈
        print("\n🔍 Test 5: 탭과 줄바꿈")
        tab_test = "hello\tworld\ntest"
        result = remove_spaces(tab_test)
        print(f"입력: {repr(tab_test)}")
        print(f"결과: {repr(result)}")
        if '\t' in result or '\n' in result:
            self.issues_found.append("remove_spaces()가 탭과 줄바꿈을 제거하지 않음")
            print("❌ 탭과 줄바꿈이 남아있음!")
        
        # 6. 매우 긴 문자열
        print("\n🔍 Test 6: 매우 긴 문자열 (1MB)")
        huge_string = "a" * 1_000_000
        try:
            result = reverse_string(huge_string)
            print(f"✅ 1MB 문자열 처리 성공")
        except:
            self.critical_issues.append("대용량 문자열 처리 실패")
        
        # 7. 숫자가 포함된 문자열
        print("\n🔍 Test 7: 숫자와 특수문자")
        test = "hello123 world!@#"
        result = capitalize_words(test)
        print(f"입력: {test}")
        print(f"결과: {result}")
        
        # 8. 앞뒤 공백
        print("\n🔍 Test 8: 앞뒤 공백")
        test = "  hello world  "
        result = capitalize_words(test)
        print(f"입력: '{test}'")
        print(f"결과: '{result}'")
        if result != "  Hello World  ":
            self.issues_found.append("앞뒤 공백이 trim됨")
        
        # 9. 타입 체크
        print("\n🔍 Test 9: 잘못된 타입")
        try:
            reverse_string(123)
            self.critical_issues.append("숫자 입력시 에러 없음")
        except:
            print("✅ 잘못된 타입 거부")
        
        # 10. 성능 문제
        print("\n🔍 Test 10: 성능 위험")
        self.issues_found.append("capitalize_words()에서 split()과 join() 사용 - 메모리 2배 사용")
        
    def generate_report(self):
        """최종 리포트 생성"""
        
        print("\n" + "="*60)
        print("📋 Devil's Advocate 최종 리포트")
        print("="*60)
        
        print("\n🚨 발견된 문제점들:")
        for i, issue in enumerate(self.issues_found, 1):
            print(f"{i}. {issue}")
        
        if self.critical_issues:
            print("\n💀 치명적 문제:")
            for issue in self.critical_issues:
                print(f"⚠️  {issue}")
        
        print("\n💡 개선 제안:")
        print("1. 입력 타입 검증 추가 (isinstance 체크)")
        print("2. None 처리 - 기본값 또는 에러")
        print("3. remove_spaces()를 remove_whitespace()로 확장")
        print("4. 유니코드 정규화 (unicodedata.normalize)")
        print("5. 연속 공백 보존 옵션 추가")
        print("6. 성능 최적화 - 제너레이터 사용 고려")
        
        print("\n😈 최예리의 판정:")
        if len(self.critical_issues) > 0:
            print("❌ REJECT - 치명적 문제 해결 필요")
        elif len(self.issues_found) > 5:
            print("⚠️  CONDITIONAL - 개선 후 재검토")
        else:
            print("✅ PASS - 하지만 개선 여지 있음")
        
        print("\n'이게 정말 프로덕션에 올라갈 수 있나요? 다시 생각해보세요.'")


if __name__ == "__main__":
    reviewer = DevilAdvocateReview()
    reviewer.test_edge_cases()
    reviewer.generate_report()