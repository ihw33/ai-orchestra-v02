# ADR 0004: 보고 시스템 도입

- 상태: 제안됨
- 날짜: 2025-09-02
- 작성자: PM Claude

## 배경(문제/문맥)
- PM이 임의로 GitHub 댓글 보고를 작성
- "이것도 네가 임의로 한거면 안되고 댓글보고라는 하나의 어댑터가 존재해야"
- 보고 활동도 시스템화되어야 함

## 결정(Decision)
1. **ReporterPort 도입**: 모든 보고 활동의 인터페이스 정의
2. **GitHubReporterAdapter**: GitHub Issue 댓글 보고 구현
3. **보고 규칙 정의**: 언제, 무엇을, 어떻게 보고할지 규칙화

## 근거(Why)
- **일관성**: 모든 보고가 동일한 형식
- **추적성**: 모든 보고에 ID와 Provenance
- **자동화**: 이벤트 기반 자동 보고
- **확장성**: 다른 플랫폼(Slack, Email 등)으로 확장 가능

## 대안(Alternatives)
1. ❌ 임의 보고 → 일관성 없음, 추적 어려움
2. ❌ 수동 보고만 → 누락 가능성, 비효율
3. ✅ 시스템화된 보고 → 일관성, 자동화, 추적성

## 결과(Consequences)
### 긍정적
- 보고 일관성 확보
- 자동 보고로 효율성 증대
- 모든 보고 추적 가능

### 부정적
- 초기 구현 오버헤드
- 보고 규칙 관리 필요

## 구현 예시

### 보고가 필요한 시점
```python
# 자동 보고 트리거
- 작업 완료 시
- 에러 발생 시
- 마일스톤 달성 시
- 25% 단위 진행률 변경 시
- AI 실행 완료 시
- 에스컬레이션 필요 시
```

### 사용 방법
```python
from src.adapters.github.github_reporter_adapter import GitHubReporterAdapter

reporter = GitHubReporterAdapter()

# 완료 보고
reporter.report_completion("82", {
    'completed_tasks': ['버그 수정', 'Adapter 구현'],
    'created_files': ['reporter_port.py', 'github_reporter_adapter.py'],
    'next_steps': ['테스트', '문서화']
})
```

## 기록(Traceability)
- 트리거: 사용자 피드백 "댓글보고라는 하나의 어댑터가 존재해야"
- 관련 ADR: ADR-0001 (Ports & Adapters)
- Issue: #82
- Provenance: {source: "pm_claude", model: "claude-3.5", prompt_hash: "report_sys_001"}