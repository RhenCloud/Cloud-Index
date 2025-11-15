from datetime import datetime, timedelta
from io import BytesIO
from typing import Any, Dict, Optional
from urllib.parse import quote

import requests
from PIL import Image

from config import Config

from .base import BaseStorage


class _InvalidGrant(Exception):
    """内部异常：用于标记 invalid_grant 以便进行下一次尝试"""

    pass


class OnedriveStorage(BaseStorage):
    """基于 OneDrive 的存储实现，支持自动令牌刷新"""

    def __init__(self):
        """初始化 OneDrive 存储客户端"""
        self.client_id = Config.ONEDRIVE_CLIENT_ID
        self.client_secret = Config.ONEDRIVE_CLIENT_SECRET
        self.refresh_token = Config.ONEDRIVE_REFRESH_TOKEN
        self.folder_id = Config.ONEDRIVE_FOLDER_ID
        self.graph_api_url = "https://graph.microsoft.com/v1.0"

        if not (self.client_id and self.client_secret and self.refresh_token):
            raise RuntimeError("ONEDRIVE_CLIENT_ID, ONEDRIVE_CLIENT_SECRET, and ONEDRIVE_REFRESH_TOKEN must be set")

        # 如果没有指定 folder_id，使用 /me/drive/root
        self.folder_item_id = self.folder_id or "root"

        # 初始化 access_token 并刷新
        self.access_token = None
        self._refresh_token()

    def _item_path_url(self, key: str, action: str | None = None) -> str:
        """根据 folder_item_id 构造基于路径的 DriveItem URL，可附带动作后缀。

        Examples:
            - action=None => ...:/path:
            - action='content' => ...:/path:/content
            - action='createLink' => ...:/path:/createLink
            - action='thumbnails' => ...:/path:/thumbnails
        """
        key = key.strip("/")
        # 对路径进行 URL 编码，但保留路径分隔符 '/'
        key_quoted = quote(key, safe="/")
        base = (
            f"{self.graph_api_url}/me/drive/root:/{key_quoted}:"
            if self.folder_item_id == "root"
            else f"{self.graph_api_url}/me/drive/items/{self.folder_item_id}:/{key_quoted}:"
        )
        if action:
            return base + f"/{action}"
        return base

    def _refresh_token(self) -> None:
        """刷新 OneDrive 访问令牌"""
        configured_scopes = getattr(Config, "ONEDRIVE_SCOPES", None)
        attempts = [None] + ([configured_scopes] if configured_scopes else []) + ["Files.ReadWrite.All offline_access"]
        token_json = self._perform_refresh_attempts(attempts)
        self.access_token = token_json["access_token"]
        new_refresh = token_json.get("refresh_token")
        if new_refresh:
            self.refresh_token = new_refresh
        self._access_token_expires_in = token_json.get("expires_in")

    def _perform_refresh_attempts(self, attempts: list) -> dict:
        errors: list[str] = []

        for idx, scope in enumerate(attempts, start=1):
            try:
                token_json = self._do_refresh_attempt(scope)
                return token_json
            except _InvalidGrant as e:
                errors.append(f"Attempt {idx} invalid_grant: {str(e)}")
                continue

        raise RuntimeError("Failed to refresh OneDrive token: " + " | ".join(errors))

    def _do_refresh_attempt(self, scope: str | None) -> dict:
        url = "https://login.microsoftonline.com/common/oauth2/v2.0/token"
        headers = {"Content-Type": "application/x-www-form-urlencoded"}

        payload = {
            "client_id": self.client_id,
            "grant_type": "refresh_token",
            "refresh_token": self.refresh_token,
        }
        if scope:
            payload["scope"] = scope
        if self.client_secret:
            payload["client_secret"] = self.client_secret
        redirect_uri = getattr(Config, "ONEDRIVE_REDIRECT_URI", None)
        if redirect_uri:
            payload["redirect_uri"] = redirect_uri

        resp = requests.post(url, data=payload, headers=headers, timeout=20)
        try:
            detail = resp.json()
        except Exception:
            detail = resp.text

        if resp.status_code != 200:
            # 如果是 invalid_grant，抛出内部异常以触发下一次尝试
            if isinstance(detail, dict) and detail.get("error") == "invalid_grant":
                raise _InvalidGrant(detail)
            raise RuntimeError(f"Token endpoint error {resp.status_code}: {detail}")

        if isinstance(detail, dict) and detail.get("error"):
            if detail.get("error") == "invalid_grant":
                raise _InvalidGrant(detail)
            raise RuntimeError(f"Token response error: {detail}")

        token_json = detail if isinstance(detail, dict) else {}
        access_token = token_json.get("access_token")
        if not access_token:
            # 视为无效，交给下一次尝试
            raise _InvalidGrant({"error": "missing_access_token", "detail": detail})
        return token_json

    def _try_refresh(self, func):
        """尝试执行函数，如果失败则刷新令牌后重试（处理令牌过期）"""
        try:
            return func()
        except Exception as e:
            if "401" in str(e) or "Unauthorized" in str(e):
                # 令牌过期，刷新并重试
                self._refresh_token()
                return func()
            raise

    def _api_request(self, method: str, url: str, **kwargs):
        """
        执行 API 请求，自动处理令牌过期

        Args:
            method: HTTP 方法 (GET, POST, PUT, DELETE, PATCH)
            url: API URL
            **kwargs: 其他请求参数

        Returns:
            响应对象
        """

        def _do_request():
            response = requests.request(method, url, headers=self._headers(), **kwargs)
            if response.status_code == 401:
                raise RuntimeError("Unauthorized - OneDrive access token expired")
            return response

        return self._try_refresh(_do_request)

    def _headers(self) -> Dict[str, str]:
        """返回 API 请求的公共头部信息"""
        return {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
        }

    def _verify_connection(self) -> None:
        """验证 OneDrive 连接是否有效"""
        try:
            url = f"{self.graph_api_url}/me/drive"
            response = requests.get(url, headers=self._headers(), timeout=10)
            if response.status_code != 200:
                raise RuntimeError(f"OneDrive connection failed: {response.text}")
        except Exception as e:
            raise RuntimeError(f"Failed to connect to OneDrive: {str(e)}") from None

    def _get_folder_id(self, path: str) -> Optional[str]:
        """获取指定路径的文件夹 ID"""
        if not path or path == "/":
            return self.folder_item_id

        try:
            # 直接获取该路径对应项的元数据（而不是其子项），以拿到该文件夹自身的 id
            path = path.strip("/")
            if self.folder_item_id == "root":
                url = f"{self.graph_api_url}/me/drive/root:/{path}:"
            else:
                url = f"{self.graph_api_url}/me/drive/items/{self.folder_item_id}:/{path}:"
            response = requests.get(url, headers=self._headers(), timeout=10)

            if response.status_code == 200:
                item = response.json()
                if item.get("folder"):
                    return item.get("id")
        except Exception:
            pass

        return None

    def list_objects(self, prefix: str = "") -> Dict[str, Any]:
        """
        列出存储桶中的对象

        Args:
            prefix: 对象前缀（用于目录浏览）

        Returns:
            包含对象列表的字典
        """
        try:
            prefix = prefix.rstrip("/") if prefix else ""

            # 直接基于路径列出，避免先查 ID 再列出造成的额外往返
            select = "$select=name,size,lastModifiedDateTime,id,folder,file"
            if prefix:
                # 对前缀进行 URL 编码，保留路径分隔符
                from urllib.parse import quote as _quote

                quoted_prefix = _quote(prefix.strip("/"), safe="/")
                if self.folder_item_id == "root":
                    url = f"{self.graph_api_url}/me/drive/root:/{quoted_prefix}:/children?{select}"
                else:
                    url = (
                        f"{self.graph_api_url}/me/drive/items/{self.folder_item_id}:/{quoted_prefix}:/children?{select}"
                    )
            else:
                if self.folder_item_id == "root":
                    url = f"{self.graph_api_url}/me/drive/root/children?{select}"
                else:
                    url = f"{self.graph_api_url}/me/drive/items/{self.folder_item_id}/children?{select}"
            response = self._api_request("GET", url)
            response.raise_for_status()

            items = response.json().get("value", [])
            files = []
            folders = []

            for item in items:
                # 跳过特殊文件
                if item.get("name", "").startswith("."):
                    continue

                item_path = f"{prefix}/{item.get('name')}" if prefix else item.get("name")

                if "folder" in item:
                    # 这是一个文件夹
                    folders.append({"Prefix": f"{item_path}/"})
                else:
                    # 这是一个文件
                    size = item.get("size", 0)
                    modified_time = item.get("lastModifiedDateTime", datetime.now().isoformat())

                    # 解析 ISO 格式时间
                    try:
                        if isinstance(modified_time, str):
                            modified_time = datetime.fromisoformat(modified_time.replace("Z", "+00:00"))
                    except Exception:
                        modified_time = datetime.now()

                    files.append(
                        {
                            "Key": item_path,
                            "Size": size,
                            "LastModified": modified_time,
                            "ETag": item.get("id", ""),
                        }
                    )

            return {
                "Contents": sorted(files, key=lambda x: x["Key"]),
                "CommonPrefixes": sorted(folders, key=lambda x: x["Prefix"]),
            }
        except Exception as e:
            import traceback

            traceback.print_exc()
            raise RuntimeError(f"Failed to list OneDrive objects: {str(e)}") from None

    def get_object_info(self, key: str) -> Dict[str, Any]:
        """
        获取对象基本信息

        Args:
            key: 对象键名

        Returns:
            对象元数据
        """
        try:
            url = self._item_path_url(key)
            response = self._api_request("GET", url)
            response.raise_for_status()

            item = response.json()
            return {
                "Key": key,
                "Size": item.get("size", 0),
                "LastModified": item.get("lastModifiedDateTime", datetime.now().isoformat()),
                "ETag": item.get("id", ""),
            }
        except Exception as e:
            raise RuntimeError(f"Failed to get OneDrive object info: {str(e)}") from None

    def get_object(self, key: str) -> Dict[str, Any]:
        """
        获取对象内容

        Args:
            key: 对象键名

        Returns:
            包含对象内容的字典
        """
        try:
            url = self._item_path_url(key, "content")
            response = self._api_request("GET", url)
            response.raise_for_status()

            return {
                "Body": response.content,
                "ContentType": response.headers.get("Content-Type", "application/octet-stream"),
            }
        except Exception as e:
            raise RuntimeError(f"Failed to get OneDrive object: {str(e)}") from None

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
            expires = expires or Config.PRESIGNED_URL_EXPIRES
            url = self._item_path_url(key, "createLink")

            body = {
                "type": "view",
                "scope": "anonymous",
                "expirationDateTime": (datetime.utcnow() + timedelta(seconds=expires)).isoformat() + "Z",
            }

            response = requests.post(url, headers=self._headers(), json=body, timeout=15)

            if response.status_code in (200, 201):
                data = response.json() or {}
                link = data.get("link") or {}
                web = link.get("webUrl")
                if web:
                    # 强制下载提示（视 OneDrive 行为而定）
                    sep = "&" if "?" in web else "?"
                    return f"{web}{sep}download=1"

            return None
        except Exception:
            return None

    def _get_direct_download_url(self, key: str) -> Optional[str]:
        """从 DriveItem 元数据中获取临时直链（@microsoft.graph.downloadUrl）。"""
        try:
            url = self._item_path_url(key)
            resp = self._api_request("GET", url)
            if resp.status_code == 200:
                data = resp.json() or {}
                # Graph 返回的预签名直链属性
                return data.get("@microsoft.graph.downloadUrl") or data.get("@microsoft.graph.downloadurl")
        except Exception:
            return None
        return None

    def generate_download_response(self, key: str) -> Dict[str, Any]:
        """优先返回 OneDrive 的临时直链（直接文件内容），避免跳转到预览页。"""
        # 1) 直链（最佳体验：直接获取文件内容，不经过 OneDrive 预览页）
        direct = self._get_direct_download_url(key)
        if direct:
            return {"type": "redirect", "url": direct}

        # 2) 匿名分享链接（添加 download=1 提示下载）
        presigned = self.generate_presigned_url(key)
        if presigned:
            return {"type": "redirect", "url": presigned}

        # 3) 回退到 webUrl（可能需要登录）
        public_url = self.get_public_url(key)
        if public_url:
            return {"type": "redirect", "url": public_url}

        return None

    def get_public_url(self, key: str) -> str:
        """
        生成对象的公共访问 URL

        Args:
            key: 对象键名

        Returns:
            公共 URL，未配置返回 None
        """
        try:
            # 直接获取 DriveItem 元数据并读取 webUrl 字段
            url = self._item_path_url(key)
            response = self._api_request("GET", url)
            if response.status_code == 200:
                return (response.json() or {}).get("webUrl")

            return None
        except Exception:
            return None

    def upload_file(self, key: str, file_data: bytes, content_type: str = None) -> bool:
        """
        上传文件

        Args:
            key: 对象键名
            file_data: 文件内容
            content_type: 文件类型（MIME type，可选）

        Returns:
            上传成功返回 True，失败返回 False
        """
        try:
            url = self._item_path_url(key, "content")

            # 自定义头部（需要指定 Content-Type）
            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": content_type or "application/octet-stream",
            }

            response = requests.put(url, headers=headers, data=file_data, timeout=30)
            response.raise_for_status()

            return response.status_code == 200 or response.status_code == 201
        except Exception as e:
            raise RuntimeError(
                f"Failed to upload file to OneDrive: {str(e)}" if isinstance(e, Exception) else str(e)
            ) from None

    def delete_file(self, key: str) -> bool:
        """
        删除文件

        Args:
            key: 对象键名

        Returns:
            删除成功返回 True，失败返回 False
        """
        try:
            url = self._item_path_url(key)
            response = self._api_request("DELETE", url)
            return response.status_code == 204
        except Exception as e:
            raise RuntimeError(f"Failed to delete file from OneDrive: {str(e)}") from None

    def copy_file(self, source_key: str, dest_key: str) -> bool:
        """
        复制文件

        Args:
            source_key: 源文件键名
            dest_key: 目标文件键名

        Returns:
            复制成功返回 True，失败返回 False
        """
        try:
            source = source_key.strip("/")
            destination = dest_key.strip("/")

            # 获取源文件 ID
            source_url = f"{self.graph_api_url}/me/drive/items/{self.folder_item_id}:/{source}:"
            source_response = self._api_request("GET", source_url)
            source_response.raise_for_status()
            source_item = source_response.json()

            # 复制文件
            copy_url = f"{self.graph_api_url}/me/drive/items/{source_item.get('id')}/copy"
            copy_body = {
                "parentReference": {"id": self.folder_item_id},
                "name": destination.split("/")[-1],
            }

            copy_response = self._api_request("POST", copy_url, json=copy_body)
            copy_response.raise_for_status()

            return copy_response.status_code == 202 or copy_response.status_code == 200
        except Exception as e:
            raise RuntimeError(f"Failed to copy file in OneDrive: {str(e)}") from None

    def generate_thumbnail(self, file_path: str) -> bytes:
        """
        生成图片缩略图

        Args:
            file_path: 文件路径

        Returns:
            缩略图字节数据
        """
        try:
            url = self._item_path_url(file_path, "thumbnails")
            response = requests.get(url, headers=self._headers(), timeout=15)
            response.raise_for_status()

            thumbnails = response.json().get("value", [])
            if thumbnails:
                thumb_set = thumbnails[0]
                # 获取中等大小的缩略图
                thumb_url = thumb_set.get("c", {}).get("url") or thumb_set.get("m", {}).get("url")

                if thumb_url:
                    thumb_response = requests.get(thumb_url)
                    if thumb_response.status_code == 200:
                        return thumb_response.content

            # 如果没有缩略图，尝试生成一个
            return self._generate_fallback_thumbnail(file_path)
        except Exception:
            return None

    def _generate_fallback_thumbnail(self, file_path: str) -> bytes:
        """
        生成备用缩略图（当 OneDrive 没有缩略图时）

        Args:
            file_path: 文件路径

        Returns:
            缩略图字节数据
        """
        try:
            file_obj = self.get_object(file_path)
            img = Image.open(BytesIO(file_obj["Body"]))

            # 调整大小
            img.thumbnail(Config.THUMB_SIZE, Image.Resampling.LANCZOS)

            # 保存为 PNG
            thumb_buffer = BytesIO()
            img.save(thumb_buffer, format="PNG")
            return thumb_buffer.getvalue()
        except Exception:
            return None

    def rename_file(self, old_key: str, new_key: str) -> bool:
        """
        重命名文件

        Args:
            old_key: 旧的文件键名
            new_key: 新的文件键名

        Returns:
            重命名成功返回 True，失败返回 False
        """
        try:
            old_key = old_key.strip("/")
            new_key = new_key.strip("/")

            # 获取旧文件的 ID
            url = f"{self.graph_api_url}/me/drive/items/{self.folder_item_id}:/{old_key}:"
            response = self._api_request("GET", url)
            response.raise_for_status()
            item_id = response.json().get("id")

            # 更新文件名
            update_url = f"{self.graph_api_url}/me/drive/items/{item_id}"
            update_body = {"name": new_key.split("/")[-1]}

            response = self._api_request("PATCH", update_url, json=update_body)
            response.raise_for_status()

            return response.status_code == 200
        except Exception as e:
            raise RuntimeError(
                f"Failed to rename file in OneDrive: {str(e)}" if isinstance(e, Exception) else str(e)
            ) from None

    def delete_folder(self, prefix: str) -> bool:
        """
        删除文件夹及其中的所有文件

        Args:
            prefix: 文件夹前缀

        Returns:
            删除成功返回 True，失败返回 False
        """
        try:
            prefix = prefix.rstrip("/")

            # 获取文件夹中的所有项目
            items = self.list_objects(prefix)

            # 删除所有文件
            for file in items.get("Contents", []):
                self.delete_file(file["Key"])

            # 删除所有子文件夹
            for folder in items.get("CommonPrefixes", []):
                self.delete_folder(folder["Prefix"])

            # 删除文件夹本身
            url = f"{self.graph_api_url}/me/drive/items/{self.folder_item_id}:/{prefix}:"
            response = self._api_request("DELETE", url)

            return response.status_code == 204
        except Exception as e:
            raise RuntimeError(
                f"Failed to delete folder from OneDrive: {str(e)}" if isinstance(e, Exception) else str(e)
            ) from None

    def rename_folder(self, old_prefix: str, new_prefix: str) -> bool:
        """
        重命名文件夹

        Args:
            old_prefix: 旧的文件夹前缀
            new_prefix: 新的文件夹前缀

        Returns:
            重命名成功返回 True，失败返回 False
        """
        try:
            old_prefix = old_prefix.rstrip("/")
            new_prefix = new_prefix.rstrip("/")

            # 获取旧文件夹的 ID
            url = f"{self.graph_api_url}/me/drive/items/{self.folder_item_id}:/{old_prefix}:"
            response = self._api_request("GET", url)
            response.raise_for_status()
            item_id = response.json().get("id")

            # 更新文件夹名
            update_url = f"{self.graph_api_url}/me/drive/items/{item_id}"
            update_body = {"name": new_prefix.split("/")[-1]}

            response = self._api_request("PATCH", update_url, json=update_body)
            response.raise_for_status()

            return response.status_code == 200
        except Exception as e:
            raise RuntimeError(
                f"Failed to rename folder in OneDrive: {str(e)}" if isinstance(e, Exception) else str(e)
            ) from None

    def copy_folder(self, source_prefix: str, dest_prefix: str) -> bool:
        """
        复制文件夹及其中的所有文件

        Args:
            source_prefix: 源文件夹前缀
            dest_prefix: 目标文件夹前缀

        Returns:
            复制成功返回 True，失败返回 False
        """
        try:
            source_prefix = source_prefix.rstrip("/")
            dest_prefix = dest_prefix.rstrip("/")

            # 创建目标文件夹
            self.create_folder(dest_prefix + "/")

            # 获取源文件夹中的所有项目
            items = self.list_objects(source_prefix)

            # 复制所有文件
            for file in items.get("Contents", []):
                source_key = file["Key"]
                # 保持相对路径
                relative_path = source_key[len(source_prefix) + 1 :]
                dest_key = f"{dest_prefix}/{relative_path}"
                self.copy_file(source_key, dest_key)

            # 递归复制子文件夹
            for folder in items.get("CommonPrefixes", []):
                source_folder = folder["Prefix"].rstrip("/")
                relative_folder = source_folder[len(source_prefix) + 1 :]
                dest_folder = f"{dest_prefix}/{relative_folder}"
                self.copy_folder(source_folder, dest_folder)

            return True
        except Exception as e:
            raise RuntimeError(
                f"Failed to copy folder in OneDrive: {str(e)}" if isinstance(e, Exception) else str(e)
            ) from None

    def create_folder(self, key: str) -> bool:
        """
        创建文件夹

        Args:
            key: 文件夹路径（以 / 结尾）

        Returns:
            创建成功返回 True，失败返回 False
        """
        try:
            key = key.rstrip("/")

            # 获取父文件夹 ID
            parts = key.split("/")
            parent_id = self.folder_item_id

            # 创建每一层文件夹
            for _, folder_name in enumerate(parts):
                # 检查文件夹是否已存在
                existing_url = f"{self.graph_api_url}/me/drive/items/{parent_id}:/{folder_name}:"
                existing_response = self._api_request("GET", existing_url)

                if existing_response.status_code == 200:
                    parent_id = existing_response.json().get("id")
                    continue

                # 创建新文件夹
                create_url = f"{self.graph_api_url}/me/drive/items/{parent_id}/children"
                create_body = {"name": folder_name, "folder": {}}

                create_response = self._api_request("POST", create_url, json=create_body)
                create_response.raise_for_status()

                parent_id = create_response.json().get("id")

            return True
        except Exception as e:
            raise RuntimeError(
                f"Failed to create folder in OneDrive: {str(e)}" if isinstance(e, Exception) else str(e)
            ) from None
