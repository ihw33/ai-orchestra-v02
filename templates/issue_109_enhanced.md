# [AI] Domain Events 시스템 구축 - DDD 이벤트 기반 아키텍처 구현

## 📌 개요
DDD 패턴의 Domain Events를 구현하여 시스템 간 느슨한 결합과 이벤트 소싱을 지원

## 🎯 비즈니스 요구사항
- **사용자 스토리**: As a 시스템, I want to 도메인 이벤트를 발행/구독 so that 컴포넌트 간 느슨한 결합 달성
- **기대 효과**: 시스템 확장성 향상, 이벤트 추적 가능, 감사 로그 자동화

## 🏗️ 기술 스펙

### 1. 도메인 모델
**파일**: `src/domain/events.py`
```python
from dataclasses import dataclass, field
from typing import Optional, Dict, Any
from datetime import datetime
from enum import Enum
import uuid

@dataclass
class DomainEvent:
    """도메인 이벤트 베이스 클래스"""
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    aggregate_id: str = ""
    event_type: str = ""
    occurred_at: datetime = field(default_factory=datetime.now)
    payload: Dict[str, Any] = field(default_factory=dict)
    version: int = 1
    
    def to_dict(self) -> Dict[str, Any]:
        """이벤트를 딕셔너리로 변환"""
        return {
            'event_id': self.event_id,
            'aggregate_id': self.aggregate_id,
            'event_type': self.event_type,
            'occurred_at': self.occurred_at.isoformat(),
            'payload': self.payload,
            'version': self.version
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DomainEvent':
        """딕셔너리에서 이벤트 생성"""
        data['occurred_at'] = datetime.fromisoformat(data['occurred_at'])
        return cls(**data)

# 구체적 이벤트 예시
@dataclass
class IssueCreatedEvent(DomainEvent):
    """이슈 생성 이벤트"""
    def __init__(self, issue_id: str, title: str, description: str):
        super().__init__(
            aggregate_id=issue_id,
            event_type="IssueCreated",
            payload={
                'title': title,
                'description': description
            }
        )
```

### 2. Port (인터페이스)
**파일**: `src/ports/event_port.py`
```python
from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any, Callable, Awaitable
from src.domain.events import DomainEvent

class EventBusPort(ABC):
    """이벤트 버스 인터페이스"""
    
    @abstractmethod
    async def publish(self, event: DomainEvent) -> None:
        """이벤트 발행"""
        pass
    
    @abstractmethod
    async def subscribe(self, event_type: str, handler: Callable[[DomainEvent], Awaitable[None]]) -> None:
        """이벤트 구독"""
        pass
    
    @abstractmethod
    async def unsubscribe(self, event_type: str, handler: Callable) -> None:
        """구독 해제"""
        pass

class EventStorePort(ABC):
    """이벤트 저장소 인터페이스"""
    
    @abstractmethod
    async def save(self, event: DomainEvent) -> None:
        """이벤트 저장"""
        pass
    
    @abstractmethod
    async def get_events(self, aggregate_id: str, after_version: int = 0) -> List[DomainEvent]:
        """특정 집계의 이벤트 조회"""
        pass
    
    @abstractmethod
    async def get_all_events(self, event_type: Optional[str] = None, limit: int = 100) -> List[DomainEvent]:
        """모든 이벤트 조회"""
        pass
```

### 3. Adapter (구현체)
**파일**: `src/adapters/event/event_bus_adapter.py`
```python
import asyncio
import logging
from typing import Dict, List, Callable, Awaitable
from collections import defaultdict
from src.ports.event_port import EventBusPort
from src.domain.events import DomainEvent

logger = logging.getLogger(__name__)

class AsyncEventBusAdapter(EventBusPort):
    """비동기 이벤트 버스 구현"""
    
    def __init__(self):
        """초기화"""
        self._handlers: Dict[str, List[Callable]] = defaultdict(list)
        self._queue: asyncio.Queue = asyncio.Queue()
        self._running = False
        
    async def publish(self, event: DomainEvent) -> None:
        """
        이벤트 발행
        1. 이벤트를 큐에 추가
        2. 등록된 핸들러들에게 비동기로 전달
        """
        logger.info(f"Publishing event: {event.event_type} for {event.aggregate_id}")
        
        handlers = self._handlers.get(event.event_type, [])
        
        # 병렬로 모든 핸들러 실행
        tasks = [handler(event) for handler in handlers]
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
    
    async def subscribe(self, event_type: str, handler: Callable[[DomainEvent], Awaitable[None]]) -> None:
        """이벤트 구독"""
        logger.info(f"Subscribing to {event_type}")
        self._handlers[event_type].append(handler)
    
    async def unsubscribe(self, event_type: str, handler: Callable) -> None:
        """구독 해제"""
        if handler in self._handlers[event_type]:
            self._handlers[event_type].remove(handler)
```

**파일**: `src/adapters/event/event_store_adapter.py`
```python
import sqlite3
import json
import logging
from typing import Optional, List
from datetime import datetime
from src.ports.event_port import EventStorePort
from src.domain.events import DomainEvent

logger = logging.getLogger(__name__)

class SQLiteEventStoreAdapter(EventStorePort):
    """SQLite 기반 이벤트 저장소"""
    
    def __init__(self, db_path: str = "events.db"):
        """
        초기화 및 테이블 생성
        Args:
            db_path: SQLite 데이터베이스 파일 경로
        """
        self.db_path = db_path
        self._init_db()
    
    def _init_db(self):
        """데이터베이스 초기화"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS events (
                    event_id TEXT PRIMARY KEY,
                    aggregate_id TEXT NOT NULL,
                    event_type TEXT NOT NULL,
                    occurred_at TEXT NOT NULL,
                    payload TEXT NOT NULL,
                    version INTEGER NOT NULL,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_aggregate ON events(aggregate_id)')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_event_type ON events(event_type)')
    
    async def save(self, event: DomainEvent) -> None:
        """이벤트 저장"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                INSERT INTO events (event_id, aggregate_id, event_type, occurred_at, payload, version)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                event.event_id,
                event.aggregate_id,
                event.event_type,
                event.occurred_at.isoformat(),
                json.dumps(event.payload),
                event.version
            ))
            logger.info(f"Event saved: {event.event_id}")
    
    async def get_events(self, aggregate_id: str, after_version: int = 0) -> List[DomainEvent]:
        """집계별 이벤트 조회"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute('''
                SELECT * FROM events 
                WHERE aggregate_id = ? AND version > ?
                ORDER BY version ASC
            ''', (aggregate_id, after_version))
            
            events = []
            for row in cursor.fetchall():
                event = DomainEvent(
                    event_id=row[0],
                    aggregate_id=row[1],
                    event_type=row[2],
                    occurred_at=datetime.fromisoformat(row[3]),
                    payload=json.loads(row[4]),
                    version=row[5]
                )
                events.append(event)
            
            return events
```

## 🔧 구현 체크리스트

### Gemini (아키텍처 설계)
- [ ] `src/ports/event_port.py` - EventBusPort, EventStorePort 인터페이스 정의
- [ ] `src/domain/events.py` - DomainEvent 베이스 클래스 및 구체 이벤트 정의
- [ ] 이벤트 플로우 다이어그램 작성

### Claude (핵심 구현)
- [ ] `src/adapters/event/event_bus_adapter.py` - AsyncEventBusAdapter 구현
- [ ] 이벤트 핸들러 등록/해제 로직
- [ ] 에러 처리 및 재시도 로직
- [ ] 유닛 테스트 작성

### Codex (백엔드/인프라)
- [ ] `src/adapters/event/event_store_adapter.py` - SQLiteEventStoreAdapter 구현
- [ ] 데이터베이스 스키마 및 인덱스 최적화
- [ ] 이벤트 조회 API 엔드포인트
- [ ] 통합 테스트 작성

## 🧪 테스트 요구사항

### 유닛 테스트
**파일**: `tests/unit/test_event_system.py`
```python
import pytest
import asyncio
from src.domain.events import DomainEvent, IssueCreatedEvent
from src.adapters.event.event_bus_adapter import AsyncEventBusAdapter

class TestEventBus:
    @pytest.mark.asyncio
    async def test_publish_subscribe(self):
        # Given: 이벤트 버스와 핸들러
        bus = AsyncEventBusAdapter()
        received_events = []
        
        async def handler(event: DomainEvent):
            received_events.append(event)
        
        # When: 구독하고 이벤트 발행
        await bus.subscribe("IssueCreated", handler)
        event = IssueCreatedEvent("123", "Test Issue", "Description")
        await bus.publish(event)
        
        # Then: 핸들러가 이벤트 수신
        assert len(received_events) == 1
        assert received_events[0].aggregate_id == "123"
```

## 📦 의존성
```txt
# requirements.txt에 추가
asyncio  # Python 내장
sqlite3  # Python 내장
pytest-asyncio==0.21.0  # 비동기 테스트용
```

## 🔌 시스템 통합
- **PM Processor**: 이슈 생성 시 IssueCreatedEvent 발행
- **Orchestrator**: 워크플로우 완료 시 WorkflowCompletedEvent 발행
- **Trigger System**: 이벤트 기반 트리거 추가

## ⚠️ 제약사항 및 고려사항
- **성능**: 이벤트 발행 100ms 이내
- **동시성**: 최대 1000 동시 이벤트 처리
- **내구성**: SQLite WAL 모드 사용
- **확장성**: 추후 Redis/Kafka로 교체 가능한 구조

## 📝 완료 조건
- [ ] 모든 필수 파일 생성 완료
- [ ] 유닛 테스트 통과 (coverage > 80%)
- [ ] 통합 테스트 통과
- [ ] 기존 시스템과 통합 완료
- [ ] 이벤트 발행/구독 동작 확인
- [ ] PR 생성 및 머지