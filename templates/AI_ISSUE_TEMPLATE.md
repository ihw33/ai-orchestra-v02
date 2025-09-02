# [AI] {기능명}

## 📌 개요
{기능 설명 1-2줄}

## 🎯 비즈니스 요구사항
- **사용자 스토리**: As a {사용자}, I want to {기능} so that {가치}
- **기대 효과**: {측정 가능한 효과}

## 🏗️ 기술 스펙

### 1. 도메인 모델
**파일**: `src/domain/{도메인}.py`
```python
from dataclasses import dataclass
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

@dataclass
class {ClassName}:
    """도메인 엔티티 설명"""
    id: str
    {속성1}: {타입1}
    {속성2}: {타입2}
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    def {비즈니스_메소드}(self, {파라미터}: {타입}) -> {리턴타입}:
        """
        메소드가 하는 일
        Args:
            {파라미터}: 설명
        Returns:
            {리턴타입}: 설명
        Raises:
            {예외}: 언제 발생
        """
        pass
```

### 2. Port (인터페이스)
**파일**: `src/ports/{기능}_port.py`
```python
from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any
from src.domain.{도메인} import {ClassName}

class {기능}Port(ABC):
    """Port 인터페이스 설명"""
    
    @abstractmethod
    def {조회_메소드}(self, {id}: str) -> Optional[{ClassName}]:
        """ID로 엔티티 조회"""
        pass
    
    @abstractmethod
    def {생성_메소드}(self, {data}: Dict[str, Any]) -> {ClassName}:
        """새 엔티티 생성"""
        pass
    
    @abstractmethod
    def {수정_메소드}(self, {id}: str, {data}: Dict[str, Any]) -> bool:
        """엔티티 수정"""
        pass
    
    @abstractmethod
    def {삭제_메소드}(self, {id}: str) -> bool:
        """엔티티 삭제"""
        pass
```

### 3. Adapter (구현체)
**파일**: `src/adapters/{카테고리}/{기능}_adapter.py`
```python
import logging
from typing import Optional, List, Dict, Any
from src.ports.{기능}_port import {기능}Port
from src.domain.{도메인} import {ClassName}

logger = logging.getLogger(__name__)

class {기능}Adapter({기능}Port):
    """Adapter 구현체 설명"""
    
    def __init__(self, {의존성_파라미터}):
        """
        초기화
        Args:
            {의존성_파라미터}: 설명
        """
        self.{의존성} = {의존성_파라미터}
        # 추가 초기화
        
    def {조회_메소드}(self, {id}: str) -> Optional[{ClassName}]:
        """
        구현 세부사항:
        1. {단계1}
        2. {단계2}
        사용 라이브러리: {라이브러리명}
        """
        try:
            # 구현
            pass
        except Exception as e:
            logger.error(f"에러 발생: {e}")
            return None
    
    def {생성_메소드}(self, {data}: Dict[str, Any]) -> {ClassName}:
        """구현"""
        pass
```

## 🔧 구현 체크리스트

### Gemini (아키텍처 설계)
- [ ] `src/ports/{기능}_port.py` - Port 인터페이스 정의
- [ ] `src/domain/{도메인}.py` - 도메인 모델 설계
- [ ] 시스템 통합 지점 정의 문서 작성
- [ ] 클래스 다이어그램 작성 (선택)

### Claude (핵심 구현)
- [ ] `src/adapters/{카테고리}/{기능}_adapter.py` - Adapter 구현
- [ ] 비즈니스 로직 구현
- [ ] 에러 처리 및 예외 클래스 정의
- [ ] 유닛 테스트 작성

### Codex (백엔드/인프라)
- [ ] 데이터 저장소 어댑터 구현
- [ ] API 엔드포인트 구현 (필요시)
- [ ] 외부 시스템 연동 어댑터
- [ ] 통합 테스트 작성

## 🧪 테스트 요구사항

### 유닛 테스트
**파일**: `tests/unit/test_{기능}.py`
```python
import pytest
from src.adapters.{카테고리}.{기능}_adapter import {기능}Adapter

class Test{기능}:
    def test_{정상_시나리오}(self):
        # Given: 초기 상태 설정
        adapter = {기능}Adapter()
        
        # When: 액션 수행
        result = adapter.{메소드}()
        
        # Then: 기대 결과 검증
        assert result == expected
    
    def test_{예외_시나리오}(self):
        # 예외 케이스 테스트
        with pytest.raises({예외클래스}):
            adapter.{메소드}({잘못된_입력})
```

### 통합 테스트
**파일**: `tests/integration/test_{기능}_integration.py`
```python
def test_{전체_플로우}():
    # End-to-end 시나리오 테스트
    pass
```

## 📦 의존성
```txt
# requirements.txt에 추가
{라이브러리1}=={버전}
{라이브러리2}=={버전}
```

## 🔌 시스템 통합
- **연동 포트**: `{기존Port}Port`
- **연동 어댑터**: `{기존Adapter}Adapter`
- **이벤트 발행**: `{EventName}Event`
- **설정 필요**: `config/{기능}.yaml`

## ⚠️ 제약사항 및 고려사항
- **성능**: {응답시간} 이내 처리
- **동시성**: 최대 {동시접속수} 동시 처리
- **보안**: {보안 요구사항}
- **확장성**: {확장 고려사항}
- **호환성**: Python 3.8+

## 📝 완료 조건
- [ ] 모든 필수 파일 생성 완료
- [ ] 유닛 테스트 통과 (coverage > 80%)
- [ ] 통합 테스트 통과
- [ ] 코드 리뷰 완료
- [ ] 문서화 완료
- [ ] PR 생성 및 머지

## 📎 참고 자료
- [관련 문서 링크]
- [API 문서]
- [라이브러리 문서]