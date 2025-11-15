import hashlib
from datetime import datetime
from typing import Any, Dict, List

from flask import Blueprint, Response, abort, jsonify, redirect, render_template, request

from config import Config
from storages.factory import StorageFactory

main_route = Blueprint("main", __name__)

# 延迟初始化的存储实例
_storage = None


def get_storage():
    """获取存储实例（延迟初始化）"""
    global _storage
    if _storage is None:
        _storage = StorageFactory.get_storage()
    return _storage


def get_file_url(key: str) -> str:
    """生成通过服务器访问文件的 URL"""
    return f"/file/{key}"


def build_file_entry(obj: Dict[str, Any], prefix: str) -> Dict[str, Any] | None:
    """根据对象信息构建文件条目。"""
    storage = get_storage()
    key = obj.get("Key", "")
    if not key:
        return None

    if prefix and key == prefix:
        return None

    if key.endswith("/"):
        return None

    rel_name = key[len(prefix) :] if prefix else key

    entry: Dict[str, Any] = {
        "name": rel_name,
        "key": key,
        "size": obj.get("Size"),
        "last_modified": storage.format_timestamp(obj.get("LastModified")),
        "is_dir": False,
        "file_url": get_file_url(key),
    }

    # 性能优化：避免在列表阶段为每个文件预取公共/预签名链接
    # 统一走 /file/<key> 路由，点击时再获取所需链接

    return entry


def build_directory_entry(prefix_value: str | None, current_prefix: str) -> Dict[str, Any] | None:
    """根据前缀构建目录条目。"""
    if not prefix_value:
        return None

    rel = prefix_value[len(current_prefix) :].rstrip("/") if current_prefix else prefix_value.rstrip("/")

    return {"name": rel, "key": prefix_value, "is_dir": True}


def build_entries(response: Dict[str, Any], prefix: str) -> List[Dict[str, Any]]:
    """将存储响应转换为用于模板渲染的条目列表。"""
    entries: List[Dict[str, Any]] = []

    for obj in response.get("Contents", []):
        entry = build_file_entry(obj, prefix)
        if entry:
            entries.append(entry)

    for pref in response.get("CommonPrefixes", []):
        directory_entry = build_directory_entry(pref.get("Prefix"), prefix)
        if directory_entry:
            entries.append(directory_entry)

    entries.sort(key=lambda x: (not x.get("is_dir", False), x["name"]))
    return entries


def build_crumbs(prefix: str) -> List[Dict[str, str]]:
    """根据当前前缀构建导航数据。"""
    crumbs: List[Dict[str, str]] = []
    if prefix:
        segs = prefix.rstrip("/").split("/")
        acc = ""
        for seg in segs:
            acc = acc + seg + "/"
            crumbs.append({"name": seg, "prefix": acc})
    return crumbs


@main_route.route("/")
def index():
    """
    返回文件和目录列表的 HTML 页面。
    """
    try:
        storage = get_storage()
        prefix = request.args.get("prefix", "") or ""

        response = storage.list_objects(prefix)
        entries = build_entries(response, prefix)
        crumbs = build_crumbs(prefix)

        return render_template(
            "index.html",
            entries=entries,
            current_prefix=prefix,
            crumbs=crumbs,
            current_year=datetime.now().year,
        )
    except Exception:
        abort(500)


@main_route.route("/<path:prefix_path>")
def browse(prefix_path):
    """目录路由。将 URL /a/b 映射为 prefix 'a/b/' 并重用 index 的逻辑。"""
    try:
        storage = get_storage()
        prefix = prefix_path or ""
        if prefix and not prefix.endswith("/"):
            prefix = prefix + "/"

        response = storage.list_objects(prefix)
        entries = build_entries(response, prefix)
        crumbs = build_crumbs(prefix)

        return render_template(
            "index.html",
            entries=entries,
            current_prefix=prefix,
            crumbs=crumbs,
            current_year=datetime.now().year,
        )
    except Exception:
        abort(500)


@main_route.route("/file/<path:file_path>")
def serve_file(file_path):
    """重定向到原始存储 URL，节省服务器资源"""
    try:
        storage = get_storage()
        # 验证文件存在
        try:
            storage.get_object_info(file_path)
        except Exception:
            abort(404)

        # 尝试获取预签名 URL（用于私有存储或需要时间限制的 URL）
        presigned = storage.generate_presigned_url(file_path)
        if presigned:
            return redirect(presigned)

        # 如果没有预签名 URL，尝试获取公共 URL
        public_url = storage.get_public_url(file_path)
        if public_url:
            return redirect(public_url)

        # 如果都没有可用的 URL，返回错误
        abort(403)

    except Exception:
        abort(500)


@main_route.route("/download/<path:file_path>")
def download_file(file_path):
    """下载文件，支持所有存储类型"""
    try:
        storage = get_storage()
        # 验证文件存在
        try:
            storage.get_object_info(file_path)
        except Exception:
            abort(404)

        # 使用存储后端的统一接口生成下载响应
        download_response = storage.generate_download_response(file_path)

        if not download_response:
            abort(403)

        # 根据响应类型处理
        if download_response["type"] == "redirect":
            return redirect(download_response["url"])
        elif download_response["type"] == "content":
            return Response(
                download_response["content"],
                headers=download_response["headers"],
                mimetype=download_response["mimetype"],
            )
        else:
            abort(500)

    except Exception as e:
        print(f"Download error: {e}")
        abort(500)


@main_route.route("/thumb/<path:file_path>")
def thumb(file_path):
    """返回图片的缩略图，使用 Vercel Cache Headers 避免重复从 R2 拉取"""
    storage = get_storage()
    # 设置更长的缓存控制头以支持浏览器本地缓存
    cache_headers = {
        "Cache-Control": f"public, max-age={Config.THUMB_TTL_SECONDS}",
        "ETag": f'W/"{hashlib.md5(file_path.encode("utf-8")).hexdigest()}"',
    }

    # 先检查客户端是否已经有缓存版本
    etag = request.headers.get("If-None-Match")
    if etag and etag == cache_headers["ETag"]:
        return Response(status=304, headers=cache_headers)

    # 从获取原始对象并生成缩略图
    try:
        # 对于较大的源文件，避免在函数内读取并处理，优先使用预签名 URL
        try:
            info = storage.get_object_info(file_path)
        except Exception:
            abort(404)

        size = int(info.get("ContentLength", 0) or 0)
        limit = 6 * 1024 * 1024
        if size > limit:
            presigned = storage.generate_presigned_url(file_path)
            if presigned:
                return redirect(presigned)
            abort(413)

        thumb_bytes = storage.generate_thumbnail(file_path)
        response = Response(thumb_bytes, mimetype="image/jpeg")
        response.headers.update(cache_headers)
        return response
    except Exception:
        abort(404)


@main_route.route("/upload", methods=["POST"])
def upload():
    """上传文件到存储"""
    try:
        storage = get_storage()
        # 检查是否有文件
        if "file" not in request.files:
            return jsonify({"success": False, "error": "No file provided"}), 400

        file = request.files["file"]

        # 检查文件名
        if file.filename == "":
            return jsonify({"success": False, "error": "No file selected"}), 400

        # 获取目标路径（可选）
        prefix = request.form.get("prefix", "")
        if prefix and not prefix.endswith("/"):
            prefix = prefix + "/"

        # 构建完整的文件路径
        file_path = prefix + file.filename

        # 读取文件数据
        file_data = file.read()

        # 获取文件类型
        content_type = file.content_type

        # 上传文件
        success = storage.upload_file(file_path, file_data, content_type)

        if success:
            return jsonify(
                {
                    "success": True,
                    "message": "File uploaded successfully",
                    "path": file_path,
                }
            )
        else:
            return jsonify({"success": False, "error": "Upload failed"}), 500

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@main_route.route("/delete/<path:file_path>", methods=["DELETE", "POST"])
def delete(file_path):
    """删除存储中的文件"""
    try:
        storage = get_storage()
        # 删除文件
        success = storage.delete_file(file_path)

        if success:
            return jsonify({"success": True, "message": "File deleted successfully"})
        else:
            return jsonify({"success": False, "error": "Delete failed"}), 500

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@main_route.route("/rename/<path:old_key>", methods=["POST"])
def rename(old_key):
    """重命名存储中的文件"""
    try:
        storage = get_storage()
        data = request.get_json()
        new_name = data.get("newName")

        if not new_name:
            return jsonify({"success": False, "error": "New name not provided"}), 400

        # 构建新的文件路径
        old_key_parts = old_key.rsplit("/", 1)
        if len(old_key_parts) > 1:
            new_key = f"{old_key_parts[0]}/{new_name}"
        else:
            new_key = new_name

        # 重命名文件
        success = storage.rename_file(old_key, new_key)

        if success:
            return jsonify(
                {
                    "success": True,
                    "message": "File renamed successfully",
                    "newKey": new_key,
                }
            )
        else:
            return jsonify({"success": False, "error": "Rename failed"}), 500

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@main_route.route("/delete_folder/<path:prefix>", methods=["DELETE"])
def delete_folder_route(prefix):
    """删除存储中的文件夹"""
    try:
        storage = get_storage()
        if not prefix.endswith("/"):
            prefix += "/"
        success = storage.delete_folder(prefix)
        if success:
            return jsonify({"success": True, "message": "Folder deleted successfully"})
        else:
            return jsonify({"success": False, "error": "Folder delete failed"}), 500
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@main_route.route("/rename_folder/<path:old_prefix>", methods=["POST"])
def rename_folder_route(old_prefix):
    """重命名存储中的文件夹"""
    try:
        storage = get_storage()
        data = request.get_json()
        new_name = data.get("newName")

        if not new_name:
            return jsonify({"success": False, "error": "New name not provided"}), 400

        if not old_prefix.endswith("/"):
            old_prefix += "/"

        # 构建新的文件夹路径
        prefix_parts = old_prefix.rstrip("/").rsplit("/", 1)
        if len(prefix_parts) > 1:
            new_prefix = f"{prefix_parts[0]}/{new_name}/"
        else:
            new_prefix = f"{new_name}/"

        success = storage.rename_folder(old_prefix, new_prefix)

        if success:
            return jsonify(
                {
                    "success": True,
                    "message": "Folder renamed successfully",
                    "newPrefix": new_prefix,
                }
            )
        else:
            return jsonify({"success": False, "error": "Folder rename failed"}), 500
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@main_route.route("/copy", methods=["POST"])
def copy_item():
    """复制文件或文件夹"""
    try:
        storage = get_storage()
        data = request.get_json()
        source = data.get("source")
        destination = data.get("destination")
        is_folder = data.get("is_folder", False)

        if not source or not destination:
            return (
                jsonify({"success": False, "error": "Source or destination not provided"}),
                400,
            )

        if is_folder:
            if not source.endswith("/"):
                source += "/"
            if not destination.endswith("/"):
                destination += "/"
            success = storage.copy_folder(source, destination)
        else:
            success = storage.copy_file(source, destination)

        if success:
            return jsonify({"success": True, "message": "Item copied successfully"})
        else:
            return jsonify({"success": False, "error": "Copy failed"}), 500
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@main_route.route("/move", methods=["POST"])
def move_item():
    """移动文件或文件夹"""
    try:
        storage = get_storage()
        data = request.get_json()
        source = data.get("source")
        destination = data.get("destination")
        is_folder = data.get("is_folder", False)

        if not source or not destination:
            return (
                jsonify({"success": False, "error": "Source or destination not provided"}),
                400,
            )

        if is_folder:
            if not source.endswith("/"):
                source += "/"
            if not destination.endswith("/"):
                destination += "/"
            success = storage.rename_folder(source, destination)
        else:
            success = storage.rename_file(source, destination)

        if success:
            return jsonify({"success": True, "message": "Item moved successfully"})
        else:
            return jsonify({"success": False, "error": "Move failed"}), 500
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@main_route.route("/create_folder", methods=["POST"])
def create_folder_route():
    """创建文件夹"""
    try:
        storage = get_storage()
        data = request.get_json()
        path = data.get("path")

        if not path:
            return jsonify({"success": False, "error": "Path not provided"}), 400

        if not path.endswith("/"):
            path += "/"

        success = storage.create_folder(path)

        if success:
            return jsonify({"success": True, "message": "Folder created successfully"})
        else:
            return jsonify({"success": False, "error": "Folder creation failed"}), 500
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
