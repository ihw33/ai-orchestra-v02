# AI Orchestra v02 도메인 모델

## 🎯 핵심 도메인 (Core Domain)

### 1. Orchestration Domain
**책임**: 여러 AI를 조율하여 작업 수행

**주요 개념**:
- `Orchestrator`: 전체 워크플로우 조정자
- `Task`: 수행할 작업 단위
- `Result`: 작업 실행 결과
- `Provenance`: 결과의 출처 메타데이터

**불변식**:
- 모든 Result는 반드시 Provenance를 포함해야 함
- 하나의 Task는 하나 이상의 AI에게 할당될 수 있음

### 2. Workflow Domain
**책임**: 작업 흐름 관리

**주요 개념**:
- `Node`: 독립적 작업 단위
- `DAG`: 노드들의 방향성 비순환 그래프
- `Pipeline`: 순차적 실행 체인
- `Executor`: 노드 실행 주체 (AI/Rules/Human)

**불변식**:
- DAG는 순환 참조를 가질 수 없음
- 모든 Node는 최소 하나의 Executor를 가져야 함

## 🔧 지원 도메인 (Supporting Domain)

### 1. GitHub Integration Domain
**책임**: GitHub Issue/PR 관리

**주요 개념**:
- `Issue`: 작업 요청
- `Comment`: 진행 상황 보고
- `PullRequest`: 코드 변경 제안

### 2. Persona Domain
**책임**: AI 역할 관리

**주요 개념**:
- `Persona`: AI에게 부여하는 전문가 역할
- `Capability`: 페르소나의 능력
- `Assignment`: 페르소나-작업 매핑

### 3. Growth Domain
**책임**: 시스템 자기 개선

**주요 개념**:
- `Experience`: 실행 경험 데이터
- `Pattern`: 학습된 패턴
- `Evolution`: 시스템 진화 단계

## 📦 일반 도메인 (Generic Domain)

### 1. Logging Domain
- 실행 로그 관리
- 디버깅 정보 수집

### 2. Caching Domain
- 결과 캐싱
- 성능 최적화

### 3. Error Handling Domain
- 에러 처리
- 재시도 로직
- 폴백 메커니즘

## 🔄 도메인 간 관계

```
GitHub Issue → Orchestrator → Workflow → Executor
                    ↓             ↓          ↓
                 Persona      Node/DAG    AI/Rules
                    ↓             ↓          ↓
                 Growth      Experience  Provenance
```

## 🚫 도메인 경계 규칙

1. **Core Domain은 외부 시스템을 직접 호출하지 않음**
   - Port를 통해서만 통신

2. **Supporting Domain은 Core Domain에 의존할 수 있음**
   - 반대는 불가 (Core → Supporting 직접 의존 X)

3. **Generic Domain은 모든 도메인에서 사용 가능**
   - 하지만 비즈니스 로직 포함 금지

## 📝 용어 사전 (Ubiquitous Language)

| 용어 | 정의 | 예시 |
|------|------|------|
| Orchestrate | 여러 AI를 조율하여 작업 수행 | "Issue #82를 orchestrate한다" |
| Node | 하나의 독립적 작업 단위 | "분석 노드", "구현 노드" |
| DAG | 노드들의 워크플로우 | "feature_development DAG" |
| Pipeline | 순차적 실행 체인 | "Gemini → Claude → Codex" |
| Persona | AI에게 부여하는 전문가 역할 | "Backend Lead", "QA Engineer" |
| -p mode | 비대화형 프롬프트 실행 | "claude -p '작업 내용'" |
| Provenance | 결과의 출처 메타데이터 | "{source: 'ai', model: 'claude'}" |
