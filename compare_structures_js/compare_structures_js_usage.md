# compareStructures.js 使用文档

## 目录

- [简介](#简介)
- [功能特性](#功能特性)
- [API 文档](#api-文档)
- [基础用法](#基础用法)
- [高级用法](#高级用法)
- [配置选项](#配置选项)
- [使用示例](#使用示例)
- [常见场景](#常见场景)

---

## 简介

`compareStructures` 是一个强大的 JavaScript 数据结构对比工具，用于深度比较两个对象或数组的差异。它能够识别字段缺失、类型不一致、值变化等多种差异，并支持灵活的配置选项。

**作者**: 崔浩浩

---

## 功能特性

### 核心功能

1. **字段缺失检测**: 检测 `currentData` 相比 `originData` 缺失的字段（包括嵌套结构）
2. **类型冲突检测**: 检测相同字段的类型不一致
3. **列表结构差异**: 检测列表长度、元素类型的差异
4. **值变化检测**: 检测字段值的变化
5. **排除字段**: 支持白名单机制，跳过指定字段的检查

### 高级特性

1. **深度递归对比**: 自动递归对比嵌套的对象和数组
2. **列表顺序控制**: 支持有序列表（按索引）和无序列表（忽略顺序）两种对比模式
3. **类型组配置**: 支持配置类型组，允许特定类型之间的转换
4. **路径匹配**: 支持嵌套路径和通配符匹配（如 `rows[*].buy_steps[*].link`）
5. **日志输出**: 支持开启详细日志，便于调试

---

## API 文档

### compareStructures

主函数，使用位置参数调用。

```javascript
compareStructures(
    originData,              // 原始数据（对象或数组）
    currentData,             // 当前数据（对象或数组）
    path = "",               // 当前路径（递归用，通常为空字符串）
    checkValue = true,       // 是否检查值差异
    checkMissing = true,     // 是否检查缺失字段
    checkRedundant = false,  // 是否检查冗余字段
    checkType = true,        // 是否检查类型差异
    excludeFields = null,    // 排除字段白名单（Set 或 Array）
    deepDiffContrastConfig = null,  // 对比配置对象
    openLog = false          // 是否开启日志（使用 console.log 输出）
)
```

**返回值**: `Array<string>` - 差异列表，每个元素是一个描述差异的字符串

### compareStructuresWithOptions

包装函数，使用对象参数调用（推荐使用）。

```javascript
compareStructuresWithOptions(
    originData,    // 原始数据
    currentData,   // 当前数据
    options = {}   // 选项对象
)
```

**选项对象 (options)**:

```javascript
{
    path: "",                    // 当前路径
    checkValue: true,            // 是否检查值差异
    checkMissing: true,           // 是否检查缺失字段
    checkRedundant: false,        // 是否检查冗余字段
    checkType: true,              // 是否检查类型差异
    excludeFields: null,          // 排除字段白名单
    deepDiffContrastConfig: null, // 对比配置对象
    openLog: false                // 是否开启日志（使用 console.log 输出）
}
```

---

## 基础用法

### 示例 1: 简单对象对比

```javascript
const origin = { name: "张三", age: 25, city: "北京" };
const current = { name: "张三", age: 26, city: "北京" };

const diffs = compareStructuresWithOptions(origin, current);

if (diffs.length === 0) {
    console.log("✅ 数据完全一致");
} else {
    diffs.forEach(diff => console.log(diff));
}
// 输出: [值变化] age Origin值: 25 → Current值: 26
```

### 示例 2: 检测缺失字段

```javascript
const origin = { name: "张三", age: 25, email: "zhang@example.com" };
const current = { name: "张三", age: 25 };

const diffs = compareStructuresWithOptions(origin, current);

// 输出: [字段缺失] email (Origin类型: string('zhang@example.com'))
```

### 示例 3: 检测类型冲突

```javascript
const origin = { count: 100 };
const current = { count: "100" };

const diffs = compareStructuresWithOptions(origin, current, {
    checkType: true
});

// 输出: [类型冲突] count Origin类型: number(100) → Current类型: string('100')
```

### 示例 4: 检测冗余字段

```javascript
const origin = { name: "张三", age: 25 };
const current = { name: "张三", age: 25, email: "zhang@example.com" };

const diffs = compareStructuresWithOptions(origin, current, {
    checkRedundant: true
});

// 输出: [冗余字段] email (Current类型: string('zhang@example.com'))
```

---

## 高级用法

### 示例 5: 排除特定字段

```javascript
const origin = {
    name: "张三",
    timestamp: 1234567890,
    data: { value: 100 }
};
const current = {
    name: "李四",
    timestamp: 1234567891,
    data: { value: 100 }
};

// 排除 timestamp 字段
const diffs = compareStructuresWithOptions(origin, current, {
    excludeFields: ["timestamp"]
});

// 只输出 name 字段的差异，timestamp 被忽略
// 输出: [值变化] name Origin值: '张三' → Current值: '李四'
```

### 示例 6: 排除嵌套字段

```javascript
const origin = {
    user: {
        name: "张三",
        profile: {
            avatar: "avatar1.jpg",
            settings: { theme: "dark" }
        }
    }
};
const current = {
    user: {
        name: "张三",
        profile: {
            avatar: "avatar2.jpg",
            settings: { theme: "light" }
        }
    }
};

// 排除整个 profile 字段及其子字段
const diffs = compareStructuresWithOptions(origin, current, {
    excludeFields: ["user.profile"]
});

// profile 及其所有子字段都不会被检查
```

### 示例 7: 使用通配符排除列表字段

```javascript
const origin = {
    rows: [
        { id: 1, link: "http://example.com/1", title: "标题1" },
        { id: 2, link: "http://example.com/2", title: "标题2" }
    ]
};
const current = {
    rows: [
        { id: 1, link: "http://example.com/1-new", title: "标题1" },
        { id: 2, link: "http://example.com/2-new", title: "标题2" }
    ]
};

// 排除所有 rows 中的 link 字段
const diffs = compareStructuresWithOptions(origin, current, {
    excludeFields: ["rows[*].link"]
});

// link 字段的差异会被忽略，只检查其他字段
```

### 示例 8: 有序列表对比（按索引）

```javascript
const origin = {
    items: [
        { id: 1, name: "第一项" },
        { id: 2, name: "第二项" }
    ]
};
const current = {
    items: [
        { id: 2, name: "第二项" },
        { id: 1, name: "第一项" }
    ]
};

// 按索引对比：origin[0] vs current[0], origin[1] vs current[1]
const diffs = compareStructuresWithOptions(origin, current, {
    deepDiffContrastConfig: {
        ignore_order: false  // 设置为 false，按索引直接对比
    }
});

// 会检测到差异，因为索引 0 和 1 的元素不同
```

### 示例 9: 无序列表对比（忽略顺序）

```javascript
const origin = {
    tags: ["tag1", "tag2", "tag3"]
};
const current = {
    tags: ["tag3", "tag1", "tag2"]
};

// 忽略顺序对比：会尝试匹配相同的元素
const diffs = compareStructuresWithOptions(origin, current, {
    deepDiffContrastConfig: {
        ignore_order: true  // 默认值，忽略顺序
    }
});

// 不会检测到差异，因为元素相同，只是顺序不同
```

### 示例 10: 复杂嵌套结构对比

```javascript
const origin = {
    users: [
        {
            id: 1,
            name: "张三",
            orders: [
                { orderId: "001", amount: 100 },
                { orderId: "002", amount: 200 }
            ]
        }
    ]
};
const current = {
    users: [
        {
            id: 1,
            name: "张三",
            orders: [
                { orderId: "001", amount: 150 },
                { orderId: "002", amount: 200 }
            ]
        }
    ]
};

const diffs = compareStructuresWithOptions(origin, current);

// 会递归对比所有嵌套字段
// 输出: [值变化] users[0].orders[0].amount Origin值: 100 → Current值: 150
```

### 示例 11: 类型组配置（允许类型转换和等价值判断）

```javascript
const origin = { count: "100" };
const current = { count: 100 };

// 配置类型组，允许 number 和 string 之间的转换和等价值判断
const diffs = compareStructuresWithOptions(origin, current, {
    deepDiffContrastConfig: {
        ignore_type_in_groups: [['number', 'string']]
    }
});

// 配置后，会启用等价值判断：
// 1. 如果值相同（如 "100" 和 100），会被识别为等价值，不会报告差异
// 2. 如果值不同（如 "100" 和 200），会报告值变化
// 3. 如果没有配置 ignore_type_in_groups，会报告类型冲突
```

### 示例 12: 开启日志调试

```javascript
const origin = { items: [1, 2, 3] };
const current = { items: [3, 1, 2] };

const diffs = compareStructuresWithOptions(origin, current, {
    openLog: true,  // 开启日志
    deepDiffContrastConfig: {
        ignore_order: true
    }
});

// 会输出详细的对比过程日志
// _compare_lists_native_path:items
// _compare_lists_native_origin_len:3
// _compare_lists_native_current_len:3
```

### 示例 13: 等价值判断（空字符串与0）

```javascript
const origin = { value: "" };
const current = { value: 0 };

// 需要配置 ignore_type_in_groups 才能启用等价值判断
const diffs = compareStructuresWithOptions(origin, current, {
    deepDiffContrastConfig: {
        ignore_type_in_groups: [['number', 'string']]
    }
});

// 空字符串和0被识别为等价值，不会报告差异
// 输出: 无差异（数据完全一致）
```

**注意**: 如果没有配置 `ignore_type_in_groups`，会报告类型冲突：
```javascript
const diffs = compareStructuresWithOptions(origin, current);
// 输出: [类型冲突] value Origin类型: string(空) → Current类型: number(0)
```

### 示例 14: 等价值判断（数字字符串与数字）

```javascript
const origin = { count: "100" };
const current = { count: 100 };

// 需要配置 ignore_type_in_groups 才能启用等价值判断
const diffs = compareStructuresWithOptions(origin, current, {
    deepDiffContrastConfig: {
        ignore_type_in_groups: [['number', 'string']]
    }
});

// 数字字符串"100"和数字100被识别为等价值，不会报告差异
// 输出: 无差异（数据完全一致）
```

### 示例 15: 等价值判断（浮点数字符串与数字）

```javascript
const origin = { price: "100.5" };
const current = { price: 100.5 };

// 需要配置 ignore_type_in_groups 才能启用等价值判断
const diffs = compareStructuresWithOptions(origin, current, {
    deepDiffContrastConfig: {
        ignore_type_in_groups: [['number', 'string']]
    }
});

// 浮点数字符串"100.5"和数字100.5被识别为等价值，不会报告差异
// 输出: 无差异（数据完全一致）
```

### 示例 16: 等价值判断（浮点数与整数）

```javascript
const origin = { value: 100.0 };
const current = { value: 100 };

// 需要配置 ignore_type_in_groups 才能启用等价值判断
// 对于浮点数和整数，只需要配置 number 类型组
const diffs = compareStructuresWithOptions(origin, current, {
    deepDiffContrastConfig: {
        ignore_type_in_groups: [['number']]
    }
});

// 浮点数100.0和整数100被识别为等价值，不会报告差异
// 输出: 无差异（数据完全一致）
```

### 示例 17: 复杂嵌套列表对比（忽略顺序）

```javascript
const origin = {
    users: [
        {
            id: 1,
            name: "张三",
            orders: [
                { orderId: "001", amount: 100 },
                { orderId: "002", amount: 200 }
            ]
        },
        {
            id: 2,
            name: "李四",
            orders: [
                { orderId: "003", amount: 300 }
            ]
        }
    ]
};
const current = {
    users: [
        {
            id: 2,
            name: "李四",
            orders: [
                { orderId: "003", amount: 300 }
            ]
        },
        {
            id: 1,
            name: "张三",
            orders: [
                { orderId: "002", amount: 200 },
                { orderId: "001", amount: 150 }  // amount 变化
            ]
        }
    ]
};

// 使用忽略顺序模式，会匹配相同id的用户，然后递归对比内部字段
const diffs = compareStructuresWithOptions(origin, current, {
    deepDiffContrastConfig: {
        ignore_order: true  // 忽略用户列表和订单列表的顺序
    }
});

// 会检测到 orders[0].amount 的变化
// 输出: [值变化] users[0].orders[0].amount Origin值: 100 → Current值: 150
```

### 示例 18: 使用真实JSON数据对比

```javascript
const fs = require('fs');
const path = require('path');

// 读取JSON文件
function getJson(filepath, filename) {
    const fullPath = path.join(filepath, filename);
    const content = fs.readFileSync(fullPath, 'utf-8');
    return JSON.parse(content);
}

// 读取真实数据
const phpData = getJson("/Users/cuihaohao/test/parameters/", "php_data.json");
const goData = getJson("/Users/cuihaohao/test/parameters/", "go_data.json");

// 对比data字段，排除链接相关字段
const diffs = compareStructuresWithOptions(
    phpData.data,
    goData.data,
    {
        excludeFields: [
            "rows[*].buy_steps[*].sub_rows[*].link",
            "rows[*].buy_steps[*].sub_rows[*].redirect_data.link",
            "rows[*].buy_steps[*].sub_rows[*].redirect_data.link_val",
            "rows[*].buy_steps[*].sub_rows[*].redirect_data.md5_url",
            "rows[*].buy_steps[*].sub_rows[*].redirect_data.sdk_link"
        ],
        openLog: false
    }
);

if (diffs.length === 0) {
    console.log("✅ 真实数据对比：排除链接字段后数据完全一致");
} else {
    console.log(`⚠️  真实数据对比：发现 ${diffs.length} 处差异（排除链接字段后）`);
    diffs.slice(0, 5).forEach((diff, i) => {
        console.log(`  ${i + 1}. ${diff}`);
    });
    if (diffs.length > 5) {
        console.log(`  ... 还有 ${diffs.length - 5} 处差异未显示`);
    }
}
```

---

## 配置选项

### deepDiffContrastConfig 配置对象

```javascript
{
    // 是否忽略列表顺序
    // true: 无序列表，会尝试匹配相同元素（默认）
    // false: 有序列表，按索引直接对比
    ignore_order: true,

    // 类型组配置，允许组内类型之间的转换和等价值判断
    // 例如: [['number', 'string']] 表示 number 和 string 可以互相转换
    // 重要：只有配置了 ignore_type_in_groups 后，等价值判断才会生效
    // 等价值判断包括：空字符串与0、数字字符串与数字、浮点数字符串与数字、浮点数与整数
    ignore_type_in_groups: [
        ['number', 'string', 'boolean']
    ]
}
```

### 等价值判断规则

函数内置了等价值判断逻辑，但**需要配置 `ignore_type_in_groups` 才能启用**。以下情况在配置相应类型组后会被识别为等价值（不会报告差异）：

1. **空字符串与0等价**
   - `""` 和 `0` 等价（需要配置 `[['number', 'string']]`）
   - `0` 和 `""` 等价

2. **数字字符串与整数等价**
   - `"100"` 和 `100` 等价（需要配置 `[['number', 'string']]`）
   - `100` 和 `"100"` 等价

3. **浮点数字符串与数字等价**
   - `"100.5"` 和 `100.5` 等价（需要配置 `[['number', 'string']]`）
   - `100.5` 和 `"100.5"` 等价

4. **浮点数与整数等价（值相等时）**
   - `100.0` 和 `100` 等价（需要配置 `[['number']]`）
   - `100` 和 `100.0` 等价

**重要说明**:
- **等价值判断仅在配置了 `ignore_type_in_groups` 时生效**
- 如果未配置 `ignore_type_in_groups`，等价值判断不会执行，会按正常类型和值对比
- 等价值判断优先于类型检查，如果两个值等价，不会报告类型冲突或值变化
- 只有当两个值的类型都在配置的同一类型组中时，才会进行等价值判断

### excludeFields 排除字段

支持多种格式：

1. **简单字段**: `"timestamp"` - 排除根级别的 timestamp 字段
2. **嵌套字段**: `"user.profile"` - 排除 user.profile 及其所有子字段
3. **列表字段**: `"items[*].id"` - 排除所有 items 元素中的 id 字段
4. **深层嵌套**: `"rows[*].buy_steps[*].sub_rows[*].link"` - 排除深层嵌套的 link 字段

**示例**:

```javascript
const excludeFields = [
    "timestamp",                           // 排除根级别字段
    "user.profile",                        // 排除嵌套字段
    "items[*].id",                         // 排除列表字段
    "rows[*].buy_steps[*].sub_rows[*].link" // 排除深层嵌套字段
];
```

---

## 使用示例

### 场景 1: API 响应对比

```javascript
// 对比两个 API 响应的差异
const originResponse = {
    code: 200,
    data: {
        users: [
            { id: 1, name: "张三", email: "zhang@example.com" },
            { id: 2, name: "李四", email: "li@example.com" }
        ],
        total: 2
    },
    timestamp: 1234567890
};

const currentResponse = {
    code: 200,
    data: {
        users: [
            { id: 1, name: "张三", email: "zhang@example.com" },
            { id: 2, name: "李四", email: "li@example.com" }
        ],
        total: 2
    },
    timestamp: 1234567891  // 时间戳不同
};

const diffs = compareStructuresWithOptions(
    originResponse,
    currentResponse,
    {
        excludeFields: ["timestamp"],  // 排除时间戳
        openLog: false
    }
);

if (diffs.length === 0) {
    console.log("✅ API 响应结构完全一致");
} else {
    console.log("❌ 发现差异:");
    diffs.forEach(diff => console.log(`  - ${diff}`));
}
```

### 场景 2: 配置文件对比

```javascript
const oldConfig = {
    database: {
        host: "localhost",
        port: 3306,
        name: "mydb"
    },
    cache: {
        enabled: true,
        ttl: 3600
    }
};

const newConfig = {
    database: {
        host: "localhost",
        port: 3306,
        name: "mydb",
        pool: { max: 10 }  // 新增配置
    },
    cache: {
        enabled: true,
        ttl: 7200  // 值变化
    }
};

const diffs = compareStructuresWithOptions(oldConfig, newConfig, {
    checkRedundant: true  // 检查新增字段
});

// 输出:
// [冗余字段] database.pool (Current类型: object[1])
// [值变化] cache.ttl Origin值: 3600 → Current值: 7200
```

### 场景 3: 数据迁移验证

```javascript
// 验证数据迁移前后的差异
const beforeMigration = {
    users: [
        { id: 1, name: "张三", oldField: "value1" },
        { id: 2, name: "李四", oldField: "value2" }
    ]
};

const afterMigration = {
    users: [
        { id: 1, name: "张三", newField: "value1" },
        { id: 2, name: "李四", newField: "value2" }
    ]
};

const diffs = compareStructuresWithOptions(beforeMigration, afterMigration, {
    excludeFields: ["users[*].oldField", "users[*].newField"],  // 排除迁移字段
    deepDiffContrastConfig: {
        ignore_order: true  // 用户列表顺序可能变化
    }
});

// 只检查核心字段（id, name）是否一致
```

### 场景 4: 测试数据对比

```javascript
// 对比测试用例的预期结果和实际结果
const expected = {
    status: "success",
    data: {
        items: [
            { id: 1, price: 100 },
            { id: 2, price: 200 }
        ]
    }
};

const actual = {
    status: "success",
    data: {
        items: [
            { id: 1, price: 100 },
            { id: 2, price: 200 }
        ]
    }
};

const diffs = compareStructuresWithOptions(expected, actual, {
    openLog: true  // 开启日志便于调试
});

if (diffs.length === 0) {
    console.log("✅ 测试通过");
} else {
    console.log("❌ 测试失败，发现差异:");
    diffs.forEach(diff => console.log(`  - ${diff}`));
}
```

### 场景 5: 等价值处理场景

```javascript
// 场景：API返回的数据中，某些字段可能是字符串或数字
// 例如：价格可能是 "100" 或 100，需要识别为相同

const origin = {
    product: {
        id: 1,
        price: "100",      // 字符串格式
        stock: 0,          // 数字格式
        discount: ""       // 空字符串
    }
};

const current = {
    product: {
        id: 1,
        price: 100,         // 数字格式（等价值）
        stock: "",          // 空字符串（等价值）
        discount: 0         // 数字0（等价值）
    }
};

// 需要配置 ignore_type_in_groups 才能启用等价值判断
const diffs = compareStructuresWithOptions(origin, current, {
    deepDiffContrastConfig: {
        ignore_type_in_groups: [['number', 'string']]
    }
});

// 由于等价值判断，这些字段不会报告差异
// 输出: 无差异（数据完全一致）
```

### 场景 6: 浮点数精度处理

```javascript
// 场景：处理浮点数和整数的等价判断
const origin = {
    metrics: {
        total: 100.0,       // 浮点数
        average: "99.5",   // 浮点数字符串
        count: 50           // 整数
    }
};

const current = {
    metrics: {
        total: 100,         // 整数（与100.0等价）
        average: 99.5,      // 浮点数（与"99.5"等价）
        count: 50.0         // 浮点数（与50等价）
    }
};

// 需要配置 ignore_type_in_groups 才能启用等价值判断
// 配置 number 和 string 类型组，支持浮点数/整数和字符串之间的等价判断
const diffs = compareStructuresWithOptions(origin, current, {
    deepDiffContrastConfig: {
        ignore_type_in_groups: [['number', 'string']]
    }
});

// 所有字段都被识别为等价值
// 输出: 无差异（数据完全一致）
```

### 场景 7: 复杂业务数据对比

```javascript
// 场景：对比电商订单数据，排除动态字段
const originOrder = {
    orderId: "ORD001",
    userId: 12345,
    items: [
        {
            productId: "P001",
            quantity: 2,
            price: "99.99",  // 字符串格式价格
            link: "http://example.com/p001"
        },
        {
            productId: "P002",
            quantity: 1,
            price: "199.99",
            link: "http://example.com/p002"
        }
    ],
    total: "299.97",
    timestamp: 1234567890,
    tracking: {
        link: "http://tracking.com/ORD001",
        code: "TRACK123"
    }
};

const currentOrder = {
    orderId: "ORD001",
    userId: 12345,
    items: [
        {
            productId: "P002",
            quantity: 1,
            price: 199.99,    // 数字格式价格（等价值）
            link: "http://example.com/p002-new"  // 链接变化
        },
        {
            productId: "P001",
            quantity: 2,
            price: 99.99,    // 数字格式价格（等价值）
            link: "http://example.com/p001-new"  // 链接变化
        }
    ],
    total: 299.97,           // 数字格式（等价值）
    timestamp: 1234567891,   // 时间戳变化
    tracking: {
        link: "http://tracking.com/ORD001-new",  // 链接变化
        code: "TRACK123"
    }
};

// 排除动态字段：链接和时间戳
// 配置类型组以启用等价值判断（价格字段可能是字符串或数字）
const diffs = compareStructuresWithOptions(originOrder, currentOrder, {
    excludeFields: [
        "items[*].link",
        "timestamp",
        "tracking.link"
    ],
    deepDiffContrastConfig: {
        ignore_order: true,  // 忽略商品列表顺序
        ignore_type_in_groups: [['number', 'string']]  // 启用等价值判断
    }
});

// 由于等价值判断和排除字段，只会检查核心业务字段
// 价格字段 "99.99" 和 99.99 会被识别为等价值
// 输出: 无差异（数据完全一致）
```

## 常见场景

### 1. 只检查结构，不检查值

```javascript
const diffs = compareStructuresWithOptions(origin, current, {
    checkValue: false,  // 不检查值差异
    checkType: true,    // 仍然检查类型
    checkMissing: true  // 仍然检查缺失字段
});
```

### 2. 只检查值，不检查类型

```javascript
const diffs = compareStructuresWithOptions(origin, current, {
    checkValue: true,   // 检查值差异
    checkType: false    // 不检查类型差异
});
```

### 3. 完全对比（包括冗余字段）

```javascript
const diffs = compareStructuresWithOptions(origin, current, {
    checkValue: true,
    checkMissing: true,
    checkRedundant: true,  // 检查冗余字段
    checkType: true
});
```

### 4. 在 Node.js 中使用

```javascript
const fs = require('fs');
const path = require('path');

// 读取 JSON 文件
function getJson(filepath, filename) {
    const fullPath = path.join(filepath, filename);
    const content = fs.readFileSync(fullPath, 'utf-8');
    return JSON.parse(content);
}

// 对比两个 JSON 文件
const originData = getJson("./data/", "origin.json");
const currentData = getJson("./data/", "current.json");

const diffs = compareStructuresWithOptions(originData, currentData, {
    excludeFields: ["timestamp", "updated_at"],
    openLog: true
});

if (diffs.length === 0) {
    console.log("✅ 数据完全一致");
} else {
    console.log(`❌ 发现 ${diffs.length} 处差异:`);
    diffs.forEach(diff => console.log(`  - ${diff}`));
}
```

### 5. 在浏览器中使用

```html
<!DOCTYPE html>
<html>
<head>
    <title>数据对比工具</title>
    <script src="compare_structures_js.js"></script>
</head>
<body>
    <script>
        const origin = { name: "张三", age: 25 };
        const current = { name: "李四", age: 25 };
        
        const diffs = window.compareStructuresWithOptions(origin, current);
        
        if (diffs.length === 0) {
            console.log("✅ 数据完全一致");
        } else {
            console.log("❌ 发现差异:");
            diffs.forEach(diff => console.log(diff));
        }
    </script>
</body>
</html>
```

---

## 差异输出格式

函数返回的差异字符串格式如下：

### 字段缺失
```
[字段缺失] path (Origin类型: typeDetail)
```

### 类型冲突
```
[类型冲突] path Origin类型: typeDetail → Current类型: typeDetail
```

### 值变化
```
[值变化] path Origin值: formattedValue → Current值: formattedValue
```

### 列表差异
```
[列表差异] path[index] (iterable_item_removed)
[列表差异] path[index] (iterable_item_added)
```

### 冗余字段
```
[冗余字段] path (Current类型: typeDetail)
```

---

## 注意事项

1. **性能考虑**: 对于大型数据结构，建议使用 `excludeFields` 排除不需要检查的字段
2. **内存使用**: 函数会深拷贝输入数据，对于非常大的对象可能消耗较多内存
3. **类型检查**: 默认会检查类型，如果数据中数字和字符串可以互换，建议配置 `ignore_type_in_groups`
4. **等价值判断**: 等价值判断（空字符串与0、数字字符串与数字等）仅在配置了 `ignore_type_in_groups` 时生效。如果未配置，会按正常类型和值对比
5. **列表顺序**: 默认忽略列表顺序，如果需要按索引对比，设置 `ignore_order: false`
6. **路径格式**: 排除字段的路径使用点号分隔，列表使用 `[*]` 通配符

---

## 版本信息

- **版本**: 1.0.0
- **作者**: 崔浩浩
- **语言**: JavaScript (ES5+)
- **环境**: Node.js / 浏览器


