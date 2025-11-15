/**
 * 下载按钮事件处理
 */

/**
 * 绑定下载按钮监听器
 */
function attachDownloadButtonListeners() {
    const downloadButtons = document.querySelectorAll("[data-download-key]");
    downloadButtons.forEach((button) => {
        if (!button.dataset.listenerAttached) {
            button.addEventListener("click", () => {
                const key = button.dataset.downloadKey;
                const name = button.dataset.downloadName;
                // 对路径分段编码，保留路径分隔符，避免 # ? 等字符破坏 URL
                const encoded = key
                    .split("/")
                    .map((seg) => encodeURIComponent(seg))
                    .join("/");
                downloadFile(`/download/${encoded}`, name);
            });
            button.dataset.listenerAttached = "true";
        }
    });
}

/**
 * 导出到全局作用域
 */
window.DownloadUtils = {
    attachDownloadButtonListeners,
};
