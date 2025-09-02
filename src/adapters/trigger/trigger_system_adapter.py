"""
Trigger System Adapter - 트리거 시스템 어댑터
"""

import re
import json
import os
from typing import Dict, List, Optional, Any
from datetime import datetime
import logging
import threading
from collections import defaultdict

from src.ports.trigger_port import (
    TriggerPort, TriggerType, TriggerCondition,
    TriggerContext, TriggerAction, TriggerResult
)


logger = logging.getLogger(__name__)


class TriggerSystemAdapter(TriggerPort):
    """트리거 시스템 어댑터 구현"""
    
    def __init__(self, config_file: str = "triggers.json"):
        self.config_file = config_file
        self.triggers: Dict[str, Dict] = {}
        self.history: List[TriggerResult] = []
        self.lock = threading.Lock()
        self._load_triggers()
    
    def _load_triggers(self):
        """설정 파일에서 트리거 로드"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    data = json.load(f)
                    for name, config in data.items():
                        condition = TriggerCondition(
                            type=TriggerType(config['condition']['type']),
                            pattern=config['condition'].get('pattern'),
                            keywords=config['condition'].get('keywords'),
                            event_name=config['condition'].get('event_name'),
                            schedule=config['condition'].get('schedule')
                        )
                        action = TriggerAction(
                            name=config['action']['name'],
                            handler=config['action']['handler'],
                            params=config['action'].get('params', {}),
                            async_execution=config['action'].get('async', False)
                        )
                        self.register_trigger(name, condition, action)
            except Exception as e:
                logger.error(f"트리거 로드 실패: {e}")
    
    def _save_triggers(self):
        """트리거 설정 저장"""
        try:
            data = {}
            for name, trigger in self.triggers.items():
                data[name] = {
                    'condition': {
                        'type': trigger['condition'].type.value,
                        'pattern': trigger['condition'].pattern,
                        'keywords': trigger['condition'].keywords,
                        'event_name': trigger['condition'].event_name,
                        'schedule': trigger['condition'].schedule
                    },
                    'action': {
                        'name': trigger['action'].name,
                        'handler': trigger['action'].handler,
                        'params': trigger['action'].params,
                        'async': trigger['action'].async_execution
                    },
                    'enabled': trigger['enabled']
                }
            
            with open(self.config_file, 'w') as f:
                json.dump(data, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"트리거 저장 실패: {e}")
    
    def register_trigger(
        self, 
        name: str, 
        condition: TriggerCondition, 
        action: TriggerAction
    ) -> bool:
        """트리거 등록"""
        with self.lock:
            try:
                self.triggers[name] = {
                    'condition': condition,
                    'action': action,
                    'enabled': True,
                    'created_at': datetime.now(),
                    'last_triggered': None,
                    'trigger_count': 0
                }
                self._save_triggers()
                logger.info(f"트리거 등록: {name}")
                return True
            except Exception as e:
                logger.error(f"트리거 등록 실패: {e}")
                return False
    
    def unregister_trigger(self, name: str) -> bool:
        """트리거 해제"""
        with self.lock:
            if name in self.triggers:
                del self.triggers[name]
                self._save_triggers()
                logger.info(f"트리거 해제: {name}")
                return True
            return False
    
    def check_triggers(self, context: TriggerContext) -> List[str]:
        """조건에 맞는 트리거 확인"""
        matching_triggers = []
        
        for name, trigger in self.triggers.items():
            if not trigger['enabled']:
                continue
            
            condition = trigger['condition']
            
            # 트리거 타입별 조건 체크
            if self._check_condition(condition, context):
                matching_triggers.append(name)
        
        return matching_triggers
    
    def _check_condition(self, condition: TriggerCondition, context: TriggerContext) -> bool:
        """트리거 조건 체크"""
        try:
            if condition.type == TriggerType.KEYWORD:
                # 키워드 체크
                if condition.keywords:
                    text = str(context.data.get('text', ''))
                    return any(keyword in text for keyword in condition.keywords)
            
            elif condition.type == TriggerType.PATTERN:
                # 정규식 패턴 체크
                if condition.pattern:
                    text = str(context.data.get('text', ''))
                    return bool(re.search(condition.pattern, text))
            
            elif condition.type == TriggerType.EVENT:
                # 이벤트 체크
                if condition.event_name:
                    return context.data.get('event') == condition.event_name
            
            elif condition.type == TriggerType.GITHUB_EVENT:
                # GitHub 이벤트 체크
                if condition.event_name:
                    return (
                        context.source == 'github' and 
                        context.data.get('action') == condition.event_name
                    )
            
            elif condition.type == TriggerType.CONDITION:
                # 커스텀 조건 체크
                if condition.custom_check:
                    return condition.custom_check(context)
            
            return False
            
        except Exception as e:
            logger.error(f"조건 체크 실패: {e}")
            return False
    
    def execute_trigger(self, name: str, context: TriggerContext) -> TriggerResult:
        """트리거 실행"""
        if name not in self.triggers:
            return TriggerResult(
                trigger_name=name,
                success=False,
                executed_actions=[],
                results={},
                error="Trigger not found"
            )
        
        trigger = self.triggers[name]
        if not trigger['enabled']:
            return TriggerResult(
                trigger_name=name,
                success=False,
                executed_actions=[],
                results={},
                error="Trigger is disabled"
            )
        
        try:
            action = trigger['action']
            
            # 액션 실행
            result = self._execute_action(action, context)
            
            # 트리거 통계 업데이트
            with self.lock:
                trigger['last_triggered'] = datetime.now()
                trigger['trigger_count'] += 1
            
            # 결과 생성
            trigger_result = TriggerResult(
                trigger_name=name,
                success=True,
                executed_actions=[action.name],
                results={'action_result': result}
            )
            
            # 히스토리에 추가
            self.history.append(trigger_result)
            
            return trigger_result
            
        except Exception as e:
            logger.error(f"트리거 실행 실패: {e}")
            error_result = TriggerResult(
                trigger_name=name,
                success=False,
                executed_actions=[],
                results={},
                error=str(e)
            )
            self.history.append(error_result)
            return error_result
    
    def _execute_action(self, action: TriggerAction, context: TriggerContext) -> Any:
        """액션 실행"""
        # 핸들러 파싱 (예: "pm_processor_adapter.process_issue")
        parts = action.handler.split('.')
        
        if len(parts) == 2:
            adapter_name, method_name = parts
            
            # 동적으로 어댑터 임포트 및 실행
            if adapter_name == 'pm_processor_adapter':
                from src.adapters.pm.pm_processor_adapter import PMProcessorAdapter
                adapter = PMProcessorAdapter()
                method = getattr(adapter, method_name, None)
                if method:
                    return method(**action.params) if action.params else method()
            
            # 다른 어댑터들도 추가 가능
        
        # 기본 동작
        logger.warning(f"핸들러를 찾을 수 없음: {action.handler}")
        return None
    
    def get_trigger_history(self, name: str = None) -> List[TriggerResult]:
        """트리거 실행 이력 조회"""
        if name:
            return [r for r in self.history if r.trigger_name == name]
        return self.history.copy()
    
    def enable_trigger(self, name: str) -> bool:
        """트리거 활성화"""
        if name in self.triggers:
            self.triggers[name]['enabled'] = True
            self._save_triggers()
            return True
        return False
    
    def disable_trigger(self, name: str) -> bool:
        """트리거 비활성화"""
        if name in self.triggers:
            self.triggers[name]['enabled'] = False
            self._save_triggers()
            return True
        return False