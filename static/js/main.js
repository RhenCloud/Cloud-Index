(function () {
    function updateStatus(message, state) {
        const statusDiv = document.getElementById("uploadStatus");
        if (!statusDiv) {
            return null;
        }

        statusDiv.textContent = message;
        statusDiv.className = "upload-status" + (state ? ` ${state}` : "");
        statusDiv.style.display = "block";
        return statusDiv;
    }

    function hideStatusLater(statusDiv, delay = 2000) {
        if (!statusDiv) {
            return;
        }
        setTimeout(() => {
            statusDiv.style.display = "none";
        }, delay);
    }

    const dialogState = {
        container: null,
        title: null,
        message: null,
        inputWrapper: null,
        input: null,
        confirmBtn: null,
        cancelBtn: null,
        resolve: null,
        options: null,
        previousActiveElement: null,
    };

    function isDialogOpen() {
        return Boolean(dialogState.container && !dialogState.container.hasAttribute("hidden"));
    }

    function closeDialog(confirmed) {
        if (!dialogState.resolve || !dialogState.container) {
            return;
        }

        const showInput = dialogState.options?.showInput;
        const value = confirmed && showInput && dialogState.input ? dialogState.input.value : undefined;

        dialogState.container.classList.remove("is-visible");
        dialogState.container.setAttribute("aria-hidden", "true");

        window.setTimeout(() => {
            if (!dialogState.container.classList.contains("is-visible")) {
                dialogState.container.setAttribute("hidden", "");
            }
        }, 200);

        if (dialogState.inputWrapper) {
            dialogState.inputWrapper.hidden = true;
        }

        const resolve = dialogState.resolve;
        dialogState.resolve = null;
        const options = dialogState.options || {};
        dialogState.options = null;

        if (dialogState.previousActiveElement && typeof dialogState.previousActiveElement.focus === "function") {
            dialogState.previousActiveElement.focus({ preventScroll: true });
        }
        dialogState.previousActiveElement = null;

        resolve({
            confirmed,
            value: value !== undefined ? value : undefined,
            options,
        });
    }

    function openDialog(options) {
        if (!dialogState.container) {
            return Promise.resolve({ confirmed: false });
        }

        return new Promise((resolve) => {
            dialogState.resolve = resolve;
            dialogState.options = options;
            dialogState.previousActiveElement =
                document.activeElement instanceof HTMLElement ? document.activeElement : null;

            dialogState.container.removeAttribute("hidden");
            dialogState.container.setAttribute("aria-hidden", "false");

            if (dialogState.title) {
                dialogState.title.textContent = options.title || "";
                dialogState.title.hidden = !options.title;
            }

            if (dialogState.message) {
                dialogState.message.textContent = options.message || "";
            }

            if (dialogState.inputWrapper && dialogState.input) {
                dialogState.inputWrapper.hidden = !options.showInput;
                dialogState.input.value = options.defaultValue || "";
                dialogState.input.placeholder = options.placeholder || "";
            }

            if (dialogState.confirmBtn) {
                dialogState.confirmBtn.textContent = options.confirmLabel || "确定";
            }

            if (dialogState.cancelBtn) {
                dialogState.cancelBtn.textContent = options.cancelLabel || "取消";
                dialogState.cancelBtn.hidden = options.hideCancel || false;
            }

            window.requestAnimationFrame(() => {
                if (!dialogState.container) {
                    return;
                }
                dialogState.container.classList.add("is-visible");

                if (options.showInput && dialogState.input) {
                    dialogState.input.focus();
                    dialogState.input.select();
                } else if (dialogState.confirmBtn) {
                    dialogState.confirmBtn.focus();
                }
            });
        });
    }

    function initDialog() {
        const container = document.getElementById("appDialog");
        if (!container || container.dataset.initialized === "true") {
            return;
        }

        container.dataset.initialized = "true";
        dialogState.container = container;
        dialogState.title = document.getElementById("appDialogTitle");
        dialogState.message = document.getElementById("appDialogMessage");
        dialogState.inputWrapper = document.getElementById("appDialogInputWrapper");
        dialogState.input = document.getElementById("appDialogInput");
        dialogState.confirmBtn = document.getElementById("appDialogConfirm");
        dialogState.cancelBtn = document.getElementById("appDialogCancel");

        if (dialogState.confirmBtn) {
            dialogState.confirmBtn.addEventListener("click", () => closeDialog(true));
        }

        if (dialogState.cancelBtn) {
            dialogState.cancelBtn.addEventListener("click", () => closeDialog(false));
        }

        container.addEventListener("click", (event) => {
            if (
                event.target === container ||
                (event.target instanceof HTMLElement && event.target.dataset.dialogDismiss === "true")
            ) {
                closeDialog(false);
            }
        });

        document.addEventListener("keydown", (event) => {
            if (!isDialogOpen()) {
                return;
            }

            if (event.key === "Escape") {
                event.preventDefault();
                closeDialog(false);
                return;
            }

            if (event.key === "Enter" && dialogState.options?.showInput) {
                const active = document.activeElement;
                if (active === dialogState.input) {
                    event.preventDefault();
                    closeDialog(true);
                }
            }
        });
    }

    function showConfirm(message, options = {}) {
        return openDialog({
            title: options.title || "确认操作",
            message,
            confirmLabel: options.confirmLabel || "确定",
            cancelLabel: options.cancelLabel || "取消",
            hideCancel: options.hideCancel || false,
        }).then((result) => Boolean(result.confirmed));
    }

    async function showPrompt(message, options = {}) {
        const result = await openDialog({
            title: options.title || "请输入内容",
            message,
            confirmLabel: options.confirmLabel || "确定",
            cancelLabel: options.cancelLabel || "取消",
            showInput: true,
            defaultValue: options.defaultValue || "",
            placeholder: options.placeholder || "",
        });

        if (!result.confirmed) {
            return null;
        }

        const value = typeof result.value === "string" ? result.value.trim() : "";
        return value === "" ? null : value;
    }

    function initThemeAndView() {
        const themeToggle = document.getElementById("themeToggle");
        const viewToggle = document.getElementById("viewToggle");

        if (!themeToggle || !viewToggle) {
            return;
        }

        const themeIcon = themeToggle.querySelector("i");
        const viewIcon = viewToggle.querySelector("i");

        const savedTheme = localStorage.getItem("theme");
        if (savedTheme === "dark") {
            document.documentElement.setAttribute("data-theme", "dark");
            if (themeIcon) {
                themeIcon.classList.remove("fa-moon");
                themeIcon.classList.add("fa-sun");
            }
        }

        const savedView = localStorage.getItem("view") || "list";
        document.documentElement.setAttribute("data-view", savedView);
        if (viewIcon) {
            if (savedView === "grid") {
                viewIcon.classList.remove("fa-th-large");
                viewIcon.classList.add("fa-th-list");
            } else {
                viewIcon.classList.remove("fa-th-list");
                viewIcon.classList.add("fa-th-large");
            }
        }

        viewToggle.addEventListener("click", () => {
            const current = document.documentElement.getAttribute("data-view") || "list";
            const next = current === "grid" ? "list" : "grid";
            document.documentElement.setAttribute("data-view", next);
            localStorage.setItem("view", next);

            if (!viewIcon) {
                return;
            }

            if (next === "grid") {
                viewIcon.classList.remove("fa-th-large");
                viewIcon.classList.add("fa-th-list");
            } else {
                viewIcon.classList.remove("fa-th-list");
                viewIcon.classList.add("fa-th-large");
            }
        });

        themeToggle.addEventListener("click", () => {
            const currentTheme = document.documentElement.getAttribute("data-theme");
            const newTheme = currentTheme === "dark" ? "light" : "dark";

            document.documentElement.setAttribute("data-theme", newTheme);
            localStorage.setItem("theme", newTheme);

            if (!themeIcon) {
                return;
            }

            if (newTheme === "dark") {
                themeIcon.classList.remove("fa-moon");
                themeIcon.classList.add("fa-sun");
            } else {
                themeIcon.classList.remove("fa-sun");
                themeIcon.classList.add("fa-moon");
            }
        });

        if (!savedTheme) {
            const prefersDark = window.matchMedia("(prefers-color-scheme: dark)").matches;
            if (prefersDark) {
                document.documentElement.setAttribute("data-theme", "dark");
                if (themeIcon) {
                    themeIcon.classList.remove("fa-moon");
                    themeIcon.classList.add("fa-sun");
                }
                localStorage.setItem("theme", "dark");
            }
        }
    }

    function unregisterServiceWorker() {
        if (!("serviceWorker" in navigator)) {
            return;
        }

        window.addEventListener("load", () => {
            navigator.serviceWorker
                .getRegistrations()
                .then((registrations) => {
                    registrations.forEach((registration) => {
                        registration.unregister().then(() => {
                            console.log("Service Worker unregistered");
                        });
                    });
                })
                .catch((error) => {
                    console.log("Error unregistering Service Worker:", error);
                });

            // 清理 Service Worker 相关的缓存
            if ("caches" in window) {
                caches.keys().then((cacheNames) => {
                    cacheNames.forEach((cacheName) => {
                        caches.delete(cacheName).then(() => {
                            console.log("Cache deleted:", cacheName);
                        });
                    });
                });
            }
        });
    }

    function registerModalHandlers() {
        const modal = document.getElementById("previewModal");
        if (!modal) {
            return;
        }

        modal.addEventListener("click", (event) => {
            if (event.target === modal) {
                closePreview();
            }
        });

        document.addEventListener("keydown", (event) => {
            if (event.key === "Escape" && !isDialogOpen()) {
                closePreview();
            }
        });
    }

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
                    // 返回上一级目录
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

    function getEntryCheckboxes() {
        return document.querySelectorAll(".entry-checkbox");
    }

    function updateSelectAllState() {
        const master = document.getElementById("selectAll");
        if (!master) {
            return;
        }

        const checkboxes = Array.from(getEntryCheckboxes());
        if (checkboxes.length === 0) {
            master.checked = false;
            master.indeterminate = false;
            return;
        }

        const checkedCount = checkboxes.filter((checkbox) => checkbox.checked).length;

        if (checkedCount === 0) {
            master.checked = false;
            master.indeterminate = false;
        } else if (checkedCount === checkboxes.length) {
            master.checked = true;
            master.indeterminate = false;
        } else {
            master.checked = false;
            master.indeterminate = true;
        }
    }

    function toggleSelectAll(master) {
        const checkboxes = getEntryCheckboxes();
        const desiredState = Boolean(master.checked);

        checkboxes.forEach((checkbox) => {
            checkbox.checked = desiredState;
        });

        master.indeterminate = false;
        updateSelectAllState();
    }

    function attachEntryCheckboxListeners() {
        const master = document.getElementById("selectAll");
        if (master && !master.dataset.listenerAttached) {
            master.addEventListener("change", () => toggleSelectAll(master));
            master.dataset.listenerAttached = "true";
        }

        getEntryCheckboxes().forEach((checkbox) => {
            if (!checkbox.dataset.listenerAttached) {
                checkbox.addEventListener("change", updateSelectAllState);
                checkbox.dataset.listenerAttached = "true";
            }
        });

        updateSelectAllState();
    }

    function attachDownloadButtonListeners() {
        const downloadButtons = document.querySelectorAll("[data-download-key]");
        downloadButtons.forEach((button) => {
            if (!button.dataset.listenerAttached) {
                button.addEventListener("click", () => {
                    const key = button.dataset.downloadKey;
                    const name = button.dataset.downloadName;
                    downloadFile(`/download/${key}`, name);
                });
                button.dataset.listenerAttached = "true";
            }
        });
    }

    function downloadFile(url, filename) {
        if (!url) {
            updateStatus("✗ 无法下载：缺少下载链接", "error");
            return;
        }

        // 对于 /download/ 路径，使用 fetch 以更好地处理大文件和错误
        if (url.startsWith("/download/")) {
            fetch(url)
                .then((response) => {
                    if (!response.ok) {
                        throw new Error(`HTTP error! status: ${response.status}`);
                    }
                    return response.blob();
                })
                .then((blob) => {
                    const link = document.createElement("a");
                    const blobUrl = URL.createObjectURL(blob);
                    link.href = blobUrl;
                    link.download = filename || "file";
                    document.body.appendChild(link);
                    link.click();
                    document.body.removeChild(link);
                    URL.revokeObjectURL(blobUrl);

                    const statusDiv = updateStatus(`✓ 开始下载: ${filename || ""}`, "success");
                    hideStatusLater(statusDiv);
                })
                .catch((error) => {
                    console.error("Download error:", error);
                    updateStatus(`✗ 下载失败: ${error.message}`, "error");
                });
        } else {
            // 对于外部 URL，使用传统方法
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

    async function deleteSelectedEntries() {
        const selected = Array.from(getEntryCheckboxes()).filter((checkbox) => checkbox.checked);

        if (selected.length === 0) {
            const statusDiv = updateStatus("✗ 请先选择要删除的项目", "error");
            hideStatusLater(statusDiv);
            return;
        }

        const directories = selected.filter((checkbox) => checkbox.dataset.type === "dir");
        if (directories.length > 0) {
            const statusDiv = updateStatus("✗ 暂不支持批量删除文件夹，请仅选择文件", "error");
            hideStatusLater(statusDiv);
            return;
        }

        const files = selected.map((checkbox) => checkbox.value);
        const confirmMessage =
            files.length === 1 ? `确定要删除 "${files[0]}" 吗？` : `确定要删除选中的 ${files.length} 个文件吗？`;

        const confirmed = await showConfirm(confirmMessage, {
            title: "批量删除",
            confirmLabel: "删除",
        });

        if (!confirmed) {
            return;
        }

        const deleteButton = document.getElementById("deleteTrigger");
        if (deleteButton) {
            deleteButton.disabled = true;
            deleteButton.classList.add("is-disabled");
        }

        const inProgressStatus = updateStatus(`正在删除 ${files.length} 个文件...`, null);

        const failures = [];
        let successCount = 0;

        for (const filePath of files) {
            // 跳过额外提示和页面刷新，在批量完成后统一处理
            const result = await deleteFile(filePath, {
                skipConfirm: true,
                suppressReload: true,
                suppressStatus: true,
            });

            if (result) {
                successCount += 1;
            } else {
                failures.push(filePath);
            }
        }

        if (deleteButton) {
            deleteButton.disabled = false;
            deleteButton.classList.remove("is-disabled");
        }

        if (inProgressStatus) {
            inProgressStatus.style.display = "none";
        }

        if (failures.length === 0 && successCount > 0) {
            const statusDiv = updateStatus(`✓ 已删除 ${successCount} 个文件`, "success");
            hideStatusLater(statusDiv, 3000);

            setTimeout(() => {
                window.location.reload();
            }, 1500);
            return;
        }

        if (failures.length > 0) {
            const message =
                failures.length === files.length
                    ? "✗ 删除失败，请稍后重试"
                    : `删除部分文件失败：${failures.join(", ")}`;
            const statusDiv = updateStatus(message, "error");
            hideStatusLater(statusDiv, 4000);

            if (successCount > 0) {
                setTimeout(() => {
                    window.location.reload();
                }, 1500);
            }
        }
    }

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

    async function promptCopyOrMove(source, isFolder, operation) {
        const opText = operation === "copy" ? "复制" : "移动";
        const itemText = isFolder ? "文件夹" : "文件";
        const dest = await showPrompt(`请输入目标目录路径：`, {
            title: `${opText}${itemText}`,
            confirmLabel: opText,
        });

        if (dest) {
            // 确保 dest 以 / 结尾
            let normalizedDest = dest;
            if (!normalizedDest.endsWith("/")) {
                normalizedDest += "/";
            }
            // 提取源名称
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

    async function copyItem(source, destination, isFolder) {
        updateStatus(`正在复制...`, null);
        await performOperation("/copy", "复制", { source, destination, is_folder: isFolder });
    }

    async function moveItem(source, destination, isFolder) {
        updateStatus(`正在移动...`, null);
        await performOperation("/move", "移动", { source, destination, is_folder: isFolder });
    }

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

    function getFileType(filename) {
        const extension = filename.toLowerCase().split(".").pop();
        const imageExtensions = ["jpg", "jpeg", "png", "gif", "bmp", "webp", "svg", "ico"];
        const videoExtensions = ["mp4", "webm", "ogg", "mov", "avi", "mkv", "m4v"];

        if (imageExtensions.includes(extension)) {
            return "image";
        }
        if (videoExtensions.includes(extension)) {
            return "video";
        }
        return "unknown";
    }

    function openPreview(url, filename) {
        const modal = document.getElementById("previewModal");
        const container = document.getElementById("previewContainer");
        const info = document.getElementById("previewInfo");

        if (!modal || !container || !info) {
            window.open(url, "_blank");
            return;
        }

        const fileType = getFileType(filename);

        if (fileType === "unknown") {
            window.open(url, "_blank");
            return;
        }

        container.innerHTML = '<div class="preview-loading">加载中...</div>';
        info.textContent = filename;
        modal.classList.add("show");
        document.body.style.overflow = "hidden";

        setTimeout(() => {
            if (fileType === "image") {
                const image = document.createElement("img");
                image.className = "preview-content";
                image.src = url;
                image.alt = filename;

                image.onload = () => {
                    container.innerHTML = "";
                    container.appendChild(image);
                };

                image.onerror = () => {
                    container.innerHTML = '<div class="preview-error">图片加载失败</div>';
                };
            } else if (fileType === "video") {
                const video = document.createElement("video");
                video.className = "preview-content";
                video.src = url;
                video.controls = true;
                video.autoplay = false;

                video.onloadedmetadata = () => {
                    container.innerHTML = "";
                    container.appendChild(video);
                };

                video.onerror = () => {
                    container.innerHTML = '<div class="preview-error">视频加载失败</div>';
                };
            }
        }, 100);
    }

    function closePreview() {
        const modal = document.getElementById("previewModal");
        const container = document.getElementById("previewContainer");

        if (!modal || !container) {
            return;
        }

        modal.classList.remove("show");
        document.body.style.overflow = "";

        setTimeout(() => {
            container.innerHTML = "";
        }, 300);
    }

    function downloadPreview() {
        const container = document.getElementById("previewContainer");
        const info = document.getElementById("previewInfo");

        if (!container || !info) {
            return;
        }

        const media = container.querySelector(".preview-content");
        if (media && media.src) {
            downloadFile(media.src, info.textContent);
        }
    }

    document.addEventListener("DOMContentLoaded", () => {
        initDialog();
        initThemeAndView();
        registerModalHandlers();
        unregisterServiceWorker();
        attachEntryCheckboxListeners();
        attachDownloadButtonListeners();
    });

    window.uploadFiles = uploadFiles;
    window.promptDelete = promptDelete;
    window.deleteFile = deleteFile;
    window.deleteSelectedEntries = deleteSelectedEntries;
    window.toggleSelectAll = (master) => toggleSelectAll(master);
    window.downloadFile = downloadFile;
    window.openPreview = openPreview;
    window.closePreview = closePreview;
    window.downloadPreview = downloadPreview;
    window.promptRename = promptRename;
    window.deleteFolder = deleteFolder;
    window.promptCopyOrMove = promptCopyOrMove;

    async function promptCreateFolder() {
        const currentPrefix = document.body.dataset.currentPrefix || "";
        const folderName = await showPrompt("请输入新文件夹的名称：", {
            title: "新建文件夹",
            confirmLabel: "创建",
        });

        if (folderName) {
            const path = currentPrefix + folderName;
            await createFolder(path);
        }
    }

    async function createFolder(path) {
        updateStatus(`正在创建文件夹: ${path}...`, null);

        try {
            const response = await fetch(`/create_folder`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({ path: path }),
            });

            const result = await response.json();

            if (result.success) {
                const statusDiv = updateStatus("✓ 文件夹创建成功！", "success");
                hideStatusLater(statusDiv);

                setTimeout(() => {
                    window.location.reload();
                }, 1500);
            } else {
                updateStatus(`✗ 创建失败: ${result.error}`, "error");
            }
        } catch (error) {
            updateStatus(`✗ 创建失败: ${error.message}`, "error");
        }
    }
    window.promptCreateFolder = promptCreateFolder;
})();
