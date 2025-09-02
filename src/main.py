"""
AI Orchestra v02 - Main Entry Point
DDD 구조로 리팩토링된 메인 실행 파일
"""

import logging
from typing import Dict, Any

from src.adapters.pm.pm_processor_adapter import PMProcessorAdapter
from src.adapters.trigger.trigger_system_adapter import TriggerSystemAdapter
from src.adapters.orchestration.orchestrator_adapter import OrchestratorAdapter
from src.ports.trigger_port import TriggerType, TriggerCondition, TriggerAction, TriggerContext
from src.ports.orchestration_port import (
    Task, WorkflowDefinition, ExecutionMode
)


# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class AIOrchestra:
    """AI Orchestra 메인 클래스"""
    
    def __init__(self):
        self.pm_processor = PMProcessorAdapter()
        self.trigger_system = TriggerSystemAdapter()
        self.orchestrator = OrchestratorAdapter()
        self._setup_triggers()
        self._setup_workflows()
    
    def _setup_triggers(self):
        """트리거 설정"""
        
        # GitHub 이슈 생성 트리거
        self.trigger_system.register_trigger(
            name="github_issue_created",
            condition=TriggerCondition(
                type=TriggerType.GITHUB_EVENT,
                event_name="opened"
            ),
            action=TriggerAction(
                name="process_new_issue",
                handler="pm_processor_adapter.process_issue"
            )
        )
        
        # AI 키워드 트리거
        self.trigger_system.register_trigger(
            name="ai_task_trigger",
            condition=TriggerCondition(
                type=TriggerType.KEYWORD,
                keywords=["[AI]", "ai-task", "needs-ai"]
            ),
            action=TriggerAction(
                name="execute_ai_workflow",
                handler="orchestrator_adapter.execute_workflow",
                params={"workflow_name": "ai_processing"}
            )
        )
        
        logger.info("트리거 설정 완료")
    
    def _setup_workflows(self):
        """워크플로우 설정"""
        
        # AI 처리 워크플로우
        ai_workflow = WorkflowDefinition(
            name="ai_processing",
            mode=ExecutionMode.PARALLEL,
            tasks=[
                Task(
                    id="gemini_analysis",
                    name="Gemini 분석",
                    executor="gemini",
                    command="아키텍처 분석 및 설계",
                    params={"profile": "architect"}
                ),
                Task(
                    id="claude_implementation",
                    name="Claude 구현",
                    executor="claude",
                    command="코드 구현",
                    params={"profile": "developer"}
                ),
                Task(
                    id="codex_backend",
                    name="Codex 백엔드",
                    executor="codex",
                    command="API 및 백엔드 구현",
                    params={"profile": "backend"}
                )
            ]
        )
        
        # Issue 처리 워크플로우
        issue_workflow = WorkflowDefinition(
            name="issue_processing",
            mode=ExecutionMode.DAG,
            tasks=[
                Task(
                    id="fetch_issue",
                    name="이슈 가져오기",
                    executor="pm_processor",
                    command="get_latest_issues",
                    params={"limit": 1}
                ),
                Task(
                    id="analyze_issue",
                    name="이슈 분석",
                    executor="gemini",
                    command="이슈 분석 및 작업 계획",
                    dependencies=["fetch_issue"]
                ),
                Task(
                    id="execute_tasks",
                    name="작업 실행",
                    executor="claude",
                    command="작업 실행",
                    dependencies=["analyze_issue"]
                ),
                Task(
                    id="report_results",
                    name="결과 보고",
                    executor="pm_processor",
                    command="post_comment",
                    dependencies=["execute_tasks"]
                )
            ]
        )
        
        self.orchestrator.create_workflow(ai_workflow)
        self.orchestrator.create_workflow(issue_workflow)
        
        logger.info("워크플로우 설정 완료")
    
    def process_latest_issues(self):
        """최신 이슈 처리"""
        issues = self.pm_processor.get_latest_issues(limit=5)
        
        for issue in issues:
            if issue.needs_ai and not issue.is_processed:
                logger.info(f"이슈 #{issue.number} 처리 시작")
                result = self.pm_processor.process_issue(issue)
                
                if result.success:
                    logger.info(f"✅ 이슈 #{issue.number} 처리 완료")
                else:
                    logger.error(f"❌ 이슈 #{issue.number} 처리 실패: {result.error}")
    
    def handle_event(self, event_data: Dict[str, Any]):
        """이벤트 처리"""
        context = TriggerContext(
            source=event_data.get('source', 'manual'),
            data=event_data
        )
        
        # 매칭되는 트리거 확인
        matching_triggers = self.trigger_system.check_triggers(context)
        
        for trigger_name in matching_triggers:
            logger.info(f"트리거 실행: {trigger_name}")
            result = self.trigger_system.execute_trigger(trigger_name, context)
            
            if result.success:
                logger.info(f"✅ 트리거 {trigger_name} 성공")
            else:
                logger.error(f"❌ 트리거 {trigger_name} 실패: {result.error}")
    
    def execute_workflow(self, workflow_name: str, context: Dict[str, Any] = None):
        """워크플로우 직접 실행"""
        logger.info(f"워크플로우 실행: {workflow_name}")
        
        execution = self.orchestrator.execute_workflow(workflow_name, context)
        
        logger.info(f"워크플로우 완료: {execution.status.value}")
        logger.info(f"성공률: {execution.success_rate:.1%}")
        
        return execution


def main():
    """메인 실행 함수"""
    orchestra = AIOrchestra()
    
    # 사용 예시
    import sys
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "process-issues":
            # 최신 이슈 처리
            orchestra.process_latest_issues()
        
        elif command == "execute-workflow":
            # 워크플로우 실행
            if len(sys.argv) > 2:
                workflow_name = sys.argv[2]
                orchestra.execute_workflow(workflow_name)
            else:
                print("워크플로우 이름을 지정하세요")
        
        elif command == "handle-event":
            # 이벤트 처리 (GitHub webhook 등)
            import json
            event_data = json.loads(sys.argv[2]) if len(sys.argv) > 2 else {}
            orchestra.handle_event(event_data)
        
        else:
            print(f"알 수 없는 명령: {command}")
            print("사용법: python main.py [process-issues|execute-workflow|handle-event]")
    
    else:
        print("AI Orchestra v02 - DDD 구조")
        print("사용법: python main.py [process-issues|execute-workflow|handle-event]")
        print("\n등록된 워크플로우:")
        for workflow in orchestra.orchestrator.list_workflows():
            print(f"  - {workflow}")


if __name__ == "__main__":
    main()