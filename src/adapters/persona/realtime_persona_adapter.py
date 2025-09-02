"""
실시간 PM Claude 페르소나 할당 Adapter
PM Claude가 실제 대화로 판단하여 페르소나 할당
"""

import subprocess
import json
import tempfile
from typing import Dict, Optional
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from ports.persona_assignment_port import Persona, PersonaType
from adapters.persona.persona_assignment_adapter import PMClaudePersonaAssignmentAdapter

class RealtimePMClaudeAdapter(PMClaudePersonaAssignmentAdapter):
    """실시간 PM Claude 판단 Adapter"""
    
    def select_persona_with_pm_reasoning(self, task_description: str) -> Dict:
        """PM Claude(나)가 실제로 판단하여 페르소나 선택"""
        
        # PM Claude에게 실제로 물어보기
        prompt = f"""당신은 PM Claude입니다. 다음 작업에 가장 적합한 페르소나를 선택해주세요.

작업: {task_description}

사용 가능한 페르소나:
1. Backend Developer - 구현, 코딩
2. Frontend Developer - UI, 사용자 인터페이스
3. System Architect - 설계, 아키텍처
4. Code Reviewer - 코드 리뷰, 품질 검사
5. PM Claude (당신) - 긴급 상황, 중요 결정

다음 형식으로 답변해주세요:
선택: [페르소나 이름]
이유: [선택 이유]
AI: [claude/gemini/codex 중 선택]
대안: [대안 페르소나]"""

        # 실제 PM Claude의 판단 받기 (시뮬레이션)
        pm_decision = self._get_pm_decision(prompt)
        
        return pm_decision
    
    def _get_pm_decision(self, prompt: str) -> Dict:
        """PM의 실제 판단 받기"""
        
        # 실제 환경에서는 claude CLI 호출
        # 여기서는 시뮬레이션
        
        # PM Claude의 지능적 판단 시뮬레이션
        if "긴급" in prompt or "critical" in prompt:
            return {
                'persona': 'PM Claude',
                'reason': '긴급 상황이므로 PM이 직접 개입 필요',
                'ai': 'claude',
                'alternative': 'System Architect'
            }
        elif "설계" in prompt or "architecture" in prompt:
            return {
                'persona': 'System Architect',
                'reason': '복잡한 설계 작업이므로 아키텍트가 적합',
                'ai': 'claude',
                'alternative': 'Backend Lead'
            }
        elif "리뷰" in prompt or "review" in prompt:
            return {
                'persona': 'Code Reviewer',
                'reason': '코드 품질 검사가 필요한 작업',
                'ai': 'claude',
                'alternative': 'Backend Developer'
            }
        else:
            return {
                'persona': 'Backend Developer',
                'reason': '일반적인 구현 작업',
                'ai': 'codex',
                'alternative': 'Frontend Developer'
            }
    
    def execute_with_persona(self, task_id: int, task_description: str) -> Dict:
        """페르소나 할당 후 실제 실행"""
        
        print(f"\n🤔 PM Claude가 작업 분석 중...")
        
        # 1. PM의 실시간 판단
        decision = self.select_persona_with_pm_reasoning(task_description)
        
        print(f"✅ PM 결정: {decision['persona']}")
        print(f"📝 이유: {decision['reason']}")
        print(f"🤖 할당 AI: {decision['ai']}")
        
        # 2. 실제 AI에게 페르소나와 함께 작업 할당
        execution_prompt = f"""당신은 {decision['persona']}입니다.

작업: {task_description}

페르소나 특성:
- 역할에 충실하게 행동
- 전문 분야 내에서 최선의 해결책 제시
- 필요시 상급자(PM)에게 보고

작업을 수행하세요."""
        
        # 3. 선택된 AI 실행
        result = self._execute_ai_with_persona(
            decision['ai'], 
            execution_prompt
        )
        
        return {
            'task_id': task_id,
            'persona': decision['persona'],
            'ai': decision['ai'],
            'result': result,
            'pm_reasoning': decision['reason']
        }
    
    def _execute_ai_with_persona(self, ai_name: str, prompt: str) -> str:
        """페르소나와 함께 AI 실행"""
        
        # 실제 환경에서는 해당 AI CLI 호출
        print(f"\n🚀 {ai_name}가 페르소나 역할로 작업 수행 중...")
        
        # 시뮬레이션 결과
        return f"{ai_name}가 작업을 완료했습니다."


# PM의 동적 할당 예시
if __name__ == "__main__":
    adapter = RealtimePMClaudeAdapter()
    
    print("="*60)
    print("🎯 실시간 PM Claude 페르소나 할당 시연")
    print("="*60)
    
    test_cases = [
        (101, "긴급! 프로덕션 API 서버 다운"),
        (102, "새로운 마이크로서비스 아키텍처 설계"),
        (103, "PR #45 코드 리뷰"),
        (104, "사용자 인증 API 구현")
    ]
    
    for task_id, description in test_cases:
        print(f"\n작업 #{task_id}: {description}")
        result = adapter.execute_with_persona(task_id, description)
        print(f"결과: {result['result']}")
        print("-"*40)