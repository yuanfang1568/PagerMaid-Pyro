"""
性能优化配置
"""

# 缓存配置
CACHE_CONFIG = {
    "api_cache_size": 200,
    "status_cache_size": 50,
    "status_cache_ttl": 30,  # 秒
    "log_cache_size": 100,
    "log_cache_ttl": 60,  # 秒
}

# 流式响应配置
STREAMING_CONFIG = {
    "log_batch_size": 10,
    "command_batch_size": 5,
    "streaming_delay": 0.01,  # 秒
    "max_streaming_time": 300,  # 秒
}

# 连接池配置
CONNECTION_POOL_CONFIG = {
    "max_connections": 10,
    "connection_timeout": 30,  # 秒
    "idle_timeout": 60,  # 秒
}

# 性能监控配置
MONITORING_CONFIG = {
    "enable_performance_monitoring": True,
    "enable_system_monitoring": True,
    "metrics_retention_days": 7,
    "log_slow_queries": True,
    "slow_query_threshold": 1.0,  # 秒
}

# Web服务器配置
WEB_SERVER_CONFIG = {
    "workers": 1,  # uvicorn workers
    "max_requests": 1000,
    "max_requests_jitter": 100,
    "keepalive_timeout": 5,
    "limit_concurrency": 100,
    "limit_max_requests": 1000,
}

# 数据库配置（如果使用）
DATABASE_CONFIG = {
    "pool_size": 10,
    "max_overflow": 20,
    "pool_timeout": 30,
    "pool_recycle": 3600,
}

# 日志配置
LOGGING_CONFIG = {
    "log_level": "INFO",
    "log_format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "log_file": "data/pagermaid.log.txt",
    "max_log_size": 10 * 1024 * 1024,  # 10MB
    "backup_count": 5,
}

# 内存优化配置
MEMORY_CONFIG = {
    "enable_garbage_collection": True,
    "gc_threshold": 100,  # 每100次操作触发一次GC
    "max_memory_usage": 512 * 1024 * 1024,  # 512MB
}

# 异步配置
ASYNC_CONFIG = {
    "max_concurrent_tasks": 50,
    "task_timeout": 30,  # 秒
    "enable_task_cancellation": True,
}

# 压缩配置
COMPRESSION_CONFIG = {
    "enable_gzip": True,
    "min_size": 1024,  # 1KB
    "compression_level": 6,
}

# 缓存预热配置
CACHE_WARMUP_CONFIG = {
    "enable_cache_warmup": True,
    "warmup_interval": 300,  # 5分钟
    "warmup_endpoints": [
        "/pagermaid/api/status",
        "/pagermaid/api/bot_info",
    ],
}

# 性能优化开关
PERFORMANCE_FEATURES = {
    "enable_response_compression": True,
    "enable_request_caching": True,
    "enable_connection_pooling": True,
    "enable_async_processing": True,
    "enable_batch_processing": True,
    "enable_lazy_loading": True,
}