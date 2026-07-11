import math
import sys
from typing import List, Dict, Any, Optional


def split_array_evenly(arr: List[Dict[str, Any]], k: int) -> List[List[Dict[str, Any]]]:
    """将数组均匀分割成多个子数组，每个子数组长度不超过k"""
    if not arr:
        return []

    # 第一步：基础贪心分组
    initial_groups = greedy_split(arr, k)

    # 第二步：根据分组数量进行优化
    if len(initial_groups) == 1:
        # 只有一个分组，无需优化
        return initial_groups
    elif len(initial_groups) <= 5:
        # 分组数少，直接对整个数组使用优化算法
        return find_optimal_split(arr, len(initial_groups), k)
    else:
        # 分组数多，只优化最后3组，使用动态规划
        return rebalance_last_three_with_dp(initial_groups, arr, k)


def find_optimal_split(arr: List[Dict[str, Any]], group_count: int, k: int) -> List[List[Dict[str, Any]]]:
    """通用的最优划分算法，支持任意分组数"""
    n = len(arr)

    # 如果分组数大于元素数，无法划分
    if group_count > n:
        return greedy_split(arr, k)

    # 如果分组数等于1，直接返回整个数组
    if group_count == 1:
        return [arr]

    # 预计算前缀和
    prefix_sum = [0]
    for i in range(n):
        prefix_sum.append(prefix_sum[i] + arr[i]['length'])

    best_split = None
    best_std_dev = float('inf')

    def backtrack(start: int, groups: List[List[Dict[str, Any]]], splits: List[int]):
        nonlocal best_split, best_std_dev

        # 如果已经找到足够的组
        if len(groups) == group_count:
            # 检查是否所有元素都已分配
            if start == n:
                # 计算标准差
                lengths = [sum(obj['length'] for obj in group) for group in groups]
                std_dev = calculate_std_dev_2(lengths)

                # 检查是否所有组都不超过k
                all_valid = all(length <= k for length in lengths)

                if all_valid and std_dev < best_std_dev:
                    best_std_dev = std_dev
                    best_split = [group.copy() for group in groups]
            return

        # 如果是最后一组，直接分配剩余所有元素
        if len(groups) == group_count - 1:
            last_group = arr[start:]
            last_group_length = prefix_sum[n] - prefix_sum[start]

            if last_group_length <= k:
                backtrack(n, groups + [last_group], splits + [n])
            return

        # 尝试不同的结束位置
        for end in range(start + 1, n - (group_count - len(groups) - 1) + 1):
            current_group = arr[start:end]
            current_length = prefix_sum[end] - prefix_sum[start]

            # 如果当前组长度超过k，停止尝试
            if current_length > k:
                break

            # 递归尝试
            backtrack(end, groups + [current_group], splits + [end])

    backtrack(0, [], [])

    # 如果没有找到满足条件的划分，使用贪心算法
    if not best_split:
        return greedy_split(arr, k)

    return best_split


def calculate_std_dev_2(lengths: List[float]) -> float:
    """计算标准差"""
    if len(lengths) <= 1:
        return 0

    mean = sum(lengths) / len(lengths)
    variance = sum((length - mean) ** 2 for length in lengths) / len(lengths)
    return math.sqrt(variance)


def find_optimal_three_split(arr: List[Dict[str, Any]], k: int) -> List[List[Dict[str, Any]]]:
    """找到最优的三分组划分"""
    n = len(arr)
    if n < 3:
        return greedy_split(arr, k)

    # 预计算前缀和
    prefix_sum = [0]
    for i in range(n):
        prefix_sum.append(prefix_sum[i] + arr[i]['length'])

    best_split = None
    best_std_dev = float('inf')

    # 枚举所有可能的两个分割点
    for i in range(1, n - 1):
        for j in range(i + 1, n):
            group1 = arr[:i]
            group2 = arr[i:j]
            group3 = arr[j:]

            # 计算每组长度
            len1 = prefix_sum[i] - prefix_sum[0]
            len2 = prefix_sum[j] - prefix_sum[i]
            len3 = prefix_sum[n] - prefix_sum[j]

            # 检查是否超过限制
            if len1 <= k and len2 <= k and len3 <= k:
                std_dev = calculate_std_dev_for_three(len1, len2, len3)

                if std_dev < best_std_dev:
                    best_std_dev = std_dev
                    best_split = [group1, group2, group3]

    # 如果没有找到满足条件的划分，使用贪心算法
    if not best_split:
        return greedy_split(arr, k)

    return best_split


def greedy_split(arr: List[Dict[str, Any]], k: int) -> List[List[Dict[str, Any]]]:
    """贪心算法分割数组"""
    result = []
    current_group = []
    current_length = 0

    for obj in arr:
        if current_length + obj['length'] <= k:
            current_group.append(obj)
            current_length += obj['length']
        else:
            if current_group:
                result.append(current_group)
            current_group = [obj]
            current_length = obj['length']

    if current_group:
        result.append(current_group)

    return result


def rebalance_last_three_with_dp(initial_groups: List[List[Dict[str, Any]]],
                                 arr: List[Dict[str, Any]],
                                 k: int) -> List[List[Dict[str, Any]]]:
    """使用动态规划重新平衡最后三组"""
    if len(initial_groups) <= 3:
        return initial_groups

    # 确定最后3组在原始数组中的起始位置
    elements_before_last_three = sum(len(group) for group in initial_groups[:-3])
    last_three_segment = arr[elements_before_last_three:]

    # 使用动态规划找到最优的3组划分
    optimal_split = find_optimal_three_split(last_three_segment, k)

    # 组合结果
    return initial_groups[:-3] + optimal_split


def calculate_std_dev_for_three(len1: float, len2: float, len3: float) -> float:
    """计算三个数的标准差"""
    mean = (len1 + len2 + len3) / 3
    variance = ((len1 - mean) ** 2 + (len2 - mean) ** 2 + (len3 - mean) ** 2) / 3
    return math.sqrt(variance)


def validate_split(result: List[List[Dict[str, Any]]], k: int) -> bool:
    """验证拆分是否合理"""
    is_valid = True
    stats = {
        'chunks': len(result),
        'lengths': [],
        'differences': []
    }

    for i, chunk in enumerate(result):
        length = sum(obj['length'] for obj in chunk)
        stats['lengths'].append(length)

        if length > k:
            print(f"错误: 子数组 {i + 1} 长度 {length} 超过限制 {k}")
            is_valid = False

        if i > 0:
            diff = abs(length - stats['lengths'][i - 1])
            stats['differences'].append(diff)

    if is_valid:
        avg_diff = sum(stats['differences']) / len(stats['differences']) if stats['differences'] else 0
        print(f"验证通过! 平均长度差异: {avg_diff:.2f}")

    return is_valid


def validate_result(result: List[List[Dict[str, Any]]], k: int,
                    expected: Optional[List[List[Dict[str, Any]]]] = None) -> bool:
    """验证结果"""
    # 检查是否超过限制
    for chunk in result:
        total_length = sum(obj['length'] for obj in chunk)
        if total_length > k:
            print(f"错误: 子数组长度 {total_length} 超过限制 {k}")
            return False

    # 如果expected为None，表示接受任何有效拆分
    if expected is None:
        return True

    # 检查与期望结果的一致性
    if expected and len(expected) > 0:
        # 检查分组数量
        if len(result) != len(expected):
            print(f"分组数量不匹配: 期望 {len(expected)} 组，实际 {len(result)} 组")
            return False

        # 检查每个分组的内容
        for i in range(len(result)):
            actual_lengths = ','.join(str(obj['length']) for obj in result[i])
            expected_lengths = ','.join(str(obj['length']) for obj in expected[i])

            if actual_lengths != expected_lengths:
                print(f"子数组 {i + 1} 不匹配")
                print(f"  期望: [{expected_lengths}]")
                print(f"  实际: [{actual_lengths}]")
                return False

    return True


def run_uniformity_tests():
    """运行均匀性测试"""
    print("开始均匀性测试...\n")

    # 测试用例
    # 测试用例集合
    uniformity_test_cases = [
        # 测试用例1
        {
            "name": "测试用例1",
            "data": [
                {"id": 1, "length": 10},
                {"id": 2, "length": 1},
                {"id": 3, "length": 1},
                {"id": 4, "length": 10},
                {"id": 5, "length": 1},
                {"id": 6, "length": 1},
                {"id": 7, "length": 10}
            ],
            "k": 12,
            "expected": [
                [{"id": 1, "length": 10}, {"id": 2, "length": 1}],
                [{"id": 3, "length": 1}, {"id": 4, "length": 10}, {"id": 5, "length": 1}],
                [{"id": 6, "length": 1}, {"id": 7, "length": 10}]
            ],
            "expected2": [
                [{"id": 1, "length": 10}, {"id": 2, "length": 1}],
                [{"id": 3, "length": 1}, {"id": 4, "length": 10}],
                [{"id": 5, "length": 1}, {"id": 6, "length": 1}, {"id": 7, "length": 10}]
            ]
        },

        # 测试用例2
        {
            "name": "测试用例2",
            "data": [
                {"id": 1, "length": 9},
                {"id": 2, "length": 3},
                {"id": 3, "length": 3},
                {"id": 4, "length": 3},
                {"id": 5, "length": 9},
                {"id": 6, "length": 3},
                {"id": 7, "length": 3},
                {"id": 8, "length": 3}
            ],
            "k": 12,
            "expected": [
                [{"id": 1, "length": 9}],
                [{"id": 2, "length": 3}, {"id": 3, "length": 3}, {"id": 4, "length": 3}],
                [{"id": 5, "length": 9}],
                [{"id": 6, "length": 3}, {"id": 7, "length": 3}, {"id": 8, "length": 3}]
            ]
        },

        # 测试用例3
        {
            "name": "测试用例3",
            "data": [
                {"id": 1, "length": 8},
                {"id": 2, "length": 2},
                {"id": 3, "length": 2},
                {"id": 4, "length": 4},
                {"id": 5, "length": 4},
                {"id": 6, "length": 8},
                {"id": 7, "length": 2},
                {"id": 8, "length": 2},
                {"id": 9, "length": 4},
                {"id": 10, "length": 4}
            ],
            "k": 12,
            "expected": [
                [{"id": 1, "length": 8}, {"id": 2, "length": 2}],
                [{"id": 3, "length": 2}, {"id": 4, "length": 4}, {"id": 5, "length": 4}],
                [{"id": 6, "length": 8}, {"id": 7, "length": 2}],
                [{"id": 8, "length": 2}, {"id": 9, "length": 4}, {"id": 10, "length": 4}]
            ]
        },

        # 测试用例4
        {
            "name": "测试用例4",
            "data": [
                {"id": 1, "length": 10},
                {"id": 2, "length": 5},
                {"id": 3, "length": 5},
                {"id": 4, "length": 10},
                {"id": 5, "length": 5},
                {"id": 6, "length": 5},
                {"id": 7, "length": 10},
                {"id": 8, "length": 5}
            ],
            "k": 20,
            # 两种方式均匀性相同，接受任意一种
            "expected": [
                [{"id": 1, "length": 10}, {"id": 2, "length": 5}, {"id": 3, "length": 5}],
                [{"id": 4, "length": 10}, {"id": 5, "length": 5}, {"id": 6, "length": 5}],
                [{"id": 7, "length": 10}, {"id": 8, "length": 5}]
            ],
            "expected2": [
                [{"id": 1, "length": 10}, {"id": 2, "length": 5}],
                [{"id": 3, "length": 5}, {"id": 4, "length": 10}, {"id": 5, "length": 5}],
                [{"id": 6, "length": 5}, {"id": 7, "length": 10}, {"id": 8, "length": 5}]
            ]
        },
        {
            "name": "空数组",
            "data": [],
            "k": 10,
            "expected": []
        },

        # 测试用例2: 单个元素
        {
            "name": "单个元素",
            "data": [{"id": 1, "length": 5}],
            "k": 10,
            "expected": [[{"id": 1, "length": 5}]]
        },

        # 测试用例3: 所有元素长度相同
        {
            "name": "所有元素长度相同",
            "data": [
                {"id": 1, "length": 5},
                {"id": 2, "length": 5},
                {"id": 3, "length": 5},
                {"id": 4, "length": 5},
                {"id": 5, "length": 5}
            ],
            "k": 12,
            "expected": [
                [{"id": 1, "length": 5}, {"id": 2, "length": 5}],
                [{"id": 3, "length": 5}, {"id": 4, "length": 5}],
                [{"id": 5, "length": 5}]
            ]
        },

        # 测试用例4: 元素长度刚好等于k
        {
            "name": "元素长度刚好等于k",
            "data": [
                {"id": 1, "length": 10},
                {"id": 2, "length": 10},
                {"id": 3, "length": 10}
            ],
            "k": 10,
            "expected": [
                [{"id": 1, "length": 10}],
                [{"id": 2, "length": 10}],
                [{"id": 3, "length": 10}]
            ]
        },

        # 测试用例5: 需要精细平衡的情况
        {
            "name": "需要精细平衡",
            "data": [
                {"id": 1, "length": 8},
                {"id": 2, "length": 7},
                {"id": 3, "length": 6},
                {"id": 4, "length": 9}
            ],
            "k": 15,
            "expected": [
                [{"id": 1, "length": 8}, {"id": 2, "length": 7}],
                [{"id": 3, "length": 6}, {"id": 4, "length": 9}]
            ]
        },

        # 测试用例6: 大数小数交替
        {
            "name": "大数小数交替",
            "data": [
                {"id": 1, "length": 9},
                {"id": 2, "length": 1},
                {"id": 3, "length": 8},
                {"id": 4, "length": 2},
                {"id": 5, "length": 7},
                {"id": 6, "length": 3}
            ],
            "k": 10,
            "expected": [
                [{"id": 1, "length": 9}, {"id": 2, "length": 1}],
                [{"id": 3, "length": 8}, {"id": 4, "length": 2}],
                [{"id": 5, "length": 7}, {"id": 6, "length": 3}]
            ]
        },

        # 测试用例7: 所有元素总和远小于k
        {
            "name": "总和远小于k",
            "data": [
                {"id": 1, "length": 2},
                {"id": 2, "length": 3},
                {"id": 3, "length": 1}
            ],
            "k": 20,
            "expected": [
                [{"id": 1, "length": 2}, {"id": 2, "length": 3}, {"id": 3, "length": 1}]
            ]
        },

        # 测试用例8: 需要多个元素才能接近k
        {
            "name": "多个小元素组合",
            "data": [
                {"id": 1, "length": 1},
                {"id": 2, "length": 1},
                {"id": 3, "length": 1},
                {"id": 4, "length": 1},
                {"id": 5, "length": 1},
                {"id": 6, "length": 1},
                {"id": 7, "length": 1},
                {"id": 8, "length": 1},
                {"id": 9, "length": 1},
                {"id": 10, "length": 1}
            ],
            "k": 5,
            "expected": [
                [{"id": 1, "length": 1}, {"id": 2, "length": 1}, {"id": 3, "length": 1}, {"id": 4, "length": 1},
                 {"id": 5, "length": 1}],
                [{"id": 6, "length": 1}, {"id": 7, "length": 1}, {"id": 8, "length": 1}, {"id": 9, "length": 1},
                 {"id": 10, "length": 1}]
            ]
        },

        # 测试用例9: 极不均匀的分布
        {
            "name": "极不均匀分布",
            "data": [
                {"id": 1, "length": 1},
                {"id": 2, "length": 19},
                {"id": 3, "length": 1},
                {"id": 4, "length": 19},
                {"id": 5, "length": 1}
            ],
            "k": 20,
            "expected": [
                [{"id": 1, "length": 1}, {"id": 2, "length": 19}],
                [{"id": 3, "length": 1}, {"id": 4, "length": 19}],
                [{"id": 5, "length": 1}]
            ]
        },

        # 测试用例10: 边界情况 - 刚好达到但不超k
        {
            "name": "边界情况",
            "data": [
                {"id": 1, "length": 6},
                {"id": 2, "length": 7},
                {"id": 3, "length": 7},
                {"id": 4, "length": 6},
                {"id": 5, "length": 7}
            ],
            "k": 13,
            "expected": [
                [{"id": 1, "length": 6}, {"id": 2, "length": 7}],
                [{"id": 3, "length": 7}, {"id": 4, "length": 6}],
                [{"id": 5, "length": 7}]
            ]
        }
    ]

    passed = 0
    failed = 0

    for test_case in uniformity_test_cases:
        print(f"{test_case['name']}:")
        print(f"输入: [{','.join(str(obj['length']) for obj in test_case['data'])}], k={test_case['k']}")

        result = split_array_evenly(test_case['data'], test_case['k'])

        # 验证结果
        is_valid = validate_result(result, test_case['k'], test_case.get('expected'))

        if is_valid:
            print("✅ 测试通过")
            passed += 1
        else:
            print("❌ 测试失败")
            failed += 1
        if len(result) == 0:
            continue
        print("拆分结果:")
        for chunk_index, chunk in enumerate(result):
            total_length = sum(obj['length'] for obj in chunk)
            chunk_lengths = ','.join(str(obj['length']) for obj in chunk)
            print(f"  子数组 {chunk_index + 1}: 长度={total_length}, 对象={chunk_lengths}")

        # 计算均匀性指标
        lengths = [sum(obj['length'] for obj in chunk) for chunk in result]
        mean = sum(lengths) / len(lengths)
        variance = sum((length - mean) ** 2 for length in lengths) / len(lengths)
        std_dev = math.sqrt(variance)

        print(f"分组长度: [{','.join(str(length) for length in lengths)}]")
        print(f"标准差: {std_dev:.3f}")
        print("---\n")

    print(f"测试总结: 通过 {passed} / 失败 {failed} / 总计 {len(uniformity_test_cases)}")


def main():
    """主函数"""

    # 测试例子
    test_data1 = [
        {"id": 1, "length": 10},
        {"id": 2, "length": 5},
        {"id": 3, "length": 5},
        {"id": 4, "length": 10}
    ]

    k1 = 20

    print("测试例子: [10, 5, 5, 10], k=20")
    print("期望结果: [10,5] 和 [5,10]")

    result1 = split_array_evenly(test_data1, k1)
    print("均匀拆分算法结果:")
    for index, chunk in enumerate(result1):
        total_length = sum(obj['length'] for obj in chunk)
        chunk_lengths = ','.join(str(obj['length']) for obj in chunk)
        print(f"子数组 {index + 1}: 长度={total_length}, 对象={chunk_lengths}")

    # 更多测试用例
    print("\n=== 更多测试用例 ===")

    # 测试用例1: 均匀分布
    test_case1 = [
        {"id": 1, "length": 8},
        {"id": 2, "length": 7},
        {"id": 3, "length": 6},
        {"id": 4, "length": 9}
    ]
    print("\n测试用例1: [8,7,6,9], k=15")
    result_case1 = split_array_evenly(test_case1, 15)
    for index, chunk in enumerate(result_case1):
        total_length = sum(obj['length'] for obj in chunk)
        chunk_lengths = ','.join(str(obj['length']) for obj in chunk)
        print(f"子数组 {index + 1}: 长度={total_length}, 对象={chunk_lengths}")

    # 测试用例2: 需要更细致的拆分
    test_case2 = [
        {"id": 1, "length": 12},
        {"id": 2, "length": 8},
        {"id": 3, "length": 5},
        {"id": 4, "length": 7},
        {"id": 5, "length": 10}
    ]
    print("\n测试用例2: [12,8,5,7,10], k=20")
    result_case2 = split_array_evenly(test_case2, 20)
    for index, chunk in enumerate(result_case2):
        total_length = sum(obj['length'] for obj in chunk)
        chunk_lengths = ','.join(str(obj['length']) for obj in chunk)
        print(f"子数组 {index + 1}: 长度={total_length}, 对象={chunk_lengths}")

    # 验证所有结果
    print("\n=== 验证结果 ===")
    validate_split(result1, k1)
    validate_split(result_case1, 15)
    validate_split(result_case2, 20)

    # 运行均匀性测试
    print("\n=== 均匀性测试 ===")
    run_uniformity_tests()


if __name__ == "__main__":
    main()