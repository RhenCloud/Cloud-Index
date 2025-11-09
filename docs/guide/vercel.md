---
title: Vercel 部署
createTime: 2025/11/09 00:26:55
permalink: /guide/vercel
---
# Vercel 部署

在 Vercel 上快速部署 Cloud Index 的完整指南。

## 优势

- ✅ 零配置部署
- ✅ 自动 HTTPS
- ✅ 全球 CDN 加速
- ✅ 自动扩展
- ✅ 免费额度充足
- ✅ 与 GitHub 无缝集成

## 前置要求

- GitHub 账户
- Vercel 账户（[注册免费账户](https://vercel.com/signup)）
- 存储后端配置（R2、S3 或 GitHub）

## 部署步骤

### 第 1 步：Fork 项目

访问 [Cloud Index GitHub 仓库](https://github.com/RhenCloud/Cloud-Index)，点击 "Fork" 按钮。

### 第 2 步：连接到 Vercel

1. 登录 [Vercel 控制台](https://vercel.com/dashboard)
2. 点击 "Add New..." → "Project"
3. 点击 "Import Git Repository"
4. 连接 GitHub 账户
5. 选择你 Fork 的仓库

### 第 3 步：配置项目

在 Import 页面：

1. **Project Name** - 输入项目名称（如 `cloud-index`）
2. **Framework** - 选择 "Python" 或保持默认
3. **Root Directory** - 保持默认（根目录）

### 第 4 步：配置环境变量

点击 "Environment Variables"，添加以下变量：

**基础配置：**

```
STORAGE_TYPE = r2
```

**R2 存储配置：**

```
R2_ENDPOINT_URL = https://your-account-id.r2.cloudflarestorage.com
R2_BUCKET_NAME = your-bucket-name
ACCESS_KEY_ID = your_access_key
SECRET_ACCESS_KEY = your_secret_key
R2_PUBLIC_URL = https://pub-your-bucket.r2.dev
```

或 **S3 存储配置：**

```
STORAGE_TYPE = s3
S3_BUCKET_NAME = your-bucket-name
S3_REGION = us-east-1
ACCESS_KEY_ID = your_access_key
SECRET_ACCESS_KEY = your_secret_key
```

或 **GitHub 存储配置：**

```
STORAGE_TYPE = github
GITHUB_REPO_OWNER = your-username
GITHUB_REPO_NAME = your-repo-name
GITHUB_ACCESS_TOKEN = your_github_token
GITHUB_RAW_PROXY_URL = https://raw.ghproxy.com
```

**应用配置：**

```
FLASK_ENV = production
THUMB_TTL_SECONDS = 604800
```

### 第 5 步：部署

1. 检查配置无误
2. 点击 "Deploy" 按钮
3. 等待部署完成

部署完成后，Vercel 会提供一个 URL（如 `https://cloud-index.vercel.app`）

## 配置自定义域名

### 1. 添加域名

1. 进入项目设置 → "Domains"
2. 输入你的域名（如 `cloud.example.com`）
3. 点击 "Add"

### 2. 配置 DNS

Vercel 会提供 DNS 记录，按照说明在你的域名提供商处配置：

- **CNAME** 记录指向 Vercel
- 或使用 **A** 记录指向 Vercel IP

### 3. 验证和启用

DNS 生效后（通常需要几分钟到几小时），Vercel 会自动验证并启用 HTTPS。

## 自动部署

当你推送代码到 GitHub 时，Vercel 会自动部署新版本。

### 触发部署

提交代码到 main 分支：

```bash
git add .
git commit -m "Update configuration"
git push origin main
```

Vercel 会自动开始部署。你可以在 Vercel Dashboard 中查看部署进度。

## 更新配置

### 方式一：通过 Vercel Dashboard

1. 进入项目设置
2. 选择 "Environment Variables"
3. 编辑相应变量
4. 需要重新部署时，点击 Redeploy

### 方式二：通过代码

在项目根目录创建 `vercel.json` 文件（已包含）：

```json
{
    "version": 2,
    "builds": [
        {
            "src": "app.py",
            "use": "@vercel/python"
        },
        {
            "src": "/static/**",
            "use": "@vercel/static"
        }
    ],
    "routes": [
        {
            "src": "/(.*)",
            "dest": "app.py"
        }
    ]
}
```

编辑后推送到 GitHub，Vercel 会自动重新部署。

## 日志查看

### 查看部署日志

1. 进入项目
2. 点击 "Deployments" 选项卡
3. 选择相应的部署
4. 查看 "Logs" 中的详细信息

### 查看实时日志

1. 进入项目
2. 点击 "Functions" 选项卡
3. 选择 `app.py`
4. 查看实时日志

### 使用 Vercel CLI

```bash
# 安装 CLI
npm i -g vercel

# 登录
vercel login

# 查看日志
vercel logs <project-url>

# 实时日志
vercel logs <project-url> --follow
```

## 性能优化

### 1. 启用 Edge Caching

在 `vercel.json` 中配置缓存头：

```json
"routes": [
    {
        "src": "/static/(.*)",
        "headers": {
            "cache-control": "public, max-age=86400, immutable"
        },
        "dest": "app.py"
    },
    {
        "src": "/(.*)",
        "dest": "app.py"
    }
]
```

### 2. 优化缓存设置

增大缩略图缓存时间（在 Environment Variables）：

```
THUMB_TTL_SECONDS = 2592000  # 30 天
```

### 3. 使用 Vercel Analytics

1. 进入项目设置
2. 选择 "Analytics"
3. 启用 Vercel Analytics

可以实时监控应用性能和用户行为。

## 监控和告警

### Vercel Monitoring

在项目设置中配置告警：

1. 进入项目 → "Settings" → "Notifications"
2. 设置部署失败时的通知
3. 选择通知方式（Email、Slack 等）

### 错误追踪

Vercel 自动集成错误追踪。通过以下方式查看：

1. 进入 "Functions" 选项卡
2. 查看错误率和详细错误信息

## 限制和配额

### 计算

- **免费版**: 100GB-Hours/月
- 每次冷启动 < 10 秒
- 单个函数最大执行时间 900 秒

### 存储

- **缓存**: 512MB（临时）
- **函数空间**: 50MB 代码

### 带宽

- **免费版**: 100GB/月

### 费用估算

假设月均 1 万次请求，每次执行 500ms：

- 计算: 5,000 秒 / 1,000 = 5GB-Hours（远低于 100GB 免费额度）
- **预计费用**: 免费 ✅

## 故障排除

### 部署失败

检查：

1. `vercel.json` 配置是否正确
2. `requirements.txt` 是否包含所有依赖
3. Python 版本是否兼容（推荐 3.9+）

### 环境变量未生效

1. 确保在 Environment Variables 中正确配置
2. 重新部署应用（Redeploy）
3. 清理浏览器缓存

### 冷启动慢

- Vercel 自动缓存函数以加速启动
- 增加使用频率会自动改善冷启动时间
- 无需手动优化

### 存储无法连接

检查：

1. 环境变量是否正确
2. 凭证是否有效
3. 防火墙/安全组是否允许访问

### 缓存空间不足

清理或减少缓存：

1. 减小缩略图生成质量
2. 减少缓存过期时间
3. 定期手动清理

## 成本优化建议

1. **使用 Cloudflare R2** 而不是 S3（成本更低）
2. **启用缓存** 减少存储访问次数
3. **监控使用量** 避免超限
4. **使用付费计划** 如果超过免费额度（$20/月 Pro 计划）

## 与本地开发保持同步

### 拉取最新变化

```bash
git pull origin main
```

### 测试本地更改

```bash
python app.py
# 访问 http://localhost:5000
```

### 推送到 Vercel

```bash
git add .
git commit -m "Bug fix or feature"
git push origin main
```

Vercel 会自动检测并部署。

## 回滚部署

如果新部署出现问题：

1. 进入项目 → "Deployments"
2. 选择之前的稳定版本
3. 点击 "Redeploy to Production"

应用会立即回滚到之前的版本。

## 获取帮助

- 📖 [Vercel 文档](https://vercel.com/docs)
- 🐛 [提交 Issue](https://github.com/RhenCloud/Cloud-Index/issues>)
- 💬 [讨论区](https://github.com/RhenCloud/Cloud-Index/discussions>)
- 📧 Email: <i@rhen.cloud>

## 总结

| 功能 | 本地 | Docker | Vercel |
|-----|------|--------|--------|
| 部署难度 | 简单 | 中等 | 简单 |
| 成本 | 自有服务器 | 中等 | 小 |
| 性能 | 取决于服务器 | 好 | 优秀 |
| 扩展性 | 有限 | 中等 | 自动 |
| 推荐用途 | 开发测试 | 生产环境 | 中小型应用 |

Vercel 最适合需要快速部署、无需运维的应用！🚀
