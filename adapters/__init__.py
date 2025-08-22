"""
Adapter registry for AI Orchestra v02
"""

from typing import Dict, Type, Optional
from .base import BaseAdapter

# 어댑터 레지스트리
_registry: Dict[str, Type[BaseAdapter]] = {}


def register_adapter(name: str, adapter_class: Type[BaseAdapter]) -> None:
    """어댑터 등록"""
    _registry[name] = adapter_class


def get_adapter(name: str) -> Optional[Type[BaseAdapter]]:
    """어댑터 클래스 가져오기"""
    return _registry.get(name)


def list_adapters() -> list[str]:
    """등록된 어댑터 목록"""
    return list(_registry.keys())


__all__ = [
    'BaseAdapter',
    'register_adapter',
    'get_adapter',
    'list_adapters'
]