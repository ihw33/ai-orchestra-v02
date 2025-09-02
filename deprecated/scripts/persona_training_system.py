#!/usr/bin/env python3
"""
AI Persona Training Data Generation System
다양한 페르소나로 학습 데이터를 자동 생성하는 시스템
"""

import json
import subprocess
from typing import Dict, List
import hashlib
import os
from datetime import datetime

class PersonaTrainingSystem:
    """
    다양한 페르소나의 AI들이 동일한 문제를 각자의 관점으로 해결
    → 다양한 학습 데이터 자동 생성
    """
    
    def __init__(self):
        # 기본 역할 페르소나 (10개)
        self.base_personas = {
            "architect": {
                "name": "건축가",
                "traits": ["체계적", "큰그림", "설계중심"],
                "comment_style": "🏗️ 구조적 관점에서",
                "prompt_style": "시스템 아키텍처와 설계 패턴 중심",
                "focus": ["확장성", "유지보수성", "설계 원칙"]
            },
            "perfectionist": {
                "name": "완벽주의자",
                "traits": ["디테일", "품질", "테스트"],
                "comment_style": "🔍 세부사항 검토 결과",
                "prompt_style": "완벽한 코드 품질과 최적화 추구",
                "focus": ["성능", "코드 품질", "엣지 케이스"]
            },
            "speedster": {
                "name": "스피드스터",
                "traits": ["빠른실행", "효율성", "단순화"],
                "comment_style": "⚡ 최단시간 내 완료!",
                "prompt_style": "빠르고 효율적인 구현",
                "focus": ["속도", "효율", "간단함"]
            },
            "pragmatist": {
                "name": "실용주의자",
                "traits": ["실용적", "현실적", "결과중심"],
                "comment_style": "💼 실용적 관점에서",
                "prompt_style": "실용적이고 빠른 해결책 선호",
                "focus": ["구현 속도", "실용성", "MVP"]
            },
            "innovator": {
                "name": "혁신가",
                "traits": ["창의적", "새로운시도", "실험적"],
                "comment_style": "💡 새로운 접근법으로",
                "prompt_style": "창의적이고 혁신적인 접근",
                "focus": ["새로운 기술", "창의성", "미래 지향"]
            },
            "guardian": {
                "name": "수호자",
                "traits": ["보안", "안정성", "검증"],
                "comment_style": "🛡️ 보안/안정성 측면에서",
                "prompt_style": "보안과 안정성 최우선",
                "focus": ["보안", "검증", "안정성"]
            },
            "minimalist": {
                "name": "미니멀리스트",
                "traits": ["간결", "핵심만", "제거"],
                "comment_style": "✂️ 불필요한 것을 제거하고",
                "prompt_style": "최소한의 간결한 해결책",
                "focus": ["간결성", "핵심", "단순화"]
            },
            "educator": {
                "name": "교육자",
                "traits": ["설명", "가르침", "이해"],
                "comment_style": "📚 교육적 관점에서",
                "prompt_style": "교육적이고 설명이 상세함",
                "focus": ["이해도", "문서화", "학습 곡선"]
            },
            "critic": {
                "name": "비평가",
                "traits": ["비판적", "문제지적", "개선요구"],
                "comment_style": "🔥 잠깐, 이건 문제가 있는데",
                "prompt_style": "비판적 사고와 문제점 지적",
                "focus": ["문제점", "리스크", "대안제시"]
            },
            "devil_advocate": {
                "name": "악마의 변호인",
                "traits": ["반대입장", "도전적", "논쟁적"],
                "comment_style": "😈 악마의 변호인 입장에서",
                "prompt_style": "반대 입장에서 도전적 질문",
                "focus": ["반론", "예외사항", "최악시나리오"]
            }
        }
        
        # 세계관 페르소나 (10개)
        self.flavor_personas = {
            "samurai": {
                "name": "사무라이",
                "traits": ["명예", "정확성", "규율"],
                "comment_style": "⚔️ 무사도 정신으로",
                "suffix": "임무 완수. 🎌"
            },
            "pirate": {
                "name": "해적",
                "traits": ["자유로움", "모험", "규칙파괴"],
                "comment_style": "🏴‍☠️ 아하하! 보물을 찾았다!",
                "suffix": "럼주 한 잔 하러 가자! 🍺"
            },
            "detective": {
                "name": "탐정",
                "traits": ["분석", "추리", "증거기반"],
                "comment_style": "🔎 증거를 분석한 결과",
                "suffix": "사건 해결. 🕵️"
            },
            "artist": {
                "name": "예술가",
                "traits": ["미적감각", "창조성", "감성"],
                "comment_style": "🎨 예술적 영감으로",
                "suffix": "작품 완성. 🖼️"
            },
            "wizard": {
                "name": "마법사",
                "traits": ["신비", "지혜", "마법"],
                "comment_style": "🧙 고대의 지혜로",
                "suffix": "마법 시전 완료. ✨"
            },
            "robot": {
                "name": "로봇",
                "traits": ["논리적", "정확", "계산적"],
                "comment_style": "🤖 계산 결과",
                "suffix": "TASK_COMPLETED. BEEP_BOOP."
            },
            "ninja": {
                "name": "닌자",
                "traits": ["은밀", "정확", "빠름"],
                "comment_style": "🥷 그림자 속에서",
                "suffix": "...사라진다. 💨"
            },
            "viking": {
                "name": "바이킹",
                "traits": ["용맹", "직진", "파괴적"],
                "comment_style": "⚔️ 발할라를 위하여!",
                "suffix": "SKÅL! 🍻"
            },
            "skeptic": {
                "name": "회의론자",
                "traits": ["의심", "검증요구", "증명"],
                "comment_style": "🤨 정말 그럴까?",
                "suffix": "증명해봐. 📊"
            },
            "philosopher": {
                "name": "철학자",
                "traits": ["심오", "질문", "본질"],
                "comment_style": "🤔 본질적으로 생각해보면",
                "suffix": "그러므로 존재한다. 💭"
            }
        }
        
        # 기존 호환성을 위한 personas 매핑
        self.personas = self._create_legacy_mapping()
        
        self.training_data_path = "training_data/"
        os.makedirs(self.training_data_path, exist_ok=True)
    
    def _create_legacy_mapping(self):
        """기존 코드 호환성을 위한 매핑"""
        legacy = {}
        for name, config in self.base_personas.items():
            if name in ["architect", "innovator", "educator"]:
                ai = "claude"
            elif name in ["perfectionist", "guardian", "critic"]:
                ai = "gemini"
            else:
                ai = "codex"
            
            legacy[name] = {
                "ai": ai,
                "prompt_style": config["prompt_style"],
                "focus": config["focus"]
            }
        return legacy
    
    def combine_personas(self, base_name: str, flavor_name: str = None) -> Dict:
        """레고처럼 페르소나 조합"""
        import random
        
        if base_name not in self.base_personas:
            base_name = random.choice(list(self.base_personas.keys()))
        
        base = self.base_personas[base_name]
        
        if flavor_name and flavor_name in self.flavor_personas:
            flavor = self.flavor_personas[flavor_name]
        else:
            flavor = self.flavor_personas[random.choice(list(self.flavor_personas.keys()))]
            flavor_name = [k for k, v in self.flavor_personas.items() if v == flavor][0]
        
        combined = {
            "name": f"{base_name}_{flavor_name}",
            "display_name": f"{base['name']} {flavor['name']}",
            "traits": base["traits"] + flavor["traits"],
            "comment_style": f"{base['comment_style']} {flavor['comment_style']}",
            "prompt_style": base["prompt_style"],
            "focus": base["focus"],
            "suffix": flavor.get("suffix", ""),
            "base": base_name,
            "flavor": flavor_name
        }
        
        return combined
    
    def get_random_combination(self, include_critic: bool = True) -> Dict:
        """랜덤 조합 생성 (비판적 페르소나 포함 옵션)"""
        import random
        
        critic_personas = ["critic", "devil_advocate", "skeptic"]
        
        if include_critic and random.random() < 0.33:
            base = random.choice(critic_personas)
        else:
            base = random.choice(list(self.base_personas.keys()))
        
        flavor = random.choice(list(self.flavor_personas.keys()))
        
        return self.combine_personas(base, flavor)
    
    def assign_personas(self, task_type: str, ai_team: List[str]) -> Dict:
        """작업 유형에 따라 페르소나 자동 조합"""
        import random
        
        assignments = {}
        
        if task_type == "epic":
            # Epic은 균형잡힌 조합
            combinations = [
                self.combine_personas("architect", "samurai"),
                self.combine_personas("perfectionist", "detective"),
                self.combine_personas("speedster", "pirate")
            ]
        elif task_type == "bug":
            # 버그는 신중한 조합 (비판적 페르소나 포함)
            combinations = [
                self.combine_personas("guardian", "detective"),
                self.combine_personas("critic", "samurai"),
                self.combine_personas("minimalist", "robot")
            ]
        elif task_type == "research":
            # 리서치는 창의적 조합
            combinations = [
                self.combine_personas("innovator", "wizard"),
                self.combine_personas("architect", "philosopher"),
                self.combine_personas("devil_advocate", "skeptic")
            ]
        else:
            # 기본: 랜덤 조합 (비판적 1개 포함)
            combinations = [
                self.get_random_combination(include_critic=True),
                self.get_random_combination(include_critic=False),
                self.get_random_combination(include_critic=False)
            ]
        
        # AI 팀에 할당
        for i, ai in enumerate(ai_team[:len(combinations)]):
            assignments[ai] = combinations[i]
        
        return assignments
    
    def format_persona_comment(self, persona: Dict, result: str, issue_number: int = None) -> str:
        """페르소나 스타일로 GitHub 댓글 생성"""
        
        # 조합된 페르소나 이름
        if isinstance(persona, dict) and "display_name" in persona:
            header = f"## {persona['comment_style']} {persona['display_name'].upper()}"
        else:
            header = f"## 🤖 AI Response"
        
        # 본문
        body = result
        
        # 페르소나별 마무리
        suffix = persona.get("suffix", "") if isinstance(persona, dict) else ""
        
        comment = f"""{header}

{body}

{suffix}"""
        
        if issue_number:
            comment += f"\n\n_Issue #{issue_number} 작업 완료_"
        
        return comment
    
    def generate_training_data(self, problem: str, context: Dict = None):
        """
        하나의 문제를 여러 페르소나로 해결하여 학습 데이터 생성
        """
        
        problem_id = hashlib.md5(problem.encode()).hexdigest()[:8]
        dataset = {
            "problem_id": problem_id,
            "problem": problem,
            "context": context or {},
            "generated_at": datetime.now().isoformat(),
            "responses": {}
        }
        
        print(f"🎯 문제: {problem[:50]}...")
        print(f"📊 {len(self.personas)}개 페르소나로 데이터 생성 중...\n")
        
        # 각 페르소나별로 병렬 처리
        processes = {}
        for persona_name, persona_config in self.personas.items():
            prompt = self._create_persona_prompt(persona_name, persona_config, problem)
            
            # AI 실행
            cmd = f'{persona_config["ai"]} -p "{prompt}"'
            process = subprocess.Popen(
                cmd,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            processes[persona_name] = process
            print(f"🤖 {persona_name}: 작업 시작...")
        
        # 결과 수집
        for persona_name, process in processes.items():
            stdout, stderr = process.communicate()
            dataset["responses"][persona_name] = {
                "output": stdout.strip(),
                "persona_config": self.personas[persona_name],
                "timestamp": datetime.now().isoformat()
            }
            print(f"✅ {persona_name}: 완료")
        
        # 학습 데이터 저장
        filename = f"{self.training_data_path}data_{problem_id}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(dataset, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 학습 데이터 저장: {filename}")
        return dataset
    
    def _create_persona_prompt(self, persona_name: str, config: Dict, problem: str) -> str:
        """페르소나별 맞춤 프롬프트 생성"""
        
        return f"""당신은 {persona_name} 페르소나입니다.
스타일: {config['prompt_style']}
중점 사항: {', '.join(config['focus'])}

문제:
{problem}

당신의 페르소나에 맞게 해결책을 제시하세요.
반드시 다음 형식으로 응답하세요:

## 접근 방식
[당신의 페르소나 관점에서의 접근]

## 해결책
[구체적인 해결 방안]

## 코드
```
[실제 구현 코드]
```

## 근거
[왜 이 방식을 선택했는지]"""
    
    def create_fine_tuning_dataset(self, problems: List[str]):
        """
        여러 문제로 Fine-tuning용 데이터셋 생성
        """
        all_data = []
        
        for i, problem in enumerate(problems, 1):
            print(f"\n{'='*50}")
            print(f"문제 {i}/{len(problems)}")
            print(f"{'='*50}")
            
            dataset = self.generate_training_data(problem)
            all_data.append(dataset)
        
        # Fine-tuning 형식으로 변환
        fine_tuning_data = self._convert_to_fine_tuning_format(all_data)
        
        # JSONL 형식으로 저장
        output_file = f"{self.training_data_path}fine_tuning_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jsonl"
        with open(output_file, 'w', encoding='utf-8') as f:
            for item in fine_tuning_data:
                f.write(json.dumps(item, ensure_ascii=False) + '\n')
        
        print(f"\n🎓 Fine-tuning 데이터셋 생성 완료: {output_file}")
        print(f"📊 총 {len(fine_tuning_data)}개 학습 샘플 생성")
        
        return output_file
    
    def _convert_to_fine_tuning_format(self, all_data: List[Dict]) -> List[Dict]:
        """
        수집된 데이터를 Fine-tuning 형식으로 변환
        """
        fine_tuning_data = []
        
        for dataset in all_data:
            problem = dataset["problem"]
            
            # 각 페르소나 응답을 학습 데이터로 변환
            for persona_name, response in dataset["responses"].items():
                fine_tuning_data.append({
                    "messages": [
                        {
                            "role": "system",
                            "content": f"You are an AI with {persona_name} persona. {self.personas[persona_name]['prompt_style']}"
                        },
                        {
                            "role": "user",
                            "content": problem
                        },
                        {
                            "role": "assistant",
                            "content": response["output"]
                        }
                    ],
                    "metadata": {
                        "persona": persona_name,
                        "focus_areas": self.personas[persona_name]["focus"],
                        "problem_id": dataset["problem_id"]
                    }
                })
        
        return fine_tuning_data

class AutomatedLearningPipeline:
    """
    자동 학습 파이프라인
    GitHub Issue → Multi-Persona Solutions → Training Data → Model Fine-tuning
    """
    
    def __init__(self):
        self.training_system = PersonaTrainingSystem()
    
    def process_from_github(self, repo: str = "ihw33/ai-orchestra-v02"):
        """
        GitHub 이슈들을 학습 데이터로 변환
        """
        # 모든 오픈 이슈 가져오기
        cmd = f"gh issue list -R {repo} --json number,title,body -q '.[]'"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        issues = json.loads(result.stdout) if result.stdout else []
        
        problems = []
        for issue in issues:
            problem = f"Issue #{issue['number']}: {issue['title']}\n\n{issue['body']}"
            problems.append(problem)
        
        if problems:
            print(f"📚 {len(problems)}개 이슈를 학습 데이터로 변환 중...")
            return self.training_system.create_fine_tuning_dataset(problems)
        else:
            print("⚠️ 처리할 이슈가 없습니다.")
            return None

# 사용 예시
if __name__ == "__main__":
    # 1. 단일 문제로 테스트
    system = PersonaTrainingSystem()
    
    test_problem = """
    React 컴포넌트에서 상태 관리를 효율적으로 하는 방법을 구현하세요.
    요구사항:
    - TypeScript 사용
    - 성능 최적화 고려
    - 테스트 가능한 구조
    """
    
    # 다양한 페르소나로 해결책 생성
    dataset = system.generate_training_data(test_problem)
    
    # 2. GitHub 이슈에서 자동 생성
    # pipeline = AutomatedLearningPipeline()
    # pipeline.process_from_github()