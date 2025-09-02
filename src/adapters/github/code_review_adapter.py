"""
GitHub Code Review Adapter
GitHub PR 코드 리뷰 워크플로우 구현
Claude 서브에이전트 및 SuperClaude 통합
"""

import subprocess
import json
import re
import tempfile
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import time
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from ports.code_review_port import (
    CodeReviewPort,
    ReviewAutomationPort,
    ReviewAIIntegrationPort,
    ReviewStatus,
    ReviewSeverity,
    ReviewCategory,
    ReviewComment,
    ReviewResult,
    ReviewChecklist,
    ReviewRequest
)
from adapters.ai.claude_command_adapter import ClaudeCommandAdapter
from ports.ai_command_port import AIType, CommandType

class GitHubCodeReviewAdapter(CodeReviewPort, ReviewAutomationPort, ReviewAIIntegrationPort):
    """GitHub 코드 리뷰 Adapter"""
    
    def __init__(self, repo: str = "ihw33/ai-orchestra-v02"):
        self.repo = repo
        self.claude_adapter = ClaudeCommandAdapter()
        self.review_templates = self._init_review_templates()
        self.ai_reviewer_mapping = self._init_ai_reviewer_mapping()
    
    def _init_review_templates(self) -> Dict:
        """리뷰 템플릿 초기화"""
        return {
            'security': [
                '하드코딩된 비밀번호나 API 키가 있는가?',
                'SQL 인젝션 취약점이 있는가?',
                'XSS 취약점이 있는가?',
                '민감한 정보가 로그에 노출되는가?'
            ],
            'performance': [
                'N+1 쿼리 문제가 있는가?',
                '불필요한 반복문이 있는가?',
                '메모리 누수 가능성이 있는가?',
                '캐싱을 활용할 수 있는가?'
            ],
            'code_quality': [
                '함수가 단일 책임 원칙을 지키는가?',
                '변수명이 명확한가?',
                '중복 코드가 있는가?',
                '에러 처리가 적절한가?'
            ],
            'architecture': [
                'Port/Adapter 패턴을 지키는가?',
                '도메인 로직이 분리되어 있는가?',
                '의존성 주입을 사용하는가?',
                '테스트 가능한 구조인가?'
            ],
            'testing': [
                '단위 테스트가 있는가?',
                '엣지 케이스를 다루는가?',
                '테스트 커버리지가 충분한가?',
                '통합 테스트가 필요한가?'
            ]
        }
    
    def _init_ai_reviewer_mapping(self) -> Dict:
        """AI 리뷰어 매핑"""
        return {
            'claude': {
                'subagent': 'code-reviewer',
                'sc_command': '/SC Review',
                'strengths': ['코드 품질', '아키텍처', '보안']
            },
            'gemini': {
                'command': '-p',
                'strengths': ['설계', 'UX', '문서화']
            },
            'codex': {
                'command': 'exec',
                'strengths': ['백엔드', 'API', '성능']
            }
        }
    
    # === CodeReviewPort 구현 ===
    
    def request_review(self, request: ReviewRequest) -> bool:
        """코드 리뷰 요청"""
        
        try:
            # PR 정보 확인
            pr_info = self._get_pr_info(request.pr_number)
            if not pr_info:
                return False
            
            # 리뷰어가 Claude인 경우 특별 처리
            if request.reviewer.lower() == 'claude':
                if request.use_superclaude:
                    # SuperClaude 사용
                    return self._request_claude_sc_review(request)
                elif request.use_subagent:
                    # 서브에이전트 사용
                    return self._request_claude_subagent_review(request)
            
            # 일반 리뷰 요청
            cmd = f'gh pr edit {request.pr_number} -R {self.repo} --add-reviewer {request.reviewer}'
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            
            return result.returncode == 0
            
        except Exception as e:
            print(f"리뷰 요청 실패: {e}")
            return False
    
    def perform_review(self, pr_number: int, reviewer: str) -> ReviewResult:
        """코드 리뷰 수행"""
        
        start_time = time.time()
        
        # 1. PR 변경사항 분석
        analysis = self.analyze_code_changes(pr_number)
        
        # 2. AI 리뷰어 선택 및 실행
        if reviewer.lower() in ['claude', 'gemini', 'codex']:
            # AI 리뷰
            prompt = self.format_review_prompt(analysis, reviewer)
            
            if reviewer.lower() == 'claude':
                # Claude는 서브에이전트 또는 /SC Review 사용
                use_sc = 'critical' in str(analysis).lower()  # 중요한 변경은 /SC 사용
                result = self.execute_ai_review(reviewer, prompt, use_sc)
            else:
                # 다른 AI
                result = self.execute_ai_review(reviewer, prompt, False)
        else:
            # 사람 리뷰어
            result = self._wait_for_human_review(pr_number, reviewer)
        
        # 시간 기록
        result.time_taken = int(time.time() - start_time)
        
        return result
    
    def get_review_checklist(self, pr_type: str) -> ReviewChecklist:
        """PR 타입별 체크리스트"""
        
        # PR 타입별 중점 체크 항목
        if pr_type == 'security':
            return ReviewChecklist(
                security_checks=self.review_templates['security'],
                performance_checks=[],
                quality_checks=self.review_templates['code_quality'][:2],
                architecture_checks=[],
                test_checks=self.review_templates['testing'][:2]
            )
        elif pr_type == 'feature':
            return ReviewChecklist(
                security_checks=self.review_templates['security'][:2],
                performance_checks=self.review_templates['performance'],
                quality_checks=self.review_templates['code_quality'],
                architecture_checks=self.review_templates['architecture'],
                test_checks=self.review_templates['testing']
            )
        else:  # 기본값
            return ReviewChecklist(
                security_checks=self.review_templates['security'][:2],
                performance_checks=self.review_templates['performance'][:2],
                quality_checks=self.review_templates['code_quality'],
                architecture_checks=self.review_templates['architecture'][:2],
                test_checks=self.review_templates['testing'][:2]
            )
    
    def analyze_code_changes(self, pr_number: int) -> Dict:
        """코드 변경사항 분석"""
        
        analysis = {
            'pr_number': pr_number,
            'files_changed': [],
            'total_additions': 0,
            'total_deletions': 0,
            'languages': set(),
            'has_tests': False,
            'has_docs': False,
            'complexity': 'low'  # low, medium, high
        }
        
        # PR diff 가져오기
        cmd = f'gh pr diff {pr_number} -R {self.repo}'
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        
        if result.returncode == 0:
            diff = result.stdout
            
            # 파일별 분석
            file_pattern = r'diff --git a/(.*) b/(.*)'
            files = re.findall(file_pattern, diff)
            
            for file_a, file_b in files:
                file_path = file_b
                analysis['files_changed'].append(file_path)
                
                # 언어 감지
                if file_path.endswith('.py'):
                    analysis['languages'].add('python')
                elif file_path.endswith(('.js', '.jsx', '.ts', '.tsx')):
                    analysis['languages'].add('javascript')
                elif file_path.endswith('.go'):
                    analysis['languages'].add('go')
                
                # 테스트 파일 확인
                if 'test' in file_path.lower():
                    analysis['has_tests'] = True
                
                # 문서 파일 확인
                if file_path.endswith('.md') or 'doc' in file_path.lower():
                    analysis['has_docs'] = True
            
            # 변경 라인 수 계산
            additions = len(re.findall(r'^\+[^+]', diff, re.MULTILINE))
            deletions = len(re.findall(r'^-[^-]', diff, re.MULTILINE))
            analysis['total_additions'] = additions
            analysis['total_deletions'] = deletions
            
            # 복잡도 판단
            if additions + deletions > 500:
                analysis['complexity'] = 'high'
            elif additions + deletions > 100:
                analysis['complexity'] = 'medium'
        
        # PR 정보 추가
        pr_info = self._get_pr_info(pr_number)
        if pr_info:
            analysis['title'] = pr_info.get('title', '')
            analysis['body'] = pr_info.get('body', '')
            analysis['labels'] = [l['name'] for l in pr_info.get('labels', [])]
        
        return analysis
    
    def generate_review_comments(self, analysis: Dict) -> List[ReviewComment]:
        """리뷰 코멘트 생성"""
        
        comments = []
        
        # 테스트 부재
        if not analysis['has_tests'] and analysis['complexity'] != 'low':
            comments.append(ReviewComment(
                file_path='',
                line_number=0,
                comment='테스트가 없습니다. 테스트 추가를 고려해주세요.',
                severity=ReviewSeverity.MAJOR,
                category=ReviewCategory.TESTING
            ))
        
        # 문서 부재
        if not analysis['has_docs'] and analysis['complexity'] == 'high':
            comments.append(ReviewComment(
                file_path='',
                line_number=0,
                comment='복잡한 변경사항에 대한 문서가 없습니다.',
                severity=ReviewSeverity.MINOR,
                category=ReviewCategory.DOCUMENTATION
            ))
        
        # 대량 변경 경고
        if analysis['total_additions'] + analysis['total_deletions'] > 1000:
            comments.append(ReviewComment(
                file_path='',
                line_number=0,
                comment='PR이 너무 큽니다. 작은 단위로 나누는 것을 고려해주세요.',
                severity=ReviewSeverity.SUGGESTION,
                category=ReviewCategory.CODE_QUALITY
            ))
        
        return comments
    
    def post_review_comments(self, pr_number: int, comments: List[ReviewComment]) -> bool:
        """리뷰 코멘트 게시"""
        
        if not comments:
            return True
        
        # 코멘트 포맷팅
        review_body = "## 🤖 자동 코드 리뷰\n\n"
        
        # 심각도별 그룹핑
        critical = [c for c in comments if c.severity == ReviewSeverity.CRITICAL]
        major = [c for c in comments if c.severity == ReviewSeverity.MAJOR]
        minor = [c for c in comments if c.severity == ReviewSeverity.MINOR]
        suggestions = [c for c in comments if c.severity == ReviewSeverity.SUGGESTION]
        
        if critical:
            review_body += "### 🔴 반드시 수정 필요\n"
            for c in critical:
                review_body += f"- [{c.category.value}] {c.comment}\n"
                if c.suggested_fix:
                    review_body += f"  제안: {c.suggested_fix}\n"
        
        if major:
            review_body += "\n### 🟡 중요 개선사항\n"
            for c in major:
                review_body += f"- [{c.category.value}] {c.comment}\n"
        
        if minor:
            review_body += "\n### 🟢 사소한 개선\n"
            for c in minor:
                review_body += f"- [{c.category.value}] {c.comment}\n"
        
        if suggestions:
            review_body += "\n### 💡 제안사항\n"
            for c in suggestions:
                review_body += f"- {c.comment}\n"
        
        # 임시 파일에 저장
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write(review_body)
            body_file = f.name
        
        try:
            # PR에 코멘트 게시
            cmd = f'gh pr comment {pr_number} -R {self.repo} --body-file {body_file}'
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            
            return result.returncode == 0
            
        finally:
            if os.path.exists(body_file):
                os.remove(body_file)
    
    def approve_pr(self, pr_number: int, comment: str) -> bool:
        """PR 승인"""
        
        cmd = f'gh pr review {pr_number} -R {self.repo} --approve --body "{comment}"'
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        
        return result.returncode == 0
    
    def request_changes(self, pr_number: int, comments: List[ReviewComment]) -> bool:
        """변경 요청"""
        
        # 코멘트 포맷팅
        body = "변경이 필요합니다:\n\n"
        for c in comments:
            if c.severity in [ReviewSeverity.CRITICAL, ReviewSeverity.MAJOR]:
                body += f"- {c.comment}\n"
        
        cmd = f'gh pr review {pr_number} -R {self.repo} --request-changes --body "{body}"'
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        
        return result.returncode == 0
    
    # === ReviewAutomationPort 구현 ===
    
    def auto_assign_reviewer(self, pr_number: int) -> str:
        """자동 리뷰어 할당"""
        
        # PR 분석
        analysis = self.analyze_code_changes(pr_number)
        
        # 언어/라벨 기반 리뷰어 선택
        if 'ai-claude' in analysis.get('labels', []):
            # Claude가 작성한 코드는 다른 AI가 리뷰
            return 'gemini'
        elif 'ai-gemini' in analysis.get('labels', []):
            return 'claude'
        elif 'ai-codex' in analysis.get('labels', []):
            return 'claude'
        
        # 복잡도 기반
        if analysis['complexity'] == 'high':
            return 'claude'  # 복잡한 코드는 Claude가 리뷰
        elif 'backend' in str(analysis.get('labels', [])).lower():
            return 'codex'
        else:
            return 'gemini'
    
    def should_auto_review(self, pr_number: int) -> bool:
        """자동 리뷰 필요 여부"""
        
        pr_info = self._get_pr_info(pr_number)
        if not pr_info:
            return False
        
        labels = [l['name'] for l in pr_info.get('labels', [])]
        
        # 자동 리뷰 조건
        auto_review_labels = ['automated', 'ai-task', 'auto-review']
        skip_review_labels = ['wip', 'draft', 'skip-review']
        
        # Skip 라벨이 있으면 리뷰 안함
        if any(label in labels for label in skip_review_labels):
            return False
        
        # Auto 라벨이 있으면 리뷰
        if any(label in labels for label in auto_review_labels):
            return True
        
        # AI가 만든 PR은 자동 리뷰
        if any(label.startswith('ai-') for label in labels):
            return True
        
        return False
    
    def trigger_review_workflow(self, pr_number: int) -> Dict:
        """리뷰 워크플로우 트리거"""
        
        workflow = {
            'pr_number': pr_number,
            'steps': [],
            'success': True
        }
        
        # 1. 자동 리뷰 필요 여부 확인
        if not self.should_auto_review(pr_number):
            workflow['steps'].append('자동 리뷰 불필요')
            return workflow
        
        # 2. 리뷰어 자동 할당
        reviewer = self.auto_assign_reviewer(pr_number)
        workflow['steps'].append(f'리뷰어 할당: {reviewer}')
        
        # 3. 리뷰 요청
        request = ReviewRequest(
            pr_number=pr_number,
            requester='auto',
            reviewer=reviewer,
            focus_areas=[ReviewCategory.CODE_QUALITY, ReviewCategory.ARCHITECTURE],
            use_superclaude=(reviewer == 'claude'),
            use_subagent=True
        )
        
        if self.request_review(request):
            workflow['steps'].append('리뷰 요청 성공')
        else:
            workflow['success'] = False
            workflow['steps'].append('리뷰 요청 실패')
            return workflow
        
        # 4. 리뷰 수행
        result = self.perform_review(pr_number, reviewer)
        workflow['steps'].append(f'리뷰 완료: {result.status.value}')
        
        # 5. 결과 처리
        if result.status == ReviewStatus.APPROVED:
            self.approve_pr(pr_number, result.summary)
            workflow['steps'].append('PR 승인됨')
        elif result.status == ReviewStatus.CHANGES_REQUESTED:
            self.request_changes(pr_number, result.comments)
            workflow['steps'].append('변경 요청됨')
        
        return workflow
    
    def handle_review_feedback(self, pr_number: int, feedback: ReviewResult) -> Dict:
        """리뷰 피드백 처리"""
        
        handling = {
            'pr_number': pr_number,
            'actions': []
        }
        
        # Critical 이슈가 있으면 즉시 알림
        critical_comments = [c for c in feedback.comments 
                           if c.severity == ReviewSeverity.CRITICAL]
        
        if critical_comments:
            # PR에 긴급 코멘트
            urgent_body = "🚨 **긴급 수정 필요**\n\n"
            for c in critical_comments:
                urgent_body += f"- {c.comment}\n"
            
            self._post_pr_comment(pr_number, urgent_body)
            handling['actions'].append('긴급 알림 발송')
        
        # 수정 사항이 있으면 원작성자에게 할당
        if feedback.status == ReviewStatus.CHANGES_REQUESTED:
            # 원작성자 찾기
            pr_info = self._get_pr_info(pr_number)
            if pr_info:
                author = pr_info.get('author', {}).get('login')
                # 수정 요청 이슈 생성
                handling['actions'].append(f'{author}에게 수정 요청')
        
        return handling
    
    def track_review_metrics(self, pr_number: int) -> Dict:
        """리뷰 메트릭 추적"""
        
        metrics = {
            'pr_number': pr_number,
            'review_count': 0,
            'approval_count': 0,
            'changes_requested_count': 0,
            'avg_review_time': 0,
            'comment_count': 0
        }
        
        # 리뷰 히스토리 가져오기
        cmd = f'gh pr view {pr_number} -R {self.repo} --json reviews'
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        
        if result.returncode == 0:
            data = json.loads(result.stdout)
            reviews = data.get('reviews', [])
            
            metrics['review_count'] = len(reviews)
            
            for review in reviews:
                state = review.get('state', '')
                if state == 'APPROVED':
                    metrics['approval_count'] += 1
                elif state == 'CHANGES_REQUESTED':
                    metrics['changes_requested_count'] += 1
        
        # 코멘트 수
        cmd = f'gh pr view {pr_number} -R {self.repo} --json comments'
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        
        if result.returncode == 0:
            data = json.loads(result.stdout)
            metrics['comment_count'] = len(data.get('comments', []))
        
        return metrics
    
    # === ReviewAIIntegrationPort 구현 ===
    
    def select_ai_reviewer(self, pr_content: Dict) -> Tuple[str, str]:
        """AI 리뷰어 선택"""
        
        # 복잡도와 변경 내용 기반 선택
        complexity = pr_content.get('complexity', 'low')
        languages = pr_content.get('languages', set())
        
        if complexity == 'high' or 'security' in str(pr_content):
            # 복잡하거나 보안 관련은 Claude + /SC Review
            return 'claude', '/SC Review'
        elif 'python' in languages or 'architecture' in str(pr_content):
            # Python이나 아키텍처는 Claude + 서브에이전트
            return 'claude', 'code-reviewer'
        elif 'backend' in str(pr_content) or 'api' in str(pr_content):
            # 백엔드는 Codex
            return 'codex', 'exec'
        else:
            # 기본값 Gemini
            return 'gemini', '-p'
    
    def format_review_prompt(self, pr_data: Dict, reviewer_type: str) -> str:
        """리뷰 프롬프트 생성"""
        
        prompt = f"""PR #{pr_data['pr_number']} 코드 리뷰

제목: {pr_data.get('title', '')}

변경 파일: {len(pr_data.get('files_changed', []))}개
추가: +{pr_data.get('total_additions', 0)} 라인
삭제: -{pr_data.get('total_deletions', 0)} 라인

다음 관점에서 리뷰해주세요:
"""
        
        # 리뷰어별 중점사항
        if reviewer_type.lower() == 'claude':
            prompt += """
1. 코드 품질과 가독성
2. 아키텍처 및 설계 패턴
3. 보안 취약점
4. Port/Adapter 패턴 준수
5. 도메인 로직 분리
"""
        elif reviewer_type.lower() == 'codex':
            prompt += """
1. API 설계 및 엔드포인트
2. 데이터베이스 쿼리 최적화
3. 백엔드 성능
4. 에러 처리
"""
        elif reviewer_type.lower() == 'gemini':
            prompt += """
1. 전체적인 설계 및 구조
2. 코드 재사용성
3. 테스트 커버리지
4. 문서화
"""
        
        # 체크리스트 추가
        checklist = self.get_review_checklist('feature')
        prompt += "\n체크리스트:\n"
        
        for check in checklist.security_checks[:2]:
            prompt += f"- [ ] {check}\n"
        for check in checklist.quality_checks[:3]:
            prompt += f"- [ ] {check}\n"
        
        return prompt
    
    def execute_ai_review(self, reviewer: str, prompt: str, 
                         use_sc: bool = False) -> ReviewResult:
        """AI 리뷰 실행"""
        
        output = ""
        
        if reviewer.lower() == 'claude':
            if use_sc:
                # SuperClaude /SC Review 사용
                sc_prompt = self.claude_adapter.format_sc_prompt('/SC Review', prompt)
                result = self._execute_claude_with_sc(sc_prompt)
                output = result
            else:
                # 서브에이전트 사용
                command = self.claude_adapter.select_best_command(
                    AIType.CLAUDE, 
                    prompt
                )
                result = self.claude_adapter.execute_with_command(
                    AIType.CLAUDE,
                    command,
                    prompt
                )
                output = result.output if result.success else ""
        
        elif reviewer.lower() == 'gemini':
            # Gemini 실행
            output = self._execute_gemini_review(prompt)
        
        elif reviewer.lower() == 'codex':
            # Codex 실행
            output = self._execute_codex_review(prompt)
        
        # 출력 파싱
        return self.parse_ai_review_output(output, reviewer)
    
    def parse_ai_review_output(self, output: str, reviewer: str) -> ReviewResult:
        """AI 리뷰 출력 파싱"""
        
        # 기본 결과
        result = ReviewResult(
            pr_number=0,  # 나중에 설정
            reviewer=reviewer,
            status=ReviewStatus.PENDING,
            comments=[],
            summary="",
            reviewed_at=datetime.now()
        )
        
        # 승인/거부 판단
        if 'approve' in output.lower() or '승인' in output.lower():
            result.status = ReviewStatus.APPROVED
        elif 'changes requested' in output.lower() or '수정 필요' in output.lower():
            result.status = ReviewStatus.CHANGES_REQUESTED
        else:
            result.status = ReviewStatus.APPROVED  # 기본값
        
        # 요약 추출
        summary_pattern = r'(?:요약|summary)[:：]\s*(.+?)(?:\n|$)'
        summary_match = re.search(summary_pattern, output, re.IGNORECASE)
        if summary_match:
            result.summary = summary_match.group(1).strip()
        else:
            # 첫 줄을 요약으로
            lines = output.strip().split('\n')
            if lines:
                result.summary = lines[0][:200]
        
        # 코멘트 파싱 (- 로 시작하는 항목들)
        comment_pattern = r'^[-*]\s+(.+)$'
        comments = re.findall(comment_pattern, output, re.MULTILINE)
        
        for comment_text in comments:
            # 심각도 판단
            severity = ReviewSeverity.SUGGESTION
            if any(word in comment_text.lower() for word in ['critical', '반드시', '심각']):
                severity = ReviewSeverity.CRITICAL
            elif any(word in comment_text.lower() for word in ['major', '중요', '필요']):
                severity = ReviewSeverity.MAJOR
            elif any(word in comment_text.lower() for word in ['minor', '사소', '개선']):
                severity = ReviewSeverity.MINOR
            
            # 카테고리 판단
            category = ReviewCategory.CODE_QUALITY
            if any(word in comment_text.lower() for word in ['security', '보안']):
                category = ReviewCategory.SECURITY
            elif any(word in comment_text.lower() for word in ['performance', '성능']):
                category = ReviewCategory.PERFORMANCE
            elif any(word in comment_text.lower() for word in ['test', '테스트']):
                category = ReviewCategory.TESTING
            
            result.comments.append(ReviewComment(
                file_path='',
                line_number=0,
                comment=comment_text,
                severity=severity,
                category=category
            ))
        
        # 점수 추출 (있는 경우)
        score_pattern = r'(?:score|점수)[:：]\s*(\d+)'
        score_match = re.search(score_pattern, output, re.IGNORECASE)
        if score_match:
            result.score = int(score_match.group(1))
        
        return result
    
    def cross_check_reviews(self, reviews: List[ReviewResult]) -> ReviewResult:
        """여러 AI 리뷰 교차 검증"""
        
        if not reviews:
            return None
        
        # 통합 결과 생성
        consolidated = ReviewResult(
            pr_number=reviews[0].pr_number,
            reviewer='cross-check',
            status=ReviewStatus.PENDING,
            comments=[],
            summary="여러 AI의 교차 검증 결과",
            reviewed_at=datetime.now()
        )
        
        # 상태 결정 (다수결)
        status_votes = {}
        for review in reviews:
            status = review.status
            status_votes[status] = status_votes.get(status, 0) + 1
        
        consolidated.status = max(status_votes, key=status_votes.get)
        
        # 코멘트 통합 (중복 제거)
        seen_comments = set()
        for review in reviews:
            for comment in review.comments:
                comment_key = (comment.category, comment.comment[:50])
                if comment_key not in seen_comments:
                    seen_comments.add(comment_key)
                    consolidated.comments.append(comment)
        
        # 평균 점수
        scores = [r.score for r in reviews if r.score is not None]
        if scores:
            consolidated.score = sum(scores) // len(scores)
        
        return consolidated
    
    # === Helper Methods ===
    
    def _get_pr_info(self, pr_number: int) -> Optional[Dict]:
        """PR 정보 조회"""
        
        cmd = f'gh pr view {pr_number} -R {self.repo} --json number,title,body,labels,author'
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        
        if result.returncode == 0:
            return json.loads(result.stdout)
        return None
    
    def _request_claude_sc_review(self, request: ReviewRequest) -> bool:
        """Claude SuperClaude 리뷰 요청"""
        
        pr_data = self.analyze_code_changes(request.pr_number)
        prompt = self.format_review_prompt(pr_data, 'claude')
        
        # /SC Review 프롬프트
        sc_prompt = f"/SC Review\n\n{prompt}"
        
        # 실행
        output = self._execute_claude_with_sc(sc_prompt)
        
        # 결과를 PR에 게시
        if output:
            self._post_pr_comment(request.pr_number, output)
            return True
        
        return False
    
    def _request_claude_subagent_review(self, request: ReviewRequest) -> bool:
        """Claude 서브에이전트 리뷰 요청"""
        
        pr_data = self.analyze_code_changes(request.pr_number)
        prompt = self.format_review_prompt(pr_data, 'claude')
        
        # code-reviewer 서브에이전트 활성화
        subagent_prompt = f"@code-reviewer\n\n{prompt}"
        
        # 실행
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write(subagent_prompt)
            prompt_file = f.name
        
        try:
            cmd = f'claude -p < {prompt_file}'
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=120)
            
            if result.returncode == 0:
                self._post_pr_comment(request.pr_number, result.stdout)
                return True
        finally:
            if os.path.exists(prompt_file):
                os.remove(prompt_file)
        
        return False
    
    def _execute_claude_with_sc(self, prompt: str) -> str:
        """Claude를 /SC 명령어로 실행"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write(prompt)
            prompt_file = f.name
        
        try:
            cmd = f'claude -p < {prompt_file}'
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=120)
            
            if result.returncode == 0:
                return result.stdout
        except:
            pass
        finally:
            if os.path.exists(prompt_file):
                os.remove(prompt_file)
        
        return ""
    
    def _execute_gemini_review(self, prompt: str) -> str:
        """Gemini 리뷰 실행"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write(prompt)
            prompt_file = f.name
        
        try:
            cmd = f'gemini -p < {prompt_file}'
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=120)
            
            if result.returncode == 0:
                return result.stdout
        except:
            pass
        finally:
            if os.path.exists(prompt_file):
                os.remove(prompt_file)
        
        return ""
    
    def _execute_codex_review(self, prompt: str) -> str:
        """Codex 리뷰 실행"""
        
        try:
            cmd = f'codex exec "{prompt}"'
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=120)
            
            if result.returncode == 0:
                return result.stdout
        except:
            pass
        
        return ""
    
    def _post_pr_comment(self, pr_number: int, comment: str) -> bool:
        """PR에 코멘트 게시"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write(comment)
            body_file = f.name
        
        try:
            cmd = f'gh pr comment {pr_number} -R {self.repo} --body-file {body_file}'
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            return result.returncode == 0
        finally:
            if os.path.exists(body_file):
                os.remove(body_file)
    
    def _wait_for_human_review(self, pr_number: int, reviewer: str) -> ReviewResult:
        """사람 리뷰어 대기"""
        
        # 실제로는 웹훅이나 폴링으로 구현
        return ReviewResult(
            pr_number=pr_number,
            reviewer=reviewer,
            status=ReviewStatus.PENDING,
            comments=[],
            summary="사람 리뷰 대기 중",
            reviewed_at=datetime.now()
        )


# 사용 예시
if __name__ == "__main__":
    adapter = GitHubCodeReviewAdapter()
    
    # PR 분석
    print("=== PR 분석 ===")
    # analysis = adapter.analyze_code_changes(90)
    # print(f"변경 파일: {len(analysis.get('files_changed', []))}개")
    # print(f"복잡도: {analysis.get('complexity')}")
    
    # 자동 리뷰어 선택
    print("\n=== 자동 리뷰어 ===")
    # reviewer = adapter.auto_assign_reviewer(90)
    # print(f"선택된 리뷰어: {reviewer}")
    
    # 리뷰 체크리스트
    print("\n=== 체크리스트 ===")
    checklist = adapter.get_review_checklist('feature')
    print(f"보안 체크: {len(checklist.security_checks)}개")
    print(f"품질 체크: {len(checklist.quality_checks)}개")