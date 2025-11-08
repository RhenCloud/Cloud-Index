# API 文档

Cloud Index 提供了 REST API 用于文件管理操作。

## API

### 1. 上传文件

**端点:** `POST /upload`

**描述:** 上传文件到存储

**请求:**

- Method: `POST`
- Content-Type: `multipart/form-data`
- Body:
  - `file` (required): 要上传的文件
  - `prefix` (optional): 目标路径前缀

**示例 (cURL):**

```bash
# 上传到根目录
curl -X POST http://localhost:5000/upload \
  -F "file=@/path/to/your/file.jpg"

# 上传到指定目录
curl -X POST http://localhost:5000/upload \
  -F "file=@/path/to/your/file.jpg" \
  -F "prefix=images/"
```

**示例 (JavaScript):**

```javascript
const formData = new FormData();
formData.append('file', fileInput.files[0]);
formData.append('prefix', 'images/');

const response = await fetch('/upload', {
    method: 'POST',
    body: formData
});

const result = await response.json();
console.log(result);
```

**响应:**

成功 (200):

```json
{
    "success": true,
    "message": "File uploaded successfully",
    "path": "images/file.jpg"
}
```

失败 (400/500):

```json
{
    "success": false,
    "error": "Error message"
}
```

### 2. 删除文件

**端点:** `DELETE /delete/<path:file_path>`

**描述:** 删除存储中的文件

**请求:**

- Method: `DELETE` 或 `POST`
- Path Parameter:
  - `file_path`: 要删除的文件路径

**示例 (cURL):**

```bash
# 使用 DELETE 方法
curl -X DELETE http://localhost:5000/delete/images/file.jpg

# 使用 POST 方法（某些环境不支持 DELETE）
curl -X POST http://localhost:5000/delete/images/file.jpg
```

**示例 (JavaScript):**

```javascript
const response = await fetch('/delete/images/file.jpg', {
    method: 'DELETE'
});

const result = await response.json();
console.log(result);
```

**响应:**

成功 (200):

```json
{
    "success": true,
    "message": "File deleted successfully"
}
```

失败 (500):

```json
{
    "success": false,
    "error": "Error message"
}
```

### 3. 列出文件

**端点:** `GET /` 或 `GET /<path:prefix_path>`

**描述:** 列出指定路径下的文件和目录

**请求:**

- Method: `GET`
- Query Parameters:
  - `prefix` (optional): 路径前缀

**示例:**

```bash
# 列出根目录
curl http://localhost:5000/

# 列出指定目录
curl http://localhost:5000/images/

# 使用查询参数
curl http://localhost:5000/?prefix=images/
```

### 4. 获取文件

**端点:** `GET /file/<path:file_path>`

**描述:** 获取文件内容或重定向到预签名 URL（大文件）

**请求:**

- Method: `GET`
- Path Parameter:
  - `file_path`: 文件路径

**示例:**

```bash
curl http://localhost:5000/file/images/photo.jpg
```

**响应:**

- 小文件 (< 6MB): 直接返回文件内容
- 大文件 (>= 6MB): 302 重定向到预签名 URL

### 5. 获取缩略图

**端点:** `GET /thumb/<path:file_path>`

**描述:** 获取图片的缩略图（320x320 JPEG）

**请求:**

- Method: `GET`
- Path Parameter:
  - `file_path`: 图片文件路径

**示例:**

```bash
curl http://localhost:5000/thumb/images/photo.jpg
```

**响应:**

- Content-Type: `image/jpeg`
- Body: 缩略图数据

### 6. 重命名文件

**端点:** `POST /rename/<path:old_key>`

**描述:** 重命名文件

**请求:**

- Method: `POST`
- Content-Type: `application/json`
- Path Parameter:
  - `old_key`: 旧的文件路径
- Body:
  - `newName`: 新的文件名

**示例 (cURL):**

```bash
curl -X POST http://localhost:5000/rename/images/photo.jpg \
  -H "Content-Type: application/json" \
  -d '{"newName":"photo_new.jpg"}'
```

**示例 (JavaScript):**

```javascript
const response = await fetch('/rename/images/photo.jpg', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({newName: 'photo_new.jpg'})
});

const result = await response.json();
console.log(result);
```

**响应:**

成功 (200):

```json
{
    "success": true,
    "message": "File renamed successfully",
    "newKey": "images/photo_new.jpg"
}
```

失败 (400/500):

```json
{
    "success": false,
    "error": "Error message"
}
```

### 7. 删除文件夹

**端点:** `DELETE /delete_folder/<path:prefix>`

**描述:** 删除文件夹及其所有内容

**请求:**

- Method: `DELETE`
- Path Parameter:
  - `prefix`: 文件夹路径

**示例 (cURL):**

```bash
curl -X DELETE http://localhost:5000/delete_folder/images
```

**示例 (JavaScript):**

```javascript
const response = await fetch('/delete_folder/images', {
    method: 'DELETE'
});

const result = await response.json();
console.log(result);
```

**响应:**

成功 (200):

```json
{
    "success": true,
    "message": "Folder deleted successfully"
}
```

失败 (500):

```json
{
    "success": false,
    "error": "Error message"
}
```

### 8. 重命名文件夹

**端点:** `POST /rename_folder/<path:old_prefix>`

**描述:** 重命名文件夹

**请求:**

- Method: `POST`
- Content-Type: `application/json`
- Path Parameter:
  - `old_prefix`: 旧的文件夹路径
- Body:
  - `newName`: 新的文件夹名

**示例 (cURL):**

```bash
curl -X POST http://localhost:5000/rename_folder/old_folder \
  -H "Content-Type: application/json" \
  -d '{"newName":"new_folder"}'
```

**示例 (JavaScript):**

```javascript
const response = await fetch('/rename_folder/old_folder', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({newName: 'new_folder'})
});

const result = await response.json();
console.log(result);
```

**响应:**

成功 (200):

```json
{
    "success": true,
    "message": "Folder renamed successfully",
    "newPrefix": "new_folder/"
}
```

失败 (500):

```json
{
    "success": false,
    "error": "Error message"
}
```

### 9. 复制文件或文件夹

**端点:** `POST /copy`

**描述:** 复制文件或文件夹到另一位置

**请求:**

- Method: `POST`
- Content-Type: `application/json`
- Body:
  - `source`: 源文件或文件夹路径
  - `destination`: 目标文件或文件夹路径
  - `is_folder`: 是否为文件夹（true/false）

**示例 (cURL):**

```bash
# 复制文件
curl -X POST http://localhost:5000/copy \
  -H "Content-Type: application/json" \
  -d '{"source":"images/photo.jpg","destination":"backup/photo.jpg","is_folder":false}'

# 复制文件夹
curl -X POST http://localhost:5000/copy \
  -H "Content-Type: application/json" \
  -d '{"source":"images/","destination":"backup/images/","is_folder":true}'
```

**示例 (JavaScript):**

```javascript
const response = await fetch('/copy', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({
        source: 'images/photo.jpg',
        destination: 'backup/photo.jpg',
        is_folder: false
    })
});

const result = await response.json();
console.log(result);
```

**响应:**

成功 (200):

```json
{
    "success": true,
    "message": "Item copied successfully"
}
```

失败 (400/500):

```json
{
    "success": false,
    "error": "Error message"
}
```

### 10. 移动文件或文件夹

**端点:** `POST /move`

**描述:** 移动（重命名路径）文件或文件夹到另一位置

**请求:**

- Method: `POST`
- Content-Type: `application/json`
- Body:
  - `source`: 源文件或文件夹路径
  - `destination`: 目标文件或文件夹路径
  - `is_folder`: 是否为文件夹（true/false）

**示例 (cURL):**

```bash
# 移动文件
curl -X POST http://localhost:5000/move \
  -H "Content-Type: application/json" \
  -d '{"source":"images/photo.jpg","destination":"archive/photo.jpg","is_folder":false}'

# 移动文件夹
curl -X POST http://localhost:5000/move \
  -H "Content-Type: application/json" \
  -d '{"source":"images/","destination":"archive/images/","is_folder":true}'
```

**示例 (JavaScript):**

```javascript
const response = await fetch('/move', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({
        source: 'images/photo.jpg',
        destination: 'archive/photo.jpg',
        is_folder: false
    })
});

const result = await response.json();
console.log(result);
```

**响应:**

成功 (200):

```json
{
    "success": true,
    "message": "Item moved successfully"
}
```

失败 (400/500):

```json
{
    "success": false,
    "error": "Error message"
}
```

### 11. 创建文件夹

**端点:** `POST /create_folder`

**描述:** 创建新文件夹

**请求:**

- Method: `POST`
- Content-Type: `application/json`
- Body:
  - `path`: 新文件夹的路径

**示例 (cURL):**

```bash
curl -X POST http://localhost:5000/create_folder \
  -H "Content-Type: application/json" \
  -d '{"path":"new_folder/subfolder"}'
```

**示例 (JavaScript):**

```javascript
const response = await fetch('/create_folder', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({path: 'new_folder/subfolder'})
});

const result = await response.json();
console.log(result);
```

**响应:**

成功 (200):

```json
{
    "success": true,
    "message": "Folder created successfully"
}
```

失败 (400/500):

```json
{
    "success": false,
    "error": "Error message"
}
```

## 错误代码

- `400 Bad Request`: 请求参数错误或缺少必要参数
- `404 Not Found`: 文件或文件夹不存在
- `413 Payload Too Large`: 文件太大（超过 6MB 且无预签名 URL）
- `500 Internal Server Error`: 服务器内部错误

## 功能特性

### 文件操作

- ✅ 上传文件
- ✅ 下载文件（直接下载或预签名 URL）
- ✅ 删除文件
- ✅ 重命名文件
- ✅ 复制文件
- ✅ 移动文件

### 文件夹操作

- ✅ 创建文件夹
- ✅ 删除文件夹（包含其所有内容）
- ✅ 重命名文件夹
- ✅ 复制文件夹（包含其所有内容）
- ✅ 移动文件夹（包含其所有内容）
- ✅ 列出文件夹内容

### 其他功能

- ✅ 生成缩略图（图片文件）
- ✅ 批量文件操作
- ✅ 预签名 URL（用于大文件直接访问）

## 批量操作

### 批量上传

前端可以遍历多个文件并依次调用上传 API：

```javascript
async function uploadMultipleFiles(files) {
    for (let file of files) {
        const formData = new FormData();
        formData.append('file', file);
        
        const response = await fetch('/upload', {
            method: 'POST',
            body: formData
        });
        
        const result = await response.json();
        console.log(`${file.name}: ${result.success ? 'success' : 'failed'}`);
    }
}
```

## 限制说明

### Cloudflare R2（免费套餐）

- 总文件大小: 最多 10GB
- API 请求频率: 根据您的 R2 套餐

<!-- ### Github

- 单文件大小: 最大 100MB（建议 < 50MB）
- API 请求频率:
  - 有 Token: 5000 请求/小时
  - 无 Token: 60 请求/小时
- Repository 总大小: 建议 < 1GB -->

## 安全建议

1. **添加认证**: 在生产环境中为所有 API 端点添加认证
2. **文件类型验证**: 验证上传文件的类型和扩展名，防止恶意文件上传
3. **文件大小限制**: 在应用层限制上传文件的大小
4. **路径验证**: 验证文件和文件夹路径，防止目录遍历攻击
5. **速率限制**: 防止滥用 API，实施请求频率限制
6. **CORS 配置**: 正确配置跨域访问策略
7. **日志记录**: 记录所有文件操作以用于审计
8. **访问控制**: 根据用户身份实施细粒度的访问控制
9. **加密**: 对敏感数据进行加密存储和传输
10. **备份**: 定期备份存储中的重要数据
