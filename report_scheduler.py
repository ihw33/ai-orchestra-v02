#!/usr/bin/env python3
"""
📝 업무일지 자동 알림 시스템
마감 시간 전에 알림을 주고 작성 상태를 체크
"""

import json
from datetime import datetime, timedelta
from pathlib import Path

class ReportScheduler:
    """업무일지 작성 스케줄러"""
    
    def __init__(self):
        self.base_dir = Path(__file__).parent
        
    def check_report_status(self):
        """오늘 작성해야 할 보고서 체크"""
        now = datetime.now()
        reports_needed = []
        
        # 일일 보고서 (매일)
        daily_file = self.base_dir / f"DAILY_REPORT_{now.strftime('%Y%m%d')}.md"
        if not daily_file.exists():
            deadline = now.replace(hour=23, minute=59)
            time_left = deadline - now
            reports_needed.append({
                "type": "일일 업무일지",
                "deadline": "오늘 밤 12시",
                "time_left": f"{time_left.seconds // 3600}시간 {(time_left.seconds % 3600) // 60}분",
                "file": str(daily_file)
            })
        
        # 주간 보고서 (일요일)
        if now.weekday() == 6:  # 일요일
            weekly_file = self.base_dir / f"WEEKLY_REPORT_{now.strftime('%Y%m%d')}.md"
            if not weekly_file.exists():
                reports_needed.append({
                    "type": "주간 업무일지",
                    "deadline": "오늘 밤 12시",
                    "file": str(weekly_file)
                })
        
        # 월간 보고서 (말일)
        next_day = now + timedelta(days=1)
        if next_day.month != now.month:  # 오늘이 말일
            monthly_file = self.base_dir / f"MONTHLY_REPORT_{now.strftime('%Y%m')}.md"
            if not monthly_file.exists():
                reports_needed.append({
                    "type": "월간 업무일지",
                    "deadline": "오늘 밤 12시",
                    "file": str(monthly_file)
                })
        
        return reports_needed
    
    def generate_reminder(self):
        """작성 알림 생성"""
        reports = self.check_report_status()
        
        if reports:
            print("\n⚠️  업무일지 작성 필요!")
            print("=" * 40)
            for report in reports:
                print(f"📝 {report['type']}")
                print(f"   마감: {report['deadline']}")
                if 'time_left' in report:
                    print(f"   남은 시간: {report['time_left']}")
                print()
            return True
        else:
            print("✅ 오늘 작성할 업무일지 없음")
            return False
    
    def auto_generate_template(self, report_type):
        """보고서 템플릿 자동 생성"""
        now = datetime.now()
        
        if report_type == "daily":
            return f"""# 📊 일일 업무일지 - {now.strftime('%Y년 %m월 %d일')}

## 🎯 오늘의 주요 작업
- [ ] 

## ✅ 완료된 작업
- 

## 🔄 진행 중인 작업
- 

## 💡 발견/개선사항
- 

## 📅 내일 계획
- 

---
*작성 시간: {now.strftime('%Y-%m-%d %H:%M')}*
*작성자: PM Claude*
"""
        
        elif report_type == "weekly":
            return f"""# 📊 주간 업무일지 - {now.strftime('%Y년 %m월 %d주차')}

## 🎯 이번 주 핵심 성과
- 

## 📈 주요 지표
- 작업 완료: X건
- PR 머지: X건
- 이슈 해결: X건

## 👥 팀 활동
- 

## 💡 개선 제안
- 

## 📅 다음 주 계획
- 

---
*작성 시간: {now.strftime('%Y-%m-%d %H:%M')}*
"""

def main():
    scheduler = ReportScheduler()
    
    # 현재 상태 체크
    needs_report = scheduler.generate_reminder()
    
    # 자동 템플릿 제공
    if needs_report:
        print("\n💡 템플릿을 생성할까요? (y/n)")
        # 실제로는 자동 생성 로직

if __name__ == "__main__":
    main()