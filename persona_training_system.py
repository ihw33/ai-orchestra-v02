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
        # 페르소나 정의 (각 AI의 특성)
        self.personas = {
            "architect": {
                "ai": "claude",
                "prompt_style": "시스템 아키텍처와 설계 패턴 중심",
                "focus": ["확장성", "유지보수성", "설계 원칙"]
            },
            "perfectionist": {
                "ai": "gemini", 
                "prompt_style": "완벽한 코드 품질과 최적화 추구",
                "focus": ["성능", "코드 품질", "엣지 케이스"]
            },
            "pragmatist": {
                "ai": "codex",
                "prompt_style": "실용적이고 빠른 해결책 선호",
                "focus": ["구현 속도", "실용성", "MVP"]
            },
            "innovator": {
                "ai": "claude",
                "prompt_style": "창의적이고 혁신적인 접근",
                "focus": ["새로운 기술", "창의성", "미래 지향"]
            },
            "educator": {
                "ai": "gemini",
                "prompt_style": "교육적이고 설명이 상세함",
                "focus": ["이해도", "문서화", "학습 곡선"]
            },
            "security_expert": {
                "ai": "codex",
                "prompt_style": "보안과 안전성 최우선",
                "focus": ["보안", "검증", "취약점"]
            }
        }
        
        self.training_data_path = "training_data/"
        os.makedirs(self.training_data_path, exist_ok=True)
    
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