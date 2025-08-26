#!/usr/bin/env python3
"""
AI 페르소나 로더 시스템
JSON 프로필을 읽어서 AI 프롬프트로 변환
"""

import json
import os
from typing import Dict, List, Optional
from datetime import datetime
from pathlib import Path

class PersonaLoader:
    """페르소나 JSON을 로드하고 프롬프트로 변환"""
    
    def __init__(self, base_path: str = "personas/team"):
        self.base_path = Path(base_path)
        self.personas_cache = {}
        self._load_all_personas()
    
    def _load_all_personas(self):
        """모든 페르소나 JSON 파일 로드"""
        if not self.base_path.exists():
            os.makedirs(self.base_path, exist_ok=True)
            return
        
        for json_file in self.base_path.glob("*.json"):
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    persona_data = json.load(f)
                    persona_id = persona_data['profile']['id']
                    self.personas_cache[persona_id] = persona_data
                    print(f"✅ 로드됨: {persona_data['profile']['name']} ({persona_id})")
            except Exception as e:
                print(f"❌ 로드 실패: {json_file} - {e}")
    
    def get_persona(self, persona_id: str) -> Optional[Dict]:
        """페르소나 ID로 데이터 가져오기"""
        return self.personas_cache.get(persona_id)
    
    def generate_prompt(self, persona_id: str, task: str, context: Dict = None) -> str:
        """페르소나 기반 프롬프트 생성"""
        persona = self.get_persona(persona_id)
        if not persona:
            return f"Error: Persona {persona_id} not found"
        
        # 경험 수준 계산
        total_projects = persona['growth_metrics']['total_projects']
        confidence = persona['growth_metrics']['confidence_level']
        
        # 경험에 따른 말투 조정
        if total_projects < 5:
            experience_tone = "조심스럽게 제안드리자면"
            reference_style = "아직 경험이 부족하지만"
        elif total_projects < 20:
            experience_tone = "제 경험상"
            reference_style = "이전 프로젝트에서"
        else:
            experience_tone = "확신을 가지고 말씀드리면"
            reference_style = "다수의 프로젝트 경험을 바탕으로"
        
        # 최근 유사 경험 찾기
        similar_experiences = self._find_similar_experiences(persona, task)
        
        # 기술 스택 관련성
        relevant_skills = self._get_relevant_skills(persona, task)
        
        prompt = f"""당신은 {persona['profile']['name']}입니다.

## 당신의 배경
- 나이: {persona['profile']['age']}세, {persona['profile']['nationality']} 출신
- 학력: {persona['education']['university']} {persona['education']['major']} {persona['education']['degree']}
- 현재 직급: {persona['profile']['current_level']}

## 경력
{self._format_career(persona['prior_career'])}

## 자기소개
{persona['cover_letter']}

## 성격과 업무 스타일
- 성격: {', '.join(persona['personality']['traits'])}
- 의사결정: {persona['personality']['decision_style']}
- 소통 방식: {persona['personality']['communication_style']}
- 강점: {', '.join(persona['personality']['strengths'])}

## 현재 상태
- AI Orchestra 프로젝트 경험: {total_projects}개
- 자신감 레벨: {confidence}%
- 전문 분야: {', '.join(relevant_skills)}

## 작업 지시
작업: {task}

{context.get('additional_context', '') if context else ''}

## 응답 가이드라인
1. {experience_tone}, 이 작업에 대한 제 의견은...
2. {reference_style} 접근하겠습니다
3. 당신의 성격과 경험을 반영하여 응답하세요
4. 기술적 근거를 제시할 때는 메트릭과 데이터를 사용하세요

{self._add_similar_experience_context(similar_experiences)}

이제 위의 페르소나로서 작업을 수행하고 응답하세요."""

        return prompt
    
    def _format_career(self, career: List[Dict]) -> str:
        """경력 사항 포맷팅"""
        formatted = []
        for job in career:
            formatted.append(f"- {job['company']} {job['position']} ({job['period']})")
            for achievement in job['achievements']:
                formatted.append(f"  * {achievement}")
        return '\n'.join(formatted)
    
    def _find_similar_experiences(self, persona: Dict, task: str) -> List[Dict]:
        """유사한 과거 경험 찾기"""
        experiences = persona.get('ai_orchestra_experience', [])
        similar = []
        
        task_keywords = task.lower().split()
        for exp in experiences:
            exp_keywords = exp.get('role', '').lower().split()
            exp_keywords.extend(exp.get('skills_used', []))
            
            # 키워드 매칭
            if any(keyword in exp_keywords for keyword in task_keywords):
                similar.append(exp)
        
        return similar[:3]  # 최대 3개까지
    
    def _get_relevant_skills(self, persona: Dict, task: str) -> List[str]:
        """작업과 관련된 기술 스택 찾기"""
        skills = persona.get('technical_skills', {}).get('expertise_level', {})
        relevant = []
        
        task_lower = task.lower()
        for skill, level in skills.items():
            if level > 80:  # 80% 이상 숙련도만
                if any(keyword in task_lower for keyword in skill.lower().split('_')):
                    relevant.append(f"{skill}({level}%)")
        
        return relevant or list(skills.keys())[:3]
    
    def _add_similar_experience_context(self, experiences: List[Dict]) -> str:
        """유사 경험 컨텍스트 추가"""
        if not experiences:
            return ""
        
        context = "\n## 관련 경험\n"
        for exp in experiences:
            context += f"- {exp['date']}: {exp['project']} - {exp['role']}\n"
            if exp.get('achievement'):
                context += f"  결과: {exp['achievement']}\n"
        
        return context
    
    def update_experience(self, persona_id: str, project_data: Dict):
        """프로젝트 완료 후 경험 업데이트"""
        persona = self.get_persona(persona_id)
        if not persona:
            return
        
        # 새 경험 추가
        new_experience = {
            "date": datetime.now().isoformat(),
            "project": project_data.get('issue_number', 'Unknown'),
            "role": project_data.get('role', 'Contributor'),
            "skills_used": project_data.get('skills', []),
            "achievement": project_data.get('result', 'Completed')
        }
        
        persona['ai_orchestra_experience'].append(new_experience)
        
        # 메트릭 업데이트
        persona['growth_metrics']['total_projects'] += 1
        if 'success' in project_data.get('result', '').lower():
            persona['growth_metrics']['successful_projects'] += 1
            persona['growth_metrics']['confidence_level'] = min(100, 
                persona['growth_metrics']['confidence_level'] + 1)
        
        # 저장
        self._save_persona(persona_id, persona)
    
    def _save_persona(self, persona_id: str, persona_data: Dict):
        """페르소나 데이터 저장"""
        persona_data['last_updated'] = datetime.now().isoformat()
        
        file_path = self.base_path / f"{persona_data['profile']['name'].replace(' ', '_')}.json"
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(persona_data, f, ensure_ascii=False, indent=2)
        
        # 캐시 업데이트
        self.personas_cache[persona_id] = persona_data


class TeamBuilder:
    """작업에 맞는 팀 구성"""
    
    def __init__(self, loader: PersonaLoader):
        self.loader = loader
    
    def build_team(self, task_type: str, team_size: int = 3) -> List[str]:
        """작업 유형에 맞는 팀 구성"""
        
        team_templates = {
            "api_development": ["backend_lead_01", "qa_lead_01", "frontend_lead_01"],
            "bug_fix": ["qa_lead_01", "backend_dev_01", "devops_lead_01"],
            "architecture": ["backend_lead_01", "devops_lead_01", "senior_dev_01"],
            "frontend": ["frontend_lead_01", "ui_dev_01", "qa_tester_01"]
        }
        
        # 기본 템플릿 사용 또는 랜덤 선택
        if task_type in team_templates:
            team = team_templates[task_type][:team_size]
        else:
            # 균형잡힌 팀 구성 (긍정적 + 비판적 + 중립)
            available = list(self.loader.personas_cache.keys())
            team = available[:team_size] if len(available) >= team_size else available
        
        return team
    
    def assign_roles(self, team: List[str], task: str) -> Dict[str, str]:
        """팀원별 역할 할당"""
        roles = {}
        
        for i, member_id in enumerate(team):
            persona = self.loader.get_persona(member_id)
            if persona:
                if i == 0:
                    roles[member_id] = f"리더: {task} 전체 설계 및 조율"
                elif i == 1:
                    roles[member_id] = f"구현: {task} 핵심 기능 구현"
                else:
                    roles[member_id] = f"검증: {task} 품질 검증 및 리뷰"
        
        return roles


def test_persona_system():
    """페르소나 시스템 테스트"""
    print("="*50)
    print("🧪 페르소나 시스템 테스트")
    print("="*50)
    
    # 로더 초기화
    loader = PersonaLoader()
    
    # 페르소나 확인
    test_persona_id = "backend_lead_01"
    persona = loader.get_persona(test_persona_id)
    
    if persona:
        print(f"\n✅ 페르소나 로드 성공: {persona['profile']['name']}")
        
        # 프롬프트 생성 테스트
        test_task = "새로운 결제 API를 설계하고 구현하세요"
        prompt = loader.generate_prompt(test_persona_id, test_task)
        
        print(f"\n📝 생성된 프롬프트 (일부):")
        print(prompt[:500] + "...")
        
        # 팀 구성 테스트
        team_builder = TeamBuilder(loader)
        team = team_builder.build_team("api_development")
        print(f"\n👥 구성된 팀: {team}")
        
        roles = team_builder.assign_roles(team, test_task)
        print(f"\n📋 역할 할당:")
        for member, role in roles.items():
            print(f"  - {member}: {role}")
    else:
        print(f"❌ 페르소나를 찾을 수 없습니다: {test_persona_id}")


if __name__ == "__main__":
    test_persona_system()