# 快速开始

## Python 版本

### 1. 安装

```bash
cd compare_structures_py
pip install -e .
```

### 2. 使用

```python
from compare_structures_py import compare_structures

# 简单示例
origin = {"name": "test", "age": 20}
current = {"name": "test", "age": 21}

diffs = compare_structures(origin, current)
for diff in diffs:
    print(diff)
```

## JavaScript 版本

### 1. 安装

```bash
cd compare_structures_js
npm install .
```

### 2. 使用

```javascript
const compareStructures = require('compare-structures');

// 简单示例
const origin = {name: "test", age: 20};
const current = {name: "test", age: 21};

const diffs = compareStructures(origin, current);
diffs.forEach(diff => console.log(diff));
```

## 在其他项目中使用

### Python 项目

在你的 `requirements.txt` 或 `setup.py` 中添加：

```txt
# requirements.txt
compare-structures @ git+https://github.com/cuihaohao1220/compare_structures.git#subdirectory=compare_structures_py
```

或

```python
# setup.py
install_requires=[
    "compare-structures @ git+https://github.com/cuihaohao1220/compare_structures.git#subdirectory=compare_structures_py",
]
```

### JavaScript 项目

在你的 `package.json` 中添加：

```json
{
  "dependencies": {
    "compare-structures": "git+https://github.com/cuihaohao1220/compare_structures.git#subdirectory=compare_structures_js"
  }
}
```

