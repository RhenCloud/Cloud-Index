import os

import dotenv
from flask import Flask

from handlers.routes import main_route
from storages.factory import StorageFactory

dotenv.load_dotenv()

app = Flask(__name__)


# 注册蓝图
app.register_blueprint(main_route)

# 初始化存储（使用工厂模式）
storage = StorageFactory.get_storage()

# 缩略图默认 TTL（秒），可通过环境变量覆盖
THUMB_TTL = int(os.environ.get("THUMB_TTL_SECONDS", "3600"))


# 注册一个安全的 filesizeformat 过滤器，处理 None 和非数字值
@app.template_filter("filesizeformat")
def filesizeformat_filter(value):
    try:
        if value is None:
            return "-"
        num = float(value)  # 使用 float 而不是 int 以保持精度
    except Exception:
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


# 注册一个文件图标过滤器
@app.template_filter("fileicon")
def fileicon_filter(filename):
    if not filename:
        return "fas fa-file"

    ext = filename.lower().split(".")[-1] if "." in filename else ""

    # 图片文件
    if ext in ["jpg", "jpeg", "png", "gif", "bmp", "webp", "svg"]:
        return "fas fa-image"

    # 音频文件
    if ext in ["mp3", "wav", "ogg", "flac", "m4a", "aac"]:
        return "fas fa-music"

    # 视频文件
    if ext in ["mp4", "webm", "avi", "mov", "wmv", "flv", "mkv"]:
        return "fas fa-video"

    # 文档文件
    if ext in ["pdf", "doc", "docx", "txt", "md", "rtf"]:
        return "fas fa-file-alt"

    # 压缩文件
    if ext in ["zip", "rar", "7z", "tar", "gz"]:
        return "fas fa-file-archive"

    # 代码文件
    if ext in ["py", "js", "html", "css", "java", "cpp", "c", "php"]:
        return "fas fa-file-code"

    # 表格文件
    if ext in ["xls", "xlsx", "csv"]:
        return "fas fa-file-excel"

    # 演示文件
    if ext in ["ppt", "pptx"]:
        return "fas fa-file-powerpoint"

    # 默认文件图标
    return "fas fa-file"


def get_public_url(key: str) -> str:
    """
    生成对象的公共访问 URL
    """
    return storage.get_public_url(key)


def format_timestamp(timestamp) -> str:
    """
    格式化时间戳为人类可读的格式
    """
    return storage.format_timestamp(timestamp)


def generate_presigned_url(
    s3_client, bucket_name: str, key: str, expires: int = None
) -> str:
    """为指定对象生成 presigned URL（GET）。"""
    return storage.generate_presigned_url(key, expires)


def get_file_url(key: str) -> str:
    """生成通过服务器访问文件的 URL"""
    return f"/file/{key}"


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    host = os.environ.get("HOST", "0.0.0.0")
    app.run(host=host, port=port, debug=True)
