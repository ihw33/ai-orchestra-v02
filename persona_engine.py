#!/usr/bin/env python3
"""
페르소나 엔진 - 메모리 부담 없이 실행
사용법: python persona_engine.py --task "대시보드 만들기" --team "Emma,Rajiv,Anna"
"""

import random
import json
from datetime import datetime
from typing import Dict, List

class PersonaEngine:
    """페르소나 동적 생성 엔진"""
    
    # 기본 페르소나 데이터 (메모리 절약)
    PERSONAS = {
        "Emma": {
            "role": "CPO",
            "nationality": "British",
            "mbti": "ENFP",
            "base_style": "Enthusiastic! Users love it! 🎉"
        },
        "Rajiv": {
            "role": "Engineering",
            "nationality": "Indian", 
            "mbti": "ISTP",
            "base_style": "Done. PR ready."
        },
        "Marcus": {
            "role": "CTO",
            "nationality": "Korean-American",
            "mbti": "INTJ",
            "base_style": "아키텍처 관점에서..."
        },
        "Anna": {
            "role": "QA",
            "nationality": "Polish",
            "mbti": "ISTJ",
            "base_style": "버그 발견. 상세 리포트."
        },
        "Yui": {
            "role": "Frontend",
            "nationality": "Japanese",
            "mbti": "ISFP",
            "base_style": "픽셀 단위로 완벽하게 🎨"
        },
        "Olaf": {
            "role": "DevOps",
            "nationality": "German",
            "mbti": "ISTJ",
            "base_style": "Genau. 14:00 배포."
        }
    }
    
    MOODS = [
        ("energetic", "💪", 1.3),
        ("tired", "😴", 0.8),
        ("focused", "🎯", 1.2),
        ("creative", "🎨", 1.1),
        ("grumpy", "😤", 0.9)
    ]
    
    RANDOM_EVENTS = [
        "☕ 커피 엎음!",
        "🐱 고양이가 키보드에!",
        "💡 유레카!",
        "🍕 피자 도착!",
        "🐛 버그 발견!",
        None, None, None  # 70% 확률로 이벤트 없음
    ]

    def __init__(self):
        self.context = self._get_context()
        
    def _get_context(self) -> Dict:
        """현재 컨텍스트 생성"""
        now = datetime.now()
        weekday = ["월", "화", "수", "목", "금", "토", "일"][now.weekday()]
        
        return {
            "date": now.strftime("%Y-%m-%d"),
            "time": now.strftime("%H:%M"),
            "weekday": weekday,
            "is_friday": weekday == "금",
            "is_monday": weekday == "월",
            "hour": now.hour
        }
    
    def generate_response(self, name: str, task: str) -> str:
        """페르소나 응답 생성"""
        if name not in self.PERSONAS:
            return f"{name}: 작업 완료"
        
        persona = self.PERSONAS[name]
        mood = random.choice(self.MOODS)
        event = random.choice(self.RANDOM_EVENTS)
        
        # 기본 응답
        response = f"{mood[1]} "
        
        # 작업 완료 메시지
        if persona["role"] == "CPO":
            response += f"User research for {task} done! "
            if self.context["is_friday"]:
                response += "TGIF! Pub anyone? 🍺"
        elif persona["role"] == "Engineering":
            response += f"{task} implemented. "
            if mood[0] == "tired":
                response += "Need coffee. PR tomorrow."
            else:
                response += f"PR #{random.randint(100,999)}."
        elif persona["role"] == "QA":
            response += f"Tested {task}. "
            bugs = random.randint(0, 10)
            response += f"{bugs} bugs found."
        elif persona["role"] == "Frontend":
            response += f"{task} UI ready. "
            if mood[0] == "creative":
                response += "Added animations! ✨"
        elif persona["role"] == "DevOps":
            response += f"Deployment ready. "
            response += f"ETA: {14 if self.context['hour'] < 14 else 'tomorrow 14'}:00"
        else:
            response += f"{task} 완료."
        
        # 랜덤 이벤트 추가
        if event:
            response += f" ({event})"
        
        return f"**{name}**: {response}"
    
    def assign_tasks(self, main_task: str, team: List[str]) -> Dict:
        """팀에 작업 할당"""
        assignments = {}
        
        # 역할별 자동 작업 분배
        task_map = {
            "CPO": "UX 리서치 및 사용자 스토리",
            "Engineering": "백엔드 API 구현", 
            "QA": "테스트 케이스 작성 및 실행",
            "Frontend": "UI 컴포넌트 개발",
            "DevOps": "배포 파이프라인 준비",
            "CTO": "아키텍처 검토"
        }
        
        for member in team:
            if member in self.PERSONAS:
                role = self.PERSONAS[member]["role"]
                subtask = task_map.get(role, main_task)
                assignments[member] = {
                    "task": subtask,
                    "response": self.generate_response(member, subtask)
                }
        
        return assignments

def main():
    """CLI 실행"""
    import argparse
    
    parser = argparse.ArgumentParser()
    parser.add_argument("--task", required=True, help="작업 내용")
    parser.add_argument("--team", default="Emma,Rajiv,Anna,Yui", help="팀원 (쉼표 구분)")
    parser.add_argument("--format", default="markdown", choices=["markdown", "json"])
    
    args = parser.parse_args()
    
    engine = PersonaEngine()
    team = args.team.split(",")
    assignments = engine.assign_tasks(args.task, team)
    
    if args.format == "json":
        print(json.dumps(assignments, ensure_ascii=False, indent=2))
    else:
        print(f"# 📋 작업 할당: {args.task}")
        print(f"**날짜**: {engine.context['date']} {engine.context['weekday']}요일")
        print()
        for member, data in assignments.items():
            print(f"### {member}")
            print(f"- 작업: {data['task']}")
            print(f"- {data['response']}")
            print()

if __name__ == "__main__":
    main()