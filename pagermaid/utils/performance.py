import asyncio
import time
import functools
from typing import Any, Callable, Dict, Optional
from collections import OrderedDict
import psutil
import logging

logger = logging.getLogger(__name__)


class PerformanceMonitor:
    """性能监控器"""
    
    def __init__(self):
        self.metrics: Dict[str, list] = {}
        self.start_times: Dict[str, float] = {}
    
    def start_timer(self, name: str):
        """开始计时"""
        self.start_times[name] = time.time()
    
    def end_timer(self, name: str):
        """结束计时并记录"""
        if name in self.start_times:
            duration = time.time() - self.start_times[name]
            if name not in self.metrics:
                self.metrics[name] = []
            self.metrics[name].append(duration)
            del self.start_times[name]
            logger.debug(f"Performance: {name} took {duration:.3f}s")
    
    def get_average_time(self, name: str) -> Optional[float]:
        """获取平均执行时间"""
        if name in self.metrics and self.metrics[name]:
            return sum(self.metrics[name]) / len(self.metrics[name])
        return None
    
    def get_system_stats(self) -> Dict[str, float]:
        """获取系统统计信息"""
        return {
            "cpu_percent": psutil.cpu_percent(),
            "memory_percent": psutil.virtual_memory().percent,
            "disk_percent": psutil.disk_usage('/').percent,
        }


# 全局性能监控器实例
performance_monitor = PerformanceMonitor()


def monitor_performance(func_name: str = None):
    """性能监控装饰器"""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            name = func_name or func.__name__
            performance_monitor.start_timer(name)
            try:
                result = await func(*args, **kwargs)
                return result
            finally:
                performance_monitor.end_timer(name)
        
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            name = func_name or func.__name__
            performance_monitor.start_timer(name)
            try:
                result = func(*args, **kwargs)
                return result
            finally:
                performance_monitor.end_timer(name)
        
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator


class LRUCache:
    """LRU缓存实现"""
    
    def __init__(self, max_size: int = 100):
        self.max_size = max_size
        self.cache: OrderedDict = OrderedDict()
    
    def get(self, key: str) -> Optional[Any]:
        """获取缓存值"""
        if key in self.cache:
            # 移动到末尾（最近使用）
            self.cache.move_to_end(key)
            return self.cache[key]
        return None
    
    def set(self, key: str, value: Any):
        """设置缓存值"""
        if key in self.cache:
            # 如果已存在，移动到末尾
            self.cache.move_to_end(key)
        else:
            # 如果缓存已满，删除最旧的项
            if len(self.cache) >= self.max_size:
                self.cache.popitem(last=False)
        
        self.cache[key] = value
    
    def clear(self):
        """清空缓存"""
        self.cache.clear()
    
    def size(self) -> int:
        """获取缓存大小"""
        return len(self.cache)


# 全局缓存实例
api_cache = LRUCache(max_size=200)
status_cache = LRUCache(max_size=50)


def cache_result(cache_instance: LRUCache, ttl: int = 300):
    """缓存结果装饰器"""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            # 生成缓存键
            cache_key = f"{func.__name__}:{hash(str(args) + str(sorted(kwargs.items())))}"
            
            # 尝试从缓存获取
            cached_result = cache_instance.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            # 执行函数并缓存结果
            result = await func(*args, **kwargs)
            cache_instance.set(cache_key, result)
            return result
        
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            # 生成缓存键
            cache_key = f"{func.__name__}:{hash(str(args) + str(sorted(kwargs.items())))}"
            
            # 尝试从缓存获取
            cached_result = cache_instance.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            # 执行函数并缓存结果
            result = func(*args, **kwargs)
            cache_instance.set(cache_key, result)
            return result
        
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator


class ConnectionPool:
    """连接池管理器"""
    
    def __init__(self, max_connections: int = 10):
        self.max_connections = max_connections
        self.active_connections = 0
        self._lock = asyncio.Lock()
    
    async def acquire(self):
        """获取连接"""
        async with self._lock:
            while self.active_connections >= self.max_connections:
                await asyncio.sleep(0.1)
            self.active_connections += 1
    
    async def release(self):
        """释放连接"""
        async with self._lock:
            if self.active_connections > 0:
                self.active_connections -= 1
    
    async def __aenter__(self):
        await self.acquire()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.release()


# 全局连接池实例
connection_pool = ConnectionPool()


def get_performance_stats() -> Dict[str, Any]:
    """获取性能统计信息"""
    return {
        "system": performance_monitor.get_system_stats(),
        "cache_sizes": {
            "api_cache": api_cache.size(),
            "status_cache": status_cache.size(),
        },
        "active_connections": connection_pool.active_connections,
        "metrics": {
            name: {
                "count": len(times),
                "avg_time": sum(times) / len(times) if times else 0,
                "min_time": min(times) if times else 0,
                "max_time": max(times) if times else 0,
            }
            for name, times in performance_monitor.metrics.items()
        }
    }