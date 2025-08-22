#!/usr/bin/env python3
"""
Gemini를 백그라운드에서 실행하고 모니터링
"""

import subprocess
import threading
import time
import queue

class GeminiRunner:
    def __init__(self):
        self.output_queue = queue.Queue()
        self.process = None
        
    def run_gemini_task(self, prompt):
        """백그라운드에서 Gemini 실행"""
        def _run():
            try:
                # Gemini를 서브프로세스로 실행
                cmd = ['gemini', '-p', prompt]
                self.process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                
                # 출력을 실시간으로 큐에 추가
                for line in iter(self.process.stdout.readline, ''):
                    if line:
                        self.output_queue.put(('stdout', line.strip()))
                
                self.process.wait()
                self.output_queue.put(('done', self.process.returncode))
                
            except Exception as e:
                self.output_queue.put(('error', str(e)))
        
        # 백그라운드 스레드에서 실행
        thread = threading.Thread(target=_run)
        thread.daemon = True
        thread.start()
        return thread
    
    def get_output(self, timeout=0.1):
        """비블로킹으로 출력 확인"""
        try:
            return self.output_queue.get(timeout=timeout)
        except queue.Empty:
            return None
    
    def is_running(self):
        """Gemini가 실행 중인지 확인"""
        return self.process and self.process.poll() is None

def main():
    print("🚀 Gemini 백그라운드 실행 테스트")
    print("=" * 50)
    
    runner = GeminiRunner()
    
    # 긴 작업 요청
    prompt = """
    Please do the following tasks:
    1. Output @@ACK id=BG-TEST
    2. Count from 1 to 5 slowly
    3. Output @@RUN id=BG-TEST
    4. Calculate 100+200
    5. Output @@EOT id=BG-TEST status=OK answer=300
    """
    
    print("📨 Gemini 작업 시작 (백그라운드)...")
    thread = runner.run_gemini_task(prompt)
    
    # 다른 작업을 하면서 주기적으로 확인
    print("\n💻 다른 작업 수행 중...")
    for i in range(30):  # 30초 동안
        # 다른 작업 시뮬레이션
        print(f"  작업 {i+1} 수행 중...", end="")
        time.sleep(1)
        
        # Gemini 출력 확인 (비블로킹)
        output = runner.get_output(timeout=0.01)
        if output:
            msg_type, content = output
            if msg_type == 'stdout':
                print(f"\n  📢 [Gemini]: {content}")
            elif msg_type == 'done':
                print(f"\n  ✅ Gemini 작업 완료! (코드: {content})")
                break
            elif msg_type == 'error':
                print(f"\n  ❌ 에러: {content}")
                break
        else:
            print(" ✓")
        
        if not runner.is_running() and output is None:
            print("\n  ✅ Gemini 작업 완료!")
            break
    
    # 남은 출력 모두 가져오기
    print("\n📋 최종 결과:")
    while True:
        output = runner.get_output(timeout=0.01)
        if output is None:
            break
        msg_type, content = output
        if msg_type == 'stdout':
            print(f"  {content}")

if __name__ == "__main__":
    main()