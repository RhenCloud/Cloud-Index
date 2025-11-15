/**
 * UI 相关的全局工具函数
 * 包括状态提示、对话框等
 */

/**
 * 更新状态消息
 * @param {string} message - 消息内容
 * @param {string} state - 状态类型 ('success', 'error', 'warning', 或空)
 * @returns {HTMLElement|null} 状态元素
 */
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

/**
 * 延迟隐藏状态消息
 * @param {HTMLElement} statusDiv - 状态元素
 * @param {number} delay - 延迟时间（毫秒）
 */
function hideStatusLater(statusDiv, delay = 2000) {
    if (!statusDiv) {
        return;
    }
    setTimeout(() => {
        statusDiv.style.display = "none";
    }, delay);
}

/**
 * 导出到全局作用域
 */
window.UIUtils = {
    updateStatus,
    hideStatusLater,
};
