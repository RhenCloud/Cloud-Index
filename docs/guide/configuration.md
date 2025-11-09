---
title: 配置指南
createTime: 2025/11/09 00:26:55
permalink: /guide/configuration
---
# 配置说明

本文档详细说明了 Cloud Index 的各种配置选项。

## 配置方式

Cloud Index 通过环境变量进行配置，有两种主要方式：

### 1. 环境变量文件 (.env)

在项目根目录创建 `.env` 文件：

```bash
cp .env.example .env
```

编辑 `.env` 文件，添加需要的配置。

### 2. 系统环境变量

直接在系统中设置环境变量（适用于 Docker、Serverless 等环境）。

## 存储后端配置

### STORAGE_TYPE（必需）

选择要使用的存储后端：

```env
# Cloudflare R2
STORAGE_TYPE=r2

# Amazon S3
STORAGE_TYPE=s3

# GitHub 仓库
STORAGE_TYPE=github

# GitHub Release
STORAGE_TYPE=github-release
```

## Cloudflare R2 配置

当 `STORAGE_TYPE=r2` 时，需要配置以下环境变量：

```env
# ===== R2 基础配置 =====
STORAGE_TYPE=r2

# R2 API 访问凭证
ACCESS_KEY_ID=your_access_key_id
SECRET_ACCESS_KEY=your_secret_access_key

# R2 存储桶信息
R2_ENDPOINT_URL=https://your-account-id.r2.cloudflarestorage.com
R2_BUCKET_NAME=your-bucket-name
R2_REGION=auto

# ===== 可选配置 =====

# 公开访问 URL（用于生成可分享的文件链接）
R2_PUBLIC_URL=https://pub-your-bucket.r2.dev

# 预签名 URL 过期时间（秒），默认 3600
R2_PRESIGN_EXPIRES=3600
```

**配置说明：**

| 配置项 | 说明 | 获取方式 |
|-------|------|---------|
| `ACCESS_KEY_ID` | R2 API Token ID | Cloudflare 控制面板 |
| `SECRET_ACCESS_KEY` | R2 API Token Secret | Cloudflare 控制面板 |
| `R2_ENDPOINT_URL` | R2 端点 URL | Cloudflare 控制面板（Account ID） |
| `R2_BUCKET_NAME` | 存储桶名称 | Cloudflare 控制面板 |
| `R2_PUBLIC_URL` | 公开 URL（可选） | Cloudflare 控制面板 → Custom Domain |

**获取凭证步骤：**

1. 登录 [Cloudflare 控制面板](https://dash.cloudflare.com)
2. 进入 R2 → API Tokens
3. 创建新 Token，复制 ID 和 Secret
4. 记录你的 Account ID（在 R2 仓库页面显示）

## Amazon S3 配置

当 `STORAGE_TYPE=s3` 时，需要配置以下环境变量：

```env
# ===== S3 基础配置 =====
STORAGE_TYPE=s3

# AWS 访问凭证
ACCESS_KEY_ID=your_aws_access_key
SECRET_ACCESS_KEY=your_aws_secret_key

# S3 存储桶信息
S3_BUCKET_NAME=your-bucket-name
S3_REGION=us-east-1

# ===== 可选配置 =====

# 自定义 S3 端点（用于兼容的 S3 服务）
S3_ENDPOINT_URL=https://s3.amazonaws.com

# 公开访问 URL
S3_PUBLIC_URL=https://your-bucket-name.s3.amazonaws.com

# 预签名 URL 过期时间（秒）
S3_PRESIGN_EXPIRES=3600
```

**配置说明：**

| 配置项 | 说明 | 获取方式 |
|-------|------|---------|
| `ACCESS_KEY_ID` | AWS Access Key ID | AWS IAM 控制台 |
| `SECRET_ACCESS_KEY` | AWS Secret Access Key | AWS IAM 控制台 |
| `S3_BUCKET_NAME` | 存储桶名称 | AWS S3 控制台 |
| `S3_REGION` | 存储桶区域 | AWS S3 控制台 |

**常用区域代码：**

```
us-east-1     - 美国东部（N. Virginia）
us-west-2     - 美国西部（Oregon）
eu-west-1     - 欧洲（Ireland）
ap-northeast-1 - 亚太（Tokyo）
cn-north-1    - 中国（北京）
```

## GitHub 存储配置

当 `STORAGE_TYPE=github` 时，需要配置以下环境变量：

```env
# ===== GitHub 基础配置 =====
STORAGE_TYPE=github

# GitHub 账户信息
GITHUB_REPO_OWNER=your-username
GITHUB_REPO_NAME=your-repo-name
GITHUB_ACCESS_TOKEN=your_github_personal_token

# ===== 可选配置 =====

# 使用的分支，默认 main
GITHUB_BRANCH=main

# GitHub Raw 内容代理 URL（用于加速访问）
GITHUB_RAW_PROXY_URL=https://raw.ghproxy.com

# 预签名 URL 过期时间（秒）
GITHUB_PRESIGN_EXPIRES=3600
```

**配置说明：**

| 配置项 | 说明 | 获取方式 |
|-------|------|---------|
| `GITHUB_REPO_OWNER` | GitHub 用户名或组织名 | GitHub Profile |
| `GITHUB_REPO_NAME` | 仓库名称 | GitHub 仓库页面 |
| `GITHUB_ACCESS_TOKEN` | Personal Access Token | GitHub Settings → Developer settings |
| `GITHUB_RAW_PROXY_URL` | Raw 内容代理（可选） | 第三方代理服务 |

**获取 Token 步骤：**

1. 登录 GitHub
2. 进入 Settings → Developer settings → Personal access tokens
3. 创建新 Token（New fine-grained personal access token）
4. 勾选 `contents` 权限（读写仓库内容）
5. 复制 Token，保存到 `.env` 文件

**推荐代理服务：**

```
https://raw.ghproxy.com      - 国内加速
https://ghproxy.com          - 国内加速
https://raw.githubusercontent.com - 官方（无加速）
```

## 应用配置

### 缓存配置

```env
# 缩略图缓存过期时间（秒），默认 3600（1小时）
THUMB_TTL_SECONDS=3600
```

### 应用服务器配置

```env
# Flask 调试模式（开发环境推荐启用）
FLASK_ENV=development
FLASK_DEBUG=1

# 应用监听地址
FLASK_RUN_HOST=0.0.0.0

# 应用监听端口
FLASK_RUN_PORT=5000
```

### 日志配置

```env
# 日志级别
LOG_LEVEL=INFO

# 日志文件路径
LOG_FILE=/var/log/Cloud Index/app.log
```

## 完整配置示例

### R2 + 国内代理

```env
# 存储配置
STORAGE_TYPE=r2
ACCESS_KEY_ID=abc123xyz
SECRET_ACCESS_KEY=def456uvw
R2_ENDPOINT_URL=https://account123.r2.cloudflarestorage.com
R2_BUCKET_NAME=my-bucket
R2_REGION=auto
R2_PUBLIC_URL=https://pub-my-bucket.r2.dev
R2_PRESIGN_EXPIRES=7200

# 应用配置
FLASK_ENV=production
FLASK_RUN_HOST=0.0.0.0
FLASK_RUN_PORT=8080
THUMB_TTL_SECONDS=7200
```

### GitHub + 加速代理

```env
# 存储配置
STORAGE_TYPE=github
GITHUB_REPO_OWNER=myusername
GITHUB_REPO_NAME=my-storage
GITHUB_ACCESS_TOKEN=ghp_xxxxxxxxxxxxxxxxxx
GITHUB_BRANCH=main
GITHUB_RAW_PROXY_URL=https://raw.ghproxy.com

# 应用配置
FLASK_ENV=production
THUMB_TTL_SECONDS=3600
```

### Amazon S3 + CDN

```env
# 存储配置
STORAGE_TYPE=s3
ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE
SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
S3_BUCKET_NAME=my-bucket
S3_REGION=us-west-2
S3_PUBLIC_URL=https://d123.cloudfront.net

# 应用配置
FLASK_ENV=production
FLASK_RUN_PORT=5000
```

## 环境变量优先级

1. 系统环境变量（最高）
2. `.env` 文件变量
3. 代码中的默认值（最低）

## 配置验证

启动应用后，检查日志输出确保配置正确：

```bash
python app.py
```

如果看到以下输出，说明配置成功：

```
 * Serving Flask app 'app'
 * Running on http://127.0.0.1:5000
[INFO] Storage backend initialized: R2
```

如果看到错误信息，检查：

1. 必需的环境变量是否都已设置
2. 凭证是否正确
3. 网络连接是否正常

## 故障排除

### 环境变量未被读取

确保：

1. `.env` 文件在项目根目录
2. 变量名称正确（区分大小写）
3. 没有多余的空格或引号

### 连接存储后端失败

检查：

1. 网络连接是否正常
2. 凭证是否有效
3. 防火墙是否阻止出站连接
4. 存储桶是否存在

### 公开 URL 不可用

确保：

1. 已配置公开 URL（可选）
2. 存储桶允许公开访问
3. CDN（如有）已配置

## 下一步

- [环境变量详解](./environment.md) - 每个环境变量的详细说明
- [部署指南](./deployment.md) - 生产环境部署
- [存储后端指南](../storage/) - 详细的后端配置指南
