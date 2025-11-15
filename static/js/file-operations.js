/**
 * 文件操作相关功能
 * 包括上传、下载、删除、重命名等
 */

/**
 * 上传文件
 * @param {FileList} files - 文件列表
 */
async function uploadFiles(files) {
    const currentPrefix = document.body.dataset.currentPrefix || "";

    for (const file of files) {
        const formData = new FormData();
        formData.append("file", file);
        formData.append("prefix", currentPrefix);

        try {
            updateStatus(`正在上传: ${file.name}...`, null);

            const response = await fetch("/upload", {
                method: "POST",
                body: formData,
            });

            const result = await response.json();

            if (result.success) {
                const statusDiv = updateStatus(`✓ ${file.name} 上传成功！`, "success");
                hideStatusLater(statusDiv);

                setTimeout(() => {
                    window.location.reload();
                }, 2000);
            } else {
                updateStatus(`✗ ${file.name} 上传失败: ${result.error}`, "error");
            }
        } catch (error) {
            updateStatus(`✗ ${file.name} 上传失败: ${error.message}`, "error");
        }
    }
}

/**
 * 提示删除文件
 */
async function promptDelete() {
    const suggested = "";
    const path = await showPrompt("请输入要删除的文件路径（相对于存储桶），例如：folder/file.jpg", {
        title: "删除文件",
        defaultValue: suggested,
        placeholder: "folder/file.jpg",
        confirmLabel: "删除",
    });

    if (path) {
        await deleteFile(path);
    }
}

/**
 * 删除文件夹
 * @param {string} prefix - 文件夹前缀
 */
async function deleteFolder(prefix) {
    const confirmed = await showConfirm(`确定要删除文件夹 "${prefix}" 及其所有内容吗？此操作不可逆！`, {
        title: "删除文件夹",
        confirmLabel: "确认删除",
    });

    if (!confirmed) {
        return;
    }

    updateStatus(`正在删除文件夹: ${prefix}...`, null);

    try {
        const response = await fetch(`/delete_folder/${prefix}`, {
            method: "DELETE",
        });

        const result = await response.json();

        if (result.success) {
            const statusDiv = updateStatus("✓ 文件夹删除成功！", "success");
            hideStatusLater(statusDiv);

            setTimeout(() => {
                const parentPath = prefix.split("/").slice(0, -2).join("/");
                window.location.href = parentPath ? `/${parentPath}` : "/";
            }, 1500);
        } else {
            updateStatus(`✗ 删除失败: ${result.error}`, "error");
        }
    } catch (error) {
        updateStatus(`✗ 删除失败: ${error.message}`, "error");
    }
}

/**
 * 删除单个文件
 * @param {string} filePath - 文件路径
 * @param {object} options - 选项
 * @returns {Promise<boolean>}
 */
async function deleteFile(filePath, options = {}) {
    const { skipConfirm = false, suppressReload = false, suppressStatus = false } = options;

    if (!skipConfirm) {
        const confirmed = await showConfirm(`确定要删除 "${filePath}" 吗？`, {
            title: "删除文件",
            confirmLabel: "删除",
        });

        if (!confirmed) {
            return false;
        }
    }

    if (!suppressStatus) {
        updateStatus(`正在删除: ${filePath}...`, null);
    }

    try {
        const response = await fetch(`/delete/${filePath}`, {
            method: "DELETE",
        });

        const result = await response.json();

        if (result.success) {
            if (!suppressStatus) {
                const statusDiv = updateStatus("✓ 文件删除成功！", "success");
                hideStatusLater(statusDiv);
            }

            if (!suppressReload) {
                setTimeout(() => {
                    window.location.reload();
                }, 2000);
            }

            return true;
        }

        if (!suppressStatus) {
            updateStatus(`✗ 删除失败: ${result.error}`, "error");
        }
        return false;
    } catch (error) {
        if (!suppressStatus) {
            updateStatus(`✗ 删除失败: ${error.message}`, "error");
        }
        return false;
    }
}

/**
 * 下载文件
 * @param {string} url - 下载 URL
 * @param {string} filename - 文件名
 */
function downloadFile(url, filename) {
    if (!url) {
        updateStatus("✗ 无法下载：缺少下载链接", "error");
        return;
    }

    if (url.startsWith("/download/") || url.startsWith("/file/")) {
        // 让浏览器原生跟随服务器重定向（OneDrive 直链/共享链接），避免 fetch 对 3xx 的处理差异
        const link = document.createElement("a");
        link.href = url;
        link.target = "_blank";
        link.rel = "noopener";

        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);

        const statusDiv = updateStatus(`✓ 开始下载: ${filename || ""}`, "success");
        hideStatusLater(statusDiv);
    } else {
        const link = document.createElement("a");
        link.href = url;
        link.download = filename || "";
        link.target = "_blank";
        link.rel = "noopener";

        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);

        const statusDiv = updateStatus(`✓ 开始下载: ${filename || ""}`, "success");
        hideStatusLater(statusDiv);
    }
}

/**
 * 重命名文件
 * @param {string} oldKey - 旧的文件键
 * @param {string} newName - 新名称
 */
async function renameFile(oldKey, newName) {
    updateStatus(`正在重命名: ${oldKey}...`, null);

    try {
        const response = await fetch(`/rename/${oldKey}`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({ newName: newName }),
        });

        const result = await response.json();

        if (result.success) {
            const statusDiv = updateStatus("✓ 文件重命名成功！", "success");
            hideStatusLater(statusDiv);

            setTimeout(() => {
                window.location.reload();
            }, 1500);
        } else {
            updateStatus(`✗ 重命名失败: ${result.error}`, "error");
        }
    } catch (error) {
        updateStatus(`✗ 重命名失败: ${error.message}`, "error");
    }
}

/**
 * 重命名文件夹
 * @param {string} oldPrefix - 旧的文件夹前缀
 * @param {string} newName - 新名称
 */
async function renameFolder(oldPrefix, newName) {
    updateStatus(`正在重命名文件夹: ${oldPrefix}...`, null);

    try {
        const response = await fetch(`/rename_folder/${oldPrefix}`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({ newName: newName }),
        });

        const result = await response.json();

        if (result.success) {
            const statusDiv = updateStatus("✓ 文件夹重命名成功！", "success");
            hideStatusLater(statusDiv);

            setTimeout(() => {
                window.location.reload();
            }, 1500);
        } else {
            updateStatus(`✗ 重命名失败: ${result.error}`, "error");
        }
    } catch (error) {
        updateStatus(`✗ 重命名失败: ${error.message}`, "error");
    }
}

/**
 * 提示重命名
 * @param {string} oldKey - 旧键
 * @param {string} oldName - 旧名称
 * @param {boolean} isFolder - 是否是文件夹
 */
async function promptRename(oldKey, oldName, isFolder = false) {
    const title = isFolder ? "重命名文件夹" : "重命名文件";
    const newName = await showPrompt(`请输入新的名称：`, {
        title: title,
        defaultValue: oldName,
        confirmLabel: "重命名",
    });

    if (newName && newName !== oldName) {
        if (isFolder) {
            await renameFolder(oldKey, newName);
        } else {
            await renameFile(oldKey, newName);
        }
    }
}

/**
 * 复制项目
 * @param {string} source - 源路径
 * @param {string} destination - 目标路径
 * @param {boolean} isFolder - 是否是文件夹
 */
async function copyItem(source, destination, isFolder) {
    updateStatus(`正在复制...`, null);
    await performOperation("/copy", "复制", { source, destination, is_folder: isFolder });
}

/**
 * 移动项目
 * @param {string} source - 源路径
 * @param {string} destination - 目标路径
 * @param {boolean} isFolder - 是否是文件夹
 */
async function moveItem(source, destination, isFolder) {
    updateStatus(`正在移动...`, null);
    await performOperation("/move", "移动", { source, destination, is_folder: isFolder });
}

/**
 * 提示复制或移动
 * @param {string} source - 源路径
 * @param {boolean} isFolder - 是否是文件夹
 * @param {string} operation - 操作类型 ('copy' 或 'move')
 */
async function promptCopyOrMove(source, isFolder, operation) {
    const opText = operation === "copy" ? "复制" : "移动";
    const itemText = isFolder ? "文件夹" : "文件";
    const dest = await showPrompt(`请输入目标目录路径：`, {
        title: `${opText}${itemText}`,
        confirmLabel: opText,
    });

    if (dest) {
        let normalizedDest = dest;
        if (!normalizedDest.endsWith("/")) {
            normalizedDest += "/";
        }
        let name = source
            .split("/")
            .filter((p) => p)
            .pop();
        if (isFolder) {
            name += "/";
        }
        const fullDest = normalizedDest + name;

        if (operation === "copy") {
            await copyItem(source, fullDest, isFolder);
        } else {
            await moveItem(source, fullDest, isFolder);
        }
    }
}

/**
 * 执行复制/移动操作
 * @param {string} endpoint - API 端点
 * @param {string} opText - 操作文本
 * @param {object} body - 请求体
 */
async function performOperation(endpoint, opText, body) {
    try {
        const response = await fetch(endpoint, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify(body),
        });

        const result = await response.json();

        if (result.success) {
            const statusDiv = updateStatus(`✓ ${opText}成功！`, "success");
            hideStatusLater(statusDiv);

            setTimeout(() => {
                window.location.reload();
            }, 1500);
        } else {
            updateStatus(`✗ ${opText}失败: ${result.error}`, "error");
        }
    } catch (error) {
        updateStatus(`✗ ${opText}失败: ${error.message}`, "error");
    }
}

/**
 * 导出到全局作用域
 */
window.FileOps = {
    uploadFiles,
    promptDelete,
    deleteFolder,
    deleteFile,
    downloadFile,
    renameFile,
    renameFolder,
    promptRename,
    copyItem,
    moveItem,
    promptCopyOrMove,
    performOperation,
};
