---
title: 基础配置
createTime: 2025/11/09
permalink: /guide/configuration/configuration
---

配置 Cloud Index 以满足您的特定需求。

## 概述

Cloud Index 使用环境变量进行配置，支持多种存储后端和自定义选项。本章节包含了所有配置相关的文档。

## 配置内容

### 1. [基础配置](/guide/configuration/configuration)

了解 Cloud Index 的基本配置方式：

- 配置文件和环境变量
- 存储后端选择
- 核心参数设置
- 快速入门配置

**适合**：初次使用者，想要快速配置应用

### 2. [环境变量完整参考](/guide/configuration/environment)

所有环境变量的详细参考文档：

- **核心配置** - 基础应用设置
- **R2 配置** - Cloudflare R2 存储后端
- **S3 配置** - Amazon S3 存储后端
- **GitHub 配置** - GitHub 仓库存储后端
- **缓存配置** - 缩略图和性能优化
- **日志配置** - 日志输出和调试

**适合**：需要详细参考的开发者，高级配置需求

---

## 快速配置

### 最小配置（Cloudflare R2）

```env
STORAGE_TYPE=r2
ACCESS_KEY_ID=your_access_key
SECRET_ACCESS_KEY=your_secret_key
R2_ENDPOINT_URL=https://your-account-id.r2.cloudflarestorage.com
R2_BUCKET_NAME=your-bucket-name
R2_PUBLIC_URL=https://pub-your-bucket.r2.dev
```

### 最小配置（Amazon S3）

```env
STORAGE_TYPE=s3
ACCESS_KEY_ID=your_access_key
SECRET_ACCESS_KEY=your_secret_key
S3_BUCKET_NAME=your-bucket-name
S3_REGION=us-east-1
```

### 最小配置（GitHub）

```env
STORAGE_TYPE=github
GITHUB_REPO_OWNER=your-username
GITHUB_REPO_NAME=your-repo-name
GITHUB_ACCESS_TOKEN=your_github_token
```

---

## 下一步

- 📖 参考 [环境变量完整参考](/guide/configuration/environment) 了解所有选项
- 🚀 查看 [部署指南](/guide/deployment/) 了解如何部署应用

---

## 获取帮助

遇到配置问题？

- 📖 [完整参考文档](/guide/configuration/environment)
- 🐛 [提交 Issue](https://github.com/RhenCloud/Cloud-Index/issues)
- 💬 [讨论区](https://github.com/RhenCloud/Cloud-Index/discussions)
- 📧 <i@rhen.cloud>
