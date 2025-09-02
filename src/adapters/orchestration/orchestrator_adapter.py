"""
Orchestrator Adapter - 오케스트레이션 어댑터
"""

import uuid
import logging
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, List, Optional, Any
from datetime import datetime
import subprocess
import json

from src.ports.orchestration_port import (
    OrchestrationPort, ExecutionMode, TaskStatus,
    Task, TaskResult, WorkflowDefinition, WorkflowExecution
)
from src.adapters.ai.transparent_reporting_adapter import TransparentReportingAdapter


logger = logging.getLogger(__name__)


class OrchestratorAdapter(OrchestrationPort):
    """오케스트레이터 어댑터 구현"""
    
    def __init__(self, max_workers: int = 5):
        self.workflows: Dict[str, WorkflowDefinition] = {}
        self.executions: Dict[str, WorkflowExecution] = {}
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.ai_adapter = TransparentReportingAdapter()
        self.lock = threading.Lock()
    
    def create_workflow(self, definition: WorkflowDefinition) -> str:
        """워크플로우 생성 및 등록"""
        with self.lock:
            self.workflows[definition.name] = definition
            logger.info(f"워크플로우 생성: {definition.name}")
            return definition.name
    
    def execute_workflow(
        self, 
        workflow_name: str, 
        context: Dict[str, Any] = None
    ) -> WorkflowExecution:
        """워크플로우 실행"""
        
        if workflow_name not in self.workflows:
            raise ValueError(f"워크플로우를 찾을 수 없음: {workflow_name}")
        
        workflow = self.workflows[workflow_name]
        execution_id = str(uuid.uuid4())
        
        # 실행 상태 초기화
        execution = WorkflowExecution(
            workflow_name=workflow_name,
            execution_id=execution_id,
            status=TaskStatus.RUNNING,
            task_results={},
            start_time=datetime.now(),
            context=context or {}
        )
        
        with self.lock:
            self.executions[execution_id] = execution
        
        try:
            # 실행 모드에 따른 처리
            if workflow.mode == ExecutionMode.SEQUENTIAL:
                self._execute_sequential(workflow, execution)
            elif workflow.mode == ExecutionMode.PARALLEL:
                self._execute_parallel(workflow, execution)
            elif workflow.mode == ExecutionMode.DAG:
                self._execute_dag(workflow, execution)
            else:
                self._execute_sequential(workflow, execution)
            
            # 전체 상태 업데이트
            execution.end_time = datetime.now()
            execution.status = self._determine_overall_status(execution)
            
        except Exception as e:
            logger.error(f"워크플로우 실행 실패: {e}")
            execution.status = TaskStatus.FAILED
            execution.end_time = datetime.now()
        
        return execution
    
    def _execute_sequential(self, workflow: WorkflowDefinition, execution: WorkflowExecution):
        """순차 실행"""
        for task in workflow.tasks:
            if execution.status == TaskStatus.FAILED:
                break
            
            result = self.execute_task(task, execution.context)
            execution.task_results[task.id] = result
            
            if result.status == TaskStatus.FAILED:
                execution.status = TaskStatus.FAILED
                break
    
    def _execute_parallel(self, workflow: WorkflowDefinition, execution: WorkflowExecution):
        """병렬 실행"""
        futures = {}
        
        for task in workflow.tasks:
            future = self.executor.submit(self.execute_task, task, execution.context)
            futures[future] = task.id
        
        for future in as_completed(futures):
            task_id = futures[future]
            try:
                result = future.result(timeout=300)
                execution.task_results[task_id] = result
            except Exception as e:
                logger.error(f"태스크 {task_id} 실행 실패: {e}")
                execution.task_results[task_id] = TaskResult(
                    task_id=task_id,
                    status=TaskStatus.FAILED,
                    error=str(e),
                    start_time=datetime.now(),
                    end_time=datetime.now()
                )
    
    def _execute_dag(self, workflow: WorkflowDefinition, execution: WorkflowExecution):
        """DAG 기반 실행"""
        completed_tasks = set()
        pending_tasks = {task.id: task for task in workflow.tasks}
        
        while pending_tasks:
            # 실행 가능한 태스크 찾기
            ready_tasks = []
            for task_id, task in pending_tasks.items():
                if all(dep in completed_tasks for dep in task.dependencies):
                    ready_tasks.append(task)
            
            if not ready_tasks:
                # 데드락 상황
                logger.error("DAG 실행 중 데드락 발생")
                execution.status = TaskStatus.FAILED
                break
            
            # 병렬로 실행
            futures = {}
            for task in ready_tasks:
                future = self.executor.submit(self.execute_task, task, execution.context)
                futures[future] = task
            
            # 결과 수집
            for future in as_completed(futures):
                task = futures[future]
                try:
                    result = future.result(timeout=task.timeout)
                    execution.task_results[task.id] = result
                    completed_tasks.add(task.id)
                    del pending_tasks[task.id]
                except Exception as e:
                    logger.error(f"태스크 {task.id} 실행 실패: {e}")
                    execution.task_results[task.id] = TaskResult(
                        task_id=task.id,
                        status=TaskStatus.FAILED,
                        error=str(e)
                    )
                    del pending_tasks[task.id]
    
    def execute_task(self, task: Task, context: Dict[str, Any] = None) -> TaskResult:
        """단일 태스크 실행"""
        start_time = datetime.now()
        
        try:
            # AI 태스크 실행
            if task.executor in ['gemini', 'claude', 'codex']:
                output = self.ai_adapter.execute_with_reporting(
                    ai_name=task.executor,
                    task=task.command,
                    **task.params
                )
            # 쉘 명령 실행
            elif task.executor == 'shell':
                result = subprocess.run(
                    task.command,
                    shell=True,
                    capture_output=True,
                    text=True,
                    timeout=task.timeout
                )
                output = {
                    'stdout': result.stdout,
                    'stderr': result.stderr,
                    'returncode': result.returncode
                }
            # 커스텀 어댑터 실행
            else:
                # 동적으로 어댑터 로드 및 실행
                output = self._execute_custom_adapter(task)
            
            return TaskResult(
                task_id=task.id,
                status=TaskStatus.SUCCESS,
                output=output,
                start_time=start_time,
                end_time=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"태스크 실행 실패: {e}")
            
            # 재시도 로직
            if task.retry_count < task.max_retries:
                task.retry_count += 1
                logger.info(f"태스크 {task.id} 재시도 {task.retry_count}/{task.max_retries}")
                return self.execute_task(task, context)
            
            return TaskResult(
                task_id=task.id,
                status=TaskStatus.FAILED,
                error=str(e),
                start_time=start_time,
                end_time=datetime.now()
            )
    
    def _execute_custom_adapter(self, task: Task) -> Any:
        """커스텀 어댑터 실행"""
        # 어댑터 동적 로드
        if task.executor == 'pm_processor':
            from src.adapters.pm.pm_processor_adapter import PMProcessorAdapter
            adapter = PMProcessorAdapter()
            method = getattr(adapter, task.command, None)
            if method:
                return method(**task.params) if task.params else method()
        
        raise ValueError(f"알 수 없는 실행자: {task.executor}")
    
    def _determine_overall_status(self, execution: WorkflowExecution) -> TaskStatus:
        """전체 워크플로우 상태 결정"""
        if not execution.task_results:
            return TaskStatus.PENDING
        
        statuses = [r.status for r in execution.task_results.values()]
        
        if all(s == TaskStatus.SUCCESS for s in statuses):
            return TaskStatus.SUCCESS
        elif any(s == TaskStatus.FAILED for s in statuses):
            return TaskStatus.FAILED
        elif any(s == TaskStatus.RUNNING for s in statuses):
            return TaskStatus.RUNNING
        else:
            return TaskStatus.SUCCESS
    
    def get_workflow_status(self, execution_id: str) -> WorkflowExecution:
        """워크플로우 상태 조회"""
        if execution_id not in self.executions:
            raise ValueError(f"실행을 찾을 수 없음: {execution_id}")
        return self.executions[execution_id]
    
    def cancel_workflow(self, execution_id: str) -> bool:
        """워크플로우 취소"""
        if execution_id in self.executions:
            execution = self.executions[execution_id]
            execution.status = TaskStatus.SKIPPED
            execution.end_time = datetime.now()
            return True
        return False
    
    def retry_task(self, execution_id: str, task_id: str) -> TaskResult:
        """태스크 재시도"""
        if execution_id not in self.executions:
            raise ValueError(f"실행을 찾을 수 없음: {execution_id}")
        
        execution = self.executions[execution_id]
        workflow = self.workflows[execution.workflow_name]
        
        # 태스크 찾기
        task = next((t for t in workflow.tasks if t.id == task_id), None)
        if not task:
            raise ValueError(f"태스크를 찾을 수 없음: {task_id}")
        
        # 재시도
        result = self.execute_task(task, execution.context)
        execution.task_results[task_id] = result
        
        return result
    
    def list_workflows(self) -> List[str]:
        """등록된 워크플로우 목록"""
        return list(self.workflows.keys())