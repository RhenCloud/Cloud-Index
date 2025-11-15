---
title: OneDrive
createTime: 2025/11/15 00:00:00
permalink: /storage/onedrive
---

使用 Microsoft OneDrive 作为存储后端的详细配置。

## 概述

OneDrive 是微软提供的云存储服务，与 Cloud Index 完美集成：

- 💼 企业级可靠性
- 🔄 自动同步和备份
- 🌐 全球访问
- 🔐 强大的权限管理
- 📊 丰富的文件管理功能
- 🖼️ 图片缩略图和预览

## 为什么选择 OneDrive？

### 优势

1. **免费存储空间** - 个人用户 5GB 免费，Microsoft 365 订阅用户 1TB+
2. **自动同步** - 本地文件自动同步到云端
3. **Office 集成** - 与 Office 套件完美集成，在线编辑
4. **版本历史** - 自动保存文件版本，轻松恢复
5. **跨平台支持** - Windows、Mac、iOS、Android 全平台支持
6. **企业级安全** - 支持企业账户，强大的安全控制

### 限制

- 免费用户存储空间有限（5GB）
- 需要 Microsoft 账户
- 文件大小限制（个人版单文件最大 250GB）

### 推荐用途

- 📄 个人文档和笔记
- 🖼️ 照片和图片库
- 🎥 视频文件
- 📁 项目文件管理
- 👥 团队协作文件
- 🔄 需要跨设备同步的文件

## 账户设置

### 1. 创建 Microsoft 账户

如果还没有 Microsoft 账户，访问 [Microsoft](https://signup.live.com) 创建一个免费账户。

### 2. 注册 Azure 应用

要使用 OneDrive API，需要在 Microsoft Entra（Azure AD）中注册应用：

1. 访问 [Azure Portal](https://portal.azure.com)
2. 搜索 "Microsoft Entra ID"（或 "Azure Active Directory"）
3. 左侧菜单选择 "应用注册"
4. 点击 "新注册"
5. 填写应用信息：
   - **名称**：例如 `Cloud Index`
   - **支持的账户类型**：选择 "任何组织目录中的账户和个人 Microsoft 账户"
   - **重定向 URI**：选择 "Web"，输入 `http://localhost:5000/callback`
6. 点击 "注册"

### 3. 配置应用权限

注册完成后，配置 API 权限：

1. 进入应用详情页
2. 左侧菜单选择 "API 权限"
3. 点击 "添加权限"
4. 选择 "Microsoft Graph"
5. 选择 "委托的权限"
6. 搜索并添加以下权限：
   - ✅ **Files.ReadWrite.All** - 读写所有文件（必需）
   - ✅ **offline_access** - 获取刷新令牌（必需）
   - ❌ openid, profile - 可选，用于获取用户信息
7. 点击 "添加权限"
8. 点击 "代表 XXX 授予管理员同意"（如果是管理员）

### 4. 创建客户端密钥

1. 左侧菜单选择 "证书和密码"
2. 点击 "新客户端密码"
3. 输入描述（例如 `Cloud Index Secret`）
4. 选择过期时间（推荐 "24 个月"）
5. 点击 "添加"
6. **立即复制密钥值**（只显示一次）

保存以下信息：

```env
应用程序(客户端) ID = xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
客户端密钥值 = your_client_secret_value
```

⚠️ **重要**: 不要分享你的客户端密钥！

## 获取刷新令牌

### 1. 构造授权 URL

使用以下模板构造授权 URL（替换 `YOUR_CLIENT_ID`）：

```
https://login.microsoftonline.com/common/oauth2/v2.0/authorize?client_id=YOUR_CLIENT_ID&response_type=code&redirect_uri=http://localhost:5000/callback&scope=Files.ReadWrite.All offline_access
```

### 2. 获取授权码

1. 在浏览器中打开上述 URL
2. 使用 Microsoft 账户登录
3. 同意应用权限
4. 浏览器会跳转到 `http://localhost:5000/callback?code=xxx`
5. 复制 URL 中的 `code` 参数值

### 3. 交换刷新令牌

使用授权码交换刷新令牌。可以使用以下 PowerShell 命令：

```powershell
$body = @{
    client_id = 'YOUR_CLIENT_ID'
    client_secret = 'YOUR_CLIENT_SECRET'
    code = 'YOUR_AUTHORIZATION_CODE'
    redirect_uri = 'http://localhost:5000/callback'
    grant_type = 'authorization_code'
}

$response = Invoke-RestMethod -Method Post -Uri 'https://login.microsoftonline.com/common/oauth2/v2.0/token' -Body $body

$response.refresh_token
```

或使用 Python：

```python
import requests

data = {
    'client_id': 'YOUR_CLIENT_ID',
    'client_secret': 'YOUR_CLIENT_SECRET',
    'code': 'YOUR_AUTHORIZATION_CODE',
    'redirect_uri': 'http://localhost:5000/callback',
    'grant_type': 'authorization_code'
}

response = requests.post(
    'https://login.microsoftonline.com/common/oauth2/v2.0/token',
    data=data
)

print(response.json()['refresh_token'])
```

保存返回的 `refresh_token`。

## 配置环境变量

编辑 `.env` 文件：

```env
# 存储类型
STORAGE_TYPE=onedrive

# OneDrive 配置
ONEDRIVE_CLIENT_ID=your_client_id
ONEDRIVE_CLIENT_SECRET=your_client_secret
ONEDRIVE_REFRESH_TOKEN=your_refresh_token

# 可选：指定文件夹
# ONEDRIVE_FOLDER_ID=folder_item_id  # 留空使用根目录

# 可选：重定向 URI（如果与授权时不同）
# ONEDRIVE_REDIRECT_URI=http://localhost:5000/callback

# 可选：自定义权限范围
# ONEDRIVE_SCOPES="Files.ReadWrite.All offline_access"
```

**配置说明：**

- `ONEDRIVE_CLIENT_ID`: Azure 应用的客户端 ID（必需）
- `ONEDRIVE_CLIENT_SECRET`: Azure 应用的客户端密钥（必需）
- `ONEDRIVE_REFRESH_TOKEN`: OAuth 刷新令牌（必需）
- `ONEDRIVE_FOLDER_ID`: 指定文件夹作为根目录（可选）
- `ONEDRIVE_REDIRECT_URI`: 重定向 URI（可选）
- `ONEDRIVE_SCOPES`: 自定义权限范围（可选）

## 环境变量详细说明

| 变量 | 必需 | 默认值 | 说明 |
|------|------|--------|------|
| `STORAGE_TYPE` | ✅ | - | 必须设置为 `onedrive` |
| `ONEDRIVE_CLIENT_ID` | ✅ | - | Azure 应用的客户端 ID |
| `ONEDRIVE_CLIENT_SECRET` | ✅ | - | Azure 应用的客户端密钥 |
| `ONEDRIVE_REFRESH_TOKEN` | ✅ | - | OAuth 刷新令牌 |
| `ONEDRIVE_FOLDER_ID` | ❌ | `root` | 指定文件夹作为根目录 |
| `ONEDRIVE_REDIRECT_URI` | ❌ | - | 重定向 URI，应与授权时一致 |
| `ONEDRIVE_SCOPES` | ❌ | - | 自定义权限范围 |

## 高级配置

### 使用特定文件夹作为根目录

如果要将 OneDrive 中的某个文件夹作为 Cloud Index 的根目录：

1. 在 OneDrive 中找到目标文件夹
2. 使用 Microsoft Graph Explorer 获取文件夹 ID：
   - 访问 [Graph Explorer](https://developer.microsoft.com/en-us/graph/graph-explorer)
   - 登录并授权
   - 执行 GET 请求：`https://graph.microsoft.com/v1.0/me/drive/root:/your/folder/path`
   - 从响应中复制 `id` 字段
3. 在 `.env` 中设置：

```env
3. 在 `.env` 中设置：

```env
ONEDRIVE_FOLDER_ID=01BYE5RZ6QN3ZWBTUFOFD3GSPGOHDJD36K
```

### 公共客户端配置

如果应用注册为"公共客户端"（桌面/移动应用）：

- 可以省略 `ONEDRIVE_CLIENT_SECRET`
- 但推荐使用机密客户端以提高安全性

### 企业账户配置

使用企业 OneDrive（OneDrive for Business）：

1. 在 Azure AD 中注册应用
2. 配置相同的权限
3. 使用企业账户登录授权
4. 其他配置步骤相同

## 成本估算

### 个人账户

- **免费存储**: 5GB
- **API 调用**: 无限制（有速率限制）
- **流量**: 无限制
- **总成本**: **免费** ✅

### Microsoft 365 个人版

- **月费**: ¥398/年（约 ¥33/月）
- **存储空间**: 1TB
- **额外功能**: Office 套件、高级安全功能
- **适用场景**: 个人用户、小团队

### Microsoft 365 商业版

- **月费**: ¥75-150/用户/月（根据套餐）
- **存储空间**: 1TB/用户起
- **额外功能**: 企业级管理、合规性工具
- **适用场景**: 中小企业、大型团队

## 与其他存储对比

| 特性 | OneDrive | R2 | S3 | GitHub |
|-----|----------|-----|-----|---------|
| **价格** | 💰 付费/限时免费 | 💚 低成本 | 💛 按需计费 | 💚 免费 |
| **存储空间** | 5GB-1TB+ | 无限 | 无限 | 1GB 限制 |
| **Office 集成** | ✅ 完美 | ❌ 无 | ❌ 无 | ❌ 无 |
| **版本历史** | ✅ 自动 | ❌ 无 | ❌ 无 | ✅ Git |
| **全球 CDN** | ✅ 有 | ✅ 有 | ✅ 有 | ⚠️ 可选 |
| **易用性** | ✅ 简单 | ✅ 简单 | ⚠️ 中等 | ✅ 简单 |
| **适用场景** | 个人/企业 | 个人/小团队 | 企业 | 开源/文档 |

## 迁移指南

### 从其他存储迁移到 OneDrive

1. **备份原有数据**
2. **配置 OneDrive** - 按照本指南完成配置
3. **迁移数据** - 使用批量上传工具
4. **验证数据** - 确保所有文件正确迁移
5. **更新配置** - 修改 Cloud Index 配置
6. **测试功能** - 验证所有功能正常

### 从 OneDrive 迁移到其他存储

1. **选择目标存储** - 确定迁移目标（R2/S3/GitHub）
2. **导出数据** - 批量下载所有文件
3. **配置新存储** - 完成目标存储配置
4. **上传数据** - 使用批量上传工具
5. **更新配置** - 修改环境变量
6. **验证迁移** - 确保数据完整

## 参考资源

### 官方文档

- [Microsoft Graph API](https://docs.microsoft.com/en-us/graph/api/overview)
- [OneDrive API 参考](https://docs.microsoft.com/en-us/graph/api/resources/onedrive)
- [OAuth 2.0 授权](https://docs.microsoft.com/en-us/azure/active-directory/develop/v2-oauth2-auth-code-flow)
- [Azure AD 应用注册](https://docs.microsoft.com/en-us/azure/active-directory/develop/quickstart-register-app)

### 工具和资源

- [Graph Explorer](https://developer.microsoft.com/en-us/graph/graph-explorer) - 测试 API
- [Azure Portal](https://portal.azure.com) - 管理应用
- [OneDrive 开发者中心](https://developer.microsoft.com/en-us/onedrive)

### 社区资源

- [Cloud Index GitHub](https://github.com/RhenCloud/Cloud-Index)
- [OneDrive API Stack Overflow](https://stackoverflow.com/questions/tagged/onedrive)
- [Microsoft Graph 社区](https://techcommunity.microsoft.com/t5/microsoft-graph/ct-p/MicrosoftGraph)

## 相关文档

- [GitHub 存储配置](/storage/github)
- [Cloudflare R2 配置](/storage/r2)
- [Amazon S3 配置](/storage/s3)
- [存储概述](/storage/overview)
- [快速开始](/guide/quickstart)
- [环境变量配置](/guide/configuration/environment)

## 获取帮助

遇到问题？

1. 查看 [常见问题](#常见问题) 章节
2. 访问 [GitHub Issues](https://github.com/RhenCloud/Cloud-Index/issues)
3. 查阅 [官方文档](https://docs.microsoft.com/en-us/graph/)
4. 加入社区讨论

---

**更新日期**: 2025-11-15  
**适用版本**: Cloud Index 主分支
