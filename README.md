# Cloud-Index

一个支持多种云存储后端的文件管理、索引和浏览服务。

更多详细信息请访问 [项目文档](https://docs.cloud-index.rhen.cloud)

我在这个项目上至少花费了：

[![CodeTime Badge](https://shields.jannchie.com/endpoint?style=social&color=222&url=https%3A%2F%2Fapi.codetime.dev%2Fv3%2Fusers%2Fshield%3Fuid%3D34631%26project%3Dr2-index)](https://codetime.dev)
[![CodeTime Badge](https://shields.jannchie.com/endpoint?style=social&color=222&url=https%3A%2F%2Fapi.codetime.dev%2Fv3%2Fusers%2Fshield%3Fuid%3D34631%26project%3DCloudIndexDocs)](https://codetime.dev)

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

## 在线演示

你可以在在线演示中体验 Cloud Index 的主要功能（浏览、预览、上传、下载等）。

- Demo 地址：[https://demo.cloud-index.rhen.cloud](https://demo.cloud-index.rhen.cloud)
- Demo 地址：[https://r2.demo.cloud-index.rhen.cloud](https://r2.demo.cloud-index.rhen.cloud)（使用Cloudflare R2作为存储后端）
- Demo 地址：[https://github.demo.cloud-index.rhen.cloud](https://github.demo.cloud-index.rhen.cloud)（使用Github Repository作为存储后端）

## TODO

- [x] Github Repo 储存支持
- [ ] Github Release 储存支持
- [ ] Microsoft Onedrive 储存支持
- [ ] 基于数据库的用户/权限管理
- [ ] 操作日志记录
- [ ] Office Documents 预览支持
- [ ] 视频预览支持
- [ ] 文件夹打包下载支持

## 支持的存储后端

- **Cloudflare R2** - Cloudflare 的对象存储服务（S3 兼容）
- **Amazon S3** - Amazon S3 对象存储服务
- **GitHub Repository** - 基于 GitHub Repository 的存储服务
<!-- - **Github Release** - 基于 GitHub Release 的存储服务 -->

## 快速开始

### 1. 克隆项目

```bash
git clone https://github.com/RhenCloud/Cloud-Index.git
cd Cloud-Index
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

## 部署

### Vercel 部署

项目包含 `vercel.json` 配置文件，可直接部署到 Vercel：

1. 在 Vercel 中导入项目
2. 在 Vercel 项目设置中配置环境变量
3. 部署

## 配置说明

### Cloudflare R2 配置

```env
STORAGE_TYPE=r2

# R2 账户 ID
R2_ACCOUNT_ID=your-account-id

# R2 访问凭证
R2_ACCESS_KEY_ID=your_access_key_id
R2_SECRET_ACCESS_KEY=your_secret_access_key

# R2 存储桶配置
R2_BUCKET_NAME=your_bucket_name

# 可选：公共访问域名
R2_PUBLIC_DOMAIN=https://pub-your-bucket.r2.dev
```

### GitHub Repository 配置

```env
STORAGE_TYPE=github

# GitHub 仓库 (格式: owner/repo)
GITHUB_REPO=your-username/your-repo

# GitHub 个人访问令牌（需要 repo 权限）
# 获取方式：https://github.com/settings/tokens
GITHUB_TOKEN=ghp_your_token_here

# GitHub 分支名称（可选，默认: main）
GITHUB_BRANCH=main
```

## 项目结构

```bash
cloud-index/
├── app.py                 # Flask 应用主入口
├── config.py              # 统一配置管理
├── utils.py               # 工具函数模块
├── handlers/
│   └── routes.py         # 路由处理器
├── storages/             # 存储后端实现
│   ├── __init__.py
│   ├── base.py          # 基础存储类（抽象类）
│   ├── factory.py       # 存储工厂类
│   ├── r2.py            # Cloudflare R2 实现
│   └── github.py        # GitHub Repository 实现
├── templates/           # HTML 模板
│   ├── base.html
│   ├── index.html
│   └── footer.html
├── static/             # 静态资源
│   ├── css/
│   │   └── main.css
│   └── js/
│       └── main.js
├── .env.example        # 环境变量示例
├── pyproject.toml      # 项目配置和依赖
└── requirements.txt    # Python 依赖
```

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

### 本地开发

```bash
# 1. 克隆项目
git clone https://github.com/RhenCloud/Cloud-Index.git
cd Cloud-Index

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
- GitHub Repository

### Q: 如何添加新的存储后端？

A: 参考项目结构中的"添加新的存储后端"部分，继承 `BaseStorage` 并实现所有抽象方法即可。

## 贡献指南

欢迎为 Cloud-Index 做出贡献！无论是报告 Bug、提出新功能建议，还是直接提交代码，我们都非常感谢。

### 如何贡献

#### 1. 报告问题

如果你发现了 Bug 或有功能建议：

1. 在 [Issues](https://github.com/RhenCloud/Cloud-Index/issues) 页面搜索是否已有相关问题
2. 如果没有，创建新的 Issue，并提供：
   - **Bug 报告**：详细的复现步骤、预期行为、实际行为、环境信息（操作系统、Python 版本等）
   - **功能建议**：清晰的需求描述、使用场景、预期效果

#### 2. 提交代码

**基本流程**：

1. **Fork 项目**  
   点击 GitHub 页面右上角的 "Fork" 按钮

2. **克隆到本地**  

   ```bash
   git clone https://github.com/your-username/Cloud-Index.git
   cd Cloud-Index
   ```

3. **创建功能分支**  

   ```bash
   git checkout -b feature/your-feature-name
   # 或修复 Bug: git checkout -b fix/bug-description
   ```

4. **进行开发**  
   - 遵循现有的代码风格
   - 添加必要的注释
   - 确保代码能正常运行

5. **提交更改**  

   ```bash
   git add .
   git commit -m "feat: 添加某某功能"
   # 或 "fix: 修复某某问题"
   ```

6. **推送到 GitHub**  

   ```bash
   git push origin feature/your-feature-name
   ```

7. **创建 Pull Request**  
   - 在 GitHub 上打开你的 Fork
   - 点击 "New Pull Request"
   - 填写 PR 描述，说明你的更改内容和原因

**Commit 信息规范**（建议）：

- `feat:` 新功能
- `fix:` 修复 Bug
- `docs:` 文档更新
- `style:` 代码格式调整（不影响功能）
- `refactor:` 重构代码
- `test:` 添加或修改测试
- `chore:` 构建工具或辅助工具的变动

### 开发指南

#### 项目架构

项目采用 **策略模式** 和 **工厂模式**，使得添加新的存储后端非常简单：

```bash
存储抽象层 (BaseStorage)
    ↓
具体实现 (R2Storage, GitHubStorage, ...)
    ↓
工厂创建 (StorageFactory)
```

**核心组件**：

- **BaseStorage** (`storages/base.py`) - 定义存储后端的统一接口（抽象基类）
- **具体存储实现** (`storages/r2.py`, `storages/github.py`) - 实现特定存储的业务逻辑
- **StorageFactory** (`storages/factory.py`) - 根据环境变量创建对应的存储实例

#### 添加新的存储后端

如果你想支持新的存储服务（如 Google Cloud Storage、Azure Blob 等），按以下步骤操作：

##### **步骤 1：创建存储实现文件**

在 `storages/` 目录下创建新文件，例如 `gcs.py`：

```python
from storages.base import BaseStorage

class GCSStorage(BaseStorage):
    """Google Cloud Storage 实现"""
    
    def __init__(self):
        # 初始化 GCS 客户端
        pass
    
    # 实现所有抽象方法
    def list_objects(self, prefix=""):
        pass
    
    def get_object(self, key):
        pass
    
    # ... 其他方法
```

##### **步骤 2：实现所有抽象方法**

参考 `BaseStorage` 中定义的方法签名，实现以下方法：

- `list_objects()` - 列出文件和目录
- `get_object()` - 获取文件内容
- `get_object_info()` - 获取文件元数据
- `upload_file()` - 上传文件
- `delete_file()` - 删除文件
- `rename_file()` - 重命名文件
- `generate_presigned_url()` - 生成预签名 URL
- `get_public_url()` - 获取公共访问 URL
- 其他文件夹操作方法...

##### **步骤 3：在工厂中注册**

编辑 `storages/factory.py`，添加新的存储类型：

```python
from storages.gcs import GCSStorage

class StorageFactory:
    @staticmethod
    def get_storage():
        storage_type = os.getenv("STORAGE_TYPE", "r2")

        if storage_type == "gcs":
            return GCSStorage()
        # ... 其他类型
```

##### **步骤 4：添加配置示例**

在 `.env.example` 中添加新存储的配置说明：

```env
# Google Cloud Storage 配置
STORAGE_TYPE=gcs
GCS_PROJECT_ID=your-project-id
GCS_BUCKET_NAME=your-bucket
GCS_CREDENTIALS_PATH=/path/to/credentials.json
```

##### **步骤 5：更新文档**

- 在 README.md 的"支持的存储后端"部分添加新存储
- 在"配置说明"部分添加详细的配置步骤

#### 本地测试

开发完成后，请在本地测试：

```bash
# 1. 配置环境变量
cp .env.example .env
# 编辑 .env，设置你的存储配置

# 2. 安装依赖
pip install -r requirements.txt

# 3. 运行应用
python app.py

# 4. 测试功能
# 访问 http://localhost:5000
# 测试文件浏览、上传、下载、删除等功能
```

### 代码规范

- 使用 **4 个空格** 缩进（Python PEP 8 标准）
- 函数和方法添加 **docstring** 说明
- 变量和函数使用 **有意义的命名**
- 复杂逻辑添加 **注释说明**
- 保持代码简洁，遵循 **单一职责原则**

### 需要帮助？

如果在贡献过程中遇到问题：

- 查看 [项目文档](https://docs.cloud-index.rhen.cloud)
- 在 [Discussions](https://github.com/RhenCloud/Cloud-Index/discussions) 提问
- 通过 Issue 联系维护者

感谢你对 Cloud-Index 的贡献！🎉

## 许可证

MIT License
