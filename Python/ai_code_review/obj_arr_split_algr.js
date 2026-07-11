function splitArrayEvenly2(arr, k) {
    if (arr.length === 0) return [];

    // 先计算最小分组数
    const minGroups = calculateMinGroups(arr, k);

    // 使用回溯法找到最均匀的拆分方式
    const result = [];
    let bestSolution = null;
    let bestStdDev = Infinity;

    function backtrack(start, groups) {
        if (start === arr.length) {
            // 找到了一个有效的拆分方案
            if (groups.length === minGroups) {
                // 计算这个方案的均匀性
                const lengths = groups.map(group =>
                    group.reduce((sum, obj) => sum + obj.length, 0)
                );
                const stdDev = calculateStdDev2(lengths);

                if (stdDev < bestStdDev) {
                    bestStdDev = stdDev;
                    bestSolution = groups.map(group => [...group]);
                }
            }
            return;
        }

        if (groups.length >= minGroups) return;

        // 尝试不同的结束位置
        let currentLength = 0;
        for (let end = start; end < arr.length; end++) {
            global_counter++;
            currentLength += arr[end].length;
            if (currentLength > k) break;

            // 创建新分组
            const newGroup = arr.slice(start, end + 1);
            groups.push(newGroup);

            // 继续递归
            backtrack(end + 1, groups);

            // 回溯
            groups.pop();
        }
    }

    backtrack(0, []);
    return bestSolution || [arr]; // 如果没有找到解，返回整个数组
}

// 计算最小分组数
function calculateMinGroups(arr, k) {
    let groups = 0;
    let currentLength = 0;

    for (const obj of arr) {
        global_counter++;
        if (currentLength + obj.length <= k) {
            currentLength += obj.length;
        } else {
            groups++;
            currentLength = obj.length;
        }
    }

    if (currentLength > 0) groups++;
    return groups;
}

// 计算标准差
function calculateStdDev2(lengths) {
    if (lengths.length <= 1) return 0;

    const mean = lengths.reduce((a, b) => a + b, 0) / lengths.length;
    const variance = lengths.reduce((sum, length) =>
        sum + Math.pow(length - mean, 2), 0) / lengths.length;

    return Math.sqrt(variance);
}



// ________________________________________________________________________________________________________________
var global_counter = 0;

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

function adjustGreedySolution(arr, k, adjustGroupIndex, removeCount) {
    const result = [];
    let currentIndex = 0;

    // 复制前adjustGroupIndex组
    const baseSolution = greedySplit(arr, k);
    for (let i = 0; i < adjustGroupIndex; i++) {
        if (i < baseSolution.length) {
            result.push([...baseSolution[i]]);
            currentIndex += baseSolution[i].length;
        }
    }

    // 调整目标组
    if (adjustGroupIndex >= baseSolution.length) return null;

    const targetGroup = baseSolution[adjustGroupIndex];
    if (targetGroup.length <= removeCount) return null;

    // 创建调整后的组（减少removeCount个元素）
    const adjustedGroup = targetGroup.slice(0, targetGroup.length - removeCount);
    result.push(adjustedGroup);
    currentIndex += adjustedGroup.length;

    // 对剩余元素重新使用贪心算法
    const remainingArr = arr.slice(currentIndex);
    const remainingGroups = greedySplit(remainingArr, k);

    // 检查总分组数是否一致
    if (result.length + remainingGroups.length !== baseSolution.length) {
        return null;
    }

    return [...result, ...remainingGroups];
}

function selectBestSolution(candidates) {
    let bestSolution = candidates[0];
    let bestStdDev = calculateStdDev(bestSolution);

    for (let i = 1; i < candidates.length; i++) {
        const stdDev = calculateStdDev(candidates[i]);
        if (stdDev < bestStdDev) {
            bestStdDev = stdDev;
            bestSolution = candidates[i];
        }
    }

    return bestSolution;
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


function splitArrayEvenly1(arr, k) {
    if (arr.length === 0) return [];

    // 生成多个候选解
    const candidates = [];

    // 基础贪心解
    const greedySolution = greedySplit(arr, k);
    candidates.push(greedySolution);

    // 尝试调整前几组
    const maxAdjustGroups = greedySolution.length - 1 //Math.min(3, greedySolution.length - 1);

    for (let adjustGroup = 0; adjustGroup < maxAdjustGroups; adjustGroup++) {
        // 尝试不同的减少元素数量
        for (let removeCount = 1; removeCount <= 3; removeCount++) {
            const adjustedSolution = adjustGreedySolution(arr, k, adjustGroup, removeCount);
            if (adjustedSolution && adjustedSolution.length === greedySolution.length) {
                candidates.push(adjustedSolution);
            }
        }
    }

    // 选择最均匀的解
    return selectBestSolution(candidates);
}

function splitArrayEvenly(arr, k) {
    if (arr.length === 0) return [];

    const candidates = new Set(); // 使用Set避免重复解

    // 1. 基础贪心解
    const baseSolution = greedySplit(arr, k);
    candidates.add(solutionToKey(baseSolution));

    // 2. 多轮调整，逐步增加调整深度
    const maxRounds = baseSolution.length - 1 //Math.min(3, baseSolution.length - 1);
    for (let round = 1; round <= maxRounds; round++) {
        const newCandidates = new Set();

        // 对每个候选解进行扩展
        candidates.forEach(solutionKey => {
            const solution = keyToSolution(solutionKey, arr);

            // 尝试调整前round组
            for (let groupIdx = 0; groupIdx < Math.min(round, solution.length - 1); groupIdx++) {
                // 尝试不同的调整粒度
                for (let removeCount = 1; removeCount <= Math.min(3, solution[groupIdx].length - 1); removeCount++) {
                    const newSolution = adjustGreedySolution(solution, arr, k, groupIdx, removeCount);
                    if (newSolution && newSolution.length === solution.length) {
                        newCandidates.add(solutionToKey(newSolution));
                    }
                }
            }
        });

        // 合并候选解
        newCandidates.forEach(key => candidates.add(key));

        // 如果候选解数量过多，进行剪枝
        if (candidates.size > 20) {
            const pruned = pruneCandidates(Array.from(candidates).map(key => keyToSolution(key, arr)));
            candidates.clear();
            pruned.forEach(sol => candidates.add(solutionToKey(sol)));
        }
    }

    // 选择最佳解
    const finalCandidates = Array.from(candidates).map(key => keyToSolution(key, arr));
    return selectBestSolution(finalCandidates);
}

// 辅助函数：解决方案序列化
function solutionToKey(solution) {
    return solution.map(group =>
        group.map(obj => obj.length).join(',')
    ).join('|');
}

function keyToSolution(key, arr) {
    const groupLengths = key.split('|').map(part => part.split(',').map(Number));

    const solution = [];
    let arrIndex = 0;

    for (const lengths of groupLengths) {
        const group = [];
        for (const len of lengths) {
            global_counter++;
            // 在原始数组中查找对应长度的对象
            // 这里简化处理，实际需要更精确的匹配
            if (arrIndex < arr.length && arr[arrIndex].length === len) {
                group.push(arr[arrIndex]);
                arrIndex++;
            }
        }
        solution.push(group);
    }

    return solution;
}

// 剪枝函数：保留均匀性最好的前N个候选解
function pruneCandidates(candidates, keepCount = 10) {
    return candidates
        .map(solution => ({
            solution,
            stdDev: calculateStdDev(solution)
        }))
        .sort((a, b) => a.stdDev - b.stdDev)
        .slice(0, keepCount)
        .map(item => item.solution);
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
        const result = splitArrayEvenly2(testCase.data, testCase.k);
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