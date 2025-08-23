#!/usr/bin/env python3
"""
AI Task Distribution Workflow
여러 AI의 의견을 수렴하고 작업을 자동 분산하는 시스템
"""

import json
import subprocess
import time
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime

@dataclass
class AITask:
    """AI 작업 정의"""
    issue_number: int
    title: str
    assignee: str  # AI 이름
    task_type: str
    description: str
    inputs: List[str]
    outputs: List[str]
    success_criteria: List[str]
    
class AIOpinionCollector:
    """여러 AI의 의견을 수집하는 시스템"""
    
    def __init__(self):
        self.ai_configs = {
            "gemini": {"cmd": "gemini", "specialty": "UX/사용성"},
            "codex": {"cmd": "codex", "specialty": "구현/로직"},
            "claude": {"cmd": "claude", "specialty": "아키텍처/품질"}
        }
        self.opinions = {}
    
    def collect_opinions_on_template(self, template_content: str) -> Dict:
        """템플릿에 대한 각 AI의 의견 수집"""
        
        prompt_template = """
        다음 Issue 템플릿을 검토하고 개선사항을 제안해주세요.
        당신의 전문 분야: {specialty}
        
        템플릿:
        {template}
        
        다음 관점에서 의견을 제시해주세요:
        1. 명확성: 작업이 명확하게 정의되었는가?
        2. 완전성: 필요한 정보가 모두 포함되었는가?
        3. 실행가능성: 단일 대화로 완료 가능한가?
        4. 개선점: 어떻게 개선할 수 있는가?
        
        JSON 형식으로 응답해주세요:
        {{
            "clarity_score": 1-10,
            "completeness_score": 1-10,
            "feasibility_score": 1-10,
            "improvements": ["개선점1", "개선점2"],
            "recommended_changes": "구체적인 수정 제안"
        }}
        """
        
        for ai_name, config in self.ai_configs.items():
            prompt = prompt_template.format(
                specialty=config["specialty"],
                template=template_content
            )
            
            # AI에게 의견 요청 (-p 모드 사용)
            try:
                result = subprocess.run(
                    [config["cmd"], "-p", prompt],
                    capture_output=True,
                    text=True,
                    timeout=60
                )
                
                # JSON 파싱 시도
                try:
                    opinion = json.loads(result.stdout)
                except:
                    opinion = {"raw_response": result.stdout}
                
                self.opinions[ai_name] = opinion
                print(f"✅ {ai_name} 의견 수집 완료")
                
            except Exception as e:
                print(f"❌ {ai_name} 의견 수집 실패: {e}")
                self.opinions[ai_name] = {"error": str(e)}
        
        return self.opinions
    
    def synthesize_opinions(self) -> str:
        """수집된 의견을 종합하여 최종 템플릿 생성"""
        
        synthesis = {
            "average_scores": {
                "clarity": 0,
                "completeness": 0,
                "feasibility": 0
            },
            "all_improvements": [],
            "consensus_changes": []
        }
        
        valid_opinions = 0
        
        for ai_name, opinion in self.opinions.items():
            if "error" not in opinion:
                valid_opinions += 1
                if "clarity_score" in opinion:
                    synthesis["average_scores"]["clarity"] += opinion["clarity_score"]
                if "completeness_score" in opinion:
                    synthesis["average_scores"]["completeness"] += opinion["completeness_score"]
                if "feasibility_score" in opinion:
                    synthesis["average_scores"]["feasibility"] += opinion["feasibility_score"]
                if "improvements" in opinion:
                    synthesis["all_improvements"].extend(opinion["improvements"])
        
        # 평균 계산
        if valid_opinions > 0:
            for key in synthesis["average_scores"]:
                synthesis["average_scores"][key] /= valid_opinions
        
        # 공통 개선사항 찾기
        improvement_counts = {}
        for improvement in synthesis["all_improvements"]:
            improvement_counts[improvement] = improvement_counts.get(improvement, 0) + 1
        
        # 2개 이상의 AI가 동의한 개선사항
        synthesis["consensus_changes"] = [
            imp for imp, count in improvement_counts.items() if count >= 2
        ]
        
        return json.dumps(synthesis, indent=2, ensure_ascii=False)

class TaskDistributor:
    """작업을 적절한 AI에게 자동 분배"""
    
    def __init__(self):
        self.task_rules = {
            "feature": {
                "ui": "gemini",
                "backend": "codex",
                "architecture": "claude"
            },
            "bug": {
                "investigation": "claude",
                "fix": "codex",
                "test": "gemini"
            },
            "review": {
                "code": "claude",
                "ux": "gemini",
                "performance": "codex"
            }
        }
    
    def analyze_task(self, task: AITask) -> str:
        """작업 분석하여 최적의 AI 선택"""
        
        # 키워드 기반 분석
        description_lower = task.description.lower()
        
        if any(keyword in description_lower for keyword in ["ui", "화면", "디자인", "사용자"]):
            return "gemini"
        elif any(keyword in description_lower for keyword in ["api", "데이터베이스", "백엔드", "서버"]):
            return "codex"
        elif any(keyword in description_lower for keyword in ["아키텍처", "설계", "리뷰", "품질"]):
            return "claude"
        else:
            # 작업 타입으로 판단
            return self.task_rules.get(task.task_type, {}).get("default", "claude")
    
    def create_subtasks(self, task: AITask) -> List[AITask]:
        """복잡한 작업을 여러 AI를 위한 서브태스크로 분할"""
        
        subtasks = []
        
        # 작업이 여러 단계를 포함하는 경우
        if len(task.success_criteria) > 3:
            # 설계 단계 (Claude)
            design_task = AITask(
                issue_number=task.issue_number,
                title=f"{task.title} - 설계",
                assignee="claude",
                task_type="design",
                description=f"설계 및 아키텍처 정의: {task.description}",
                inputs=task.inputs,
                outputs=["설계 문서", "API 스펙"],
                success_criteria=["설계 완료", "리뷰 통과"]
            )
            subtasks.append(design_task)
            
            # 구현 단계 (Codex)
            impl_task = AITask(
                issue_number=task.issue_number,
                title=f"{task.title} - 구현",
                assignee="codex",
                task_type="implementation",
                description=f"기능 구현: {task.description}",
                inputs=["설계 문서"] + task.inputs,
                outputs=task.outputs,
                success_criteria=["코드 구현", "테스트 작성"]
            )
            subtasks.append(impl_task)
            
            # 검증 단계 (Gemini)
            test_task = AITask(
                issue_number=task.issue_number,
                title=f"{task.title} - 검증",
                assignee="gemini",
                task_type="testing",
                description=f"사용성 테스트 및 검증: {task.description}",
                inputs=task.outputs,
                outputs=["테스트 리포트", "개선 제안"],
                success_criteria=["테스트 완료", "사용성 확인"]
            )
            subtasks.append(test_task)
        else:
            # 단일 작업은 분석 후 할당
            task.assignee = self.analyze_task(task)
            subtasks.append(task)
        
        return subtasks

def create_pr_for_review(issue_number: int, branch_name: str, files: List[str]):
    """리뷰를 위한 PR 생성"""
    
    # 브랜치 생성
    subprocess.run(["git", "checkout", "-b", branch_name])
    
    # 파일 커밋
    for file in files:
        subprocess.run(["git", "add", file])
    
    subprocess.run(["git", "commit", "-m", f"feat: AI task template system (#{issue_number})"])
    subprocess.run(["git", "push", "origin", branch_name])
    
    # PR 생성
    pr_body = f"""
## 🤖 AI 협업 리뷰 요청

이 PR은 Issue #{issue_number}에서 논의된 AI 작업 템플릿 시스템입니다.

### 📋 포함된 내용
- Issue 템플릿 (.github/ISSUE_TEMPLATE/ai_task_template.yml)
- 작업 분산 워크플로우 (ai_task_workflow.py)
- 의견 수렴 시스템

### 🔍 리뷰 포인트
1. 템플릿의 명확성과 완전성
2. 자동화 워크플로우의 효율성
3. AI 간 협업 프로세스

### 👥 리뷰어
- @gemini: UX/사용성 관점
- @codex: 구현 가능성 관점
- @claude: 아키텍처/품질 관점

각 AI는 자신의 전문 분야에서 리뷰해주세요.
    """
    
    result = subprocess.run([
        "gh", "pr", "create",
        "-R", "ihw33/ai-orchestra-v02",
        "--title", f"feat: AI task template system (#{issue_number})",
        "--body", pr_body,
        "--base", "main",
        "--head", branch_name
    ], capture_output=True, text=True)
    
    return result.stdout

def main():
    """메인 실행 함수"""
    
    print("🚀 AI 작업 분산 시스템 시작\n")
    
    # 1. 의견 수집
    collector = AIOpinionCollector()
    
    with open("issue_template.md", "r") as f:
        template_content = f.read()
    
    print("📊 각 AI의 의견 수집 중...")
    opinions = collector.collect_opinions_on_template(template_content)
    
    # 2. 의견 종합
    print("\n📝 의견 종합 중...")
    synthesis = collector.synthesize_opinions()
    
    print("\n✨ 종합된 의견:")
    print(synthesis)
    
    # 3. PR 생성
    print("\n🔄 PR 생성 중...")
    pr_url = create_pr_for_review(
        issue_number=34,
        branch_name="feat/ai-task-templates",
        files=[
            ".github/ISSUE_TEMPLATE/ai_task_template.yml",
            "ai_task_workflow.py",
            "issue_template.md"
        ]
    )
    
    print(f"\n✅ PR 생성 완료: {pr_url}")
    
    # 4. 작업 분산 예시
    distributor = TaskDistributor()
    
    example_task = AITask(
        issue_number=35,
        title="사용자 프로필 페이지 구현",
        assignee="",
        task_type="feature",
        description="사용자 프로필 페이지 UI와 API 구현",
        inputs=["user model", "design mockup"],
        outputs=["profile.tsx", "profile_api.py"],
        success_criteria=["UI 구현", "API 구현", "테스트 통과"]
    )
    
    print("\n📤 작업 분산 예시:")
    subtasks = distributor.create_subtasks(example_task)
    for subtask in subtasks:
        print(f"  - {subtask.assignee}: {subtask.title}")

if __name__ == "__main__":
    main()