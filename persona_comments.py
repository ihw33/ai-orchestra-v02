#!/usr/bin/env python3
"""
페르소나 코멘트 생성기 - 재미있고 감동적인 PR/Issue 코멘트
핵심: 업무 + 인간미 + 팀워크
"""

import random
import json
from datetime import datetime

class PersonaComments:
    """재미와 감동이 있는 코멘트 생성"""
    
    def generate_pr_comment(self, pr_info, persona_name):
        """PR 코멘트 생성 - 업무 + 인간미"""
        
        templates = {
            "Emma": [
                "✨ {task} 리뷰 완료! Users are gonna LOVE this! 🎉\n\n"
                "**좋은 점:**\n"
                "- UX가 정말 직관적이에요\n"
                "- 사용자 피드백 완벽 반영 👍\n\n"
                "**제안:**\n"
                "- 모바일에서 버튼 조금 더 크게?\n\n"
                "P.S. 어제 그 카페 가봤는데 라떼 진짜 맛있더라! ☕",
                
                "OMG! {task} 대박이에요! 🚀\n\n"
                "진짜 이런 기능 기다렸어요. 유저 테스트 그룹에서\n"
                "벌써 난리났다니까요? NPS 스코어 72→85로 급상승!\n\n"
                "근데 혹시... 다크모드도 고려해볼까요? 🌙\n"
                "(요즘 다크모드 없으면 서운해하는 유저들이...)"
            ],
            
            "Rajiv": [
                "Code reviewed. {task} implementation solid.\n\n"
                "```python\n"
                "# Performance: O(n) → O(log n)\n"
                "# Memory: -40%\n"
                "# Coffee consumed: 3 cups\n"
                "```\n\n"
                "One concern: Line 234 might cause race condition.\n"
                "Fix: Add mutex lock.\n\n"
                "BTW, India won cricket match. Productivity +20% today. 🏏",
                
                "LGTM. {task} done right.\n\n"
                "Stats:\n"
                "- Lines: 420 (nice)\n"
                "- Test coverage: 94%\n"
                "- Bugs: 0\n\n"
                "PR #{pr_number}. Merging in 5... 4... 3..."
            ],
            
            "Anna": [
                "🔍 {task} 테스트 완료!\n\n"
                "**테스트 결과:**\n"
                "✅ Unit tests: 156/156 passed\n"
                "✅ Integration: 43/43 passed\n"
                "⚠️ E2E: 1 flaky test (재실행하면 통과)\n\n"
                "**발견한 엣지 케이스:**\n"
                "- 사용자가 버튼을 0.1초 안에 10번 클릭하면... (누가 그럴까요? 😅)\n"
                "- 해결: Debounce 추가\n\n"
                "P.S. 할머니가 폴란드에서 피에로기 레시피 보내주셨어요. 다음 주 팀 런치? 🥟",
                
                "버그 사냥 완료! 🎯 {task}\n\n"
                "23개 테스트 시나리오 모두 통과!\n"
                "특히 새벽 3시 동시접속 1000명 시뮬레이션도 OK.\n\n"
                "근데... 한 가지 발견:\n"
                "금요일 오후 4시 이후 커밋은 버그 확률 34% 상승 📊\n"
                "(통계는 거짓말하지 않아요)"
            ],
            
            "Marcus": [
                "아키텍처 리뷰 완료했습니다. {task}\n\n"
                "**장점:**\n"
                "- 확장 가능한 구조 ✅\n"
                "- 클린 아키텍처 원칙 준수 ✅\n"
                "- 10년 후에도 유지보수 가능 ✅\n\n"
                "**제안:**\n"
                "SOLID 원칙 중 DIP를 조금 더 적용하면 좋을 것 같습니다.\n\n"
                "오늘 점심 김치찌개 어떠세요? 회사 앞 새로 생긴 집 괜찮대요. 🍲\n"
                "12시 로비에서 만나요!",
                
                "{task} 검토했습니다.\n\n"
                "이 설계로 가면 3년 후 트래픽 100배 증가해도 문제없습니다.\n"
                "실제로 2015년에 비슷한 아키텍처로 성공한 사례가 있죠.\n\n"
                "**기술 스택 제안:**\n"
                "- 현재: Good\n"
                "- 제안: Better (Redis 캐싱 추가)\n"
                "- 미래: Best (마이크로서비스 전환)\n\n"
                "P.S. 아들이 파이썬 배우기 시작했는데, 첫 프로그램이 'Hello Dad'... 🥺"
            ],
            
            "Yui": [
                "UI 작업 완료했습니다! {task} 🎨\n\n"
                "**디자인 포인트:**\n"
                "- 애니메이션: 0.3초 → 0.15초 (더 스냅피!)\n"
                "- 색상: #3B82F6 (신뢰감 있는 파란색)\n"
                "- 여백: 황금비율 적용 ✨\n\n"
                "모바일에서 특히 예쁘게 나왔어요!\n"
                "벚꽃 시즌이라 핑크 포인트도 살짝... 🌸\n\n"
                "픽셀 하나하나 신경썼습니다!",
                
                "はい! {task} UI 완성! ✨\n\n"
                "일본 미니멀리즘 스타일 적용했어요:\n"
                "- 여백의 미\n"
                "- 절제된 애니메이션\n"
                "- 직관적인 플로우\n\n"
                "다크모드도 완벽 지원! 🌙\n"
                "(새벽 코딩할 때 눈 아프지 않게...)"
            ],
            
            "Olaf": [
                "Deployment ready. {task}\n\n"
                "**배포 계획:**\n"
                "- 시간: 정확히 14:00 KST\n"
                "- 방식: Blue-Green\n"
                "- 다운타임: 0초\n"
                "- 롤백 시간: 30초 이내\n\n"
                "German engineering precision. 🇩🇪\n\n"
                "P.S. 독일 맥주 축제 티켓 2장 남았는데... 관심 있으신 분? 🍺",
                
                "CI/CD pipeline optimized. {task}\n\n"
                "빌드 시간: 12분 → 3분 (75% 개선)\n"
                "자동화율: 99.7%\n"
                "수동 작업: 최종 승인 버튼만\n\n"
                "Alles ist bereit! (모든 준비 완료!)"
            ]
        }
        
        # 페르소나별 템플릿 선택
        if persona_name in templates:
            template = random.choice(templates[persona_name])
            comment = template.format(
                task=pr_info.get('title', 'Task'),
                pr_number=pr_info.get('number', '999')
            )
            
            # 시간대별 추가 코멘트
            hour = datetime.now().hour
            if hour < 10:
                comment += "\n\n☕ (아침이라 커피 한 잔 더...)"
            elif hour > 22:
                comment += "\n\n🌙 (야근 중... 하지만 재밌어서 OK!)"
            elif datetime.now().weekday() == 4:  # 금요일
                comment += "\n\n🎉 TGIF! 불금 준비 완료!"
            
            return comment
        
        return f"{persona_name}: {pr_info.get('title', 'Task')} 검토 완료!"
    
    def generate_issue_thread(self, issue_info):
        """이슈 스레드 - 팀원들 대화"""
        
        thread = []
        
        # 첫 코멘트 (문제 인식)
        thread.append({
            "author": "Emma",
            "comment": "어? 이거 유저들이 많이 요청했던 기능이에요! 🎯\n"
                      "지난주 설문조사에서 73%가 원했던 거잖아요?\n"
                      "우선순위 높여야 할 것 같은데..."
        })
        
        # 기술 검토
        thread.append({
            "author": "Rajiv",
            "comment": "@Emma Feasible. 2-3 days max.\n"
                      "But need to refactor auth module first.\n"
                      "Coffee ready. Let's do this. ☕"
        })
        
        # 우려사항
        thread.append({
            "author": "Anna",
            "comment": "@Rajiv auth 모듈 건드리면 테스트 200개 다시 돌려야 해요... 😅\n"
                      "하지만 이참에 테스트 커버리지 90%로 올릴 기회!\n"
                      "주말에 할머니 집 가야 하는데... 금요일까지 가능?"
        })
        
        # 디자인 의견
        thread.append({
            "author": "Yui",
            "comment": "UI 목업 만들어봤어요! 🎨\n"
                      "```\n"
                      "[==예쁜 버튼==] [==더 예쁜 버튼==]\n"
                      "```\n"
                      "Material Design 3 적용하면 더 좋을 것 같아요!"
        })
        
        # CTO 결정
        thread.append({
            "author": "Marcus",
            "comment": "좋습니다. 진행하죠.\n\n"
                      "**액션 플랜:**\n"
                      "1. Rajiv: Auth 리팩토링 (수요일)\n"
                      "2. Yui: UI 구현 (목요일)\n"
                      "3. Anna: 테스트 (금요일 오전)\n"
                      "4. Olaf: 배포 (금요일 14:00)\n\n"
                      "점심은 제가 삽니다. 🍜"
        })
        
        # 팀 반응
        thread.append({
            "author": "Olaf",
            "comment": "@Marcus 금요일 14:00 배포 확정.\n"
                      "맥주는 제가 삽니다. 🍺"
        })
        
        thread.append({
            "author": "Emma",
            "comment": "팀워크 최고! Dream team! 💪\n"
                      "Users are gonna be SO happy!"
        })
        
        return thread
    
    def generate_daily_standup(self):
        """일일 스탠드업 코멘트"""
        
        standup = {
            "Emma": {
                "yesterday": "유저 인터뷰 5개 완료! 인사이트 대박!",
                "today": "리서치 결과 정리 & 새 피처 제안서",
                "blocker": "없음! (커피 머신 고장 빼고... ☕)"
            },
            "Rajiv": {
                "yesterday": "API 3개. Tests 45개. Bugs 0.",
                "today": "Performance optimization. Target: -50ms",
                "blocker": "None. Code flows like water."
            },
            "Anna": {
                "yesterday": "버그 12개 발견, 10개 수정 확인",
                "today": "E2E 테스트 스위트 작성",
                "blocker": "Flaky test in CI. 조사 중..."
            },
            "Marcus": {
                "yesterday": "아키텍처 리뷰 2건, 기술 멘토링",
                "today": "시스템 설계 문서 업데이트",
                "blocker": "없습니다. 순항 중입니다."
            },
            "Yui": {
                "yesterday": "대시보드 UI 80% 완성 🎨",
                "today": "반응형 디자인 마무리",
                "blocker": "디자이너 피드백 대기 중"
            },
            "Olaf": {
                "yesterday": "CI 파이프라인 3분으로 단축",
                "today": "프로덕션 배포 준비",
                "blocker": "없음. All systems operational."
            }
        }
        
        return standup

# CLI 실행
if __name__ == "__main__":
    generator = PersonaComments()
    
    # 예시 PR 코멘트
    pr_info = {"title": "Dashboard Feature", "number": 456}
    
    print("=== PR Comments ===")
    for persona in ["Emma", "Rajiv", "Anna"]:
        print(f"\n### {persona}")
        print(generator.generate_pr_comment(pr_info, persona))
        print("-" * 50)