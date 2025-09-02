"""
Label Management Adapter
GitHub 라벨 관리 구현 - 최소한의 자동 생성
"""

import subprocess
import json
import re
from typing import Dict, List, Optional, Set
import sys
import os

# Port 인터페이스 import
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from ports.label_management_port import (
    LabelManagementPort,
    Label,
    LabelCategory,
    LabelRule
)

class GitHubLabelManagementAdapter(LabelManagementPort):
    """GitHub 라벨 관리 Adapter - 최소 필요 라벨만 자동 생성"""
    
    def __init__(self, repo: str = "ihw33/ai-orchestra-v02"):
        self.repo = repo
        self.essential_labels = self._define_essential_labels()
        self.label_rules = self._define_label_rules()
        self._label_cache = None
    
    def _define_essential_labels(self) -> Dict[str, Label]:
        """필수 라벨만 정의 (최소한)"""
        return {
            # Issue Type (필수)
            'epic': Label('epic', 'FFA500', 'Epic 이슈', LabelCategory.ISSUE_TYPE),
            'story': Label('story', '8A2BE2', 'Story 이슈', LabelCategory.ISSUE_TYPE),
            'task': Label('task', '0366d6', 'Task 이슈', LabelCategory.ISSUE_TYPE),
            
            # AI Assignment (필요시에만)
            'ai-gemini': Label('ai-gemini', 'FBCA04', 'Gemini AI 담당', LabelCategory.AI_ASSIGNMENT),
            'ai-claude': Label('ai-claude', 'C5DEF5', 'Claude AI 담당', LabelCategory.AI_ASSIGNMENT),
            'ai-codex': Label('ai-codex', 'E99695', 'Codex AI 담당', LabelCategory.AI_ASSIGNMENT),
            
            # Priority (선택적)
            'p0': Label('p0', 'D73A4A', '긴급', LabelCategory.PRIORITY, auto_create=False),
            'p1': Label('p1', 'FFA500', '중요', LabelCategory.PRIORITY, auto_create=False),
            
            # Workflow (자동화에 필요한 것만)
            'automated': Label('automated', '28a745', '자동화됨', LabelCategory.WORKFLOW),
        }
    
    def _define_label_rules(self) -> List[LabelRule]:
        """라벨 자동 적용 규칙 (최소한)"""
        return [
            # Epic/Story/Task는 제목으로 판단
            LabelRule(r'\[Epic\]', ['epic'], 0.99),
            LabelRule(r'\[Story\]', ['story'], 0.99),
            LabelRule(r'\[Task\]', ['task'], 0.99),
            
            # AI 할당은 명시적인 경우만
            LabelRule(r'AI:\s*Gemini|담당:\s*Gemini', ['ai-gemini'], 0.95),
            LabelRule(r'AI:\s*Claude|담당:\s*Claude', ['ai-claude'], 0.95),
            LabelRule(r'AI:\s*Codex|담당:\s*Codex', ['ai-codex'], 0.95),
            
            # 긴급도는 명시적 키워드만
            LabelRule(r'긴급|URGENT|CRITICAL', ['p0'], 0.90),
            LabelRule(r'중요|IMPORTANT', ['p1'], 0.85),
        ]
    
    def ensure_label_exists(self, label_name: str) -> bool:
        """라벨이 존재하는지 확인하고 필수 라벨만 생성"""
        
        # 캐시 확인
        if self._label_cache is None:
            self._refresh_label_cache()
        
        if label_name in self._label_cache:
            return True
        
        # 필수 라벨인지 확인
        if label_name in self.essential_labels:
            label = self.essential_labels[label_name]
            if label.auto_create:
                return self.create_label(label)
        
        # 필수가 아니면 생성하지 않음
        return False
    
    def create_label(self, label: Label) -> bool:
        """라벨 생성 (필요한 경우만)"""
        
        # 이미 존재하는지 확인
        if self._label_exists(label.name):
            return True
        
        cmd = f'gh label create "{label.name}" -R {self.repo}'
        cmd += f' --color "{label.color}"'
        cmd += f' --description "{label.description}"'
        
        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            if result.returncode == 0:
                # 캐시 업데이트
                if self._label_cache is not None:
                    self._label_cache.add(label.name)
                return True
        except:
            pass
        
        return False
    
    def update_label(self, old_name: str, new_label: Label) -> bool:
        """라벨 업데이트"""
        
        cmd = f'gh label edit "{old_name}" -R {self.repo}'
        cmd += f' --name "{new_label.name}"'
        cmd += f' --color "{new_label.color}"'
        cmd += f' --description "{new_label.description}"'
        
        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            return result.returncode == 0
        except:
            return False
    
    def delete_label(self, label_name: str) -> bool:
        """라벨 삭제 (주의: 필수 라벨은 삭제하지 않음)"""
        
        # 필수 라벨인지 확인
        if label_name in self.essential_labels:
            print(f"⚠️ 필수 라벨 '{label_name}'은 삭제할 수 없습니다")
            return False
        
        cmd = f'gh label delete "{label_name}" -R {self.repo} --yes'
        
        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            if result.returncode == 0:
                # 캐시에서 제거
                if self._label_cache and label_name in self._label_cache:
                    self._label_cache.remove(label_name)
                return True
        except:
            pass
        
        return False
    
    def get_all_labels(self) -> List[Label]:
        """모든 라벨 조회"""
        
        cmd = f'gh label list -R {self.repo} --json name,color,description --limit 100'
        
        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            if result.returncode == 0:
                data = json.loads(result.stdout)
                labels = []
                
                for item in data:
                    # 카테고리 추론
                    category = self._infer_category(item['name'])
                    labels.append(Label(
                        name=item['name'],
                        color=item['color'],
                        description=item.get('description', ''),
                        category=category
                    ))
                
                return labels
        except:
            pass
        
        return []
    
    def suggest_labels(self, issue_title: str, issue_body: str) -> List[str]:
        """이슈 내용 기반 라벨 제안 (최소한만)"""
        
        suggested = set()
        content = f"{issue_title}\n{issue_body}"
        
        # 규칙 기반 매칭
        for rule in self.label_rules:
            if re.search(rule.pattern, content, re.IGNORECASE):
                if rule.confidence >= 0.90:  # 높은 확신도만
                    suggested.update(rule.labels)
        
        # 필수 라벨만 반환
        return [label for label in suggested if label in self.essential_labels]
    
    def apply_labels(self, issue_number: int, labels: List[str]) -> bool:
        """이슈에 라벨 적용 (존재하는 라벨만)"""
        
        if not labels:
            return True
        
        # 존재하는 라벨만 필터링
        existing_labels = []
        for label in labels:
            if self.ensure_label_exists(label):
                existing_labels.append(label)
        
        if not existing_labels:
            return True
        
        # 라벨 적용
        label_str = ','.join(existing_labels)
        cmd = f'gh issue edit {issue_number} -R {self.repo} --add-label "{label_str}"'
        
        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            return result.returncode == 0
        except:
            return False
    
    def sync_labels(self) -> Dict:
        """프로젝트 표준 라벨과 동기화 (필수 라벨만)"""
        
        created = []
        skipped = []
        errors = []
        
        # 현재 라벨 확인
        self._refresh_label_cache()
        
        # 필수 라벨만 체크
        for label_name, label in self.essential_labels.items():
            if not label.auto_create:
                skipped.append(label_name)
                continue
                
            if label_name not in self._label_cache:
                if self.create_label(label):
                    created.append(label_name)
                else:
                    errors.append(label_name)
            else:
                skipped.append(label_name)
        
        return {
            'created': created,
            'skipped': skipped,
            'errors': errors,
            'total_labels': len(self._label_cache) if self._label_cache else 0
        }
    
    # === Helper Methods ===
    
    def _label_exists(self, label_name: str) -> bool:
        """라벨 존재 여부 확인"""
        
        if self._label_cache is None:
            self._refresh_label_cache()
        
        return label_name in self._label_cache
    
    def _refresh_label_cache(self):
        """라벨 캐시 새로고침"""
        
        cmd = f'gh label list -R {self.repo} --json name --limit 200'
        
        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            if result.returncode == 0:
                data = json.loads(result.stdout)
                self._label_cache = {item['name'] for item in data}
        except:
            self._label_cache = set()
    
    def _infer_category(self, label_name: str) -> LabelCategory:
        """라벨 이름으로 카테고리 추론"""
        
        name_lower = label_name.lower()
        
        if name_lower in ['epic', 'story', 'task']:
            return LabelCategory.ISSUE_TYPE
        elif name_lower.startswith('ai-'):
            return LabelCategory.AI_ASSIGNMENT
        elif name_lower.startswith('p') and name_lower[1:].isdigit():
            return LabelCategory.PRIORITY
        elif name_lower in ['in-progress', 'blocked', 'review']:
            return LabelCategory.STATUS
        elif name_lower in ['automated', 'manual']:
            return LabelCategory.WORKFLOW
        
        return LabelCategory.WORKFLOW  # 기본값


# 사용 예시
if __name__ == "__main__":
    adapter = GitHubLabelManagementAdapter()
    
    # 필수 라벨 동기화
    print("=== 필수 라벨 동기화 ===")
    result = adapter.sync_labels()
    print(f"생성: {result['created']}")
    print(f"건너뜀: {len(result['skipped'])}개")
    print(f"전체 라벨: {result['total_labels']}개")
    
    # 라벨 제안 테스트
    print("\n=== 라벨 제안 테스트 ===")
    test_title = "[Story] PR 자동화 시스템 구현"
    test_body = "AI: Gemini가 설계하고 긴급 처리 필요"
    
    suggested = adapter.suggest_labels(test_title, test_body)
    print(f"제안된 라벨: {suggested}")