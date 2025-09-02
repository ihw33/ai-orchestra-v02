#!/usr/bin/env python3
"""
재귀 성장 시스템 테스트
새로운 노드와 DAG가 자동으로 생성되는지 확인
"""

import asyncio
import json
from pathlib import Path
import sys

# 프로젝트 루트 추가
sys.path.append(str(Path(__file__).parent))

from generators.ai_interface import AIInterface
from generators.recursive_node_generator import RecursiveNodeGenerator
from generators.recursive_dag_composer import RecursiveDAGComposer


def test_ai_interface():
    """AI 인터페이스 테스트"""
    print("\n🧪 AI 인터페이스 테스트")
    print("=" * 50)
    
    ai = AIInterface()
    
    # 테스트 이슈
    issue_body = """
    [AI] YouTube 동영상 분석 및 요약 기능 구현
    
    ## 요구사항
    - YouTube URL에서 동영상 정보 추출
    - 자막 다운로드 및 분석
    - AI를 사용한 요약 생성
    - 결과를 데이터베이스에 저장
    """
    
    # 이슈 분석
    print("📋 이슈 분석 중...")
    analysis = ai.analyze_issue(issue_body)
    print(f"분석 결과:\n{json.dumps(analysis, indent=2, ensure_ascii=False)}")
    
    return analysis


def test_node_generation(analysis):
    """노드 생성 테스트"""
    print("\n🧪 노드 생성 테스트")
    print("=" * 50)
    
    generator = RecursiveNodeGenerator()
    nodes_dir = Path(__file__).parent / "nodes"
    
    # 기존 노드 확인
    existing_nodes = [f.stem for f in nodes_dir.glob("*.py")]
    print(f"기존 노드 수: {len(existing_nodes)}")
    print(f"기존 노드: {existing_nodes[:5]}...")
    
    # 필요한 노드 확인
    required_nodes = analysis.get('required_nodes', [])
    print(f"\n필요한 노드: {required_nodes}")
    
    # 새로운 노드 생성 시뮬레이션
    for node_type in required_nodes[:1]:  # 첫 번째 노드만 테스트
        node_name = f"{node_type}_node"
        if node_name not in existing_nodes:
            print(f"\n🔄 새 노드 생성 중: {node_type}")
            
            # 노드 코드 생성
            ai = AIInterface()
            code = ai.generate_node_code(node_type, {
                'description': f"Test node for {node_type}",
                'context': analysis
            })
            
            if code:
                print(f"✅ 코드 생성 완료 (길이: {len(code)}자)")
                print("생성된 코드 (처음 10줄):")
                print("\n".join(code.split("\n")[:10]))
                
                # 자동으로 저장 (테스트 모드)
                print("\n🔄 노드를 자동으로 저장합니다...")
                try:
                    file_path = generator.save_new_node(node_type, code)
                    print(f"✨ 노드 저장됨: {file_path}")
                except Exception as e:
                    print(f"❌ 노드 저장 실패: {e}")
            else:
                print("❌ 코드 생성 실패")
        else:
            print(f"이미 존재하는 노드: {node_name}")


def test_dag_composition(analysis):
    """DAG 구성 테스트"""
    print("\n🧪 DAG 구성 테스트")
    print("=" * 50)
    
    composer = RecursiveDAGComposer()
    dags_dir = Path(__file__).parent / "dags"
    
    # 기존 DAG 확인
    existing_dags = [f.stem for f in dags_dir.glob("*.py")]
    print(f"기존 DAG 수: {len(existing_dags)}")
    print(f"기존 DAG: {existing_dags}")
    
    # DAG 구성
    task_type = analysis.get('task_type', 'general')
    dag_name = f"{task_type}_youtube_analysis"
    
    if dag_name not in existing_dags:
        print(f"\n🔄 새 DAG 구성 중: {dag_name}")
        
        # DAG 코드 생성
        dag_code = composer.compose_dag(analysis)
        
        if dag_code:
            print(f"✅ DAG 코드 생성 완료 (길이: {len(dag_code)}자)")
            print("생성된 DAG 코드 (처음 20줄):")
            print("\n".join(dag_code.split("\n")[:20]))
            
            # 자동으로 저장 (테스트 모드)
            print("\n🔄 DAG를 자동으로 저장합니다...")
            try:
                file_path = composer.save_dag(dag_code, dag_name)
                print(f"✨ DAG 저장됨: {file_path}")
            except Exception as e:
                print(f"❌ DAG 저장 실패: {e}")
        else:
            print("❌ DAG 생성 실패")
    else:
        print(f"이미 존재하는 DAG: {dag_name}")


async def test_integrated_system():
    """통합 시스템 테스트"""
    print("\n🧪 통합 시스템 테스트")
    print("=" * 50)
    
    # executors 임포트 시도
    try:
        from executors.iwl_executor import IWLExecutor
        
        executor = IWLExecutor()
        print("✅ IWL Executor 로드 성공")
        
        # 테스트 이슈로 실행 시뮬레이션
        test_issue_id = "999"  # 테스트용 가짜 이슈
        
        print(f"\n테스트 이슈 #{test_issue_id} 실행 시뮬레이션")
        print("(실제 GitHub 이슈가 아니므로 에러가 발생할 수 있습니다)")
        
        # 이슈 분석 테스트
        test_issue_body = """
        [AI] 새로운 기능: PDF 문서 자동 요약
        - PDF 파일 업로드
        - 텍스트 추출
        - AI 요약 생성
        """
        
        analysis = executor.ai_interface.analyze_issue(test_issue_body)
        print(f"분석 결과: {analysis}")
        
        # 필요한 노드 확인
        await executor.ensure_required_nodes(analysis)
        print("✅ 노드 확인/생성 완료")
        
        # 필요한 DAG 확인
        await executor.ensure_required_dag(analysis)
        print("✅ DAG 확인/생성 완료")
        
    except Exception as e:
        print(f"❌ 통합 테스트 실패: {e}")


def main():
    """메인 테스트 함수"""
    print("\n" + "="*60)
    print("🧬 재귀 성장 시스템 테스트 시작")
    print("="*60)
    
    # 1. AI 인터페이스 테스트
    analysis = test_ai_interface()
    
    if not analysis:
        print("❌ AI 인터페이스 테스트 실패")
        return
    
    # 2. 노드 생성 테스트
    test_node_generation(analysis)
    
    # 3. DAG 구성 테스트
    test_dag_composition(analysis)
    
    # 4. 통합 시스템 테스트
    asyncio.run(test_integrated_system())
    
    print("\n" + "="*60)
    print("✅ 재귀 성장 시스템 테스트 완료")
    print("="*60)
    
    # 최종 상태 확인
    nodes_dir = Path(__file__).parent / "nodes"
    dags_dir = Path(__file__).parent / "dags"
    
    print(f"\n📊 최종 상태:")
    print(f"  - 노드 수: {len(list(nodes_dir.glob('*.py')))}")
    print(f"  - DAG 수: {len(list(dags_dir.glob('*.py')))}")
    print(f"  - 학습된 패턴: {Path(__file__).parent / 'learned_patterns.json'} 존재 여부: {(Path(__file__).parent / 'learned_patterns.json').exists()}")


if __name__ == "__main__":
    main()