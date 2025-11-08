# R2-Index

一个支持多种云存储后端的文件管理、索引和浏览服务。

## 特性

- 📁 浏览和预览云存储中的文件
- 🖼️ 图片缩略图生成
- 🌐 公共访问 URL 支持
- 🔄 多存储后端支持（可扩展）
- ⬆️ 文件上传功能
- 🗑️ 文件删除功能
- ✏️ 文件/文件夹重命名
- 📂 创建文件夹
- 📋 文件/文件夹复制
- 🔄 文件/文件夹移动
- 📱 响应式界面，多种设备尺寸支持
- 🌙 深色模式支持

## TODO

- [] Github Repo 储存支持
- [] Github Release 储存支持
- [] 基于数据库的用户/权限管理
- [] 操作日志记录
- [] Office Documents 预览支持
- [] 视频预览支持
- [] 文件夹打包下载支持

## 支持的存储后端

- **Cloudflare R2** - Cloudflare 的对象存储服务（S3 兼容）
- **Amazon S3** - Amazon S3 对象存储服务
<!-- - **Github Repo** - 基于 GitHub Repository 的存储服务 -->

## 快速开始

### 1. 克隆项目

```bash
git clone https://github.com/RhenCloud/R2-Index.git
cd R2-Index
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 配置环境变量

复制 `.env.example` 到 `.env` 并填写配置：

```bash
cp .env.example .env
```

### 4. 运行应用

```bash
python app.py
```

## 配置说明

### 选择存储类型

在 `.env` 文件中设置 `STORAGE_TYPE` 来选择存储后端：

```env
# 使用 Cloudflare R2
STORAGE_TYPE=r2

# 或使用腾讯云 cnb.cool
STORAGE_TYPE=cnbcool
```

### Cloudflare R2 配置

```env
STORAGE_TYPE=r2

# R2 访问凭证
ACCESS_KEY_ID=your_access_key_id
SECRET_ACCESS_KEY=your_secret_access_key

# R2 存储桶配置
R2_BUCKET_NAME=your_bucket_name
R2_ENDPOINT_URL=https://your-account-id.r2.cloudflarestorage.com
R2_REGION=auto

# 可选：公共访问 URL
R2_PUBLIC_URL=https://pub-your-bucket.r2.dev

# 可选：预签名 URL 过期时间（秒）
R2_PRESIGN_EXPIRES=3600
```

## 项目结构

```
r2-index/
├── app.py                 # Flask 应用主入口
├── handlers/
│   └── routes.py         # 路由处理器
├── storages/             # 存储后端实现
│   ├── __init__.py
│   ├── base.py          # 基础存储类（抽象类）
│   ├── factory.py       # 存储工厂类
│   ├── r2.py            # Cloudflare R2 实现
│   └── cnbcool.py       # 腾讯云 cnb.cool 实现
├── templates/           # HTML 模板
│   ├── index.html
│   └── footer.html
├── static/             # 静态资源
│   └── thumbs/
├── .env.example        # 环境变量示例
└── requirements.txt    # Python 依赖
```

## 贡献

项目采用策略模式和工厂模式，使得添加新的存储后端变得简单：

1. **BaseStorage** - 定义存储后端的统一接口
2. **具体实现** (R2Storage, CnbCoolStorage) - 实现具体的存储逻辑
3. **StorageFactory** - 根据配置创建对应的存储实例

### 添加新的存储后端

1. 在 `storages/` 目录下创建新的存储实现文件
2. 继承 `BaseStorage` 并实现所有抽象方法
3. 在 `StorageFactory` 中添加对应的创建逻辑
4. 更新 `.env.example` 添加新的配置项

## API 路由

- `GET /` - 浏览根目录
- `GET /<path:prefix_path>` - 浏览指定目录
- `GET /file/<path:file_path>` - 获取文件内容
- `GET /thumb/<path:file_path>` - 获取图片缩略图
- `POST /upload` - 上传文件
- `DELETE /delete/<path:file_path>` - 删除文件
- `POST /rename/<path:old_key>` - 重命名文件
- `DELETE /delete_folder/<path:prefix>` - 删除文件夹
- `POST /rename_folder/<path:old_prefix>` - 重命名文件夹
- `POST /copy` - 复制文件或文件夹
- `POST /move` - 移动文件或文件夹
- `POST /create_folder` - 创建文件夹

详细 API 文档：[API 文档](docs/api.md)

## 部署

### Vercel 部署

项目包含 `vercel.json` 配置文件，可直接部署到 Vercel：

1. 在 Vercel 中导入项目
2. 在 Vercel 项目设置中配置环境变量
3. 部署

### Docker 部署

您也可以使用 Docker 部署此应用：

```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "app.py"]
```

构建和运行：

```bash
docker build -t r2-index .
docker run -p 5000:5000 --env-file .env r2-index
```

### 本地开发

```bash
# 1. 克隆项目
git clone https://github.com/RhenCloud/R2-Index.git
cd R2-Index

# 2. 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. 安装依赖
pip install -r requirements.txt

# 4. 配置环境变量
cp .env.example .env
# 编辑 .env 文件，填入你的存储配置

# 5. 运行应用
python app.py
```

应用将在 `http://localhost:5000` 启动。

## 技术栈

- **Flask** - Web 框架
- **Boto3** - AWS SDK（用于 S3 兼容存储）
- **Pillow** - 图片处理
- **Python-dotenv** - 环境变量管理

## 常见问题

### Q: 如何限制上传文件大小？

A: 在 `handlers/routes.py` 中的 `upload()` 函数中添加文件大小检查：

```python
@main_route.route("/upload", methods=["POST"])
def upload():
    file = request.files["file"]
    
    # 限制文件大小为 100MB
    MAX_FILE_SIZE = 100 * 1024 * 1024
    if len(file.read()) > MAX_FILE_SIZE:
        return jsonify({"success": False, "error": "File too large"}), 413
    
    file.seek(0)  # 重置文件指针
    # ... 继续上传逻辑
```

### Q: 如何添加访问认证？

A: 参考 [API 文档](docs/api.md) 的"安全建议"部分，可以添加基于 Token 的简单认证。

### Q: 支持哪些图片格式的缩略图生成？

A: 支持 `jpg`, `jpeg`, `png`, `gif`, `bmp`, `webp`, `svg`, `ico` 等常见格式。

### Q: 如何在深色模式和浅色模式间切换？

A: 点击页面顶部的月亮/太阳图标即可切换。设置将保存在本地存储中。

### Q: 支持哪些存储后端？

A: 当前支持：

- Cloudflare R2（推荐）
- Amazon S3
- GitHub Repository（通过 cnb.cool）

### Q: 如何添加新的存储后端？

A: 参考项目结构中的"添加新的存储后端"部分，继承 `BaseStorage` 并实现所有抽象方法即可。

## 贡献指南

欢迎提交 Issue 和 Pull Request！

1. Fork 项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 许可证

MIT License
