#!/usr/bin/env python3
"""
캐시 매니저 테스트
"""

import unittest
import sys
import os
import time
import tempfile
import shutil

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from cache_manager import CacheManager, cached, AIResponseCache, GitHubCache

class TestCacheManager(unittest.TestCase):
    """CacheManager 테스트"""
    
    def setUp(self):
        """테스트 설정"""
        # 임시 캐시 디렉토리
        self.temp_dir = tempfile.mkdtemp()
        self.cache = CacheManager(cache_dir=self.temp_dir, max_memory_items=3)
    
    def tearDown(self):
        """테스트 정리"""
        # 임시 디렉토리 삭제
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_basic_cache_operations(self):
        """기본 캐시 작업 테스트"""
        # 캐시 저장
        self.cache.set('key1', 'value1', ttl=10)
        
        # 캐시 조회
        value = self.cache.get('key1')
        self.assertEqual(value, 'value1')
        
        # 존재하지 않는 키
        value = self.cache.get('nonexistent')
        self.assertIsNone(value)
    
    def test_cache_expiration(self):
        """캐시 만료 테스트"""
        # 짧은 TTL로 저장
        self.cache.set('expire_key', 'expire_value', ttl=1)
        
        # 즉시 조회 - 있어야 함
        value = self.cache.get('expire_key')
        self.assertEqual(value, 'expire_value')
        
        # 2초 대기
        time.sleep(2)
        
        # 만료 후 조회 - 없어야 함
        value = self.cache.get('expire_key')
        self.assertIsNone(value)
    
    def test_memory_cache_lru(self):
        """메모리 캐시 LRU 정책 테스트"""
        # max_memory_items=3으로 설정됨
        
        # 4개 항목 추가
        self.cache.set('item1', 'value1')
        self.cache.set('item2', 'value2')
        self.cache.set('item3', 'value3')
        
        # item1 접근 (최근 사용으로 갱신)
        self.cache.get('item1')
        
        # 4번째 항목 추가 (item2가 제거되어야 함)
        self.cache.set('item4', 'value4')
        
        # item2는 제거됨
        self.assertEqual(len(self.cache.memory_cache), 3)
        
        # 통계 확인
        stats = self.cache.get_stats()
        self.assertEqual(stats['evictions'], 1)
    
    def test_cache_stats(self):
        """캐시 통계 테스트"""
        # 초기 상태
        stats = self.cache.get_stats()
        self.assertEqual(stats['hits'], 0)
        self.assertEqual(stats['misses'], 0)
        
        # 캐시 미스
        self.cache.get('missing')
        stats = self.cache.get_stats()
        self.assertEqual(stats['misses'], 1)
        
        # 캐시 히트
        self.cache.set('hit_key', 'hit_value')
        self.cache.get('hit_key')
        stats = self.cache.get_stats()
        self.assertEqual(stats['hits'], 1)
    
    def test_file_cache(self):
        """파일 캐시 테스트"""
        # 메모리 캐시 비우기
        self.cache.memory_cache.clear()
        
        # 파일 캐시에 저장
        self.cache.set('file_key', 'file_value')
        
        # 새 캐시 인스턴스 생성 (메모리는 비어있음)
        new_cache = CacheManager(cache_dir=self.temp_dir)
        
        # 파일에서 로드되어야 함
        value = new_cache.get('file_key')
        self.assertEqual(value, 'file_value')
    
    def test_clear_cache(self):
        """캐시 삭제 테스트"""
        # 여러 항목 추가
        self.cache.set('clear1', 'value1')
        self.cache.set('clear2', 'value2')
        
        # 캐시 삭제
        self.cache.clear()
        
        # 모두 없어야 함
        self.assertIsNone(self.cache.get('clear1'))
        self.assertIsNone(self.cache.get('clear2'))
        
        # 통계 확인
        stats = self.cache.get_stats()
        self.assertEqual(stats['memory_items'], 0)

class TestCacheDecorator(unittest.TestCase):
    """캐싱 데코레이터 테스트"""
    
    def setUp(self):
        """테스트 설정"""
        # 전역 캐시 초기화
        from cache_manager import cache
        cache.clear()
        self.call_count = 0
    
    def test_cached_function(self):
        """캐시된 함수 테스트"""
        @cached(ttl=10)
        def expensive_function(x):
            self.call_count += 1
            return x * 2
        
        # 첫 호출 - 실행됨
        result1 = expensive_function(5)
        self.assertEqual(result1, 10)
        self.assertEqual(self.call_count, 1)
        
        # 두 번째 호출 - 캐시에서
        result2 = expensive_function(5)
        self.assertEqual(result2, 10)
        self.assertEqual(self.call_count, 1)  # 증가하지 않음
        
        # 다른 인자 - 새로 실행
        result3 = expensive_function(3)
        self.assertEqual(result3, 6)
        self.assertEqual(self.call_count, 2)

class TestAIResponseCache(unittest.TestCase):
    """AI 응답 캐시 테스트"""
    
    def setUp(self):
        """테스트 설정"""
        self.temp_dir = tempfile.mkdtemp()
        self.ai_cache = AIResponseCache(ttl=10)
        self.ai_cache.cache.cache_dir = self.temp_dir
    
    def tearDown(self):
        """테스트 정리"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_ai_response_caching(self):
        """AI 응답 캐싱 테스트"""
        # 응답 캐싱
        self.ai_cache.cache_response('gemini', 'test prompt', 'test response')
        
        # 캐시에서 가져오기
        response = self.ai_cache.get_cached_response('gemini', 'test prompt')
        self.assertEqual(response, 'test response')
        
        # 다른 프롬프트는 없어야 함
        response = self.ai_cache.get_cached_response('gemini', 'different prompt')
        self.assertIsNone(response)

def run_tests():
    """테스트 실행"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # 테스트 추가
    suite.addTests(loader.loadTestsFromTestCase(TestCacheManager))
    suite.addTests(loader.loadTestsFromTestCase(TestCacheDecorator))
    suite.addTests(loader.loadTestsFromTestCase(TestAIResponseCache))
    
    # 실행
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print("\n" + "="*60)
    print("📊 Cache Manager Test Summary")
    print("="*60)
    print(f"Tests run: {result.testsRun}")
    print(f"Success rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
    
    return result.wasSuccessful()

if __name__ == '__main__':
    success = run_tests()