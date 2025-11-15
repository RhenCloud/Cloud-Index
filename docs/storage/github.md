---
title: GitHub
createTime: 2025/11/09 00:26:55
permalink: /storage/github
---
# GitHub 存储配置指南

使用 GitHub 仓库作为存储后端的详细配置。

## 概述

GitHub 存储是一个创新的免费存储方案，利用 GitHub 仓库来存储文件：

- 💚 完全免费（通过 GitHub）
- 📝 自动版本控制
- 🔐 私密仓库支持
- 🌍 全球访问
- 📦 便于备份和迁移

## 为什么选择 GitHub 存储？

### 优势

1. **完全免费** - 无需付费，利用 GitHub 存储空间
2. **自动版本控制** - 所有文件自动保存版本历史
3. **内置权限管理** - 利用 GitHub 的访问权限系统
4. **易于备份** - 通过 Git 可以轻松备份和迁移
5. **开发者友好** - 与 Git 工作流完美集成

### 限制

- 仓库大小建议不超过 1GB
- 文件大小建议不超过 100MB
- 不适合大规模二进制文件存储

### 推荐用途

- 📄 文档和文本文件
- 🖼️ 博客和网站图片
- 🔧 配置文件
- 📋 CSV 数据文件
- 🎯 开源项目资源

## 账户设置

### 1. 创建 GitHub 账户

如果还没有 GitHub 账户，访问 [GitHub](https://github.com/signup) 创建一个免费账户。

### 2. 创建仓库

1. 登录 GitHub
2. 点击 "+" 图标 → "New repository"
3. 输入仓库名称（例如 `my-storage`）
4. 选择 "Private"（私密）或 "Public"（公开）
5. **不要** 初始化 README
6. 点击 "Create repository"

## 生成 Personal Access Token

### 1. 创建 Token

1. 登录 GitHub
2. 进入 Settings → Developer settings → Personal access tokens
3. 点击 "Generate new token"（选择 "Tokens (classic)"）
4. 输入 Token 名称（例如 `cloud-index`）
5. 选择过期时间（推荐 "90 days" 或 "No expiration"）

### 2. 设置权限

选择以下权限：

- ✅ **repo** - 完整控制私有仓库（包括所有子权限）
- ✅ **workflow** - 更新 GitHub Action 工作流
- ❌ 其他权限保持未勾选

### 3. 生成并复制 Token

1. 点击 "Generate token"
2. **立即复制 Token**（只显示一次）
3. 保存到安全位置

⚠️ **重要**: 不要分享你的 Token！

## 配置环境变量

编辑 `.env` 文件：

```env
# 存储类型
STORAGE_TYPE=github

# GitHub 账户信息
GITHUB_REPO_OWNER=your-username
GITHUB_REPO_NAME=my-storage
GITHUB_ACCESS_TOKEN=ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# 可选：使用的分支
GITHUB_BRANCH=main

# 可选：GitHub Raw 内容代理（用于加速国内访问）
GITHUB_RAW_PROXY_URL=https://raw.ghproxy.com

# 可选：预签名 URL 过期时间（秒）
GITHUB_PRESIGN_EXPIRES=3600
```

**配置说明：**

- `GITHUB_REPO_OWNER`: 你的 GitHub 用户名
- `GITHUB_REPO_NAME`: 创建的仓库名称
- `GITHUB_ACCESS_TOKEN`: 生成的 Personal Access Token
- `GITHUB_BRANCH`: 默认 `main`（仓库主分支）
- `GITHUB_RAW_PROXY_URL`: 可选，用于加速访问

## 国内加速代理配置

由于 GitHub 在国内访问速度较慢，推荐使用代理加速：

### 推荐代理服务

```env
# GitHub 官方（无加速）
GITHUB_RAW_PROXY_URL=

# ghproxy.com - 国内加速（推荐）
GITHUB_RAW_PROXY_URL=https://raw.ghproxy.com

# ghproxy.net - 国内加速
GITHUB_RAW_PROXY_URL=https://ghproxy.net

# 其他代理服务
GITHUB_RAW_PROXY_URL=https://raw.fastgit.org
```

## 初始化仓库

首次使用时，需要初始化仓库（可选但推荐）：

```bash
# 克隆空仓库
git clone https://github.com/your-username/my-storage.git
cd my-storage

# 创建初始文件
echo "# 存储仓库" > README.md
git add README.md
git commit -m "Initial commit"
git push -u origin main

# 返回 Cloud Index 目录
cd ../cloud-index
```

## 启用版本控制特性

### 查看文件历史

1. 在 GitHub Web 上打开文件
2. 点击 "History"
3. 查看所有历史版本

### 恢复旧版本文件

```bash
# 查看文件历史
git log -- filename

# 恢复到特定版本
git checkout <commit-hash> -- filename

# 提交恢复
git commit -m "Restore filename to previous version"
git push
```

### 标记发布版本

```bash
# 创建标签
git tag -a v1.0 -m "Release version 1.0"
git push origin v1.0

# 查看所有标签
git tag -l
```

## 生成公开访问 URL

### Raw 文件 URL

文件会自动通过 Raw GitHub URL 访问：

```
# 官方 URL（国外快）
https://raw.githubusercontent.com/your-username/my-storage/main/path/to/file

# 使用代理加速（国内快）
https://raw.ghproxy.com/https://raw.githubusercontent.com/your-username/my-storage/main/path/to/file
```

### 在应用中生成

在 Cloud Index 应用中：

1. 点击文件
2. 选择 "复制链接"
3. 分享链接给他人

## 高级配置

### 使用 GitHub Actions 自动化

可以创建自动化工作流（可选）：

```yaml
# .github/workflows/backup.yml
name: Daily Backup

on:
  schedule:
    - cron: '0 0 * * *'

jobs:
  backup:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Backup
        run: |
          # 你的备份脚本
          echo "Backup completed"
```

### 使用分支隔离环境

为不同环境使用不同分支：

```bash
# 创建开发分支
git checkout -b develop
git push -u origin develop

# 创建生产分支
git checkout -b production
git push -u origin production
```

## 文件大小限制处理

如果遇到文件过大（> 100MB）：

### 使用 Git LFS

```bash
# 安装 Git LFS
git lfs install

# 追踪大文件
git lfs track "*.psd"
git add .gitattributes

# 提交文件
git add large-file.psd
git commit -m "Add large file"
git push
```

### 分割文件

```bash
# 分割大文件
split -b 50M large-file.zip large-file.zip.part_

# 上传分割后的文件
git add large-file.zip.part_*
git commit -m "Add split files"
git push

# 恢复时合并
cat large-file.zip.part_* > large-file.zip
```

## 与其他存储的对比

| 特性 | GitHub | R2 | S3 |
|-----|--------|-----|-----|
| 成本 | 免费 | $0.36/百万请求 | $2-3/GB |
| 文件大小限制 | 100MB | 无限 | 5TB |
| 仓库大小限制 | 1GB | 无限 | 无限 |
| 版本控制 | ✅ | ❌ | ⚠️ |
| 适合大文件 | ❌ | ✅ | ✅ |

## 成本示例

月均使用情况：

| 指标 | 数值 | 费用 |
|-----|------|------|
| 存储 | 500MB | 免费 |
| 请求 | 10K | 免费 |
| 流量 | 1GB | 免费 |
| **总计** | - | **完全免费** ✅ |

## 获取帮助

- 📖 [GitHub API 文档](https://docs.github.com/en/rest)
- 📖 [GitHub 仓库管理指南](https://docs.github.com/en/repositories)
- 🐛 [提交 Issue](https://github.com/RhenCloud/Cloud-Index/issues)
- 💬 [讨论区](https://github.com/RhenCloud/Cloud-Index/discussions)

## 下一步

- 🚀 [快速开始](../guide/quickstart.md) - 开始使用应用
- 📖 [存储后端对比](./overview.md) - 对比其他服务
- 💾 [Cloudflare R2 配置](./r2.md) - R2 配置指南
