import tomllib
from pathlib import Path

from flask import Flask

import utils
from config import Config
from handlers.routes import main_route
from storages.factory import StorageFactory

# 验证配置
Config.validate()


# 从 pyproject.toml 读取版本号
def get_version() -> str:
    """从 pyproject.toml 读取项目版本号"""
    try:
        pyproject_path = Path(__file__).parent / "pyproject.toml"
        with open(pyproject_path, "rb") as f:
            pyproject_data = tomllib.load(f)
        return pyproject_data.get("project", {}).get("version", "0.0.0")
    except Exception:
        return "0.0.0"


__version__ = get_version()

app = Flask(__name__)


# 注册蓝图
app.register_blueprint(main_route)

# 初始化存储（使用工厂模式）
storage = StorageFactory.get_storage()


# 注册模板过滤器
@app.template_filter("filesizeformat")
def filesizeformat_filter(value):
    """格式化文件大小"""
    return utils.format_file_size(value)


@app.template_filter("fileicon")
def fileicon_filter(filename):
    """获取文件图标"""
    return utils.get_file_icon(filename)


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


def generate_presigned_url(s3_client, bucket_name: str, key: str, expires: int = None) -> str:
    """为指定对象生成 presigned URL（GET）。"""
    return storage.generate_presigned_url(key, expires)


def get_file_url(key: str) -> str:
    """生成通过服务器访问文件的 URL"""
    return f"/file/{key}"


# 注册全局模板变量
@app.context_processor
def inject_version():
    """向所有模板注入版本号"""
    return {"app_version": __version__}


if __name__ == "__main__":
    app.run(host=Config.HOST, port=Config.PORT, debug=Config.DEBUG)
