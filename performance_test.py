#!/usr/bin/env python3
"""
性能测试脚本
用于验证 PagerMaid-Pyro 的性能优化效果
"""

import asyncio
import time
import aiohttp
import statistics
from typing import List, Dict
import json


class PerformanceTester:
    def __init__(self, base_url: str = "http://localhost:8080"):
        self.base_url = base_url
        self.results = {}
    
    async def test_api_endpoint(self, endpoint: str, method: str = "GET", 
                               params: Dict = None, data: Dict = None) -> Dict:
        """测试单个API端点"""
        url = f"{self.base_url}{endpoint}"
        times = []
        
        async with aiohttp.ClientSession() as session:
            for i in range(10):  # 测试10次
                start_time = time.time()
                try:
                    if method == "GET":
                        async with session.get(url, params=params) as response:
                            await response.text()
                    elif method == "POST":
                        async with session.post(url, json=data) as response:
                            await response.text()
                    
                    end_time = time.time()
                    times.append(end_time - start_time)
                    
                except Exception as e:
                    print(f"Error testing {endpoint}: {e}")
                    times.append(float('inf'))
                
                await asyncio.sleep(0.1)  # 避免过于频繁的请求
        
        return {
            "endpoint": endpoint,
            "method": method,
            "times": times,
            "avg_time": statistics.mean(times) if times else 0,
            "min_time": min(times) if times else 0,
            "max_time": max(times) if times else 0,
            "median_time": statistics.median(times) if times else 0,
            "success_rate": len([t for t in times if t != float('inf')]) / len(times) * 100
        }
    
    async def test_status_endpoint(self) -> Dict:
        """测试状态端点"""
        return await self.test_api_endpoint("/pagermaid/api/status")
    
    async def test_log_endpoint(self) -> Dict:
        """测试日志端点"""
        return await self.test_api_endpoint("/pagermaid/api/log", params={"num": "100"})
    
    async def test_performance_endpoint(self) -> Dict:
        """测试性能端点"""
        return await self.test_api_endpoint("/pagermaid/api/performance")
    
    async def test_command_endpoint(self) -> Dict:
        """测试命令执行端点"""
        return await self.test_api_endpoint("/pagermaid/api/run_sh", params={"cmd": "echo 'test'"})
    
    async def run_all_tests(self) -> Dict:
        """运行所有测试"""
        print("开始性能测试...")
        
        tests = [
            ("状态端点", self.test_status_endpoint),
            ("日志端点", self.test_log_endpoint),
            ("性能端点", self.test_performance_endpoint),
            ("命令端点", self.test_command_endpoint),
        ]
        
        results = {}
        for test_name, test_func in tests:
            print(f"测试 {test_name}...")
            result = await test_func()
            results[test_name] = result
            print(f"  {test_name} 平均响应时间: {result['avg_time']:.3f}s")
        
        return results
    
    def generate_report(self, results: Dict) -> str:
        """生成测试报告"""
        report = []
        report.append("# PagerMaid-Pyro 性能测试报告")
        report.append("")
        report.append(f"测试时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"测试URL: {self.base_url}")
        report.append("")
        
        # 总体统计
        all_times = []
        for test_name, result in results.items():
            all_times.extend([t for t in result['times'] if t != float('inf')])
        
        if all_times:
            report.append("## 总体性能统计")
            report.append(f"- 总请求数: {len(all_times)}")
            report.append(f"- 平均响应时间: {statistics.mean(all_times):.3f}s")
            report.append(f"- 最小响应时间: {min(all_times):.3f}s")
            report.append(f"- 最大响应时间: {max(all_times):.3f}s")
            report.append(f"- 中位数响应时间: {statistics.median(all_times):.3f}s")
            report.append("")
        
        # 详细结果
        report.append("## 详细测试结果")
        report.append("")
        
        for test_name, result in results.items():
            report.append(f"### {test_name}")
            report.append(f"- 端点: {result['endpoint']}")
            report.append(f"- 方法: {result['method']}")
            report.append(f"- 平均响应时间: {result['avg_time']:.3f}s")
            report.append(f"- 最小响应时间: {result['min_time']:.3f}s")
            report.append(f"- 最大响应时间: {result['max_time']:.3f}s")
            report.append(f"- 中位数响应时间: {result['median_time']:.3f}s")
            report.append(f"- 成功率: {result['success_rate']:.1f}%")
            report.append("")
        
        # 性能评估
        report.append("## 性能评估")
        report.append("")
        
        avg_times = [result['avg_time'] for result in results.values()]
        if avg_times:
            overall_avg = statistics.mean(avg_times)
            if overall_avg < 0.1:
                report.append("✅ **优秀** - 平均响应时间小于100ms")
            elif overall_avg < 0.5:
                report.append("✅ **良好** - 平均响应时间小于500ms")
            elif overall_avg < 1.0:
                report.append("⚠️ **一般** - 平均响应时间小于1s")
            else:
                report.append("❌ **需要优化** - 平均响应时间超过1s")
        
        return "\n".join(report)


async def main():
    """主函数"""
    print("PagerMaid-Pyro 性能测试工具")
    print("=" * 50)
    
    # 配置测试参数
    base_url = input("请输入测试URL (默认: http://localhost:8080): ").strip()
    if not base_url:
        base_url = "http://localhost:8080"
    
    tester = PerformanceTester(base_url)
    
    try:
        # 运行测试
        results = await tester.run_all_tests()
        
        # 生成报告
        report = tester.generate_report(results)
        
        # 保存报告
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        filename = f"performance_test_report_{timestamp}.md"
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"\n测试完成！报告已保存到: {filename}")
        print("\n" + "=" * 50)
        print(report)
        
    except Exception as e:
        print(f"测试过程中出现错误: {e}")
        print("请确保 PagerMaid-Pyro 正在运行且可访问")


if __name__ == "__main__":
    asyncio.run(main())