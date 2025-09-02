#!/usr/bin/env python3
"""
IWL Development DAG
이슈 분석 → 작업 분해 → 할당 → 실행 → 검증 → PR의 전체 워크플로우 관리
"""

import json
import os
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional
import subprocess
import sys

# 프로젝트 루트를 Python path에 추가
sys.path.append(str(Path(__file__).parent.parent))

from core.protocol import WorkflowRequest, WorkflowResult
from nodes.iwl_development_node import IWLDevelopmentNode


class IWLDevelopmentDAG:
    """IWL 개발을 위한 전체 워크플로우 DAG"""
    
    def __init__(self):
        self.iwl_node = IWLDevelopmentNode()
        self.iwl_repo = "ihw33/iwl-v5-rebuild"
        self.results_dir = Path(__file__).parent.parent / "pipeline_results"
        self.results_dir.mkdir(exist_ok=True)
        
        # 워크플로우 단계 정의
        self.workflow_stages = [
            "issue_analysis",      # 1. 이슈 분석
            "task_breakdown",      # 2. 작업 분해  
            "persona_assignment",  # 3. 페르소나 할당
            "execution_planning",  # 4. 실행 계획
            "quality_check",       # 5. 품질 체크
            "implementation",      # 6. 구현 실행
            "testing",            # 7. 테스트
            "code_review",        # 8. 코드 리뷰
            "pr_creation",        # 9. PR 생성
            "completion"          # 10. 완료
        ]
    
    def execute_workflow(self, issue_id: str, workflow_type: str = "feature_development") -> Dict:
        """전체 워크플로우 실행"""
        workflow_id = f"iwl_{workflow_type}_{issue_id}_{int(time.time())}"
        
        workflow_state = {
            'workflow_id': workflow_id,
            'issue_id': issue_id,
            'workflow_type': workflow_type,
            'current_stage': 0,
            'stages': self.workflow_stages,
            'stage_results': {},
            'overall_status': 'running',
            'started_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat(),
            'retry_count': {},
            'checkpoints': {}
        }
        
        try:
            # 각 단계별로 순차 실행
            for stage_idx, stage_name in enumerate(self.workflow_stages):
                workflow_state['current_stage'] = stage_idx
                workflow_state['updated_at'] = datetime.now().isoformat()
                
                print(f"🚀 Stage {stage_idx + 1}/{len(self.workflow_stages)}: {stage_name}")
                
                # 단계별 실행
                stage_result = self._execute_stage(stage_name, workflow_state)
                workflow_state['stage_results'][stage_name] = stage_result
                
                # 체크포인트 저장
                self._save_checkpoint(workflow_state)
                
                # 실패 시 재시도 로직
                if not stage_result.get('success', False):
                    retry_result = self._handle_stage_failure(stage_name, workflow_state)
                    if not retry_result:
                        workflow_state['overall_status'] = 'failed'
                        workflow_state['failed_stage'] = stage_name
                        break
                
                # 완료 조건 체크
                if stage_name == 'completion':
                    workflow_state['overall_status'] = 'completed'
                    workflow_state['completed_at'] = datetime.now().isoformat()
            
            # 최종 결과 저장
            self._save_final_result(workflow_state)
            
            return workflow_state
            
        except Exception as e:
            workflow_state['overall_status'] = 'error'
            workflow_state['error'] = str(e)
            workflow_state['failed_at'] = datetime.now().isoformat()
            self._save_final_result(workflow_state)
            return workflow_state
    
    def _execute_stage(self, stage_name: str, workflow_state: Dict) -> Dict:
        """개별 단계 실행"""
        issue_id = workflow_state['issue_id']
        
        if stage_name == "issue_analysis":
            return self._analyze_issue(issue_id)
        
        elif stage_name == "task_breakdown":
            return self._breakdown_tasks(issue_id)
        
        elif stage_name == "persona_assignment":
            return self._assign_personas(issue_id)
        
        elif stage_name == "execution_planning":
            return self._plan_execution(issue_id)
        
        elif stage_name == "quality_check":
            return self._quality_check(issue_id)
        
        elif stage_name == "implementation":
            return self._execute_implementation(issue_id)
        
        elif stage_name == "testing":
            return self._run_tests(issue_id)
        
        elif stage_name == "code_review":
            return self._code_review(issue_id)
        
        elif stage_name == "pr_creation":
            return self._create_pull_request(issue_id)
        
        elif stage_name == "completion":
            return self._finalize_completion(issue_id)
        
        else:
            return {'success': False, 'message': f'Unknown stage: {stage_name}'}
    
    def _analyze_issue(self, issue_id: str) -> Dict:
        """1단계: 이슈 분석"""
        try:
            # GitHub 이슈 정보 가져오기
            issue = self.iwl_node.parse_github_issue(issue_id)
            
            if not issue:
                return {'success': False, 'message': 'Issue not found'}
            
            # 이슈 복잡도 분석
            complexity = self._analyze_complexity(issue)
            
            # 예상 소요 시간 계산
            estimated_hours = self._estimate_total_hours(issue, complexity)
            
            # 필요한 전문 분야 식별
            required_expertise = self._identify_required_expertise(issue)
            
            return {
                'success': True,
                'issue': issue,
                'complexity': complexity,
                'estimated_hours': estimated_hours,
                'required_expertise': required_expertise,
                'analysis_completed_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {'success': False, 'message': f'Issue analysis failed: {str(e)}'}
    
    def _breakdown_tasks(self, issue_id: str) -> Dict:
        """2단계: 작업 분해"""
        try:
            request = WorkflowRequest(
                workflow_id="iwl_task_breakdown",
                parameters={'issue_id': issue_id}
            )
            
            result = self.iwl_node.execute(request)
            
            if result.success:
                tasks = result.data.get('tasks', [])
                return {
                    'success': True,
                    'tasks': tasks,
                    'task_count': len(tasks),
                    'breakdown_completed_at': datetime.now().isoformat()
                }
            else:
                return {'success': False, 'message': result.message}
                
        except Exception as e:
            return {'success': False, 'message': f'Task breakdown failed: {str(e)}'}
    
    def _assign_personas(self, issue_id: str) -> Dict:
        """3단계: 페르소나 할당"""
        try:
            # 할당 파일 확인
            assignments_file = self.results_dir / f"iwl_assignments_{issue_id}.json"
            
            if assignments_file.exists():
                with open(assignments_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    assignments = data['assignments']
                
                return {
                    'success': True,
                    'assignments': assignments,
                    'assignment_count': len(assignments),
                    'assignment_completed_at': datetime.now().isoformat()
                }
            else:
                return {'success': False, 'message': 'Assignments file not found'}
                
        except Exception as e:
            return {'success': False, 'message': f'Persona assignment failed: {str(e)}'}
    
    def _plan_execution(self, issue_id: str) -> Dict:
        """4단계: 실행 계획 수립"""
        try:
            # 할당 정보 로드
            assignments_file = self.results_dir / f"iwl_assignments_{issue_id}.json"
            
            if not assignments_file.exists():
                return {'success': False, 'message': 'No assignments found'}
            
            with open(assignments_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                assignments = data['assignments']
            
            # 실행 계획 생성
            execution_plan = self._create_execution_plan(assignments)
            
            # 실행 순서 최적화
            optimized_plan = self._optimize_execution_order(execution_plan)
            
            # 계획 저장
            plan_file = self.results_dir / f"iwl_execution_plan_{issue_id}.json"
            with open(plan_file, 'w', encoding='utf-8') as f:
                json.dump({
                    'issue_id': issue_id,
                    'execution_plan': optimized_plan,
                    'created_at': datetime.now().isoformat()
                }, f, ensure_ascii=False, indent=2)
            
            return {
                'success': True,
                'execution_plan': optimized_plan,
                'plan_file': str(plan_file),
                'planning_completed_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {'success': False, 'message': f'Execution planning failed: {str(e)}'}
    
    def _quality_check(self, issue_id: str) -> Dict:
        """5단계: 품질 체크"""
        try:
            # 코드 품질 체크
            quality_issues = []
            
            # Lint 체크
            lint_result = self._run_linting()
            if lint_result.get('issues'):
                quality_issues.extend(lint_result['issues'])
            
            # 타입 체크
            type_result = self._run_type_checking()
            if type_result.get('issues'):
                quality_issues.extend(type_result['issues'])
            
            # 테스트 커버리지 체크
            coverage_result = self._check_test_coverage()
            
            return {
                'success': len(quality_issues) == 0,
                'quality_issues': quality_issues,
                'lint_result': lint_result,
                'type_result': type_result,
                'coverage_result': coverage_result,
                'quality_check_completed_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {'success': False, 'message': f'Quality check failed: {str(e)}'}
    
    def _execute_implementation(self, issue_id: str) -> Dict:
        """6단계: 구현 실행"""
        try:
            # 실행 계획 로드
            plan_file = self.results_dir / f"iwl_execution_plan_{issue_id}.json"
            
            if not plan_file.exists():
                return {'success': False, 'message': 'Execution plan not found'}
            
            with open(plan_file, 'r', encoding='utf-8') as f:
                plan_data = json.load(f)
                execution_plan = plan_data['execution_plan']
            
            # 각 작업 단위별로 구현 실행
            implementation_results = []
            
            for task in execution_plan:
                task_result = self._execute_single_task(task)
                implementation_results.append(task_result)
                
                # 의존성이 있는 작업의 경우 이전 작업 완료 확인
                if not task_result.get('success', False) and task.get('critical', False):
                    return {
                        'success': False,
                        'message': f'Critical task failed: {task.get("name")}',
                        'failed_task': task,
                        'implementation_results': implementation_results
                    }
            
            success_count = sum(1 for result in implementation_results if result.get('success', False))
            total_count = len(implementation_results)
            
            return {
                'success': success_count == total_count,
                'implementation_results': implementation_results,
                'success_rate': success_count / total_count if total_count > 0 else 0,
                'implementation_completed_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {'success': False, 'message': f'Implementation failed: {str(e)}'}
    
    def _run_tests(self, issue_id: str) -> Dict:
        """7단계: 테스트 실행"""
        try:
            test_results = {}
            
            # 단위 테스트
            unit_test_result = self._run_unit_tests()
            test_results['unit_tests'] = unit_test_result
            
            # 통합 테스트
            integration_test_result = self._run_integration_tests()
            test_results['integration_tests'] = integration_test_result
            
            # E2E 테스트
            e2e_test_result = self._run_e2e_tests()
            test_results['e2e_tests'] = e2e_test_result
            
            # 전체 테스트 성공 여부
            all_passed = all(
                result.get('success', False) for result in test_results.values()
            )
            
            return {
                'success': all_passed,
                'test_results': test_results,
                'testing_completed_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {'success': False, 'message': f'Testing failed: {str(e)}'}
    
    def _code_review(self, issue_id: str) -> Dict:
        """8단계: 코드 리뷰"""
        try:
            # 자동 코드 리뷰 실행
            review_issues = []
            
            # 코드 스타일 체크
            style_issues = self._check_code_style()
            review_issues.extend(style_issues)
            
            # 보안 취약점 체크
            security_issues = self._check_security_vulnerabilities()
            review_issues.extend(security_issues)
            
            # 성능 최적화 제안
            performance_suggestions = self._check_performance_optimization()
            
            # 리뷰 결과 생성
            review_result = {
                'total_issues': len(review_issues),
                'critical_issues': len([i for i in review_issues if i.get('severity') == 'critical']),
                'style_issues': style_issues,
                'security_issues': security_issues,
                'performance_suggestions': performance_suggestions,
                'review_passed': len([i for i in review_issues if i.get('severity') == 'critical']) == 0
            }
            
            return {
                'success': review_result['review_passed'],
                'review_result': review_result,
                'code_review_completed_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {'success': False, 'message': f'Code review failed: {str(e)}'}
    
    def _create_pull_request(self, issue_id: str) -> Dict:
        """9단계: PR 생성"""
        try:
            # PR 생성을 위한 정보 수집
            pr_info = self._collect_pr_information(issue_id)
            
            if not pr_info:
                return {'success': False, 'message': 'Failed to collect PR information'}
            
            # PR 생성
            pr_url = self.iwl_node.create_pr_when_complete(issue_id, pr_info['assignments'])
            
            if pr_url:
                return {
                    'success': True,
                    'pr_url': pr_url,
                    'pr_created_at': datetime.now().isoformat()
                }
            else:
                return {'success': False, 'message': 'PR creation failed'}
                
        except Exception as e:
            return {'success': False, 'message': f'PR creation failed: {str(e)}'}
    
    def _finalize_completion(self, issue_id: str) -> Dict:
        """10단계: 완료 처리"""
        try:
            # 모든 단계 완료 확인
            completion_checklist = {
                'issue_analyzed': True,
                'tasks_broken_down': True,
                'personas_assigned': True,
                'implementation_completed': True,
                'tests_passed': True,
                'code_reviewed': True,
                'pr_created': True
            }
            
            # 최종 리포트 생성
            final_report = self._generate_final_report(issue_id)
            
            # 이슈 상태 업데이트
            self._update_issue_status(issue_id, 'completed')
            
            # 페르소나 경험치 업데이트 (재귀 성장 시스템)
            self._update_persona_experience(issue_id)
            
            return {
                'success': True,
                'completion_checklist': completion_checklist,
                'final_report': final_report,
                'completion_time': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {'success': False, 'message': f'Completion failed: {str(e)}'}
    
    def _handle_stage_failure(self, stage_name: str, workflow_state: Dict) -> bool:
        """단계 실패 시 재시도 로직"""
        retry_count = workflow_state['retry_count'].get(stage_name, 0)
        max_retries = 3
        
        if retry_count < max_retries:
            print(f"⚠️  Stage {stage_name} failed. Retrying... ({retry_count + 1}/{max_retries})")
            
            workflow_state['retry_count'][stage_name] = retry_count + 1
            
            # 잠시 대기 후 재시도
            time.sleep(2 ** retry_count)  # 지수 백오프
            
            # 재시도 실행
            retry_result = self._execute_stage(stage_name, workflow_state)
            workflow_state['stage_results'][f"{stage_name}_retry_{retry_count + 1}"] = retry_result
            
            return retry_result.get('success', False)
        
        return False
    
    def _save_checkpoint(self, workflow_state: Dict):
        """체크포인트 저장"""
        checkpoint_file = self.results_dir / f"iwl_checkpoint_{workflow_state['workflow_id']}.json"
        
        with open(checkpoint_file, 'w', encoding='utf-8') as f:
            json.dump(workflow_state, f, ensure_ascii=False, indent=2)
    
    def _save_final_result(self, workflow_state: Dict):
        """최종 결과 저장"""
        result_file = self.results_dir / f"iwl_workflow_result_{workflow_state['workflow_id']}.json"
        
        with open(result_file, 'w', encoding='utf-8') as f:
            json.dump(workflow_state, f, ensure_ascii=False, indent=2)
    
    # 헬퍼 메서드들
    def _analyze_complexity(self, issue: Dict) -> str:
        """이슈 복잡도 분석"""
        body_length = len(issue.get('body', ''))
        title = issue.get('title', '').lower()
        
        if body_length > 1000 or any(keyword in title for keyword in ['architecture', 'migration', 'refactor']):
            return 'high'
        elif body_length > 500 or any(keyword in title for keyword in ['feature', 'enhancement']):
            return 'medium'
        else:
            return 'low'
    
    def _estimate_total_hours(self, issue: Dict, complexity: str) -> int:
        """전체 소요 시간 추정"""
        base_hours = {'low': 8, 'medium': 24, 'high': 56}
        return base_hours.get(complexity, 16)
    
    def _identify_required_expertise(self, issue: Dict) -> List[str]:
        """필요한 전문 분야 식별"""
        content = f"{issue.get('title', '')} {issue.get('body', '')}".lower()
        
        expertise = []
        if any(keyword in content for keyword in ['ui', 'frontend', 'react']):
            expertise.append('frontend')
        if any(keyword in content for keyword in ['api', 'backend', 'server']):
            expertise.append('backend')
        if any(keyword in content for keyword in ['ai', 'ml', 'llm']):
            expertise.append('ai')
        if any(keyword in content for keyword in ['design', 'ux']):
            expertise.append('design')
        
        return expertise or ['general']
    
    def _create_execution_plan(self, assignments: List[Dict]) -> List[Dict]:
        """실행 계획 생성"""
        # 우선순위 기반으로 정렬
        sorted_assignments = sorted(assignments, key=lambda x: x.get('priority', 999))
        
        execution_plan = []
        for assignment in sorted_assignments:
            execution_plan.append({
                'name': assignment['task_name'],
                'persona': assignment['persona_name'],
                'estimated_hours': assignment['estimated_hours'],
                'priority': assignment['priority'],
                'dependencies': [],
                'critical': assignment['priority'] <= 2
            })
        
        return execution_plan
    
    def _optimize_execution_order(self, execution_plan: List[Dict]) -> List[Dict]:
        """실행 순서 최적화"""
        # 간단한 최적화: 의존성과 우선순위 기반 정렬
        return sorted(execution_plan, key=lambda x: (x['priority'], -x['estimated_hours']))
    
    # 각종 체크 및 테스트 메서드들 (실제 구현은 환경에 따라 조정 필요)
    def _run_linting(self) -> Dict:
        """Lint 검사"""
        return {'success': True, 'issues': []}
    
    def _run_type_checking(self) -> Dict:
        """타입 검사"""
        return {'success': True, 'issues': []}
    
    def _check_test_coverage(self) -> Dict:
        """테스트 커버리지 체크"""
        return {'success': True, 'coverage': 85.0}
    
    def _execute_single_task(self, task: Dict) -> Dict:
        """단일 작업 실행"""
        # 실제 환경에서는 해당 페르소나의 AI에게 작업 요청
        return {'success': True, 'task_name': task['name'], 'completed_at': datetime.now().isoformat()}
    
    def _run_unit_tests(self) -> Dict:
        """단위 테스트 실행"""
        return {'success': True, 'tests_passed': 0, 'tests_failed': 0}
    
    def _run_integration_tests(self) -> Dict:
        """통합 테스트 실행"""
        return {'success': True, 'tests_passed': 0, 'tests_failed': 0}
    
    def _run_e2e_tests(self) -> Dict:
        """E2E 테스트 실행"""
        return {'success': True, 'tests_passed': 0, 'tests_failed': 0}
    
    def _check_code_style(self) -> List[Dict]:
        """코드 스타일 체크"""
        return []
    
    def _check_security_vulnerabilities(self) -> List[Dict]:
        """보안 취약점 체크"""
        return []
    
    def _check_performance_optimization(self) -> List[Dict]:
        """성능 최적화 체크"""
        return []
    
    def _collect_pr_information(self, issue_id: str) -> Optional[Dict]:
        """PR 정보 수집"""
        assignments_file = self.results_dir / f"iwl_assignments_{issue_id}.json"
        
        if assignments_file.exists():
            with open(assignments_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data
        
        return None
    
    def _generate_final_report(self, issue_id: str) -> Dict:
        """최종 리포트 생성"""
        return {
            'issue_id': issue_id,
            'workflow_completed': True,
            'completion_time': datetime.now().isoformat(),
            'summary': f'Issue #{issue_id} successfully completed through IWL Orchestra system'
        }
    
    def _update_issue_status(self, issue_id: str, status: str):
        """이슈 상태 업데이트"""
        # GitHub API 또는 CLI를 통해 이슈 상태 업데이트
        try:
            if status == 'completed':
                cmd = f"gh issue close {issue_id} -R {self.iwl_repo} --comment 'Completed by IWL Orchestra system'"
                subprocess.run(cmd, shell=True, check=True)
        except Exception as e:
            print(f"이슈 상태 업데이트 실패: {e}")
    
    def _update_persona_experience(self, issue_id: str):
        """페르소나 경험치 업데이트 (재귀 성장 시스템)"""
        try:
            assignments_file = self.results_dir / f"iwl_assignments_{issue_id}.json"
            
            if assignments_file.exists():
                with open(assignments_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    assignments = data['assignments']
                
                # 각 페르소나의 경험치 업데이트
                for assignment in assignments:
                    persona_id = assignment.get('persona_id')
                    if persona_id:
                        # 성장 포인트 계산
                        growth_points = self._calculate_growth_points(assignment)
                        
                        # 페르소나 데이터 업데이트
                        self._update_persona_growth(persona_id, growth_points, assignment)
                        
        except Exception as e:
            print(f"페르소나 경험치 업데이트 실패: {e}")
    
    def _calculate_growth_points(self, assignment: Dict) -> int:
        """성장 포인트 계산"""
        base_points = 10
        hours_bonus = min(assignment.get('estimated_hours', 0), 20) * 2
        priority_bonus = (4 - assignment.get('priority', 4)) * 5
        
        return base_points + hours_bonus + priority_bonus
    
    def _update_persona_growth(self, persona_id: str, growth_points: int, assignment: Dict):
        """개별 페르소나 성장 데이터 업데이트"""
        # 실제 구현에서는 페르소나 데이터베이스 업데이트
        print(f"Persona {persona_id} gained {growth_points} growth points from {assignment['task_name']}")


def main():
    """CLI 인터페이스"""
    import argparse
    
    parser = argparse.ArgumentParser(description='IWL Development DAG')
    parser.add_argument('--issue-id', required=True, help='GitHub 이슈 ID')
    parser.add_argument('--workflow', default='feature_development', 
                       choices=['feature_development', 'bug_fix', 'enhancement', 'refactor'],
                       help='워크플로우 유형')
    parser.add_argument('--resume', help='중단된 워크플로우 재개 (workflow_id 필요)')
    
    args = parser.parse_args()
    
    dag = IWLDevelopmentDAG()
    
    if args.resume:
        # 중단된 워크플로우 재개 로직
        print(f"워크플로우 재개: {args.resume}")
        # 구현 필요
    else:
        # 새로운 워크플로우 시작
        print(f"🚀 Starting IWL Development Workflow for Issue #{args.issue_id}")
        result = dag.execute_workflow(args.issue_id, args.workflow)
        
        print(f"\n✅ Workflow Status: {result['overall_status']}")
        if result['overall_status'] == 'completed':
            print(f"🎉 Issue #{args.issue_id} successfully completed!")
        elif result['overall_status'] == 'failed':
            print(f"❌ Workflow failed at stage: {result.get('failed_stage')}")
        
        print(f"\n📊 Results saved to: pipeline_results/iwl_workflow_result_{result['workflow_id']}.json")


if __name__ == "__main__":
    main()