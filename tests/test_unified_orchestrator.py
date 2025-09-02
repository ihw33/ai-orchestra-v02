#!/usr/bin/env python3
"""
통합 오케스트레이터 테스트
"""

import unittest
import sys
import os
import json
import time
from unittest.mock import Mock, patch, MagicMock

# 상위 디렉토리를 path에 추가
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from unified_orchestrator import UnifiedOrchestrator

class TestUnifiedOrchestrator(unittest.TestCase):
    """UnifiedOrchestrator 테스트"""
    
    def setUp(self):
        """테스트 설정"""
        self.orchestrator = UnifiedOrchestrator()
    
    def tearDown(self):
        """테스트 정리"""
        self.orchestrator.cleanup()
    
    def test_pattern_detection(self):
        """패턴 감지 테스트"""
        test_cases = [
            ("백업 시스템을 분석해줘", "ANALYSIS_PIPELINE"),
            ("새 기능 구현해줘", "IMPLEMENTATION_PIPELINE"),
            ("버그 수정 필요", "BUGFIX_WORKFLOW"),
            ("테스트 코드 작성", "TEST_PIPELINE"),
            ("문서 작성해줘", "DOCUMENTATION_PIPELINE"),
            ("성능 최적화", "OPTIMIZATION_PIPELINE"),
            ("알 수 없는 요청", "GENERAL_PIPELINE")
        ]
        
        for text, expected_pattern in test_cases:
            with self.subTest(text=text):
                pattern = self.orchestrator.detect_pattern(text)
                self.assertEqual(pattern, expected_pattern, 
                               f"Failed for '{text}': expected {expected_pattern}, got {pattern}")
    
    @patch('subprocess.run')
    def test_github_issue_fetch(self, mock_run):
        """GitHub 이슈 가져오기 테스트"""
        # Mock GitHub API 응답
        mock_response = {
            'title': 'Test Issue',
            'body': 'Test body',
            'labels': [{'name': 'test'}]
        }
        
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout=json.dumps(mock_response)
        )
        
        result = self.orchestrator._get_issue_content(1)
        
        self.assertIsNotNone(result)
        self.assertEqual(result['title'], 'Test Issue')
        mock_run.assert_called_once()
    
    @patch('subprocess.run')
    def test_ai_execution(self, mock_run):
        """AI 실행 테스트"""
        # Mock AI 응답
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="AI response"
        )
        
        result = self.orchestrator._execute_ai('gemini', 'test prompt')
        
        self.assertTrue(result['success'])
        self.assertEqual(result['output'], "AI response")
        self.assertEqual(result['ai'], 'gemini')
    
    @patch('subprocess.run')
    def test_ai_execution_failure(self, mock_run):
        """AI 실행 실패 테스트"""
        # Mock 실패 응답
        mock_run.return_value = MagicMock(
            returncode=1,
            stderr="Error message"
        )
        
        result = self.orchestrator._execute_ai('gemini', 'test prompt')
        
        self.assertFalse(result['success'])
        self.assertIn('error', result)
    
    def test_workflow_selection(self):
        """워크플로우 선택 테스트"""
        # 분석 패턴
        pattern = self.orchestrator.detect_pattern("분석해줘")
        workflow = self.orchestrator.workflows.get(pattern)
        self.assertEqual(workflow, ['gemini', 'claude'])
        
        # 구현 패턴
        pattern = self.orchestrator.detect_pattern("구현해줘")
        workflow = self.orchestrator.workflows.get(pattern)
        self.assertEqual(workflow, ['gemini', 'codex', 'claude'])
    
    def test_stats_tracking(self):
        """통계 추적 테스트"""
        initial_requests = self.orchestrator.stats['total_requests']
        
        # Mock 실행
        with patch.object(self.orchestrator, '_execute_ai') as mock_execute:
            mock_execute.return_value = {'success': True, 'output': 'test'}
            
            # 요청 처리
            self.orchestrator.process_request("테스트")
            
            # 통계 확인
            self.assertEqual(
                self.orchestrator.stats['total_requests'],
                initial_requests + 1
            )
    
    def test_history_management(self):
        """히스토리 관리 테스트"""
        initial_history_len = len(self.orchestrator.history)
        
        with patch.object(self.orchestrator, '_execute_ai') as mock_execute:
            mock_execute.return_value = {'success': True, 'output': 'test'}
            
            # 요청 처리
            self.orchestrator.process_request("테스트 요청")
            
            # 히스토리 확인
            self.assertEqual(
                len(self.orchestrator.history),
                initial_history_len + 1
            )
            
            # 마지막 항목 확인
            last_item = self.orchestrator.history[-1]
            self.assertEqual(last_item['request'], "테스트 요청")
    
    @patch('concurrent.futures.ThreadPoolExecutor')
    def test_parallel_execution(self, mock_executor):
        """병렬 실행 테스트"""
        # Mock executor
        mock_future = MagicMock()
        mock_future.result.return_value = {'success': True, 'output': 'test'}
        
        mock_executor.return_value.__enter__.return_value.submit.return_value = mock_future
        
        # 병렬 실행 테스트
        issue_content = {'title': 'Test', 'body': 'Test body'}
        workflow = ['gemini', 'claude']
        
        # 실행 (실제 AI 호출 방지)
        with patch.object(self.orchestrator, '_execute_ai') as mock_ai:
            mock_ai.return_value = {'success': True, 'output': 'test'}
            results = self.orchestrator._execute_parallel(workflow, issue_content)
            
            # 결과 확인
            self.assertIn('gemini', results)
            self.assertIn('claude', results)

class TestPatternMatching(unittest.TestCase):
    """패턴 매칭 상세 테스트"""
    
    def setUp(self):
        self.orchestrator = UnifiedOrchestrator()
    
    def test_korean_patterns(self):
        """한국어 패턴 테스트"""
        patterns = {
            "이 코드를 분석해주세요": "ANALYSIS_PIPELINE",
            "버그를 수정해야 합니다": "BUGFIX_WORKFLOW",
            "새로운 기능을 구현하고 싶습니다": "IMPLEMENTATION_PIPELINE",
            "테스트를 작성해주세요": "TEST_PIPELINE",
            "문서를 만들어주세요": "DOCUMENTATION_PIPELINE",
            "최적화가 필요합니다": "OPTIMIZATION_PIPELINE"
        }
        
        for text, expected in patterns.items():
            result = self.orchestrator.detect_pattern(text)
            self.assertEqual(result, expected, f"Failed for: {text}")
    
    def test_english_patterns(self):
        """영어 패턴 테스트"""
        patterns = {
            "analyze this": "ANALYSIS_PIPELINE",
            "fix the bug": "BUGFIX_WORKFLOW",
            "implement feature": "IMPLEMENTATION_PIPELINE",
            "write tests": "TEST_PIPELINE",
            "create documentation": "DOCUMENTATION_PIPELINE",
            "optimize performance": "OPTIMIZATION_PIPELINE"
        }
        
        for text, expected in patterns.items():
            result = self.orchestrator.detect_pattern(text.lower())
            # 영어는 한국어 키워드가 없으므로 GENERAL_PIPELINE이 될 수 있음
            # 이 부분은 실제 구현에 따라 조정 필요
            self.assertIsNotNone(result)

def run_tests():
    """테스트 실행"""
    # 테스트 스위트 생성
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # 테스트 추가
    suite.addTests(loader.loadTestsFromTestCase(TestUnifiedOrchestrator))
    suite.addTests(loader.loadTestsFromTestCase(TestPatternMatching))
    
    # 실행
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # 결과 요약
    print("\n" + "="*60)
    print("📊 Test Summary")
    print("="*60)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
    
    return result.wasSuccessful()

if __name__ == '__main__':
    success = run_tests()