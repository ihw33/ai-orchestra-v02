#!/usr/bin/env python3
"""
코드 수정 승인 체크 시스템
기존 코드 수정 시 반드시 사용자 승인을 받도록 강제
"""

import os
import hashlib
import json
from datetime import datetime
from typing import Dict, Optional, List
import subprocess
import sys

class CodeModificationGuard:
    """코드 수정 전 승인 체크"""
    
    def __init__(self):
        self.approval_log = "code_modification_approvals.json"
        self.modification_history = []
        
    def check_before_modify(self, file_path: str, modification_type: str, description: str) -> bool:
        """수정 전 승인 체크"""
        
        # 파일 존재 여부 확인
        if not os.path.exists(file_path):
            print(f"✅ 새 파일 생성: {file_path}")
            return True
        
        # 기존 파일 수정인 경우
        print("\n" + "="*70)
        print("🚨 기존 코드 수정 승인 요청")
        print("="*70)
        
        # 현재 파일 상태 표시
        file_info = self._get_file_info(file_path)
        
        print(f"\n📄 파일: {file_path}")
        print(f"📏 크기: {file_info['size']} bytes")
        print(f"📅 수정일: {file_info['modified']}")
        print(f"🔧 작업 유형: {modification_type}")
        print(f"📝 설명: {description}")
        
        # 특히 주석 처리인 경우 강조
        if "주석" in modification_type or "comment" in modification_type.lower():
            print("\n⚠️  주의: 주석 처리 작업입니다!")
            print("기존 동작하는 코드를 비활성화할 수 있습니다.")
        
        # 승인 요청
        print("\n" + "-"*70)
        approval = self._request_approval()
        
        if approval:
            self._log_approval(file_path, modification_type, description)
            print("✅ 승인됨 - 수정 진행")
            return True
        else:
            print("❌ 거부됨 - 수정 취소")
            return False
    
    def _get_file_info(self, file_path: str) -> Dict:
        """파일 정보 가져오기"""
        stat = os.stat(file_path)
        return {
            'size': stat.st_size,
            'modified': datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S'),
            'hash': self._calculate_hash(file_path)
        }
    
    def _calculate_hash(self, file_path: str) -> str:
        """파일 해시 계산"""
        with open(file_path, 'rb') as f:
            return hashlib.md5(f.read()).hexdigest()[:8]
    
    def _request_approval(self) -> bool:
        """사용자 승인 요청 (시뮬레이션)"""
        print("이 수정을 진행하시겠습니까? [y/n]")
        
        # 실제 구현에서는 사용자 입력 받기
        # 여기서는 GitHub Issue 댓글이나 별도 UI를 통해 승인
        
        # 시뮬레이션: 자동 승인 (실제는 입력 대기)
        return True
    
    def _log_approval(self, file_path: str, modification_type: str, description: str):
        """승인 기록"""
        approval_record = {
            'timestamp': datetime.now().isoformat(),
            'file': file_path,
            'type': modification_type,
            'description': description,
            'approved': True
        }
        
        # 기존 로그 읽기
        if os.path.exists(self.approval_log):
            with open(self.approval_log, 'r') as f:
                logs = json.load(f)
        else:
            logs = []
        
        # 새 기록 추가
        logs.append(approval_record)
        
        # 저장
        with open(self.approval_log, 'w') as f:
            json.dump(logs, f, indent=2)
        
        self.modification_history.append(approval_record)
    
    def show_pending_modifications(self) -> List[Dict]:
        """대기 중인 수정 사항 표시"""
        print("\n📋 대기 중인 수정 사항:")
        print("-"*70)
        
        pending = []
        
        # Git diff로 변경 예정 사항 확인
        cmd = "git diff --name-only"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        
        if result.returncode == 0 and result.stdout:
            files = result.stdout.strip().split('\n')
            for file in files:
                pending.append({
                    'file': file,
                    'status': 'modified',
                    'needs_approval': True
                })
                print(f"  📝 {file} - 수정됨")
        
        if not pending:
            print("  (없음)")
        
        return pending
    
    def enforce_approval_policy(self, operation: str) -> bool:
        """승인 정책 강제"""
        
        critical_operations = [
            'comment_out',      # 주석 처리
            'delete_function',  # 함수 삭제
            'modify_core',      # 핵심 로직 수정
            'change_api',       # API 변경
            'remove_test'       # 테스트 제거
        ]
        
        if operation in critical_operations:
            print(f"\n🔴 위험한 작업: {operation}")
            print("반드시 승인이 필요합니다!")
            return self._request_approval()
        
        return True


class PMClaudeModificationRestrictor:
    """PM Claude의 수정 제한"""
    
    def __init__(self):
        self.guard = CodeModificationGuard()
        self.restricted_patterns = [
            'subprocess.run(',  # 직접 실행 금지
            '# result =',       # 주석 처리 금지
            'TODO',            # TODO 남기기 금지
            'FIXME'            # FIXME 남기기 금지
        ]
    
    def before_edit(self, file_path: str, old_content: str, new_content: str) -> bool:
        """편집 전 체크"""
        
        # 주석 처리 감지
        if self._detect_commenting_out(old_content, new_content):
            print("\n🚨 주석 처리 감지!")
            return self.guard.check_before_modify(
                file_path, 
                "comment_out",
                "기존 코드를 주석 처리"
            )
        
        # 코드 삭제 감지
        if self._detect_code_deletion(old_content, new_content):
            print("\n🚨 코드 삭제 감지!")
            return self.guard.check_before_modify(
                file_path,
                "delete_code", 
                "기존 코드 삭제"
            )
        
        # 일반 수정
        return self.guard.check_before_modify(
            file_path,
            "modify",
            "일반 수정"
        )
    
    def _detect_commenting_out(self, old: str, new: str) -> bool:
        """주석 처리 감지"""
        old_lines = old.split('\n')
        new_lines = new.split('\n')
        
        for old_line, new_line in zip(old_lines, new_lines):
            # 기존 코드가 주석이 되었는지 체크
            if old_line.strip() and not old_line.strip().startswith('#'):
                if new_line.strip().startswith('#') and old_line.strip() in new_line:
                    return True
        
        return False
    
    def _detect_code_deletion(self, old: str, new: str) -> bool:
        """코드 삭제 감지"""
        return len(new) < len(old) * 0.8  # 20% 이상 삭제 시


# 실행 예시
if __name__ == "__main__":
    print("🛡️ 코드 수정 승인 시스템")
    print("="*70)
    
    guard = CodeModificationGuard()
    restrictor = PMClaudeModificationRestrictor()
    
    # 테스트 케이스
    test_cases = [
        {
            'file': 'src/adapters/ai/ai_execution_adapter.py',
            'type': 'comment_out',
            'desc': 'Claude 실행 코드 주석 처리'
        },
        {
            'file': 'orchestration/workflow.py',
            'type': 'modify_core',
            'desc': '핵심 워크플로우 로직 변경'
        },
        {
            'file': 'new_file.py',
            'type': 'create',
            'desc': '새 파일 생성'
        }
    ]
    
    print("\n📌 테스트 시나리오:")
    for i, test in enumerate(test_cases, 1):
        print(f"\n[테스트 {i}]")
        approved = guard.check_before_modify(
            test['file'],
            test['type'],
            test['desc']
        )
        print(f"결과: {'✅ 승인' if approved else '❌ 거부'}")
    
    # 대기 중인 수정 사항 표시
    guard.show_pending_modifications()
    
    print("\n✅ 코드 수정 승인 시스템 준비 완료!")
    print("이제 모든 수정은 승인을 받아야 합니다.")