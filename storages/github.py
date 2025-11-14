import base64
from datetime import datetime
from io import BytesIO
from typing import Any, Dict

import requests
from PIL import Image

from config import Config

from .base import BaseStorage


class StreamWrapper:
    """为 BytesIO 包装器，使其支持 iter_chunks() 方法以兼容 R2 的流式响应"""

    def __init__(self, data: bytes, chunk_size: int = 8192):
        self.data = data
        self.chunk_size = chunk_size
        self.position = 0

    def iter_chunks(self, chunk_size: int = None):
        """迭代返回数据块"""
        chunk_size = chunk_size or self.chunk_size
        offset = 0
        while offset < len(self.data):
            yield self.data[offset : offset + chunk_size]
            offset += chunk_size

    def read(self, size: int = -1):
        """为了兼容性支持 read() 方法"""
        if size == -1:
            return self.data
        result = self.data[self.position : self.position + size]
        self.position += len(result)
        return result

    def seek(self, offset: int):
        """为了兼容性支持 seek() 方法"""
        self.position = offset

    def tell(self):
        """为了兼容性支持 tell() 方法"""
        return self.position


class GitHubStorage(BaseStorage):
    """基于 GitHub 仓库的存储实现"""

    def __init__(self):
        """初始化 GitHub 存储客户端"""
        self.token = Config.GITHUB_TOKEN
        repo_full = Config.GITHUB_REPO  # 格式: owner/repo
        self.branch = Config.GITHUB_BRANCH

        if not self.token or not repo_full:
            raise RuntimeError("GITHUB_TOKEN and GITHUB_REPO must be set")

        # 解析 owner/repo
        repo_parts = repo_full.split("/")
        if len(repo_parts) != 2:
            raise RuntimeError(f"GITHUB_REPO must be in format 'owner/repo', got: {repo_full}")

        self.repo_owner = repo_parts[0]
        self.repo_name = repo_parts[1]
        self.repo = repo_full

        self.api_base_url = f"https://api.github.com/repos/{self.repo_owner}/{self.repo_name}"
        self.raw_content_url = f"https://raw.githubusercontent.com/{self.repo_owner}/{self.repo_name}/{self.branch}"

    def _headers(self) -> Dict[str, str]:
        """返回 API 请求的公共头部信息"""
        return {
            "Authorization": f"token {self.token}",
            "Accept": "application/vnd.github.v3+json",
        }

    def _get_file_sha(self, file_path: str) -> str:
        """获取文件的 SHA 值用于更新或删除"""
        try:
            url = f"{self.api_base_url}/contents/{file_path}"
            response = requests.get(url, headers=self._headers())
            if response.status_code == 200:
                return response.json().get("sha")
        except Exception:
            pass
        return None

    def _get_last_commit_time(self, file_path: str) -> datetime:
        """获取文件的最后提交时间，返回 datetime 对象"""
        try:
            url = f"{self.api_base_url}/commits"
            params = {"path": file_path, "per_page": 1}
            response = requests.get(url, headers=self._headers(), params=params)
            if response.status_code == 200:
                commits = response.json()
                if commits and len(commits) > 0:
                    time_str = commits[0]["commit"]["author"]["date"]
                    # 解析 ISO 格式时间字符串为 datetime 对象
                    # 格式: "2025-11-08T10:55:26Z"
                    return datetime.fromisoformat(time_str.replace("Z", "+00:00"))
        except Exception:
            pass
        return datetime.now()

    def list_objects(self, prefix: str = "") -> Dict[str, Any]:
        """
        列出存储桶中的对象

        Args:
            prefix: 对象前缀（用于目录浏览）

        Returns:
            包含对象列表的字典
        """
        try:
            # 移除末尾的 / 以保持 GitHub API 的一致性
            prefix = prefix.rstrip("/") if prefix else ""
            url = f"{self.api_base_url}/contents/{prefix}" if prefix else f"{self.api_base_url}/contents"
            response = requests.get(url, headers=self._headers())
            response.raise_for_status()

            contents = response.json()
            if not isinstance(contents, list):
                contents = [contents]

            files = []
            folders = []

            for item in contents:
                if item["type"] == "file":
                    # 跳过 .gitkeep 文件
                    if item["name"] == ".gitkeep":
                        continue

                    # 获取最后提交时间
                    last_modified = self._get_last_commit_time(item["path"])

                    files.append(
                        {
                            "Key": item["path"],
                            "Size": item["size"],
                            "LastModified": last_modified,
                            "ETag": item["sha"],
                        }
                    )
                elif item["type"] == "dir":
                    folders.append({"Prefix": item["path"] + "/"})

            return {
                "Contents": files,
                "CommonPrefixes": folders,
                "IsTruncated": False,
            }
        except Exception as e:
            return {"Contents": [], "CommonPrefixes": [], "Error": str(e)}

    def get_object_info(self, key: str) -> Dict[str, Any]:
        """
        获取对象基本信息

        Args:
            key: 对象键名

        Returns:
            对象元数据
        """
        try:
            url = f"{self.api_base_url}/contents/{key}"
            response = requests.get(url, headers=self._headers())
            response.raise_for_status()

            data = response.json()
            last_modified = self._get_last_commit_time(key)

            return {
                "Key": data["path"],
                "Size": data["size"],
                "ContentLength": data["size"],  # 为了兼容路由代码
                "LastModified": last_modified,
                "ETag": data["sha"],
                "ContentType": "application/octet-stream",
            }
        except Exception as e:
            raise RuntimeError(f"Failed to get object info: {str(e)}") from e

    def get_object(self, key: str) -> Dict[str, Any]:
        """
        获取对象内容

        Args:
            key: 对象键名

        Returns:
            包含对象内容的字典，Body 支持 iter_chunks() 方法
        """
        try:
            url = f"{self.raw_content_url}/{key}"
            response = requests.get(url)
            response.raise_for_status()

            content = response.content
            return {
                "Body": StreamWrapper(content),
                "ContentLength": len(content),
                "ContentType": response.headers.get("Content-Type", "application/octet-stream"),
            }
        except Exception as e:
            raise RuntimeError(f"Failed to get object: {str(e)}") from e

    def generate_presigned_url(self, key: str, expires: int = None) -> str:
        """
        为指定对象生成预签名 URL

        Args:
            key: 对象键名
            expires: 过期时间（秒）

        Returns:
            预签名 URL，失败返回 None
        """
        try:
            # GitHub raw 内容 URL - 直接返回文件内容
            # 这会被前端用于下载
            return f"{self.raw_content_url}/{key}"
        except Exception:
            return None

    def get_public_url(self, key: str) -> str:
        """
        生成对象的公共访问 URL

        Args:
            key: 对象键名

        Returns:
            公共 URL，未配置返回 None
        """
        return f"{self.raw_content_url}/{key}"

    def generate_thumbnail(self, file_path: str) -> bytes:
        """
        生成图片缩略图

        Args:
            file_path: 文件路径

        Returns:
            缩略图字节数据
        """
        try:
            obj = self.get_object(file_path)
            # StreamWrapper 需要转换为 BytesIO 以兼容 PIL
            body = obj["Body"]
            if isinstance(body, StreamWrapper):
                image_data = body.read()
                image_bytes = BytesIO(image_data)
            else:
                image_bytes = body

            img = Image.open(image_bytes)
            img.thumbnail((200, 200))

            thumbnail_io = BytesIO()
            img.save(thumbnail_io, format="JPEG")
            thumbnail_io.seek(0)
            return thumbnail_io.read()
        except Exception as e:
            raise RuntimeError(f"Failed to generate thumbnail: {str(e)}") from e

    def upload_file(self, key: str, file_data: bytes, content_type: str = None) -> bool:
        """
        上传文件到存储

        Args:
            key: 对象键名（文件路径）
            file_data: 文件二进制数据
            content_type: 文件类型（MIME type）

        Returns:
            上传成功返回 True，失败返回 False
        """
        try:
            url = f"{self.api_base_url}/contents/{key}"
            encoded_content = base64.b64encode(file_data).decode("utf-8")

            # 检查文件是否已存在
            sha = self._get_file_sha(key)

            data = {
                "message": f"Upload {key}",
                "content": encoded_content,
                "branch": self.branch,
            }

            if sha:
                data["sha"] = sha

            response = requests.put(url, json=data, headers=self._headers())
            response.raise_for_status()
            return True
        except Exception as e:
            print(f"Upload failed: {str(e)}")
            return False

    def delete_file(self, key: str) -> bool:
        """
        删除存储中的文件

        Args:
            key: 对象键名（文件路径）

        Returns:
            删除成功返回 True，失败返回 False
        """
        try:
            sha = self._get_file_sha(key)
            if not sha:
                return False

            url = f"{self.api_base_url}/contents/{key}"
            data = {
                "message": f"Delete {key}",
                "sha": sha,
                "branch": self.branch,
            }

            response = requests.delete(url, json=data, headers=self._headers())
            response.raise_for_status()
            return True
        except Exception as e:
            print(f"Delete failed: {str(e)}")
            return False

    def rename_file(self, old_key: str, new_key: str) -> bool:
        """
        重命名存储中的文件

        Args:
            old_key: 旧的对象键名
            new_key: 新的对象键名

        Returns:
            重命名成功返回 True，失败返回 False
        """
        try:
            # 获取原文件内容
            obj = self.get_object(old_key)
            content = obj["Body"].read()

            # 上传到新位置
            if not self.upload_file(new_key, content):
                return False

            # 删除原文件
            return self.delete_file(old_key)
        except Exception as e:
            print(f"Rename failed: {str(e)}")
            return False

    def delete_folder(self, prefix: str) -> bool:
        """
        删除存储中的文件夹（前缀）

        Args:
            prefix: 要删除的文件夹前缀

        Returns:
            删除成功返回 True，失败返回 False
        """
        try:
            # 确保前缀以 / 结尾
            if prefix and not prefix.endswith("/"):
                prefix = prefix + "/"

            contents = self.list_objects(prefix)
            files = contents.get("Contents", [])

            # 删除所有文件
            for file_info in files:
                file_key = file_info["Key"]
                if not self.delete_file(file_key):
                    return False

            # 递归删除子文件夹
            folders = contents.get("CommonPrefixes", [])
            for folder in folders:
                folder_prefix = folder["Prefix"]
                # 确保递归时也传入正确格式的前缀（带末尾 /）
                if not self.delete_folder(folder_prefix):
                    return False

            return True
        except Exception as e:
            print(f"Delete folder failed: {str(e)}")
            return False

    def rename_folder(self, old_prefix: str, new_prefix: str) -> bool:
        """
        重命名存储中的文件夹（前缀）

        Args:
            old_prefix: 旧的文件夹前缀
            new_prefix: 新的文件夹前缀

        Returns:
            重命名成功返回 True，失败返回 False
        """
        try:
            contents = self.list_objects(old_prefix)
            files = contents.get("Contents", [])

            for file_info in files:
                old_key = file_info["Key"]
                new_key = old_key.replace(old_prefix, new_prefix, 1)

                if not self.rename_file(old_key, new_key):
                    return False

            return True
        except Exception as e:
            print(f"Rename folder failed: {str(e)}")
            return False

    def copy_file(self, source_key: str, dest_key: str) -> bool:
        """
        复制存储中的文件

        Args:
            source_key: 源对象键名
            dest_key: 目标对象键名

        Returns:
            复制成功返回 True，失败返回 False
        """
        try:
            obj = self.get_object(source_key)
            content = obj["Body"].read()
            return self.upload_file(dest_key, content)
        except Exception as e:
            print(f"Copy failed: {str(e)}")
            return False

    def copy_folder(self, source_prefix: str, dest_prefix: str) -> bool:
        """
        复制存储中的文件夹（前缀）

        Args:
            source_prefix: 源文件夹前缀
            dest_prefix: 目标文件夹前缀

        Returns:
            复制成功返回 True，失败返回 False
        """
        try:
            contents = self.list_objects(source_prefix)
            files = contents.get("Contents", [])

            for file_info in files:
                source_key = file_info["Key"]
                dest_key = source_key.replace(source_prefix, dest_prefix, 1)

                if not self.copy_file(source_key, dest_key):
                    return False

            return True
        except Exception as e:
            print(f"Copy folder failed: {str(e)}")
            return False

    def create_folder(self, key: str) -> bool:
        """
        创建文件夹

        Args:
            key: 文件夹路径（以 / 结尾）

        Returns:
            创建成功返回 True，失败返回 False
        """
        try:
            # GitHub 不需要显式创建文件夹
            # 如果需要标记文件夹存在，可以创建 .gitkeep 文件
            # 但为了不显示 .gitkeep，我们在这里直接返回 True
            # 实际的文件夹会在上传文件时自动创建
            return True
        except Exception as e:
            print(f"Create folder failed: {str(e)}")
            return False

    def generate_download_response(self, key: str) -> Dict[str, Any]:
        """
        生成文件下载响应（GitHub 特有实现）

        GitHub 存储需要通过服务器中继以添加 Content-Disposition 头

        Args:
            key: 对象键名（文件路径）

        Returns:
            包含下载信息的字典
        """
        try:
            file_obj = self.get_object(key)
            file_name = key.split("/")[-1] if "/" in key else key

            # 获取完整内容
            body = file_obj.get("Body")
            if hasattr(body, "read"):
                content = body.read()
            elif hasattr(body, "data"):
                content = body.data
            else:
                content = body

            # 使用 RFC 5987 编码处理文件名中的特殊字符
            from urllib.parse import quote

            encoded_filename = quote(file_name.encode("utf-8"), safe="")

            headers = {
                "Content-Type": file_obj.get("ContentType", "application/octet-stream"),
                "Content-Disposition": f"attachment; filename=\"{file_name}\"; filename*=UTF-8''{encoded_filename}",
                "Cache-Control": "public, max-age=86400",
            }

            return {
                "type": "content",
                "content": content,
                "headers": headers,
                "mimetype": file_obj.get("ContentType", "application/octet-stream"),
            }
        except Exception as e:
            print(f"GitHub download response generation failed: {str(e)}")
            return None
