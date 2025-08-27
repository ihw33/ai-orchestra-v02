#!/usr/bin/env python3
"""
Evolution Logger - AI Orchestra 성장 추적 시스템
작업 완료마다 경험치를 기록하고 레벨/진화 상태를 관리
"""

import os
import json
from datetime import datetime
from typing import Dict, Tuple, Optional

class EvolutionLogger:
    """AI Orchestra 진화 로거"""
    
    def __init__(self):
        self.status_file = "orchestra_status.txt"
        self.log_file = "orchestra.log"
        
        # 노드 타입별 경험치 테이블
        self.exp_table = {
            # GitHub 작업
            "CREATE_ISSUE": 3,          # 이슈 생성만
            "CLOSE_ISSUE": 8,           # 이슈 완료시 보너스
            "ADD_COMMENT": 2,
            "UPDATE_LABELS": 1,
            "CREATE_PR": 5,             # PR 생성 (10→5로 감소)
            "MERGE_PR": 10,             # PR 머지시 큰 보상
            
            # 코드 작성
            "WRITE_FUNCTION": 6,
            "CREATE_CLASS": 8,
            "FIX_BUG_LINE": 8,          # 버그 수정 유지
            "WRITE_TEST_CASE": 6,       # 테스트 케이스 작성 (단위 테스트)
            
            # 파일 조작
            "CREATE_FILE": 4,
            "UPDATE_FILE_SECTION": 5,
            "DELETE_FILE": 2,
            
            # 분석/리서치
            "ANALYZE_CODE": 5,
            "RESEARCH_TOPIC": 7,
            "FIND_PATTERN": 4,
            
            # 테스트 실행
            "RUN_TEST": 5,              # 테스트 실행
            "CHECK_COVERAGE": 6,
            "VALIDATE_OUTPUT": 4,
            "ACTIONS_LOCAL_TEST": 8,
            
            # 리뷰/검토 (성공/실패 분리 필요)
            "REVIEW_CODE": 8,           # 코드 리뷰 성공시
            "REVIEW_CODE_FAILED": -5,  # 코드 리뷰 실패시 감점
            "SUGGEST_IMPROVEMENT": 5,
            
            # MCP 노드
            "MCP_MEMORY_STORE": 4,
            "MCP_MEMORY_SEARCH": 3,
            "MCP_CONTEXT7_RESOLVE": 5,
            "MCP_CONTEXT7_DOCS": 5,
            
            # Context7 고도화 노드
            "USE_LATEST_DOCS": 5,        # 최신 문서 사용
            "AUTO_DOCS_LOAD": 3,          # 문서 자동 로드
            "VALIDATE_SUCCESS": 8,        # API 검증 성공
            "VALIDATE_ISSUES": 3,         # API 검증 이슈 발견
            "DETECT_BREAKING": 10,        # Breaking change 감지
            "AUTO_MIGRATE": 12,           # 자동 마이그레이션
            "OUTDATED_API": -3,           # 구버전 API 사용
        }
        
        # 진화 단계 정의
        self.evolution_stages = [
            (0, 49, 1, "🥚", "알"),
            (50, 149, 2, "🐣", "부화"),
            (150, 299, 3, "🐥", "병아리"),
            (300, 499, 4, "🐤", "성장"),
            (500, 799, 5, "🦆", "오리"),
            (800, 1199, 6, "🦅", "독수리"),
            (1200, float('inf'), 7, "🐉", "드래곤"),
        ]
        
        # 초기화
        self._init_files()
    
    def _init_files(self):
        """파일 초기화"""
        # 상태 파일이 없으면 생성
        if not os.path.exists(self.status_file):
            self._write_status(0, 1, "🥚", 0, 0)
        
        # 로그 파일이 없으면 생성
        if not os.path.exists(self.log_file):
            with open(self.log_file, "w") as f:
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                f.write(f"{timestamp} | INIT | Orchestra Evolution Logger Started\n")
    
    def on_node_complete(self, node_type: str, success: bool = True) -> Dict:
        """노드 완료시 호출"""
        # 노드 타입을 대문자로 변환 (enum value가 소문자일 경우 대비)
        node_type_upper = node_type.upper()
        
        # 실패한 특정 노드들은 감점 처리
        if not success:
            # 코드 리뷰 실패시 감점
            if node_type_upper == "REVIEW_CODE":
                exp_gain = self.exp_table.get("REVIEW_CODE_FAILED", -5)
            else:
                # 일반 실패는 경험치 없음
                self._append_log("FAILED", node_type, 0)
                return {"exp_gain": 0, "level_up": False}
        else:
            # 성공시 정상 경험치
            # 기본값 3: 테이블에 없는 새로운 노드 타입이 추가되어도 작동
            exp_gain = self.exp_table.get(node_type_upper, 3)
        
        # 로그에 기록
        self._append_log("COMPLETE", node_type, exp_gain)
        
        # 현재 상태 읽기
        current_exp = self._get_total_exp()
        new_exp = current_exp + exp_gain
        
        # 레벨 계산
        old_level, old_form, _ = self._get_level_form(current_exp)
        new_level, new_form, stage_name = self._get_level_form(new_exp)
        
        # 레벨업 체크
        level_up = old_level != new_level
        if level_up:
            self._append_log("LEVEL_UP", f"{old_form}→{new_form}", 0)
        
        # 상태 업데이트
        total_nodes = self._count_completed_nodes()
        success_rate = self._calculate_success_rate()
        self._write_status(new_exp, new_level, new_form, total_nodes, success_rate)
        
        return {
            "exp_gain": exp_gain,
            "total_exp": new_exp,
            "level": new_level,
            "form": new_form,
            "stage_name": stage_name,
            "level_up": level_up,
            "total_nodes": total_nodes,
            "success_rate": success_rate
        }
    
    def _get_level_form(self, exp: int) -> Tuple[int, str, str]:
        """경험치로 레벨과 폼 계산"""
        for min_exp, max_exp, level, form, name in self.evolution_stages:
            if min_exp <= exp <= max_exp:
                return level, form, name
        return 1, "🥚", "알"
    
    def _get_total_exp(self) -> int:
        """총 경험치 계산"""
        total = 0
        if os.path.exists(self.log_file):
            with open(self.log_file, "r") as f:
                for line in f:
                    if "exp:" in line:
                        try:
                            # exp:+10 또는 exp:-5 형태 파싱
                            exp_part = line.split("exp:")[1].split()[0]
                            total += int(exp_part)
                        except:
                            continue
        # 음수가 되지 않도록 보호
        return max(0, total)
    
    def _count_completed_nodes(self) -> int:
        """완료된 노드 수 계산"""
        count = 0
        if os.path.exists(self.log_file):
            with open(self.log_file, "r") as f:
                for line in f:
                    if "| COMPLETE |" in line:
                        count += 1
        return count
    
    def _calculate_success_rate(self) -> float:
        """성공률 계산"""
        success = 0
        failed = 0
        if os.path.exists(self.log_file):
            with open(self.log_file, "r") as f:
                for line in f:
                    if "| COMPLETE |" in line:
                        success += 1
                    elif "| FAILED |" in line:
                        failed += 1
        
        total = success + failed
        return round((success / total * 100), 1) if total > 0 else 0
    
    def _write_status(self, exp: int, level: int, form: str, nodes: int, success_rate: float):
        """상태 파일 업데이트"""
        with open(self.status_file, "w") as f:
            f.write(f"[Lv.{level} {form}] 노드:{nodes} | 성공:{success_rate}% | exp:{exp}\n")
    
    def _append_log(self, event_type: str, detail: str, exp: int):
        """로그 파일에 추가"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(self.log_file, "a") as f:
            if exp > 0:
                f.write(f"{timestamp} | {event_type} | {detail} | exp:+{exp}\n")
            elif exp < 0:
                f.write(f"{timestamp} | {event_type} | {detail} | exp:{exp}\n")  # 음수는 그대로
            else:
                f.write(f"{timestamp} | {event_type} | {detail}\n")
    
    def get_current_status(self) -> Dict:
        """현재 상태 조회"""
        exp = self._get_total_exp()
        level, form, stage = self._get_level_form(exp)
        nodes = self._count_completed_nodes()
        success_rate = self._calculate_success_rate()
        
        return {
            "level": level,
            "form": form,
            "stage_name": stage,
            "exp": exp,
            "total_nodes": nodes,
            "success_rate": success_rate,
            "next_level_exp": self._get_next_level_exp(exp)
        }
    
    def _get_next_level_exp(self, current_exp: int) -> int:
        """다음 레벨까지 필요한 경험치"""
        for min_exp, max_exp, _, _, _ in self.evolution_stages:
            if min_exp <= current_exp <= max_exp:
                return max_exp + 1 - current_exp
        return 0
    
    def show_progress(self):
        """진행 상황 출력"""
        status = self.get_current_status()
        print(f"\n{'='*50}")
        print(f"🎮 AI Orchestra Evolution Status")
        print(f"{'='*50}")
        print(f"레벨: Lv.{status['level']} {status['form']} ({status['stage_name']})")
        print(f"경험치: {status['exp']} (다음 레벨까지: {status['next_level_exp']})")
        print(f"완료 노드: {status['total_nodes']}개")
        print(f"성공률: {status['success_rate']}%")
        print(f"{'='*50}\n")


# 싱글톤 인스턴스
_logger_instance = None

def get_logger() -> EvolutionLogger:
    """싱글톤 로거 인스턴스 반환"""
    global _logger_instance
    if _logger_instance is None:
        _logger_instance = EvolutionLogger()
    return _logger_instance


# 테스트용
if __name__ == "__main__":
    logger = get_logger()
    
    # 테스트 노드 실행
    print("🧪 Evolution Logger 테스트 시작")
    
    # 몇 가지 노드 완료 시뮬레이션
    test_nodes = [
        "CREATE_ISSUE",
        "WRITE_FUNCTION", 
        "RUN_TEST",
        "FIX_BUG_LINE",
        "CREATE_PR"
    ]
    
    for node in test_nodes:
        result = logger.on_node_complete(node, success=True)
        print(f"✅ {node} 완료: +{result['exp_gain']} exp")
        if result['level_up']:
            print(f"🎉 레벨업! {result['form']} Lv.{result['level']}")
    
    # 현재 상태 표시
    logger.show_progress()