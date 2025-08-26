#!/usr/bin/env python3
"""
백그라운드 Gemini 실시간 모니터링
"""

import subprocess
import time
import sys
from datetime import datetime

def run_and_monitor_gemini(prompt):
    """Gemini를 실행하고 실시간으로 출력 모니터링"""
    
    print(f"🚀 Gemini 시작: {datetime.now().strftime('%H:%M:%S')}")
    print(f"📝 프롬프트: {prompt[:50]}...")
    print("=" * 60)
    
    # Gemini 프로세스 시작 (실시간 출력 스트리밍)
    process = subprocess.Popen(
        ['gemini', '-p', prompt],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1,  # 라인 버퍼링
        universal_newlines=True
    )
    
    print("📊 실시간 출력:")
    print("-" * 40)
    
    # 실시간으로 출력 읽기
    output_lines = []
    while True:
        line = process.stdout.readline()
        if not line:
            break
        
        line = line.rstrip()
        # 시스템 메시지 필터링
        if not line.startswith("Data collection") and not line.startswith("Loaded cached"):
            print(f"  > {line}")
            output_lines.append(line)
    
    # 프로세스 종료 대기
    process.wait()
    
    print("-" * 40)
    print(f"✅ 완료: {datetime.now().strftime('%H:%M:%S')}")
    print(f"📌 총 {len(output_lines)}줄 출력")
    
    return output_lines

def monitor_multiple_geminis():
    """여러 Gemini 동시 모니터링"""
    
    print("🎯 여러 Gemini 백그라운드 실행 및 모니터링")
    print("=" * 60)
    
    # 로그 파일들
    tasks = [
        ("계산", "Calculate 123 * 456", "/tmp/gemini_calc.log"),
        ("코드", "Write hello world in Python", "/tmp/gemini_code.log"),
        ("설명", "Explain what is REST API in one sentence", "/tmp/gemini_explain.log")
    ]
    
    processes = []
    
    # 모든 작업 시작
    for name, prompt, logfile in tasks:
        with open(logfile, 'w') as f:
            proc = subprocess.Popen(
                ['gemini', '-p', prompt],
                stdout=f,
                stderr=subprocess.STDOUT,
                text=True
            )
            processes.append((name, proc, logfile))
            print(f"  ▶️ {name} 작업 시작 (PID: {proc.pid}, 로그: {logfile})")
    
    print("\n⏳ 모니터링 중...")
    print("-" * 40)
    
    # 주기적으로 상태 확인
    all_done = False
    check_count = 0
    
    while not all_done:
        time.sleep(1)
        check_count += 1
        
        print(f"\n[체크 #{check_count}]")
        all_done = True
        
        for name, proc, logfile in processes:
            if proc.poll() is None:
                # 아직 실행 중
                print(f"  ⏳ {name}: 실행 중...")
                all_done = False
                
                # 현재까지의 출력 미리보기
                try:
                    with open(logfile, 'r') as f:
                        lines = f.readlines()
                        if lines:
                            last_line = lines[-1].strip()
                            if last_line and not last_line.startswith("Data"):
                                print(f"      최근: {last_line[:50]}...")
                except:
                    pass
            else:
                # 완료됨
                print(f"  ✅ {name}: 완료!")
    
    print("\n" + "=" * 60)
    print("📋 최종 결과:")
    
    # 모든 결과 출력
    for name, proc, logfile in processes:
        print(f"\n### {name} 작업 결과:")
        with open(logfile, 'r') as f:
            content = f.read()
            # 시스템 메시지 제거
            lines = [l for l in content.split('\n') 
                    if l and not l.startswith("Data") and not l.startswith("Loaded")]
            for line in lines[:5]:  # 처음 5줄만
                print(f"  {line}")
            if len(lines) > 5:
                print(f"  ... (총 {len(lines)}줄)")

def tail_gemini_log():
    """실시간 로그 파일 모니터링 (tail -f 같은 기능)"""
    
    print("🔍 Gemini 로그 실시간 모니터링")
    print("=" * 60)
    
    # Gemini 시작 (로그 파일로 출력)
    logfile = "/tmp/gemini_live.log"
    prompt = "Count from 1 to 20, one per line, with 0.5 second delay between each"
    
    with open(logfile, 'w') as f:
        proc = subprocess.Popen(
            ['gemini', '-p', prompt],
            stdout=f,
            stderr=subprocess.STDOUT,
            text=True
        )
        print(f"▶️ Gemini 시작 (PID: {proc.pid})")
    
    print(f"📂 로그 파일: {logfile}")
    print("-" * 40)
    
    # tail -f 구현
    with open(logfile, 'r') as f:
        # 끝으로 이동
        f.seek(0, 2)
        
        while proc.poll() is None:
            line = f.readline()
            if line:
                line = line.rstrip()
                if line and not line.startswith("Data") and not line.startswith("Loaded"):
                    print(f"  > {line}")
            else:
                time.sleep(0.1)
        
        # 남은 출력 읽기
        for line in f:
            line = line.rstrip()
            if line and not line.startswith("Data") and not line.startswith("Loaded"):
                print(f"  > {line}")
    
    print("-" * 40)
    print("✅ 모니터링 완료!")

if __name__ == "__main__":
    print("백그라운드 Gemini 모니터링 데모\n")
    
    # 1. 단일 작업 실시간 모니터링
    print("1️⃣ 단일 작업 실시간 모니터링:")
    result = run_and_monitor_gemini("Calculate 99 * 99 and show the result")
    
    print("\n" + "=" * 60 + "\n")
    
    # 2. 여러 작업 동시 모니터링
    print("2️⃣ 여러 작업 동시 모니터링:")
    monitor_multiple_geminis()
    
    print("\n" + "=" * 60 + "\n")
    
    # 3. tail -f 스타일 모니터링
    print("3️⃣ tail -f 스타일 실시간 모니터링:")
    tail_gemini_log()