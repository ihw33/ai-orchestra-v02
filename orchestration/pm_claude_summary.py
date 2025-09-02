#!/usr/bin/env python3
"""
PM Claude가 AI들의 개별 보고를 받아서 최종 정리
"""

import subprocess
import json
import re
from datetime import datetime

class PMClaudeSummary:
    """PM Claude의 최종 정리"""
    
    def __init__(self):
        self.issue_number = 101
        self.repo = "ihw33/ai-orchestra-v02"
    
    def read_ai_comments(self):
        """각 AI가 작성한 코멘트 읽기"""
        
        print("📖 PM Claude: AI들의 보고서 읽는 중...")
        
        # GitHub에서 최근 코멘트들 가져오기
        cmd = f"gh issue view {self.issue_number} -R {self.repo} --comments --json comments"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        
        if result.returncode == 0:
            data = json.loads(result.stdout)
            comments = data.get('comments', [])
            
            # 최근 4개 코멘트 (각 AI의 보고)
            recent_comments = comments[-4:] if len(comments) >= 4 else comments
            
            reports = {
                'backend': None,
                'devil': None,
                'performance': None,
                'qa': None
            }
            
            for comment in recent_comments:
                body = comment.get('body', '')
                
                # 각 AI 식별
                if 'Backend Developer' in body:
                    reports['backend'] = self.parse_backend_report(body)
                elif 'Devil' in body or '최예리' in body:
                    reports['devil'] = self.parse_devil_report(body)
                elif 'Performance' in body or 'Sarah' in body:
                    reports['performance'] = self.parse_performance_report(body)
                elif 'QA' in body or '박민수' in body:
                    reports['qa'] = self.parse_qa_report(body)
            
            return reports
        
        return None
    
    def parse_backend_report(self, body):
        """Backend 보고서 파싱"""
        return {
            'status': 'completed' if '완료' in body else 'in_progress',
            'functions': 3 if 'reverse_string' in body else 0,
            'tests': 'included' if '테스트' in body else 'missing'
        }
    
    def parse_devil_report(self, body):
        """Devil's Advocate 보고서 파싱"""
        issues = []
        if 'None' in body:
            issues.append('None 입력 미처리')
        if '공백' in body:
            issues.append('공백 처리 문제')
        if '유니코드' in body:
            issues.append('유니코드 이슈')
        
        return {
            'issues_found': len(issues),
            'critical': issues,
            'verdict': 'conditional' if issues else 'pass'
        }
    
    def parse_performance_report(self, body):
        """Performance 보고서 파싱"""
        # 시간 추출 (예: 0.0007ms)
        times = re.findall(r'(\d+\.\d+)ms', body)
        
        return {
            'all_under_1ms': all(float(t) < 1.0 for t in times) if times else False,
            'complexity': 'O(n)' if 'O(n)' in body else 'unknown',
            'verdict': 'pass' if 'PASS' in body else 'fail'
        }
    
    def parse_qa_report(self, body):
        """QA 보고서 파싱"""
        return {
            'coverage': 92 if '92%' in body else 0,
            'approved': 'APPROVED' in body,
            'conditional': '조건부' in body
        }
    
    def create_summary(self, reports):
        """PM의 최종 요약"""
        
        summary = f"""## 🎯 PM Claude 최종 정리

**Issue #101 작업 상황**

### 📊 AI 보고 요약

#### Backend Developer
- 상태: {'✅ 완료' if reports['backend']['status'] == 'completed' else '⏳ 진행중'}
- 함수: {reports['backend']['functions']}/3 구현
- 테스트: {reports['backend']['tests']}

#### Devil's Advocate 최예리  
- 발견 이슈: {reports['devil']['issues_found']}개
- 주요 문제: {', '.join(reports['devil']['critical'][:3])}
- 판정: {reports['devil']['verdict']}

#### Performance Tester Sarah
- 성능: {'✅ 모두 < 1ms' if reports['performance']['all_under_1ms'] else '❌ 일부 초과'}
- 복잡도: {reports['performance']['complexity']}
- 판정: {reports['performance']['verdict']}

#### QA Lead 박민수
- 커버리지: {reports['qa']['coverage']}%
- 최종: {'✅ 승인' if reports['qa']['approved'] else '❌ 거부'}
- 조건: {'조건부' if reports['qa']['conditional'] else '무조건'}

### 🎬 PM 결정

**다음 단계:**
"""
        
        # PM의 판단
        if reports['qa']['approved']:
            if reports['devil']['issues_found'] > 3:
                summary += """
1. ✅ PR 머지 승인
2. ⚠️ Issue #102 생성 - Devil's Advocate 이슈 해결
3. 📅 다음 스프린트에서 개선"""
            else:
                summary += """
1. ✅ PR 즉시 머지
2. 📝 개선사항 백로그 추가"""
        else:
            summary += """
1. ❌ 재작업 필요
2. 🔄 AI 팀 재실행
3. 📋 체크리스트 재검증"""
        
        summary += f"""

---
*PM Claude Summary - {datetime.now().strftime('%Y-%m-%d %H:%M')}*"""
        
        return summary
    
    def post_summary(self, summary):
        """GitHub에 요약 게시"""
        
        # 임시 파일에 저장
        with open('/tmp/pm_summary.md', 'w') as f:
            f.write(summary)
        
        # GitHub에 코멘트
        cmd = f"gh issue comment {self.issue_number} -R {self.repo} --body-file /tmp/pm_summary.md"
        subprocess.run(cmd, shell=True)
        
        print("✅ PM 요약 게시 완료")


if __name__ == "__main__":
    pm = PMClaudeSummary()
    
    # 시뮬레이션 (실제로는 AI들이 먼저 코멘트 작성)
    reports = {
        'backend': {'status': 'completed', 'functions': 3, 'tests': 'included'},
        'devil': {'issues_found': 6, 'critical': ['None 처리', '공백 문제', '유니코드'], 'verdict': 'conditional'},
        'performance': {'all_under_1ms': True, 'complexity': 'O(n)', 'verdict': 'pass'},
        'qa': {'coverage': 92, 'approved': True, 'conditional': True}
    }
    
    summary = pm.create_summary(reports)
    print(summary)
    
    # 실제 환경에서는:
    # 1. AI들이 각자 코멘트 작성
    # 2. PM이 읽고 요약
    # reports = pm.read_ai_comments()
    # summary = pm.create_summary(reports)
    # pm.post_summary(summary)