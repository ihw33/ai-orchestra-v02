#!/usr/bin/env python3
"""
통합 에러 처리 및 로깅 시스템
모든 모듈에서 사용할 수 있는 에러 처리 유틸리티
"""

import logging
import traceback
import json
import os
from datetime import datetime
from typing import Any, Optional, Dict, Callable
from functools import wraps
import time

# 로그 디렉토리 생성
LOG_DIR = "logs"
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

class OrchestraError(Exception):
    """기본 Orchestra 에러 클래스"""
    pass

class AIExecutionError(OrchestraError):
    """AI 실행 관련 에러"""
    pass

class GitHubAPIError(OrchestraError):
    """GitHub API 관련 에러"""
    pass

class TimeoutError(OrchestraError):
    """타임아웃 에러"""
    pass

class ErrorHandler:
    """통합 에러 처리기"""
    
    def __init__(self, module_name: str = "orchestra"):
        self.module_name = module_name
        self.setup_logging()
        self.error_count = 0
        self.error_history = []
        
    def setup_logging(self):
        """로깅 설정"""
        # 파일 핸들러
        log_file = os.path.join(LOG_DIR, f"{self.module_name}_{datetime.now().strftime('%Y%m%d')}.log")
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)
        
        # 콘솔 핸들러
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # 포맷터
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        # 로거 설정
        self.logger = logging.getLogger(self.module_name)
        self.logger.setLevel(logging.DEBUG)
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
    
    def log_error(self, error: Exception, context: Dict = None):
        """에러 로깅"""
        self.error_count += 1
        
        error_info = {
            'timestamp': datetime.now().isoformat(),
            'error_type': type(error).__name__,
            'error_message': str(error),
            'traceback': traceback.format_exc(),
            'context': context or {}
        }
        
        self.error_history.append(error_info)
        
        # 파일에 기록
        self.logger.error(f"Error #{self.error_count}: {error}")
        self.logger.debug(f"Context: {json.dumps(context or {}, indent=2)}")
        
        # 에러 파일에도 저장
        error_file = os.path.join(LOG_DIR, f"errors_{datetime.now().strftime('%Y%m%d')}.json")
        try:
            with open(error_file, 'a') as f:
                json.dump(error_info, f)
                f.write('\n')
        except:
            pass
        
        return error_info
    
    def safe_execute(self, func: Callable, *args, **kwargs) -> tuple[bool, Any]:
        """안전한 함수 실행"""
        try:
            result = func(*args, **kwargs)
            return True, result
        except Exception as e:
            self.log_error(e, {'function': func.__name__, 'args': str(args), 'kwargs': str(kwargs)})
            return False, None
    
    def get_error_summary(self) -> Dict:
        """에러 요약 반환"""
        return {
            'total_errors': self.error_count,
            'recent_errors': self.error_history[-10:],
            'error_types': self._count_error_types()
        }
    
    def _count_error_types(self) -> Dict[str, int]:
        """에러 타입별 카운트"""
        types = {}
        for error in self.error_history:
            error_type = error['error_type']
            types[error_type] = types.get(error_type, 0) + 1
        return types

def retry_on_error(max_retries: int = 3, delay: float = 1.0, backoff: float = 2.0):
    """재시도 데코레이터"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            handler = ErrorHandler(func.__module__)
            
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_retries - 1:
                        handler.log_error(e, {
                            'function': func.__name__,
                            'attempt': attempt + 1,
                            'max_retries': max_retries
                        })
                        raise
                    
                    wait_time = delay * (backoff ** attempt)
                    handler.logger.warning(
                        f"Attempt {attempt + 1}/{max_retries} failed for {func.__name__}. "
                        f"Retrying in {wait_time:.1f}s..."
                    )
                    time.sleep(wait_time)
            
            return None
        return wrapper
    return decorator

def handle_errors(error_handler: Optional[ErrorHandler] = None):
    """에러 처리 데코레이터"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            handler = error_handler or ErrorHandler(func.__module__)
            
            try:
                return func(*args, **kwargs)
            except Exception as e:
                handler.log_error(e, {
                    'function': func.__name__,
                    'args': str(args)[:200],
                    'kwargs': str(kwargs)[:200]
                })
                
                # 에러 타입에 따른 처리
                if isinstance(e, TimeoutError):
                    handler.logger.error("⏱️ Operation timed out")
                    return {'success': False, 'error': 'Timeout', 'error_type': 'timeout'}
                elif isinstance(e, GitHubAPIError):
                    handler.logger.error("🐙 GitHub API error")
                    return {'success': False, 'error': str(e), 'error_type': 'github'}
                elif isinstance(e, AIExecutionError):
                    handler.logger.error("🤖 AI execution error")
                    return {'success': False, 'error': str(e), 'error_type': 'ai'}
                else:
                    handler.logger.error(f"❌ Unexpected error: {e}")
                    return {'success': False, 'error': str(e), 'error_type': 'unknown'}
        
        return wrapper
    return decorator

class SafeExecutor:
    """안전한 실행을 위한 컨텍스트 매니저"""
    
    def __init__(self, operation_name: str, handler: Optional[ErrorHandler] = None):
        self.operation_name = operation_name
        self.handler = handler or ErrorHandler("SafeExecutor")
        self.start_time = None
        
    def __enter__(self):
        self.start_time = time.time()
        self.handler.logger.info(f"Starting: {self.operation_name}")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        elapsed = time.time() - self.start_time
        
        if exc_type is None:
            self.handler.logger.info(
                f"Completed: {self.operation_name} ({elapsed:.2f}s)"
            )
        else:
            self.handler.log_error(exc_val, {
                'operation': self.operation_name,
                'elapsed_time': elapsed
            })
            
        # 에러를 재발생시키지 않음 (처리됨)
        return True

# 전역 에러 핸들러
global_handler = ErrorHandler("global")

def log_info(message: str):
    """정보 로깅"""
    global_handler.logger.info(message)

def log_warning(message: str):
    """경고 로깅"""
    global_handler.logger.warning(message)

def log_error(message: str, error: Optional[Exception] = None):
    """에러 로깅"""
    if error:
        global_handler.log_error(error, {'message': message})
    else:
        global_handler.logger.error(message)

def log_debug(message: str):
    """디버그 로깅"""
    global_handler.logger.debug(message)

# 사용 예제
if __name__ == "__main__":
    # 데코레이터 사용
    @retry_on_error(max_retries=3, delay=1)
    def flaky_function():
        import random
        if random.random() < 0.7:
            raise Exception("Random failure")
        return "Success!"
    
    # 컨텍스트 매니저 사용
    with SafeExecutor("Test Operation"):
        print("Doing something...")
        # raise Exception("Test error")
    
    # 직접 로깅
    log_info("This is info")
    log_warning("This is warning")
    log_error("This is error")
    
    print("\n📊 Error Summary:")
    print(json.dumps(global_handler.get_error_summary(), indent=2))