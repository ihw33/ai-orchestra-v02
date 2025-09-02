"""
Smart Issue Creator Adapter
대화 분석하여 필요시에만 확인하고 이슈 생성
"""

import subprocess
import json
import re
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import sys
import os

# Port 인터페이스 import
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from ports.issue_decision_port import (
    IssueDecisionPort,
    IssueCreatorPort,
    DecisionResult,
    IssueType,
    Confidence
)

class SmartIssueDecisionAdapter(IssueDecisionPort):
    """스마트한 이슈 생성 판단 Adapter"""
    
    def __init__(self):
        # 명확한 이슈 생성 패턴 (확신도 HIGH)
        self.clear_issue_patterns = {
            r'구현해\s*줘|만들어\s*줘|개발해\s*줘': (IssueType.FEATURE, 0.95),
            r'추가해야|추가해\s*줘|넣어\s*줘': (IssueType.ENHANCEMENT, 0.9),
            r'버그|오류|에러|안\s*돼|안\s*됨': (IssueType.BUG, 0.95),
            r'수정해\s*줘|고쳐\s*줘|바꿔\s*줘': (IssueType.BUG, 0.85),
            r'adapter|port|시스템에?\s*추가': (IssueType.AI_TASK, 0.9),
            r'\[AI\]|\[ai\]': (IssueType.AI_TASK, 1.0),
        }
        
        # 명확한 비이슈 패턴 (확신도 HIGH)
        self.clear_no_issue_patterns = {
            r'뭐야\?|뭔데\?|어떻게|왜': ('question', 0.9),
            r'설명해|알려줘|보여줘': ('explanation', 0.85),
            r'확인해|체크해|테스트': ('verification', 0.8),
            r'고마워|잘했어|좋아': ('feedback', 0.95),
            r'맞아|응|그래': ('agreement', 0.9),
        }
        
        # 애매한 패턴 (확신도 MEDIUM/LOW - 확인 필요)
        self.ambiguous_patterns = {
            r'해야|필요해|있어야': 0.6,  # 제안일 수도, 요청일 수도
            r'어떻게\s*하면|할\s*수\s*있': 0.5,  # 질문일 수도, 요청일 수도
            r'이슈|작업|태스크': 0.7,  # 문맥에 따라 다름
        }
    
    def analyze_conversation(self, message: str, context: Dict) -> DecisionResult:
        """대화 분석하여 이슈 생성 필요 여부 판단"""
        
        # 1. 명확한 이슈 패턴 확인
        for pattern, (issue_type, confidence) in self.clear_issue_patterns.items():
            if re.search(pattern, message, re.IGNORECASE):
                return DecisionResult(
                    should_create=True,
                    confidence=Confidence.HIGH if confidence > 0.9 else Confidence.MEDIUM,
                    issue_type=issue_type,
                    reason=f"{issue_type.value} 작업 요청 감지",
                    needs_confirmation=False  # HIGH confidence는 확인 불필요
                )
        
        # 2. 명확한 비이슈 패턴 확인
        for pattern, (intent, confidence) in self.clear_no_issue_patterns.items():
            if re.search(pattern, message, re.IGNORECASE):
                return DecisionResult(
                    should_create=False,
                    confidence=Confidence.HIGH if confidence > 0.9 else Confidence.MEDIUM,
                    issue_type=None,
                    reason=f"{intent} - 이슈 생성 불필요",
                    needs_confirmation=False
                )
        
        # 3. 애매한 패턴 - 확인 필요
        for pattern, confidence in self.ambiguous_patterns.items():
            if re.search(pattern, message, re.IGNORECASE):
                # 문맥 분석으로 확신도 조정
                adjusted_confidence = self._adjust_confidence_by_context(message, context, confidence)
                
                if adjusted_confidence < 0.6:
                    conf_level = Confidence.LOW
                    needs_confirm = True
                elif adjusted_confidence < 0.9:
                    conf_level = Confidence.MEDIUM
                    # MEDIUM은 중요한 키워드가 있을 때만 확인
                    needs_confirm = self._should_confirm_medium(message)
                else:
                    conf_level = Confidence.HIGH
                    needs_confirm = False
                
                return DecisionResult(
                    should_create=adjusted_confidence > 0.5,
                    confidence=conf_level,
                    issue_type=IssueType.FEATURE if adjusted_confidence > 0.5 else None,
                    reason="문맥상 작업 요청 가능성",
                    needs_confirmation=needs_confirm,
                    confirmation_message=self._generate_smart_confirmation(message, adjusted_confidence)
                )
        
        # 4. 패턴 매칭 실패 - 기본값
        return DecisionResult(
            should_create=False,
            confidence=Confidence.LOW,
            issue_type=None,
            reason="명확한 작업 요청 없음",
            needs_confirmation=True,
            confirmation_message="이 내용을 이슈로 만들어야 할까요?"
        )
    
    def _adjust_confidence_by_context(self, message: str, context: Dict, base_confidence: float) -> float:
        """문맥 기반 확신도 조정"""
        adjusted = base_confidence
        
        # 이전 대화가 구현 관련이었으면 확신도 상승
        if context.get('previous_topic') == 'implementation':
            adjusted += 0.2
        
        # 명령형 어미가 있으면 확신도 상승
        if re.search(r'해줘|하자|해야|하면\s*돼', message):
            adjusted += 0.15
        
        # 질문 어미가 있으면 확신도 하락
        if re.search(r'\?|까요|나요|가요', message):
            adjusted -= 0.2
        
        return min(1.0, max(0.0, adjusted))
    
    def _should_confirm_medium(self, message: str) -> bool:
        """MEDIUM 확신도에서 확인 필요 여부"""
        # 중요한 키워드가 있으면 확인
        important_keywords = ['시스템', '전체', '모든', '삭제', '변경', '수정']
        return any(keyword in message for keyword in important_keywords)
    
    def _generate_smart_confirmation(self, message: str, confidence: float) -> str:
        """스마트한 확인 메시지 생성"""
        if confidence > 0.7:
            return f"이 작업을 AI 팀에게 할당할까요? ('{message[:30]}...')"
        elif confidence > 0.5:
            return f"이슈를 생성하시겠습니까? 아니면 제가 직접 답변할까요?"
        else:
            return "이 내용은 이슈로 만들 필요가 있을까요?"
    
    def generate_confirmation_prompt(self, decision: DecisionResult) -> str:
        """사용자 확인 프롬프트 생성"""
        if decision.confirmation_message:
            return decision.confirmation_message
        
        if decision.should_create:
            return f"[{decision.issue_type.value}] 이슈를 생성할까요? (확신도: {decision.confidence.value})"
        else:
            return "이슈 생성이 필요하지 않아 보입니다. 직접 답변해드릴까요?"
    
    def classify_intent(self, message: str) -> Tuple[str, float]:
        """사용자 의도 분류"""
        # 각 패턴 확인하여 가장 높은 확신도 반환
        max_confidence = 0.0
        best_intent = "unknown"
        
        # 이슈 패턴 확인
        for pattern, (issue_type, conf) in self.clear_issue_patterns.items():
            if re.search(pattern, message, re.IGNORECASE):
                if conf > max_confidence:
                    max_confidence = conf
                    best_intent = f"create_issue:{issue_type.value}"
        
        # 비이슈 패턴 확인
        for pattern, (intent, conf) in self.clear_no_issue_patterns.items():
            if re.search(pattern, message, re.IGNORECASE):
                if conf > max_confidence:
                    max_confidence = conf
                    best_intent = f"no_issue:{intent}"
        
        return best_intent, max_confidence
    
    def extract_requirements(self, message: str) -> Dict:
        """메시지에서 요구사항 추출"""
        requirements = {
            'raw_message': message,
            'extracted_features': [],
            'constraints': [],
            'references': []
        }
        
        # 기능 추출
        if '구현' in message or '만들' in message:
            # "X를 구현해줘" 패턴에서 X 추출
            match = re.search(r'(.+?)를?\s*(?:구현|만들)', message)
            if match:
                requirements['extracted_features'].append(match.group(1))
        
        # 제약사항 추출
        if '해야' in message or '필요' in message:
            requirements['constraints'].append(message)
        
        # 참조 추출 (Adapter, Port 등)
        technical_terms = re.findall(r'[A-Z][a-z]+(?:[A-Z][a-z]+)*', message)
        requirements['references'].extend(technical_terms)
        
        return requirements


class GitHubIssueCreatorAdapter(IssueCreatorPort):
    """GitHub 이슈 생성 Adapter"""
    
    def __init__(self, repo: str = "ihw33/ai-orchestra-v02"):
        self.repo = repo
        self.decision_adapter = SmartIssueDecisionAdapter()
    
    def create_issue(self, title: str, body: str, labels: List[str]) -> Dict:
        """GitHub 이슈 생성"""
        try:
            import tempfile
            
            # 라벨 문자열 생성
            label_str = ','.join(labels) if labels else 'ai-task'
            
            # 본문을 임시 파일로 저장
            with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
                f.write(body)
                body_file = f.name
            
            # GitHub CLI로 이슈 생성
            cmd = f'gh issue create -R {self.repo} --title "{title}" --body-file {body_file} --label "{label_str}"'
            
            result = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                text=True,
                timeout=10
            )
            
            # 임시 파일 삭제
            import os
            os.remove(body_file)
            
            if result.returncode == 0:
                # URL에서 이슈 번호 추출
                url = result.stdout.strip()
                issue_number = url.split('/')[-1] if url else None
                
                return {
                    'success': True,
                    'issue_number': issue_number,
                    'url': url,
                    'created_at': datetime.now().isoformat()
                }
            else:
                return {
                    'success': False,
                    'error': result.stderr
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def update_issue(self, issue_number: int, updates: Dict) -> Dict:
        """이슈 업데이트"""
        try:
            cmd_parts = [f'gh issue edit {issue_number} -R {self.repo}']
            
            if 'title' in updates:
                cmd_parts.append(f'--title "{updates["title"]}"')
            if 'body' in updates:
                cmd_parts.append(f'--body "{updates["body"]}"')
            if 'labels' in updates:
                cmd_parts.append(f'--add-label "{",".join(updates["labels"])}"')
            
            cmd = ' '.join(cmd_parts)
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            
            return {
                'success': result.returncode == 0,
                'issue_number': issue_number
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def close_issue(self, issue_number: int, reason: str) -> Dict:
        """이슈 종료"""
        try:
            # 종료 코멘트 추가
            comment_cmd = f'gh issue comment {issue_number} -R {self.repo} --body "종료 사유: {reason}"'
            subprocess.run(comment_cmd, shell=True)
            
            # 이슈 종료
            close_cmd = f'gh issue close {issue_number} -R {self.repo}'
            result = subprocess.run(close_cmd, shell=True, capture_output=True, text=True)
            
            return {
                'success': result.returncode == 0,
                'issue_number': issue_number,
                'closed_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def format_issue_body(self, requirements: Dict, persona_style: Optional[str] = None) -> str:
        """이슈 본문 포맷팅"""
        
        if persona_style == 'formal':
            # 김정호 스타일 - 체계적
            body = "## 목적\n"
            body += f"{requirements.get('raw_message', '')}\n\n"
            body += "## 요구사항\n"
            for feature in requirements.get('extracted_features', []):
                body += f"- {feature}\n"
            body += "\n## 제약사항\n"
            for constraint in requirements.get('constraints', []):
                body += f"- {constraint}\n"
            
        elif persona_style == 'friendly':
            # Maria 스타일 - 친근함
            body = "## 🎯 할 일\n"
            body += f"{requirements.get('raw_message', '')} 😊\n\n"
            body += "## ✨ 만들 것들\n"
            for feature in requirements.get('extracted_features', []):
                body += f"- {feature}\n"
            body += "\n화이팅! 💪\n"
            
        else:
            # 기본 스타일
            body = "## 작업 내용\n"
            body += f"{requirements.get('raw_message', '')}\n\n"
            if requirements.get('extracted_features'):
                body += "## 구현 항목\n"
                for feature in requirements['extracted_features']:
                    body += f"- {feature}\n"
            if requirements.get('references'):
                body += "\n## 참조\n"
                for ref in requirements['references']:
                    body += f"- {ref}\n"
        
        return body


# 사용 예시
if __name__ == "__main__":
    # 테스트
    decision_adapter = SmartIssueDecisionAdapter()
    issue_creator = GitHubIssueCreatorAdapter()
    
    test_messages = [
        "PR Creator Adapter 구현해줘",  # HIGH confidence - 이슈 생성
        "이게 뭐야?",  # HIGH confidence - 이슈 불필요
        "이것도 추가해야 할 것 같은데",  # MEDIUM confidence - 확인 필요할 수도
        "시스템 전체를 수정해야 해",  # MEDIUM confidence - 중요하므로 확인
        "잘했어",  # HIGH confidence - 이슈 불필요
    ]
    
    for msg in test_messages:
        decision = decision_adapter.analyze_conversation(msg, {})
        print(f"\n메시지: {msg}")
        print(f"이슈 생성: {decision.should_create}")
        print(f"확신도: {decision.confidence.value}")
        print(f"확인 필요: {decision.needs_confirmation}")
        if decision.needs_confirmation:
            print(f"확인 메시지: {decision.confirmation_message}")