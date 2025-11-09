/**
 * @see https://theme-plume.vuejs.press/config/navigation/ 查看文档了解配置详情
 *
 * Navbar 配置文件，它在 `.vuepress/plume.config.ts` 中被导入。
 */

import { defineNavbarConfig } from "vuepress-theme-plume";

export default defineNavbarConfig([
    { text: "首页", link: "/" },
    {
        text: "📖 文档",
        items: [
            { text: "项目介绍", link: "/guide/introduction" },
            { text: "快速开始", link: "/guide/quickstart" },
            { text: "部署指南", link: "/guide/deployment/overview" },
            { text: "配置指南", link: "/guide/configuration/configuration" },
        ],
    },
    {
        text: "☁️ 存储后端",
        items: [
            { text: "后端概览", link: "/storage/overview" },
            { text: "Cloudflare R2", link: "/storage/r2" },
            { text: "Amazon S3", link: "/storage/s3" },
            { text: "GitHub", link: "/storage/github" },
        ],
    },
]);
