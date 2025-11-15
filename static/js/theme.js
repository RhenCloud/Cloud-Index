/**
 * 主题和视图切换功能
 * 包括深色/浅色主题切换、列表/网格视图切换
 */

/**
 * 初始化主题和视图
 */
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

/**
 * 导出到全局作用域
 */
window.ThemeUtils = {
    initThemeAndView,
};
