/**
 * 对话框（Dialog）相关功能
 * 包括确认、输入、提示等对话框
 */

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

/**
 * 检查对话框是否打开
 * @returns {boolean}
 */
function isDialogOpen() {
    return Boolean(dialogState.container && !dialogState.container.hasAttribute("hidden"));
}

/**
 * 关闭对话框
 * @param {boolean} confirmed - 是否确认
 */
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

/**
 * 打开对话框
 * @param {object} options - 对话框选项
 * @returns {Promise}
 */
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

/**
 * 初始化对话框
 */
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

/**
 * 显示确认对话框
 * @param {string} message - 消息
 * @param {object} options - 选项
 * @returns {Promise<boolean>}
 */
function showConfirm(message, options = {}) {
    return openDialog({
        title: options.title || "确认操作",
        message,
        confirmLabel: options.confirmLabel || "确定",
        cancelLabel: options.cancelLabel || "取消",
        hideCancel: options.hideCancel || false,
    }).then((result) => Boolean(result.confirmed));
}

/**
 * 显示输入对话框
 * @param {string} message - 消息
 * @param {object} options - 选项
 * @returns {Promise<string|null>}
 */
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

/**
 * 导出到全局作用域
 */
window.DialogUtils = {
    isDialogOpen,
    closeDialog,
    openDialog,
    initDialog,
    showConfirm,
    showPrompt,
};
