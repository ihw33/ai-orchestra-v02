#!/usr/bin/env python3
"""
IWL Executor
IWL Orchestra 시스템의 통합 실행기
30명 페르소나 팀을 조율하여 IWL 개발 작업을 실행
"""

import asyncio
import json
import logging
import os
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# 프로젝트 루트를 Python path에 추가
sys.path.append(str(Path(__file__).parent.parent))

from nodes.iwl_development_node import IWLDevelopmentNode
from dags.iwl_development_dag import IWLDevelopmentDAG
from personas.persona_loader import PersonaLoader


class IWLExecutor:
    """IWL Orchestra 시스템 통합 실행기"""
    
    def __init__(self):
        self.iwl_node = IWLDevelopmentNode()
        self.iwl_dag = IWLDevelopmentDAG()
        self.persona_loader = PersonaLoader()
        
        # 설정
        self.iwl_repo = "ihw33/iwl-v5-rebuild"
        self.orchestra_repo = "ihw33/ai-orchestra-v02"
        self.results_dir = Path(__file__).parent.parent / "pipeline_results"
        self.results_dir.mkdir(exist_ok=True)
        
        # 로깅 설정
        self.setup_logging()
        
        # 성능 메트릭
        self.metrics = {
            'tasks_completed': 0,
            'personas_utilized': 0,
            'average_completion_time': 0,
            'success_rate': 0,
            'total_execution_time': 0
        }
        
    def setup_logging(self):
        """로깅 설정"""
        log_file = Path(__file__).parent.parent / "logs" / "iwl_executor.log"
        log_file.parent.mkdir(exist_ok=True)
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    async def execute_issue(self, issue_id: str, workflow_type: str = "feature_development") -> Dict:
        """이슈 실행 (비동기)"""
        start_time = time.time()
        
        self.logger.info(f"🚀 Starting IWL issue execution: #{issue_id}")
        
        try:
            # 1. 페르소나 가용성 체크
            available_personas = await self.check_persona_availability()
            self.logger.info(f"📊 Available personas: {len(available_personas)}")
            
            # 2. 이슈 우선순위 분석
            priority = await self.analyze_issue_priority(issue_id)
            
            # 3. 리소스 할당
            allocated_resources = await self.allocate_resources(issue_id, priority)
            
            # 4. 워크플로우 실행
            workflow_result = self.iwl_dag.execute_workflow(issue_id, workflow_type)
            
            # 5. 실시간 모니터링
            monitoring_task = asyncio.create_task(
                self.monitor_execution(workflow_result['workflow_id'])
            )
            
            # 6. 결과 처리
            execution_result = await self.process_workflow_result(workflow_result)
            
            # 7. 모니터링 종료
            monitoring_task.cancel()
            
            # 8. 메트릭 업데이트
            execution_time = time.time() - start_time
            await self.update_metrics(execution_result, execution_time)
            
            # 9. 페르소나 성장 처리
            await self.process_persona_growth(issue_id, execution_result)
            
            self.logger.info(f"✅ Issue #{issue_id} execution completed in {execution_time:.2f}s")
            
            return {
                'success': True,
                'issue_id': issue_id,
                'workflow_result': workflow_result,
                'execution_result': execution_result,
                'execution_time': execution_time,
                'metrics': self.metrics
            }
            
        except Exception as e:
            self.logger.error(f"❌ Issue #{issue_id} execution failed: {str(e)}")
            return {
                'success': False,
                'issue_id': issue_id,
                'error': str(e),
                'execution_time': time.time() - start_time
            }
    
    async def check_persona_availability(self) -> List[Dict]:
        """페르소나 가용성 체크 (비동기)"""
        try:
            # 모든 페르소나 로드
            all_personas = []
            iwl_team_dir = Path(__file__).parent.parent / "personas" / "iwl_team"
            
            for dept_dir in iwl_team_dir.iterdir():
                if dept_dir.is_dir():
                    for persona_file in dept_dir.glob("*.json"):
                        with open(persona_file, 'r', encoding='utf-8') as f:
                            persona = json.load(f)
                            all_personas.append(persona)
            
            # 가용성 체크 및 필터링
            available_personas = [
                p for p in all_personas 
                if p.get('availability', True) and p.get('current_workload', 0) < 80
            ]
            
            return available_personas
            
        except Exception as e:
            self.logger.error(f"페르소나 가용성 체크 실패: {e}")
            return []
    
    async def analyze_issue_priority(self, issue_id: str) -> str:
        """이슈 우선순위 분석"""
        try:
            # GitHub에서 이슈 정보 가져오기
            issue = self.iwl_node.parse_github_issue(issue_id)
            
            if not issue:
                return "medium"
            
            # 라벨 기반 우선순위 분석
            labels = [label.lower() for label in issue.get('labels', [])]
            
            if any(label in labels for label in ['critical', 'urgent', 'hotfix']):
                return "high"
            elif any(label in labels for label in ['enhancement', 'feature']):
                return "medium"
            else:
                return "low"
                
        except Exception as e:
            self.logger.error(f"이슈 우선순위 분석 실패: {e}")
            return "medium"
    
    async def allocate_resources(self, issue_id: str, priority: str) -> Dict:
        """리소스 할당"""
        try:
            # 우선순위에 따른 리소스 할당 전략
            allocation_strategy = {
                "high": {"max_personas": 8, "parallel_tasks": 4},
                "medium": {"max_personas": 5, "parallel_tasks": 3},
                "low": {"max_personas": 3, "parallel_tasks": 2}
            }
            
            strategy = allocation_strategy.get(priority, allocation_strategy["medium"])
            
            # 가용 페르소나 가져오기
            available_personas = await self.check_persona_availability()
            
            # 최적 페르소나 선정
            selected_personas = self.select_optimal_personas(
                available_personas, 
                strategy["max_personas"]
            )
            
            return {
                'priority': priority,
                'strategy': strategy,
                'selected_personas': selected_personas,
                'allocation_time': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"리소스 할당 실패: {e}")
            return {}
    
    def select_optimal_personas(self, available_personas: List[Dict], max_count: int) -> List[Dict]:
        """최적 페르소나 선정"""
        # 스킬 레벨과 가용성을 기준으로 스코어링
        def calculate_score(persona):
            skills = persona.get('skills', {})
            skill_avg = sum(skills.values()) / len(skills) if skills else 0
            workload_penalty = persona.get('current_workload', 0) / 100
            growth_bonus = min(persona.get('growth_points', 0) / 1000, 2)
            
            return skill_avg + growth_bonus - workload_penalty
        
        # 스코어 기준으로 정렬하여 상위 선택
        sorted_personas = sorted(available_personas, key=calculate_score, reverse=True)
        return sorted_personas[:max_count]
    
    async def monitor_execution(self, workflow_id: str):
        """실행 모니터링 (비동기)"""
        try:
            while True:
                await asyncio.sleep(10)  # 10초마다 체크
                
                # 체크포인트 파일 확인
                checkpoint_file = self.results_dir / f"iwl_checkpoint_{workflow_id}.json"
                
                if checkpoint_file.exists():
                    with open(checkpoint_file, 'r', encoding='utf-8') as f:
                        state = json.load(f)
                    
                    current_stage = state.get('current_stage', 0)
                    total_stages = len(state.get('stages', []))
                    progress = (current_stage / total_stages * 100) if total_stages > 0 else 0
                    
                    self.logger.info(f"📈 Workflow {workflow_id} progress: {progress:.1f}% (Stage {current_stage + 1}/{total_stages})")
                    
                    # 완료 또는 실패 시 모니터링 종료
                    if state.get('overall_status') in ['completed', 'failed', 'error']:
                        break
                        
        except asyncio.CancelledError:
            self.logger.info("모니터링이 종료되었습니다")
        except Exception as e:
            self.logger.error(f"모니터링 오류: {e}")
    
    async def process_workflow_result(self, workflow_result: Dict) -> Dict:
        """워크플로우 결과 처리"""
        try:
            workflow_id = workflow_result['workflow_id']
            status = workflow_result['overall_status']
            
            # 결과 파일 확인
            result_file = self.results_dir / f"iwl_workflow_result_{workflow_id}.json"
            
            if result_file.exists():
                with open(result_file, 'r', encoding='utf-8') as f:
                    detailed_result = json.load(f)
            else:
                detailed_result = workflow_result
            
            # 성공률 계산
            stage_results = detailed_result.get('stage_results', {})
            total_stages = len(stage_results)
            successful_stages = sum(1 for result in stage_results.values() if result.get('success', False))
            success_rate = successful_stages / total_stages if total_stages > 0 else 0
            
            # 처리된 결과 반환
            return {
                'workflow_id': workflow_id,
                'status': status,
                'success_rate': success_rate,
                'total_stages': total_stages,
                'successful_stages': successful_stages,
                'detailed_result': detailed_result,
                'processed_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"워크플로우 결과 처리 실패: {e}")
            return {
                'status': 'error',
                'error': str(e),
                'processed_at': datetime.now().isoformat()
            }
    
    async def update_metrics(self, execution_result: Dict, execution_time: float):
        """메트릭 업데이트"""
        try:
            # 메트릭 업데이트
            if execution_result.get('status') == 'completed':
                self.metrics['tasks_completed'] += 1
            
            # 평균 실행 시간 업데이트
            total_executions = self.metrics['tasks_completed']
            if total_executions > 0:
                current_avg = self.metrics['average_completion_time']
                self.metrics['average_completion_time'] = (
                    (current_avg * (total_executions - 1) + execution_time) / total_executions
                )
            
            # 성공률 업데이트
            self.metrics['success_rate'] = execution_result.get('success_rate', 0)
            self.metrics['total_execution_time'] += execution_time
            
            # 메트릭 저장
            metrics_file = self.results_dir / "iwl_executor_metrics.json"
            with open(metrics_file, 'w', encoding='utf-8') as f:
                json.dump({
                    'metrics': self.metrics,
                    'updated_at': datetime.now().isoformat()
                }, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            self.logger.error(f"메트릭 업데이트 실패: {e}")
    
    async def process_persona_growth(self, issue_id: str, execution_result: Dict):
        """페르소나 성장 처리 (재귀 성장 시스템)"""
        try:
            # 할당 파일에서 페르소나 정보 가져오기
            assignments_file = self.results_dir / f"iwl_assignments_{issue_id}.json"
            
            if not assignments_file.exists():
                return
            
            with open(assignments_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                assignments = data['assignments']
            
            # 각 페르소나의 성장 처리
            for assignment in assignments:
                await self.update_single_persona_growth(assignment, execution_result)
                
        except Exception as e:
            self.logger.error(f"페르소나 성장 처리 실패: {e}")
    
    async def update_single_persona_growth(self, assignment: Dict, execution_result: Dict):
        """개별 페르소나 성장 업데이트"""
        try:
            persona_id = assignment.get('persona_id')
            if not persona_id:
                return
            
            # 페르소나 파일 찾기
            iwl_team_dir = Path(__file__).parent.parent / "personas" / "iwl_team"
            persona_file = None
            
            for dept_dir in iwl_team_dir.iterdir():
                if dept_dir.is_dir():
                    for file in dept_dir.glob("*.json"):
                        with open(file, 'r', encoding='utf-8') as f:
                            persona = json.load(f)
                            if persona.get('id') == persona_id:
                                persona_file = file
                                break
                        if persona_file:
                            break
            
            if not persona_file:
                self.logger.warning(f"페르소나 파일을 찾을 수 없습니다: {persona_id}")
                return
            
            # 페르소나 데이터 로드
            with open(persona_file, 'r', encoding='utf-8') as f:
                persona_data = json.load(f)
            
            # 성장 포인트 계산
            base_points = 10
            task_complexity = assignment.get('estimated_hours', 8)
            success_bonus = 20 if execution_result.get('success_rate', 0) > 0.8 else 10
            
            growth_points = base_points + min(task_complexity, 20) + success_bonus
            
            # 경험치 및 스킬 업데이트
            persona_data['growth_points'] = persona_data.get('growth_points', 0) + growth_points
            
            # 새로운 경험 추가
            new_experience = {
                "project": f"IWL Issue #{assignment.get('issue_id')}",
                "role": assignment.get('persona_role'),
                "contribution": assignment.get('task_name'),
                "rating": min(5.0, 3.0 + execution_result.get('success_rate', 0) * 2),
                "date": datetime.now().isoformat()
            }
            
            if 'experience' not in persona_data:
                persona_data['experience'] = []
            persona_data['experience'].append(new_experience)
            
            # 스킬 레벨 업데이트 (성장 시스템)
            await self.update_persona_skills(persona_data, assignment)
            
            # 업데이트된 데이터 저장
            persona_data['updated_at'] = datetime.now().isoformat()
            
            with open(persona_file, 'w', encoding='utf-8') as f:
                json.dump(persona_data, f, ensure_ascii=False, indent=2)
            
            self.logger.info(f"📈 Persona {persona_data.get('name')} gained {growth_points} growth points")
            
        except Exception as e:
            self.logger.error(f"개별 페르소나 성장 업데이트 실패: {e}")
    
    async def update_persona_skills(self, persona_data: Dict, assignment: Dict):
        """페르소나 스킬 업데이트"""
        try:
            # 작업과 관련된 스킬 식별
            task_name = assignment.get('task_name', '').lower()
            skills = persona_data.get('skills', {})
            
            # 스킬 매핑
            skill_mappings = {
                'react': ['react', 'frontend', 'component'],
                'nextjs': ['next', 'nextjs', 'frontend'],
                'typescript': ['typescript', 'ts', 'type'],
                'api_design': ['api', 'endpoint', 'backend'],
                'database_design': ['database', 'db', 'schema'],
                'ai_integration': ['ai', 'ml', 'llm', 'machine learning'],
                'testing': ['test', 'qa', 'quality'],
                'design': ['ui', 'ux', 'design']
            }
            
            # 관련 스킬 찾기 및 업데이트
            for skill, keywords in skill_mappings.items():
                if any(keyword in task_name for keyword in keywords):
                    current_level = skills.get(skill, 0)
                    if current_level < 10:  # 최대 레벨 10
                        growth_rate = 0.1 + (0.05 * (10 - current_level) / 10)  # 레벨이 낮을수록 빠른 성장
                        skills[skill] = min(10, current_level + growth_rate)
            
            persona_data['skills'] = skills
            
        except Exception as e:
            self.logger.error(f"페르소나 스킬 업데이트 실패: {e}")
    
    def execute_issue_sync(self, issue_id: str, workflow_type: str = "feature_development") -> Dict:
        """동기 버전의 이슈 실행"""
        return asyncio.run(self.execute_issue(issue_id, workflow_type))
    
    def get_system_status(self) -> Dict:
        """시스템 상태 반환"""
        try:
            # 페르소나 통계
            persona_stats = asyncio.run(self._get_persona_statistics())
            
            # 최근 실행 결과
            recent_results = self._get_recent_execution_results()
            
            return {
                'system_status': 'active',
                'metrics': self.metrics,
                'persona_statistics': persona_stats,
                'recent_results': recent_results,
                'updated_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"시스템 상태 조회 실패: {e}")
            return {
                'system_status': 'error',
                'error': str(e),
                'updated_at': datetime.now().isoformat()
            }
    
    async def _get_persona_statistics(self) -> Dict:
        """페르소나 통계 조회"""
        try:
            available_personas = await self.check_persona_availability()
            
            # 부서별 통계
            dept_stats = {}
            total_growth_points = 0
            
            for persona in available_personas:
                dept = persona.get('department', 'unknown')
                if dept not in dept_stats:
                    dept_stats[dept] = {'count': 0, 'avg_level': 0, 'avg_workload': 0}
                
                dept_stats[dept]['count'] += 1
                dept_stats[dept]['avg_level'] += persona.get('level', 0)
                dept_stats[dept]['avg_workload'] += persona.get('current_workload', 0)
                total_growth_points += persona.get('growth_points', 0)
            
            # 평균 계산
            for dept, stats in dept_stats.items():
                if stats['count'] > 0:
                    stats['avg_level'] /= stats['count']
                    stats['avg_workload'] /= stats['count']
            
            return {
                'total_personas': len(available_personas),
                'department_statistics': dept_stats,
                'total_growth_points': total_growth_points,
                'average_growth_points': total_growth_points / len(available_personas) if available_personas else 0
            }
            
        except Exception as e:
            self.logger.error(f"페르소나 통계 조회 실패: {e}")
            return {}
    
    def _get_recent_execution_results(self, limit: int = 5) -> List[Dict]:
        """최근 실행 결과 조회"""
        try:
            result_files = list(self.results_dir.glob("iwl_workflow_result_*.json"))
            result_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
            
            recent_results = []
            for file in result_files[:limit]:
                with open(file, 'r', encoding='utf-8') as f:
                    result = json.load(f)
                    recent_results.append({
                        'workflow_id': result.get('workflow_id'),
                        'issue_id': result.get('issue_id'),
                        'status': result.get('overall_status'),
                        'completed_at': result.get('completed_at'),
                        'duration': result.get('updated_at')  # 실제로는 duration 계산 필요
                    })
            
            return recent_results
            
        except Exception as e:
            self.logger.error(f"최근 실행 결과 조회 실패: {e}")
            return []


def main():
    """CLI 인터페이스"""
    import argparse
    
    parser = argparse.ArgumentParser(description='IWL Executor - IWL Orchestra System')
    parser.add_argument('--issue-id', help='실행할 GitHub 이슈 ID')
    parser.add_argument('--workflow', default='feature_development',
                       choices=['feature_development', 'bug_fix', 'enhancement', 'refactor'],
                       help='워크플로우 유형')
    parser.add_argument('--status', action='store_true', help='시스템 상태 조회')
    parser.add_argument('--metrics', action='store_true', help='메트릭 조회')
    
    args = parser.parse_args()
    
    executor = IWLExecutor()
    
    if args.status:
        # 시스템 상태 조회
        status = executor.get_system_status()
        print(json.dumps(status, ensure_ascii=False, indent=2))
        
    elif args.metrics:
        # 메트릭만 조회
        print(json.dumps(executor.metrics, ensure_ascii=False, indent=2))
        
    elif args.issue_id:
        # 이슈 실행
        print(f"🚀 Executing IWL Issue #{args.issue_id} with {args.workflow} workflow")
        
        result = executor.execute_issue_sync(args.issue_id, args.workflow)
        
        if result['success']:
            print(f"✅ Issue #{args.issue_id} executed successfully!")
            print(f"⏱️  Execution time: {result['execution_time']:.2f}s")
            print(f"📊 Success rate: {result['execution_result']['success_rate']:.1%}")
        else:
            print(f"❌ Issue #{args.issue_id} execution failed: {result['error']}")
        
        print(f"\n📄 Detailed results saved to pipeline_results/")
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()