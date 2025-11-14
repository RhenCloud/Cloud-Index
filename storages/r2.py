import os
from io import BytesIO
from typing import Any, Dict

import boto3
from botocore.config import Config as BotocoreConfig
from PIL import Image

from config import Config

from .base import BaseStorage


class R2Storage(BaseStorage):
    """Cloudflare R2 存储后端实现"""

    def __init__(self):
        """初始化 R2 存储客户端"""
        # 从统一配置中读取
        account_id = Config.R2_ACCOUNT_ID
        if not account_id:
            raise RuntimeError("R2_ACCOUNT_ID environment variable is not set")

        self.endpoint = f"https://{account_id}.r2.cloudflarestorage.com"
        self.access_key = Config.R2_ACCESS_KEY_ID
        self.secret_key = Config.R2_SECRET_ACCESS_KEY

        if not self.access_key or not self.secret_key:
            raise RuntimeError("R2_ACCESS_KEY_ID and R2_SECRET_ACCESS_KEY must be set")

        self.region_name = "auto"
        self.bucket_name = Config.R2_BUCKET_NAME
        self.public_domain = Config.R2_PUBLIC_DOMAIN

    def get_s3_client(self):
        """
        创建并返回配置好的 S3 客户端，用于访问 R2 存储
        """
        return boto3.client(
            "s3",
            endpoint_url=self.endpoint,
            aws_access_key_id=self.access_key,
            aws_secret_access_key=self.secret_key,
            config=BotocoreConfig(signature_version="s3v4"),
            region_name=self.region_name,
        )

    def list_objects(self, prefix: str = "") -> Dict[str, Any]:
        """
        列出存储桶中的对象
        """
        s3_client = self.get_s3_client()

        if prefix and not prefix.endswith("/"):
            prefix = prefix + "/"

        list_kwargs = {"Bucket": self.bucket_name, "Delimiter": "/"}
        if prefix:
            list_kwargs["Prefix"] = prefix

        return s3_client.list_objects_v2(**list_kwargs)

    def get_object_info(self, key: str) -> Dict[str, Any]:
        """
        获取对象基本信息
        """
        s3_client = self.get_s3_client()
        return s3_client.head_object(Bucket=self.bucket_name, Key=key)

    def get_object(self, key: str) -> Dict[str, Any]:
        """
        获取对象内容
        """
        s3_client = self.get_s3_client()
        return s3_client.get_object(Bucket=self.bucket_name, Key=key)

    def generate_presigned_url(self, key: str, expires: int = None) -> str:
        """为指定对象生成 presigned URL（GET）。"""
        s3_client = self.get_s3_client()

        if expires is None:
            try:
                expires = int(os.getenv("R2_PRESIGN_EXPIRES", "3600"))
            except Exception:
                expires = 3600

        try:
            url = s3_client.generate_presigned_url(
                "get_object",
                Params={"Bucket": self.bucket_name, "Key": key},
                ExpiresIn=expires,
            )
            return url
        except Exception:
            return None

    def get_public_url(self, key: str) -> str:
        """
        生成对象的公共访问 URL
        """
        if not self.public_domain:
            return None
        return f"{self.public_domain.rstrip('/')}/{key}"

    def generate_thumbnail(self, file_path: str) -> bytes:
        """
        生成图片缩略图
        """
        try:
            obj = self.get_object(file_path)
            data = obj["Body"].read()

            img = Image.open(BytesIO(data))
            img = img.convert("RGB")
            img.thumbnail((320, 320))
            buf = BytesIO()
            img.save(buf, "JPEG", quality=80, optimize=True)
            buf.seek(0)
            return buf.getvalue()
        except Exception:
            raise

    def upload_file(self, key: str, file_data: bytes, content_type: str = None) -> bool:
        """
        上传文件到 R2 存储
        """
        try:
            s3_client = self.get_s3_client()

            # 如果没有指定 content_type，尝试根据文件扩展名猜测
            if not content_type:
                content_type = self._guess_content_type(key)

            # 上传文件
            s3_client.put_object(
                Bucket=self.bucket_name,
                Key=key,
                Body=file_data,
                ContentType=content_type,
            )
            return True
        except Exception as e:
            print(f"Upload failed: {str(e)}")
            return False

    def delete_file(self, key: str) -> bool:
        """
        从 R2 存储删除文件
        """
        try:
            s3_client = self.get_s3_client()
            s3_client.delete_object(Bucket=self.bucket_name, Key=key)
            return True
        except Exception as e:
            print(f"Delete failed: {str(e)}")
            return False

    def rename_file(self, old_key: str, new_key: str) -> bool:
        """
        重命名 R2 中的对象，通过复制和删除实现
        """
        try:
            s3_client = self.get_s3_client()

            # 复制对象到新路径
            copy_source = {"Bucket": self.bucket_name, "Key": old_key}
            s3_client.copy_object(CopySource=copy_source, Bucket=self.bucket_name, Key=new_key)

            # 删除原对象
            s3_client.delete_object(Bucket=self.bucket_name, Key=old_key)

            return True
        except Exception as e:
            print(f"Rename failed: {str(e)}")
            return False

    def delete_folder(self, prefix: str) -> bool:
        """
        删除 R2 中整个文件夹（前缀）下的所有对象
        """
        try:
            s3_client = self.get_s3_client()
            paginator = s3_client.get_paginator("list_objects_v2")
            pages = paginator.paginate(Bucket=self.bucket_name, Prefix=prefix)

            objects_to_delete = []
            for page in pages:
                if "Contents" in page:
                    for obj in page["Contents"]:
                        objects_to_delete.append({"Key": obj["Key"]})

            if not objects_to_delete:
                return True  # 文件夹为空，直接返回成功

            # 分批次删除，S3/R2 一次最多删除 1000 个
            for i in range(0, len(objects_to_delete), 1000):
                chunk = objects_to_delete[i : i + 1000]
                s3_client.delete_objects(Bucket=self.bucket_name, Delete={"Objects": chunk})

            return True
        except Exception as e:
            print(f"Folder delete failed: {str(e)}")
            return False

    def rename_folder(self, old_prefix: str, new_prefix: str) -> bool:
        """
        重命名 R2 中的文件夹（前缀），通过复制和删除实现
        """
        try:
            s3_client = self.get_s3_client()
            paginator = s3_client.get_paginator("list_objects_v2")
            pages = paginator.paginate(Bucket=self.bucket_name, Prefix=old_prefix)

            objects_to_rename = []
            for page in pages:
                if "Contents" in page:
                    for obj in page["Contents"]:
                        objects_to_rename.append(obj["Key"])

            if not objects_to_rename:
                return True  # 文件夹为空，直接返回成功

            for old_key in objects_to_rename:
                new_key = old_key.replace(old_prefix, new_prefix, 1)
                copy_source = {"Bucket": self.bucket_name, "Key": old_key}
                s3_client.copy_object(CopySource=copy_source, Bucket=self.bucket_name, Key=new_key)

            # 删除旧文件夹下的所有对象
            self.delete_folder(old_prefix)

            return True
        except Exception as e:
            print(f"Folder rename failed: {str(e)}")
            return False

    def copy_file(self, source_key: str, dest_key: str) -> bool:
        """
        复制 R2 中的对象
        """
        try:
            s3_client = self.get_s3_client()
            copy_source = {"Bucket": self.bucket_name, "Key": source_key}
            s3_client.copy_object(CopySource=copy_source, Bucket=self.bucket_name, Key=dest_key)
            return True
        except Exception as e:
            print(f"File copy failed: {str(e)}")
            return False

    def copy_folder(self, source_prefix: str, dest_prefix: str) -> bool:
        """
        复制 R2 中的文件夹（前缀）
        """
        try:
            s3_client = self.get_s3_client()
            paginator = s3_client.get_paginator("list_objects_v2")
            pages = paginator.paginate(Bucket=self.bucket_name, Prefix=source_prefix)

            for page in pages:
                if "Contents" in page:
                    for obj in page["Contents"]:
                        old_key = obj["Key"]
                        new_key = old_key.replace(source_prefix, dest_prefix, 1)
                        copy_source = {"Bucket": self.bucket_name, "Key": old_key}
                        s3_client.copy_object(
                            CopySource=copy_source,
                            Bucket=self.bucket_name,
                            Key=new_key,
                        )
            return True
        except Exception as e:
            print(f"Folder copy failed: {str(e)}")
            return False

    def create_folder(self, key: str) -> bool:
        """
        在 R2 中创建文件夹（通过创建一个以 / 结尾的 0 字节对象）
        """
        try:
            s3_client = self.get_s3_client()
            s3_client.put_object(Bucket=self.bucket_name, Key=key, Body=b"")
            return True
        except Exception as e:
            print(f"Folder creation failed: {str(e)}")
            return False

    def _guess_content_type(self, filename: str) -> str:
        """
        根据文件扩展名猜测 Content-Type
        """
        ext = filename.lower().split(".")[-1] if "." in filename else ""

        content_types = {
            "jpg": "image/jpeg",
            "jpeg": "image/jpeg",
            "png": "image/png",
            "gif": "image/gif",
            "webp": "image/webp",
            "svg": "image/svg+xml",
            "pdf": "application/pdf",
            "html": "text/html",
            "css": "text/css",
            "js": "application/javascript",
            "json": "application/json",
            "xml": "application/xml",
            "txt": "text/plain",
            "md": "text/markdown",
            "mp4": "video/mp4",
            "webm": "video/webm",
            "mp3": "audio/mpeg",
            "wav": "audio/wav",
            "zip": "application/zip",
            "rar": "application/x-rar-compressed",
            "7z": "application/x-7z-compressed",
            "tar": "application/x-tar",
            "gz": "application/gzip",
        }

        return content_types.get(ext, "application/octet-stream")

    def generate_download_response(self, key: str) -> Dict[str, Any]:
        """
        生成文件下载响应（R2 实现）

        Args:
            key: 对象键名（文件路径）

        Returns:
            包含下载信息的字典
        """
        try:
            s3_client = self.get_s3_client()
            file_name = key.split("/")[-1] if "/" in key else key

            # 使用 RFC 5987 编码处理文件名
            from urllib.parse import quote

            encoded_filename = quote(file_name.encode("utf-8"), safe="")

            # 生成带有 Content-Disposition 的预签名 URL
            expires = int(os.getenv("R2_PRESIGN_EXPIRES", "3600"))

            url = s3_client.generate_presigned_url(
                "get_object",
                Params={
                    "Bucket": self.bucket_name,
                    "Key": key,
                    "ResponseContentDisposition": f"attachment; filename=\"{file_name}\"; filename*=UTF-8''{encoded_filename}",
                },
                ExpiresIn=expires,
            )

            if url:
                return {"type": "redirect", "url": url}

            # 如果预签名 URL 失败，尝试公共 URL
            public_url = self.get_public_url(key)
            if public_url:
                return {"type": "redirect", "url": public_url}

            return None
        except Exception as e:
            print(f"R2 download response generation failed: {str(e)}")
            return None
