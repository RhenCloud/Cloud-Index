"""
工具函数模块
集中管理常用的辅助函数
"""

from datetime import datetime
from typing import Optional


def format_timestamp(timestamp) -> str:
    """
    格式化时间戳为人类可读的格式

    Args:
        timestamp: 时间戳对象（datetime 或其他）

    Returns:
        格式化后的时间字符串
    """
    if isinstance(timestamp, datetime):
        return timestamp.strftime("%Y-%m-%d %H:%M:%S")
    return str(timestamp)


def format_file_size(size_bytes: Optional[int]) -> str:
    """
    格式化文件大小为人类可读的格式

    Args:
        size_bytes: 文件大小（字节）

    Returns:
        格式化后的大小字符串（如 "1.23MB"）
    """
    try:
        if size_bytes is None:
            return "-"
        num = float(size_bytes)
    except (ValueError, TypeError):
        return "-"

    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if num < 1024:
            # 对于字节，显示整数
            if unit == "B":
                return f"{int(num)}{unit}"
            # 其他单位保留两位小数
            return f"{num:.2f}{unit}"
        num = num / 1024.0
    return f"{num:.2f}PB"


def get_file_icon(filename: Optional[str]) -> str:
    """
    根据文件名返回对应的 Font Awesome 图标类名

    Args:
        filename: 文件名

    Returns:
        Font Awesome 图标类名
    """
    if not filename:
        return "fas fa-file"

    ext = filename.lower().split(".")[-1] if "." in filename else ""

    # 定义文件类型映射
    icon_map = {
        "fas fa-image": ["jpg", "jpeg", "png", "gif", "bmp", "webp", "svg"],
        "fas fa-music": ["mp3", "wav", "ogg", "flac", "m4a", "aac"],
        "fas fa-video": ["mp4", "webm", "avi", "mov", "wmv", "flv", "mkv"],
        "fas fa-file-alt": ["pdf", "doc", "docx", "txt", "md", "rtf"],
        "fas fa-file-archive": ["zip", "rar", "7z", "tar", "gz"],
        "fas fa-file-code": ["py", "js", "html", "css", "java", "cpp", "c", "php"],
        "fas fa-file-excel": ["xls", "xlsx", "csv"],
        "fas fa-file-powerpoint": ["ppt", "pptx"],
    }

    for icon, extensions in icon_map.items():
        if ext in extensions:
            return icon

    return "fas fa-file"


def normalize_path(path: str, is_folder: bool = False) -> str:
    """
    规范化路径格式

    Args:
        path: 原始路径
        is_folder: 是否为文件夹

    Returns:
        规范化后的路径（文件夹以 / 结尾）
    """
    path = path.strip()
    if is_folder and not path.endswith("/"):
        return path + "/"
    if not is_folder and path.endswith("/"):
        return path.rstrip("/")
    return path


def get_file_extension(filename: str) -> str:
    """
    获取文件扩展名

    Args:
        filename: 文件名

    Returns:
        小写的文件扩展名（不含点）
    """
    if not filename or "." not in filename:
        return ""
    return filename.lower().split(".")[-1]


def is_image_file(filename: str) -> bool:
    """
    判断文件是否为图片

    Args:
        filename: 文件名

    Returns:
        如果是图片文件返回 True
    """
    image_extensions = ["jpg", "jpeg", "png", "gif", "bmp", "webp", "svg", "ico"]
    return get_file_extension(filename) in image_extensions


def is_video_file(filename: str) -> bool:
    """
    判断文件是否为视频

    Args:
        filename: 文件名

    Returns:
        如果是视频文件返回 True
    """
    video_extensions = ["mp4", "webm", "ogg", "mov", "avi", "mkv", "m4v"]
    return get_file_extension(filename) in video_extensions


def is_audio_file(filename: str) -> bool:
    """
    判断文件是否为音频

    Args:
        filename: 文件名

    Returns:
        如果是音频文件返回 True
    """
    audio_extensions = ["mp3", "wav", "ogg", "m4a", "aac", "flac", "opus", "weba"]
    return get_file_extension(filename) in audio_extensions
