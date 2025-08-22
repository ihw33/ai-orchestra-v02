"""
KPI Tracking System - 실시간 성능 측정
"""

import sqlite3
import time
import os
from datetime import datetime
from typing import Optional
from pathlib import Path


class KPITracker:
    """싱글톤 KPI 추적기"""
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self, db_path: str = "var/kpi.sqlite"):
        if not hasattr(self, 'initialized'):
            # DB 디렉토리 생성
            Path(os.path.dirname(db_path)).mkdir(parents=True, exist_ok=True)
            
            self.db = sqlite3.connect(db_path, check_same_thread=False)
            self._init_tables()
            self.initialized = True
    
    def _init_tables(self):
        """테이블 초기화"""
        self.db.executescript("""
            CREATE TABLE IF NOT EXISTS kpi_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ts INTEGER NOT NULL,
                kind TEXT NOT NULL,
                phase TEXT,
                verb TEXT,
                success INTEGER,
                duration_ms INTEGER,
                error_type TEXT,
                ai_agent TEXT,
                task_id TEXT
            );
            CREATE INDEX IF NOT EXISTS idx_ts ON kpi_events(ts);
            CREATE INDEX IF NOT EXISTS idx_kind ON kpi_events(kind);
            CREATE INDEX IF NOT EXISTS idx_task ON kpi_events(task_id);
            
            CREATE TABLE IF NOT EXISTS kpi_daily (
                day TEXT NOT NULL,
                metric TEXT NOT NULL,
                value REAL NOT NULL,
                PRIMARY KEY(day, metric)
            );
        """)
        self.db.commit()
    
    def record(self, kind: str, phase: Optional[str] = None,
              verb: Optional[str] = None, success: Optional[bool] = None,
              duration_ms: Optional[int] = None, error_type: Optional[str] = None,
              ai_agent: Optional[str] = None, task_id: Optional[str] = None):
        """이벤트 기록
        
        Examples:
            # 핸드셰이크 기록
            kpi.record(kind='handshake', phase='ack', success=True, task_id='T001')
            
            # EXEC 명령 기록
            kpi.record(kind='exec', verb='TEST', success=True, duration_ms=1234)
            
            # 에러 기록
            kpi.record(kind='error', error_type='timeout', success=False)
        """
        try:
            self.db.execute(
                """INSERT INTO kpi_events 
                   (ts, kind, phase, verb, success, duration_ms, error_type, ai_agent, task_id)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (int(time.time()), kind, phase, verb,
                 int(success) if success is not None else None,
                 duration_ms, error_type, ai_agent, task_id)
            )
            self.db.commit()
        except Exception as e:
            # KPI 기록 실패가 메인 로직을 방해하면 안 됨
            print(f"KPI record failed: {e}")
    
    def rollup_today(self) -> dict:
        """오늘의 KPI 집계"""
        day = datetime.utcnow().strftime("%Y-%m-%d")
        metrics = {}
        
        try:
            # 1. 핸드셰이크 성공률
            cur = self.db.execute("""
                SELECT 
                    SUM(CASE WHEN kind='handshake' AND phase='eot' THEN 1 ELSE 0 END) AS total,
                    SUM(CASE WHEN kind='handshake' AND phase='eot' AND success=1 THEN 1 ELSE 0 END) AS ok
                FROM kpi_events 
                WHERE DATE(ts, 'unixepoch') = DATE('now')
            """)
            total, ok = cur.fetchone()
            if total and total > 0:
                rate = (ok or 0) * 100.0 / total
                self.db.execute(
                    "REPLACE INTO kpi_daily (day, metric, value) VALUES (?, ?, ?)",
                    (day, "handshake_success_rate", rate)
                )
                metrics["handshake_success_rate"] = rate
            
            # 2. EXEC 동사별 성공률
            cur = self.db.execute("""
                SELECT verb,
                       COUNT(*) AS attempts,
                       SUM(CASE WHEN success=1 THEN 1 ELSE 0 END) AS ok,
                       AVG(duration_ms) AS avg_ms
                FROM kpi_events
                WHERE kind='exec' AND DATE(ts, 'unixepoch') = DATE('now')
                GROUP BY verb
            """)
            for verb, attempts, ok, avg_ms in cur.fetchall():
                if attempts:
                    rate = (ok or 0) * 100.0 / attempts
                    self.db.execute(
                        "REPLACE INTO kpi_daily (day, metric, value) VALUES (?, ?, ?)",
                        (day, f"exec_{verb}_success_rate", rate)
                    )
                    metrics[f"exec_{verb}_success_rate"] = rate
                    
                if avg_ms is not None:
                    self.db.execute(
                        "REPLACE INTO kpi_daily (day, metric, value) VALUES (?, ?, ?)",
                        (day, f"exec_{verb}_avg_ms", avg_ms)
                    )
                    metrics[f"exec_{verb}_avg_ms"] = avg_ms
            
            # 3. 에러 복구율
            cur = self.db.execute("""
                SELECT 
                    COUNT(*) AS total_errors,
                    SUM(CASE WHEN error_type='auto_recovered' THEN 1 ELSE 0 END) AS recovered
                FROM kpi_events
                WHERE kind='error' AND DATE(ts, 'unixepoch') = DATE('now')
            """)
            total_errors, recovered = cur.fetchone()
            if total_errors and total_errors > 0:
                rate = (recovered or 0) * 100.0 / total_errors
                self.db.execute(
                    "REPLACE INTO kpi_daily (day, metric, value) VALUES (?, ?, ?)",
                    (day, "error_recovery_rate", rate)
                )
                metrics["error_recovery_rate"] = rate
            
            self.db.commit()
            return metrics
            
        except Exception as e:
            print(f"KPI rollup failed: {e}")
            return {}
    
    def get_today_metrics(self) -> dict:
        """오늘의 메트릭 조회 (대시보드용)"""
        day = datetime.utcnow().strftime("%Y-%m-%d")
        try:
            cur = self.db.execute(
                "SELECT metric, value FROM kpi_daily WHERE day = ?", (day,)
            )
            return dict(cur.fetchall())
        except Exception as e:
            print(f"KPI query failed: {e}")
            return {}
    
    def get_recent_stats(self, hours: int = 1) -> dict:
        """최근 N시간 통계 (실시간 모니터링용)"""
        since = int(time.time()) - (hours * 3600)
        stats = {}
        
        try:
            # 최근 핸드셰이크 성공률
            cur = self.db.execute("""
                SELECT 
                    COUNT(*) AS total,
                    SUM(CASE WHEN success=1 THEN 1 ELSE 0 END) AS ok
                FROM kpi_events
                WHERE kind='handshake' AND phase='eot' AND ts >= ?
            """, (since,))
            total, ok = cur.fetchone()
            if total and total > 0:
                stats["recent_handshake_rate"] = (ok or 0) * 100.0 / total
                stats["recent_handshake_count"] = total
            
            # 최근 에러
            cur = self.db.execute("""
                SELECT error_type, COUNT(*) AS cnt
                FROM kpi_events
                WHERE kind='error' AND ts >= ?
                GROUP BY error_type
                ORDER BY cnt DESC
                LIMIT 5
            """, (since,))
            stats["recent_errors"] = dict(cur.fetchall())
            
            return stats
            
        except Exception as e:
            print(f"Recent stats query failed: {e}")
            return {}
    
    def print_summary(self):
        """콘솔에 요약 출력 (디버깅용)"""
        metrics = self.get_today_metrics()
        recent = self.get_recent_stats()
        
        print("\n=== KPI Summary ===")
        print(f"Today's Metrics:")
        for key, value in metrics.items():
            if "rate" in key:
                print(f"  {key}: {value:.1f}%")
            elif "ms" in key:
                print(f"  {key}: {value:.0f}ms")
            else:
                print(f"  {key}: {value}")
        
        if recent:
            print(f"\nLast Hour:")
            if "recent_handshake_rate" in recent:
                print(f"  Handshake: {recent['recent_handshake_rate']:.1f}% ({recent.get('recent_handshake_count', 0)} attempts)")
            if "recent_errors" in recent and recent["recent_errors"]:
                print(f"  Top Errors: {recent['recent_errors']}")
        print("==================\n")


# 전역 싱글톤 인스턴스
kpi = KPITracker()