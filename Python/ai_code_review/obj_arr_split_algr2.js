var global_counter = 0;

function splitArrayEvenly(arr, k) {
    if (arr.length === 0) return [];

    // 第一步：基础贪心分组
    const initialGroups = greedySplit(arr, k);

    // 第二步：根据分组数量进行优化
    if (initialGroups.length === 1) {
        // 只有一个分组，无需优化
        return initialGroups;
    } else if (initialGroups.length <= 5) {
        // 分组数少（2或3组），直接对整个数组使用优化算法
        return findOptimalSplit(arr, initialGroups.length, k);
    } else {
        // 分组数多，只优化最后3组，使用动态规划
        return rebalanceLastThreeWithDP(initialGroups, arr, k);
    }
}

// 通用的最优划分算法，支持任意分组数
function findOptimalSplit(arr, groupCount, k) {
    const n = arr.length;

    // 如果分组数大于元素数，无法划分
    if (groupCount > n) {
        return greedySplit(arr, k);
    }

    // 如果分组数等于1，直接返回整个数组
    if (groupCount === 1) {
        return [arr];
    }

    // 预计算前缀和
    const prefixSum = [0];
    for (let i = 0; i < n; i++) {
        prefixSum[i + 1] = prefixSum[i] + arr[i].length;
    }

    let bestSplit = null;
    let bestStdDev = Infinity;

    // 使用回溯法找到最优划分
    function backtrack(start, groups, splits) {
        // 如果已经找到足够的组
        if (groups.length === groupCount) {
            // 检查是否所有元素都已分配
            if (start === n) {
                // 计算标准差
                const lengths = groups.map(group =>
                    group.reduce((sum, obj) => sum + obj.length, 0)
                );
                const stdDev = calculateStdDev2(lengths);

                // 检查是否所有组都不超过k
                const allValid = lengths.every(length => length <= k);

                if (allValid && stdDev < bestStdDev) {
                    bestStdDev = stdDev;
                    bestSplit = groups.map(group => [...group]);
                }
            }
            return;
        }

        // 如果是最后一组，直接分配剩余所有元素
        if (groups.length === groupCount - 1) {
            global_counter++;
            const lastGroup = arr.slice(start);
            const lastGroupLength = prefixSum[n] - prefixSum[start];

            if (lastGroupLength <= k) {
                backtrack(n, [...groups, lastGroup], [...splits, n]);
            }
            return;
        }

        // 尝试不同的结束位置
        for (let end = start + 1; end <= n - (groupCount - groups.length - 1); end++) {
            global_counter++;
            const currentGroup = arr.slice(start, end);
            const currentLength = prefixSum[end] - prefixSum[start];

            // 如果当前组长度超过k，停止尝试
            if (currentLength > k) break;

            // 递归尝试
            backtrack(end, [...groups, currentGroup], [...splits, end]);
        }
    }

    backtrack(0, [], []);

    // 如果没有找到满足条件的划分，使用贪心算法
    if (!bestSplit) {
        return greedySplit(arr, k);
    }

    return bestSplit;
}


// 计算标准差
function calculateStdDev2(lengths) {
    if (lengths.length <= 1) return 0;

    const mean = lengths.reduce((a, b) => a + b, 0) / lengths.length;
    const variance = lengths.reduce((sum, length) =>
        sum + Math.pow(length - mean, 2), 0) / lengths.length;

    return Math.sqrt(variance);
}








function splitArrayEvenly2(arr, k) {
    if (arr.length === 0) return [];

    // 第一步：基础贪心分组
    const initialGroups = greedySplit(arr, k);

    // 第二步：根据分组数量进行优化
    if (initialGroups.length === 1) {
        // 只有一个分组，无需优化
        return initialGroups;
    } else if (initialGroups.length <= 3) {
        // 分组数少（2或3组），直接对整个数组使用优化算法
        return optimizeSmallGroups(arr, initialGroups.length, k);
    } else {
        // 分组数多，只优化最后3组，使用动态规划
        return rebalanceLastThreeWithDP(initialGroups, arr, k);
    }
}

function optimizeSmallGroups(arr, groupCount, k) {
    if (groupCount === 1) {
        return [arr];
    } else if (groupCount === 2) {
        return findOptimalTwoSplit(arr, k);
    } else if (groupCount === 3) {
        return findOptimalThreeSplit(arr, k);
    }
    return greedySplit(arr, k); // 备用方案
}

function findOptimalTwoSplit(arr, k) {
    const n = arr.length;
    if (n < 2) {
        return greedySplit(arr, k);
    }

    let bestSplit = null;
    let bestStdDev = Infinity;

    // 预计算前缀和
    const prefixSum = [0];
    for (let i = 0; i < n; i++) {
        prefixSum[i + 1] = prefixSum[i] + arr[i].length;
    }

    // 枚举所有可能的分割点
    for (let i = 1; i <= n - 1; i++) {
        global_counter++;
        const group1 = arr.slice(0, i);
        const group2 = arr.slice(i);

        // 计算每组长度
        const len1 = prefixSum[i] - prefixSum[0];
        const len2 = prefixSum[n] - prefixSum[i];

        // 检查是否超过限制
        if (len1 <= k && len2 <= k) {
            const mean = (len1 + len2) / 2;
            const stdDev = Math.sqrt((Math.pow(len1 - mean, 2) + Math.pow(len2 - mean, 2)) / 2);

            if (stdDev < bestStdDev) {
                bestStdDev = stdDev;
                bestSplit = [group1, group2];
            }
        }
    }

    // 如果没有找到满足条件的划分，使用贪心算法
    if (!bestSplit) {
        return greedySplit(arr, k);
    }

    return bestSplit;
}

function findOptimalThreeSplit(arr, k) {
    const n = arr.length;
    if (n < 3) {
        return greedySplit(arr, k);
    }

    // 预计算前缀和
    const prefixSum = [0];
    for (let i = 0; i < n; i++) {
        prefixSum[i + 1] = prefixSum[i] + arr[i].length;
    }

    let bestSplit = null;
    let bestStdDev = Infinity;

    // 枚举所有可能的两个分割点
    for (let i = 1; i <= n - 2; i++) {
        for (let j = i + 1; j <= n - 1; j++) {
            global_counter++;
            const group1 = arr.slice(0, i);
            const group2 = arr.slice(i, j);
            const group3 = arr.slice(j);

            // 计算每组长度
            const len1 = prefixSum[i] - prefixSum[0];
            const len2 = prefixSum[j] - prefixSum[i];
            const len3 = prefixSum[n] - prefixSum[j];

            // 检查是否超过限制
            if (len1 <= k && len2 <= k && len3 <= k) {
                const stdDev = calculateStdDevForThree(len1, len2, len3);

                if (stdDev < bestStdDev) {
                    bestStdDev = stdDev;
                    bestSplit = [group1, group2, group3];
                }
            }
        }
    }

    // 如果没有找到满足条件的划分，使用贪心算法
    if (!bestSplit) {
        return greedySplit(arr, k);
    }

    return bestSplit;
}

// 其他辅助函数保持不变
function greedySplit(arr, k) {
    const result = [];
    let currentGroup = [];
    let currentLength = 0;

    for (const obj of arr) {
        global_counter++;
        if (currentLength + obj.length <= k) {
            currentGroup.push(obj);
            currentLength += obj.length;
        } else {
            if (currentGroup.length > 0) {
                result.push(currentGroup);
            }
            currentGroup = [obj];
            currentLength = obj.length;
        }
    }

    if (currentGroup.length > 0) {
        result.push(currentGroup);
    }

    return result;
}

function rebalanceLastThreeWithDP(initialGroups, arr, k) {
    if (initialGroups.length <= 3) {
        return initialGroups;
    }

    // 确定最后3组在原始数组中的起始位置
    const elementsBeforeLastThree = initialGroups.slice(0, -3).reduce(
        (count, group) => count + group.length, 0
    );
    const lastThreeSegment = arr.slice(elementsBeforeLastThree);

    // 使用动态规划找到最优的3组划分
    const optimalSplit = findOptimalThreeSplit(lastThreeSegment, k);

    // 组合结果
    return [...initialGroups.slice(0, -3), ...optimalSplit];
}

function calculateStdDevForThree(len1, len2, len3) {
    const mean = (len1 + len2 + len3) / 3;
    const variance = (
        Math.pow(len1 - mean, 2) +
        Math.pow(len2 - mean, 2) +
        Math.pow(len3 - mean, 2)
    ) / 3;

    return Math.sqrt(variance);
}

// 完整版本，结合所有优化
function robustBalancedSplit(arr, k) {
    if (arr.length === 0) return [];

    const initialGroups = greedySplit(arr, k);

    // 如果只有一个分组，不需要优化
    if (initialGroups.length === 1) {
        return initialGroups;
    }

    // 计算当前分组的均匀性
    const currentStdDev = calculateStdDev(initialGroups);

    // 如果均匀性已经很好，不需要优化
    if (currentStdDev < k * 0.2) {
        return initialGroups;
    }

    // 应用优化
    let optimized;
    if (initialGroups.length <= 3) {
        optimized = optimizeSmallGroups(arr, initialGroups.length, k);
    } else {
        optimized = rebalanceLastThreeWithDP(initialGroups, arr, k);
    }

    // 只有当优化后的均匀性更好时才使用
    return calculateStdDev(optimized) < currentStdDev ? optimized : initialGroups;
}

function calculateStdDev(groups) {
    const lengths = groups.map(group =>
        group.reduce((sum, obj) => sum + obj.length, 0)
    );

    const mean = lengths.reduce((a, b) => a + b, 0) / lengths.length;
    const variance = lengths.reduce((sum, length) =>
        sum + Math.pow(length - mean, 2), 0) / lengths.length;

    return Math.sqrt(variance);
}









// 测试你的例子
const testData1 = [
    { id: 1, length: 10 },
    { id: 2, length: 5 },
    { id: 3, length: 5 },
    { id: 4, length: 10 }
];

const k1 = 20;

console.log("测试例子: [10, 5, 5, 10], k=20");
console.log("期望结果: [10,5] 和 [5,10]");

const result1 = splitArrayEvenly(testData1, k1);
console.log("均匀拆分算法结果:");
result1.forEach((chunk, index) => {
    const totalLength = chunk.reduce((sum, obj) => sum + obj.length, 0);
    console.log(`子数组 ${index + 1}: 长度=${totalLength}, 对象=${chunk.map(obj => obj.length).join(',')}`);
});

// 更多测试用例
console.log("\n=== 更多测试用例 ===");

// 测试用例1: 均匀分布
const testCase1 = [
    { id: 1, length: 8 },
    { id: 2, length: 7 },
    { id: 3, length: 6 },
    { id: 4, length: 9 }
];
console.log("\n测试用例1: [8,7,6,9], k=15");
const resultCase1 = splitArrayEvenly(testCase1, 15);
resultCase1.forEach((chunk, index) => {
    const totalLength = chunk.reduce((sum, obj) => sum + obj.length, 0);
    console.log(`子数组 ${index + 1}: 长度=${totalLength}, 对象=${chunk.map(obj => obj.length).join(',')}`);
});

// 测试用例2: 需要更细致的拆分
const testCase2 = [
    { id: 1, length: 12 },
    { id: 2, length: 8 },
    { id: 3, length: 5 },
    { id: 4, length: 7 },
    { id: 5, length: 10 }
];
console.log("\n测试用例2: [12,8,5,7,10], k=20");
const resultCase2 = splitArrayEvenly(testCase2, 20);
resultCase2.forEach((chunk, index) => {
    const totalLength = chunk.reduce((sum, obj) => sum + obj.length, 0);
    console.log(`子数组 ${index + 1}: 长度=${totalLength}, 对象=${chunk.map(obj => obj.length).join(',')}`);
});

// 验证函数：检查拆分是否合理
function validateSplit(result, k) {
    let isValid = true;
    const stats = {
        chunks: result.length,
        lengths: [],
        differences: []
    };

    for (let i = 0; i < result.length; i++) {
        const length = result[i].reduce((sum, obj) => sum + obj.length, 0);
        stats.lengths.push(length);

        if (length > k) {
            console.log(`错误: 子数组 ${i + 1} 长度 ${length} 超过限制 ${k}`);
            isValid = false;
        }

        if (i > 0) {
            const diff = Math.abs(length - stats.lengths[i - 1]);
            stats.differences.push(diff);
        }
    }

    if (isValid) {
        const avgDiff = stats.differences.reduce((a, b) => a + b, 0) / stats.differences.length || 0;
        console.log(`验证通过! 平均长度差异: ${avgDiff.toFixed(2)}`);
    }

    return isValid;
}

// 验证所有结果
console.log("\n=== 验证结果 ===");
validateSplit(result1, k1);
validateSplit(resultCase1, 15);
validateSplit(resultCase2, 20);

















// 均匀性测试用例
const uniformityTestCases = [
    // 测试用例1
    {
        name: "测试用例1",
        data: [
            { id: 1, length: 10 },
            { id: 2, length: 1 },
            { id: 3, length: 1 },
            { id: 4, length: 10 },
            { id: 5, length: 1 },
            { id: 6, length: 1 },
            { id: 7, length: 10 }
        ],
        k: 12,
        expected: [
            [{ id: 1, length: 10 }, { id: 2, length: 1 }],
            [{ id: 3, length: 1 }, { id: 4, length: 10 }, { id: 5, length: 1 }],
            [{ id: 6, length: 1 }, { id: 7, length: 10 }]
        ],
        expected2: [
            [{ id: 1, length: 10 }, { id: 2, length: 1 }],
            [{ id: 3, length: 1 }, { id: 4, length: 10 }],
            [{ id: 5, length: 1 }, { id: 6, length: 1 }, { id: 7, length: 10 }]
        ]
    },

    // 测试用例2
    {
        name: "测试用例2",
        data: [
            { id: 1, length: 9 },
            { id: 2, length: 3 },
            { id: 3, length: 3 },
            { id: 4, length: 3 },
            { id: 5, length: 9 },
            { id: 6, length: 3 },
            { id: 7, length: 3 },
            { id: 8, length: 3 }
        ],
        k: 12,
        expected: [
            [{ id: 1, length: 9 }],
            [{ id: 2, length: 3 }, { id: 3, length: 3 }, { id: 4, length: 3 },],
            [{ id: 5, length: 9 }],
            [{ id: 6, length: 3 },{ id: 7, length: 3 }, { id: 8, length: 3 }]
        ]
    },

    // 测试用例3
    {
        name: "测试用例3",
        data: [
            { id: 1, length: 8 },
            { id: 2, length: 2 },
            { id: 3, length: 2 },
            { id: 4, length: 4 },
            { id: 5, length: 4 },
            { id: 6, length: 8 },
            { id: 7, length: 2 },
            { id: 8, length: 2 },
            { id: 9, length: 4 },
            { id: 10, length: 4 }
        ],
        k: 12,
        expected: [
            [{ id: 1, length: 8 }, { id: 2, length: 2 }],
            [{ id: 3, length: 2 }, { id: 4, length: 4 }, { id: 5, length: 4 }],
            [{ id: 6, length: 8 }, { id: 7, length: 2 }],
            [{ id: 8, length: 2 }, { id: 9, length: 4 }, { id: 10, length: 4 }]
        ]
    },

    // 测试用例4
    {
        name: "测试用例4",
        data: [
            { id: 1, length: 10 },
            { id: 2, length: 5 },
            { id: 3, length: 5 },
            { id: 4, length: 10 },
            { id: 5, length: 5 },
            { id: 6, length: 5 },
            { id: 7, length: 10 },
            { id: 8, length: 5 }
        ],
        k: 20,
        // 两种方式均匀性相同，接受任意一种
        expected: [
            [{ id: 1, length: 10 }, { id: 2, length: 5 }, { id: 3, length: 5 }],
             [{ id: 4, length: 10 }, { id: 5, length: 5 }, { id: 6, length: 5 }],
            [{ id: 7, length: 10 }, { id: 8, length: 5 }]
        ],
        expected2: [
            [{ id: 1, length: 10 }, { id: 2, length: 5 }],
             [{ id: 3, length: 5 }, { id: 4, length: 10 }, { id: 5, length: 5 }],
            [{ id: 6, length: 5 },{ id: 7, length: 10 }, { id: 8, length: 5 }]
        ]
    }
];


// 测试用例集合
const additionalTestCases = [
    // 测试用例1: 空数组
    {
        name: "空数组",
        data: [],
        k: 10,
        expected: []
    },

    // 测试用例2: 单个元素
    {
        name: "单个元素",
        data: [{ id: 1, length: 5 }],
        k: 10,
        expected: [[{ id: 1, length: 5 }]]
    },

    // 测试用例3: 所有元素长度相同
    {
        name: "所有元素长度相同",
        data: [
            { id: 1, length: 5 },
            { id: 2, length: 5 },
            { id: 3, length: 5 },
            { id: 4, length: 5 },
            { id: 5, length: 5 }
        ],
        k: 12,
        expected: [
            [{ id: 1, length: 5 }, { id: 2, length: 5 }],
            [{ id: 3, length: 5 }, { id: 4, length: 5 }],
            [{ id: 5, length: 5 }]
        ]
    },

    // 测试用例4: 元素长度刚好等于k
    {
        name: "元素长度刚好等于k",
        data: [
            { id: 1, length: 10 },
            { id: 2, length: 10 },
            { id: 3, length: 10 }
        ],
        k: 10,
        expected: [
            [{ id: 1, length: 10 }],
            [{ id: 2, length: 10 }],
            [{ id: 3, length: 10 }]
        ]
    },

    // 测试用例5: 需要精细平衡的情况
    {
        name: "需要精细平衡",
        data: [
            { id: 1, length: 8 },
            { id: 2, length: 7 },
            { id: 3, length: 6 },
            { id: 4, length: 9 }
        ],
        k: 15,
        expected: [
            [{ id: 1, length: 8 }, { id: 2, length: 7 }],
            [{ id: 3, length: 6 }, { id: 4, length: 9 }]
        ]
    },

    // 测试用例6: 大数小数交替
    {
        name: "大数小数交替",
        data: [
            { id: 1, length: 9 },
            { id: 2, length: 1 },
            { id: 3, length: 8 },
            { id: 4, length: 2 },
            { id: 5, length: 7 },
            { id: 6, length: 3 }
        ],
        k: 10,
        expected: [
            [{ id: 1, length: 9 }, { id: 2, length: 1 }],
            [{ id: 3, length: 8 }, { id: 4, length: 2 }],
            [{ id: 5, length: 7 }, { id: 6, length: 3 }]
        ]
    },

    // 测试用例7: 所有元素总和远小于k
    {
        name: "总和远小于k",
        data: [
            { id: 1, length: 2 },
            { id: 2, length: 3 },
            { id: 3, length: 1 }
        ],
        k: 20,
        expected: [
            [{ id: 1, length: 2 }, { id: 2, length: 3 }, { id: 3, length: 1 }]
        ]
    },

    // 测试用例8: 需要多个元素才能接近k
    {
        name: "多个小元素组合",
        data: [
            { id: 1, length: 1 },
            { id: 2, length: 1 },
            { id: 3, length: 1 },
            { id: 4, length: 1 },
            { id: 5, length: 1 },
            { id: 6, length: 1 },
            { id: 7, length: 1 },
            { id: 8, length: 1 },
            { id: 9, length: 1 },
            { id: 10, length: 1 }
        ],
        k: 5,
        expected: [
            [{ id: 1, length: 1 }, { id: 2, length: 1 }, { id: 3, length: 1 }, { id: 4, length: 1 }, { id: 5, length: 1 }],
            [{ id: 6, length: 1 }, { id: 7, length: 1 }, { id: 8, length: 1 }, { id: 9, length: 1 }, { id: 10, length: 1 }]
        ]
    },

    // 测试用例9: 极不均匀的分布
    {
        name: "极不均匀分布",
        data: [
            { id: 1, length: 1 },
            { id: 2, length: 19 },
            { id: 3, length: 1 },
            { id: 4, length: 19 },
            { id: 5, length: 1 }
        ],
        k: 20,
        expected: [
            [{ id: 1, length: 1 }, { id: 2, length: 19 }],
            [{ id: 3, length: 1 }, { id: 4, length: 19 }],
            [{ id: 5, length: 1 }]
        ]
    },

    // 测试用例10: 边界情况 - 刚好达到但不超k
    {
        name: "边界情况",
        data: [
            { id: 1, length: 6 },
            { id: 2, length: 7 },
            { id: 3, length: 7 },
            { id: 4, length: 6 },
            { id: 5, length: 7 }
        ],
        k: 13,
        expected: [
            [{ id: 1, length: 6 }, { id: 2, length: 7 }],
            [{ id: 3, length: 7 }, { id: 4, length: 6 }],
            [{ id: 5, length: 7 }]
        ]
    }
];




// 简化的测试运行器
function runUniformityTests() {
    console.log("开始均匀性测试...\n");

    let passed = 0;
    let failed = 0;

    uniformityTestCases.push(...additionalTestCases)

    uniformityTestCases.forEach((testCase, index) => {
        console.log(`${testCase.name}:`);
        console.log(`输入: [${testCase.data.map(obj => obj.length).join(',')}], k=${testCase.k}`);

        global_counter = 0;
        const result = splitArrayEvenly(testCase.data, testCase.k);
        console.log("复杂度:" + global_counter);

        // 验证结果
        var isValid = validateResult(result, testCase.k, testCase.expected);
        if(testCase.expected2 && !isValid) {
            isValid = validateResult(result, testCase.k, testCase.expected2);
        }

        if (isValid) {
            console.log("✅ 测试通过");
            passed++;
        } else {
            console.log("❌ 测试失败");
            failed++;
        }

        console.log("拆分结果:");
        result.forEach((chunk, chunkIndex) => {
            const totalLength = chunk.reduce((sum, obj) => sum + obj.length, 0);
            console.log(`  子数组 ${chunkIndex + 1}: 长度=${totalLength}, 对象=${chunk.map(obj => obj.length).join(',')}`);
        });

        // 计算均匀性指标
        const lengths = result.map(chunk => chunk.reduce((sum, obj) => sum + obj.length, 0));
        const mean = lengths.reduce((a, b) => a + b, 0) / lengths.length;
        const variance = lengths.reduce((sum, length) => sum + Math.pow(length - mean, 2), 0) / lengths.length;
        const stdDev = Math.sqrt(variance);

        console.log(`分组长度: [${lengths.join(',')}]`);
        console.log(`标准差: ${stdDev.toFixed(3)}`);
        console.log("---\n");
    });

    console.log(`测试总结: 通过 ${passed} / 失败 ${failed} / 总计 ${uniformityTestCases.length}`);
}

// 简化的验证函数
function validateResult(result, k, expected) {
    // 检查是否超过限制
    for (const chunk of result) {
        const totalLength = chunk.reduce((sum, obj) => sum + obj.length, 0);
        if (totalLength > k) {
            console.log(`错误: 子数组长度 ${totalLength} 超过限制 ${k}`);
            return false;
        }
    }

    // 如果expected为null，表示接受任何有效拆分
    if (expected === null) {
        return true;
    }

    // 检查与期望结果的一致性
    if (expected && expected.length > 0) {
        // 检查分组数量
        if (result.length !== expected.length) {
            console.log(`分组数量不匹配: 期望 ${expected.length} 组，实际 ${result.length} 组`);
            return false;
        }

        // 检查每个分组的内容
        for (let i = 0; i < result.length; i++) {
            const actualLengths = result[i].map(obj => obj.length).join(',');
            const expectedLengths = expected[i].map(obj => obj.length).join(',');

            if (actualLengths !== expectedLengths) {
                console.log(`子数组 ${i + 1} 不匹配`);
                console.log(`  期望: [${expectedLengths}]`);
                console.log(`  实际: [${actualLengths}]`);
                return false;
            }
        }
    }

    return true;
}

// 运行测试
runUniformityTests();