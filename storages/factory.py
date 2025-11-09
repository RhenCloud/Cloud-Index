import os
from typing import Optional

import dotenv

from .base import BaseStorage
from .github import GitHubStorage
from .r2 import R2Storage

dotenv.load_dotenv()


class StorageFactory:
    """存储工厂类，根据配置创建对应的存储实例"""

    _instance: Optional[BaseStorage] = None

    @classmethod
    def get_storage(cls) -> BaseStorage:
        """
        获取存储实例（单例模式）

        Returns:
            BaseStorage: 存储实例

        Raises:
            RuntimeError: 当存储类型未配置或不支持时
        """
        if cls._instance is not None:
            return cls._instance

        storage_type = os.getenv(
            "STORAGE_TYPE",
        ).lower()

        if storage_type == "r2":
            cls._instance = R2Storage()
        elif storage_type == "github":
            cls._instance = GitHubStorage()
        else:
            raise RuntimeError(
                f"Unsupported storage type: {storage_type}. Supported types: r2, github"
            )

        return cls._instance

    @classmethod
    def reset(cls):
        """重置单例实例（主要用于测试）"""
        cls._instance = None
