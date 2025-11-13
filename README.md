# compare_structures

增强版结构对比库 - 用于深度对比两个数据结构（字典/列表或对象/数组）

作者: 崔浩浩

## 功能特性

- ✅ 识别缺失字段（包括嵌套结构）
- ✅ 检测类型不一致
- ✅ 列表结构差异对比（长度、元素类型）
- ✅ 值变化检测
- ✅ 支持排除字段白名单
- ✅ 支持忽略列表顺序
- ✅ 支持类型组配置（如数值精度、类型检查等）
- ✅ 支持嵌套路径和通配符匹配

## 安装方式

### Python 版本

#### 方式1: 从本地安装（开发模式）

```bash
cd compare_structures_py
pip install -e .
```

#### 方式2: 从本地安装（生产模式）

```bash
cd compare_structures_py
pip install .
```

#### 方式3: 从 Git 仓库安装

```bash
pip install git+https://github.com/yourusername/compare_structures.git#subdirectory=compare_structures_py
```

#### 方式4: 打包后安装

```bash
cd compare_structures_py
python setup.py sdist bdist_wheel
pip install dist/compare-structures-1.0.0.tar.gz
```

### JavaScript 版本

#### 方式1: 从本地安装

```bash
cd compare_structures_js
npm install .
```

#### 方式2: 从 Git 仓库安装

```bash
npm install git+https://github.com/yourusername/compare_structures.git#subdirectory=compare_structures_js
```

#### 方式3: 发布到 npm 后安装

```bash
cd compare_structures_js
npm publish
# 然后在其他项目中使用
npm install compare-structures
```

## 使用方法

### Python 版本

```python
from compare_structures_py import compare_structures

origin_data = {
    "name": "test",
    "age": 20,
    "tags": ["python", "javascript"]
}

current_data = {
    "name": "test",
    "age": 21,
    "tags": ["javascript", "python"]
}

# 基本使用
differences = compare_structures(
    origin_data=origin_data,
    current_data=current_data,
    check_value=True,
    check_missing=True,
    check_type=True
)

if differences:
    for diff in differences:
        print(diff)
else:
    print("结构完全一致")
```

#### 高级配置

```python
from compare_structures_py import compare_structures

# 配置排除字段
exclude_fields = {"timestamp", "user.medal", "list[*].id"}

# 配置对比参数
deep_diff_contrast_config = {
    "ignore_order": True,  # 忽略列表顺序
    "ignore_type_in_groups": [(int, str, float)]  # 忽略类型组内的类型差异
}

differences = compare_structures(
    origin_data=origin_data,
    current_data=current_data,
    exclude_fields=exclude_fields,
    deep_diff_contrast_config=deep_diff_contrast_config,
    open_log=True  # 开启日志
)
```

### JavaScript 版本

#### Node.js 环境

```javascript
const compareStructures = require('compare-structures');

const originData = {
    name: "test",
    age: 20,
    tags: ["python", "javascript"]
};

const currentData = {
    name: "test",
    age: 21,
    tags: ["javascript", "python"]
};

// 方式1: 使用位置参数
const differences = compareStructures(
    originData,
    currentData,
    "",      // path
    true,    // checkValue
    true,    // checkMissing
    false,   // checkRedundant
    true,    // checkType
    null,    // excludeFields
    null,    // deepDiffContrastConfig
    false    // openLog
);

// 方式2: 使用对象参数（推荐）
const differences = compareStructures.compareStructuresWithOptions(
    originData,
    currentData,
    {
        checkValue: true,
        checkMissing: true,
        excludeFields: ["timestamp", "user.medal"],
        deepDiffContrastConfig: {
            ignore_order: true
        }
    }
);

if (differences.length === 0) {
    console.log("结构完全一致");
} else {
    differences.forEach(diff => console.log(diff));
}
```

#### 浏览器环境

```html
<script src="compare_structures_js.js"></script>
<script>
    const differences = compareStructures(originData, currentData);
    // 或使用
    const differences = compareStructuresWithOptions(originData, currentData, options);
</script>
```

## 参数说明

### Python 参数

- `origin_data`: Origin数据（字典或列表）
- `current_data`: Current数据（字典或列表）
- `path`: 当前路径（递归用，默认 ""）
- `check_value`: 是否检查值差异（默认 True）
- `check_missing`: 是否检查缺失字段（默认 True）
- `check_redundant`: 是否检查冗余字段（默认 False）
- `check_type`: 是否检查类型差异（默认 True）
- `exclude_fields`: 排除字段白名单（Set[str]，默认 None）
- `deep_diff_contrast_config`: 对比配置参数（Dict，默认 None）
  - `ignore_order`: 是否忽略列表顺序（默认 True）
  - `ignore_type_in_groups`: 类型组列表，如 `[(int, str, float)]`
- `open_log`: 开启日志（默认 False）

### JavaScript 参数

参数与 Python 版本类似，但使用 JavaScript 类型：
- `originData`: Origin数据（对象或数组）
- `currentData`: Current数据（对象或数组）
- `path`: 当前路径（默认 ""）
- `checkValue`: 是否检查值差异（默认 true）
- `checkMissing`: 是否检查缺失字段（默认 true）
- `checkRedundant`: 是否检查冗余字段（默认 false）
- `checkType`: 是否检查类型差异（默认 true）
- `excludeFields`: 排除字段白名单（Set 或 Array，默认 null）
- `deepDiffContrastConfig`: 对比配置参数（Object，默认 null）
- `openLog`: 开启日志（默认 false）

## 排除字段示例

支持嵌套路径和通配符：

```python
exclude_fields = {
    "timestamp",                    # 排除顶层字段
    "user.medal",                   # 排除嵌套字段
    "list[*].id",                   # 排除列表中所有元素的 id 字段
    "rows[*].buy_steps[*].link"     # 排除多层嵌套列表中的字段
}
```

## 返回结果

函数返回一个字符串列表，每个字符串描述一个差异：

- `[字段缺失] path (Origin类型: type)` - 字段在 Current 中缺失
- `[冗余字段] path (Current类型: type)` - 字段在 Origin 中不存在
- `[类型冲突] path Origin类型: type → Current类型: type` - 类型不一致
- `[值变化] path Origin值: value → Current值: value` - 值发生变化
- `[列表差异] path[index] (iterable_item_added)` - 列表元素增加
- `[列表差异] path[index] (iterable_item_removed)` - 列表元素移除

## 开发

### Python 开发

```bash
cd compare_structures_py
pip install -e ".[dev]"  # 如果有开发依赖
```

### JavaScript 开发

```bash
cd compare_structures_js
npm install
```

## 许可证

MIT License

## 贡献

欢迎提交 Issue 和 Pull Request！

