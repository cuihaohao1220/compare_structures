# Git 配置和推送指南

代码已经提交到本地仓库，但推送到 GitHub 需要身份验证。

## 当前状态

✅ Git 仓库已初始化
✅ 远程仓库已关联：`https://github.com/cuihaohao1220/compare_structures.git`
✅ 代码已提交到本地（16 个文件，5461 行代码）
✅ 分支已重命名为 `main`

## 推送代码到 GitHub

### 方式1: 使用个人访问令牌（PAT，推荐）

1. **创建 GitHub 个人访问令牌**：
   - 访问：https://github.com/settings/tokens
   - 点击 "Generate new token" → "Generate new token (classic)"
   - 设置名称和过期时间
   - 勾选 `repo` 权限
   - 点击 "Generate token"
   - **复制生成的令牌**（只显示一次）

2. **推送代码**：
   ```bash
   cd /Users/cuihaohao/compare_structures
   git push -u origin main
   ```
   
   当提示输入用户名时：
   - Username: `cuihaohao1220`
   - Password: 粘贴你的个人访问令牌（不是 GitHub 密码）

### 方式2: 使用 SSH 密钥

1. **检查是否已有 SSH 密钥**：
   ```bash
   ls -al ~/.ssh
   ```

2. **如果没有，生成 SSH 密钥**：
   ```bash
   ssh-keygen -t ed25519 -C "your_email@example.com"
   # 按 Enter 使用默认路径
   # 可以设置密码或直接按 Enter
   ```

3. **复制公钥**：
   ```bash
   cat ~/.ssh/id_ed25519.pub
   # 复制输出的内容
   ```

4. **添加到 GitHub**：
   - 访问：https://github.com/settings/keys
   - 点击 "New SSH key"
   - 粘贴公钥内容
   - 点击 "Add SSH key"

5. **更改远程 URL 为 SSH**：
   ```bash
   cd /Users/cuihaohao/compare_structures
   git remote set-url origin git@github.com:cuihaohao1220/compare_structures.git
   git push -u origin main
   ```

### 方式3: 使用 GitHub CLI

```bash
# 安装 GitHub CLI（如果未安装）
brew install gh

# 登录
gh auth login

# 推送
cd /Users/cuihaohao/compare_structures
git push -u origin main
```

## 验证推送

推送成功后，访问 https://github.com/cuihaohao1220/compare_structures 查看你的代码。

## 后续操作

推送成功后，你可以：

1. **在其他项目中安装 Python 版本**：
   ```bash
   pip install git+https://github.com/cuihaohao1220/compare_structures.git#subdirectory=compare_structures_py
   ```

2. **在其他项目中安装 JavaScript 版本**：
   ```bash
   npm install git+https://github.com/cuihaohao1220/compare_structures.git#subdirectory=compare_structures_js
   ```

3. **更新 README 中的 GitHub 链接**（如果需要）

