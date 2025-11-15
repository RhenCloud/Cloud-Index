"""
配置管理模块
集中管理所有环境变量和应用配置
"""

import os
from typing import Optional

import dotenv

# 加载环境变量
dotenv.load_dotenv()


class Config:
    """应用配置类"""

    # 存储配置
    STORAGE_TYPE: str = os.getenv("STORAGE_TYPE", "").lower()

    # R2 配置
    R2_ACCOUNT_ID: Optional[str] = os.getenv("R2_ACCOUNT_ID")
    R2_ACCESS_KEY_ID: Optional[str] = os.getenv("R2_ACCESS_KEY_ID")
    R2_SECRET_ACCESS_KEY: Optional[str] = os.getenv("R2_SECRET_ACCESS_KEY")
    R2_BUCKET_NAME: Optional[str] = os.getenv("R2_BUCKET_NAME")
    R2_PUBLIC_DOMAIN: Optional[str] = os.getenv("R2_PUBLIC_DOMAIN")

    # GitHub 配置
    GITHUB_TOKEN: Optional[str] = os.getenv("GITHUB_TOKEN")
    GITHUB_REPO: Optional[str] = os.getenv("GITHUB_REPO")  # 格式: owner/repo
    GITHUB_BRANCH: str = os.getenv("GITHUB_BRANCH", "main")

    # OneDrive 配置
    ONEDRIVE_REFRESH_TOKEN: Optional[str] = os.getenv("ONEDRIVE_REFRESH_TOKEN")
    ONEDRIVE_CLIENT_ID: Optional[str] = os.getenv("ONEDRIVE_CLIENT_ID")
    ONEDRIVE_CLIENT_SECRET: Optional[str] = os.getenv("ONEDRIVE_CLIENT_SECRET")
    ONEDRIVE_FOLDER_ID: Optional[str] = os.getenv("ONEDRIVE_FOLDER_ID")  # 可选，默认使用 /me/drive/root
    ONEDRIVE_REDIRECT_URI: Optional[str] = os.getenv("ONEDRIVE_REDIRECT_URI")  # 可选，刷新令牌时某些应用需要

    # 应用配置
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "5000"))
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"

    # 缩略图配置
    THUMB_TTL_SECONDS: int = int(os.getenv("THUMB_TTL_SECONDS", "3600"))
    THUMB_SIZE: tuple[int, int] = (300, 300)  # 缩略图尺寸

    # URL过期时间配置
    PRESIGNED_URL_EXPIRES: int = int(os.getenv("PRESIGNED_URL_EXPIRES", "3600"))

    @classmethod
    def validate(cls) -> None:
        """验证必需的配置项是否已设置"""
        if not cls.STORAGE_TYPE:
            raise ValueError("STORAGE_TYPE environment variable is not set. Supported types: r2, github, onedrive")

        if cls.STORAGE_TYPE == "r2":
            required = ["R2_ACCOUNT_ID", "R2_ACCESS_KEY_ID", "R2_SECRET_ACCESS_KEY", "R2_BUCKET_NAME"]
            missing = [key for key in required if not getattr(cls, key)]
            if missing:
                raise ValueError(f"Missing required R2 configuration: {', '.join(missing)}")

        elif cls.STORAGE_TYPE == "github":
            required = ["GITHUB_TOKEN", "GITHUB_REPO"]
            missing = [key for key in required if not getattr(cls, key)]
            if missing:
                raise ValueError(f"Missing required GitHub configuration: {', '.join(missing)}")

        elif cls.STORAGE_TYPE == "onedrive":
            required = ["ONEDRIVE_REFRESH_TOKEN", "ONEDRIVE_CLIENT_ID", "ONEDRIVE_CLIENT_SECRET"]
            missing = [key for key in required if not getattr(cls, key)]
            if missing:
                raise ValueError(f"Missing required OneDrive configuration: {', '.join(missing)}")

        elif cls.STORAGE_TYPE not in ["r2", "github", "onedrive"]:
            raise ValueError(f"Unsupported storage type: {cls.STORAGE_TYPE}. Supported types: r2, github, onedrive")

    @classmethod
    def get_storage_config(cls) -> dict:
        """获取当前存储类型的配置字典"""
        if cls.STORAGE_TYPE == "r2":
            return {
                "account_id": cls.R2_ACCOUNT_ID,
                "access_key_id": cls.R2_ACCESS_KEY_ID,
                "secret_access_key": cls.R2_SECRET_ACCESS_KEY,
                "bucket_name": cls.R2_BUCKET_NAME,
                "public_domain": cls.R2_PUBLIC_DOMAIN,
            }
        elif cls.STORAGE_TYPE == "github":
            return {
                "token": cls.GITHUB_TOKEN,
                "repo": cls.GITHUB_REPO,
                "branch": cls.GITHUB_BRANCH,
            }
        elif cls.STORAGE_TYPE == "onedrive":
            return {
                "client_id": cls.ONEDRIVE_CLIENT_ID,
                "client_secret": cls.ONEDRIVE_CLIENT_SECRET,
                "refresh_token": cls.ONEDRIVE_REFRESH_TOKEN,
                "folder_id": cls.ONEDRIVE_FOLDER_ID,
                "redirect_uri": cls.ONEDRIVE_REDIRECT_URI,
            }
        return {}
