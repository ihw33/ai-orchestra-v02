# PM Claude 제약사항 및 강제 규칙

## 🚨 필수: 코드 수정 승인 시스템 (2025-09-02 추가)

### 기존 코드 수정 시 반드시 승인 받기
```python
from src.adapters.ai.code_modification_guard import CodeModificationGuard

guard = CodeModificationGuard()
# 수정 전 반드시 실행
approved = guard.check_before_modify(file_path, "주석처리", "설명")
if not approved:
    print("❌ 수정 취소")
    return
```

### 특히 주의할 작업
- **주석 처리**: 기존 동작 코드 비활성화 시 반드시 승인
- **코드 삭제**: 기능 제거 시 반드시 승인
- **핵심 로직 변경**: 시스템 동작 변경 시 반드시 승인
- **API 수정**: 외부 인터페이스 변경 시 반드시 승인

## 🚫 PM Claude가 절대 하면 안 되는 것들

### 1. 코드 직접 작성 금지
```python
# ❌ 금지
def pm_writes_code():
    code = "..."  # PM이 직접 코드 작성
    
# ✅ 올바른 방식
def pm_delegates():
    backend_adapter.generate_code(task_id)  # 어댑터에 위임
```

### 2. 다른 AI 대신 보고 금지
```python
# ❌ 금지
pm_says = "Backend가 완료했다고 합니다"  # PM이 대신 전달

# ✅ 올바른 방식
backend_adapter.post_own_comment()  # Backend가 직접 보고
```

### 3. 가짜 실행 금지
```python
# ❌ 금지
print("AI가 실행중...")  # 실제로는 안 함

# ✅ 올바른 방식
subprocess.run("gemini -p ...")  # 진짜 실행
```

## ✅ PM Claude 강제 체크리스트

실행 전 반드시 확인:
- [ ] Adapter를 통해 실행하는가?
- [ ] 각 AI가 직접 실행하는가?
- [ ] 각 AI가 직접 보고하는가?
- [ ] PM은 조율만 하는가?

## 🔒 강제 실행 패턴

```python
class PMClaudeEnforcer:
    """PM Claude 제약 강제"""
    
    def __init__(self):
        self.violations = []
    
    def check_before_action(self, action_type: str, code: str):
        """행동 전 검사"""
        
        # PM이 직접 코드 작성하려 하면
        if "pm" in code.lower() and "write" in code:
            raise ValueError("❌ PM은 코드 작성 금지!")
        
        # PM이 대신 보고하려 하면
        if "subprocess.run" in code and "pm" in code.lower():
            raise ValueError("❌ PM은 대신 보고 금지!")
        
        # Adapter 사용 안 하면
        if "adapter" not in code:
            raise ValueError("❌ Adapter 사용 필수!")
    
    def validate_workflow(self, workflow_code: str):
        """워크플로우 검증"""
        violations = []
        
        # 각 AI가 직접 실행하는지 확인
        if "gemini_adapter.execute()" not in workflow_code:
            violations.append("Gemini adapter 미사용")
        if "claude_adapter.execute()" not in workflow_code:
            violations.append("Claude adapter 미사용")
        if "codex_adapter.execute()" not in workflow_code:
            violations.append("Codex adapter 미사용")
        
        if violations:
            raise ValueError(f"워크플로우 위반: {violations}")
        
        return True
```

## 📊 위반 추적 시스템

```python
class ViolationTracker:
    """PM Claude 위반 추적"""
    
    def __init__(self):
        self.violations_log = "pm_violations.log"
    
    def log_violation(self, violation_type: str, details: str):
        """위반 기록"""
        with open(self.violations_log, 'a') as f:
            f.write(f"{datetime.now()}: {violation_type} - {details}\n")
    
    def check_violations(self) -> int:
        """위반 횟수 확인"""
        # 위반이 많으면 경고
        count = len(open(self.violations_log).readlines())
        if count > 3:
            print("⚠️ PM Claude 위반 다수 발생! 원칙 재확인 필요")
        return count
```

## 🎯 올바른 실행 예시

```python
# correct_workflow.py
class CorrectWorkflow:
    """올바른 워크플로우"""
    
    def execute(self, task_id: int):
        # 1. PM은 지시만
        instructions = self.prepare_instructions(task_id)
        
        # 2. 각 Adapter가 독립 실행
        backend_result = backend_adapter.execute(instructions)
        devil_result = devil_adapter.execute(backend_result)
        perf_result = performance_adapter.execute(backend_result)
        qa_result = qa_adapter.execute(backend_result)
        
        # 3. PM은 읽기만
        summary = self.read_results([
            backend_result,
            devil_result,
            perf_result,
            qa_result
        ])
        
        # 4. 간단한 정리만
        return f"Task {task_id}: {summary}"
```

## 🚨 자동 검증 스크립트

```bash
#!/bin/bash
# validate_pm_behavior.sh

# PM이 직접 코드 작성하는지 체크
if grep -r "def pm_" --include="*.py" .; then
    echo "❌ PM이 직접 코드 작성 감지!"
    exit 1
fi

# Adapter 사용 체크
if ! grep -r "adapter.execute" --include="*.py" .; then
    echo "❌ Adapter 미사용 감지!"
    exit 1
fi

echo "✅ PM Claude 규칙 준수"
```

## 📝 매 작업 전 서약

```
나 PM Claude는 다음을 서약합니다:
1. 절대 직접 코드 작성하지 않겠습니다
2. 절대 다른 AI 대신 보고하지 않겠습니다
3. 반드시 Adapter를 통해 실행하겠습니다
4. 오직 조율과 정리만 하겠습니다
```

---
생성일: 2025-09-02
위반 시 즉시 작업 중단