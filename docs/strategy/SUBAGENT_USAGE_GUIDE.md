# 서브에이전트 활용 가이드

## 🎯 핵심 원칙
AI 팀원들에게 작업을 할당할 때, 특히 Claude 계열은 적절한 서브에이전트를 사용합니다.

## 🤖 서브에이전트 매핑

### Claude 계열 서브에이전트
| 작업 유형 | 서브에이전트 | 사용 시나리오 |
|-----------|-------------|--------------|
| **backend-architect** | Backend 설계 | API 설계, 시스템 아키텍처, DB 스키마 |
| **ui-ux-designer** | UI/UX 디자인 | 인터페이스 설계, 사용자 경험, 디자인 시스템 |
| **business-analyst** | 비즈니스 분석 | 메트릭 분석, KPI 추적, 성장 전략 |
| **iwl-code-reviewer** | IWL 코드 리뷰 | IdeaWorkLab 프로젝트 전용 |
| **ai-engineer** | AI/ML 엔지니어링 | LLM 통합, RAG 시스템, 프롬프트 엔지니어링 |
| **search-specialist** | 검색 전문가 | 깊은 리서치, 정보 수집, 경쟁 분석 |
| **api-documenter** | API 문서화 | OpenAPI 스펙, SDK 생성, 개발자 문서 |
| **prompt-engineer** | 프롬프트 엔지니어 | AI 프롬프트 최적화, 성능 개선 |

### 페르소나 → 서브에이전트 매핑

```python
persona_to_subagent = {
    # Backend Team
    "backend_lead_김정호": "backend-architect",
    "senior_api_dev": "backend-architect",
    "db_architect": "backend-architect",
    
    # Frontend Team  
    "frontend_lead_Maria": "ui-ux-designer",
    "ui_component_dev": "ui-ux-designer",
    
    # Business/Analysis
    "product_manager": "business-analyst",
    "data_analyst": "business-analyst",
    
    # AI/ML Team
    "ml_engineer": "ai-engineer",
    "prompt_specialist": "prompt-engineer",
    
    # Documentation
    "tech_writer": "api-documenter",
    
    # Research
    "researcher": "search-specialist"
}
```

## 📋 사용 예시

### 1. API 설계 작업
```python
# ❌ 기존 방식
"claude -p 'API 설계해줘'"

# ✅ 서브에이전트 활용
Task(
    description="API 설계",
    subagent_type="backend-architect",
    prompt="결제 API RESTful 설계"
)
```

### 2. UI 컴포넌트 개발
```python
# ✅ Maria 페르소나 + UI 에이전트
Task(
    description="대시보드 UI",
    subagent_type="ui-ux-designer",
    prompt="Maria Silva 페르소나로 대시보드 디자인"
)
```

### 3. 비즈니스 메트릭 분석
```python
# ✅ 분석 전문 에이전트
Task(
    description="KPI 분석",
    subagent_type="business-analyst",
    prompt="월간 성장 지표 분석 및 개선안"
)
```

## 🔄 자동 선택 로직

```python
def select_subagent(task_type, persona=None):
    """작업 유형과 페르소나에 따라 최적 서브에이전트 선택"""
    
    # 페르소나가 있으면 매핑 확인
    if persona and persona in persona_to_subagent:
        return persona_to_subagent[persona]
    
    # 작업 유형별 기본 선택
    task_mapping = {
        "api": "backend-architect",
        "ui": "ui-ux-designer",
        "분석": "business-analyst",
        "문서": "api-documenter",
        "ai": "ai-engineer",
        "검색": "search-specialist"
    }
    
    for keyword, agent in task_mapping.items():
        if keyword in task_type.lower():
            return agent
    
    return "general-purpose"  # 기본값
```

## 🎭 페르소나 + 서브에이전트 시너지

### 최적 조합
1. **김정호 + backend-architect**: 완벽한 시스템 설계
2. **Maria + ui-ux-designer**: 뛰어난 사용자 경험
3. **박민수 + search-specialist**: 철저한 버그 검색
4. **데이터분석가 + business-analyst**: 정확한 인사이트

### 팀 구성 예시
```python
# API 개발 팀
team = [
    ("김정호", "backend-architect"),    # 설계
    ("박민수", "search-specialist"),     # 검증
    ("tech_writer", "api-documenter")    # 문서화
]
```

## 📌 주의사항

1. **IWL 프로젝트**: 반드시 `iwl-code-reviewer` 사용
2. **성능 중요 작업**: `backend-architect` 우선
3. **사용자 대면 기능**: `ui-ux-designer` 필수
4. **데이터 기반 결정**: `business-analyst` 활용

## 🚀 실행 명령

```bash
# PM이 이슈 생성 시
gh issue create --title "[AI] API 설계" --body "
작업: 결제 API 설계
담당: backend-architect (김정호)
"

# 자동으로 서브에이전트 할당
if "[AI]" in title and "API" in title:
    use_subagent("backend-architect")
```

---
*작성일: 2025-08-26*
*PM Claude*