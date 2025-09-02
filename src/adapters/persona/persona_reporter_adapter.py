"""
Persona-based Reporter Adapter
페르소나의 성격과 스타일로 보고하는 Adapter
"""

import subprocess
import json
from typing import Dict, List, Optional, Any
from datetime import datetime
import sys
import os
import random

# Port 인터페이스 import
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from ports.reporter_port import (
    ReporterPort, 
    Report, 
    ReportResult, 
    ReportType
)

class PersonaReporterAdapter(ReporterPort):
    """페르소나 기반 보고 Adapter"""
    
    def __init__(self, persona_id: str, repo: str = "ihw33/ai-orchestra-v02"):
        self.repo = repo
        self.persona_id = persona_id
        self.persona = self._load_persona(persona_id)
        self.style_formatter = PersonaStyleFormatter(self.persona)
    
    def report_progress(self, target_id: str, progress: Dict) -> ReportResult:
        """페르소나 스타일로 진행 상황 보고"""
        
        # 페르소나 스타일로 내용 생성
        styled_content = self.style_formatter.format_progress(progress)
        
        # 페르소나 서명 추가
        styled_content = self._add_persona_signature(styled_content)
        
        report = Report(
            id=f"{self.persona_id}_progress_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            type=ReportType.PROGRESS,
            target_id=target_id,
            title=self._get_styled_title("진행 상황"),
            content=styled_content,
            metadata={'persona': self.persona_id, **progress}
        )
        
        return self._post_to_github(target_id, report)
    
    def report_completion(self, target_id: str, results: Dict) -> ReportResult:
        """페르소나 스타일로 완료 보고"""
        
        styled_content = self.style_formatter.format_completion(results)
        styled_content = self._add_persona_signature(styled_content)
        
        report = Report(
            id=f"{self.persona_id}_completion_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            type=ReportType.COMPLETION,
            target_id=target_id,
            title=self._get_styled_title("작업 완료"),
            content=styled_content,
            metadata={'persona': self.persona_id, **results}
        )
        
        return self._post_to_github(target_id, report)
    
    def report_error(self, target_id: str, error: Dict) -> ReportResult:
        """페르소나 스타일로 에러 보고"""
        
        styled_content = self.style_formatter.format_error(error)
        styled_content = self._add_persona_signature(styled_content)
        
        report = Report(
            id=f"{self.persona_id}_error_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            type=ReportType.ERROR,
            target_id=target_id,
            title=self._get_styled_title("문제 발생"),
            content=styled_content,
            metadata={'persona': self.persona_id, **error}
        )
        
        return self._post_to_github(target_id, report)
    
    def generate_summary(self, target_id: str, data: Dict) -> Report:
        """페르소나 스타일 요약 생성"""
        summary_content = self.style_formatter.format_summary(data)
        
        return Report(
            id=f"{self.persona_id}_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            type=ReportType.SUMMARY,
            target_id=target_id,
            title=self._get_styled_title("요약"),
            content=summary_content,
            metadata={'persona': self.persona_id, **data}
        )
    
    def should_report(self, event_type: str, context: Dict) -> bool:
        """페르소나별 보고 기준"""
        
        # 기본 규칙
        base_rules = {
            'task_completed': True,
            'error_occurred': True,
            'milestone_reached': True
        }
        
        # 페르소나별 추가 규칙
        if self.persona.get('personality', {}).get('traits'):
            traits = self.persona['personality']['traits']
            
            # 꼼꼼한 성격은 더 자주 보고
            if '꼼꼼함' in traits or '체계적' in traits:
                base_rules['progress_update'] = context.get('progress', 0) % 10 == 0
            
            # 신중한 성격은 중요한 것만 보고
            elif '신중함' in traits:
                base_rules['progress_update'] = context.get('progress', 0) % 50 == 0
            
            # 열정적인 성격은 모든 것을 보고
            elif '열정적' in traits:
                base_rules['any_update'] = True
        
        return base_rules.get(event_type, False)
    
    def _load_persona(self, persona_id: str) -> Dict:
        """페르소나 데이터 로드"""
        # 실제로는 personas/profiles/에서 로드
        # 여기서는 예시 데이터
        personas = {
            'backend_lead_01': {
                'profile': {
                    'name': '김정호',
                    'role': 'Backend Lead',
                    'experience': 10
                },
                'personality': {
                    'traits': ['신중함', '체계적', '완벽주의'],
                    'communication_style': 'formal'
                }
            },
            'frontend_lead_01': {
                'profile': {
                    'name': 'Maria Silva',
                    'role': 'Frontend Lead',
                    'experience': 8
                },
                'personality': {
                    'traits': ['창의적', '열정적', '협력적'],
                    'communication_style': 'friendly'
                }
            },
            'qa_lead_01': {
                'profile': {
                    'name': '박민수',
                    'role': 'QA Lead',
                    'experience': 7
                },
                'personality': {
                    'traits': ['꼼꼼함', '분석적', '비판적'],
                    'communication_style': 'analytical'
                }
            }
        }
        
        return personas.get(persona_id, personas['backend_lead_01'])
    
    def _get_styled_title(self, base_title: str) -> str:
        """페르소나 스타일의 제목 생성"""
        
        style = self.persona.get('personality', {}).get('communication_style', 'formal')
        name = self.persona['profile']['name']
        
        if style == 'formal':
            return f"[{name}] {base_title} 보고"
        elif style == 'friendly':
            return f"{name}의 {base_title} 소식! 🎉"
        elif style == 'analytical':
            return f"[분석] {base_title} - {name}"
        else:
            return f"{name}: {base_title}"
    
    def _add_persona_signature(self, content: str) -> str:
        """페르소나 서명 추가"""
        
        profile = self.persona['profile']
        traits = self.persona.get('personality', {}).get('traits', [])
        
        signature = f"\n\n---\n"
        signature += f"*보고자: {profile['name']} ({profile['role']})*\n"
        signature += f"*성향: {', '.join(traits[:2])}*"
        
        return content + signature
    
    def _post_to_github(self, issue_number: str, report: Report) -> ReportResult:
        """GitHub에 페르소나 스타일로 포스팅"""
        
        comment = f"## {report.title}\n\n{report.content}"
        
        try:
            # 임시 파일을 사용하여 multi-line 텍스트 전달
            import tempfile
            with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
                f.write(comment)
                temp_file = f.name
            
            cmd = f'gh issue comment {issue_number} -R {self.repo} --body-file {temp_file}'
            
            result = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                text=True,
                timeout=10
            )
            
            # 임시 파일 삭제
            import os
            os.remove(temp_file)
            
            if result.returncode == 0:
                return ReportResult(
                    success=True,
                    report_id=report.id,
                    url=result.stdout.strip() if result.stdout else None
                )
            else:
                return ReportResult(
                    success=False,
                    report_id=report.id,
                    errors=[result.stderr]
                )
                
        except Exception as e:
            return ReportResult(
                success=False,
                report_id=report.id,
                errors=[str(e)]
            )


class PersonaStyleFormatter:
    """페르소나별 스타일 포맷터"""
    
    def __init__(self, persona: Dict):
        self.persona = persona
        self.style = persona.get('personality', {}).get('communication_style', 'formal')
        self.traits = persona.get('personality', {}).get('traits', [])
    
    def format_progress(self, data: Dict) -> str:
        """페르소나 스타일 진행 상황"""
        
        if self.style == 'formal':
            return self._formal_progress(data)
        elif self.style == 'friendly':
            return self._friendly_progress(data)
        elif self.style == 'analytical':
            return self._analytical_progress(data)
        else:
            return self._default_progress(data)
    
    def format_completion(self, data: Dict) -> str:
        """페르소나 스타일 완료 보고"""
        
        if self.style == 'formal':
            return self._formal_completion(data)
        elif self.style == 'friendly':
            return self._friendly_completion(data)
        elif self.style == 'analytical':
            return self._analytical_completion(data)
        else:
            return self._default_completion(data)
    
    def format_error(self, data: Dict) -> str:
        """페르소나 스타일 에러 보고"""
        
        if self.style == 'formal':
            return self._formal_error(data)
        elif self.style == 'friendly':
            return self._friendly_error(data)
        elif self.style == 'analytical':
            return self._analytical_error(data)
        else:
            return self._default_error(data)
    
    def format_summary(self, data: Dict) -> str:
        """페르소나 스타일 요약"""
        # 각 스타일별 요약 구현
        return self._default_summary(data)
    
    # === Formal Style (김정호 - Backend Lead) ===
    def _formal_progress(self, data: Dict) -> str:
        content = "### 진행 상황 보고\n\n"
        content += f"현재 진행 중인 작업: {data.get('current_task', 'N/A')}\n"
        content += f"진행률: {data.get('progress', 0)}%\n\n"
        
        if 'details' in data:
            content += "#### 상세 내역\n"
            for key, value in data['details'].items():
                content += f"- {key}: {value}\n"
        
        content += "\n모든 작업이 계획대로 진행되고 있습니다."
        return content
    
    def _formal_completion(self, data: Dict) -> str:
        content = "### 작업 완료 보고\n\n"
        content += "다음 작업들이 성공적으로 완료되었습니다:\n\n"
        
        for task in data.get('completed_tasks', []):
            content += f"- [완료] {task}\n"
        
        content += "\n검토 후 차기 단계를 진행하겠습니다."
        return content
    
    def _formal_error(self, data: Dict) -> str:
        content = "### 오류 발생 보고\n\n"
        content += f"**발생 오류**: {data.get('error_message', 'Unknown')}\n"
        content += f"**영향 범위**: {data.get('impact', '확인 중')}\n\n"
        content += "조치 방안을 검토 중입니다."
        return content
    
    # === Friendly Style (Maria Silva - Frontend Lead) ===
    def _friendly_progress(self, data: Dict) -> str:
        greetings = ["안녕하세요!", "진행 상황 공유드려요!", "업데이트가 있어요!"]
        content = f"{random.choice(greetings)} 😊\n\n"
        
        content += f"지금 **{data.get('current_task', '작업')}** 진행 중이에요!\n"
        
        progress = data.get('progress', 0)
        if progress < 30:
            content += f"아직 초반이지만 열심히 하고 있어요! ({progress}%)\n"
        elif progress < 70:
            content += f"순조롭게 진행되고 있어요~ ({progress}%)\n"
        else:
            content += f"거의 다 왔어요! 조금만 더! ({progress}%)\n"
        
        return content
    
    def _friendly_completion(self, data: Dict) -> str:
        content = "### 🎉 완료했어요!\n\n"
        content += "다음 작업들을 마쳤어요:\n"
        
        for task in data.get('completed_tasks', []):
            content += f"- ✨ {task}\n"
        
        content += "\n잘 동작하는지 확인해보세요! 피드백 환영합니다 💪"
        return content
    
    def _friendly_error(self, data: Dict) -> str:
        content = "### 😅 앗, 문제가 생겼어요\n\n"
        content += f"이런 에러가 발생했어요: {data.get('error_message', '')}\n\n"
        content += "걱정 마세요! 금방 해결할 수 있을 거예요.\n"
        content += "도움이 필요하면 말씀해주세요!"
        return content
    
    # === Analytical Style (박민수 - QA Lead) ===
    def _analytical_progress(self, data: Dict) -> str:
        content = "### 진행 상황 분석\n\n"
        content += f"**작업명**: `{data.get('current_task', 'undefined')}`\n"
        content += f"**진행률**: {data.get('progress', 0)}% (정량적 측정)\n\n"
        
        content += "#### 메트릭스\n"
        content += f"- 예상 소요 시간: {data.get('estimated_time', 'N/A')}\n"
        content += f"- 실제 소요 시간: {data.get('actual_time', 'N/A')}\n"
        content += f"- 리스크 레벨: {data.get('risk_level', 'Low')}\n"
        
        return content
    
    def _analytical_completion(self, data: Dict) -> str:
        content = "### 완료 검증 보고\n\n"
        content += "#### 완료 항목\n"
        
        for i, task in enumerate(data.get('completed_tasks', []), 1):
            content += f"{i}. {task} ✓\n"
        
        content += "\n#### 품질 지표\n"
        content += f"- 테스트 커버리지: {data.get('coverage', 'N/A')}\n"
        content += f"- 코드 품질 점수: {data.get('quality_score', 'N/A')}\n"
        
        return content
    
    def _analytical_error(self, data: Dict) -> str:
        content = "### 오류 분석 보고\n\n"
        content += f"**오류 코드**: `{data.get('error_code', 'UNKNOWN')}`\n"
        content += f"**오류 메시지**: {data.get('error_message', '')}\n"
        content += f"**발생 위치**: {data.get('location', 'N/A')}\n\n"
        
        content += "#### 근본 원인 분석\n"
        content += f"- 직접 원인: {data.get('direct_cause', '분석 중')}\n"
        content += f"- 근본 원인: {data.get('root_cause', '조사 필요')}\n"
        
        return content
    
    # === Default Styles ===
    def _default_progress(self, data: Dict) -> str:
        return f"진행 중: {data.get('current_task', 'N/A')} ({data.get('progress', 0)}%)"
    
    def _default_completion(self, data: Dict) -> str:
        tasks = ', '.join(data.get('completed_tasks', []))
        return f"완료: {tasks}"
    
    def _default_error(self, data: Dict) -> str:
        return f"에러: {data.get('error_message', 'Unknown')}"
    
    def _default_summary(self, data: Dict) -> str:
        return f"요약: {data}"


# 사용 예시
if __name__ == "__main__":
    # 김정호 (신중하고 체계적인 백엔드 리드)
    backend_reporter = PersonaReporterAdapter('backend_lead_01')
    
    # Maria (친근하고 열정적인 프론트엔드 리드)
    frontend_reporter = PersonaReporterAdapter('frontend_lead_01')
    
    # 박민수 (분석적이고 꼼꼼한 QA 리드)
    qa_reporter = PersonaReporterAdapter('qa_lead_01')
    
    # 같은 데이터를 다른 스타일로 보고
    test_data = {
        'current_task': 'Golden Set 시스템 구현',
        'progress': 75,
        'details': {'설계': '완료', '구현': '진행 중'}
    }
    
    # 각 페르소나가 자기 스타일로 보고
    # backend_reporter.report_progress("82", test_data)  # 격식있게
    # frontend_reporter.report_progress("82", test_data)  # 친근하게
    # qa_reporter.report_progress("82", test_data)  # 분석적으로