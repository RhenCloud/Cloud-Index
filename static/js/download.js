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
                downloadFile(`/download/${key}`, name);
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
