#!/usr/bin/env python3
"""
🎯 Workflow CLI - 레고처럼 조립하는 작업 자동화
AI Orchestra Modular Workflow System
"""

import os
import sys
import json
import subprocess
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

class WorkflowCLI:
    """경량 워크플로우 실행 엔진"""
    
    def __init__(self):
        self.base_dir = Path(__file__).parent
        self.modules_file = self.base_dir / "modules" / "base_modules.json"
        self.patterns_file = self.base_dir / "user_patterns.json"
        self.workflows_dir = self.base_dir / "workflows"
        
        # 단축키 매핑
        self.shortcuts = {
            'm': 'morning_routine',
            'h': 'hotfix',
            'd': 'deploy',
            't': 'test_all',
            'r': 'send_report',
            'b': 'backup'
        }
        
        # 모듈 로드
        self.modules = self.load_modules()
        self.user_patterns = self.load_user_patterns()
        
    def load_modules(self) -> Dict:
        """기본 모듈 로드"""
        if self.modules_file.exists():
            with open(self.modules_file, 'r') as f:
                data = json.load(f)
                return {m['id']: m for m in data.get('modules', [])}
        # 기본 모듈 정의
        return {
            'create_issue': {'id': 'create_issue', 'name': '이슈 생성', 'description': 'GitHub 이슈 생성'},
            'code_generation': {'id': 'code_generation', 'name': '코드 생성', 'description': '코드 자동 생성'},
            'test_execution': {'id': 'test_execution', 'name': '테스트', 'description': '테스트 실행'},
            'deploy': {'id': 'deploy', 'name': '배포', 'description': '프로덕션 배포'},
            'send_report': {'id': 'send_report', 'name': '보고서', 'description': '보고서 전송'},
            'feature_scan': {'id': 'feature_scan', 'name': '기능 검색', 'description': '기존 기능 검색'},
            'assign_team': {'id': 'assign_team', 'name': '팀 할당', 'description': 'AI 팀원 할당'},
            'merge_pr': {'id': 'merge_pr', 'name': 'PR 병합', 'description': 'Pull Request 병합'}
        }
    
    def load_user_patterns(self) -> Dict:
        """사용자 패턴 로드"""
        if self.patterns_file.exists():
            with open(self.patterns_file, 'r') as f:
                return json.load(f)
        return {
            "user": "current_user",
            "patterns": {},
            "favorites": [],
            "history": []
        }
    
    def save_user_patterns(self):
        """사용자 패턴 저장"""
        with open(self.patterns_file, 'w') as f:
            json.dump(self.user_patterns, f, indent=2)
    
    def execute_module(self, module_id: str, params: Dict = None) -> Dict:
        """단일 모듈 실행"""
        if module_id not in self.modules:
            return {"success": False, "error": f"Module {module_id} not found"}
        
        module = self.modules[module_id]
        print(f"⚡ Executing: {module['name']}")
        
        # 실제 실행 로직 (간단한 시뮬레이션)
        start_time = time.time()
        
        if module.get('command'):
            # 실제 명령어 실행
            if module_id == 'create_issue':
                cmd = ["gh", "issue", "create", "-R", "ihw33/ai-orchestra-v02", "-t", "Test Issue", "-b", "Auto-generated"]
                # subprocess.run(cmd)
                print(f"  → Would run: {' '.join(cmd)}")
            elif module_id == 'test_execution':
                print(f"  → Running tests...")
                time.sleep(0.5)  # 시뮬레이션
        
        execution_time = time.time() - start_time
        
        # 패턴 학습
        self.learn_pattern(module_id)
        
        return {
            "success": True,
            "module": module_id,
            "time": f"{execution_time:.2f}s"
        }
    
    def learn_pattern(self, module_id: str):
        """사용자 패턴 학습"""
        now = datetime.now()
        key = f"{now.hour}_{now.weekday()}"
        
        if key not in self.user_patterns['patterns']:
            self.user_patterns['patterns'][key] = []
        
        self.user_patterns['patterns'][key].append(module_id)
        self.user_patterns['history'].append({
            "module": module_id,
            "timestamp": now.isoformat()
        })
        
        # 최근 100개만 유지
        if len(self.user_patterns['history']) > 100:
            self.user_patterns['history'] = self.user_patterns['history'][-100:]
        
        self.save_user_patterns()
    
    def suggest_next(self) -> Optional[str]:
        """다음 모듈 제안"""
        now = datetime.now()
        key = f"{now.hour}_{now.weekday()}"
        
        if key in self.user_patterns['patterns']:
            patterns = self.user_patterns['patterns'][key]
            if patterns:
                # 가장 자주 사용하는 모듈 제안
                from collections import Counter
                most_common = Counter(patterns).most_common(1)[0][0]
                return most_common
        return None
    
    def run_workflow(self, workflow_name: str):
        """워크플로우 실행"""
        print(f"\n🚀 Starting Workflow: {workflow_name}")
        print("=" * 40)
        
        # 내장 워크플로우
        if workflow_name == 'morning_routine':
            workflow = ['feature_scan', 'create_issue', 'assign_team']
        elif workflow_name == 'hotfix':
            workflow = ['code_generation', 'test_execution', 'deploy']
        elif workflow_name == 'test_all':
            workflow = ['test_execution', 'send_report']
        elif workflow_name == 'code_review':
            workflow = ['request_review', 'test_execution', 'send_report']
        else:
            # 커스텀 워크플로우 파일 찾기
            custom_file = self.workflows_dir / f"{workflow_name}.json"
            if custom_file.exists():
                with open(custom_file, 'r') as f:
                    data = json.load(f)
                    workflow = data.get('steps', [])
            else:
                print(f"❌ Workflow '{workflow_name}' not found")
                return
        
        # 워크플로우 실행
        total_time = 0
        for i, module_id in enumerate(workflow, 1):
            print(f"\n[{i}/{len(workflow)}] ", end="")
            result = self.execute_module(module_id)
            if result['success']:
                total_time += float(result['time'].rstrip('s'))
            else:
                print(f"❌ Failed: {result.get('error')}")
                break
        
        print(f"\n{'='*40}")
        print(f"✅ Workflow Complete! Total time: {total_time:.2f}s")
        
        # 다음 제안
        suggestion = self.suggest_next()
        if suggestion:
            print(f"💡 Suggestion: Usually you run '{suggestion}' next at this time")
    
    def list_workflows(self):
        """사용 가능한 워크플로우 목록"""
        print("\n📚 Available Workflows:")
        print("=" * 40)
        
        # 내장 워크플로우
        built_in = {
            'morning_routine': 'Daily startup sequence',
            'hotfix': 'Emergency fix and deploy',
            'test_all': 'Run all tests and report',
            'deploy': 'Production deployment'
        }
        
        print("\n🔧 Built-in:")
        for name, desc in built_in.items():
            shortcut = [k for k, v in self.shortcuts.items() if v == name]
            shortcut_str = f" (shortcut: {shortcut[0]})" if shortcut else ""
            print(f"  • {name:20} - {desc}{shortcut_str}")
        
        # 커스텀 워크플로우
        if self.workflows_dir.exists():
            custom_files = list(self.workflows_dir.glob("*.json"))
            if custom_files:
                print("\n📝 Custom:")
                for file in custom_files:
                    print(f"  • {file.stem}")
        
        # 즐겨찾기
        if self.user_patterns.get('favorites'):
            print("\n⭐ Favorites:")
            for fav in self.user_patterns['favorites']:
                print(f"  • {fav}")
    
    def create_workflow(self, name: str):
        """새 워크플로우 생성"""
        print(f"\n🔨 Creating workflow: {name}")
        
        # 대화형 워크플로우 빌더
        steps = []
        print("\nAvailable modules:")
        for i, (mod_id, mod) in enumerate(self.modules.items(), 1):
            print(f"  {i}. {mod_id} - {mod['description']}")
        
        print("\nAdd modules (enter numbers, comma-separated, or 'done'):")
        while True:
            choice = input("> ").strip()
            if choice.lower() == 'done':
                break
            
            try:
                indices = [int(x.strip()) - 1 for x in choice.split(',')]
                module_ids = list(self.modules.keys())
                for idx in indices:
                    if 0 <= idx < len(module_ids):
                        steps.append(module_ids[idx])
                        print(f"  Added: {module_ids[idx]}")
            except (ValueError, IndexError) as e:
                print("Invalid input. Try again.")
        
        if steps:
            # 워크플로우 저장
            self.workflows_dir.mkdir(exist_ok=True)
            workflow_file = self.workflows_dir / f"{name}.json"
            
            workflow_data = {
                'name': name,
                'created': datetime.now().isoformat(),
                'steps': steps
            }
            
            with open(workflow_file, 'w') as f:
                json.dump(workflow_data, f, indent=2)
            
            print(f"✅ Workflow '{name}' created with {len(steps)} steps")
        else:
            print("❌ No steps added")
    
    def show_stats(self):
        """사용 통계 표시"""
        print("\n📊 Workflow Statistics:")
        print("=" * 40)
        
        if self.user_patterns['history']:
            from collections import Counter
            
            # 모듈 사용 빈도
            module_counts = Counter([h['module'] for h in self.user_patterns['history']])
            
            print("\n🔝 Most Used Modules:")
            for module, count in module_counts.most_common(5):
                print(f"  • {module:20} - {count} times")
            
            # 시간대별 패턴
            print("\n⏰ Time Patterns:")
            for key, modules in self.user_patterns['patterns'].items():
                if modules:
                    hour, day = key.split('_')
                    days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
                    print(f"  • {days[int(day)]} {hour}:00 - {Counter(modules).most_common(1)[0][0]}")
        else:
            print("No usage data yet. Start using workflows!")
    
    def interactive_menu(self):
        """대화형 메뉴"""
        print("\n🎯 Workflow CLI - Interactive Mode")
        print("=" * 40)
        
        while True:
            print("\nOptions:")
            print("  1. Run workflow")
            print("  2. List workflows")
            print("  3. Create workflow")
            print("  4. Show stats")
            print("  5. Exit")
            
            choice = input("\nChoice: ").strip()
            
            if choice == '1':
                name = input("Workflow name (or shortcut): ").strip()
                name = self.shortcuts.get(name, name)
                self.run_workflow(name)
            elif choice == '2':
                self.list_workflows()
            elif choice == '3':
                name = input("New workflow name: ").strip()
                self.create_workflow(name)
            elif choice == '4':
                self.show_stats()
            elif choice == '5':
                print("👋 Goodbye!")
                break
            else:
                print("Invalid choice")
    
    def cli(self, args):
        """명령줄 인터페이스"""
        if len(args) < 2:
            self.interactive_menu()
            return
        
        command = args[1]
        
        # 단축키 처리
        if command in self.shortcuts:
            self.run_workflow(self.shortcuts[command])
        elif command == 'run':
            if len(args) > 2:
                self.run_workflow(args[2])
            else:
                print("Usage: workflow run <name>")
        elif command == 'list':
            self.list_workflows()
        elif command == 'create':
            if len(args) > 2:
                self.create_workflow(args[2])
            else:
                print("Usage: workflow create <name>")
        elif command == 'stats':
            self.show_stats()
        elif command == 'help':
            print("""
🎯 Workflow CLI - Help

Commands:
  workflow              - Interactive menu
  workflow m           - Run morning_routine (shortcut)
  workflow run <name>  - Run specific workflow
  workflow list        - List all workflows
  workflow create <name> - Create new workflow
  workflow stats       - Show usage statistics
  
Shortcuts:
  m - morning_routine
  h - hotfix
  d - deploy
  t - test_all
  r - send_report
  b - backup
""")
        else:
            # 워크플로우 이름으로 직접 실행
            self.run_workflow(command)

def main():
    """메인 진입점"""
    cli = WorkflowCLI()
    cli.cli(sys.argv)

if __name__ == "__main__":
    main()