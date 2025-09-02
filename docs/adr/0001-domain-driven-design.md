# ADR-001: 도메인 기반 설계 및 Ports & Adapters 패턴 채택

- 상태: 승인됨
- 날짜: 2025-09-02
- 작성자: PM Claude

## 배경(문제/문맥)
- AI와 코드가 뒤섞여 있어 책임 경계가 불명확
- 시간이 지나면서 주요 기능이 자도 모르게 변경됨
- 다른 프로젝트에 이식이 어려움
- 누가 무엇을 생성했는지 추적 불가

## 결정(Decision)
Ports & Adapters(Hexagonal) 아키텍처 패턴을 채택하여 도메인 로직과 외부 시스템(AI CLI)을 명확히 분리한다.

## 근거(Why)
- **명확한 경계**: AI와 코드의 책임 분리
- **테스트 용이성**: AI 없이도 테스트 가능
- **이식성**: 어떤 프로젝트에도 적용 가능
- **추적성**: 모든 출력에 Provenance 메타데이터

## 대안(Alternatives)
- **모놀리식 구조** (폐기): 현재의 문제를 해결하지 못함
- **완전 재작성** (폐기): 기존 시스템 파괴, 위험도 높음
- **현상 유지** (폐기): 문제가 계속 악화됨

## 결과(Consequences)
### 긍정적
- AI 의존성 제거 가능 (Rules Adapter로 대체)
- 명확한 테스트 경계
- 점진적 마이그레이션 가능

### 부정적
- 초기 구현 복잡도 증가
- 기존 코드 수정 필요
- 학습 곡선 존재

## 기록(Traceability)
- 관련 이슈: #82
- 참고 문서: /Users/m4_macbook/Documents/thomas_vault/inbox/도메인 기반 개발에 대한 대화.md
- Provenance: {
    "source": "pm_claude",
    "decision_type": "architecture",
    "impact": "high",
    "reversible": true
  }
