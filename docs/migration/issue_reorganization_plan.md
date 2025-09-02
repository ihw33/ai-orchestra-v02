# 기존 이슈 재구성 계획

## 현재 상태
- ✅ 새 형식 (Epic/Story/Task): 6개
- 🔄 [AI] 태그 형식: 8개
- 📝 기타 기존 형식: 11개
- 총 Open 이슈: 25개

## 재구성 방안

### 1. Epic으로 승격할 이슈
```
#54 → [Epic] AI Orchestra 2025 로드맵
#81 → [Epic] IWL 솔루션 개발 오케스트레이션
```

### 2. 기존 Epic에 Story로 편입

#### Epic #88 (GitHub 워크플로우 자동화)에 편입
```
#87 [AI] Smart Issue Creator → [Story] 스마트 이슈 생성 시스템
#84 [AI] Golden Set → [Story] Golden Set 시스템
#74 [AI] PR 코드 리뷰 → Story #90의 Task로
#34 [Template] → Story #89의 Task로
```

#### Epic #35 (100 AI 협업)에 편입
```
#82 [AI] 도메인 기반 개발 → [Story] 도메인 기반 아키텍처
#79 [AI] 자가 진화 → [Story] 자가 진화 시스템
#75 [AI] Node-DAG-Executor → [Story] 워크플로우 엔진
#55 [워크플로우] 자동화 패턴 → Story #75의 Task로
```

#### Epic #1 (AI Orchestra v02 기반)에 편입
```
#80 [AI] Context7 고도화 → [Story] Context 관리 시스템
#78 [AI] 이식 가능성 → [Story] 솔루션 이식성
#11 [v03] 업무 자동화 → [Story] 프로세스 자동화
#10 [Enhancement] SLO → Task로
#9 [Enhancement] DLQ → Task로
#17, #18 → Task로
```

### 3. Spike로 전환
```
#56 [분석] 패턴 분석 → [Spike] 패턴 분석 (1개월 후)
```

## 실행 계획

### Phase 1: Epic 정리
1. 새 Epic 생성 (#54, #81 → Epic)
2. Epic에 하위 Story 연결

### Phase 2: Story 재배치
1. [AI] 태그 이슈들을 적절한 Epic 하위 Story로 변환
2. 제목에 [Story] 추가
3. 부모 Epic 참조 추가

### Phase 3: Task 정리
1. 작은 이슈들을 관련 Story의 Task로 변환
2. 제목에 [Task] 추가
3. 적절한 라벨 부여

## 라벨 정리
```yaml
추가 필요:
- spike: 조사/연구 (노란색)
- bug: 버그 (이미 있음)
- deprecated: 더 이상 필요 없음

정리:
- ai-task → task로 통일
- priority-high → p0로 통일
```

## 예상 결과
```
Epic (5-6개)
├── Story (15-20개)
│   └── Task (20-30개)
└── Spike (2-3개)
```

## 자동화 스크립트
```python
# 이슈 일괄 수정 스크립트
def reorganize_issues():
    # 1. 이슈 목록 가져오기
    # 2. 분류 규칙 적용
    # 3. 제목/본문 수정
    # 4. 라벨 업데이트
    pass
```