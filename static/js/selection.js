/**
 * 文件选择和批量操作相关功能
 */

/**
 * 获取所有条目复选框
 * @returns {NodeListOf<Element>}
 */
function getEntryCheckboxes() {
    return document.querySelectorAll(".entry-checkbox");
}

/**
 * 更新全选状态
 */
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

/**
 * 切换全选
 * @param {HTMLInputElement} master - 主复选框
 */
function toggleSelectAll(master) {
    const checkboxes = getEntryCheckboxes();
    const desiredState = Boolean(master.checked);

    checkboxes.forEach((checkbox) => {
        checkbox.checked = desiredState;
    });

    master.indeterminate = false;
    updateSelectAllState();
}

/**
 * 绑定复选框监听器
 */
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

/**
 * 删除选定的条目
 */
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
            failures.length === files.length ? "✗ 删除失败，请稍后重试" : `删除部分文件失败：${failures.join(", ")}`;
        const statusDiv = updateStatus(message, "error");
        hideStatusLater(statusDiv, 4000);

        if (successCount > 0) {
            setTimeout(() => {
                window.location.reload();
            }, 1500);
        }
    }
}

/**
 * 导出到全局作用域
 */
window.SelectionUtils = {
    getEntryCheckboxes,
    updateSelectAllState,
    toggleSelectAll,
    attachEntryCheckboxListeners,
    deleteSelectedEntries,
};
