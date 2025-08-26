# 🧬 Node-DAG-Executor 핵심 정의

## 📚 기본 개념

### Node (노드)
**정의**: 하나의 독립적인 작업 단위
```
Node = {
  입력(Input) + 처리(Process) + 출력(Output)
}
```

**특징**:
- 독립 실행 가능
- 재사용 가능
- 조합 가능

**예시**:
```yaml
Node: KEYWORD_ENRICHMENT
  입력: 이슈 제목, 본문
  처리: 키워드 분석
  출력: 라벨, 해시태그
```

### DAG (Directed Acyclic Graph)
**정의**: 노드들의 방향성 있는 비순환 연결
```
DAG = Node들 + 실행 순서 + 의존성
```

**패턴 종류**:
- **Sequential**: A → B → C (순차)
- **Parallel**: A → [B, C] → D (병렬)
- **Pipeline**: A | B | C (파이프라인)
- **Cascade**: A → [B → C, D → E] (계단식)

**예시**:
```
분석 DAG:
[READ] → [ANALYZE] → [REPORT]
```

### Executor (실행자)
**정의**: 노드를 실제로 실행하는 주체
```
Executor = AI | Script | Human | System
```

**종류**:
- **AI Executor**: Gemini, Claude, Codex
- **Script Executor**: Python, Bash, Node.js
- **Human Executor**: PM, 사용자
- **System Executor**: GitHub Actions, Cron

**할당 규칙**:
```python
if node.type == "ANALYSIS":
    executor = "Gemini"
elif node.type == "IMPLEMENTATION":
    executor = "Claude"
elif node.type == "TESTING":
    executor = "Codex"
```

## 🔧 활용 방법

### 1. 노드 정의
```python
class Node:
    def __init__(self, name, type, executor):
        self.name = name        # 노드 이름
        self.type = type        # 작업 유형
        self.executor = executor # 실행 주체
        self.input = None       # 입력 데이터
        self.output = None      # 출력 결과
```

### 2. DAG 구성
```python
class DAG:
    def __init__(self):
        self.nodes = []         # 노드 목록
        self.edges = []         # 연결 관계
        
    def add_node(self, node):
        self.nodes.append(node)
        
    def connect(self, from_node, to_node):
        self.edges.append((from_node, to_node))
```

### 3. Executor 실행
```python
class Executor:
    def execute(self, node):
        if self.type == "AI":
            return self.run_ai(node)
        elif self.type == "Script":
            return self.run_script(node)
```

## 📊 표준 노드 타입

| 타입 | 설명 | 주 실행자 |
|------|------|----------|
| ANALYZE | 분석 작업 | Gemini |
| IMPLEMENT | 구현 작업 | Claude |
| TEST | 테스트 작업 | Codex |
| DOCUMENT | 문서화 작업 | Claude |
| REVIEW | 검토 작업 | PM |
| DEPLOY | 배포 작업 | Script |
| MONITOR | 모니터링 | System |

## 🎯 실제 사용 예시

### 새 기능 추가 시
```yaml
1. 노드 정의:
   name: AUTO_BACKUP
   type: SYSTEM
   executor: Script
   
2. DAG 구성:
   [DETECT_CHANGE] → [CREATE_COMMIT] → [PUSH]
   
3. 카탈로그 등록:
   NODE_DAG_PATTERNS.md에 추가
```

### 작업 실행 시
```bash
# 1. 필요한 노드 선택
nodes = ["CREATE_ISSUE", "KEYWORD_ENRICHMENT", "AI_ANALYSIS"]

# 2. DAG 구성
dag = Sequential(nodes)

# 3. 실행
executor.run(dag)
```

## 🔗 관련 문서

- **NODE_DAG_PATTERNS.md**: 패턴 예시 모음
- **MODULAR_WORKFLOW_SYSTEM.md**: 노드 카탈로그
- **PM_ISSUE_CREATION_GUIDE.md**: 실전 활용법

## 💡 핵심 원칙

1. **모든 작업은 노드다**
2. **노드는 조합하여 DAG를 만든다**
3. **DAG는 Executor가 실행한다**
4. **새 기능 = 새 노드/DAG로 등록**
5. **재사용과 조합으로 성장**