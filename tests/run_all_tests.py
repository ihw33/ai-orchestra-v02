#!/usr/bin/env python3
"""
전체 테스트 실행기
모든 테스트를 실행하고 종합 리포트 생성
"""

import unittest
import sys
import os
import time
from datetime import datetime

# 상위 디렉토리를 path에 추가
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def run_all_tests():
    """모든 테스트 실행"""
    print("="*60)
    print("🧪 AI Orchestra v02 - Test Suite")
    print("="*60)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # 테스트 로더
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # 테스트 디렉토리
    test_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 모든 test_*.py 파일 찾기
    for file in os.listdir(test_dir):
        if file.startswith('test_') and file.endswith('.py') and file != 'run_all_tests.py':
            module_name = file[:-3]  # .py 제거
            try:
                # 모듈 동적 임포트
                module = __import__(module_name)
                # 테스트 추가
                suite.addTests(loader.loadTestsFromModule(module))
                print(f"✅ Loaded tests from {module_name}")
            except Exception as e:
                print(f"❌ Failed to load {module_name}: {e}")
    
    print("\n" + "-"*60)
    print("Running tests...\n")
    
    # 테스트 실행
    runner = unittest.TextTestRunner(verbosity=2)
    start_time = time.time()
    result = runner.run(suite)
    elapsed_time = time.time() - start_time
    
    # 결과 분석
    print("\n" + "="*60)
    print("📊 Test Results Summary")
    print("="*60)
    
    # 통계
    total_tests = result.testsRun
    failures = len(result.failures)
    errors = len(result.errors)
    success = total_tests - failures - errors
    
    print(f"Total Tests: {total_tests}")
    print(f"✅ Passed: {success}")
    print(f"❌ Failed: {failures}")
    print(f"💥 Errors: {errors}")
    print(f"⏱️ Time: {elapsed_time:.2f}s")
    
    # 성공률
    if total_tests > 0:
        success_rate = (success / total_tests) * 100
        print(f"\n🎯 Success Rate: {success_rate:.1f}%")
        
        # 이모지 기반 평가
        if success_rate == 100:
            print("🏆 Perfect! All tests passed!")
        elif success_rate >= 90:
            print("🎉 Excellent! Most tests passed.")
        elif success_rate >= 70:
            print("👍 Good, but needs improvement.")
        else:
            print("⚠️ Needs attention! Many tests failing.")
    
    # 실패한 테스트 상세
    if failures:
        print("\n" + "-"*60)
        print("Failed Tests:")
        for test, traceback in result.failures:
            print(f"  ❌ {test}")
            print(f"     {traceback.split(chr(10))[0]}")
    
    # 에러난 테스트 상세
    if errors:
        print("\n" + "-"*60)
        print("Error Tests:")
        for test, traceback in result.errors:
            print(f"  💥 {test}")
            print(f"     {traceback.split(chr(10))[0]}")
    
    print("\n" + "="*60)
    print(f"Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)
    
    return result.wasSuccessful()

def generate_coverage_report():
    """코드 커버리지 리포트 생성 (옵션)"""
    try:
        import coverage
        print("\n📈 Generating coverage report...")
        
        cov = coverage.Coverage()
        cov.start()
        
        # 테스트 실행
        success = run_all_tests()
        
        cov.stop()
        cov.save()
        
        # 리포트 생성
        print("\nCoverage Report:")
        cov.report()
        
        return success
    except ImportError:
        print("⚠️ Coverage module not installed. Run: pip install coverage")
        return run_all_tests()

if __name__ == '__main__':
    # 기본 테스트 실행
    success = run_all_tests()
    
    # 종료 코드 설정 (CI/CD용)
    sys.exit(0 if success else 1)