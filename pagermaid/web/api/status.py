import asyncio
from typing import Union

from fastapi import APIRouter
from fastapi.responses import JSONResponse, StreamingResponse

from pagermaid.common.status import get_status
from pagermaid.common.system import run_eval
from pagermaid.utils import execute
from pagermaid.utils.performance import monitor_performance, cache_result, status_cache, get_performance_stats
from pagermaid.web.api.utils import authentication

route = APIRouter()


@route.get("/log", dependencies=[authentication()])
@monitor_performance("get_log")
async def get_log(num: Union[int, str] = 100):
    try:
        num = int(num)
    except ValueError:
        num = 100

    async def streaming_logs():
        try:
            with open("data/pagermaid.log.txt", "r", encoding="utf-8") as f:
                lines = f.readlines()[-num:]
                # 批量发送日志，减少延迟
                batch_size = 10
                for i in range(0, len(lines), batch_size):
                    batch = lines[i:i + batch_size]
                    yield "".join(batch)
                    # 减少延迟时间
                    await asyncio.sleep(0.01)
        except FileNotFoundError:
            yield "日志文件不存在\n"
        except Exception as e:
            yield f"读取日志失败: {str(e)}\n"

    return StreamingResponse(streaming_logs())


@route.get("/run_eval", dependencies=[authentication()])
@monitor_performance("run_eval")
async def run_cmd(cmd: str = ""):
    async def run_cmd_func():
        try:
            result = (await run_eval(cmd)).split("\n")
            # 批量发送结果
            batch_size = 5
            for i in range(0, len(result), batch_size):
                batch = result[i:i + batch_size]
                yield "\n".join(batch) + "\n"
                await asyncio.sleep(0.01)
        except Exception as e:
            yield f"执行失败: {str(e)}\n"

    return StreamingResponse(run_cmd_func()) if cmd else "无效命令"


@route.get("/run_sh", dependencies=[authentication()])
@monitor_performance("run_sh")
async def run_sh(cmd: str = ""):
    async def run_sh_func():
        try:
            result = (await execute(cmd)).split("\n")
            # 批量发送结果
            batch_size = 5
            for i in range(0, len(result), batch_size):
                batch = result[i:i + batch_size]
                yield "\n".join(batch) + "\n"
                await asyncio.sleep(0.01)
        except Exception as e:
            yield f"执行失败: {str(e)}\n"

    return StreamingResponse(run_sh_func()) if cmd else "无效命令"


@route.get("/status", response_class=JSONResponse, dependencies=[authentication()])
@monitor_performance("get_status")
@cache_result(status_cache, ttl=30)  # 缓存30秒
async def status():
    return (await get_status()).dict()


@route.get("/performance", response_class=JSONResponse, dependencies=[authentication()])
async def performance_stats():
    """获取性能统计信息"""
    return get_performance_stats()
