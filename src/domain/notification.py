"""
Notification Domain Model

실시간 알림 시스템의 핵심 도메인 모델을 정의합니다.
- 알림 엔티티
- 우선순위 시스템
- 읽음/안읽음 상태 관리
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, Any, Optional, List
import uuid
from abc import ABC, abstractmethod


class NotificationPriority(Enum):
    """알림 우선순위"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"


class NotificationType(Enum):
    """알림 유형"""
    SYSTEM = "system"
    TASK_COMPLETED = "task_completed"
    TASK_ASSIGNED = "task_assigned"
    ISSUE_UPDATED = "issue_updated"
    PR_REVIEW = "pr_review"
    DEPLOYMENT = "deployment"
    ERROR_ALERT = "error_alert"


@dataclass
class NotificationMetadata:
    """알림 메타데이터"""
    source: str = ""
    action_url: Optional[str] = None
    issue_number: Optional[int] = None
    pr_number: Optional[int] = None
    repository: Optional[str] = None
    additional_data: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Notification:
    """
    알림 엔티티
    
    비즈니스 규칙:
    1. id는 자동 생성되며 변경 불가
    2. 생성 시간은 자동 설정
    3. 읽음 처리 시 read_at 자동 설정
    4. 우선순위에 따라 TTL 결정
    """
    user_id: str
    title: str
    message: str
    notification_type: NotificationType
    priority: NotificationPriority = NotificationPriority.NORMAL
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    is_read: bool = False
    created_at: datetime = field(default_factory=datetime.utcnow)
    read_at: Optional[datetime] = None
    metadata: NotificationMetadata = field(default_factory=NotificationMetadata)
    
    def mark_as_read(self) -> None:
        """알림을 읽음으로 표시"""
        if not self.is_read:
            self.is_read = True
            self.read_at = datetime.utcnow()
    
    def mark_as_unread(self) -> None:
        """알림을 안읽음으로 표시"""
        self.is_read = False
        self.read_at = None
    
    def get_ttl_seconds(self) -> int:
        """우선순위에 따른 TTL 반환 (초)"""
        ttl_map = {
            NotificationPriority.CRITICAL: 86400,  # 1일
            NotificationPriority.HIGH: 604800,     # 1주
            NotificationPriority.NORMAL: 2592000,  # 30일
            NotificationPriority.LOW: 7776000      # 90일
        }
        return ttl_map[self.priority]
    
    def to_dict(self) -> Dict[str, Any]:
        """딕셔너리로 변환 (JSON 직렬화용)"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "title": self.title,
            "message": self.message,
            "notification_type": self.notification_type.value,
            "priority": self.priority.value,
            "is_read": self.is_read,
            "created_at": self.created_at.isoformat(),
            "read_at": self.read_at.isoformat() if self.read_at else None,
            "metadata": {
                "source": self.metadata.source,
                "action_url": self.metadata.action_url,
                "issue_number": self.metadata.issue_number,
                "pr_number": self.metadata.pr_number,
                "repository": self.metadata.repository,
                "additional_data": self.metadata.additional_data
            }
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Notification':
        """딕셔너리에서 생성"""
        metadata = NotificationMetadata(
            source=data["metadata"].get("source", ""),
            action_url=data["metadata"].get("action_url"),
            issue_number=data["metadata"].get("issue_number"),
            pr_number=data["metadata"].get("pr_number"),
            repository=data["metadata"].get("repository"),
            additional_data=data["metadata"].get("additional_data", {})
        )
        
        notification = cls(
            id=data["id"],
            user_id=data["user_id"],
            title=data["title"],
            message=data["message"],
            notification_type=NotificationType(data["notification_type"]),
            priority=NotificationPriority(data["priority"]),
            is_read=data["is_read"],
            created_at=datetime.fromisoformat(data["created_at"]),
            read_at=datetime.fromisoformat(data["read_at"]) if data["read_at"] else None,
            metadata=metadata
        )
        return notification


@dataclass
class NotificationQueue:
    """
    사용자별 알림 큐
    
    비즈니스 규칙:
    1. 우선순위 기반 정렬
    2. 읽지 않은 알림 우선 표시
    3. 최대 큐 사이즈 제한
    """
    user_id: str
    notifications: List[Notification] = field(default_factory=list)
    max_size: int = 1000
    
    def add_notification(self, notification: Notification) -> bool:
        """알림 추가"""
        if len(self.notifications) >= self.max_size:
            # 가장 오래된 읽은 알림 제거
            self._remove_oldest_read()
        
        # 우선순위 기반으로 삽입
        insert_index = self._find_insert_position(notification)
        self.notifications.insert(insert_index, notification)
        return True
    
    def mark_notification_read(self, notification_id: str) -> bool:
        """특정 알림을 읽음으로 표시"""
        for notification in self.notifications:
            if notification.id == notification_id:
                notification.mark_as_read()
                return True
        return False
    
    def get_unread_notifications(self) -> List[Notification]:
        """읽지 않은 알림 조회"""
        return [n for n in self.notifications if not n.is_read]
    
    def get_notifications_by_priority(self, priority: NotificationPriority) -> List[Notification]:
        """우선순위별 알림 조회"""
        return [n for n in self.notifications if n.priority == priority]
    
    def remove_notification(self, notification_id: str) -> bool:
        """알림 제거"""
        for i, notification in enumerate(self.notifications):
            if notification.id == notification_id:
                del self.notifications[i]
                return True
        return False
    
    def cleanup_expired_notifications(self) -> int:
        """만료된 알림 정리"""
        current_time = datetime.utcnow()
        removed_count = 0
        
        for i in range(len(self.notifications) - 1, -1, -1):
            notification = self.notifications[i]
            elapsed_seconds = (current_time - notification.created_at).total_seconds()
            
            if elapsed_seconds > notification.get_ttl_seconds():
                del self.notifications[i]
                removed_count += 1
        
        return removed_count
    
    def _find_insert_position(self, notification: Notification) -> int:
        """우선순위 기반 삽입 위치 찾기"""
        priority_order = {
            NotificationPriority.CRITICAL: 0,
            NotificationPriority.HIGH: 1,
            NotificationPriority.NORMAL: 2,
            NotificationPriority.LOW: 3
        }
        
        target_priority = priority_order[notification.priority]
        
        for i, existing_notification in enumerate(self.notifications):
            existing_priority = priority_order[existing_notification.priority]
            if target_priority < existing_priority:
                return i
            elif target_priority == existing_priority:
                # 같은 우선순위면 최신순으로
                if notification.created_at > existing_notification.created_at:
                    return i
        
        return len(self.notifications)
    
    def _remove_oldest_read(self) -> None:
        """가장 오래된 읽은 알림 제거"""
        for i in range(len(self.notifications) - 1, -1, -1):
            if self.notifications[i].is_read:
                del self.notifications[i]
                break


class NotificationRepository(ABC):
    """알림 저장소 인터페이스"""
    
    @abstractmethod
    async def save_notification(self, notification: Notification) -> bool:
        """알림 저장"""
        pass
    
    @abstractmethod
    async def get_notifications_by_user(self, user_id: str, limit: int = 50) -> List[Notification]:
        """사용자별 알림 조회"""
        pass
    
    @abstractmethod
    async def mark_notification_read(self, notification_id: str) -> bool:
        """알림 읽음 처리"""
        pass
    
    @abstractmethod
    async def delete_notification(self, notification_id: str) -> bool:
        """알림 삭제"""
        pass
    
    @abstractmethod
    async def cleanup_expired_notifications(self, user_id: str) -> int:
        """만료된 알림 정리"""
        pass


class NotificationService:
    """알림 도메인 서비스"""
    
    def __init__(self, repository: NotificationRepository):
        self.repository = repository
        self._queues: Dict[str, NotificationQueue] = {}
    
    async def create_notification(
        self,
        user_id: str,
        title: str,
        message: str,
        notification_type: NotificationType,
        priority: NotificationPriority = NotificationPriority.NORMAL,
        metadata: Optional[NotificationMetadata] = None
    ) -> Notification:
        """새 알림 생성"""
        notification = Notification(
            user_id=user_id,
            title=title,
            message=message,
            notification_type=notification_type,
            priority=priority,
            metadata=metadata or NotificationMetadata()
        )
        
        # 저장소에 저장
        await self.repository.save_notification(notification)
        
        # 메모리 큐에 추가
        self._add_to_queue(notification)
        
        return notification
    
    def get_user_queue(self, user_id: str) -> NotificationQueue:
        """사용자 큐 조회"""
        if user_id not in self._queues:
            self._queues[user_id] = NotificationQueue(user_id)
        return self._queues[user_id]
    
    def _add_to_queue(self, notification: Notification) -> None:
        """큐에 알림 추가"""
        queue = self.get_user_queue(notification.user_id)
        queue.add_notification(notification)
    
    async def cleanup_expired_notifications(self, user_id: str) -> int:
        """만료된 알림 정리"""
        # 메모리 큐 정리
        queue = self.get_user_queue(user_id)
        memory_cleaned = queue.cleanup_expired_notifications()
        
        # 저장소 정리
        storage_cleaned = await self.repository.cleanup_expired_notifications(user_id)
        
        return memory_cleaned + storage_cleaned