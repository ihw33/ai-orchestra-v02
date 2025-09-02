#!/usr/bin/env python3
"""
PM Monitor Node - Issue 진행 상황 모니터링 및 다음 작업 지시
"""

import subprocess
import json
import time
from datetime import datetime
from typing import Dict, List, Optional

class PMMonitorNode:
    """PM 모니터링 노드"""
    
    def __init__(self):
        self.node_type = "PM_MONITOR"
        self.issue_number = 34
        self.repo = "ihw33/iwl-v5-rebuild"
        
    def check_issue_status(self) -> Dict:
        """Issue 상태 및 최신 댓글 확인"""
        cmd = f"gh issue view {self.issue_number} -R {self.repo} --json comments,state"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        
        if result.returncode == 0:
            return json.loads(result.stdout)
        return {}
        
    def analyze_progress(self, issue_data: Dict) -> Dict:
        """진행 상황 분석"""
        progress = {
            "main_platform": False,
            "kb_system": False,
            "llm_service": False,
            "completed_tasks": [],
            "pending_tasks": []
        }
        
        # 댓글에서 완료 보고 찾기
        for comment in issue_data.get('comments', []):
            body = comment.get('body', '')
            if 'Main Platform' in body and '완료' in body:
                progress['main_platform'] = True
                progress['completed_tasks'].append('Main Platform 환경 설정')
            if 'KB System' in body and '완료' in body:
                progress['kb_system'] = True
                progress['completed_tasks'].append('KB System API 구동')
            if 'LLM Service' in body and '완료' in body:
                progress['llm_service'] = True
                progress['completed_tasks'].append('LLM Service API 구축')
                
        # 다음 작업 결정
        if progress['main_platform'] and not progress['kb_system']:
            progress['pending_tasks'].append('KB System 통합')
        if progress['kb_system'] and not progress['llm_service']:
            progress['pending_tasks'].append('LLM Service 통합')
        if all([progress['main_platform'], progress['kb_system'], progress['llm_service']]):
            progress['pending_tasks'].append('전체 통합 테스트')
            
        return progress
        
    def generate_next_instruction(self, progress: Dict) -> Optional[str]:
        """다음 작업 지시 생성"""
        if not progress['pending_tasks']:
            return None
            
        next_task = progress['pending_tasks'][0]
        
        instructions = {
            'KB System 통합': {
                'session': 'KB Claude',
                'command': 'Main Platform과 API 연결 구현. REST 엔드포인트 테스트'
            },
            'LLM Service 통합': {
                'session': 'LLM Claude',
                'command': 'Main Platform과 LLM API 연결. 프롬프트 파이프라인 구축'
            },
            '전체 통합 테스트': {
                'session': 'Main Claude',
                'command': '전체 시스템 통합 테스트 실행. E2E 시나리오 검증'
            }
        }
        
        return instructions.get(next_task)
        
    def send_instruction(self, instruction: Dict):
        """AppleScript를 통한 작업 지시 전송"""
        if not instruction:
            return
            
        applescript = f'''
        tell application "iTerm"
            tell current window
                tell current tab
                    repeat with s in sessions
                        if name of s contains "{instruction['session']}" then
                            tell s
                                write text "claude -p '{instruction['command']}'" newline no
                                delay 0.1
                                write text ""
                            end tell
                        end if
                    end repeat
                end tell
            end tell
        end tell
        '''
        
        subprocess.run(['osascript', '-e', applescript])
        
    def execute(self) -> Dict:
        """노드 실행"""
        print(f"🔍 PM Monitor Node 실행 - {datetime.now()}")
        
        # Issue 상태 확인
        issue_data = self.check_issue_status()
        
        # 진행 상황 분석
        progress = self.analyze_progress(issue_data)
        
        # 다음 작업 지시 생성
        next_instruction = self.generate_next_instruction(progress)
        
        if next_instruction:
            print(f"📌 다음 작업 지시: {next_instruction}")
            self.send_instruction(next_instruction)
            
        return {
            "node_type": self.node_type,
            "timestamp": str(datetime.now()),
            "progress": progress,
            "next_instruction": next_instruction,
            "status": "SUCCESS"
        }

# Node로 등록
PM_MONITOR = PMMonitorNode()