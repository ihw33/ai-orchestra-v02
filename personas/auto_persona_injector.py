#!/usr/bin/env python3
"""
자동 페르소나 주입 시스템
이슈 생성 시 자동으로 페르소나를 할당하고 AI에게 주입
"""

import json
import subprocess
from typing import Dict, List
from personas.persona_loader import PersonaLoader, TeamBuilder
from pathlib import Path

class AutoPersonaInjector:
    """이슈 작업 시 자동으로 페르소나 주입"""
    
    def __init__(self):
        self.loader = PersonaLoader()
        self.team_builder = TeamBuilder(self.loader)
    
    def process_issue(self, issue_number: int, issue_title: str, issue_body: str) -> Dict:
        """
        이슈가 생성되면 자동으로:
        1. 작업 유형 분석
        2. 적절한 팀 구성
        3. 페르소나 할당
        4. AI 실행 명령 생성
        """
        
        print(f"\n🎯 Issue #{issue_number} 처리 시작: {issue_title}")
        
        # 1. 작업 유형 분석
        task_type = self._analyze_task_type(issue_title, issue_body)
        print(f"📌 작업 유형: {task_type}")
        
        # 2. 팀 구성 (긍정적/비판적 균형)
        team = self.team_builder.build_team(task_type, team_size=3)
        print(f"👥 할당된 팀: {team}")
        
        # 3. 각 팀원에게 역할 할당
        roles = self.team_builder.assign_roles(team, issue_title)
        
        # 4. AI별 실행 명령 생성
        commands = []
        for persona_id, role in roles.items():
            persona = self.loader.get_persona(persona_id)
            if persona:
                # 페르소나 기반 프롬프트 생성
                prompt = self.loader.generate_prompt(
                    persona_id, 
                    f"{role}\n원본 작업: {issue_title}",
                    {"issue_number": issue_number, "issue_body": issue_body}
                )
                
                # AI 실행 명령 생성
                ai_command = self._generate_ai_command(persona, prompt)
                commands.append({
                    "persona": persona['profile']['name'],
                    "role": role,
                    "command": ai_command
                })
                
                print(f"\n🤖 {persona['profile']['name']} ({persona_id})")
                print(f"   역할: {role}")
                print(f"   성격: {', '.join(persona['personality']['traits'][:3])}")
        
        return {
            "issue_number": issue_number,
            "task_type": task_type,
            "team": team,
            "commands": commands
        }
    
    def _analyze_task_type(self, title: str, body: str) -> str:
        """작업 유형 자동 분석"""
        text = f"{title} {body}".lower()
        
        if any(word in text for word in ["api", "backend", "서버", "데이터베이스"]):
            return "api_development"
        elif any(word in text for word in ["버그", "오류", "수정", "fix"]):
            return "bug_fix"
        elif any(word in text for word in ["ui", "프론트", "화면", "컴포넌트"]):
            return "frontend"
        elif any(word in text for word in ["아키텍처", "설계", "구조"]):
            return "architecture"
        else:
            return "general"
    
    def _generate_ai_command(self, persona: Dict, prompt: str) -> str:
        """AI별 실행 명령 생성"""
        # AI 도구 매핑 (예시)
        ai_mapping = {
            "backend_lead_01": "gemini",
            "frontend_lead_01": "claude",
            "qa_lead_01": "codex"
        }
        
        ai_tool = ai_mapping.get(persona['profile']['id'], "gemini")
        
        # 프롬프트를 파일로 저장 (너무 길어서)
        prompt_file = f"/tmp/persona_{persona['profile']['id']}_prompt.txt"
        with open(prompt_file, 'w', encoding='utf-8') as f:
            f.write(prompt)
        
        return f"{ai_tool} -p \"$(cat {prompt_file})\""
    
    def execute_with_personas(self, issue_data: Dict):
        """페르소나와 함께 AI 실행"""
        print("\n" + "="*50)
        print("🚀 AI 팀 작업 시작")
        print("="*50)
        
        results = []
        for cmd_data in issue_data['commands']:
            print(f"\n🎭 {cmd_data['persona']} 작업 중...")
            print(f"역할: {cmd_data['role']}")
            
            # 실제 AI 실행 (시뮬레이션)
            # result = subprocess.run(cmd_data['command'], shell=True, capture_output=True, text=True)
            # results.append(result.stdout)
            
            # 테스트용 출력
            print(f"명령: {cmd_data['command'][:100]}...")
        
        return results


class IssueWorkflowIntegration:
    """기존 워크플로우에 페르소나 자동 통합"""
    
    def __init__(self):
        self.persona_injector = AutoPersonaInjector()
    
    def on_issue_created(self, issue_number: int):
        """이슈 생성 시 자동 훅"""
        # GitHub에서 이슈 정보 가져오기
        cmd = f"gh issue view {issue_number} -R ihw33/ai-orchestra-v02 --json title,body"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        
        if result.returncode == 0:
            issue_data = json.loads(result.stdout)
            
            # 페르소나 자동 처리
            persona_data = self.persona_injector.process_issue(
                issue_number,
                issue_data['title'],
                issue_data['body']
            )
            
            # AI 실행
            self.persona_injector.execute_with_personas(persona_data)
            
            # 경험 업데이트
            self._update_experiences(persona_data)
    
    def _update_experiences(self, persona_data: Dict):
        """작업 완료 후 경험 자동 업데이트"""
        for member_id in persona_data['team']:
            project_data = {
                'issue_number': f"#{persona_data['issue_number']}",
                'role': '구현',
                'skills': ['Python', 'API'],
                'result': 'Success'
            }
            self.persona_injector.loader.update_experience(member_id, project_data)


def integrate_with_orchestrator():
    """unified_orchestrator.py와 통합"""
    integration_code = '''
# unified_orchestrator.py에 추가할 코드
from personas.auto_persona_injector import IssueWorkflowIntegration

class UnifiedOrchestrator:
    def __init__(self):
        # 기존 코드...
        self.persona_integration = IssueWorkflowIntegration()
    
    def process_issue(self, issue_number):
        # [AI] 태그가 있으면 페르소나 자동 적용
        if "[AI]" in issue_title:
            self.persona_integration.on_issue_created(issue_number)
        else:
            # 기존 처리 방식
            pass
'''
    
    print(integration_code)


if __name__ == "__main__":
    # 테스트
    print("🧪 페르소나 자동 주입 테스트")
    print("-" * 50)
    
    injector = AutoPersonaInjector()
    
    # 테스트 이슈
    test_issue = injector.process_issue(
        75,
        "[AI] 새로운 결제 API 구현",
        "결제 시스템을 마이크로서비스로 분리하고 API를 구현합니다."
    )
    
    print("\n📋 생성된 작업 계획:")
    print(json.dumps(test_issue, ensure_ascii=False, indent=2))
    
    print("\n✅ 통합 방법:")
    integrate_with_orchestrator()