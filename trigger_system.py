#!/usr/bin/env python3
"""
Trigger System - 자동 실행 트리거 관리
"""

import re
import json
import os
from typing import Dict, List, Optional, Callable
from datetime import datetime, time
import threading
import subprocess
# import schedule  # Optional dependency

class TriggerType:
    """트리거 타입"""
    KEYWORD = "keyword"
    EVENT = "event"
    TIME = "time"
    CONDITION = "condition"
    PATTERN = "pattern"

class Trigger:
    """기본 트리거 클래스"""
    
    def __init__(self, name: str, trigger_type: str, condition: Dict, action: str):
        self.name = name
        self.type = trigger_type
        self.condition = condition
        self.action = action
        self.enabled = True
        self.last_triggered = None
        self.trigger_count = 0
    
    def check(self, context: Dict) -> bool:
        """트리거 조건 체크"""
        raise NotImplementedError
    
    def execute(self, context: Dict) -> Dict:
        """트리거 실행"""
        self.last_triggered = datetime.now()
        self.trigger_count += 1
        
        return {
            "trigger": self.name,
            "action": self.action,
            "timestamp": self.last_triggered.isoformat(),
            "context": context
        }

class KeywordTrigger(Trigger):
    """키워드 기반 트리거"""
    
    def __init__(self, name: str, keywords: List[str], action: str):
        super().__init__(name, TriggerType.KEYWORD, {"keywords": keywords}, action)
        self.keywords = keywords
    
    def check(self, context: Dict) -> bool:
        """텍스트에 키워드 포함 여부 체크"""
        text = context.get("text", "").lower()
        return any(keyword in text for keyword in self.keywords)

class EventTrigger(Trigger):
    """이벤트 기반 트리거"""
    
    def __init__(self, name: str, event_type: str, conditions: Dict, action: str):
        super().__init__(name, TriggerType.EVENT, {"event": event_type, **conditions}, action)
        self.event_type = event_type
        self.conditions = conditions
    
    def check(self, context: Dict) -> bool:
        """이벤트 발생 체크"""
        if context.get("event") != self.event_type:
            return False
        
        # 추가 조건 체크
        for key, value in self.conditions.items():
            if context.get(key) != value:
                return False
        
        return True

class TimeTrigger(Trigger):
    """시간 기반 트리거"""
    
    def __init__(self, name: str, schedule_time: str, action: str):
        super().__init__(name, TriggerType.TIME, {"time": schedule_time}, action)
        self.schedule_time = schedule_time
        self.scheduled = False
    
    def check(self, context: Dict) -> bool:
        """현재 시간이 스케줄 시간인지 체크"""
        # schedule 라이브러리 사용
        return False  # schedule 라이브러리가 직접 처리

class ConditionTrigger(Trigger):
    """조건 기반 트리거"""
    
    def __init__(self, name: str, condition_func: str, action: str):
        super().__init__(name, TriggerType.CONDITION, {"condition": condition_func}, action)
        self.condition_func = condition_func
    
    def check(self, context: Dict) -> bool:
        """조건 함수 실행"""
        # 간단한 조건 평가 (실제로는 더 안전한 평가 필요)
        try:
            # 예: "error_rate > 10"
            if ">" in self.condition_func:
                var, threshold = self.condition_func.split(">")
                var = var.strip()
                threshold = float(threshold.strip())
                value = context.get(var, 0)
                return value > threshold
            elif "<" in self.condition_func:
                var, threshold = self.condition_func.split("<")
                var = var.strip()
                threshold = float(threshold.strip())
                value = context.get(var, 0)
                return value < threshold
        except:
            pass
        
        return False

class PatternTrigger(Trigger):
    """패턴 기반 트리거"""
    
    def __init__(self, name: str, pattern: str, action: str):
        super().__init__(name, TriggerType.PATTERN, {"pattern": pattern}, action)
        self.pattern = re.compile(pattern)
    
    def check(self, context: Dict) -> bool:
        """정규식 패턴 매칭"""
        text = context.get("text", "")
        return bool(self.pattern.search(text))

class TriggerSystem:
    """트리거 시스템 관리자"""
    
    def __init__(self, config_file: str = "triggers.json"):
        self.triggers = []
        self.config_file = config_file
        self.running = False
        self.thread = None
        
        # 설정 파일 로드
        self.load_config()
        
        # 기본 트리거 설정
        self.setup_default_triggers()
    
    def load_config(self):
        """설정 파일에서 트리거 로드"""
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r') as f:
                config = json.load(f)
                
                for trigger_config in config.get("triggers", []):
                    self.add_trigger_from_config(trigger_config)
    
    def save_config(self):
        """현재 트리거 설정 저장"""
        config = {
            "triggers": []
        }
        
        for trigger in self.triggers:
            config["triggers"].append({
                "name": trigger.name,
                "type": trigger.type,
                "condition": trigger.condition,
                "action": trigger.action,
                "enabled": trigger.enabled
            })
        
        with open(self.config_file, 'w') as f:
            json.dump(config, f, indent=2)
    
    def add_trigger_from_config(self, config: Dict):
        """설정에서 트리거 추가"""
        trigger_type = config.get("type")
        
        if trigger_type == TriggerType.KEYWORD:
            trigger = KeywordTrigger(
                name=config["name"],
                keywords=config["condition"]["keywords"],
                action=config["action"]
            )
        elif trigger_type == TriggerType.EVENT:
            trigger = EventTrigger(
                name=config["name"],
                event_type=config["condition"]["event"],
                conditions=config["condition"].get("conditions", {}),
                action=config["action"]
            )
        elif trigger_type == TriggerType.TIME:
            trigger = TimeTrigger(
                name=config["name"],
                schedule_time=config["condition"]["time"],
                action=config["action"]
            )
        elif trigger_type == TriggerType.PATTERN:
            trigger = PatternTrigger(
                name=config["name"],
                pattern=config["condition"]["pattern"],
                action=config["action"]
            )
        else:
            return
        
        trigger.enabled = config.get("enabled", True)
        self.triggers.append(trigger)
    
    def setup_default_triggers(self):
        """기본 트리거 설정"""
        # 버그 키워드 트리거
        self.add_trigger(KeywordTrigger(
            name="bug_fix_trigger",
            keywords=["버그", "에러", "오류", "수정", "고쳐"],
            action="bug_fix_process"
        ))
        
        # 개발 키워드 트리거
        self.add_trigger(KeywordTrigger(
            name="feature_dev_trigger",
            keywords=["만들어", "개발", "구현", "추가"],
            action="feature_development"
        ))
        
        # 분석 키워드 트리거
        self.add_trigger(KeywordTrigger(
            name="analysis_trigger",
            keywords=["분석", "조사", "왜", "원인"],
            action="research_process"
        ))
        
        # 긴급 패턴 트리거
        self.add_trigger(PatternTrigger(
            name="urgent_trigger",
            pattern=r"(급해|빨리|ASAP|긴급)",
            action="quick_process"
        ))
        
        # GitHub 이벤트 트리거
        self.add_trigger(EventTrigger(
            name="pr_merged_trigger",
            event_type="pr_merged",
            conditions={"branch": "main"},
            action="deploy_check"
        ))
        
        # 에러율 조건 트리거
        self.add_trigger(ConditionTrigger(
            name="high_error_trigger",
            condition_func="error_rate > 10",
            action="emergency_review"
        ))
    
    def add_trigger(self, trigger: Trigger):
        """트리거 추가"""
        self.triggers.append(trigger)
        
        # 시간 트리거는 스케줄 등록
        if isinstance(trigger, TimeTrigger):
            self.schedule_time_trigger(trigger)
    
    def schedule_time_trigger(self, trigger: TimeTrigger):
        """시간 트리거 스케줄 등록"""
        # schedule 라이브러리 사용 (optional)
        schedule_time = trigger.schedule_time
        print(f"⏰ 시간 트리거 등록: {trigger.name} - {schedule_time}")
        # 실제 구현은 schedule 라이브러리 설치 후 활성화
    
    def check_triggers(self, context: Dict) -> List[Dict]:
        """모든 트리거 체크"""
        triggered = []
        
        for trigger in self.triggers:
            if not trigger.enabled:
                continue
            
            if trigger.check(context):
                result = trigger.execute(context)
                triggered.append(result)
        
        return triggered
    
    def execute_trigger(self, trigger: Trigger, context: Dict = None):
        """트리거 실행"""
        if context is None:
            context = {}
        
        result = trigger.execute(context)
        
        # 액션 실행
        self.execute_action(result["action"], context)
        
        return result
    
    def execute_action(self, action: str, context: Dict):
        """액션 실행"""
        print(f"🎯 트리거 액션 실행: {action}")
        
        # 1. 먼저 GitHub 이슈 생성
        issue_number = self.create_github_issue(action, context)
        
        if issue_number:
            print(f"✅ GitHub Issue #{issue_number} 생성됨")
            context['issue_number'] = issue_number
            
            # 2. 프로세스 실행
            if action.endswith("_process"):
                # orchestrator 호출 (이슈 번호 포함)
                cmd = f"python3 orchestrator.py --process {action} --issue {issue_number} --auto"
                subprocess.run(cmd, shell=True)
            else:
                # 기타 액션
                print(f"  액션: {action}")
                print(f"  컨텍스트: {context}")
        else:
            print(f"❌ 이슈 생성 실패, 작업 중단")
    
    def create_github_issue(self, action: str, context: Dict) -> str:
        """GitHub 이슈 생성"""
        from datetime import datetime
        
        title = f"[Trigger] {action} - 자동 실행"
        body = f"""## 🎯 트리거 자동 실행

### 액션
{action}

### 컨텍스트
{json.dumps(context, indent=2, ensure_ascii=False)}

### 생성 시간
{datetime.now().isoformat()}

---
*AI Orchestra v2 - Trigger System*"""
        
        cmd = f'''gh issue create -R ihw33/ai-orchestra-v02 \
            --title "{title}" \
            --body "{body}"'''
        
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        
        if result.returncode == 0:
            issue_url = result.stdout.strip()
            issue_number = issue_url.split('/')[-1]
            return issue_number
        
        return None
    
    def start_monitoring(self):
        """백그라운드 모니터링 시작"""
        self.running = True
        
        def monitor():
            while self.running:
                # schedule.run_pending()  # Optional when schedule is installed
                threading.Event().wait(1)
        
        self.thread = threading.Thread(target=monitor)
        self.thread.start()
    
    def stop_monitoring(self):
        """모니터링 중지"""
        self.running = False
        if self.thread:
            self.thread.join()
    
    def get_status(self) -> Dict:
        """트리거 시스템 상태"""
        return {
            "total_triggers": len(self.triggers),
            "enabled_triggers": sum(1 for t in self.triggers if t.enabled),
            "trigger_stats": [
                {
                    "name": t.name,
                    "type": t.type,
                    "enabled": t.enabled,
                    "trigger_count": t.trigger_count,
                    "last_triggered": t.last_triggered.isoformat() if t.last_triggered else None
                }
                for t in self.triggers
            ]
        }

class SmartTriggerAdapter:
    """지시 분석과 트리거 연동"""
    
    def __init__(self, trigger_system: TriggerSystem):
        self.trigger_system = trigger_system
    
    def process_instruction(self, instruction: str) -> List[str]:
        """지시에서 트리거 액션 추출"""
        context = {"text": instruction}
        
        # 트리거 체크
        triggered = self.trigger_system.check_triggers(context)
        
        # 트리거된 액션들 반환
        actions = [t["action"] for t in triggered]
        
        if actions:
            print(f"🔥 자동 트리거 발동: {actions}")
        
        return actions

# 사용 예시
if __name__ == "__main__":
    # 트리거 시스템 초기화
    trigger_system = TriggerSystem()
    
    # 테스트 컨텍스트
    test_contexts = [
        {"text": "버그 #123을 수정해줘"},
        {"text": "로그인 기능 만들어줘"},
        {"text": "이 코드 왜 느린지 분석해줘"},
        {"text": "빨리 처리해줘 ASAP"},
        {"event": "pr_merged", "branch": "main"},
        {"error_rate": 15}
    ]
    
    print("=== 트리거 시스템 테스트 ===\n")
    
    for context in test_contexts:
        print(f"컨텍스트: {context}")
        triggered = trigger_system.check_triggers(context)
        
        if triggered:
            for t in triggered:
                print(f"  ✅ 트리거: {t['trigger']} → 액션: {t['action']}")
        else:
            print(f"  ❌ 트리거 없음")
        print()
    
    # 상태 확인
    print("=== 트리거 시스템 상태 ===")
    status = trigger_system.get_status()
    print(f"전체 트리거: {status['total_triggers']}")
    print(f"활성 트리거: {status['enabled_triggers']}")
    
    # 설정 저장
    trigger_system.save_config()
    print("\n✅ 트리거 설정 저장됨: triggers.json")