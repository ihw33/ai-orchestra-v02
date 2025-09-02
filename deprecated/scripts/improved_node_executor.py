#!/usr/bin/env python3
"""개선된 노드 실행기 - 프로덕션 레벨 구현"""

import os
import shutil
import subprocess
import json
import logging
import time
from typing import Dict, Any, Optional, List
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeoutError
from datetime import datetime

class ImprovedNodeExecutor:
    def __init__(self, config_file: str = 'node_config.json'):
        """초기화 및 설정"""
        self.setup_logging()
        self.load_config(config_file)
        self.check_dependencies()
        self.executor_pool = ThreadPoolExecutor(max_workers=3)
        self.execution_stats = {}
        
    def setup_logging(self):
        """로깅 설정"""
        log_dir = 'logs'
        os.makedirs(log_dir, exist_ok=True)
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(f'{log_dir}/node_executor.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def load_config(self, config_file: str):
        """설정 파일 로드"""
        # 기본값 설정
        self.repo = os.getenv('GITHUB_REPO', 'ihw33/ai-orchestra-v02')
        self.timeout = int(os.getenv('NODE_TIMEOUT', '300'))
        self.retry_count = 3
        self.ai_configs = {}
        
        # 설정 파일이 있으면 로드
        if os.path.exists(config_file):
            try:
                with open(config_file) as f:
                    config = json.load(f)
                    self.repo = config.get('repo', self.repo)
                    self.timeout = config.get('timeout', self.timeout)
                    self.retry_count = config.get('retry_count', self.retry_count)
                    self.ai_configs = config.get('ai_models', {})
                    self.custom_nodes = config.get('custom_nodes', {})
                    self.logger.info(f"Config loaded from {config_file}")
            except Exception as e:
                self.logger.warning(f"Failed to load config: {e}")
                self.custom_nodes = {}
        else:
            self.custom_nodes = {}
        
        # 노드 매핑 초기화
        self.init_nodes()
    
    def init_nodes(self):
        """노드 함수 매핑 초기화"""
        self.nodes = {
            "CREATE_ISSUE": self.create_issue,
            "KEYWORD_ENRICHMENT": self.keyword_enrichment,
            "AI_ANALYSIS": self.ai_analysis,
            "AI_IMPLEMENTATION": self.ai_implementation,
            "AI_TESTING": self.ai_testing,
            "GENERATE_REPORT": self.generate_report,
            "PARSE_SOLUTION": self.parse_solution,
            "ANALYZE_FEATURES": self.analyze_features,
            "EVALUATE_FIT": self.evaluate_fit,
            "ADOPTION_REPORT": self.adoption_report,
            "VALIDATE_RESULT": self.validate_result,
            "NOTIFY": self.notify
        }
        
        # 커스텀 노드 추가
        for name, func_name in self.custom_nodes.items():
            if hasattr(self, func_name):
                self.nodes[name] = getattr(self, func_name)
                self.logger.info(f"Custom node added: {name}")
    
    def check_dependencies(self):
        """의존성 확인 및 경고"""
        required = {
            'gh': ('GitHub CLI가 필요합니다', 'brew install gh'),
            'python3': ('Python 3.7+가 필요합니다', None),
        }
        
        optional = {
            'gemini': 'Gemini CLI',
            'claude': 'Claude CLI',
            'codex': 'Codex CLI'
        }
        
        # 필수 도구 확인
        missing_required = []
        for cmd, (msg, install) in required.items():
            if not shutil.which(cmd):
                missing_required.append((msg, install))
                self.logger.error(f"Missing required: {cmd}")
        
        if missing_required:
            print("❌ 필수 도구가 없습니다:")
            for msg, install in missing_required:
                print(f"  - {msg}")
                if install:
                    print(f"    설치: {install}")
            raise SystemExit(1)
        
        # 선택적 도구 확인
        missing_optional = []
        for cmd, name in optional.items():
            if not shutil.which(cmd):
                missing_optional.append(name)
                self.logger.warning(f"Missing optional: {cmd}")
        
        if missing_optional:
            print("⚠️ 선택적 도구 (일부 기능 제한):")
            for name in missing_optional:
                print(f"  - {name}")
    
    def execute(self, node_name: str, params: Dict[str, Any]) -> Any:
        """노드 실행 (메인 인터페이스)"""
        start_time = time.time()
        
        if node_name not in self.nodes:
            self.logger.error(f"Unknown node: {node_name}")
            return None
        
        try:
            self.logger.info(f"Executing node: {node_name}")
            result = self.nodes[node_name](params)
            
            # 실행 통계 기록
            execution_time = time.time() - start_time
            self.record_stats(node_name, True, execution_time)
            
            return result
            
        except Exception as e:
            self.logger.error(f"Node {node_name} failed: {e}")
            self.record_stats(node_name, False, time.time() - start_time)
            raise
    
    def execute_with_retry(self, cmd: list, retries: int = None) -> subprocess.CompletedProcess:
        """재시도 로직을 포함한 명령 실행"""
        retries = retries or self.retry_count
        last_error = None
        
        for attempt in range(retries):
            try:
                self.logger.debug(f"Executing command (attempt {attempt + 1}): {' '.join(cmd)}")
                
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=self.timeout
                )
                
                if result.returncode == 0:
                    return result
                    
                last_error = f"Command failed with code {result.returncode}: {result.stderr}"
                self.logger.warning(f"Attempt {attempt + 1} failed: {last_error}")
                
                if attempt < retries - 1:
                    time.sleep(2 ** attempt)  # 지수 백오프
                    
            except subprocess.TimeoutExpired as e:
                last_error = f"Command timed out after {self.timeout}s"
                self.logger.warning(f"Timeout on attempt {attempt + 1}")
            except Exception as e:
                last_error = str(e)
                self.logger.error(f"Error on attempt {attempt + 1}: {e}")
        
        raise Exception(f"Command failed after {retries} attempts: {last_error}")
    
    def execute_parallel(self, nodes: List[tuple]) -> List[Any]:
        """노드들을 병렬로 실행"""
        futures = []
        
        for node_name, params in nodes:
            future = self.executor_pool.submit(self.execute, node_name, params)
            futures.append((node_name, future))
        
        results = []
        for node_name, future in futures:
            try:
                result = future.result(timeout=self.timeout)
                results.append(result)
                self.logger.info(f"Parallel node {node_name} completed")
            except FutureTimeoutError:
                results.append(None)
                self.logger.error(f"Parallel node {node_name} timed out")
            except Exception as e:
                results.append(None)
                self.logger.error(f"Parallel node {node_name} failed: {e}")
        
        return results
    
    def create_issue(self, params: Dict) -> str:
        """GitHub 이슈 생성 (개선된 버전)"""
        title = params.get('title', 'New Issue')
        body = params.get('body', '')
        labels = params.get('labels', 'ai-task')
        
        # 이슈 본문에 메타데이터 추가
        metadata = {
            'created_by': 'AI Orchestra v02',
            'timestamp': datetime.now().isoformat(),
            'pattern': params.get('pattern', 'unknown'),
            'request': params.get('request', '')
        }
        
        enhanced_body = f"{body}\n\n---\n```json\n{json.dumps(metadata, indent=2)}\n```"
        
        cmd = [
            "gh", "issue", "create",
            "--title", title,
            "--body", enhanced_body,
            "--label", labels,
            "-R", self.repo
        ]
        
        try:
            result = self.execute_with_retry(cmd)
            issue_url = result.stdout.strip()
            issue_num = issue_url.split('/')[-1]
            
            self.logger.info(f"Issue created: #{issue_num} - {title}")
            return issue_num
            
        except Exception as e:
            self.logger.error(f"Failed to create issue: {e}")
            return None
    
    def keyword_enrichment(self, params: Dict) -> Dict:
        """키워드 자동 추가 (개선된 버전)"""
        issue_num = params.get('issue_num')
        content = params.get('content', '')
        title = params.get('title', '')
        
        # 제목과 본문 모두 분석
        full_content = f"{title} {content}".lower()
        
        # 향상된 키워드 매핑
        keyword_rules = {
            'process_labels': {
                ('분석', 'analysis', '검토', 'review'): 'analysis',
                ('구현', 'implement', '개발', 'develop'): 'implementation',
                ('버그', 'bug', 'error', '오류'): 'bug',
                ('문서', 'document', 'docs'): 'documentation',
                ('테스트', 'test', '검증'): 'testing',
                ('리팩토링', 'refactor', '개선'): 'refactoring',
                ('긴급', 'urgent', 'critical'): 'urgent',
                ('배포', 'deploy', 'release'): 'deployment'
            },
            'content_hashtags': {
                ('ai', '인공지능'): '#AI',
                ('자동화', 'automation'): '#자동화',
                ('백업', 'backup'): '#백업',
                ('보안', 'security'): '#보안',
                ('성능', 'performance'): '#성능',
                ('ui', 'ux', '인터페이스'): '#UI/UX'
            }
        }
        
        labels = []
        hashtags = []
        
        # 라벨 추출
        for keywords, label in keyword_rules['process_labels'].items():
            if any(kw in full_content for kw in keywords):
                if label not in labels:
                    labels.append(label)
        
        # 해시태그 추출
        for keywords, hashtag in keyword_rules['content_hashtags'].items():
            if any(kw in full_content for kw in keywords):
                if hashtag not in hashtags:
                    hashtags.append(hashtag)
        
        # GitHub에 적용
        if issue_num:
            if labels:
                self.apply_labels(issue_num, labels)
            if hashtags:
                self.add_hashtags(issue_num, hashtags)
        
        return {
            'labels': labels,
            'hashtags': hashtags,
            'confidence': len(labels) + len(hashtags) > 0
        }
    
    def apply_labels(self, issue_num: str, labels: List[str]):
        """GitHub 이슈에 라벨 추가"""
        cmd = [
            "gh", "issue", "edit", str(issue_num),
            "--add-label", ",".join(labels),
            "-R", self.repo
        ]
        
        try:
            self.execute_with_retry(cmd, retries=2)
            self.logger.info(f"Labels added to #{issue_num}: {labels}")
        except Exception as e:
            self.logger.error(f"Failed to add labels: {e}")
    
    def add_hashtags(self, issue_num: str, hashtags: List[str]):
        """이슈에 해시태그 코멘트 추가"""
        hashtag_text = " ".join(hashtags)
        comment = f"🏷️ **키워드**: {hashtag_text}"
        
        cmd = [
            "gh", "issue", "comment", str(issue_num),
            "--body", comment,
            "-R", self.repo
        ]
        
        try:
            self.execute_with_retry(cmd, retries=2)
            self.logger.info(f"Hashtags added to #{issue_num}: {hashtags}")
        except Exception as e:
            self.logger.error(f"Failed to add hashtags: {e}")
    
    def ai_analysis(self, params: Dict) -> str:
        """AI 분석 실행 (개선된 버전)"""
        prompt = params.get('prompt', '')
        ai = params.get('ai', 'gemini')
        issue_num = params.get('issue_num', '')
        
        # AI별 설정 적용
        ai_config = self.ai_configs.get(ai, {})
        timeout = ai_config.get('timeout', self.timeout)
        
        # AI 사용 가능 여부 확인
        if not shutil.which(ai):
            self.logger.warning(f"{ai} not available, using mock response")
            return f"[Mock {ai} response for: {prompt[:50]}...]"
        
        full_prompt = f"이슈 #{issue_num}: {prompt}" if issue_num else prompt
        
        # AI 명령 실행
        if ai == 'gemini':
            cmd = ["gemini", "-p", full_prompt]
        elif ai == 'claude':
            cmd = ["claude", "-p", full_prompt]
        else:
            cmd = ["codex", "exec", full_prompt]
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            
            output = result.stdout if result.returncode == 0 else f"Error: {result.stderr}"
            
            # 결과를 이슈에 기록
            if issue_num and output:
                self.record_ai_result(issue_num, ai, output)
            
            return output
            
        except subprocess.TimeoutExpired:
            self.logger.error(f"{ai} timed out after {timeout}s")
            return f"[{ai} timeout]"
        except Exception as e:
            self.logger.error(f"{ai} failed: {e}")
            return f"[{ai} error: {e}]"
    
    def record_ai_result(self, issue_num: str, ai: str, output: str):
        """AI 결과를 이슈에 기록"""
        # 출력 길이 제한
        max_length = 2000
        if len(output) > max_length:
            output = output[:max_length] + "\n...[truncated]"
        
        comment = f"### 🤖 {ai.upper()} 분석 결과\n\n```\n{output}\n```"
        
        cmd = [
            "gh", "issue", "comment", str(issue_num),
            "--body", comment,
            "-R", self.repo
        ]
        
        try:
            self.execute_with_retry(cmd, retries=2)
        except Exception as e:
            self.logger.error(f"Failed to record AI result: {e}")
    
    def ai_implementation(self, params: Dict) -> str:
        """AI 구현"""
        params['ai'] = params.get('ai', 'claude')
        params['prompt'] = params.get('prompt', '요구사항에 따라 구현하세요')
        return self.ai_analysis(params)
    
    def ai_testing(self, params: Dict) -> str:
        """AI 테스트"""
        params['ai'] = params.get('ai', 'codex')
        params['prompt'] = params.get('prompt', '구현된 코드를 테스트하세요')
        return self.ai_analysis(params)
    
    def generate_report(self, params: Dict) -> str:
        """종합 보고서 생성"""
        issue_num = params.get('issue_num')
        results = params.get('results', [])
        pattern = params.get('pattern', 'unknown')
        
        # 보고서 생성
        report = f"# 📊 실행 보고서\n\n"
        report += f"**패턴**: {pattern}\n"
        report += f"**시간**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        
        # 실행 통계
        if self.execution_stats:
            report += "## 📈 실행 통계\n\n"
            for node, stats in self.execution_stats.items():
                success_rate = stats['success'] / stats['total'] * 100 if stats['total'] > 0 else 0
                avg_time = stats['total_time'] / stats['total'] if stats['total'] > 0 else 0
                report += f"- **{node}**: {success_rate:.1f}% 성공률, {avg_time:.2f}초 평균\n"
            report += "\n"
        
        # 결과 요약
        report += "## 📝 실행 결과\n\n"
        for i, result in enumerate(results, 1):
            if result:
                result_str = str(result)[:500]
                report += f"### Step {i}\n```\n{result_str}\n```\n\n"
        
        # 이슈에 보고서 추가
        if issue_num:
            cmd = [
                "gh", "issue", "comment", str(issue_num),
                "--body", report,
                "-R", self.repo
            ]
            
            try:
                self.execute_with_retry(cmd, retries=2)
                self.logger.info(f"Report added to #{issue_num}")
            except Exception as e:
                self.logger.error(f"Failed to add report: {e}")
        
        return report
    
    def parse_solution(self, params: Dict) -> str:
        """솔루션 파싱"""
        params['ai'] = 'gemini'
        params['prompt'] = params.get('prompt', '제공된 솔루션의 구조를 분석하세요')
        return self.ai_analysis(params)
    
    def analyze_features(self, params: Dict) -> str:
        """기능 분석"""
        params['ai'] = 'claude'
        params['prompt'] = params.get('prompt', '기능과 작동 방식을 상세히 분석하세요')
        return self.ai_analysis(params)
    
    def evaluate_fit(self, params: Dict) -> str:
        """적합성 평가"""
        params['ai'] = 'codex'
        params['prompt'] = params.get('prompt', '기술적 적합성과 위험 요소를 평가하세요')
        return self.ai_analysis(params)
    
    def adoption_report(self, params: Dict) -> str:
        """도입 보고서"""
        return self.generate_report(params)
    
    def validate_result(self, params: Dict) -> bool:
        """결과 검증"""
        result = params.get('result')
        criteria = params.get('criteria', {})
        
        # 기본 검증
        if not result:
            return False
        
        # 커스텀 검증 로직
        for key, expected in criteria.items():
            if key not in result or result[key] != expected:
                return False
        
        return True
    
    def notify(self, params: Dict) -> bool:
        """알림 전송"""
        message = params.get('message', 'Task completed')
        issue_num = params.get('issue_num')
        
        if issue_num:
            cmd = [
                "gh", "issue", "comment", str(issue_num),
                "--body", f"🔔 **알림**: {message}",
                "-R", self.repo
            ]
            
            try:
                self.execute_with_retry(cmd, retries=1)
                return True
            except:
                return False
        
        print(f"🔔 {message}")
        return True
    
    def record_stats(self, node_name: str, success: bool, execution_time: float):
        """실행 통계 기록"""
        if node_name not in self.execution_stats:
            self.execution_stats[node_name] = {
                'total': 0,
                'success': 0,
                'failure': 0,
                'total_time': 0
            }
        
        stats = self.execution_stats[node_name]
        stats['total'] += 1
        stats['total_time'] += execution_time
        
        if success:
            stats['success'] += 1
        else:
            stats['failure'] += 1
    
    def get_stats(self) -> Dict:
        """통계 반환"""
        return self.execution_stats
    
    def cleanup(self):
        """리소스 정리"""
        self.executor_pool.shutdown(wait=True)
        self.logger.info("Node executor cleaned up")


if __name__ == "__main__":
    import sys
    
    # 설정 파일 생성 (없으면)
    if not os.path.exists('node_config.json'):
        default_config = {
            "repo": "ihw33/ai-orchestra-v02",
            "timeout": 300,
            "retry_count": 3,
            "ai_models": {
                "gemini": {"timeout": 120, "retry": 3},
                "claude": {"timeout": 180, "retry": 2},
                "codex": {"timeout": 150, "retry": 2}
            }
        }
        
        with open('node_config.json', 'w') as f:
            json.dump(default_config, f, indent=2)
        print("✅ Created default node_config.json")
    
    # 실행
    executor = ImprovedNodeExecutor()
    
    try:
        if len(sys.argv) > 1:
            node_name = sys.argv[1]
            
            if node_name == '--list':
                print("📋 Available nodes:")
                for name in executor.nodes.keys():
                    print(f"  - {name}")
            
            elif node_name == '--stats':
                stats = executor.get_stats()
                print("📊 Execution Statistics:")
                for node, data in stats.items():
                    print(f"  {node}: {data}")
            
            else:
                # 파라미터 파싱
                params = {}
                if len(sys.argv) > 2:
                    try:
                        params = json.loads(sys.argv[2])
                    except json.JSONDecodeError:
                        params = {"prompt": sys.argv[2]}
                
                # 노드 실행
                result = executor.execute(node_name, params)
                if result:
                    print(f"✅ {node_name} completed")
                    print(f"Result: {str(result)[:500]}")
        else:
            print("Usage:")
            print("  python3 improved_node_executor.py NODE_NAME [PARAMS]")
            print("  python3 improved_node_executor.py --list")
            print("  python3 improved_node_executor.py --stats")
    
    finally:
        executor.cleanup()