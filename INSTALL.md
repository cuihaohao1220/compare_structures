# 安装指南

## Python 版本安装

### 方式1: 开发模式安装（推荐用于开发）

开发模式安装允许你在修改代码后立即生效，无需重新安装：

```bash
cd compare_structures_py
pip install -e .
```

### 方式2: 生产模式安装

```bash
cd compare_structures_py
pip install .
```

### 方式3: 从本地打包文件安装

首先打包：

```bash
cd compare_structures_py
python setup.py sdist bdist_wheel
```

然后安装：

```bash
pip install dist/compare-structures-1.0.0.tar.gz
# 或
pip install dist/compare_structures-1.0.0-py3-none-any.whl
```

### 方式4: 从 Git 仓库安装

```bash
# 从 GitHub 安装
pip install git+https://github.com/yourusername/compare_structures.git#subdirectory=compare_structures_py

# 从本地 Git 仓库安装
pip install git+file:///path/to/compare_structures#subdirectory=compare_structures_py
```

### 方式5: 发布到 PyPI 后安装

如果已经发布到 PyPI：

```bash
pip install compare-structures
```

## JavaScript 版本安装

### 方式1: 从本地安装

```bash
cd compare_structures_js
npm install .
```

### 方式2: 从 Git 仓库安装

```bash
npm install git+https://github.com/yourusername/compare_structures.git#subdirectory=compare_structures_js
```

### 方式3: 发布到 npm 后安装

如果已经发布到 npm：

```bash
npm install compare-structures
```

### 方式4: 直接使用（浏览器环境）

直接将 `compare_structures_js.js` 文件复制到项目中，然后在 HTML 中引用：

```html
<script src="path/to/compare_structures_js.js"></script>
```

## 验证安装

### Python 验证

```python
# 测试导入
from compare_structures_py import compare_structures
print("安装成功！")

# 测试功能
result = compare_structures(
    {"a": 1},
    {"a": 1}
)
print(f"测试结果: {result}")
```

### JavaScript 验证

```javascript
// Node.js 环境
const compareStructures = require('compare-structures');
console.log("安装成功！");

// 测试功能
const result = compareStructures({a: 1}, {a: 1});
console.log("测试结果:", result);
```

## 卸载

### Python 卸载

```bash
pip uninstall compare-structures
```

### JavaScript 卸载

```bash
npm uninstall compare-structures
```

## 常见问题

### Python 安装问题

1. **权限错误**: 使用 `pip install --user` 安装到用户目录
2. **依赖缺失**: 确保已安装 `logzero`: `pip install logzero`
3. **Python 版本**: 确保 Python 版本 >= 3.7

### JavaScript 安装问题

1. **Node.js 版本**: 确保 Node.js 版本 >= 12.0.0
2. **npm 权限**: 如果遇到权限问题，使用 `sudo` 或配置 npm 全局路径

