/**
 * Service Worker 和其他工具函数
 */

/**
 * 注销 Service Worker
 */
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

/**
 * 注册模态框处理程序
 */
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

/**
 * 导出到全局作用域
 */
window.UtilityFuncs = {
    unregisterServiceWorker,
    registerModalHandlers,
};
