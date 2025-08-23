#!/usr/bin/env python3
"""
Allow 요청 자동 처리 시스템
PL Bot과 연동하여 Allow 요청을 감지하고 자동으로 처리
"""
import subprocess
import time
import json
from datetime import datetime

class AllowHandler:
    def __init__(self):
        self.allow_patterns = [
            "allow request",
            "permission required",
            "waiting for approval",
            "needs authorization",
            "blocked by allow"
        ]
        self.auto_allow_list = [
            "file read",
            "file write", 
            "bash command",
            "api call"
        ]
        
    def detect_allow_request(self, output_text):
        """Allow 요청 패턴 감지"""
        lower_text = output_text.lower()
        for pattern in self.allow_patterns:
            if pattern in lower_text:
                return True
        return False
        
    def parse_allow_type(self, output_text):
        """Allow 요청 타입 파악"""
        if "file" in output_text.lower():
            if "read" in output_text.lower():
                return "file_read"
            elif "write" in output_text.lower():
                return "file_write"
        elif "bash" in output_text.lower() or "command" in output_text.lower():
            return "bash_command"
        elif "api" in output_text.lower():
            return "api_call"
        return "unknown"
        
    def should_auto_allow(self, allow_type):
        """자동 승인 가능 여부 판단"""
        return allow_type in self.auto_allow_list
        
    def send_allow_response(self, session_id, allow=True):
        """Allow 응답 전송"""
        response = "y" if allow else "n"
        
        # AppleScript로 응답 전송
        script = f'''
        tell application "iTerm2"
            tell current window
                tell session id "{session_id}"
                    write text "{response}"
                end tell
            end tell
        end tell
        '''
        
        try:
            subprocess.run(['osascript', '-e', script], check=True)
            return True
        except:
            return False
            
    def handle_allow_request(self, ai_name, session_id, output_text):
        """Allow 요청 처리 메인 로직"""
        print(f"\n🔔 Allow 요청 감지: {ai_name}")
        
        # 1. Allow 타입 파악
        allow_type = self.parse_allow_type(output_text)
        print(f"   타입: {allow_type}")
        
        # 2. 자동 승인 가능 체크
        if self.should_auto_allow(allow_type):
            print(f"   ✅ 자동 승인 가능")
            if self.send_allow_response(session_id, allow=True):
                print(f"   ✅ Allow 승인 완료")
                return {"status": "auto_allowed", "type": allow_type}
        else:
            print(f"   ⚠️ Thomas 승인 필요")
            return {"status": "manual_required", "type": allow_type}
            
    def batch_allow_all(self, pending_allows):
        """대기 중인 모든 Allow 일괄 처리"""
        results = []
        for item in pending_allows:
            result = self.handle_allow_request(
                item['ai_name'],
                item['session_id'],
                item['output']
            )
            results.append(result)
            time.sleep(0.5)  # 안정성을 위한 딜레이
        return results

# 테스트 코드
if __name__ == "__main__":
    handler = AllowHandler()
    
    # 테스트 케이스
    test_cases = [
        "Allow request: Read file /Users/test.py",
        "Permission required for bash command: git push",
        "Waiting for approval to call API endpoint"
    ]
    
    for test in test_cases:
        if handler.detect_allow_request(test):
            allow_type = handler.parse_allow_type(test)
            auto = handler.should_auto_allow(allow_type)
            print(f"테스트: {test[:30]}...")
            print(f"  타입: {allow_type}, 자동승인: {auto}")