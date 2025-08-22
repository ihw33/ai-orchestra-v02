#!/usr/bin/env python3
"""
KPI 대시보드 - 실시간 성능 모니터링 (개선 버전)
"""

import sys
import time
import os
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Tuple, Dict, Any

# 프로젝트 루트를 Python 경로에 추가
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.kpi import kpi

# 로깅 설정
log_dir = Path(__file__).parent.parent / "logs"
log_dir.mkdir(exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_dir / "kpi_dashboard.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# 환경 변수
REFRESH_INTERVAL = int(os.getenv("KPI_REFRESH", "30"))
OUTPUT_FORMAT = os.getenv("KPI_OUTPUT", "console")  # console, json, slack
ALERT_ENABLED = os.getenv("KPI_ALERT", "true").lower() == "true"


def colorize(value: float, thresholds: Tuple[float, float] = (90, 80), 
            colors: Tuple[str, str, str] = ("\033[92m", "\033[93m", "\033[91m")) -> str:
    """값에 따른 색상 적용"""
    if value >= thresholds[0]:
        return f"{colors[0]}{value:.1f}%\033[0m"  # Green
    elif value >= thresholds[1]:
        return f"{colors[1]}{value:.1f}%\033[0m"  # Yellow
    return f"{colors[2]}{value:.1f}%\033[0m"  # Red


def check_alerts(metrics: dict, recent: dict) -> list:
    """알림 조건 체크"""
    alerts = []
    
    # 핸드셰이크 성공률 체크
    hs_rate = metrics.get('handshake_success_rate', 100)
    if hs_rate < 80:
        alert = {"level": "warning", "message": f"Handshake success rate low: {hs_rate:.1f}%"}
        alerts.append(alert)
        logger.warning(alert["message"])
    
    # 에러 복구율 체크
    recovery_rate = metrics.get('error_recovery_rate', 100)
    if recovery_rate < 50:
        alert = {"level": "critical", "message": f"Error recovery rate critical: {recovery_rate:.1f}%"}
        alerts.append(alert)
        logger.error(alert["message"])
    
    # 최근 에러 급증 체크
    if recent.get('recent_errors'):
        total_errors = sum(recent['recent_errors'].values())
        if total_errors > 10:
            alert = {"level": "warning", "message": f"Error spike detected: {total_errors} errors in last hour"}
            alerts.append(alert)
            logger.warning(alert["message"])
    
    return alerts


def run_once() -> Tuple[dict, dict, list]:
    """한 번 실행 (테스트 가능)"""
    try:
        # 오늘의 집계 실행
        kpi.rollup_today()
        
        # 메트릭 조회
        metrics = kpi.get_today_metrics()
        recent = kpi.get_recent_stats(hours=1)
        
        # 알림 체크
        alerts = check_alerts(metrics, recent) if ALERT_ENABLED else []
        
        return metrics, recent, alerts
        
    except Exception as e:
        logger.error(f"Failed to fetch KPI metrics: {e}")
        return {}, {}, []


def render_console(metrics: dict, recent: dict, alerts: list):
    """콘솔 출력"""
    print("\n" + "="*50)
    print(f"    OrchestrEX KPI Dashboard - {datetime.now().strftime('%H:%M:%S')}")
    print("="*50)
    
    print("\n📊 Today's Performance")
    print("-" * 30)
    
    # 핸드셰이크 성공률
    hs_rate = metrics.get('handshake_success_rate', 0)
    print(f"Handshake Success: {colorize(hs_rate)}")
    
    # EXEC 명령별 성공률
    exec_metrics = []
    for verb in ['TEST', 'IMPLEMENT', 'ANALYZE', 'REVIEW']:
        key = f'exec_{verb}_success_rate'
        if key in metrics:
            rate = metrics[key]
            avg_key = f'exec_{verb}_avg_ms'
            avg_ms = metrics.get(avg_key, 0)
            exec_metrics.append(f"  {verb}: {colorize(rate, (85, 70))} (avg {avg_ms:.0f}ms)")
    
    if exec_metrics:
        print("EXEC Commands:")
        for metric in exec_metrics:
            print(metric)
    
    # 에러 복구율
    recovery_rate = metrics.get('error_recovery_rate', 100)
    print(f"Error Recovery: {colorize(recovery_rate, (70, 50))}")
    
    # 최근 1시간 통계
    if recent:
        print("\n⏱️  Last Hour")
        print("-" * 30)
        if 'recent_handshake_rate' in recent:
            print(f"Handshake: {recent['recent_handshake_rate']:.1f}% ({recent.get('recent_handshake_count', 0)} attempts)")
        if 'recent_errors' in recent and recent['recent_errors']:
            print("Top Errors:")
            for error_type, count in list(recent['recent_errors'].items())[:3]:
                print(f"  - {error_type}: {count}")
    
    # 알림 표시
    if alerts:
        print("\n🚨 Alerts")
        print("-" * 30)
        for alert in alerts:
            icon = "⚠️" if alert["level"] == "warning" else "🔴"
            print(f"{icon} {alert['message']}")
    
    print("\n" + "-"*50)


def render_json(metrics: dict, recent: dict, alerts: list):
    """JSON 출력 (API/웹 연동용)"""
    output = {
        "timestamp": datetime.utcnow().isoformat(),
        "metrics": metrics,
        "recent": recent,
        "alerts": alerts
    }
    print(json.dumps(output, indent=2))


def render_slack(metrics: dict, recent: dict, alerts: list):
    """Slack 메시지 포맷 (향후 구현)"""
    # Slack 웹훅 URL
    webhook_url = os.getenv("SLACK_WEBHOOK_URL")
    if not webhook_url:
        logger.warning("SLACK_WEBHOOK_URL not set")
        return
    
    # 메시지 구성
    hs_rate = metrics.get('handshake_success_rate', 0)
    recovery_rate = metrics.get('error_recovery_rate', 100)
    
    message = {
        "text": "KPI Dashboard Update",
        "attachments": [
            {
                "color": "good" if hs_rate >= 90 else "warning" if hs_rate >= 80 else "danger",
                "fields": [
                    {
                        "title": "Handshake Success Rate",
                        "value": f"{hs_rate:.1f}%",
                        "short": True
                    },
                    {
                        "title": "Error Recovery Rate",
                        "value": f"{recovery_rate:.1f}%",
                        "short": True
                    }
                ]
            }
        ]
    }
    
    if alerts:
        message["attachments"].append({
            "color": "danger",
            "title": "⚠️ Alerts",
            "text": "\n".join([f"• {a['message']}" for a in alerts])
        })
    
    # TODO: 실제 Slack 전송 구현
    logger.info(f"Slack message prepared: {message}")


def main():
    """메인 루프"""
    logger.info("KPI Dashboard started")
    logger.info(f"Refresh interval: {REFRESH_INTERVAL}s")
    logger.info(f"Output format: {OUTPUT_FORMAT}")
    
    render_funcs = {
        "console": render_console,
        "json": render_json,
        "slack": render_slack
    }
    
    render = render_funcs.get(OUTPUT_FORMAT, render_console)
    
    if OUTPUT_FORMAT == "json":
        # JSON 모드는 한 번만 실행
        metrics, recent, alerts = run_once()
        render(metrics, recent, alerts)
        return
    
    # 콘솔 모드는 계속 실행
    try:
        while True:
            metrics, recent, alerts = run_once()
            
            if OUTPUT_FORMAT == "console":
                # 화면 지우기 (옵션)
                if os.getenv("CLEAR_SCREEN", "false").lower() == "true":
                    print("\033[2J\033[H")
            
            render(metrics, recent, alerts)
            
            if OUTPUT_FORMAT == "console":
                print(f"Press Ctrl+C to exit | Refreshing in {REFRESH_INTERVAL}s...")
            
            time.sleep(REFRESH_INTERVAL)
            
    except KeyboardInterrupt:
        logger.info("Dashboard stopped by user")
        if OUTPUT_FORMAT == "console":
            print("\n\n👋 Dashboard stopped")
    except Exception as e:
        logger.error(f"Dashboard error: {e}")
        raise


if __name__ == "__main__":
    main()