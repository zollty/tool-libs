import os
import time
import psutil
import random
import string
from pathlib import Path
from collections import defaultdict
from dataclasses import dataclass
from typing import List, Tuple, Optional, Callable
import argparse
import sys


@dataclass
class FileInfo:
    path: str
    name: str
    size: int


class FileSystemScanner:
    """文件系统扫描器，用于创建测试环境"""

    @staticmethod
    def create_test_files(root_dir: str, num_files: int = 10000, target_file: str = "target.txt",
                          target_size: int = 1024):
        """创建测试文件"""
        root = Path(root_dir)
        root.mkdir(parents=True, exist_ok=True)

        # 创建不同大小的随机文件
        size_distribution = [
            (100, 1000, 0.7),  # 小文件: 70%
            (1000, 10000, 0.2),  # 中文件: 20%
            (10000, 100000, 0.08),  # 大文件: 8%
            (100000, 1000000, 0.02)  # 特大文件: 2%
        ]

        print(f"在 {root_dir} 中创建 {num_files} 个测试文件...")

        created_files = []
        for i in range(num_files):
            # 随机选择文件大小范围
            rand = random.random()
            cumulative = 0
            for min_sz, max_sz, prob in size_distribution:
                cumulative += prob
                if rand <= cumulative:
                    file_size = random.randint(min_sz, max_sz)
                    break
            else:
                file_size = random.randint(100, 1000)

            # 生成随机文件名
            if i == 0:  # 第一个文件作为目标文件
                filename = target_file
                file_size = target_size
            else:
                name_len = random.randint(5, 20)
                filename = f"{''.join(random.choices(string.ascii_letters + string.digits, k=name_len))}.txt"

            filepath = root / filename

            # 创建文件
            with open(filepath, 'wb') as f:
                f.write(os.urandom(file_size))

            if filename == target_file:
                print(f"目标文件: {filepath}, 大小: {file_size} 字节")

            created_files.append(FileInfo(str(filepath), filename, file_size))

        print(f"创建完成! 总文件数: {len(created_files)}")
        return created_files

    @staticmethod
    def get_file_size_distribution(files: List[FileInfo]):
        """分析文件大小分布"""
        sizes = [f.size for f in files]
        return {
            'min': min(sizes),
            'max': max(sizes),
            'avg': sum(sizes) / len(sizes),
            'median': sorted(sizes)[len(sizes) // 2]
        }


class FileSearchStrategies:
    """文件搜索策略对比"""

    @staticmethod
    def strategy_name_only(root_dir: str, target_name: str, stop_first: bool = True) -> List[str]:
        """策略1: 仅通过名称匹配"""
        results = []

        for root, dirs, files in os.walk(root_dir):
            if stop_first and results:
                break

            for file in files:
                if file == target_name:
                    full_path = os.path.join(root, file)
                    results.append(full_path)
                    if stop_first:
                        return results

        return results

    @staticmethod
    def strategy_name_only_optimized(root_dir: str, target_name: str, stop_first: bool = True) -> List[str]:
        """策略1优化版: 使用scandir()"""
        results = []

        def scan_directory(dir_path):
            nonlocal results
            if stop_first and results:
                return

            try:
                with os.scandir(dir_path) as entries:
                    for entry in entries:
                        if stop_first and results:
                            return

                        if entry.is_file():
                            if entry.name == target_name:
                                results.append(entry.path)
                                if stop_first:
                                    return
                        elif entry.is_dir():
                            scan_directory(entry.path)
            except PermissionError:
                pass

        scan_directory(root_dir)
        return results

    @staticmethod
    def strategy_size_then_name(root_dir: str, target_name: str,
                                min_size: int, max_size: int, stop_first: bool = True) -> List[str]:
        """策略2: 先用大小筛选，再用名称匹配"""
        results = []

        for root, dirs, files in os.walk(root_dir):
            if stop_first and results:
                break

            for file in files:
                if stop_first and results:
                    break

                full_path = os.path.join(root, file)

                try:
                    # 先检查文件大小
                    file_size = os.path.getsize(full_path)

                    if min_size <= file_size <= max_size:
                        # 大小符合范围，再检查文件名
                        if file == target_name:
                            results.append(full_path)
                            if stop_first:
                                return results
                except (OSError, PermissionError):
                    continue

        return results

    @staticmethod
    def strategy_size_then_name_optimized(root_dir: str, target_name: str,
                                          min_size: int, max_size: int, stop_first: bool = True) -> List[str]:
        """策略2优化版: 使用scandir()并批量获取文件信息"""
        results = []

        def scan_directory(dir_path):
            nonlocal results
            if stop_first and results:
                return

            try:
                with os.scandir(dir_path) as entries:
                    for entry in entries:
                        if stop_first and results:
                            return

                        if entry.is_file():
                            try:
                                # 获取文件大小（某些系统可能需要stat()调用）
                                file_size = entry.stat().st_size

                                if min_size <= file_size <= max_size:
                                    if entry.name == target_name:
                                        results.append(entry.path)
                                        if stop_first:
                                            return
                            except (OSError, PermissionError):
                                continue
                        elif entry.is_dir():
                            scan_directory(entry.path)
            except PermissionError:
                pass

        scan_directory(root_dir)
        return results

    @staticmethod
    def strategy_hybrid(root_dir: str, target_name: str,
                        min_size: int, max_size: int, stop_first: bool = True) -> List[str]:
        """混合策略: 根据大小范围宽度决定先检查什么"""

        # 计算大小范围相对于平均文件大小的宽度
        # 这里假设我们知道平均文件大小（实际中可以采样估计）
        avg_file_size = 5000  # 假设的平均文件大小

        size_range_width = (max_size - min_size) / avg_file_size

        # 如果大小范围很窄（小于平均文件大小的20%），先检查大小
        if size_range_width < 0.2:
            return FileSearchStrategies.strategy_size_then_name_optimized(
                root_dir, target_name, min_size, max_size, stop_first)
        else:
            # 否则先检查名称
            return FileSearchStrategies.strategy_name_only_optimized(
                root_dir, target_name, stop_first)


class PerformanceTester:
    """性能测试器"""

    @staticmethod
    def clear_cache():
        """尝试清除文件系统缓存（Linux/Mac有效）"""
        if sys.platform == 'linux':
            os.system('sync && echo 3 | sudo tee /proc/sys/vm/drop_caches')
        elif sys.platform == 'darwin':
            os.system('purge')
        # Windows没有简单的清除缓存方法

    @staticmethod
    def measure_search_time(search_func: Callable, *args, **kwargs) -> Tuple[List[str], float]:
        """测量搜索函数执行时间"""
        start_time = time.perf_counter()
        results = search_func(*args, **kwargs)
        end_time = time.perf_counter()

        return results, end_time - start_time

    @staticmethod
    def run_comparison(root_dir: str, target_name: str,
                       min_size: int, max_size: int, num_runs: int = 5):
        """运行对比测试"""
        strategies = [
            ("仅名称匹配 (os.walk)",
             lambda: FileSearchStrategies.strategy_name_only(root_dir, target_name)),

            ("仅名称匹配 (scandir优化)",
             lambda: FileSearchStrategies.strategy_name_only_optimized(root_dir, target_name)),

            ("大小筛选+名称匹配 (os.walk)",
             lambda: FileSearchStrategies.strategy_size_then_name(
                 root_dir, target_name, min_size, max_size)),

            ("大小筛选+名称匹配 (scandir优化)",
             lambda: FileSearchStrategies.strategy_size_then_name_optimized(
                 root_dir, target_name, min_size, max_size)),

            ("混合策略",
             lambda: FileSearchStrategies.strategy_hybrid(
                 root_dir, target_name, min_size, max_size)),
        ]

        print(f"\n{'=' * 80}")
        print(f"性能对比测试")
        print(f"目标文件: {target_name}")
        print(f"大小范围: {min_size} - {max_size} 字节")
        print(f"测试目录: {root_dir}")
        print(f"每个策略运行 {num_runs} 次")
        print(f"{'=' * 80}\n")

        results = {}

        for strategy_name, search_func in strategies:
            times = []
            found_files = []

            print(f"测试策略: {strategy_name}")

            for i in range(num_runs):
                # 每次运行前尝试清除缓存（需要管理员权限）
                # PerformanceTester.clear_cache()

                files, elapsed = PerformanceTester.measure_search_time(search_func)
                times.append(elapsed)
                found_files = files

                print(f"  第 {i + 1} 次: {elapsed:.4f} 秒, 找到 {len(files)} 个文件")

            avg_time = sum(times) / len(times)
            min_time = min(times)
            max_time = max(times)

            results[strategy_name] = {
                'avg_time': avg_time,
                'min_time': min_time,
                'max_time': max_time,
                'found_files': found_files,
                'all_times': times
            }

            print(f"  平均时间: {avg_time:.4f} 秒, 最短: {min_time:.4f} 秒, 最长: {max_time:.4f} 秒")

            if found_files:
                print(f"  找到的文件: {', '.join(found_files[:3])}")
                if len(found_files) > 3:
                    print(f"  ... 以及另外 {len(found_files) - 3} 个文件")
            else:
                print(f"  未找到文件")

            print()

        # 显示对比结果
        print(f"{'=' * 80}")
        print("性能对比总结:")
        print(f"{'策略':<30} {'平均时间(秒)':<15} {'速度提升':<15}")

        # 以最优策略为基准
        best_strategy = min(results.items(), key=lambda x: x[1]['avg_time'])
        best_time = best_strategy[1]['avg_time']

        for strategy_name, data in results.items():
            avg_time = data['avg_time']
            speedup = best_time / avg_time if avg_time > 0 else 0

            if strategy_name == best_strategy[0]:
                print(f"{strategy_name:<30} {avg_time:<15.4f} {'(基准)':<15}")
            else:
                relative_speed = best_time / avg_time
                print(f"{strategy_name:<30} {avg_time:<15.4f} {relative_speed:<15.2f}x")

        print(f"{'=' * 80}")

        return results


def main():
    parser = argparse.ArgumentParser(description="文件搜索策略性能对比")
    parser.add_argument("--root-dir", default="./test_files", help="测试目录路径")
    parser.add_argument("--num-files", type=int, default=10000, help="测试文件数量")
    parser.add_argument("--target-file", default="target.txt", help="目标文件名")
    parser.add_argument("--target-size", type=int, default=1024, help="目标文件大小")
    parser.add_argument("--size-range", type=float, default=0.1,
                        help="大小范围宽度（相对于目标大小的比例）")
    parser.add_argument("--num-runs", type=int, default=3, help="每个策略运行次数")
    parser.add_argument("--skip-create", action="store_true", help="跳过创建测试文件")

    args = parser.parse_args()

    # 创建测试文件
    if not args.skip_create:
        files = FileSystemScanner.create_test_files(
            args.root_dir, args.num_files, args.target_file, args.target_size
        )

    # 计算大小范围
    target_size = args.target_size
    size_range = target_size * args.size_range
    min_size = int(target_size - size_range / 2)
    max_size = int(target_size + size_range / 2)

    if min_size < 0:
        min_size = 0

    print(f"\n目标文件大小范围: {min_size} - {max_size} 字节")
    print(f"大小范围宽度: {size_range} 字节 (目标大小的 {args.size_range * 100:.1f}%)")

    # 运行性能对比
    results = PerformanceTester.run_comparison(
        args.root_dir, args.target_file, min_size, max_size, args.num_runs
    )

    # 分析哪种策略更快
    print("\n结论分析:")

    name_only_avg = results["仅名称匹配 (scandir优化)"]['avg_time']
    size_then_name_avg = results["大小筛选+名称匹配 (scandir优化)"]['avg_time']

    if name_only_avg < size_then_name_avg:
        faster_strategy = "仅名称匹配"
        speedup = name_only_avg / size_then_name_avg
    else:
        faster_strategy = "先大小筛选再名称匹配"
        speedup = size_then_name_avg / name_only_avg

    print(f"1. 更快的策略: {faster_strategy}")
    print(f"2. 速度优势: {speedup:.2f}x")

    # 建议
    print(f"\n建议:")
    if args.size_range < 0.2:
        print(f"- 由于大小范围较窄 ({args.size_range * 100:.1f}%)，先按大小筛选可能更有效")
    else:
        print(f"- 由于大小范围较宽 ({args.size_range * 100:.1f}%)，仅按名称匹配可能更直接")

    print(f"- 实际速度受文件系统缓存、磁盘类型(HDD/SSD)、文件数量等因素影响")
    print(f"- 对于大量文件，scandir()优化版本比os.walk()更快")


if __name__ == "__main__":
    main()