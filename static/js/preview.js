/**
 * 文件预览功能
 * 包括图片、视频、音频、PDF、文本等预览
 */

/**
 * 获取文件类型
 * @param {string} filename - 文件名
 * @returns {string} 文件类型
 */
function getFileType(filename) {
    const extension = filename.toLowerCase().split(".").pop();
    const imageExtensions = ["jpg", "jpeg", "png", "gif", "bmp", "webp", "svg", "ico"];
    const videoExtensions = ["mp4", "webm", "ogg", "mov", "avi", "mkv", "m4v"];
    const audioExtensions = ["mp3", "wav", "ogg", "m4a", "aac", "flac", "opus", "weba"];
    const pdfExtensions = ["pdf"];
    const textExtensions = [
        "txt",
        "log",
        "md",
        "json",
        "xml",
        "csv",
        "js",
        "css",
        "html",
        "py",
        "java",
        "c",
        "cpp",
        "h",
        "hpp",
        "sh",
        "bat",
        "yaml",
        "yml",
        "toml",
        "ini",
        "conf",
    ];

    if (imageExtensions.includes(extension)) {
        return "image";
    }
    if (videoExtensions.includes(extension)) {
        return "video";
    }
    if (audioExtensions.includes(extension)) {
        return "audio";
    }
    if (pdfExtensions.includes(extension)) {
        return "pdf";
    }
    if (textExtensions.includes(extension)) {
        return "text";
    }
    return "unsupported";
}

/**
 * 关闭预览
 */
function closePreview() {
    const modal = document.getElementById("previewModal");
    if (modal) {
        modal.classList.remove("show");
        document.body.style.overflow = "";
    }
}

/**
 * 打开预览
 * @param {string} url - 文件 URL
 * @param {string} filename - 文件名
 */
function openPreview(url, filename) {
    const modal = document.getElementById("previewModal");
    const container = document.getElementById("previewContainer");
    const info = document.getElementById("previewInfo");

    if (!modal || !container || !info) {
        window.open(url, "_blank");
        return;
    }

    const fileType = getFileType(filename);

    // 对于不支持预览的文件类型，显示提示信息
    if (fileType === "unsupported") {
        container.innerHTML = `
            <div class="preview-unsupported">
                <i class="fas fa-file-alt" style="font-size: 64px; color: var(--text-secondary); margin-bottom: 16px;"></i>
                <p style="font-size: 18px; margin-bottom: 8px;">该文件不支持预览</p>
                <p style="color: var(--text-secondary); margin-bottom: 24px;">文件名: ${filename}</p>
                <div style="display: flex; gap: 12px; justify-content: center;">
                    <button class="action-link" onclick="downloadFile('${url}', '${filename}'); closePreview();" style="padding: 8px 16px;">
                        <i class="fas fa-download"></i> 下载文件
                    </button>
                    <button class="action-link" onclick="window.open('${url}', '_blank'); closePreview();" style="padding: 8px 16px;">
                        <i class="fas fa-external-link-alt"></i> 新窗口打开
                    </button>
                </div>
            </div>
        `;
        info.textContent = filename;
        modal.classList.add("show");
        document.body.style.overflow = "hidden";
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
            image.style.maxWidth = "100%";
            image.style.maxHeight = "100%";
            image.onerror = () => {
                container.innerHTML = '<div class="preview-error">加载失败</div>';
            };
            container.innerHTML = "";
            container.appendChild(image);
        } else if (fileType === "video") {
            const video = document.createElement("video");
            video.className = "preview-content";
            video.controls = true;
            video.style.maxWidth = "100%";
            video.style.maxHeight = "100%";
            const source = document.createElement("source");
            source.src = url;
            source.type = `video/${url.split(".").pop()}`;
            video.appendChild(source);
            container.innerHTML = "";
            container.appendChild(video);
        } else if (fileType === "audio") {
            const audio = document.createElement("audio");
            audio.className = "preview-content";
            audio.controls = true;
            audio.style.width = "100%";
            const source = document.createElement("source");
            source.src = url;
            source.type = `audio/${url.split(".").pop()}`;
            audio.appendChild(source);
            container.innerHTML = "";
            container.appendChild(audio);
        } else if (fileType === "pdf") {
            container.innerHTML = `
                <iframe
                    src="${url}#toolbar=0"
                    style="width: 100%; height: 100%; border: none;"
                    title="${filename}"
                ></iframe>
            `;
        } else if (fileType === "text") {
            fetch(url)
                .then((response) => response.text())
                .then((text) => {
                    const pre = document.createElement("pre");
                    pre.className = "preview-text";
                    pre.textContent = text;
                    pre.style.margin = "0";
                    pre.style.padding = "16px";
                    pre.style.overflow = "auto";
                    pre.style.whiteSpace = "pre-wrap";
                    pre.style.wordWrap = "break-word";
                    container.innerHTML = "";
                    container.appendChild(pre);
                })
                .catch(() => {
                    container.innerHTML = '<div class="preview-error">加载失败</div>';
                });
        }
    }, 100);
}

/**
 * 导出到全局作用域
 */
window.PreviewUtils = {
    getFileType,
    closePreview,
    openPreview,
};
