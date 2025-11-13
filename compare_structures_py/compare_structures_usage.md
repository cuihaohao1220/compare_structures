# compare_structures.py 使用文档

## 目录

- [简介](#简介)
- [功能特性](#功能特性)
- [API 文档](#api-文档)
- [基础用法](#基础用法)
- [高级用法](#高级用法)
- [配置选项](#配置选项)
- [使用示例](#使用示例)
- [常见场景](#常见场景)
- [注意事项](#注意事项)

---

## 简介

`compare_structures` 是一个强大的 Python 数据结构对比工具，用于深度比较两个对象或数组的差异。它能够识别字段缺失、类型不一致、值变化等多种差异，并支持灵活的配置选项。

**作者**: 崔浩浩

**版本**: 优化后，等价值判断需配置版本

---

## 功能特性

### 核心功能

1. **字段缺失检测**: 检测 `current_data` 相比 `origin_data` 缺失的字段（包括嵌套结构）
2. **类型冲突检测**: 检测相同字段的类型不一致
3. **列表结构差异**: 检测列表长度、元素类型的差异
4. **值变化检测**: 检测字段值的变化
5. **排除字段**: 支持白名单机制，跳过指定字段的检查

### 高级特性

1. **深度递归对比**: 自动递归对比嵌套的对象和数组
2. **列表顺序控制**: 支持有序列表（按索引）和无序列表（忽略顺序）两种对比模式
3. **类型组配置**: 支持配置类型组，允许特定类型之间的转换和等价值判断
4. **路径匹配**: 支持嵌套路径和通配符匹配（如 `rows[*].buy_steps[*].link`）
5. **日志输出**: 支持开启详细日志，便于调试
6. **等价值判断**: 支持空字符串与0、数字字符串与数字、浮点数与整数等等价判断（需配置）

---

## API 文档

### compare_structures

主函数，用于对比两个数据结构。

```python
compare_structures(
    origin_data: Union[Dict, List],           # 原始数据（字典或列表）
    current_data: Union[Dict, List],           # 当前数据（字典或列表）
    path: str = "",                           # 当前路径（递归用，通常为空字符串）
    check_value: bool = True,                 # 是否检查值差异
    check_missing: bool = True,               # 是否检查缺失字段
    check_redundant: bool = False,            # 是否检查冗余字段
    check_type: bool = True,                  # 是否检查类型差异
    exclude_fields: Set[str] = None,          # 排除字段白名单（集合或列表）
    deep_diff_contrast_config: Dict = None,  # 对比配置对象
    open_log: bool = False                    # 是否开启日志（使用 logzero.logger 输出）
) -> List[str]
```

**参数说明**:

- **origin_data** (必需): 原始数据，可以是字典或列表
- **current_data** (必需): 当前数据，可以是字典或列表
- **path** (可选): 当前路径，用于递归调用，通常为空字符串
- **check_value** (可选): 是否检查值差异，默认为 `True`
- **check_missing** (可选): 是否检查缺失字段，默认为 `True`
- **check_redundant** (可选): 是否检查冗余字段，默认为 `False`
- **check_type** (可选): 是否检查类型差异，默认为 `True`
- **exclude_fields** (可选): 排除字段白名单，可以是集合或列表，默认为 `{"go_article_service"}`
- **deep_diff_contrast_config** (可选): 对比配置对象，包含列表顺序、类型组等配置
- **open_log** (可选): 是否开启日志，默认为 `False`

**返回值**: `List[str]` - 差异列表，每个元素是一个描述差异的字符串

**差异格式**:
- `[字段缺失] path (Origin类型: typeDetail)`
- `[类型冲突] path Origin类型: typeDetail → Current类型: typeDetail`
- `[值变化] path Origin值: formattedValue → Current值: formattedValue`
- `[列表差异] path[index] (iterable_item_removed)` 或 `(iterable_item_added)`
- `[冗余字段] path (Current类型: typeDetail)`

---

## 基础用法

### 示例 1: 简单对象对比

```python
from compare_structures import compare_structures

origin = {"name": "张三", "age": 25, "city": "北京"}
current = {"name": "张三", "age": 26, "city": "北京"}

diffs = compare_structures(origin, current)

if not diffs:
    print("✅ 数据完全一致")
else:
    for diff in diffs:
        print(diff)
# 输出: [值变化] age Origin值: 25 → Current值: 26
```

### 示例 2: 检测缺失字段

```python
origin = {"name": "张三", "age": 25, "email": "zhang@example.com"}
current = {"name": "张三", "age": 25}

diffs = compare_structures(origin, current)

# 输出: [字段缺失] email (Origin类型: str('zhang@example.com'))
```

### 示例 3: 检测类型冲突

```python
origin = {"count": 100}
current = {"count": "100"}

diffs = compare_structures(origin, current, check_type=True)

# 输出: [类型冲突] count Origin类型: int(100) → Current类型: str('100')
```

### 示例 4: 检测冗余字段

```python
origin = {"name": "张三", "age": 25}
current = {"name": "张三", "age": 25, "email": "zhang@example.com"}

diffs = compare_structures(origin, current, check_redundant=True)

# 输出: [冗余字段] email (Current类型: str('zhang@example.com'))
```

---

## 高级用法

### 示例 5: 排除特定字段

```python
origin = {
    "name": "张三",
    "timestamp": 1234567890,
    "data": {"value": 100}
}
current = {
    "name": "李四",
    "timestamp": 1234567891,
    "data": {"value": 100}
}

# 排除 timestamp 字段
diffs = compare_structures(
    origin, 
    current, 
    exclude_fields={"timestamp"}
)

# 只输出 name 字段的差异，timestamp 被忽略
# 输出: [值变化] name Origin值: '张三' → Current值: '李四'
```

### 示例 6: 排除嵌套字段

```python
origin = {
    "user": {
        "name": "张三",
        "profile": {
            "avatar": "avatar1.jpg",
            "settings": {"theme": "dark"}
        }
    }
}
current = {
    "user": {
        "name": "张三",
        "profile": {
            "avatar": "avatar2.jpg",
            "settings": {"theme": "light"}
        }
    }
}

# 排除整个 profile 字段及其子字段
diffs = compare_structures(
    origin, 
    current, 
    exclude_fields={"user.profile"}
)

# profile 及其所有子字段都不会被检查
```

### 示例 7: 使用通配符排除列表字段

```python
origin = {
    "rows": [
        {"id": 1, "link": "http://example.com/1", "title": "标题1"},
        {"id": 2, "link": "http://example.com/2", "title": "标题2"}
    ]
}
current = {
    "rows": [
        {"id": 1, "link": "http://example.com/1-new", "title": "标题1"},
        {"id": 2, "link": "http://example.com/2-new", "title": "标题2"}
    ]
}

# 排除所有 rows 中的 link 字段
diffs = compare_structures(
    origin, 
    current, 
    exclude_fields={"rows[*].link"}
)

# link 字段的差异会被忽略，只检查其他字段
```

### 示例 8: 有序列表对比（按索引）

```python
origin = {
    "items": [
        {"id": 1, "name": "第一项"},
        {"id": 2, "name": "第二项"}
    ]
}
current = {
    "items": [
        {"id": 2, "name": "第二项"},
        {"id": 1, "name": "第一项"}
    ]
}

# 按索引对比：origin[0] vs current[0], origin[1] vs current[1]
diffs = compare_structures(
    origin, 
    current, 
    deep_diff_contrast_config={"ignore_order": False}  # 设置为 False，按索引直接对比
)

# 会检测到差异，因为索引 0 和 1 的元素不同
```

### 示例 9: 无序列表对比（忽略顺序）

```python
origin = {
    "tags": ["tag1", "tag2", "tag3"]
}
current = {
    "tags": ["tag3", "tag1", "tag2"]
}

# 忽略顺序对比：会尝试匹配相同的元素
diffs = compare_structures(
    origin, 
    current, 
    deep_diff_contrast_config={"ignore_order": True}  # 默认值，忽略顺序
)

# 不会检测到差异，因为元素相同，只是顺序不同
```

### 示例 10: 复杂嵌套结构对比

```python
origin = {
    "users": [
        {
            "id": 1,
            "name": "张三",
            "orders": [
                {"orderId": "001", "amount": 100},
                {"orderId": "002", "amount": 200}
            ]
        }
    ]
}
current = {
    "users": [
        {
            "id": 1,
            "name": "张三",
            "orders": [
                {"orderId": "001", "amount": 150},
                {"orderId": "002", "amount": 200}
            ]
        }
    ]
}

diffs = compare_structures(origin, current)

# 会递归对比所有嵌套字段
# 输出: [值变化] users[0].orders[0].amount Origin值: 100 → Current值: 150
```

### 示例 11: 类型组配置（允许类型转换和等价值判断）

```python
origin = {"count": "100"}
current = {"count": 100}

# 配置类型组，允许 number 和 string 之间的转换和等价值判断
diffs = compare_structures(
    origin, 
    current, 
    deep_diff_contrast_config={
        "ignore_type_in_groups": [(int, str)]
    }
)

# 配置后，会启用等价值判断：
# 1. 如果值相同（如 "100" 和 100），会被识别为等价值，不会报告差异
# 2. 如果值不同（如 "100" 和 200），会报告值变化
# 3. 如果没有配置 ignore_type_in_groups，会报告类型冲突
```

### 示例 12: 开启日志调试

```python
origin = {"items": [1, 2, 3]}
current = {"items": [3, 1, 2]}

diffs = compare_structures(
    origin, 
    current, 
    open_log=True,  # 开启日志
    deep_diff_contrast_config={
        "ignore_order": True
    }
)

# 会输出详细的对比过程日志
# _compare_lists_native: path=items, origin_len=3, current_len=3
```

### 示例 13: 等价值判断（空字符串与0）

```python
origin = {"value": ""}
current = {"value": 0}

# 需要配置 ignore_type_in_groups 才能启用等价值判断
diffs = compare_structures(
    origin, 
    current, 
    deep_diff_contrast_config={
        "ignore_type_in_groups": [(int, str)]
    }
)

# 空字符串和0被识别为等价值，不会报告差异
# 输出: 无差异（数据完全一致）
```

**注意**: 如果没有配置 `ignore_type_in_groups`，会报告类型冲突：
```python
diffs = compare_structures(origin, current)
# 输出: [类型冲突] value Origin类型: str(空) → Current类型: int(0)
```

### 示例 14: 等价值判断（数字字符串与数字）

```python
origin = {"count": "100"}
current = {"count": 100}

# 需要配置 ignore_type_in_groups 才能启用等价值判断
diffs = compare_structures(
    origin, 
    current, 
    deep_diff_contrast_config={
        "ignore_type_in_groups": [(int, str)]
    }
)

# 数字字符串"100"和数字100被识别为等价值，不会报告差异
# 输出: 无差异（数据完全一致）
```

### 示例 15: 等价值判断（浮点数字符串与数字）

```python
origin = {"price": "100.5"}
current = {"price": 100.5}

# 需要配置 ignore_type_in_groups 才能启用等价值判断
diffs = compare_structures(
    origin, 
    current, 
    deep_diff_contrast_config={
        "ignore_type_in_groups": [(int, str, float)]
    }
)

# 浮点数字符串"100.5"和数字100.5被识别为等价值，不会报告差异
# 输出: 无差异（数据完全一致）
```

### 示例 16: 等价值判断（浮点数与整数）

```python
origin = {"value": 100.0}
current = {"value": 100}

# 需要配置 ignore_type_in_groups 才能启用等价值判断
# 对于浮点数和整数，只需要配置 number 类型组
diffs = compare_structures(
    origin, 
    current, 
    deep_diff_contrast_config={
        "ignore_type_in_groups": [(int, float)]
    }
)

# 浮点数100.0和整数100被识别为等价值，不会报告差异
# 输出: 无差异（数据完全一致）
```

### 示例 17: 复杂嵌套列表对比（忽略顺序）

```python
origin = {
    "users": [
        {
            "id": 1,
            "name": "张三",
            "orders": [
                {"orderId": "001", "amount": 100},
                {"orderId": "002", "amount": 200}
            ]
        },
        {
            "id": 2,
            "name": "李四",
            "orders": [
                {"orderId": "003", "amount": 300}
            ]
        }
    ]
}
current = {
    "users": [
        {
            "id": 2,
            "name": "李四",
            "orders": [
                {"orderId": "003", "amount": 300}
            ]
        },
        {
            "id": 1,
            "name": "张三",
            "orders": [
                {"orderId": "002", "amount": 200},
                {"orderId": "001", "amount": 150}  # amount 变化
            ]
        }
    ]
}

# 使用忽略顺序模式，会匹配相同id的用户，然后递归对比内部字段
diffs = compare_structures(
    origin, 
    current, 
    deep_diff_contrast_config={
        "ignore_order": True  # 忽略用户列表和订单列表的顺序
    }
)

# 会检测到 orders[0].amount 的变化
# 输出: [值变化] users[0].orders[0].amount Origin值: 100 → Current值: 150
```

### 示例 18: 使用真实JSON数据对比

```python
import json
import os

# 读取JSON文件
def get_json(filepath, filename):
    full_path = os.path.join(filepath, filename)
    with open(full_path, 'r', encoding='utf-8') as f:
        return json.load(f)

# 读取真实数据
php_data = get_json("/Users/cuihaohao/test/parameters/", "php_data.json")
go_data = get_json("/Users/cuihaohao/test/parameters/", "go_data.json")

# 对比data字段，排除链接相关字段
diffs = compare_structures(
    php_data.get("data", {}),
    go_data.get("data", {}),
    exclude_fields={
        "rows[*].buy_steps[*].sub_rows[*].link",
        "rows[*].buy_steps[*].sub_rows[*].redirect_data.link",
        "rows[*].buy_steps[*].sub_rows[*].redirect_data.link_val",
        "rows[*].buy_steps[*].sub_rows[*].redirect_data.md5_url",
        "rows[*].buy_steps[*].sub_rows[*].redirect_data.sdk_link"
    },
    open_log=False
)

if not diffs:
    print("✅ 真实数据对比：排除链接字段后数据完全一致")
else:
    print(f"⚠️  真实数据对比：发现 {len(diffs)} 处差异（排除链接字段后）")
    for i, diff in enumerate(diffs[:5], 1):
        print(f"  {i}. {diff}")
    if len(diffs) > 5:
        print(f"  ... 还有 {len(diffs) - 5} 处差异未显示")
```

---

## 配置选项

### deep_diff_contrast_config 配置对象

```python
{
    # 是否忽略列表顺序
    # True: 无序列表，会尝试匹配相同元素（默认）
    # False: 有序列表，按索引直接对比
    "ignore_order": True,

    # 类型组配置，允许组内类型之间的转换和等价值判断
    # 例如: [(int, str)] 表示 int 和 str 可以互相转换
    # 重要：只有配置了 ignore_type_in_groups 后，等价值判断才会生效
    # 等价值判断包括：空字符串与0、数字字符串与数字、浮点数字符串与数字、浮点数与整数
    "ignore_type_in_groups": [
        (int, str, float, bool)
    ]
}
```

### 等价值判断规则

函数内置了等价值判断逻辑，但**需要配置 `ignore_type_in_groups` 才能启用**。以下情况在配置相应类型组后会被识别为等价值（不会报告差异）：

1. **空字符串与0等价**
   - `""` 和 `0` 等价（需要配置 `[(int, str)]`）
   - `0` 和 `""` 等价

2. **数字字符串与整数等价**
   - `"100"` 和 `100` 等价（需要配置 `[(int, str)]`）
   - `100` 和 `"100"` 等价

3. **浮点数字符串与数字等价**
   - `"100.5"` 和 `100.5` 等价（需要配置 `[(int, str, float)]`）
   - `100.5` 和 `"100.5"` 等价

4. **浮点数与整数等价（值相等时）**
   - `100.0` 和 `100` 等价（需要配置 `[(int, float)]`）
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

```python
exclude_fields = {
    "timestamp",                           # 排除根级别字段
    "user.profile",                        # 排除嵌套字段
    "items[*].id",                         # 排除列表字段
    "rows[*].buy_steps[*].sub_rows[*].link" # 排除深层嵌套字段
}
```

---

## 使用示例

### 场景 1: API 响应对比

```python
# 对比两个 API 响应的差异
origin_response = {
    "code": 200,
    "data": {
        "users": [
            {"id": 1, "name": "张三", "email": "zhang@example.com"},
            {"id": 2, "name": "李四", "email": "li@example.com"}
        ],
        "total": 2
    },
    "timestamp": 1234567890
}

current_response = {
    "code": 200,
    "data": {
        "users": [
            {"id": 1, "name": "张三", "email": "zhang@example.com"},
            {"id": 2, "name": "李四", "email": "li@example.com"}
        ],
        "total": 2
    },
    "timestamp": 1234567891  # 时间戳不同
}

diffs = compare_structures(
    origin_response,
    current_response,
    exclude_fields={"timestamp"},  # 排除时间戳
    open_log=False
)

if not diffs:
    print("✅ API 响应结构完全一致")
else:
    print("❌ 发现差异:")
    for diff in diffs:
        print(f"  - {diff}")
```

### 场景 2: 配置文件对比

```python
old_config = {
    "database": {
        "host": "localhost",
        "port": 3306,
        "name": "mydb"
    },
    "cache": {
        "enabled": True,
        "ttl": 3600
    }
}

new_config = {
    "database": {
        "host": "localhost",
        "port": 3306,
        "name": "mydb",
        "pool": {"max": 10}  # 新增配置
    },
    "cache": {
        "enabled": True,
        "ttl": 7200  # 值变化
    }
}

diffs = compare_structures(old_config, new_config, check_redundant=True)

# 输出:
# [冗余字段] database.pool (Current类型: dict[1])
# [值变化] cache.ttl Origin值: 3600 → Current值: 7200
```

### 场景 3: 数据迁移验证

```python
# 验证数据迁移前后的差异
before_migration = {
    "users": [
        {"id": 1, "name": "张三", "oldField": "value1"},
        {"id": 2, "name": "李四", "oldField": "value2"}
    ]
}

after_migration = {
    "users": [
        {"id": 1, "name": "张三", "newField": "value1"},
        {"id": 2, "name": "李四", "newField": "value2"}
    ]
}

diffs = compare_structures(
    before_migration, 
    after_migration, 
    exclude_fields={"users[*].oldField", "users[*].newField"},  # 排除迁移字段
    deep_diff_contrast_config={
        "ignore_order": True  # 用户列表顺序可能变化
    }
)

# 只检查核心字段（id, name）是否一致
```

### 场景 4: 测试数据对比

```python
# 对比测试用例的预期结果和实际结果
expected = {
    "status": "success",
    "data": {
        "items": [
            {"id": 1, "price": 100},
            {"id": 2, "price": 200}
        ]
    }
}

actual = {
    "status": "success",
    "data": {
        "items": [
            {"id": 1, "price": 100},
            {"id": 2, "price": 200}
        ]
    }
}

diffs = compare_structures(expected, actual, open_log=True)

if not diffs:
    print("✅ 测试通过")
else:
    print("❌ 测试失败，发现差异:")
    for diff in diffs:
        print(f"  - {diff}")
```

### 场景 5: 等价值处理场景

```python
# 场景：API返回的数据中，某些字段可能是字符串或数字
# 例如：价格可能是 "100" 或 100，需要识别为相同

origin = {
    "product": {
        "id": 1,
        "price": "100",      # 字符串格式
        "stock": 0,          # 数字格式
        "discount": ""       # 空字符串
    }
}

current = {
    "product": {
        "id": 1,
        "price": 100,         # 数字格式（等价值）
        "stock": "",          # 空字符串（等价值）
        "discount": 0         # 数字0（等价值）
    }
}

# 需要配置 ignore_type_in_groups 才能启用等价值判断
diffs = compare_structures(
    origin, 
    current, 
    deep_diff_contrast_config={
        "ignore_type_in_groups": [(int, str)]
    }
)

# 由于等价值判断，这些字段不会报告差异
# 输出: 无差异（数据完全一致）
```

### 场景 6: 浮点数精度处理

```python
# 场景：处理浮点数和整数的等价判断
origin = {
    "metrics": {
        "total": 100.0,       # 浮点数
        "average": "99.5",   # 浮点数字符串
        "count": 50           # 整数
    }
}

current = {
    "metrics": {
        "total": 100,         # 整数（与100.0等价）
        "average": 99.5,      # 浮点数（与"99.5"等价）
        "count": 50.0         # 浮点数（与50等价）
    }
}

# 需要配置 ignore_type_in_groups 才能启用等价值判断
# 配置 number 和 string 类型组，支持浮点数/整数和字符串之间的等价判断
diffs = compare_structures(
    origin, 
    current, 
    deep_diff_contrast_config={
        "ignore_type_in_groups": [(int, str, float)]
    }
)

# 所有字段都被识别为等价值
# 输出: 无差异（数据完全一致）
```

### 场景 7: 复杂业务数据对比

```python
# 场景：对比电商订单数据，排除动态字段
origin_order = {
    "orderId": "ORD001",
    "userId": 12345,
    "items": [
        {
            "productId": "P001",
            "quantity": 2,
            "price": "99.99",  # 字符串格式价格
            "link": "http://example.com/p001"
        },
        {
            "productId": "P002",
            "quantity": 1,
            "price": "199.99",
            "link": "http://example.com/p002"
        }
    ],
    "total": "299.97",
    "timestamp": 1234567890,
    "tracking": {
        "link": "http://tracking.com/ORD001",
        "code": "TRACK123"
    }
}

current_order = {
    "orderId": "ORD001",
    "userId": 12345,
    "items": [
        {
            "productId": "P002",
            "quantity": 1,
            "price": 199.99,    # 数字格式价格（等价值）
            "link": "http://example.com/p002-new"  # 链接变化
        },
        {
            "productId": "P001",
            "quantity": 2,
            "price": 99.99,    # 数字格式价格（等价值）
            "link": "http://example.com/p001-new"  # 链接变化
        }
    ],
    "total": 299.97,           # 数字格式（等价值）
    "timestamp": 1234567891,   # 时间戳变化
    "tracking": {
        "link": "http://tracking.com/ORD001-new",  # 链接变化
        "code": "TRACK123"
    }
}

# 排除动态字段：链接和时间戳
# 配置类型组以启用等价值判断（价格字段可能是字符串或数字）
diffs = compare_structures(
    origin_order, 
    current_order, 
    exclude_fields={
        "items[*].link",
        "timestamp",
        "tracking.link"
    },
    deep_diff_contrast_config={
        "ignore_order": True,  # 忽略商品列表顺序
        "ignore_type_in_groups": [(int, str, float)]  # 启用等价值判断
    }
)

# 由于等价值判断和排除字段，只会检查核心业务字段
# 价格字段 "99.99" 和 99.99 会被识别为等价值
# 输出: 无差异（数据完全一致）
```

---

## 常见场景

### 1. 只检查结构，不检查值

```python
diffs = compare_structures(
    origin, 
    current, 
    check_value=False,  # 不检查值差异
    check_type=True,    # 仍然检查类型
    check_missing=True  # 仍然检查缺失字段
)
```

### 2. 只检查值，不检查类型

```python
diffs = compare_structures(
    origin, 
    current, 
    check_value=True,   # 检查值差异
    check_type=False   # 不检查类型差异
)
```

### 3. 完全对比（包括冗余字段）

```python
diffs = compare_structures(
    origin, 
    current, 
    check_value=True,
    check_missing=True,
    check_redundant=True,  # 检查冗余字段
    check_type=True
)
```

### 4. 从JSON文件读取数据对比

```python
import json
import os

def get_json(filepath, filename):
    full_path = os.path.join(filepath, filename)
    with open(full_path, 'r', encoding='utf-8') as f:
        return json.load(f)

# 对比两个 JSON 文件
origin_data = get_json("./data/", "origin.json")
current_data = get_json("./data/", "current.json")

diffs = compare_structures(
    origin_data, 
    current_data, 
    exclude_fields={"timestamp", "updated_at"},
    open_log=True
)

if not diffs:
    print("✅ 数据完全一致")
else:
    print(f"❌ 发现 {len(diffs)} 处差异:")
    for diff in diffs:
        print(f"  - {diff}")
```

### 5. 在命令行中使用（通过 main 函数）

```python
# compare_structures.py 提供了 main 函数，支持从命令行调用
# 参数通过 JSON 字符串传递

import json
import subprocess

# 准备参数
params = {
    "origin_data": {"name": "张三", "age": 25},
    "current_data": {"name": "李四", "age": 25},
    "check_value": True,
    "check_type": True,
    "exclude_fields": ["timestamp"]
}

# 转换为 JSON 字符串
json_params = json.dumps(params, ensure_ascii=False)

# 调用脚本
result = subprocess.run(
    ["python", "compare_structures.py", json_params],
    capture_output=True,
    text=True
)

# 解析结果
output = json.loads(result.stdout)
if output["success"]:
    print(f"发现 {output['difference_count']} 处差异")
    for diff in output["differences"]:
        print(diff)
else:
    print(f"错误: {output['error']}")
```

---

## 注意事项

1. **性能考虑**: 对于大型数据结构，建议使用 `exclude_fields` 排除不需要检查的字段
2. **内存使用**: 函数会深拷贝输入数据，对于非常大的对象可能消耗较多内存
3. **类型检查**: 默认会检查类型，如果数据中数字和字符串可以互换，建议配置 `ignore_type_in_groups`
4. **等价值判断**: 等价值判断（空字符串与0、数字字符串与数字等）仅在配置了 `ignore_type_in_groups` 时生效。如果未配置，会按正常类型和值对比
5. **列表顺序**: 默认忽略列表顺序，如果需要按索引对比，设置 `ignore_order: False`
6. **路径格式**: 排除字段的路径使用点号分隔，列表使用 `[*]` 通配符
7. **日志输出**: 开启 `open_log=True` 时，会使用 `logzero.logger` 输出详细日志，需要确保已安装 `logzero` 库

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

## 版本信息

- **版本**: 优化后，等价值判断需配置版本
- **作者**: 崔浩浩
- **语言**: Python 3.x
- **依赖**: 
  - `typing` (标准库)
  - `copy` (标准库)
  - `re` (标准库)
  - `logzero` (需要安装: `pip install logzero`)

---

## 更新日志

### 最新版本更新

- **等价值判断配置要求**: 等价值判断功能现在需要通过 `ignore_type_in_groups` 配置来控制是否启用
- **所有等价值判断场景**: 现在都需要配置才能生效
- **与 JavaScript 版本一致**: 与 `compare_structures_js.js` 保持一致的行为

---

## 相关文档

- 测试报告: `compare_structures_test_report.md`
- 测试场景: `test_compare_structures_scenarios.py`
- JavaScript 版本: `../compare_structures_js/compare_structures_js.js`

