"""
Code Review Workflow
AI 기반 PR 코드 리뷰 자동화 워크플로우
"""

import sys
import os
from typing import Dict, List

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from src.adapters.github.code_review_adapter import GitHubCodeReviewAdapter
from src.adapters.github.pr_adapter import GitHubPRAdapter
from src.ports.code_review_port import (
    ReviewRequest,
    ReviewStatus,
    ReviewCategory,
    ReviewSeverity
)

class CodeReviewWorkflow:
    """코드 리뷰 워크플로우"""
    
    def __init__(self, repo: str = "ihw33/ai-orchestra-v02"):
        self.repo = repo
        self.review_adapter = GitHubCodeReviewAdapter(repo)
        self.pr_adapter = GitHubPRAdapter(repo)
    
    def execute_full_review_cycle(self, pr_number: int) -> Dict:
        """전체 리뷰 사이클 실행"""
        
        print(f"\n🔍 PR #{pr_number} 리뷰 사이클 시작")
        
        result = {
            'pr_number': pr_number,
            'steps': [],
            'success': True,
            'final_status': None
        }
        
        # 1. PR 정보 확인
        pr = self.pr_adapter.get_pr(pr_number)
        if not pr:
            result['success'] = False
            result['steps'].append('❌ PR을 찾을 수 없음')
            return result
        
        print(f"📋 PR: {pr.title}")
        result['steps'].append(f"PR 확인: {pr.title}")
        
        # 2. 자동 리뷰 필요 여부 확인
        if not self.review_adapter.should_auto_review(pr_number):
            result['steps'].append('⏭️ 자동 리뷰 불필요')
            print("⏭️ 자동 리뷰가 필요하지 않습니다")
            return result
        
        # 3. 코드 변경사항 분석
        print("📊 코드 변경사항 분석 중...")
        analysis = self.review_adapter.analyze_code_changes(pr_number)
        result['steps'].append(f"분석 완료: {len(analysis['files_changed'])}개 파일")
        
        # 4. 리뷰어 자동 선택
        reviewer = self.review_adapter.auto_assign_reviewer(pr_number)
        print(f"🤖 리뷰어 선택: {reviewer}")
        result['steps'].append(f"리뷰어 할당: {reviewer}")
        
        # 5. 리뷰 요청 생성
        request = self._create_review_request(pr_number, reviewer, analysis)
        
        # 6. 리뷰 실행
        print(f"🔄 {reviewer} 리뷰 실행 중...")
        review_result = self.review_adapter.perform_review(pr_number, reviewer)
        
        result['steps'].append(f"리뷰 완료: {review_result.status.value}")
        result['final_status'] = review_result.status.value
        
        # 7. 리뷰 결과 처리
        self._handle_review_result(pr_number, review_result)
        
        # 8. 크로스 체크 (필요시)
        if analysis['complexity'] == 'high':
            print("🔀 복잡한 PR - 크로스 체크 실행")
            cross_result = self._perform_cross_check(pr_number, reviewer)
            result['steps'].append("크로스 체크 완료")
        
        # 9. 최종 결정
        final_decision = self._make_final_decision(pr_number, review_result)
        result['steps'].append(f"최종 결정: {final_decision}")
        
        print(f"✅ 리뷰 사이클 완료: {final_decision}")
        
        return result
    
    def _create_review_request(self, pr_number: int, reviewer: str, 
                              analysis: Dict) -> ReviewRequest:
        """리뷰 요청 생성"""
        
        # 집중 검토 영역 결정
        focus_areas = []
        
        if not analysis.get('has_tests'):
            focus_areas.append(ReviewCategory.TESTING)
        
        if analysis['complexity'] == 'high':
            focus_areas.append(ReviewCategory.ARCHITECTURE)
            focus_areas.append(ReviewCategory.CODE_QUALITY)
        
        if 'security' in str(analysis.get('labels', [])).lower():
            focus_areas.append(ReviewCategory.SECURITY)
        
        # 기본값
        if not focus_areas:
            focus_areas = [ReviewCategory.CODE_QUALITY]
        
        # Claude 특별 처리
        use_sc = False
        use_subagent = True
        
        if reviewer.lower() == 'claude':
            # 복잡하거나 보안 관련은 /SC Review 사용
            if analysis['complexity'] == 'high' or ReviewCategory.SECURITY in focus_areas:
                use_sc = True
                use_subagent = False
        
        return ReviewRequest(
            pr_number=pr_number,
            requester='workflow',
            reviewer=reviewer,
            focus_areas=focus_areas,
            use_superclaude=use_sc,
            use_subagent=use_subagent
        )
    
    def _handle_review_result(self, pr_number: int, review_result):
        """리뷰 결과 처리"""
        
        # 코멘트 게시
        if review_result.comments:
            self.review_adapter.post_review_comments(pr_number, review_result.comments)
        
        # 상태별 처리
        if review_result.status == ReviewStatus.APPROVED:
            print("✅ PR 승인됨")
            self.review_adapter.approve_pr(pr_number, review_result.summary)
            
        elif review_result.status == ReviewStatus.CHANGES_REQUESTED:
            print("🔧 변경 요청됨")
            
            # Critical 이슈 확인
            critical = [c for c in review_result.comments 
                       if c.severity == ReviewSeverity.CRITICAL]
            
            if critical:
                print(f"🚨 {len(critical)}개의 치명적 이슈 발견")
                # 변경 요청
                self.review_adapter.request_changes(pr_number, critical)
    
    def _perform_cross_check(self, pr_number: int, primary_reviewer: str) -> Dict:
        """크로스 체크 수행"""
        
        # 다른 AI 선택
        secondary_reviewers = []
        if primary_reviewer != 'claude':
            secondary_reviewers.append('claude')
        if primary_reviewer != 'gemini':
            secondary_reviewers.append('gemini')
        
        # 추가 리뷰 수행
        reviews = []
        for reviewer in secondary_reviewers[:1]:  # 1명만
            print(f"  🔄 {reviewer} 크로스 체크 중...")
            review = self.review_adapter.perform_review(pr_number, reviewer)
            reviews.append(review)
        
        # 교차 검증
        if reviews:
            consolidated = self.review_adapter.cross_check_reviews(reviews)
            
            # 불일치 확인
            if consolidated.status != reviews[0].status:
                print("  ⚠️ 리뷰 의견 불일치 - 사람 검토 필요")
        
        return {'cross_checked': True}
    
    def _make_final_decision(self, pr_number: int, review_result) -> str:
        """최종 결정"""
        
        if review_result.status == ReviewStatus.APPROVED:
            # 자동 병합 여부 결정
            if review_result.score and review_result.score >= 80:
                # 높은 점수는 자동 병합 가능
                return "자동 병합 가능"
            else:
                return "승인됨 - 수동 병합 필요"
        
        elif review_result.status == ReviewStatus.CHANGES_REQUESTED:
            # Critical 이슈가 있으면 블록
            critical = [c for c in review_result.comments 
                       if c.severity == ReviewSeverity.CRITICAL]
            
            if critical:
                return "병합 차단 - 치명적 이슈"
            else:
                return "개선 필요 - 병합 가능"
        
        return "검토 필요"


def main():
    """메인 실행"""
    
    import argparse
    
    parser = argparse.ArgumentParser(description='코드 리뷰 워크플로우')
    parser.add_argument('pr_number', type=int, help='PR 번호')
    parser.add_argument('--repo', default='ihw33/ai-orchestra-v02', help='저장소')
    
    args = parser.parse_args()
    
    # 워크플로우 실행
    workflow = CodeReviewWorkflow(args.repo)
    result = workflow.execute_full_review_cycle(args.pr_number)
    
    # 결과 출력
    print("\n" + "=" * 50)
    print("📊 리뷰 워크플로우 결과")
    print("=" * 50)
    print(f"PR: #{result['pr_number']}")
    print(f"성공: {result['success']}")
    print(f"최종 상태: {result.get('final_status', 'N/A')}")
    print("\n단계:")
    for step in result['steps']:
        print(f"  - {step}")


if __name__ == "__main__":
    # 테스트 모드
    if len(sys.argv) == 1:
        print("테스트 모드")
        workflow = CodeReviewWorkflow()
        
        # 테스트용 더미 실행
        print("사용법: python code_review_workflow.py <PR번호>")
    else:
        main()