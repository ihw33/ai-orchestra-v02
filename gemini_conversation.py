#!/usr/bin/env python3
"""
Gemini와 여러 번 대화하기
"""

import subprocess
import time

def gemini_conversation():
    """여러 번의 대화 시뮬레이션"""
    
    conversations = [
        ("첫 번째 질문", "What is 2+2?"),
        ("두 번째 질문", "What is 10*10?"),
        ("세 번째 질문", "What is the capital of France?"),
    ]
    
    print("🎯 Gemini와 순차적 대화")
    print("=" * 60)
    
    for title, prompt in conversations:
        print(f"\n📨 {title}: {prompt}")
        
        # 각 질문마다 새로운 Gemini 프로세스
        result = subprocess.run(
            ['gemini', '-p', prompt],
            capture_output=True,
            text=True
        )
        
        # 응답 출력 (시스템 메시지 제외)
        response = [line for line in result.stdout.split('\n') 
                   if line and not line.startswith("Data") and not line.startswith("Loaded")]
        
        print(f"🤖 Gemini: {' '.join(response)}")
        time.sleep(1)
    
    print("\n" + "=" * 60)
    print("✅ 대화 완료!")

def gemini_context_conversation():
    """컨텍스트를 유지하는 대화 (시뮬레이션)"""
    
    print("🎯 컨텍스트 유지 대화 시도")
    print("=" * 60)
    
    # 이전 대화 내용을 포함한 프롬프트
    context = ""
    
    questions = [
        "My name is Thomas.",
        "What is my name?",
        "Calculate 5+5 for me.",
    ]
    
    for q in questions:
        # 전체 컨텍스트 포함
        if context:
            full_prompt = f"Previous conversation:\n{context}\n\nNow answer: {q}"
        else:
            full_prompt = q
        
        print(f"\n📨 User: {q}")
        
        result = subprocess.run(
            ['gemini', '-p', full_prompt],
            capture_output=True,
            text=True
        )
        
        response = [line for line in result.stdout.split('\n') 
                   if line and not line.startswith("Data") and not line.startswith("Loaded")]
        response_text = ' '.join(response)
        
        print(f"🤖 Gemini: {response_text[:100]}...")
        
        # 컨텍스트 업데이트
        context += f"\nUser: {q}\nGemini: {response_text}"
        
        time.sleep(1)

if __name__ == "__main__":
    # 1. 독립적인 대화들
    gemini_conversation()
    
    print("\n" + "=" * 60 + "\n")
    
    # 2. 컨텍스트 유지 시도 (제한적)
    gemini_context_conversation()