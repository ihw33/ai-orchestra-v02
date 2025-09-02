# 🥚 AI Orchestra Evolution System

AI Orchestra가 작업할 때마다 경험치를 얻고 성장하는 시스템입니다.

## 📊 경험치 테이블

### GitHub 작업
- `CREATE_ISSUE`: **+3** - 이슈 생성
- `CLOSE_ISSUE`: **+8** - 이슈 완료 (보너스)
- `CREATE_PR`: **+5** - PR 생성
- `MERGE_PR`: **+10** - PR 머지 (큰 보상)
- `ADD_COMMENT`: **+2** - 코멘트 추가
- `UPDATE_LABELS`: **+1** - 라벨 업데이트

### 코드 작성
- `FIX_BUG_LINE`: **+8** - 버그 수정
- `WRITE_FUNCTION`: **+6** - 함수 작성
- `CREATE_CLASS`: **+8** - 클래스 생성
- `WRITE_TEST_CASE`: **+6** - 테스트 케이스 작성

### 코드 리뷰
- `REVIEW_CODE` (성공): **+8** - 코드 리뷰 통과
- `REVIEW_CODE` (실패): **-5** - 코드 리뷰 실패 (감점!)

### 기타
- 테이블에 없는 노드: **+3** (기본값)
- 일반 실패: **0** (경험치 없음)

## 🐣 진화 단계

| 레벨 | 경험치 | 모습 | 이름 |
|------|--------|------|------|
| Lv.1 | 0-49 | 🥚 | 알 |
| Lv.2 | 50-149 | 🐣 | 부화 |
| Lv.3 | 150-299 | 🐥 | 병아리 |
| Lv.4 | 300-499 | 🐤 | 성장 |
| Lv.5 | 500-799 | 🦆 | 오리 |
| Lv.6 | 800-1199 | 🦅 | 독수리 |
| Lv.7 | 1200+ | 🐉 | 드래곤 |

## 📁 파일 구조

- **orchestra_status.txt**: 현재 상태 (1줄)
  ```
  [Lv.2 🐣] 노드:45 | 성공:87% | exp:125
  ```

- **orchestra.log**: 작업 이력 (append-only)
  ```
  2025-01-26 14:23:01 | COMPLETE | FIX_BUG_LINE | exp:+8
  2025-01-26 14:25:33 | LEVEL_UP | 🐣→🐥
  2025-01-26 14:26:15 | COMPLETE | REVIEW_CODE | exp:-5
  ```

## 💡 특별 규칙

1. **WRITE_TEST_CASE**는 단위 테스트 작성시 부여
2. **기본값 +3**은 새로운 노드 타입이 추가되었을 때 자동 적용
3. **코드 리뷰 실패**는 유일한 감점 요소 (-5)
4. **경험치는 0 이하로 떨어지지 않음** (보호 장치)

## 🚀 사용법

```python
from evolution_logger import get_logger

logger = get_logger()

# 노드 완료시 자동 호출 (node_system.py에 통합됨)
result = logger.on_node_complete("FIX_BUG_LINE", success=True)

if result['level_up']:
    print(f"🎉 레벨업! {result['form']} Lv.{result['level']}")

# 현재 상태 확인
logger.show_progress()
```

## 📈 성장 목표

- **초급 (Lv.1-3)**: 기본 작업 수행
- **중급 (Lv.4-5)**: 복잡한 워크플로우 처리
- **고급 (Lv.6-7)**: 자가 진화 시스템 활성화

리소스 부담 없이 AI Orchestra의 성장을 추적할 수 있는 가벼운 시스템입니다!