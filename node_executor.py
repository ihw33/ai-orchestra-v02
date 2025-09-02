#!/usr/bin/env python3
"""노드 실행기 - 모든 노드를 실행 가능하게 만드는 핵심"""

import subprocess
import json
import sys
from typing import Dict, Any

class NodeExecutor:
    def __init__(self):
        self.nodes = {
            "CREATE_ISSUE": self.create_issue,
            "KEYWORD_ENRICHMENT": self.keyword_enrichment,
            "AI_ANALYSIS": self.ai_analysis,
            "AI_IMPLEMENTATION": self.ai_implementation,
            "AI_TESTING": self.ai_testing,
            "GENERATE_REPORT": self.generate_report,
            "PARSE_SOLUTION": self.parse_solution,
            "ANALYZE_FEATURES": self.analyze_features,
            "EVALUATE_FIT": self.evaluate_fit,
            "ADOPTION_REPORT": self.adoption_report
        }
    
    def execute(self, node_name: str, params: Dict[str, Any]) -> Any:
        """노드 실행"""
        if node_name in self.nodes:
            print(f"🔄 Executing node: {node_name}")
            return self.nodes[node_name](params)
        else:
            print(f"❌ Unknown node: {node_name}")
            return None
    
    def create_issue(self, params: Dict) -> str:
        """GitHub 이슈 생성"""
        title = params.get('title', 'New Issue')
        body = params.get('body', '')
        labels = params.get('labels', 'ai-task')
        
        cmd = [
            "gh", "issue", "create",
            "--title", title,
            "--body", body,
            "--label", labels,
            "-R", "ihw33/ai-orchestra-v02"
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            issue_url = result.stdout.strip()
            issue_num = issue_url.split('/')[-1]
            print(f"✅ Issue created: #{issue_num}")
            return issue_num
        else:
            print(f"❌ Failed to create issue: {result.stderr}")
            return None
    
    def keyword_enrichment(self, params: Dict) -> Dict:
        """키워드 자동 추가"""
        issue_num = params.get('issue_num')
        content = params.get('content', '')
        
        # 키워드 분석
        keywords = self.analyze_keywords(content)
        
        # 라벨 추가
        if keywords['labels'] and issue_num:
            cmd = [
                "gh", "issue", "edit", str(issue_num),
                "--add-label", ",".join(keywords['labels']),
                "-R", "ihw33/ai-orchestra-v02"
            ]
            subprocess.run(cmd)
            print(f"✅ Labels added: {keywords['labels']}")
        
        # 해시태그를 이슈 코멘트로 추가
        if keywords['hashtags'] and issue_num:
            hashtag_text = " ".join(keywords['hashtags'])
            cmd = [
                "gh", "issue", "comment", str(issue_num),
                "--body", f"🏷️ 키워드: {hashtag_text}",
                "-R", "ihw33/ai-orchestra-v02"
            ]
            subprocess.run(cmd)
            print(f"✅ Hashtags added: {keywords['hashtags']}")
        
        return keywords
    
    def ai_analysis(self, params: Dict) -> str:
        """AI 분석 실행"""
        prompt = params.get('prompt', '')
        ai = params.get('ai', 'gemini')
        issue_num = params.get('issue_num', '')
        
        full_prompt = f"이슈 #{issue_num}: {prompt}" if issue_num else prompt
        
        if ai == 'gemini':
            cmd = ["gemini", "-p", full_prompt]
        elif ai == 'claude':
            cmd = ["claude", "-p", full_prompt]
        else:
            cmd = ["codex", "exec", full_prompt]
        
        print(f"🤖 Running {ai} analysis...")
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        # 결과를 이슈에 코멘트로 추가
        if issue_num and result.stdout:
            comment_cmd = [
                "gh", "issue", "comment", str(issue_num),
                "--body", f"### {ai.upper()} 분석 결과\n{result.stdout[:1000]}",
                "-R", "ihw33/ai-orchestra-v02"
            ]
            subprocess.run(comment_cmd)
        
        return result.stdout
    
    def ai_implementation(self, params: Dict) -> str:
        """AI 구현 실행"""
        params['ai'] = params.get('ai', 'claude')
        params['prompt'] = params.get('prompt', '구현을 시작하세요')
        return self.ai_analysis(params)
    
    def ai_testing(self, params: Dict) -> str:
        """AI 테스트 실행"""
        params['ai'] = params.get('ai', 'codex')
        params['prompt'] = params.get('prompt', '테스트를 수행하세요')
        return self.ai_analysis(params)
    
    def generate_report(self, params: Dict) -> str:
        """보고서 생성"""
        issue_num = params.get('issue_num')
        results = params.get('results', [])
        
        report = "# 📊 실행 보고서\n\n"
        for i, result in enumerate(results):
            report += f"## Step {i+1}\n{result[:500]}\n\n"
        
        if issue_num:
            cmd = [
                "gh", "issue", "comment", str(issue_num),
                "--body", report,
                "-R", "ihw33/ai-orchestra-v02"
            ]
            subprocess.run(cmd)
            print("✅ Report generated")
        
        return report
    
    def parse_solution(self, params: Dict) -> str:
        """솔루션 파싱 (Gemini)"""
        params['ai'] = 'gemini'
        params['prompt'] = params.get('prompt', '솔루션 구조를 분석하세요')
        return self.ai_analysis(params)
    
    def analyze_features(self, params: Dict) -> str:
        """기능 분석 (Claude)"""
        params['ai'] = 'claude'
        params['prompt'] = params.get('prompt', '기능을 상세히 분석하세요')
        return self.ai_analysis(params)
    
    def evaluate_fit(self, params: Dict) -> str:
        """적합성 평가 (Codex)"""
        params['ai'] = 'codex'
        params['prompt'] = params.get('prompt', '기술적 적합성을 평가하세요')
        return self.ai_analysis(params)
    
    def adoption_report(self, params: Dict) -> str:
        """도입 보고서 작성"""
        return self.generate_report(params)
    
    def analyze_keywords(self, content: str) -> Dict:
        """키워드 분석"""
        labels = []
        hashtags = []
        
        # 프로세스 라벨 (GitHub Labels)
        keyword_map = {
            ('분석', 'analysis'): ('analysis', '#분석'),
            ('구현', 'implementation'): ('implementation', '#구현'),
            ('버그', 'bug', 'error'): ('bug', '#버그수정'),
            ('문서', 'documentation'): ('documentation', '#문서화'),
            ('테스트', 'test'): ('testing', '#테스트'),
            ('리팩토링', 'refactor'): ('refactoring', '#리팩토링'),
            ('긴급', 'urgent'): ('urgent', '#긴급'),
            ('AI', 'ai'): ('ai-task', '#AI작업')
        }
        
        content_lower = content.lower()
        for keywords, (label, hashtag) in keyword_map.items():
            if any(kw in content_lower for kw in keywords):
                if label not in labels:
                    labels.append(label)
                if hashtag not in hashtags:
                    hashtags.append(hashtag)
        
        return {'labels': labels, 'hashtags': hashtags}


if __name__ == "__main__":
    executor = NodeExecutor()
    
    # CLI 사용
    if len(sys.argv) > 1:
        node_name = sys.argv[1]
        
        # 파라미터 파싱
        if len(sys.argv) > 2:
            try:
                params = json.loads(sys.argv[2])
            except json.JSONDecodeError:
                # JSON이 아니면 문자열로 처리
                params = {"prompt": sys.argv[2]}
        else:
            params = {}
        
        result = executor.execute(node_name, params)
        if result:
            print(f"✅ {node_name} completed")
            print(f"Result: {result[:200]}..." if len(str(result)) > 200 else f"Result: {result}")
    else:
        print("Usage: python3 node_executor.py NODE_NAME [PARAMS_JSON]")
        print("Available nodes:", ", ".join(executor.nodes.keys()))