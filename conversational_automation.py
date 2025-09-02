#!/usr/bin/env python3
"""
대화형 자동화 시스템
사용자와 대화만으로 모든 작업을 자동화
"""

import re
import subprocess
from typing import Dict, List, Optional
from orchestrator import SmartOrchestrator
from trigger_system import TriggerSystem

class ConversationalAutomation:
    """대화 기반 자동화 시스템"""
    
    def __init__(self):
        self.orchestrator = SmartOrchestrator()
        self.triggers = TriggerSystem()
        
        # 대화 패턴 매칭
        self.patterns = {
            'feature': ['만들어', '구현', '개발', '추가'],
            'bug': ['수정', '버그', '에러', '오류'],
            'analysis': ['분석', '조사', '검토', '리뷰'],
            'deploy': ['배포', '릴리즈', '출시'],
            'test': ['테스트', '검증', '확인']
        }
    
    def process_conversation(self, user_input: str) -> Dict:
        """대화 입력을 자동 작업으로 변환"""
        
        # 1. 의도 파악
        intent = self.detect_intent(user_input)
        print(f"🧠 의도 파악: {intent}")
        
        # 2. 자동 이슈 생성 및 처리
        if intent:
            result = self.orchestrator.process_instruction(
                user_input,
                auto_execute=True
            )
            
            if 'issue_number' in result:
                return {
                    'status': 'success',
                    'message': f"✅ 작업 시작됨 (Issue #{result['issue_number']})",
                    'issue': result['issue_number'],
                    'process': result.get('name', 'unknown')
                }
        
        return {
            'status': 'unknown',
            'message': "🤔 무엇을 도와드릴까요?"
        }
    
    def detect_intent(self, text: str) -> Optional[str]:
        """대화에서 의도 추출"""
        text_lower = text.lower()
        
        for intent, keywords in self.patterns.items():
            if any(kw in text_lower for kw in keywords):
                return intent
        
        return None
    
    def suggest_next_action(self, context: Dict) -> str:
        """다음 행동 제안"""
        if context.get('status') == 'success':
            return f"Issue #{context['issue']}의 진행상황을 확인하시겠습니까?"
        else:
            return "어떤 작업을 도와드릴까요?"

# CLI 인터페이스
def main():
    """대화형 인터페이스"""
    automation = ConversationalAutomation()
    
    print("🤖 대화형 자동화 시스템")
    print("무엇이든 말씀해주세요. (종료: quit)")
    
    while True:
        user_input = input("\n👤 You: ")
        
        if user_input.lower() == 'quit':
            break
        
        result = automation.process_conversation(user_input)
        print(f"🤖 PM: {result['message']}")
        
        # 다음 제안
        suggestion = automation.suggest_next_action(result)
        print(f"💡 {suggestion}")

if __name__ == "__main__":
    main()