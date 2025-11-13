/**
 * 增强版结构对比函数（JavaScript原生实现）
 * 
 * @author 崔浩浩
 * 
 * @description
 * 识别以下差异：
 * 1. dict2相比dict1缺失的字段（包括嵌套结构）
 * 2. 相同字段的类型不一致
 * 3. 列表结构差异（长度、元素类型）
 * 4. 字段返回内容一致
 * 5. 剔除白名单字段检查
 *    示例：{"go_article_service", "user.medal"}
 *    功能：
 *    1. 支持嵌套路径 (如 "user.medal" 会跳过该字段及其子字段)
 *    2. 支持列表元素路径 (如 "tags")
 *    3. 完全匹配路径时跳过所有检查
 * 
 * 新增功能：
 * 1. 对列表使用JavaScript原生代码进行深度对比
 * 2. 支持忽略列表顺序（ignore_order）
 * 3. 支持配置类型组参数（如数值精度、类型检查等）
 * 
 * @param {Object|Array} originData - Origin数据（字典或列表）
 * @param {Object|Array} currentData - Current数据（字典或列表）
 * @param {string} [path=""] - 当前路径（递归用）
 * @param {boolean} [checkValue=true] - 是否检查值差异
 * @param {boolean} [checkMissing=true] - 是否检查缺失字段
 * @param {boolean} [checkRedundant=false] - 是否检查冗余字段
 * @param {boolean} [checkType=true] - 是否检查类型差异
 * @param {Set<string>|Array<string>|null} [excludeFields=null] - 排除字段白名单
 * @param {Object|null} [deepDiffContrastConfig=null] - 对比配置参数
 * @param {boolean} [openLog=false] - 开启日志，默认关闭
 * 
 * @returns {Array<string>} 差异列表
 * 
 * @example
 * const differences = compareStructures(
 *   { name: "test", age: 20 },
 *   { name: "test", age: 21 },
 *   "",
 *   true,
 *   true,
 *   false,
 *   true,
 *   new Set(["timestamp"]),
 *   { ignore_order: true },
 *   false
 * );
 */
 compareStructures = function(
    originData,
    currentData,
    path = "",
    checkValue = true,
    checkMissing = true,
    checkRedundant = false,
    checkType = true,
    excludeFields = null,
    deepDiffContrastConfig = null,
    openLog = false
) {
    // ==================== 内部辅助函数定义开始 ====================

    /**
     * 深拷贝对象或数组
     * @param {*} obj - 要拷贝的对象
     * @returns {*} 深拷贝后的对象
     */
    function deepCopy(obj) {
        return JSON.parse(JSON.stringify(obj));
    }

    /**
     * 判断是否为对象类型（不包括null和数组）
     * @param {*} obj - 待判断的值
     * @returns {boolean} 是否为对象
     */
    function isObject(obj) {
        return obj !== null && typeof obj === 'object' && !Array.isArray(obj);
    }

    /**
     * 判断是否为数组类型
     * @param {*} obj - 待判断的值
     * @returns {boolean} 是否为数组
     */
    function isArray(obj) {
        return Array.isArray(obj);
    }

    /**
     * 判断是否为字典或列表类型
     * @param {*} obj - 待判断的值
     * @returns {boolean} 是否为字典或列表
     */
    function isDictOrList(obj) {
        return isObject(obj) || isArray(obj);
    }

    /**
     * 处理字典类型对比
     * @param {Object} originDict - Origin字典
     * @param {Object} currentDict - Current字典
     * @param {string} path - 当前路径
     * @param {boolean} checkValue - 是否检查值差异
     * @param {boolean} checkMissing - 是否检查缺失字段
     * @param {boolean} checkRedundant - 是否检查冗余字段
     * @param {boolean} checkType - 是否检查类型差异
     * @param {Set<string>} excludeFields - 排除字段集合
     * @param {Object} deepDiffContrastConfig - 对比配置
     * @param {Array<string>} differences - 差异列表
     * @param {boolean} openLog - 是否开启日志
     * @returns {Array<string>} 差异列表
     */
    function compareDicts(
        originDict,
        currentDict,
        path,
        checkValue,
        checkMissing,
        checkRedundant,
        checkType,
        excludeFields,
        deepDiffContrastConfig,
        differences,
        openLog
    ) {
        // 检查Origin字段
        for (const key in originDict) {
            if (!originDict.hasOwnProperty(key)) continue;

            const currentPath = formatPath(path ? `${path}.${key}` : key);
            
            // 检查路径是否在排除字段集合中 普通匹配
            if (excludeFields.has(currentPath)) {
                continue;
            }

            // 检查路径是否在排除字段集合中 数组匹配
            let skipCurrentPath = false;
            for (const excludePattern of excludeFields) {
                // 步骤1: 转义整个模式（确保特殊字符被转义）
                let regexPattern = excludePattern.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
                // 步骤2: 将转义后的 \[\*\] 替换为匹配数字的 \[\d+\]
                regexPattern = regexPattern.replace(/\\\[\\\*\\\]/g, '\\[\\d+\\]');
                // 步骤3: 编译正则并匹配完整路径
                const regex = new RegExp(`^${regexPattern}$`);
                if (regex.test(currentPath)) {
                    skipCurrentPath = true;
                    break;
                }
            }
            // 数组类型的字段忽略跳过
            if (skipCurrentPath) {
                continue;
            }

            const originVal = originDict[key];

            // 字段存在性检查
            if (!(key in currentDict)) {
                if (checkMissing) {
                    differences.push(
                        `[字段缺失] ${currentPath} (Origin类型: ${typeDetail(originVal)})`
                    );
                }
                continue;
            }

            const currentVal = currentDict[key];

            // 递归处理嵌套结构
            if (isDictOrList(originVal) && isDictOrList(currentVal)) {
                const nestedDiffs = compareStructures(
                    originVal,
                    currentVal,
                    currentPath,
                    checkValue,
                    checkMissing,
                    checkRedundant,
                    checkType,
                    excludeFields,
                    deepDiffContrastConfig,
                    openLog
                );
                differences.push(...nestedDiffs);
            } else {
                // 值对比开启
                if (checkValue) {
                    // 第一步：快速等价判断（优先于类型检查，需要配置 ignore_type_in_groups）
                    if (isEquivalentValue(originVal, currentVal, deepDiffContrastConfig)) {
                        continue; // 跳过差异记录
                    }
                    
                    // 第二步：类型冲突检查（考虑嵌套结构）
                    if (checkType && !isSameType(originVal, currentVal, deepDiffContrastConfig)) {
                        differences.push(
                            `[类型冲突] ${currentPath} ` +
                            `Origin类型: ${typeDetail(originVal)} → ` +
                            `Current类型: ${typeDetail(currentVal)}`
                        );
                        continue;
                    }
                    
                    // 第三步：值对比
                    if (originVal !== currentVal) {
                        differences.push(
                            `[值变化] ${currentPath} ` +
                            `Origin值: ${formatValue(originVal)} → ` +
                            `Current值: ${formatValue(currentVal)}`
                        );
                    }
                } else {
                    // 值对比关闭时检查逻辑
                    differences = specialValueCheck(
                        originVal,
                        currentVal,
                        currentPath,
                        differences
                    );
                }
            }
        }

        // 冗余字段检查
        if (checkRedundant) {
            for (const key in currentDict) {
                if (!currentDict.hasOwnProperty(key)) continue;
                const currentPath = formatPath(path ? `${path}.${key}` : key);
                if (!(key in originDict) && !excludeFields.has(currentPath)) {
                    differences.push(
                        `[冗余字段] ${currentPath} (Current类型: ${typeDetail(currentDict[key])})`
                    );
                }
            }
        }

        return differences;
    }

    /**
     * 列表对比逻辑
     * @param {Array} originList - Origin列表
     * @param {Array} currentList - Current列表
     * @param {string} path - 当前路径
     * @param {boolean} checkValue - 是否检查值差异
     * @param {boolean} checkMissing - 是否检查缺失字段
     * @param {boolean} checkRedundant - 是否检查冗余字段
     * @param {boolean} checkType - 是否检查类型差异
     * @param {Set<string>} excludeFields - 排除字段集合
     * @param {Object} deepDiffContrastConfig - 对比配置
     * @param {Array<string>} differences - 差异列表
     * @param {boolean} openLog - 是否开启日志
     * @returns {Array<string>} 差异列表
     */
    function compareLists(
        originList,
        currentList,
        path,
        checkValue,
        checkMissing,
        checkRedundant,
        checkType,
        excludeFields,
        deepDiffContrastConfig,
        differences,
        openLog
    ) {
        // 值对比开启
        if (checkValue) {
            differences = compareListsNative(
                originList,
                currentList,
                path,
                checkType,
                excludeFields,
                deepDiffContrastConfig,
                differences,
                openLog
            );
        } else {
            // 不检查值时需要校验字段是否非空
            const minLen = Math.min(originList.length, currentList.length);
            for (let i = 0; i < minLen; i++) {
                const elemPath = `${path}[${i}]`;
                if (isDictOrList(originList[i]) && isDictOrList(currentList[i])) {
                    const nestedDiffs = compareStructures(
                        originList[i],
                        currentList[i],
                        elemPath,
                        checkValue,
                        checkMissing,
                        checkRedundant,
                        checkType,
                        excludeFields,
                        deepDiffContrastConfig,
                        openLog
                    );
                    differences.push(...nestedDiffs);
                } else {
                    // 当关闭值对比时检查逻辑
                    differences = specialValueCheck(
                        originList[i],
                        currentList[i],
                        elemPath,
                        differences
                    );

                    // 基础类型对比
                    if (checkType && !isSameType(originList[i], currentList[i], deepDiffContrastConfig)) {
                        differences.push(
                            `[类型冲突] ${elemPath} ` +
                            `Origin类型: ${typeDetail(originList[i])} → ` +
                            `Current类型: ${typeDetail(currentList[i])}`
                        );
                    }
                }
            }
        }
        return differences;
    }

    /**
     * 使用JavaScript原生代码实现列表对比
     * @param {Array} originList - Origin列表
     * @param {Array} currentList - Current列表
     * @param {string} path - 当前路径
     * @param {boolean} checkType - 是否检查类型差异
     * @param {Set<string>} excludeFields - 排除字段集合
     * @param {Object} deepDiffContrastConfig - 对比配置
     * @param {Array<string>} differences - 差异列表
     * @param {boolean} openLog - 是否开启日志
     * @returns {Array<string>} 差异列表
     */
    function compareListsNative(
        originList,
        currentList,
        path,
        checkType,
        excludeFields,
        deepDiffContrastConfig,
        differences,
        openLog
    ) {
        if (openLog) {
            console.log(`_compare_lists_native_path:${path}`);
            console.log(`_compare_lists_native_origin_len:${originList.length}`);
            console.log(`_compare_lists_native_current_len:${currentList.length}`);
        }

        const ignoreOrder = (deepDiffContrastConfig && deepDiffContrastConfig.ignore_order !== undefined) 
            ? deepDiffContrastConfig.ignore_order 
            : true;

        // 如果忽略顺序，需要特殊处理
        if (ignoreOrder) {
            // 创建副本以避免修改原始数据
            const originListCopy = deepCopy(originList);
            const currentListCopy = deepCopy(currentList);

            // 记录匹配关系：origin_index -> current_index
            const originMatched = {}; // {origin_index: current_index}
            const currentMatched = new Set(); // 已匹配的current索引

            // 第一遍：精确匹配并记录匹配关系
            for (let i = 0; i < originListCopy.length; i++) {
                const originItem = originListCopy[i];
                for (let j = 0; j < currentListCopy.length; j++) {
                    if (currentMatched.has(j)) {
                        continue;
                    }
                    // 检查是否匹配
                    if (itemsMatch(originItem, currentListCopy[j], checkType, deepDiffContrastConfig)) {
                        originMatched[i] = j;
                        currentMatched.add(j);
                        break;
                    }
                }
            }

            // 处理未匹配的元素：尝试找到最相似的元素进行对比，或标记为差异
            const originUnmatched = [];
            const currentUnmatched = [];
            
            for (let i = 0; i < originListCopy.length; i++) {
                if (!(i in originMatched)) {
                    originUnmatched.push(i);
                }
            }

            for (let j = 0; j < currentListCopy.length; j++) {
                if (!currentMatched.has(j)) {
                    currentUnmatched.push(j);
                }
            }

            // 尝试匹配未匹配的元素（用于详细对比）
            const unmatchedMatched = {}; // {origin_idx: current_idx}
            const currentUnmatchedMatched = new Set();
            
            for (const origIdx of originUnmatched) {
                const originItem = originListCopy[origIdx];
                let bestMatch = null;
                let bestMatchIdx = -1;
                
                // 尝试找到最相似的元素（至少是相同类型）
                for (const currIdx of currentUnmatched) {
                    if (currentUnmatchedMatched.has(currIdx)) {
                        continue;
                    }
                    const currentItem = currentListCopy[currIdx];
                    
                    // 如果类型相同，尝试匹配
                    if (isSameType(originItem, currentItem, deepDiffContrastConfig)) {
                        if (isDictOrList(originItem) && isDictOrList(currentItem)) {
                            bestMatch = currIdx;
                            bestMatchIdx = currIdx;
                            break; // 找到类型匹配的就对比
                        } else if (originItem === currentItem) {
                            bestMatch = currIdx;
                            bestMatchIdx = currIdx;
                            break;
                        }
                    }
                }
                
                if (bestMatch !== null) {
                    unmatchedMatched[origIdx] = bestMatch;
                    currentUnmatchedMatched.add(bestMatch);
                }
            }

            // 对于未匹配但找到相似元素的，进行递归对比
            for (const origIdx in unmatchedMatched) {
                const currIdx = unmatchedMatched[origIdx];
                const elemPath = `${path}[${origIdx}]`;
                if (shouldExclude(elemPath, excludeFields)) {
                    continue;
                }

                const originItem = originListCopy[origIdx];
                const currentItem = currentListCopy[currIdx];

                // 递归对比
                if (isDictOrList(originItem) && isDictOrList(currentItem)) {
                    const nestedDiffs = compareStructures(
                        originItem,
                        currentItem,
                        elemPath,
                        true, // check_value
                        true, // check_missing
                        false, // check_redundant
                        checkType,
                        excludeFields,
                        deepDiffContrastConfig,
                        openLog
                    );
                    differences.push(...nestedDiffs);
                }
            }

            // 对于完全无法匹配的元素，标记为差异
            for (const i of originUnmatched) {
                if (!(i in unmatchedMatched)) {
                    const elemPath = `${path}[${i}]`;
                    if (shouldExclude(elemPath, excludeFields)) {
                        continue;
                    }
                    // 即使无法匹配，也尝试递归对比其内部结构（如果有的话）
                    const originItem = originListCopy[i];
                    if (isDictOrList(originItem)) {
                        // 尝试与 current 中第一个未匹配的元素对比
                        let foundMatch = false;
                        for (const j of currentUnmatched) {
                            if (!currentUnmatchedMatched.has(j)) {
                                const currentItem = currentListCopy[j];
                                if (isDictOrList(currentItem)) {
                                    const nestedDiffs = compareStructures(
                                        originItem,
                                        currentItem,
                                        elemPath,
                                        true,
                                        true,
                                        false,
                                        checkType,
                                        excludeFields,
                                        deepDiffContrastConfig,
                                        openLog
                                    );
                                    differences.push(...nestedDiffs);
                                    currentUnmatchedMatched.add(j);
                                    foundMatch = true;
                                    break;
                                }
                            }
                        }
                        if (!foundMatch) {
                            differences.push(
                                `[列表差异] ${elemPath} (iterable_item_removed)`
                            );
                        }
                    } else {
                        differences.push(
                            `[列表差异] ${elemPath} (iterable_item_removed)`
                        );
                    }
                }
            }

            for (const j of currentUnmatched) {
                if (!currentUnmatchedMatched.has(j)) {
                    const elemPath = `${path}[${j}]`;
                    if (shouldExclude(elemPath, excludeFields)) {
                        continue;
                    }
                    differences.push(
                        `[列表差异] ${elemPath} (iterable_item_added)`
                    );
                }
            }

            // 对于已匹配的元素，递归对比（使用原始索引路径）
            for (const origIdx in originMatched) {
                const currIdx = originMatched[origIdx];
                const elemPath = `${path}[${origIdx}]`;
                if (shouldExclude(elemPath, excludeFields)) {
                    continue;
                }

                const originItem = originListCopy[origIdx];
                const currentItem = currentListCopy[currIdx];

                // 递归对比
                if (isDictOrList(originItem) && isDictOrList(currentItem)) {
                    const nestedDiffs = compareStructures(
                        originItem,
                        currentItem,
                        elemPath,
                        true, // check_value
                        true, // check_missing
                        false, // check_redundant
                        checkType,
                        excludeFields,
                        deepDiffContrastConfig,
                        openLog
                    );
                    differences.push(...nestedDiffs);
                } else if (isObject(originItem) || isObject(currentItem)) {
                    // 如果一个是对象另一个不是，说明类型不匹配
                    if (checkType) {
                        differences.push(
                            `[类型冲突] ${elemPath} ` +
                            `Origin类型：${typeDetail(originItem)} → ` +
                            `Current类型：${typeDetail(currentItem)}`
                        );
                    }
                } else if (isArray(originItem) || isArray(currentItem)) {
                    // 如果一个是数组另一个不是，说明类型不匹配
                    if (checkType) {
                        differences.push(
                            `[类型冲突] ${elemPath} ` +
                            `Origin类型：${typeDetail(originItem)} → ` +
                            `Current类型：${typeDetail(currentItem)}`
                        );
                    }
                } else {
                    // 基础类型对比
                    // 第一步：检查等价值（优先于类型检查，需要配置 ignore_type_in_groups）
                    if (isEquivalentValue(originItem, currentItem, deepDiffContrastConfig)) {
                        continue; // 跳过差异记录
                    }
                    
                    // 第二步：类型冲突检查
                    if (checkType && !isSameType(originItem, currentItem, deepDiffContrastConfig)) {
                        differences.push(
                            `[类型冲突] ${elemPath} ` +
                            `Origin类型：${typeDetail(originItem)} → ` +
                            `Current类型：${typeDetail(currentItem)}`
                        );
                    } else if (originItem !== currentItem) {
                        // 检查类型转换
                        if (deepDiffContrastConfig && deepDiffContrastConfig.ignore_type_in_groups) {
                            const skip = typeConversionJudgment(originItem, currentItem, deepDiffContrastConfig);
                            if (skip) {
                                continue;
                            }
                        }
                        const oldFormatted = formatStructure(originItem);
                        const newFormatted = formatStructure(currentItem);
                        differences.push(
                            `[值变化] ${elemPath} Origin值: ${oldFormatted} → Current值: ${newFormatted}`
                        );
                    }
                }
            }
        } else {
            // 不忽略顺序，按索引对比
            const maxLen = Math.max(originList.length, currentList.length);
            for (let i = 0; i < maxLen; i++) {
                const elemPath = `${path}[${i}]`;

                // 检查是否在排除字段中
                if (shouldExclude(elemPath, excludeFields)) {
                    continue;
                }

                if (i >= originList.length) {
                    differences.push(
                        `[列表差异] ${elemPath} (iterable_item_added)`
                    );
                    continue;
                }

                if (i >= currentList.length) {
                    differences.push(
                        `[列表差异] ${elemPath} (iterable_item_removed)`
                    );
                    continue;
                }

                const originItem = originList[i];
                const currentItem = currentList[i];

                // 递归对比
                if (isDictOrList(originItem) && isDictOrList(currentItem)) {
                    const nestedDiffs = compareStructures(
                        originItem,
                        currentItem,
                        elemPath,
                        true, // check_value
                        true, // check_missing
                        false, // check_redundant
                        checkType,
                        excludeFields,
                        deepDiffContrastConfig,
                        openLog
                    );
                    differences.push(...nestedDiffs);
                } else {
                    // 基础类型对比
                    // 第一步：检查等价值（优先于类型检查，需要配置 ignore_type_in_groups）
                    if (isEquivalentValue(originItem, currentItem, deepDiffContrastConfig)) {
                        continue; // 跳过差异记录
                    }
                    
                    // 第二步：类型冲突检查
                    if (checkType && !isSameType(originItem, currentItem, deepDiffContrastConfig)) {
                        differences.push(
                            `[类型冲突] ${elemPath} ` +
                            `Origin类型：${typeDetail(originItem)} → ` +
                            `Current类型：${typeDetail(currentItem)}`
                        );
                    } else if (originItem !== currentItem) {
                        // 检查类型转换
                        if (deepDiffContrastConfig && deepDiffContrastConfig.ignore_type_in_groups) {
                            const skip = typeConversionJudgment(originItem, currentItem, deepDiffContrastConfig);
                            if (skip) {
                                continue;
                            }
                        }
                        const oldFormatted = formatStructure(originItem);
                        const newFormatted = formatStructure(currentItem);
                        differences.push(
                            `[值变化] ${elemPath} Origin值: ${oldFormatted} → Current值: ${newFormatted}`
                        );
                    }
                }
            }
        }

        return differences;
    }

    /**
     * 判断两个列表元素是否匹配（用于忽略顺序的列表对比）
     * @param {*} originItem - Origin元素
     * @param {*} currentItem - Current元素
     * @param {boolean} checkType - 是否检查类型
     * @param {Object} deepDiffContrastConfig - 对比配置
     * @returns {boolean} 是否匹配
     */
    function itemsMatch(originItem, currentItem, checkType, deepDiffContrastConfig) {
        // 类型检查
        if (checkType && !isSameType(originItem, currentItem, deepDiffContrastConfig)) {
            return false;
        }

        // 基本类型直接比较
        if (!isDictOrList(originItem) && !isDictOrList(currentItem)) {
            // 检查类型转换
            if (deepDiffContrastConfig && deepDiffContrastConfig.ignore_type_in_groups) {
                if (typeConversionJudgment(originItem, currentItem, deepDiffContrastConfig)) {
                    return true;
                }
            }
            return originItem === currentItem;
        }

        // 复杂类型需要深度比较
        if (isObject(originItem) && isObject(currentItem)) {
            const originKeys = Object.keys(originItem);
            const currentKeys = Object.keys(currentItem);
            if (originKeys.length !== currentKeys.length) {
                return false;
            }
            for (const key of originKeys) {
                if (!(key in currentItem)) {
                    return false;
                }
                if (!itemsMatch(originItem[key], currentItem[key], checkType, deepDiffContrastConfig)) {
                    return false;
                }
            }
            return true;
        }

        if (isArray(originItem) && isArray(currentItem)) {
            if (originItem.length !== currentItem.length) {
                return false;
            }
            // 对于列表，递归比较每个元素
            for (let i = 0; i < originItem.length; i++) {
                if (!itemsMatch(originItem[i], currentItem[i], checkType, deepDiffContrastConfig)) {
                    return false;
                }
            }
            return true;
        }

        return false;
    }

    /**
     * 判断给定的路径是否需要被排除，支持多层结构和通配符 [*] 的匹配
     * @param {string} cleanPath - 待检查的路径字符串，可能是多层级结构，如 "users.series.title"
     * @param {Set<string>} excludeFields - 包含需要排除的字段的集合，部分字段可能带有通配符 [*]，
     *                                      例如 "list[*].interest_tag[*].add_time"
     * @returns {boolean} 如果 cleanPath 匹配到 excludeFields 中的某个字段，则返回 true；否则返回 false
     */
    function shouldExclude(cleanPath, excludeFields) {
        // 将 cleanPath 按点号分割成多个部分，用于后续逐部分匹配
        const cleanParts = cleanPath.split('.');
        // 遍历排除字段集合中的每个字段
        for (const field of excludeFields) {
            // 将当前排除字段按点号分割成多个部分
            const fieldParts = field.split('.');
            // 若排除字段的部分数量少于 cleanPath 的部分数量，无法匹配，跳过该字段
            if (fieldParts.length < cleanParts.length) {
                continue;
            }
            // 初始化匹配标志为 true
            let match = true;
            // 逐部分比较 cleanPath 和当前排除字段
            for (let i = 0; i < fieldParts.length; i++) {
                const part = fieldParts[i];
                // 若已遍历完 cleanPath 的所有部分，跳出循环
                if (i >= cleanParts.length) {
                    break;
                }
                // 检查当前部分是否以 [*] 结尾，若是则表示使用了通配符
                if (part.endsWith('[*]')) {
                    // 提取 [*] 之前的基础部分
                    const base = part.slice(0, -3);
                    // 若 cleanPath 对应部分与基础部分不匹配，标记为不匹配
                    if (cleanParts[i] !== base) {
                        match = false;
                        break;
                    }
                } else if (part !== cleanParts[i]) {
                    // 若当前部分不以 [*] 结尾，直接检查是否与 cleanPath 对应部分不匹配
                    match = false;
                    break;
                }
            }
            // 若所有部分都匹配，返回 true
            if (match) {
                return true;
            }
        }
        // 若遍历完所有排除字段都未匹配，返回 false
        return false;
    }

    /**
     * 类型转换判断逻辑
     * @param {*} oldValue - 旧值
     * @param {*} newValue - 新值
     * @param {Object} deepDiffContrastConfig - 对比配置
     * @returns {boolean|null} 如果应该跳过则返回true，否则返回null
     */
    function typeConversionJudgment(oldValue, newValue, deepDiffContrastConfig) {
        const typeGroups = (deepDiffContrastConfig && deepDiffContrastConfig.ignore_type_in_groups) || [];
        for (const group of typeGroups) {
            const oldType = typeof oldValue;
            const newType = typeof newValue;
            
            // 检查类型是否在组中（需要将JavaScript类型映射到Python类型概念）
            const oldTypeInGroup = group.includes(oldType) || 
                (oldType === 'number' && (group.includes('number') || group.includes(Number))) ||
                (oldType === 'string' && (group.includes('string') || group.includes(String))) ||
                (oldType === 'boolean' && (group.includes('boolean') || group.includes(Boolean)));
            
            const newTypeInGroup = group.includes(newType) ||
                (newType === 'number' && (group.includes('number') || group.includes(Number))) ||
                (newType === 'string' && (group.includes('string') || group.includes(String))) ||
                (newType === 'boolean' && (group.includes('boolean') || group.includes(Boolean)));

            if (oldType !== newType && oldTypeInGroup && newTypeInGroup) {
                try {
                    if (oldType === 'string' && String(oldValue) === String(newValue)) {
                        return true;
                    } else if (oldType === 'number' && Number(oldValue) === Number(newValue)) {
                        return true;
                    } else if (typeof oldValue === 'number' && typeof newValue === 'number' && 
                               oldValue === newValue) {
                        return true;
                    } else {
                        // 尝试转换后比较
                        const oldNum = Number(oldValue);
                        const newNum = Number(newValue);
                        if (!isNaN(oldNum) && !isNaN(newNum) && oldNum === newNum) {
                            return true;
                        }
                        return true;
                    }
                } catch (e) {
                    continue;
                }
            }
        }
        return null;
    }

    /**
     * 统一特殊值检查函数
     * @param {*} originVal - Origin值
     * @param {*} currentVal - Current值
     * @param {string} path - 路径
     * @param {Array<string>} differences - 差异列表
     * @returns {Array<string>} 差异列表
     */
    function specialValueCheck(originVal, currentVal, path, differences) {
        // 类型分流检查
        if (typeof originVal === 'string' && typeof currentVal === 'string') {
            // 字符串空值检查
            if (originVal.trim() !== '' && currentVal.trim() === '') {
                differences.push(
                    `[值变化] ${path} ` +
                    `Origin值: '${truncate(originVal, 30)}' → ` +
                    `Current值: '${truncate(currentVal, 30)}' (空值警告)`
                );
            }
        } else if (typeof originVal === 'number' && typeof currentVal === 'number') {
            // 整数值合法性检查
            if (originVal !== currentVal && currentVal <= 0) {
                differences.push(
                    `[值变化] ${path} ` +
                    `Origin值: ${originVal} → ` +
                    `Current值: ${currentVal} (负数/零警告)`
                );
            }
        }

        return differences;
    }

    /**
     * 独立等价判断逻辑
     * 只有当 deepDiffContrastConfig.ignore_type_in_groups 配置了相应类型组时才启用等价值判断
     * @param {*} originVal - Origin值
     * @param {*} currentVal - Current值
     * @param {Object} deepDiffContrastConfig - 对比配置对象
     * @returns {boolean} 是否等价
     */
    function isEquivalentValue(originVal, currentVal, deepDiffContrastConfig) {
        // 如果没有配置 ignore_type_in_groups，则不进行等价值判断
        const typeGroups = (deepDiffContrastConfig && deepDiffContrastConfig.ignore_type_in_groups) || [];
        if (!typeGroups || typeGroups.length === 0) {
            return false;
        }
        
        // 检查类型是否在配置的类型组中
        const originType = typeof originVal;
        const currentType = typeof currentVal;
        
        // 判断两个类型是否在同一个类型组中
        let typesInSameGroup = false;
        for (const group of typeGroups) {
            if (!Array.isArray(group)) {
                continue;
            }
            
            // 将 JavaScript 类型映射到类型组中的类型
            // 支持字符串形式：'number', 'string', 'boolean'
            // 支持构造函数形式：Number, String, Boolean
            const originInGroup = group.includes(originType) || 
                (originType === 'number' && (group.includes('number') || group.some(g => g === Number))) ||
                (originType === 'string' && (group.includes('string') || group.some(g => g === String))) ||
                (originType === 'boolean' && (group.includes('boolean') || group.some(g => g === Boolean)));
            
            const currentInGroup = group.includes(currentType) ||
                (currentType === 'number' && (group.includes('number') || group.some(g => g === Number))) ||
                (currentType === 'string' && (group.includes('string') || group.some(g => g === String))) ||
                (currentType === 'boolean' && (group.includes('boolean') || group.some(g => g === Boolean)));
            
            if (originInGroup && currentInGroup) {
                typesInSameGroup = true;
                break;
            }
        }
        
        // 如果类型不在同一个类型组中，不进行等价值判断
        if (!typesInSameGroup) {
            return false;
        }
        
        // 空字符串与0等价（需要配置了 number 和 string 类型组）
        if ((originVal === '' && currentVal === 0) || (originVal === 0 && currentVal === '')) {
            return true;
        }

        // 数字字符串与数字等价
        if (typeof originVal === 'string' && /^\d+$/.test(originVal) && typeof currentVal === 'number') {
            return parseInt(originVal, 10) === currentVal;
        }
        if (typeof currentVal === 'string' && /^\d+$/.test(currentVal) && typeof originVal === 'number') {
            return parseInt(currentVal, 10) === originVal;
        }

        // 浮点数字符串与数字等价
        if (typeof originVal === 'string' && typeof currentVal === 'number') {
            try {
                const numVal = parseFloat(originVal);
                if (!isNaN(numVal)) {
                    return numVal === currentVal;
                }
            } catch (e) {
                // 忽略转换错误
            }
        }
        if (typeof currentVal === 'string' && typeof originVal === 'number') {
            try {
                const numVal = parseFloat(currentVal);
                if (!isNaN(numVal)) {
                    return numVal === originVal;
                }
            } catch (e) {
                // 忽略转换错误
            }
        }

        // 浮点数与整数等价（值相等时）
        // 在JavaScript中，所有数字都是number类型，但可以通过检查是否为整数来判断
        if (typeof originVal === 'number' && typeof currentVal === 'number') {
            // 如果一个是整数，另一个是浮点数，但值相等，则等价
            if (Number.isInteger(originVal) && !Number.isInteger(currentVal)) {
                return originVal === currentVal;
            }
            if (!Number.isInteger(originVal) && Number.isInteger(currentVal)) {
                return originVal === currentVal;
            }
        }

        return false;
    }

    /**
     * 仅处理类型组配置
     * @param {*} originVal - Origin值
     * @param {*} currentVal - Current值
     * @param {Object} config - 配置对象
     * @returns {boolean} 是否为相同类型
     */
    function isSameType(originVal, currentVal, config) {
        const typeGroups = (config && config.ignore_type_in_groups) || [];
        for (const group of typeGroups) {
            const originType = typeof originVal;
            const currentType = typeof currentVal;
            
            // 检查类型是否在组中
            const originInGroup = group.includes(originType) || 
                (originType === 'number' && (group.includes('number') || group.includes(Number))) ||
                (originType === 'string' && (group.includes('string') || group.includes(String))) ||
                (originType === 'boolean' && (group.includes('boolean') || group.includes(Boolean)));
            
            const currentInGroup = group.includes(currentType) ||
                (currentType === 'number' && (group.includes('number') || group.includes(Number))) ||
                (currentType === 'string' && (group.includes('string') || group.includes(String))) ||
                (currentType === 'boolean' && (group.includes('boolean') || group.includes(Boolean)));

            if (originInGroup && currentInGroup) {
                return true;
            }
        }
        return typeof originVal === typeof currentVal;
    }

    /**
     * 标准化路径格式：将 ['0'] 转换为 [0]
     * @param {string} rawPath - 原始路径
     * @returns {string} 格式化后的路径
     */
    function formatPath(rawPath) {
        return rawPath.replace(/\[\'(\d+)\'\]/g, '[$1]');
    }

    /**
     * 增强类型描述
     * @param {*} obj - 待描述的对象
     * @returns {string} 类型描述字符串
     */
    function typeDetail(obj) {
        if (obj === null || obj === undefined) {
            return 'null';
        }
        if (typeof obj === 'boolean') {
            return 'bool';
        }
        if (typeof obj === 'number') {
            return `${typeof obj}(${obj})`;
        }
        if (typeof obj === 'string') {
            return obj ? `string('${truncate(obj)}')` : 'string(空)';
        }
        if (isArray(obj)) {
            return `array[${obj.length}]`;
        }
        if (isObject(obj)) {
            return `object[${Object.keys(obj).length}]`;
        }
        return typeof obj;
    }

    /**
     * 仅格式化单个值，不修改容器结构
     * @param {*} value - 待格式化的值
     * @returns {string} 格式化后的值字符串
     */
    function formatValue(value) {
        if (typeof value === 'string') {
            if (value === '') {
                return "'' → (等价0)";
            }
            if (/^\d+$/.test(value)) {
                return `'${value}' → (${parseInt(value, 10)})`;
            }
            return `'${value}'`;
        }

        if (typeof value === 'boolean') {
            return String(value).toLowerCase();
        }

        if (typeof value === 'number') {
            return value === 0 ? `${value} → (等价'${value}')` : String(value);
        }

        return String(value);
    }

    /**
     * 安全遍历数据结构并格式化
     * @param {*} data - 待格式化的数据
     * @returns {*} 格式化后的数据
     */
    function formatStructure(data) {
        if (!isDictOrList(data) && typeof data !== 'string' && typeof data !== 'number' && 
            typeof data !== 'boolean' && data !== null && data !== undefined) {
            return String(data); // 处理不可序列化对象
        }
        if (isObject(data)) {
            const result = {};
            for (const key in data) {
                if (data.hasOwnProperty(key)) {
                    result[key] = formatStructure(data[key]);
                }
            }
            return result;
        } else if (isArray(data)) {
            return data.map(e => formatStructure(e));
        } else {
            // 仅叶子节点被格式化
            return formatValue(data);
        }
    }

    /**
     * 字符串截断
     * @param {string} s - 待截断的字符串
     * @param {number} [maxLen=50] - 最大长度
     * @returns {string} 截断后的字符串
     */
    function truncate(s, maxLen = 50) {
        return s.length > maxLen ? s.substring(0, maxLen) + '...' : s;
    }

    // ==================== 主函数逻辑开始 ====================
    let differences = [];
    
    // 设置默认值
    excludeFields = excludeFields || new Set(['go_article_service']);
    // 如果excludeFields是数组，转换为Set
    if (Array.isArray(excludeFields)) {
        excludeFields = new Set(excludeFields);
    }
    
    deepDiffContrastConfig = deepDiffContrastConfig || {
        // 忽略对比列表顺序
        ignore_order: true,
        // 忽略类型不一致
        // ignore_type_in_groups: [['number', 'string', 'boolean']],
    };

    // 深拷贝数据以避免修改原始数据
    const originDataCopy = deepCopy(originData);
    const currentDataCopy = deepCopy(currentData);

    // 判断是否是第一次进入函数
    if (!path) {
        // 检查originData和currentData是否为字典和列表类型
        if (!isDictOrList(originDataCopy) || !isDictOrList(currentDataCopy)) {
            throw new Error('Origin和Current数据必须是字典或列表类型');
        }
    }

    // 处理null值特殊情况
    if (originDataCopy === null && currentDataCopy === null) {
        return differences;
    }
    if (originDataCopy === null) {
        if (checkMissing) {
            differences.push(`[字段缺失] ${path} (Origin类型: null)`);
        }
        return differences;
    }
    if (currentDataCopy === null) {
        if (checkRedundant) {
            differences.push(`[冗余字段] ${path} (Current类型: null)`);
        }
        return differences;
    }

    // 主对比逻辑
    if (isObject(originDataCopy) && isObject(currentDataCopy)) {
        return compareDicts(
            originDataCopy,
            currentDataCopy,
            path,
            checkValue,
            checkMissing,
            checkRedundant,
            checkType,
            excludeFields,
            deepDiffContrastConfig,
            differences,
            openLog
        );
    } else if (isArray(originDataCopy) && isArray(currentDataCopy)) {
        return compareLists(
            originDataCopy,
            currentDataCopy,
            path,
            checkValue,
            checkMissing,
            checkRedundant,
            checkType,
            excludeFields,
            deepDiffContrastConfig,
            differences,
            openLog
        );
    } else {
        // originData和currentData类型不一致
        if (checkType && !isSameType(originDataCopy, currentDataCopy, deepDiffContrastConfig)) {
            differences.push(
                `[类型冲突] ${path} ` +
                `Origin类型: ${typeDetail(originDataCopy)} → ` +
                `Current类型: ${typeDetail(currentDataCopy)}`
            );
        }
    }

    return differences;
}

/**
 * 支持对象参数的包装函数（类似Python的关键字参数）
 * @param {Object|Array} originData - Origin数据
 * @param {Object|Array} currentData - Current数据
 * @param {Object} [options={}] - 选项对象
 * @param {string} [options.path=""] - 当前路径
 * @param {boolean} [options.checkValue=true] - 是否检查值差异
 * @param {boolean} [options.checkMissing=true] - 是否检查缺失字段
 * @param {boolean} [options.checkRedundant=false] - 是否检查冗余字段
 * @param {boolean} [options.checkType=true] - 是否检查类型差异
 * @param {Set<string>|Array<string>|null} [options.excludeFields=null] - 排除字段白名单
 * @param {Object|null} [options.deepDiffContrastConfig=null] - 对比配置参数
 * @param {boolean} [options.openLog=false] - 开启日志
 * @returns {Array<string>} 差异列表
 */
compareStructuresWithOptions = function(originData, currentData, options = {}) {
    return compareStructures(
        originData,
        currentData,
        options.path !== undefined ? options.path : "",
        options.checkValue !== undefined ? options.checkValue : true,
        options.checkMissing !== undefined ? options.checkMissing : true,
        options.checkRedundant !== undefined ? options.checkRedundant : false,
        options.checkType !== undefined ? options.checkType : true,
        options.excludeFields !== undefined ? options.excludeFields : null,
        options.deepDiffContrastConfig !== undefined ? options.deepDiffContrastConfig : null,
        options.openLog !== undefined ? options.openLog : false
    );
}

// 如果是在Node.js环境中，导出函数
if (typeof module !== 'undefined' && module.exports) {
    module.exports = compareStructures;
    module.exports.compareStructuresWithOptions = compareStructuresWithOptions;
}

// 如果是在浏览器环境中，将函数挂载到全局对象
if (typeof window !== 'undefined') {
    window.compareStructures = compareStructures;
    window.compareStructuresWithOptions = compareStructuresWithOptions;
}

// 测试代码
// 如果是在Node.js环境中，使用fs模块读取JSON文件
if (typeof require !== 'undefined') {
    const fs = require('fs');
    const path = require('path');
    
    // 读取JSON文件的辅助函数
    function getJson(filepath, filename) {
        const fullPath = path.join(filepath, filename);
        const content = fs.readFileSync(fullPath, 'utf-8');
        return JSON.parse(content);
    }
    
    // 预期值
    const origin_data = getJson("/Users/cuihaohao/test/parameters/", "php_data.json");
    // 实际值
    const current_data = getJson("/Users/cuihaohao/test/parameters/", "go_data.json");
    
    const exclude_fields = [
        "rows[*].buy_steps[*].sub_rows[*].link",
        "rows[*].buy_steps[*].sub_rows[*].redirect_data.link",
        "rows[*].buy_steps[*].sub_rows[*].redirect_data.link_val",
        "rows[*].buy_steps[*].sub_rows[*].redirect_data.md5_url",
        "rows[*].buy_steps[*].sub_rows[*].redirect_data.sdk_link"
    ];
    
    // 方式1：使用位置参数（需要按顺序传递所有参数）
    // const diffs = compareStructures(
    //     origin_data['data'], 
    //     current_data['data'], 
    //     "", // path
    //     true, // checkValue
    //     true, // checkMissing
    //     false, // checkRedundant
    //     true, // checkType
    //     exclude_fields, // excludeFields
    //     null, // deepDiffContrastConfig
    //     true // openLog
    // );
    
    // 方式2：使用对象参数（类似Python的关键字参数，更灵活）
    const diffs = compareStructuresWithOptions(
        origin_data['data'], 
        current_data['data'], 
        {
            excludeFields: exclude_fields,
            openLog: true,
        }
    );
    
    if (!diffs || diffs.length === 0) {
        console.log("✅ 两次响应结构完全一致");
    } else {
        for (const diff of diffs) {
            console.log(`❌ 发现差异：${diff}`);
        }
    }
}
