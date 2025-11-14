from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Dict


class BaseStorage(ABC):
    """存储后端的基类，定义统一接口"""

    @abstractmethod
    def list_objects(self, prefix: str = "") -> Dict[str, Any]:
        """
        列出存储桶中的对象

        Args:
            prefix: 对象前缀（用于目录浏览）

        Returns:
            包含对象列表的字典
        """
        pass

    @abstractmethod
    def get_object_info(self, key: str) -> Dict[str, Any]:
        """
        获取对象基本信息

        Args:
            key: 对象键名

        Returns:
            对象元数据
        """
        pass

    @abstractmethod
    def get_object(self, key: str) -> Dict[str, Any]:
        """
        获取对象内容

        Args:
            key: 对象键名

        Returns:
            包含对象内容的字典
        """
        pass

    @abstractmethod
    def generate_presigned_url(self, key: str, expires: int = None) -> str:
        """
        为指定对象生成预签名 URL

        Args:
            key: 对象键名
            expires: 过期时间（秒）

        Returns:
            预签名 URL，失败返回 None
        """
        pass

    @abstractmethod
    def get_public_url(self, key: str) -> str:
        """
        生成对象的公共访问 URL

        Args:
            key: 对象键名

        Returns:
            公共 URL，未配置返回 None
        """
        pass

    def format_timestamp(self, timestamp) -> str:
        """
        格式化时间戳为人类可读的格式

        Args:
            timestamp: 时间戳对象

        Returns:
            格式化后的时间字符串
        """
        if isinstance(timestamp, datetime):
            return timestamp.strftime("%Y-%m-%d %H:%M:%S")
        return str(timestamp)

    @abstractmethod
    def generate_thumbnail(self, file_path: str) -> bytes:
        """
        生成图片缩略图

        Args:
            file_path: 文件路径

        Returns:
            缩略图字节数据
        """
        pass

    @abstractmethod
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
        pass

    @abstractmethod
    def delete_file(self, key: str) -> bool:
        """
        删除存储中的文件

        Args:
            key: 对象键名（文件路径）

        Returns:
            删除成功返回 True，失败返回 False
        """
        pass

    @abstractmethod
    def rename_file(self, old_key: str, new_key: str) -> bool:
        """
        重命名存储中的文件

        Args:
            old_key: 旧的对象键名
            new_key: 新的对象键名

        Returns:
            重命名成功返回 True，失败返回 False
        """
        pass

    @abstractmethod
    def delete_folder(self, prefix: str) -> bool:
        """
        删除存储中的文件夹（前缀）

        Args:
            prefix: 要删除的文件夹前缀

        Returns:
            删除成功返回 True，失败返回 False
        """
        pass

    @abstractmethod
    def rename_folder(self, old_prefix: str, new_prefix: str) -> bool:
        """
        重命名存储中的文件夹（前缀）

        Args:
            old_prefix: 旧的文件夹前缀
            new_prefix: 新的文件夹前缀

        Returns:
            重命名成功返回 True，失败返回 False
        """
        pass

    @abstractmethod
    def copy_file(self, source_key: str, dest_key: str) -> bool:
        """
        复制存储中的文件

        Args:
            source_key: 源对象键名
            dest_key: 目标对象键名

        Returns:
            复制成功返回 True，失败返回 False
        """
        pass

    @abstractmethod
    def copy_folder(self, source_prefix: str, dest_prefix: str) -> bool:
        """
        复制存储中的文件夹（前缀）

        Args:
            source_prefix: 源文件夹前缀
            dest_prefix: 目标文件夹前缀

        Returns:
            复制成功返回 True，失败返回 False
        """
        pass

    @abstractmethod
    def create_folder(self, key: str) -> bool:
        """
        创建文件夹

        Args:
            key: 文件夹路径（以 / 结尾）

        Returns:
            创建成功返回 True，失败返回 False
        """
        pass

    def generate_download_response(self, key: str) -> Dict[str, Any]:
        """
        生成文件下载响应

        Args:
            key: 对象键名（文件路径）

        Returns:
            包含下载信息的字典，包括:
            - type: "redirect" 或 "content"
            - url: 重定向URL（当type为redirect时）
            - content: 文件内容（当type为content时）
            - headers: HTTP响应头
            - mimetype: MIME类型
        """
        # 默认实现：返回重定向URL
        presigned = self.generate_presigned_url(key)
        if presigned:
            return {"type": "redirect", "url": presigned}

        public_url = self.get_public_url(key)
        if public_url:
            return {"type": "redirect", "url": public_url}

        return None
