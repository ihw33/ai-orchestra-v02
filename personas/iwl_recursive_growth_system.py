#!/usr/bin/env python3
"""
IWL 재귀 성장 시스템 (Recursive Growth System)
페르소나들이 작업을 통해 경험을 쌓고 스킬을 향상시키며, 
새로운 지식을 다른 페르소나들에게 전수하는 자기 진화 시스템
"""

import json
import logging
import math
import random
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Set


class RecursiveGrowthSystem:
    """재귀 성장 시스템"""
    
    def __init__(self):
        self.persona_dir = Path(__file__).parent / "iwl_team"
        self.growth_log_file = Path(__file__).parent.parent / "logs" / "persona_growth.log"
        self.growth_log_file.parent.mkdir(exist_ok=True)
        
        # 성장 설정
        self.growth_config = {
            'base_growth_rate': 0.1,
            'experience_multiplier': 1.5,
            'collaboration_bonus': 0.2,
            'teaching_bonus': 0.3,
            'max_skill_level': 10,
            'skill_transfer_rate': 0.7,
            'innovation_threshold': 8.0,
            'mentorship_threshold': 7.0
        }
        
        # 스킬 카테고리
        self.skill_categories = {
            'technical': ['react', 'nextjs', 'typescript', 'nodejs', 'python', 'api_design', 'database_design'],
            'ai_ml': ['machine_learning', 'llm_integration', 'ai_ethics', 'model_optimization', 'vector_databases'],
            'design': ['ui_ux_design', 'responsive_design', 'design_systems', 'user_research', 'prototyping'],
            'management': ['team_leadership', 'project_management', 'strategic_planning', 'decision_making'],
            'operations': ['devops', 'ci_cd', 'monitoring', 'security', 'performance_optimization'],
            'soft_skills': ['communication', 'collaboration', 'mentoring', 'problem_solving', 'creativity']
        }
        
        # 로깅 설정
        self.setup_logging()
    
    def setup_logging(self):
        """로깅 설정"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
        
        # 파일 핸들러 추가
        file_handler = logging.FileHandler(self.growth_log_file)
        file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        self.logger.addHandler(file_handler)
    
    def process_task_completion(self, persona_id: str, task_data: Dict, success_rate: float) -> Dict:
        """작업 완료 후 성장 처리"""
        try:
            persona = self.load_persona(persona_id)
            if not persona:
                return {'success': False, 'error': 'Persona not found'}
            
            # 1. 기본 경험치 및 스킬 성장
            growth_result = self.apply_basic_growth(persona, task_data, success_rate)
            
            # 2. 혁신 기회 탐지
            innovation_result = self.detect_innovation_opportunities(persona, task_data)
            
            # 3. 멘토십 기회 탐지
            mentorship_result = self.detect_mentorship_opportunities(persona)
            
            # 4. 지식 전수 처리
            knowledge_transfer_result = self.process_knowledge_transfer(persona, task_data)
            
            # 5. 새로운 스킬 학습 기회
            new_skills_result = self.discover_new_skills(persona, task_data)
            
            # 6. 페르소나 데이터 업데이트
            updated_persona = self.update_persona_data(
                persona, growth_result, innovation_result, 
                mentorship_result, knowledge_transfer_result, new_skills_result
            )
            
            # 7. 저장
            self.save_persona(updated_persona)
            
            # 8. 성장 로그 기록
            self.log_growth_event(persona_id, {
                'task': task_data,
                'growth_result': growth_result,
                'innovation_result': innovation_result,
                'mentorship_result': mentorship_result,
                'knowledge_transfer_result': knowledge_transfer_result,
                'new_skills_result': new_skills_result
            })
            
            return {
                'success': True,
                'persona_id': persona_id,
                'growth_summary': {
                    'growth_points_gained': growth_result.get('growth_points', 0),
                    'skills_improved': growth_result.get('skills_improved', []),
                    'innovations_discovered': innovation_result.get('innovations', []),
                    'mentorship_opportunities': mentorship_result.get('opportunities', []),
                    'knowledge_transferred': knowledge_transfer_result.get('transfers', []),
                    'new_skills_learned': new_skills_result.get('new_skills', [])
                }
            }
            
        except Exception as e:
            self.logger.error(f"작업 완료 성장 처리 실패 ({persona_id}): {e}")
            return {'success': False, 'error': str(e)}
    
    def apply_basic_growth(self, persona: Dict, task_data: Dict, success_rate: float) -> Dict:
        """기본 성장 적용"""
        try:
            growth_points = self.calculate_growth_points(task_data, success_rate)
            skills_improved = []
            
            # 작업과 관련된 스킬 식별
            relevant_skills = self.identify_relevant_skills(task_data, persona.get('skills', {}))
            
            # 스킬 성장 적용
            current_skills = persona.get('skills', {})
            
            for skill, relevance_score in relevant_skills.items():
                current_level = current_skills.get(skill, 0)
                
                if current_level < self.growth_config['max_skill_level']:
                    # 성장률 계산: 레벨이 높을수록 성장 속도 감소
                    growth_rate = self.growth_config['base_growth_rate'] * relevance_score
                    growth_rate *= (1 + success_rate) * self.growth_config['experience_multiplier']
                    growth_rate *= (1 - (current_level / self.growth_config['max_skill_level']) * 0.5)
                    
                    new_level = min(
                        self.growth_config['max_skill_level'],
                        current_level + growth_rate
                    )
                    
                    if new_level > current_level + 0.01:  # 의미있는 성장만 기록
                        current_skills[skill] = round(new_level, 2)
                        skills_improved.append({
                            'skill': skill,
                            'old_level': current_level,
                            'new_level': new_level,
                            'improvement': new_level - current_level
                        })
            
            persona['skills'] = current_skills
            
            return {
                'growth_points': growth_points,
                'skills_improved': skills_improved,
                'success_rate_factor': success_rate
            }
            
        except Exception as e:
            self.logger.error(f"기본 성장 적용 실패: {e}")
            return {'growth_points': 0, 'skills_improved': []}
    
    def detect_innovation_opportunities(self, persona: Dict, task_data: Dict) -> Dict:
        """혁신 기회 탐지"""
        try:
            innovations = []
            skills = persona.get('skills', {})
            
            # 고급 스킬 보유자의 혁신 가능성 체크
            advanced_skills = {k: v for k, v in skills.items() if v >= self.growth_config['innovation_threshold']}
            
            if advanced_skills:
                # 스킬 조합을 통한 혁신 탐지
                skill_combinations = self.generate_skill_combinations(advanced_skills, task_data)
                
                for combination in skill_combinations:
                    innovation_potential = self.calculate_innovation_potential(combination, task_data)
                    
                    if innovation_potential > 0.7:  # 높은 혁신 잠재력
                        innovation = {
                            'type': 'skill_synthesis',
                            'skills_involved': combination,
                            'potential': innovation_potential,
                            'description': self.generate_innovation_description(combination, task_data),
                            'discovered_at': datetime.now().isoformat()
                        }
                        innovations.append(innovation)
            
            # 문제 해결 과정에서의 혁신 탐지
            if task_data.get('complexity', 'medium') == 'high' and persona.get('level', 0) >= 8:
                problem_solving_innovation = self.detect_problem_solving_innovation(persona, task_data)
                if problem_solving_innovation:
                    innovations.append(problem_solving_innovation)
            
            return {'innovations': innovations}
            
        except Exception as e:
            self.logger.error(f"혁신 기회 탐지 실패: {e}")
            return {'innovations': []}
    
    def detect_mentorship_opportunities(self, persona: Dict) -> Dict:
        """멘토십 기회 탐지"""
        try:
            opportunities = []
            skills = persona.get('skills', {})
            
            # 멘토 자격이 있는 스킬 찾기
            mentoring_skills = {k: v for k, v in skills.items() if v >= self.growth_config['mentorship_threshold']}
            
            if mentoring_skills:
                # 다른 페르소나들과 비교하여 멘토링 기회 탐지
                all_personas = self.load_all_personas()
                
                for other_persona in all_personas:
                    if other_persona['id'] == persona['id']:
                        continue
                    
                    mentoring_match = self.find_mentoring_match(persona, other_persona, mentoring_skills)
                    if mentoring_match:
                        opportunities.append(mentoring_match)
            
            return {'opportunities': opportunities}
            
        except Exception as e:
            self.logger.error(f"멘토십 기회 탐지 실패: {e}")
            return {'opportunities': []}
    
    def process_knowledge_transfer(self, persona: Dict, task_data: Dict) -> Dict:
        """지식 전수 처리"""
        try:
            transfers = []
            
            # 협업한 페르소나들과의 지식 교환
            collaborators = task_data.get('collaborators', [])
            
            for collaborator_id in collaborators:
                collaborator = self.load_persona(collaborator_id)
                if not collaborator:
                    continue
                
                # 양방향 지식 전수
                transfer_to_collaborator = self.transfer_knowledge(persona, collaborator)
                transfer_from_collaborator = self.transfer_knowledge(collaborator, persona)
                
                if transfer_to_collaborator:
                    transfers.append(transfer_to_collaborator)
                    # 상대방 페르소나도 업데이트
                    self.apply_knowledge_transfer(collaborator, transfer_to_collaborator)
                    self.save_persona(collaborator)
                
                if transfer_from_collaborator:
                    # 현재 페르소나에 지식 적용
                    self.apply_knowledge_transfer(persona, transfer_from_collaborator)
                    transfers.append({
                        **transfer_from_collaborator,
                        'direction': 'received'
                    })
            
            return {'transfers': transfers}
            
        except Exception as e:
            self.logger.error(f"지식 전수 처리 실패: {e}")
            return {'transfers': []}
    
    def discover_new_skills(self, persona: Dict, task_data: Dict) -> Dict:
        """새로운 스킬 발견"""
        try:
            new_skills = []
            current_skills = set(persona.get('skills', {}).keys())
            
            # 작업 컨텍스트에서 새로운 스킬 요구사항 탐지
            required_skills = self.analyze_skill_requirements(task_data)
            
            for skill_requirement in required_skills:
                skill_name = skill_requirement['skill']
                
                if skill_name not in current_skills:
                    # 새로운 스킬 학습 조건 체크
                    learning_feasibility = self.assess_learning_feasibility(
                        persona, skill_name, skill_requirement
                    )
                    
                    if learning_feasibility['feasible']:
                        initial_level = learning_feasibility['initial_level']
                        persona['skills'][skill_name] = initial_level
                        
                        new_skills.append({
                            'skill': skill_name,
                            'initial_level': initial_level,
                            'learning_source': skill_requirement['source'],
                            'feasibility_score': learning_feasibility['score'],
                            'learned_at': datetime.now().isoformat()
                        })
            
            # 관련 스킬 기반 새로운 스킬 추천
            recommended_skills = self.recommend_related_skills(persona)
            for recommendation in recommended_skills:
                if recommendation['skill'] not in current_skills:
                    if random.random() < recommendation['probability']:
                        initial_level = recommendation['initial_level']
                        persona['skills'][recommendation['skill']] = initial_level
                        
                        new_skills.append({
                            'skill': recommendation['skill'],
                            'initial_level': initial_level,
                            'learning_source': 'skill_correlation',
                            'probability': recommendation['probability'],
                            'learned_at': datetime.now().isoformat()
                        })
            
            return {'new_skills': new_skills}
            
        except Exception as e:
            self.logger.error(f"새로운 스킬 발견 실패: {e}")
            return {'new_skills': []}
    
    def update_persona_data(self, persona: Dict, *growth_results) -> Dict:
        """페르소나 데이터 통합 업데이트"""
        try:
            # 성장 포인트 합산
            total_growth_points = sum(
                result.get('growth_points', 0) for result in growth_results 
                if isinstance(result, dict)
            )
            
            persona['growth_points'] = persona.get('growth_points', 0) + total_growth_points
            
            # 레벨 업 체크
            new_level = self.calculate_level_from_growth_points(persona['growth_points'])
            if new_level > persona.get('level', 1):
                persona['level'] = new_level
                self.logger.info(f"🎉 {persona['name']} leveled up to {new_level}!")
            
            # 메타데이터 업데이트
            persona['last_growth_update'] = datetime.now().isoformat()
            persona['updated_at'] = datetime.now().isoformat()
            
            # 성장 히스토리 추가
            if 'growth_history' not in persona:
                persona['growth_history'] = []
            
            persona['growth_history'].append({
                'growth_points': total_growth_points,
                'level': persona['level'],
                'timestamp': datetime.now().isoformat(),
                'growth_details': [
                    result for result in growth_results 
                    if isinstance(result, dict) and result
                ]
            })
            
            # 히스토리 크기 제한 (최근 50개만 유지)
            if len(persona['growth_history']) > 50:
                persona['growth_history'] = persona['growth_history'][-50:]
            
            return persona
            
        except Exception as e:
            self.logger.error(f"페르소나 데이터 업데이트 실패: {e}")
            return persona
    
    # 헬퍼 메서드들
    
    def calculate_growth_points(self, task_data: Dict, success_rate: float) -> int:
        """성장 포인트 계산"""
        base_points = 10
        
        # 작업 복잡도에 따른 보너스
        complexity_bonus = {
            'low': 5,
            'medium': 10,
            'high': 20
        }.get(task_data.get('complexity', 'medium'), 10)
        
        # 성공률에 따른 보너스
        success_bonus = int(success_rate * 15)
        
        # 추정 시간에 따른 보너스
        time_bonus = min(task_data.get('estimated_hours', 8), 24)
        
        return base_points + complexity_bonus + success_bonus + time_bonus
    
    def identify_relevant_skills(self, task_data: Dict, current_skills: Dict) -> Dict:
        """작업과 관련된 스킬 식별 및 관련성 점수 계산"""
        task_description = f"{task_data.get('name', '')} {task_data.get('description', '')}".lower()
        
        relevant_skills = {}
        
        # 키워드 매칭을 통한 관련성 점수 계산
        skill_keywords = {
            'react': ['react', 'component', 'jsx', 'frontend'],
            'nextjs': ['next', 'nextjs', 'ssr', 'routing'],
            'typescript': ['typescript', 'ts', 'type', 'interface'],
            'api_design': ['api', 'endpoint', 'rest', 'graphql'],
            'database_design': ['database', 'db', 'schema', 'sql'],
            'machine_learning': ['ml', 'ai', 'model', 'algorithm'],
            'ui_ux_design': ['ui', 'ux', 'design', 'interface'],
            'team_leadership': ['lead', 'manage', 'coordinate', 'mentor'],
            'testing': ['test', 'qa', 'quality', 'validation'],
            'security': ['security', 'auth', 'secure', 'vulnerability']
        }
        
        for skill, keywords in skill_keywords.items():
            if skill in current_skills:
                relevance_score = sum(1 for keyword in keywords if keyword in task_description)
                if relevance_score > 0:
                    relevant_skills[skill] = min(1.0, relevance_score / len(keywords))
        
        return relevant_skills
    
    def generate_skill_combinations(self, advanced_skills: Dict, task_data: Dict) -> List[List[str]]:
        """고급 스킬 조합 생성"""
        skills_list = list(advanced_skills.keys())
        combinations = []
        
        # 2-3개 스킬 조합 생성
        for i in range(len(skills_list)):
            for j in range(i + 1, len(skills_list)):
                combinations.append([skills_list[i], skills_list[j]])
                
                for k in range(j + 1, len(skills_list)):
                    combinations.append([skills_list[i], skills_list[j], skills_list[k]])
        
        return combinations[:10]  # 최대 10개 조합만
    
    def calculate_innovation_potential(self, skill_combination: List[str], task_data: Dict) -> float:
        """혁신 잠재력 계산"""
        # 스킬 다양성 점수
        diversity_score = len(set(self.get_skill_categories(skill_combination))) / len(self.skill_categories)
        
        # 작업 복잡도와의 매칭
        complexity_match = {
            'low': 0.3,
            'medium': 0.6,
            'high': 1.0
        }.get(task_data.get('complexity', 'medium'), 0.6)
        
        # 무작위 요소 (창의성 모방)
        creativity_factor = random.uniform(0.5, 1.0)
        
        return (diversity_score * 0.4 + complexity_match * 0.4 + creativity_factor * 0.2)
    
    def get_skill_categories(self, skills: List[str]) -> List[str]:
        """스킬들의 카테고리 반환"""
        categories = []
        for skill in skills:
            for category, category_skills in self.skill_categories.items():
                if skill in category_skills:
                    categories.append(category)
                    break
        return categories
    
    def generate_innovation_description(self, skill_combination: List[str], task_data: Dict) -> str:
        """혁신 설명 생성"""
        categories = self.get_skill_categories(skill_combination)
        task_type = task_data.get('type', 'development')
        
        return f"Innovative {task_type} approach combining {', '.join(categories)} expertise through {', '.join(skill_combination)} skills"
    
    def load_persona(self, persona_id: str) -> Optional[Dict]:
        """페르소나 데이터 로드"""
        try:
            for dept_dir in self.persona_dir.iterdir():
                if dept_dir.is_dir():
                    for file in dept_dir.glob("*.json"):
                        with open(file, 'r', encoding='utf-8') as f:
                            persona = json.load(f)
                            if persona.get('id') == persona_id:
                                persona['_file_path'] = str(file)
                                return persona
            return None
            
        except Exception as e:
            self.logger.error(f"페르소나 로드 실패 ({persona_id}): {e}")
            return None
    
    def load_all_personas(self) -> List[Dict]:
        """모든 페르소나 로드"""
        try:
            personas = []
            for dept_dir in self.persona_dir.iterdir():
                if dept_dir.is_dir():
                    for file in dept_dir.glob("*.json"):
                        with open(file, 'r', encoding='utf-8') as f:
                            persona = json.load(f)
                            persona['_file_path'] = str(file)
                            personas.append(persona)
            return personas
            
        except Exception as e:
            self.logger.error(f"모든 페르소나 로드 실패: {e}")
            return []
    
    def save_persona(self, persona: Dict):
        """페르소나 데이터 저장"""
        try:
            file_path = persona.get('_file_path')
            if file_path and Path(file_path).exists():
                # _file_path는 저장하지 않음
                save_data = {k: v for k, v in persona.items() if k != '_file_path'}
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(save_data, f, ensure_ascii=False, indent=2)
            else:
                self.logger.warning(f"페르소나 파일 경로를 찾을 수 없습니다: {persona.get('id')}")
                
        except Exception as e:
            self.logger.error(f"페르소나 저장 실패 ({persona.get('id')}): {e}")
    
    def calculate_level_from_growth_points(self, growth_points: int) -> int:
        """성장 포인트로부터 레벨 계산"""
        # 지수적 성장 곡선: level = log2(growth_points / 100) + 1
        if growth_points < 100:
            return 1
        
        level = int(math.log2(growth_points / 100)) + 1
        return min(level, 15)  # 최대 레벨 15
    
    def log_growth_event(self, persona_id: str, growth_data: Dict):
        """성장 이벤트 로깅"""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'persona_id': persona_id,
            'event_type': 'growth_processing',
            'data': growth_data
        }
        
        self.logger.info(f"Growth processed for {persona_id}: {json.dumps(log_entry, ensure_ascii=False)}")
    
    # 추가 헬퍼 메서드들 (간소화된 구현)
    
    def detect_problem_solving_innovation(self, persona: Dict, task_data: Dict) -> Optional[Dict]:
        """문제 해결 혁신 탐지"""
        if random.random() < 0.1:  # 10% 확률로 혁신 발견
            return {
                'type': 'problem_solving',
                'description': f"Innovative solution approach for {task_data.get('name', 'complex task')}",
                'potential': random.uniform(0.7, 0.95),
                'discovered_at': datetime.now().isoformat()
            }
        return None
    
    def find_mentoring_match(self, mentor: Dict, mentee: Dict, mentoring_skills: Dict) -> Optional[Dict]:
        """멘토링 매치 찾기"""
        mentee_skills = mentee.get('skills', {})
        
        for skill, mentor_level in mentoring_skills.items():
            mentee_level = mentee_skills.get(skill, 0)
            
            if mentor_level - mentee_level >= 2:  # 2레벨 이상 차이
                return {
                    'mentee_id': mentee['id'],
                    'mentee_name': mentee['name'],
                    'skill': skill,
                    'mentor_level': mentor_level,
                    'mentee_level': mentee_level,
                    'potential_improvement': min(2.0, mentor_level - mentee_level) * 0.3
                }
        
        return None
    
    def transfer_knowledge(self, source: Dict, target: Dict) -> Optional[Dict]:
        """지식 전수"""
        source_skills = source.get('skills', {})
        target_skills = target.get('skills', {})
        
        transferable_knowledge = []
        
        for skill, source_level in source_skills.items():
            target_level = target_skills.get(skill, 0)
            
            if source_level > target_level + 1:
                transfer_amount = min(
                    self.growth_config['skill_transfer_rate'],
                    (source_level - target_level) * 0.2
                )
                
                transferable_knowledge.append({
                    'skill': skill,
                    'transfer_amount': transfer_amount,
                    'from_level': source_level,
                    'to_level': target_level
                })
        
        if transferable_knowledge:
            return {
                'from_persona': source['id'],
                'to_persona': target['id'],
                'knowledge': transferable_knowledge,
                'transfer_date': datetime.now().isoformat()
            }
        
        return None
    
    def apply_knowledge_transfer(self, persona: Dict, transfer_data: Dict):
        """지식 전수 적용"""
        skills = persona.get('skills', {})
        
        for knowledge in transfer_data.get('knowledge', []):
            skill = knowledge['skill']
            transfer_amount = knowledge['transfer_amount']
            
            current_level = skills.get(skill, 0)
            new_level = min(
                self.growth_config['max_skill_level'],
                current_level + transfer_amount
            )
            
            skills[skill] = new_level
        
        persona['skills'] = skills
    
    def analyze_skill_requirements(self, task_data: Dict) -> List[Dict]:
        """작업의 스킬 요구사항 분석"""
        # 간소화된 구현
        task_type = task_data.get('type', 'development')
        
        requirements = []
        if 'ai' in task_data.get('name', '').lower():
            requirements.append({
                'skill': 'ai_integration',
                'source': 'task_requirement',
                'importance': 0.8
            })
        
        if 'test' in task_data.get('name', '').lower():
            requirements.append({
                'skill': 'automated_testing',
                'source': 'task_requirement',
                'importance': 0.7
            })
        
        return requirements
    
    def assess_learning_feasibility(self, persona: Dict, skill_name: str, requirement: Dict) -> Dict:
        """스킬 학습 가능성 평가"""
        current_skills = persona.get('skills', {})
        level = persona.get('level', 1)
        
        # 관련 스킬 보유 여부 체크
        related_skills = self.find_related_skills(skill_name, current_skills)
        
        if related_skills:
            feasible = True
            initial_level = min(2.0, sum(related_skills.values()) / len(related_skills) * 0.3)
            score = 0.8
        elif level >= 5:  # 고레벨 페르소나는 새 스킬 습득 가능
            feasible = True
            initial_level = 1.0
            score = 0.6
        else:
            feasible = False
            initial_level = 0.0
            score = 0.2
        
        return {
            'feasible': feasible,
            'initial_level': initial_level,
            'score': score,
            'related_skills': related_skills
        }
    
    def find_related_skills(self, target_skill: str, current_skills: Dict) -> Dict:
        """관련 스킬 찾기"""
        related = {}
        
        # 같은 카테고리의 스킬들 찾기
        target_category = None
        for category, skills in self.skill_categories.items():
            if target_skill in skills:
                target_category = category
                break
        
        if target_category:
            category_skills = self.skill_categories[target_category]
            for skill in category_skills:
                if skill in current_skills:
                    related[skill] = current_skills[skill]
        
        return related
    
    def recommend_related_skills(self, persona: Dict) -> List[Dict]:
        """관련 스킬 추천"""
        current_skills = persona.get('skills', {})
        recommendations = []
        
        # 각 카테고리에서 강한 스킬이 있으면 같은 카테고리의 다른 스킬 추천
        for category, skills in self.skill_categories.items():
            category_levels = [current_skills.get(skill, 0) for skill in skills if skill in current_skills]
            
            if category_levels and max(category_levels) >= 6:  # 카테고리에서 고급 스킬 보유
                for skill in skills:
                    if skill not in current_skills:
                        probability = min(0.3, max(category_levels) / 10)
                        initial_level = max(category_levels) * 0.2
                        
                        recommendations.append({
                            'skill': skill,
                            'category': category,
                            'probability': probability,
                            'initial_level': initial_level,
                            'reason': 'category_expertise'
                        })
        
        return recommendations


def main():
    """테스트 및 데모"""
    import argparse
    
    parser = argparse.ArgumentParser(description='IWL Recursive Growth System')
    parser.add_argument('--test-persona', help='테스트할 페르소나 ID')
    parser.add_argument('--simulate-growth', action='store_true', help='성장 시뮬레이션 실행')
    
    args = parser.parse_args()
    
    growth_system = RecursiveGrowthSystem()
    
    if args.test_persona:
        # 테스트 작업 데이터
        test_task = {
            'name': 'AI Integration Enhancement',
            'description': 'Implement advanced AI features with React components',
            'type': 'development',
            'complexity': 'high',
            'estimated_hours': 16,
            'collaborators': ['iwl_cto_001']
        }
        
        result = growth_system.process_task_completion(args.test_persona, test_task, 0.9)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        
    elif args.simulate_growth:
        # 전체 팀 성장 시뮬레이션
        all_personas = growth_system.load_all_personas()
        print(f"Found {len(all_personas)} personas")
        
        for persona in all_personas[:3]:  # 처음 3명만 테스트
            test_task = {
                'name': f'Skill Development Task for {persona["name"]}',
                'description': 'Practice and improve existing skills',
                'type': 'development',
                'complexity': 'medium',
                'estimated_hours': 8,
                'collaborators': []
            }
            
            result = growth_system.process_task_completion(persona['id'], test_task, 0.85)
            if result['success']:
                print(f"✅ Growth processed for {persona['name']}")
                print(f"   Growth points gained: {result['growth_summary']['growth_points_gained']}")
                print(f"   Skills improved: {len(result['growth_summary']['skills_improved'])}")
            else:
                print(f"❌ Growth processing failed for {persona['name']}: {result['error']}")


if __name__ == "__main__":
    main()