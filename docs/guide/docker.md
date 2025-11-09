---
title: Docker 部署
createTime: 2025/11/09 00:26:55
permalink: /guide/docker
---
# Docker 部署

详细的 Docker 部署指南。

## 前置要求

- Docker 已安装（[获取 Docker](https://docs.docker.com/get-docker/)）
- Docker Compose 已安装（通常随 Docker Desktop 一同安装）
- 基本的 Docker 命令行知识

## 快速开始

### 1. 构建镜像

```bash
git clone https://github.com/RhenCloud/Cloud-Index.git
cd Cloud Index

# 构建镜像
docker build -t Cloud Index:latest .
```

### 2. 运行容器

```bash
docker run -d \
  --name Cloud Index \
  -p 5000:5000 \
  -e STORAGE_TYPE=r2 \
  -e R2_ENDPOINT_URL=https://account.r2.cloudflarestorage.com \
  -e ACCESS_KEY_ID=your_key \
  -e SECRET_ACCESS_KEY=your_secret \
  -e R2_BUCKET_NAME=your_bucket \
  Cloud Index:latest
```

### 3. 访问应用

打开浏览器访问 `http://localhost:5000`

## Docker Compose 部署

### 基础配置

创建 `docker-compose.yml`：

```yaml
version: '3.8'

services:
  Cloud Index:
    build: .
    container_name: Cloud Index
    ports:
      - "5000:5000"
    environment:
      STORAGE_TYPE: r2
      R2_ENDPOINT_URL: https://account.r2.cloudflarestorage.com
      R2_BUCKET_NAME: your-bucket
      ACCESS_KEY_ID: your_key
      SECRET_ACCESS_KEY: your_secret
      FLASK_ENV: production
    volumes:
      - ./cache:/app/static/thumbs
    restart: always
```

启动服务：

```bash
docker-compose up -d
docker-compose logs -f
```

### 完整配置（含 Nginx）

```yaml
version: '3.8'

services:
  app:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: Cloud Index-app
    environment:
      STORAGE_TYPE: r2
      R2_ENDPOINT_URL: ${R2_ENDPOINT_URL}
      R2_BUCKET_NAME: ${R2_BUCKET_NAME}
      ACCESS_KEY_ID: ${ACCESS_KEY_ID}
      SECRET_ACCESS_KEY: ${SECRET_ACCESS_KEY}
      FLASK_ENV: production
      THUMB_TTL_SECONDS: 86400
    volumes:
      - app-cache:/app/static/thumbs
      - app-logs:/app/logs
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:5000/"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 10s
    networks:
      - r2-network

  nginx:
    image: nginx:alpine
    container_name: Cloud Index-nginx
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./ssl:/etc/nginx/ssl:ro
      - ./cache:/app/static/thumbs:ro
    depends_on:
      - app
    restart: unless-stopped
    networks:
      - r2-network

volumes:
  app-cache:
  app-logs:

networks:
  r2-network:
    driver: bridge
```

## Dockerfile 详解

标准的 Dockerfile 配置：

```dockerfile
# 使用官方 Python 运行时作为基础镜像
FROM python:3.11-slim

# 设置工作目录
WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    libjpeg-dev \
    zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .

# 安装 Python 依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY . .

# 设置环境变量
ENV FLASK_APP=app.py
ENV FLASK_ENV=production
ENV FLASK_RUN_HOST=0.0.0.0

# 暴露端口
EXPOSE 5000

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:5000/ || exit 1

# 启动应用
CMD ["python", "app.py"]
```

## 环境变量配置

### 方式一：直接在命令行指定

```bash
docker run -d \
  --name Cloud Index \
  -p 5000:5000 \
  -e STORAGE_TYPE=r2 \
  -e R2_ENDPOINT_URL=https://account.r2.cloudflarestorage.com \
  -e R2_BUCKET_NAME=my-bucket \
  -e ACCESS_KEY_ID=key123 \
  -e SECRET_ACCESS_KEY=secret456 \
  Cloud Index:latest
```

### 方式二：使用环境文件

创建 `.env.docker`：

```env
STORAGE_TYPE=r2
R2_ENDPOINT_URL=https://account.r2.cloudflarestorage.com
R2_BUCKET_NAME=my-bucket
ACCESS_KEY_ID=key123
SECRET_ACCESS_KEY=secret456
FLASK_ENV=production
THUMB_TTL_SECONDS=86400
```

运行时指定：

```bash
docker run -d \
  --name Cloud Index \
  -p 5000:5000 \
  --env-file .env.docker \
  Cloud Index:latest
```

### 方式三：Docker Compose 环境文件

创建 `.env`，`docker-compose.yml` 自动读取：

```bash
cp .env.example .env
# 编辑 .env 文件

docker-compose up -d
```

## 数据卷管理

### 挂载缓存目录

```bash
# 本地缓存
docker run -d \
  --name Cloud Index \
  -p 5000:5000 \
  -v $(pwd)/cache:/app/static/thumbs \
  --env-file .env.docker \
  Cloud Index:latest

# 命名卷
docker volume create r2-cache
docker run -d \
  --name Cloud Index \
  -p 5000:5000 \
  -v r2-cache:/app/static/thumbs \
  --env-file .env.docker \
  Cloud Index:latest
```

### 挂载日志目录

```bash
docker run -d \
  --name Cloud Index \
  -p 5000:5000 \
  -v $(pwd)/logs:/app/logs \
  -v $(pwd)/cache:/app/static/thumbs \
  --env-file .env.docker \
  Cloud Index:latest
```

## 网络配置

### 单容器模式

```bash
docker run -d \
  --name Cloud Index \
  -p 5000:5000 \
  --env-file .env.docker \
  Cloud Index:latest
```

### Docker Compose 网络

```yaml
networks:
  r2-network:
    driver: bridge
```

容器内相互通信：

```yaml
services:
  app:
    networks:
      - r2-network
  nginx:
    depends_on:
      - app
    networks:
      - r2-network
```

访问 `http://app:5000` 时，Nginx 容器可以连接到应用容器。

## 常用命令

### 镜像操作

```bash
# 列出镜像
docker images

# 删除镜像
docker rmi Cloud Index:latest

# 标记镜像
docker tag Cloud Index:v1.0

# 推送到仓库
docker push myrepo/Cloud Index:v1.0

# 构建带标签的镜像
docker build -t Cloud Index:v1.0 .
```

### 容器操作

```bash
# 列出运行中的容器
docker ps

# 列出所有容器
docker ps -a

# 查看容器日志
docker logs Cloud Index
docker logs -f Cloud Index  # 实时日志
docker logs --tail 100 Cloud Index  # 最后 100 行

# 进入容器
docker exec -it Cloud Index bash

# 停止容器
docker stop Cloud Index

# 启动容器
docker start Cloud Index

# 重启容器
docker restart Cloud Index

# 删除容器
docker rm Cloud Index  # 容器必须已停止

# 查看容器统计信息
docker stats Cloud Index
```

### Docker Compose 操作

```bash
# 启动所有服务
docker-compose up -d

# 停止所有服务
docker-compose down

# 查看日志
docker-compose logs -f

# 查看特定服务日志
docker-compose logs -f app

# 重启服务
docker-compose restart

# 构建镜像
docker-compose build

# 删除卷
docker-compose down -v
```

## 生产部署最佳实践

### 1. 使用数据卷持久化存储

```yaml
volumes:
  app-cache:
    driver: local
  app-logs:
    driver: local

services:
  app:
    volumes:
      - app-cache:/app/static/thumbs
      - app-logs:/app/logs
```

### 2. 设置资源限制

```yaml
services:
  app:
    resources:
      limits:
        cpus: '1'
        memory: 512M
      reservations:
        cpus: '0.5'
        memory: 256M
```

### 3. 配置健康检查

```yaml
services:
  app:
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:5000/"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 10s
```

### 4. 日志驱动配置

```yaml
services:
  app:
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
```

### 5. 重启策略

```yaml
services:
  app:
    restart: unless-stopped  # 推荐值
    # unless-stopped: 容器异常退出时重启，停止后不重启
    # always: 总是重启
    # on-failure: 仅在非 0 退出码时重启
    # no: 不自动重启
```

## 监控和维护

### 查看容器资源使用

```bash
# 实时监控
docker stats Cloud Index

# 查看完整统计信息
docker stats --no-stream Cloud Index
```

### 清理无用资源

```bash
# 清理停止的容器
docker container prune

# 清理无用的镜像
docker image prune

# 清理无用的数据卷
docker volume prune

# 一次性清理所有无用资源
docker system prune -a
```

### 备份数据卷

```bash
# 备份名称为 r2-cache 的卷
docker run --rm \
  -v r2-cache:/data \
  -v $(pwd):/backup \
  ubuntu \
  tar czf /backup/r2-cache.tar.gz -C /data .

# 恢复
docker run --rm \
  -v r2-cache:/data \
  -v $(pwd):/backup \
  ubuntu \
  tar xzf /backup/r2-cache.tar.gz -C /data
```

## 故障排除

### 容器无法启动

```bash
# 查看详细错误日志
docker logs Cloud Index

# 进入容器调试
docker run -it --rm Cloud Index:latest bash
```

### 端口已被占用

```bash
# 查看占用端口的进程
lsof -i :5000

# 使用其他端口
docker run -d -p 8080:5000 Cloud Index:latest
```

### 卷权限问题

```bash
# 检查卷权限
docker inspect r2-cache

# 修复权限（进入容器操作）
docker exec Cloud Index chmod -R 755 /app/static/thumbs
```

### 内存溢出

```bash
# 设置内存限制
docker run -d \
  --memory=512m \
  --memory-swap=1g \
  Cloud Index:latest

# 清理缓存
docker exec Cloud Index rm -rf /app/static/thumbs/*
```

## 参考资源

- [Docker 官方文档](https://docs.docker.com/)
- [Docker Compose 文件参考](https://docs.docker.com/compose/compose-file/)
- [Best practices for writing Dockerfiles](https://docs.docker.com/develop/dev-best-practices/dockerfile_best-practices/)
