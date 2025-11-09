---
title: 环境配置
createTime: 2025/11/09 00:26:55
permalink: /guide/environment
---
# 环境变量完整参考

本文档列出了 Cloud Index 支持的所有环境变量及其详细说明。

## 环境变量表

### 核心配置

| 变量名 | 类型 | 必需 | 默认值 | 说明 |
|-------|------|------|-------|------|
| `STORAGE_TYPE` | string | ✅ | - | 存储后端类型：`r2`、`s3`、`github` |
| `FLASK_ENV` | string | ❌ | development | Flask 环境：`development` 或 `production` |
| `FLASK_DEBUG` | bool | ❌ | 0 | 调试模式（0 或 1） |
| `FLASK_RUN_HOST` | string | ❌ | 127.0.0.1 | 应用监听地址 |
| `FLASK_RUN_PORT` | int | ❌ | 5000 | 应用监听端口 |

### R2 配置

| 变量名 | 类型 | 必需 | 说明 |
|-------|------|------|------|
| `R2_ENDPOINT_URL` | string | ✅ | R2 端点 URL（包含 Account ID） |
| `R2_BUCKET_NAME` | string | ✅ | R2 存储桶名称 |
| `R2_REGION` | string | ❌ | 区域代码，R2 通常使用 `auto` |
| `R2_PUBLIC_URL` | string | ❌ | 公开访问 URL（用于生成分享链接） |
| `R2_PRESIGN_EXPIRES` | int | ❌ | 3600 | 预签名 URL 有效期（秒） |
| `ACCESS_KEY_ID` | string | ✅ | R2 API Token ID |
| `SECRET_ACCESS_KEY` | string | ✅ | R2 API Token Secret |

### S3 配置

| 变量名 | 类型 | 必需 | 说明 |
|-------|------|------|------|
| `S3_BUCKET_NAME` | string | ✅ | S3 存储桶名称 |
| `S3_REGION` | string | ✅ | AWS 区域代码（如 `us-east-1`） |
| `S3_ENDPOINT_URL` | string | ❌ | 自定义 S3 端点（默认 AWS 官方） |
| `S3_PUBLIC_URL` | string | ❌ | 公开访问 URL |
| `S3_PRESIGN_EXPIRES` | int | ❌ | 3600 | 预签名 URL 有效期（秒） |
| `ACCESS_KEY_ID` | string | ✅ | AWS Access Key ID |
| `SECRET_ACCESS_KEY` | string | ✅ | AWS Secret Access Key |

### GitHub 配置

| 变量名 | 类型 | 必需 | 说明 |
|-------|------|------|------|
| `GITHUB_REPO_OWNER` | string | ✅ | GitHub 用户名或组织名 |
| `GITHUB_REPO_NAME` | string | ✅ | GitHub 仓库名称 |
| `GITHUB_ACCESS_TOKEN` | string | ✅ | GitHub Personal Access Token |
| `GITHUB_BRANCH` | string | ❌ | 使用的分支，默认 `main` |
| `GITHUB_RAW_PROXY_URL` | string | ❌ | Raw 内容代理 URL（国内加速） |
| `GITHUB_PRESIGN_EXPIRES` | int | ❌ | 3600 | 预签名 URL 有效期（秒） |

### 缓存配置

| 变量名 | 类型 | 必需 | 默认值 | 说明 |
|-------|------|------|-------|------|
| `THUMB_TTL_SECONDS` | int | ❌ | 3600 | 缩略图缓存过期时间（秒） |
| `CACHE_DIR` | string | ❌ | static/thumbs | 缓存目录路径 |

### 日志配置

| 变量名 | 类型 | 必需 | 默认值 | 说明 |
|-------|------|------|-------|------|
| `LOG_LEVEL` | string | ❌ | INFO | 日志级别（DEBUG/INFO/WARNING/ERROR） |
| `LOG_FILE` | string | ❌ | - | 日志文件路径 |

## 详细说明

### STORAGE_TYPE

**类型**: String  
**必需**: Yes  
**可选值**:

- `r2` - Cloudflare R2
- `s3` - Amazon S3  
- `github` - GitHub 仓库
- `github-release` - GitHub Release（开发中）

**示例**:

```env
STORAGE_TYPE=r2
```

### FLASK_ENV

**类型**: String  
**必需**: No  
**默认**: development  
**可选值**:

- `development` - 开发模式（启用自动重载、详细错误日志）
- `production` - 生产模式（性能优化、最小化日志）

**示例**:

```env
FLASK_ENV=production
```

### FLASK_DEBUG

**类型**: Integer (0 or 1)  
**必需**: No  
**默认**: 0  
**说明**: 启用 Flask 调试器和代码热加载（仅用于开发）

**示例**:

```env
FLASK_DEBUG=1
```

⚠️ **警告**: 不要在生产环境启用调试模式！

### FLASK_RUN_HOST

**类型**: String  
**必需**: No  
**默认**: 127.0.0.1  
**说明**: 应用监听的 IP 地址

**常用值**:

```env
FLASK_RUN_HOST=0.0.0.0      # 监听所有网络接口（推荐用于部署）
FLASK_RUN_HOST=127.0.0.1    # 仅本地访问（开发用）
FLASK_RUN_HOST=192.168.1.10 # 监听特定 IP
```

### FLASK_RUN_PORT

**类型**: Integer  
**必需**: No  
**默认**: 5000  
**说明**: 应用监听的端口号

**示例**:

```env
FLASK_RUN_PORT=8080         # 使用 8080 端口
FLASK_RUN_PORT=80           # 使用 HTTP 默认端口
```

### ACCESS_KEY_ID 和 SECRET_ACCESS_KEY

**类型**: String  
**必需**: Yes（对于 R2 和 S3）  
**说明**: 云存储服务的 API 凭证

⚠️ **安全提示**:

- ✅ 在 `.env` 文件中存储凭证
- ✅ 将 `.env` 加入 `.gitignore`
- ❌ 不要在代码中硬编码凭证
- ❌ 不要上传 `.env` 到 Git
- ❌ 不要在日志中打印凭证

**示例**:

```env
ACCESS_KEY_ID=abc123xyz789
SECRET_ACCESS_KEY=def456uvw789ghi
```

### R2_ENDPOINT_URL

**类型**: String  
**必需**: Yes（对于 R2）  
**格式**: `https://<account-id>.r2.cloudflarestorage.com`  
**说明**: Cloudflare R2 API 端点

**获取方式**: 在 Cloudflare 控制面板 R2 部分查看

**示例**:

```env
R2_ENDPOINT_URL=https://a1b2c3d4e5f6g7h8i.r2.cloudflarestorage.com
```

### R2_BUCKET_NAME

**类型**: String  
**必需**: Yes（对于 R2）  
**说明**: R2 存储桶名称

**示例**:

```env
R2_BUCKET_NAME=my-storage
```

### R2_PUBLIC_URL

**类型**: String  
**必需**: No  
**说明**: R2 公开访问 URL，用于生成可分享的文件链接

**格式**: `https://pub-<bucket-name>.r2.dev`  

**获取方式**: 在 Cloudflare 控制面板 R2 存储桶设置中配置自定义域

**示例**:

```env
R2_PUBLIC_URL=https://pub-my-storage.r2.dev
```

### S3_REGION

**类型**: String  
**必需**: Yes（对于 S3）  
**说明**: AWS 区域代码

**常用值**:

```
us-east-1      美国东部（N. Virginia）
us-west-2      美国西部（Oregon）
eu-west-1      欧洲（Ireland）
ap-northeast-1 亚太（Tokyo）
ap-southeast-1 亚太（Singapore）
cn-north-1     中国（北京）
```

**示例**:

```env
S3_REGION=ap-northeast-1
```

### GITHUB_REPO_OWNER

**类型**: String  
**必需**: Yes（对于 GitHub）  
**说明**: GitHub 用户名或组织名

**示例**:

```env
GITHUB_REPO_OWNER=myusername
GITHUB_REPO_OWNER=my-organization  # 组织名
```

### GITHUB_ACCESS_TOKEN

**类型**: String  
**必需**: Yes（对于 GitHub）  
**格式**: `ghp_xxxxxxxxxxxxxxxxxxxxx`  
**说明**: GitHub Personal Access Token

⚠️ **安全提示**: Token 具有访问仓库的权限，保护好它！

### GITHUB_RAW_PROXY_URL

**类型**: String  
**必需**: No  
**说明**: GitHub Raw 文件内容的代理 URL（用于加速国内访问）

**推荐代理服务**:

```
https://raw.ghproxy.com/     国内加速（推荐）
https://ghproxy.com/         国内加速
https://raw.githubusercontent.com/ 官方（无代理）
```

**示例**:

```env
GITHUB_RAW_PROXY_URL=https://raw.ghproxy.com
```

### THUMB_TTL_SECONDS

**类型**: Integer  
**必需**: No  
**默认**: 3600  
**说明**: 生成的缩略图缓存过期时间（秒）

**常用值**:

```
3600    1 小时
86400   1 天
604800  1 周
2592000 30 天
```

**示例**:

```env
THUMB_TTL_SECONDS=86400  # 缩略图缓存 1 天
```

### LOG_LEVEL

**类型**: String  
**必需**: No  
**默认**: INFO  
**可选值**: DEBUG, INFO, WARNING, ERROR, CRITICAL

**示例**:

```env
LOG_LEVEL=DEBUG     # 开发环境
LOG_LEVEL=WARNING   # 生产环境
```

## 快速参考

### 最小配置（R2）

```env
STORAGE_TYPE=r2
ACCESS_KEY_ID=your_key
SECRET_ACCESS_KEY=your_secret
R2_ENDPOINT_URL=https://account.r2.cloudflarestorage.com
R2_BUCKET_NAME=mybucket
```

### 最小配置（S3）

```env
STORAGE_TYPE=s3
ACCESS_KEY_ID=your_key
SECRET_ACCESS_KEY=your_secret
S3_BUCKET_NAME=mybucket
S3_REGION=us-east-1
```

### 最小配置（GitHub）

```env
STORAGE_TYPE=github
GITHUB_REPO_OWNER=myusername
GITHUB_REPO_NAME=my-storage
GITHUB_ACCESS_TOKEN=ghp_xxx
```

## 验证配置

运行以下命令验证环境变量是否正确加载：

```bash
python -c "import os; from dotenv import load_dotenv; load_dotenv(); print('STORAGE_TYPE:', os.getenv('STORAGE_TYPE'))"
```

## 相关文档

- [配置说明](./configuration.md) - 配置指南
- [部署指南](./deployment.md) - 生产部署
- [存储后端指南](../storage/) - 各后端详细配置
