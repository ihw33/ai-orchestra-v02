#!/usr/bin/env python3
"""
이슈 키워드 추천 시스템
이슈 내용을 분석하여 적절한 라벨과 해시태그를 추천
"""

import re
from typing import List, Dict, Tuple

class IssueKeywordRecommender:
    def __init__(self):
        # 프로세스 라벨 매핑
        self.process_labels = {
            'analysis': ['분석', 'analyze', 'review', '검토', 'evaluate', '평가'],
            'research': ['리서치', 'research', '조사', 'investigate', '탐색'],
            'implementation': ['구현', 'implement', 'build', '개발', 'develop', '구축'],
            'documentation': ['문서', 'document', 'readme', 'guide', '가이드', '설명'],
            'testing': ['테스트', 'test', 'verify', '검증', 'check'],
            'refactor': ['리팩토링', 'refactor', '개선', 'improve', '최적화'],
        }
        
        # 주제 해시태그 매핑
        self.topic_hashtags = {
            '#백업시스템': ['backup', '백업', 'save', '저장'],
            '#자동화': ['auto', '자동', 'automatic', 'automate'],
            '#클라우드코드': ['claude', 'claude code', '클라우드'],
            '#깃훅': ['hook', 'git hook', 'pre-commit', 'post-commit'],
            '#CI/CD': ['ci', 'cd', 'continuous', 'deploy', 'pipeline'],
            '#모니터링': ['monitor', '모니터링', 'watch', '감시'],
            '#API': ['api', 'endpoint', 'rest', 'graphql'],
            '#데이터베이스': ['database', 'db', 'sql', 'mongodb'],
        }
        
        # 기술 스택 해시태그
        self.tech_hashtags = {
            '#python': ['python', 'py', '파이썬'],
            '#javascript': ['javascript', 'js', 'node', 'nodejs'],
            '#typescript': ['typescript', 'ts'],
            '#bash': ['bash', 'shell', 'sh', 'script'],
            '#docker': ['docker', 'container', '도커'],
            '#kubernetes': ['kubernetes', 'k8s'],
        }

    def analyze_issue(self, title: str, body: str) -> Tuple[List[str], List[str]]:
        """이슈 제목과 본문을 분석하여 라벨과 해시태그 추천"""
        text = f"{title} {body}".lower()
        
        # 추천 라벨 (프로세스)
        recommended_labels = []
        for label, keywords in self.process_labels.items():
            if any(keyword in text for keyword in keywords):
                recommended_labels.append(label)
        
        # 추천 해시태그 (주제 + 기술)
        recommended_hashtags = []
        
        # 주제 해시태그
        for hashtag, keywords in self.topic_hashtags.items():
            if any(keyword in text for keyword in keywords):
                recommended_hashtags.append(hashtag)
        
        # 기술 해시태그
        for hashtag, keywords in self.tech_hashtags.items():
            if any(keyword in text for keyword in keywords):
                recommended_hashtags.append(hashtag)
        
        # DAG 패턴 감지
        if 'parallel' in text or '병렬' in text:
            recommended_labels.append('parallel')
        elif 'relay' in text or '순차' in text:
            recommended_labels.append('relay')
        elif 'pipeline' in text:
            recommended_labels.append('pipeline')
        
        return recommended_labels, recommended_hashtags

    def format_recommendation(self, labels: List[str], hashtags: List[str]) -> str:
        """추천 결과를 포맷팅"""
        result = "## 🤖 키워드 추천\n\n"
        
        if labels:
            result += "### 🏷️ 추천 라벨 (GitHub)\n"
            result += f"```\n{','.join(labels)}\n```\n\n"
        
        if hashtags:
            result += "### #️⃣ 추천 해시태그 (본문)\n"
            result += f"{' '.join(hashtags)}\n\n"
        
        return result

# 사용 예시
if __name__ == "__main__":
    recommender = IssueKeywordRecommender()
    
    # 이슈 #70 예시
    title = "[AI] 이슈 #69 수정 - Claude Code 자동 백업 솔루션 분석"
    body = """
    제공된 자동 백업 솔루션 문서를 분석하여 다음을 보고:
    1. 시스템 개요 - hooks 동작 방식
    2. 설치 및 사용법
    3. 기술적 분석 - 코드 리뷰
    """
    
    labels, hashtags = recommender.analyze_issue(title, body)
    print(recommender.format_recommendation(labels, hashtags))
    
    # gh 명령어 생성
    if labels:
        print(f"gh issue edit ISSUE_NUM --add-label \"{','.join(labels)}\"")
    if hashtags:
        print(f"\n본문에 추가:\n{' '.join(hashtags)}")