# 🚀 AI CLI -p 모드 완벽 가이드

**작성일**: 2025-08-23  
**핵심**: 대화형 모드 대신 직접 실행으로 완전 자동화 실현

---

## 📌 -p 모드란?

**-p (--prompt)**: AI CLI의 **비대화형 직접 실행 모드**
- 프롬프트를 직접 전달하여 즉시 실행
- 결과 출력 후 자동 종료
- 스크립트와 자동화에 최적화

---

## 🎯 기본 사용법

### 1. 각 AI별 명령어
```bash
# Claude
claude -p "프롬프트 내용"

# Gemini  
gemini -p "프롬프트 내용"

# Codex
codex -p "프롬프트 내용"

# ChatGPT (있다면)
chatgpt -p "프롬프트 내용"
```

### 2. 실제 사용 예시

#### 간단한 질문
```bash
# 코드 생성
gemini -p "파이썬으로 피보나치 수열 코드 작성해줘"

# 파일 분석
claude -p "package.json 파일을 읽고 의존성 분석해줘"

# 버그 수정
codex -p "TypeError: Cannot read property 'length' of undefined 에러 해결 방법"
```

#### 복잡한 작업
```bash
# 긴 프롬프트는 따옴표로 감싸기
claude -p "다음 요구사항으로 React 컴포넌트 만들어줘:
1. TypeScript 사용
2. Props 타입 정의
3. 에러 처리 포함
4. 테스트 코드 작성"
```

---

## 💾 결과 처리 방법

### 1. 파일로 저장
```bash
# 직접 저장
gemini -p "프로젝트 구조 분석해줘" > analysis.md

# 추가 모드로 저장
claude -p "추가 분석" >> analysis.md
```

### 2. 변수에 저장
```bash
# Bash 변수
RESULT=$(claude -p "버그 수정 방법 제안해줘")
echo "$RESULT"

# 조건부 처리
if gemini -p "이 코드에 버그가 있나?" | grep -q "버그"; then
    echo "버그 발견!"
fi
```

### 3. 파이프라인 연결
```bash
# AI 체인
claude -p "코드 작성해줘" | gemini -p "이 코드 테스트해줘"

# GitHub 직접 연동
gemini -p "이슈 #123 해결책" | gh issue comment 123 -F -

# 여러 도구 연결
claude -p "SQL 쿼리 생성" | mysql -u user -p database
```

---

## 🐍 Python에서 사용

### 1. 기본 실행
```python
import subprocess

# 단일 실행
result = subprocess.run(
    'gemini -p "질문 내용"',
    shell=True,
    capture_output=True,
    text=True
)
print(result.stdout)
```

### 2. 병렬 실행
```python
import subprocess
from concurrent.futures import ThreadPoolExecutor

def run_ai(ai_name, prompt):
    result = subprocess.run(
        f'{ai_name} -p "{prompt}"',
        shell=True,
        capture_output=True,
        text=True
    )
    return ai_name, result.stdout

# 여러 AI 동시 실행
with ThreadPoolExecutor(max_workers=3) as executor:
    futures = []
    for ai in ['claude', 'gemini', 'codex']:
        future = executor.submit(run_ai, ai, "동일한 질문")
        futures.append(future)
    
    # 결과 수집
    for future in futures:
        ai_name, output = future.result()
        print(f"{ai_name}: {output}")
```

### 3. 스트리밍 처리
```python
import subprocess

# 실시간 출력 스트리밍
process = subprocess.Popen(
    'gemini -p "긴 응답 생성해줘"',
    shell=True,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True,
    bufsize=1
)

# 한 줄씩 읽기
for line in process.stdout:
    print(line, end='')
```

---

## 🔄 대화형 모드 vs -p 모드

| 특징 | 대화형 모드 | -p 모드 |
|------|------------|---------|
| **실행 방식** | `gemini` → 대화 → `exit` | `gemini -p "질문"` → 종료 |
| **자동화** | ❌ 어려움 | ✅ 완벽 지원 |
| **병렬 처리** | ❌ 불가능 | ✅ 무제한 |
| **스크립트** | ❌ 복잡함 | ✅ 간단함 |
| **컨텍스트** | ✅ 유지됨 | ❌ 일회성 |
| **세션 관리** | 필요함 | 불필요 |

---

## 🎭 실전 활용 예시

### 1. GitHub Issue 자동 처리
```bash
#!/bin/bash
# issue_processor.sh

ISSUE_NUM=$1
ISSUE_BODY=$(gh issue view $ISSUE_NUM --json body -q .body)

# Claude가 해결책 제안
SOLUTION=$(claude -p "이슈 해결: $ISSUE_BODY")

# Gemini가 검증
VALIDATION=$(echo "$SOLUTION" | gemini -p "이 해결책 검증해줘")

# 결과를 이슈에 코멘트
echo "## AI 분석 결과
### 해결책 (Claude)
$SOLUTION

### 검증 (Gemini)
$VALIDATION" | gh issue comment $ISSUE_NUM -F -
```

### 2. 코드 리뷰 자동화
```bash
# 변경된 파일들에 대해 리뷰
git diff --name-only | while read file; do
    echo "Reviewing $file..."
    git diff $file | codex -p "이 변경사항 코드 리뷰해줘"
done > code_review.md
```

### 3. 다중 AI 의견 수집
```bash
#!/bin/bash
QUESTION="React vs Vue vs Angular 중 뭐가 최고?"

echo "# AI 의견 모음" > opinions.md
echo "## 질문: $QUESTION" >> opinions.md
echo "" >> opinions.md

for ai in claude gemini codex; do
    echo "### $ai의 의견" >> opinions.md
    $ai -p "$QUESTION" >> opinions.md
    echo "" >> opinions.md
done
```

---

## 🚨 주의사항

### 1. 따옴표 처리
```bash
# 잘못된 예
gemini -p 여러 줄의
텍스트  # 에러!

# 올바른 예
gemini -p "여러 줄의
텍스트"
```

### 2. 특수문자 이스케이프
```bash
# 잘못된 예
claude -p "변수 $USER 출력"  # $USER가 치환됨

# 올바른 예
claude -p '변수 $USER 출력'  # 작은따옴표 사용
claude -p "변수 \$USER 출력"  # 이스케이프
```

### 3. 타임아웃 설정
```bash
# 타임아웃 설정 (60초)
timeout 60 gemini -p "복잡한 작업"

# Python에서
process.communicate(timeout=60)
```

### 4. 에러 처리
```bash
# Bash에서
if ! gemini -p "질문"; then
    echo "실행 실패"
fi

# Python에서
try:
    result = subprocess.run(..., check=True)
except subprocess.CalledProcessError as e:
    print(f"에러: {e}")
```

---

## 🏗️ 우리가 구축한 시스템

### 1. Multi-AI Orchestrator (병렬)
```bash
python multi_ai_orchestrator.py 123
# Issue #123을 여러 AI가 동시 처리
```

### 2. Relay Pipeline (순차)
```bash
python relay_pipeline_system.py 456
# Issue #456을 구현→테스트→리뷰 순차 처리
```

### 3. Persona Training (학습 데이터)
```bash
python persona_training_system.py
# 6개 페르소나로 다양한 해결책 생성
```

### 4. 자동 감시 모드
```bash
python relay_pipeline_system.py watch
# GitHub 이슈 자동 감시 및 처리
```

---

## 💡 핵심 인사이트

**-p 모드의 발견이 게임 체인저인 이유:**

1. **완전 자동화**: 인간 개입 없이 AI 작업 자동화
2. **무한 확장성**: AI 인스턴스 무제한 실행
3. **파이프라인**: AI들의 릴레이 작업 가능
4. **통합 용이**: 기존 도구와 완벽 통합

이제 **"AI가 AI를 관리하는"** 시대가 열렸습니다! 🚀

---

*작성: 2025-08-23*  
*by Claude Code & Thomas*