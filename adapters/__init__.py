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


def _init_adapters():
    """기본 어댑터 초기화"""
    # Lazy import to avoid circular dependencies
    try:
        from .tmux_adapter import TmuxAdapter
        register_adapter("tmux", TmuxAdapter)
    except ImportError:
        pass
    
    try:
        from .gemini_adapter import GeminiAdapter
        register_adapter("gemini", GeminiAdapter)
    except ImportError:
        pass


# 모듈 로드 시 초기화
_init_adapters()


__all__ = [
    'BaseAdapter',
    'register_adapter',
    'get_adapter',
    'list_adapters'
]