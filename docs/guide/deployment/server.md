---
title: 服务器部署
createTime: 2025/11/09 00:26:55
permalink: /guide/deployment/server
---

在自有或云服务器上部署 Cloud Index 的完整指南。

## 优势

- ✅ 完全自主可控
- ✅ 无运营商限制
- ✅ 成本可预测
- ✅ 性能稳定
- ✅ 支持自定义配置
- ✅ 适合生产环境

## 前置要求

- Linux 服务器（推荐 Ubuntu 20.04 LTS 或更新版本）
- Python 3.9+ 已安装
- pip 或 poetry 包管理器
- 服务器可访问互联网
- 存储后端配置（R2、S3 或 GitHub）
- （可选）Nginx 反向代理
- （可选）SSL 证书

## 快速开始（5 分钟）

### 第 1 步：连接到服务器

```bash
ssh user@your-server-ip
```

### 第 2 步：下载项目

```bash
cd /opt
git clone https://github.com/RhenCloud/Cloud-Index.git
cd Cloud-Index
```

### 第 3 步：安装依赖

```bash
# 更新系统包
sudo apt-get update && sudo apt-get upgrade -y

# 安装 Python 和必要工具
sudo apt-get install -y python3 python3-pip python3-venv git

# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 安装项目依赖
pip install -r requirements.txt
```

### 第 4 步：配置环境变量

创建 `.env` 文件：

```bash
cp .env.example .env
nano .env
```

编辑 `.env` 文件，配置你的存储后端：

```env
# 基础配置
STORAGE_TYPE=r2
FLASK_ENV=production
FLASK_RUN_HOST=0.0.0.0
FLASK_RUN_PORT=5000

# R2 配置（选择一种）
R2_ENDPOINT_URL=https://your-account-id.r2.cloudflarestorage.com
R2_BUCKET_NAME=your-bucket-name
ACCESS_KEY_ID=your_access_key
SECRET_ACCESS_KEY=your_secret_key
R2_PUBLIC_URL=https://pub-your-bucket.r2.dev
```

### 第 5 步：启动应用

```bash
python app.py
```

访问 `http://your-server-ip:5000` 查看应用。

## 生产环境配置

### 使用 Gunicorn 和 Nginx

#### 1. 安装 Gunicorn

```bash
source venv/bin/activate
pip install gunicorn
```

#### 2. 创建 Systemd 服务文件

创建 `/etc/systemd/system/cloud-index.service`：

```bash
sudo nano /etc/systemd/system/cloud-index.service
```

写入以下内容：

```ini
[Unit]
Description=Cloud Index Application
After=network.target

[Service]
User=www-data
WorkingDirectory=/opt/Cloud-Index
Environment="PATH=/opt/Cloud-Index/venv/bin"
ExecStart=/opt/Cloud-Index/venv/bin/gunicorn \
    --workers 4 \
    --worker-class sync \
    --bind 127.0.0.1:5000 \
    --timeout 120 \
    --access-logfile /var/log/cloud-index/access.log \
    --error-logfile /var/log/cloud-index/error.log \
    app:app

Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

#### 3. 创建日志目录

```bash
sudo mkdir -p /var/log/cloud-index
sudo chown www-data:www-data /var/log/cloud-index
```

#### 4. 加载并启动服务

```bash
sudo systemctl daemon-reload
sudo systemctl start cloud-index
sudo systemctl enable cloud-index  # 开机自启

# 查看状态
sudo systemctl status cloud-index
```

#### 5. 配置 Nginx 反向代理

安装 Nginx：

```bash
sudo apt-get install -y nginx
```

创建 Nginx 配置文件 `/etc/nginx/sites-available/cloud-index`：

```bash
sudo nano /etc/nginx/sites-available/cloud-index
```

写入以下内容：

```nginx
server {
    listen 80;
    server_name your-domain.com;  # 替换为你的域名

    client_max_body_size 100M;  # 允许大文件上传

    # 重定向 HTTP 到 HTTPS（可选）
    # return 301 https://$server_name$request_uri;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # 连接超时配置
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # 静态文件缓存配置
    location /static/ {
        alias /opt/Cloud-Index/static/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
}
```

启用此配置：

```bash
sudo ln -s /etc/nginx/sites-available/cloud-index /etc/nginx/sites-enabled/
sudo nginx -t  # 测试配置
sudo systemctl restart nginx
```

### 配置 HTTPS（SSL/TLS）

#### 使用 Let's Encrypt 免费证书

安装 Certbot：

```bash
sudo apt-get install -y certbot python3-certbot-nginx
```

申请证书：

```bash
sudo certbot certonly --nginx -d your-domain.com
```

更新 Nginx 配置为 HTTPS：

```bash
sudo nano /etc/nginx/sites-available/cloud-index
```

修改为：

```nginx
server {
    listen 80;
    server_name your-domain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com;

    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;
    
    # SSL 安全配置
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;
    
    client_max_body_size 100M;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    location /static/ {
        alias /opt/Cloud-Index/static/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
}
```

重启 Nginx：

```bash
sudo systemctl restart nginx
```

设置证书自动续期：

```bash
sudo certbot renew --dry-run  # 测试
sudo systemctl enable certbot.timer  # 启用自动续期
```

## 环境变量配置

创建 `.env` 文件配置存储后端。参考 [环境配置](/guide/environment) 获取完整参数说明。

### R2 配置示例

```env
STORAGE_TYPE=r2
R2_ENDPOINT_URL=https://your-account-id.r2.cloudflarestorage.com
R2_BUCKET_NAME=your-bucket-name
ACCESS_KEY_ID=your_access_key
SECRET_ACCESS_KEY=your_secret_key
R2_PUBLIC_URL=https://pub-your-bucket.r2.dev
FLASK_ENV=production
THUMB_TTL_SECONDS=604800
```

### S3 配置示例

```env
STORAGE_TYPE=s3
S3_BUCKET_NAME=your-bucket-name
S3_REGION=us-east-1
ACCESS_KEY_ID=your_access_key
SECRET_ACCESS_KEY=your_secret_key
FLASK_ENV=production
```

### GitHub 配置示例

```env
STORAGE_TYPE=github
GITHUB_REPO_OWNER=your-username
GITHUB_REPO_NAME=your-repo-name
GITHUB_ACCESS_TOKEN=your_github_token
GITHUB_RAW_PROXY_URL=https://raw.ghproxy.com
FLASK_ENV=production
```

## 自动部署（GitHub Actions）

### 配置 SSH 部署

1. 在服务器上创建部署用户（可选）：

```bash
sudo useradd -m -s /bin/bash deploy
sudo usermod -aG sudo deploy
```

1. 生成 SSH 密钥对：

```bash
ssh-keygen -t rsa -b 4096 -f ~/.ssh/github-deploy -N ""
```

1. 将公钥添加到服务器 `authorized_keys`：

```bash
cat ~/.ssh/github-deploy.pub | ssh deploy@your-server "cat >> ~/.ssh/authorized_keys"
```

1. 在 GitHub 仓库中添加 Secret：

- `SERVER_HOST`: 服务器 IP 或域名
- `SERVER_USER`: 部署用户名
- `SERVER_SSH_KEY`: 私钥内容（`cat ~/.ssh/github-deploy`）
- `DEPLOY_PATH`: 部署路径，如 `/opt/Cloud-Index`

### 创建部署脚本

创建 `.github/workflows/deploy-to-server.yml`：

```yaml
name: Deploy to Server

on:
  push:
    branches:
      - main
  workflow_dispatch: {}

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout repository
        uses: actions/checkout@v4

      - name: Deploy to server
        uses: appleboy/ssh-action@master
        with:
          host: ${{ secrets.SERVER_HOST }}
          username: ${{ secrets.SERVER_USER }}
          key: ${{ secrets.SERVER_SSH_KEY }}
          script: |
            cd ${{ secrets.DEPLOY_PATH }}
            git pull origin main
            source venv/bin/activate
            pip install -r requirements.txt
            sudo systemctl restart cloud-index
            echo "✅ Deployment completed"
```

每次推送到 `main` 分支，应用会自动部署到服务器。

## 监控和维护

### 查看日志

```bash
# 查看实时日志
sudo journalctl -u cloud-index -f

# 查看应用日志
tail -f /var/log/cloud-index/error.log
tail -f /var/log/cloud-index/access.log
```

### 监控系统资源

```bash
# 查看内存和 CPU 使用
top

# 查看磁盘使用
df -h

# 查看网络连接
netstat -tulpn | grep 5000
```

### 定期更新

```bash
# 更新系统包
sudo apt-get update && sudo apt-get upgrade -y

# 更新应用依赖
source venv/bin/activate
pip install -r requirements.txt --upgrade
```

### 备份重要文件

```bash
# 定期备份环境配置
sudo cp /opt/Cloud-Index/.env /backup/.env.backup.$(date +%Y%m%d)

# 定期备份缓存
sudo tar -czf /backup/cache-$(date +%Y%m%d).tar.gz /opt/Cloud-Index/static/thumbs/
```

## 性能优化

### 1. Gunicorn Worker 配置

根据服务器 CPU 核心数调整 Worker 数：

```bash
# 查看 CPU 核心数
nproc

# 推荐配置：(2 × CPU 核心数) + 1
```

修改 `/etc/systemd/system/cloud-index.service` 中的 `--workers` 参数。

### 2. 启用缓存

增加缩略图缓存时间（`.env` 文件）：

```env
THUMB_TTL_SECONDS=2592000  # 30 天
```

### 3. 配置反向代理缓存

在 Nginx 配置中添加：

```nginx
http {
    proxy_cache_path /var/cache/nginx levels=1:2 keys_zone=my_cache:10m;

    server {
        location /static/ {
            proxy_cache my_cache;
            proxy_cache_valid 200 30d;
            add_header X-Cache-Status $upstream_cache_status;
        }
    }
}
```

### 4. 数据库连接池

如果使用数据库，配置连接池以提高性能。

## 故障排除

### 应用无法启动

检查：

```bash
# 查看错误日志
sudo journalctl -u cloud-index -n 50

# 验证环境变量
env | grep -E "STORAGE_|R2_|S3_|GITHUB_"

# 测试手动启动
source venv/bin/activate
python app.py
```

### Nginx 502 错误

检查：

```bash
# 验证应用是否运行
sudo systemctl status cloud-index

# 查看 Nginx 错误日志
sudo tail -f /var/log/nginx/error.log

# 检查 Nginx 配置
sudo nginx -t
```

### 内存不足

```bash
# 查看内存使用
free -h

# 调整 Gunicorn workers
# 在 /etc/systemd/system/cloud-index.service 中减少 workers 数量
```

### 存储无法连接

检查：

```bash
# 验证环境变量设置
grep -E "^(R2_|S3_|GITHUB_)" .env

# 测试连接
python -c "from app import app; app.test_client()"
```

## 安全建议

### 1. 防火墙配置

```bash
# 只允许 HTTP/HTTPS
sudo ufw allow 22/tcp   # SSH
sudo ufw allow 80/tcp   # HTTP
sudo ufw allow 443/tcp  # HTTPS
sudo ufw enable
```

### 2. 定期备份

```bash
# 创建备份脚本 backup.sh
#!/bin/bash
BACKUP_DIR="/backup/cloud-index"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

# 备份 .env 文件
cp /opt/Cloud-Index/.env $BACKUP_DIR/.env.$DATE

# 删除 7 天前的备份
find $BACKUP_DIR -name ".env.*" -mtime +7 -delete

# 使用 crontab 定期运行
# 0 2 * * * /path/to/backup.sh
```

### 3. SSH 安全

```bash
# 禁用密码登录
sudo nano /etc/ssh/sshd_config
# 设置 PasswordAuthentication no

# 更改 SSH 端口（可选）
# 设置 Port 2222

sudo systemctl restart ssh
```

### 4. 定期更新

```bash
# 启用自动安全更新
sudo apt-get install -y unattended-upgrades
sudo dpkg-reconfigure -plow unattended-upgrades
```

## 与 Docker 的对比

| 功能 | 直接部署 | Docker | Systemd |
|-----|---------|--------|---------|
| 部署难度 | 简单 | 中等 | 中等 |
| 系统开销 | 最小 | 需要容器 | 最小 |
| 隔离性 | 低 | 高 | 低 |
| 自动重启 | 需要配置 | 自动 | 自动 |
| 推荐用途 | 小型部署 | 团队开发 | 生产环境 |

## 常见问题

**Q: 如何更新应用代码？**

A: 使用 Git 拉取最新代码，然后重启服务：

```bash
cd /opt/Cloud-Index
git pull origin main
source venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart cloud-index
```

**Q: 如何处理长时间运行的大文件上传？**

A: 增加 Nginx 和 Gunicorn 的超时配置：

```nginx
# Nginx 配置
proxy_connect_timeout 300s;
proxy_send_timeout 300s;
proxy_read_timeout 300s;
```

```bash
# Gunicorn 配置
--timeout 300
```

**Q: 如何监控应用性能？**

A: 推荐安装监控工具：

```bash
# 使用 htop 监控实时资源
sudo apt-get install -y htop

# 使用 Prometheus 和 Grafana 构建完整监控（可选）
```

**Q: 生产环境推荐配置是什么？**

A:

- 4+ CPU 核心
- 8+ GB 内存
- 50+ GB SSD 存储
- 独立的存储后端（R2/S3）
- HTTPS 证书
- 定期备份策略

## 获取帮助

- 📖 [文档首页](/guide/introduction)
- 🐛 [提交 Issue](https://github.com/RhenCloud/Cloud-Index/issues)
- 💬 [讨论区](https://github.com/RhenCloud/Cloud-Index/discussions)
- 📧 Email: <i@rhen.cloud>

## 总结

服务器部署提供了最大的灵活性和控制权。通过 Nginx 反向代理、Systemd 自动管理和 GitHub Actions 自动部署，可以构建一个生产级的、高可用的应用系统！🚀

---

**下一步**：

- 查看 [Docker 部署](/guide/docker) 了解容器化部署方案
- 查看 [Vercel 部署](/guide/vercel) 了解 Serverless 部署方案
- 查看 [环境配置](/guide/environment) 了解所有配置选项
