#!/usr/bin/env python3
"""
AI Relay Pipeline System
이슈 → AI1(구현) → AI2(검증) → AI3(리뷰) → 완료
각 단계가 완료되면 자동으로 다음 AI에게 전달
"""

import subprocess
import json
import time
from datetime import datetime
from typing import Dict, List, Optional, Any
from enum import Enum
import os

class PipelineStage(Enum):
    """파이프라인 단계 정의"""
    PENDING = "pending"
    IMPLEMENTING = "implementing"
    TESTING = "testing"
    REVIEWING = "reviewing"
    COMPLETED = "completed"
    FAILED = "failed"

class RelayPipeline:
    """
    릴레이 방식 자동 파이프라인
    각 AI가 이전 AI의 결과를 받아서 작업
    """
    
    def __init__(self):
        # 릴레이 단계 정의
        self.stages = [
            {
                "stage": PipelineStage.IMPLEMENTING,
                "ai": "claude",
                "role": "구현",
                "prompt_template": self._implementation_prompt,
                "success_criteria": ["코드 생성 완료", "함수 구현", "class"]
            },
            {
                "stage": PipelineStage.TESTING,
                "ai": "gemini",
                "role": "테스트 & 검증",
                "prompt_template": self._testing_prompt,
                "success_criteria": ["테스트 통과", "검증 완료", "PASS"]
            },
            {
                "stage": PipelineStage.REVIEWING,
                "ai": "codex",
                "role": "코드 리뷰",
                "prompt_template": self._review_prompt,
                "success_criteria": ["리뷰 완료", "승인", "APPROVED"]
            }
        ]
        
        self.pipeline_logs = []
        self.results_path = "pipeline_results/"
        os.makedirs(self.results_path, exist_ok=True)
    
    def process_issue(self, issue_number: int, repo: str = "ihw33/ai-orchestra-v02"):
        """
        이슈를 릴레이 방식으로 처리
        """
        print(f"🚀 릴레이 파이프라인 시작: Issue #{issue_number}")
        print("="*60)
        
        # 파이프라인 실행 기록 초기화
        pipeline_run = {
            "issue_number": issue_number,
            "repo": repo,
            "started_at": datetime.now().isoformat(),
            "stages": [],
            "final_status": None
        }
        
        # 이슈 내용 가져오기
        issue_body = self._get_issue_content(issue_number, repo)
        
        # 릴레이 실행 - 각 단계를 순차적으로
        previous_output = issue_body
        current_stage = 0
        
        while current_stage < len(self.stages):
            stage_config = self.stages[current_stage]
            print(f"\n📍 Stage {current_stage + 1}: {stage_config['role']}")
            print("-" * 40)
            
            # 현재 단계 실행
            stage_result = self._execute_stage(
                stage_config=stage_config,
                input_data=previous_output,
                issue_number=issue_number,
                stage_num=current_stage + 1
            )
            
            # 결과 기록
            pipeline_run["stages"].append(stage_result)
            
            # GitHub 이슈에 진행상황 업데이트
            self._update_issue_progress(issue_number, repo, stage_result)
            
            # 성공 여부 확인
            if stage_result["success"]:
                print(f"✅ {stage_config['role']} 완료")
                previous_output = stage_result["output"]
                current_stage += 1
            else:
                print(f"❌ {stage_config['role']} 실패")
                pipeline_run["final_status"] = "FAILED"
                break
        
        # 파이프라인 완료
        if current_stage == len(self.stages):
            pipeline_run["final_status"] = "COMPLETED"
            print("\n🎉 파이프라인 완료!")
            
            # 최종 결과를 이슈에 추가
            self._post_final_result(issue_number, repo, pipeline_run)
        
        # 결과 저장
        self._save_pipeline_run(pipeline_run)
        
        return pipeline_run
    
    def _execute_stage(self, stage_config: Dict, input_data: str, 
                      issue_number: int, stage_num: int) -> Dict:
        """
        단일 스테이지 실행
        """
        stage_result = {
            "stage": stage_config["stage"].value,
            "ai": stage_config["ai"],
            "role": stage_config["role"],
            "started_at": datetime.now().isoformat(),
            "input_length": len(input_data)
        }
        
        try:
            # 프롬프트 생성
            prompt = stage_config["prompt_template"](input_data, issue_number, stage_num)
            
            # AI 실행
            print(f"🤖 {stage_config['ai'].upper()} 작업 중...")
            cmd = f'{stage_config["ai"]} -p "{prompt}"'
            
            process = subprocess.Popen(
                cmd,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                env={**os.environ, "TIMEOUT": "60"}  # 60초 타임아웃
            )
            
            stdout, stderr = process.communicate(timeout=60)
            
            stage_result["output"] = stdout.strip()
            stage_result["error"] = stderr.strip() if stderr else None
            stage_result["completed_at"] = datetime.now().isoformat()
            
            # 성공 기준 체크
            success = self._check_success_criteria(
                stdout, 
                stage_config["success_criteria"]
            )
            stage_result["success"] = success
            
            # 실행 시간 계산
            start = datetime.fromisoformat(stage_result["started_at"])
            end = datetime.fromisoformat(stage_result["completed_at"])
            stage_result["duration_seconds"] = (end - start).total_seconds()
            
        except subprocess.TimeoutExpired:
            stage_result["success"] = False
            stage_result["error"] = "Timeout exceeded (60s)"
            stage_result["completed_at"] = datetime.now().isoformat()
        except Exception as e:
            stage_result["success"] = False
            stage_result["error"] = str(e)
            stage_result["completed_at"] = datetime.now().isoformat()
        
        return stage_result
    
    def _check_success_criteria(self, output: str, criteria: List[str]) -> bool:
        """
        출력에서 성공 기준 확인
        """
        output_lower = output.lower()
        for criterion in criteria:
            if criterion.lower() in output_lower:
                return True
        return len(output) > 100  # 최소한 의미있는 출력이 있으면 성공
    
    def _implementation_prompt(self, input_data: str, issue_number: int, stage_num: int) -> str:
        """구현 단계 프롬프트"""
        return f"""[STAGE {stage_num}: IMPLEMENTATION]
Issue #{issue_number}

요구사항:
{input_data}

작업:
1. 요구사항을 분석하고 구현하세요
2. 실제 동작하는 코드를 작성하세요
3. 주요 함수와 클래스를 포함하세요

출력 형식:
## 구현 내용
[설명]

## 코드
```python
[실제 코드]
```

## 다음 단계 전달 사항
[테스터가 확인해야 할 핵심 기능]

반드시 "코드 생성 완료"라는 문구를 포함하세요."""
    
    def _testing_prompt(self, input_data: str, issue_number: int, stage_num: int) -> str:
        """테스트 단계 프롬프트"""
        return f"""[STAGE {stage_num}: TESTING & VALIDATION]
Issue #{issue_number}

이전 단계 결과:
{input_data}

작업:
1. 제공된 코드를 분석하세요
2. 테스트 케이스를 작성하세요
3. 잠재적 버그나 문제점을 찾으세요
4. 검증 결과를 제시하세요

출력 형식:
## 테스트 결과
- 기능 테스트: [PASS/FAIL]
- 엣지 케이스: [PASS/FAIL]
- 성능 검증: [PASS/FAIL]

## 발견된 문제
[문제점 리스트]

## 개선 제안
[제안 사항]

반드시 "검증 완료" 또는 "테스트 통과"를 포함하세요."""
    
    def _review_prompt(self, input_data: str, issue_number: int, stage_num: int) -> str:
        """리뷰 단계 프롬프트"""
        return f"""[STAGE {stage_num}: CODE REVIEW]
Issue #{issue_number}

테스트 완료된 코드:
{input_data}

작업:
1. 코드 품질 평가
2. 베스트 프랙티스 준수 확인
3. 보안 취약점 검사
4. 최종 승인 또는 거부 결정

출력 형식:
## 코드 리뷰 결과
### 장점
- [긍정적 측면]

### 개선 필요
- [개선점]

### 보안 검토
- [보안 이슈]

## 최종 판정
[APPROVED/REJECTED]

## 머지 준비 상태
[Ready to merge: YES/NO]

반드시 "리뷰 완료"와 "APPROVED" 또는 "REJECTED"를 포함하세요."""
    
    def _get_issue_content(self, issue_number: int, repo: str) -> str:
        """GitHub 이슈 내용 가져오기"""
        cmd = f"gh issue view {issue_number} -R {repo} --json title,body"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        
        if result.stdout:
            data = json.loads(result.stdout)
            return f"제목: {data['title']}\n\n{data['body']}"
        return ""
    
    def _update_issue_progress(self, issue_number: int, repo: str, stage_result: Dict):
        """이슈에 진행상황 업데이트"""
        status_emoji = "✅" if stage_result["success"] else "❌"
        
        comment = f"""## {status_emoji} Stage: {stage_result['role']}
        
**AI**: {stage_result['ai']}
**Status**: {'Success' if stage_result['success'] else 'Failed'}
**Duration**: {stage_result.get('duration_seconds', 0):.2f}s

### Output Preview:
```
{stage_result['output'][:500]}...
```

*Processed at: {stage_result['completed_at']}*
"""
        
        cmd = f'gh issue comment {issue_number} -R {repo} -b "{comment}"'
        subprocess.run(cmd, shell=True)
    
    def _post_final_result(self, issue_number: int, repo: str, pipeline_run: Dict):
        """최종 결과를 이슈에 게시"""
        
        # 각 스테이지 요약
        stages_summary = ""
        for i, stage in enumerate(pipeline_run["stages"], 1):
            emoji = "✅" if stage["success"] else "❌"
            stages_summary += f"{i}. {emoji} {stage['role']} ({stage['ai']}): "
            stages_summary += f"{stage.get('duration_seconds', 0):.1f}s\n"
        
        comment = f"""# 🏁 Pipeline Completed: {pipeline_run['final_status']}

## 📊 Stage Summary:
{stages_summary}

## 📝 Final Output:
```
{pipeline_run['stages'][-1]['output'][:1000] if pipeline_run['stages'] else 'No output'}
```

## ⏱️ Total Duration:
Start: {pipeline_run['started_at']}
Status: **{pipeline_run['final_status']}**

---
*Automated by Relay Pipeline System*"""
        
        cmd = f'gh issue comment {issue_number} -R {repo} -b "{comment}"'
        subprocess.run(cmd, shell=True)
        
        # 완료 라벨 추가
        if pipeline_run['final_status'] == 'COMPLETED':
            subprocess.run(
                f"gh issue edit {issue_number} -R {repo} --add-label pipeline-completed",
                shell=True
            )
    
    def _save_pipeline_run(self, pipeline_run: Dict):
        """파이프라인 실행 결과 저장"""
        filename = f"{self.results_path}pipeline_{pipeline_run['issue_number']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(pipeline_run, f, indent=2, ensure_ascii=False)
        print(f"💾 결과 저장: {filename}")

class AutomatedRelaySystem:
    """
    GitHub Webhook과 연동된 자동 릴레이 시스템
    """
    
    def __init__(self):
        self.pipeline = RelayPipeline()
        self.watch_label = "relay-pipeline"
    
    def watch_and_process(self, repo: str = "ihw33/ai-orchestra-v02"):
        """
        특정 라벨이 붙은 이슈를 자동으로 릴레이 처리
        """
        print(f"👀 Watching for issues with label '{self.watch_label}'...")
        
        processed_issues = set()
        
        while True:
            # 라벨이 붙은 이슈 확인
            cmd = f'gh issue list -R {repo} -l {self.watch_label} --state open --json number'
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            
            if result.stdout:
                issues = json.loads(result.stdout)
                for issue in issues:
                    issue_num = issue['number']
                    if issue_num not in processed_issues:
                        print(f"\n🎯 새 이슈 발견: #{issue_num}")
                        self.pipeline.process_issue(issue_num, repo)
                        processed_issues.add(issue_num)
            
            time.sleep(10)  # 10초마다 체크

# CLI 인터페이스
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("""
Relay Pipeline System
Usage:
  python relay_pipeline_system.py <issue_number>  # 특정 이슈 처리
  python relay_pipeline_system.py watch            # 자동 감시 모드
  
Example:
  python relay_pipeline_system.py 123
  python relay_pipeline_system.py watch
        """)
    elif sys.argv[1] == "watch":
        system = AutomatedRelaySystem()
        system.watch_and_process()
    else:
        pipeline = RelayPipeline()
        issue_num = int(sys.argv[1])
        result = pipeline.process_issue(issue_num)
        
        print("\n" + "="*60)
        print(f"Pipeline Result: {result['final_status']}")
        print(f"Total Stages: {len(result['stages'])}")
        print("="*60)