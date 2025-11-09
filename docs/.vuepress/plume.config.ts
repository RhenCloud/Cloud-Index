/**
 * 查看以下文档了解主题配置
 * - @see https://theme-plume.vuejs.press/config/intro/ 配置说明
 * - @see https://theme-plume.vuejs.press/config/theme/ 主题配置项
 *
 * 请注意，对此文件的修改不会重启 vuepress 服务，而是通过热更新的方式生效
 * 但同时部分配置项不支持热更新，请查看文档说明
 * 对于不支持热更新的配置项，请在 `.vuepress/config.ts` 文件中配置
 *
 * 特别的，请不要在两个配置文件中重复配置相同的项，当前文件的配置项会覆盖 `.vuepress/config.ts` 文件中的配置
 */

import { defineThemeConfig } from "vuepress-theme-plume";
import navbar from "./navbar";
import collections from "./collections";

/**
 * @see https://theme-plume.vuejs.press/config/basic/
 */
export default defineThemeConfig({
    logo: "https://theme-plume.vuejs.press/plume.png",

    appearance: true, // 配置 深色模式

    social: [
        { icon: "github", link: "https://github.com/RhenCloud/Cloud-Index" }, // TODO: 替换为实际仓库 URL
    ],
    // navbarSocialInclude: ['github'], // 允许显示在导航栏的 social 社交链接
    aside: true, // 页内侧边栏， 默认显示在右侧
    outline: [2, 3], // 页内大纲， 默认显示 h2, h3

    /**
     * 文章版权信息
     * @see https://theme-plume.vuejs.press/guide/features/copyright/
     */
    // copyright: true,

    // prevPage: true,   // 是否启用上一页链接
    // nextPage: true,   // 是否启用下一页链接
    // createTime: true, // 是否显示文章创建时间

    /* 站点页脚 */
    // footer: {
    //   message: 'Power by <a target="_blank" href="https://v2.vuepress.vuejs.org/">VuePress</a> & <a target="_blank" href="https://theme-plume.vuejs.press">vuepress-theme-plume</a>',
    //   copyright: '',
    // },

    /**
     * @see https://theme-plume.vuejs.press/config/basic/#profile
     */
    profile: {
        avatar: "https://theme-plume.vuejs.press/plume.png",
        name: "Cloud Index Docs",
        description: "一个支持多种云存储后端的文件管理、索引和浏览服务",
        // circle: true,
        // location: '',
        // organization: '',
    },

    navbar,
    // collections,

    /**
     * 侧边栏配置
     * @see https://theme-plume.vuejs.press/config/navigation/#sidebar
     */
    sidebar: {
        "/guide/": [
            {
                text: "📖 使用指南",
                collapsed: false,
                items: [
                    { text: "项目介绍", link: "/guide/introduction" },
                    { text: "快速开始", link: "/guide/quickstart" },
                    {
                        text: "部署",
                        collapsed: false,
                        items: [
                            { text: "部署指南", link: "/guide/deployment/overview" },
                            { text: "服务器部署", link: "/guide/deployment/server" },
                            // { text: "Docker 部署", link: "/guide/deployment/docker" },
                            { text: "Vercel 部署", link: "/guide/deployment/vercel" },
                        ],
                    },
                    {
                        text: "配置",
                        collapsed: false,
                        items: [
                            { text: "基础配置", link: "/guide/configuration/configuration" },
                            { text: "环境配置", link: "/guide/configuration/environment" },
                        ],
                    },
                ],
            },
        ],
        "/storage/": [
            {
                text: "☁️ 存储后端",
                collapsed: false,
                items: [
                    { text: "后端概览", link: "/storage/overview" },
                    { text: "Cloudflare R2", link: "/storage/r2" },
                    { text: "Amazon S3", link: "/storage/s3" },
                    { text: "GitHub", link: "/storage/github" },
                ],
            },
        ],
    },

    /**
     * 公告板
     * @see https://theme-plume.vuejs.press/guide/features/bulletin/
     */
    // bulletin: {
    //   layout: 'top-right',
    //   contentType: 'markdown',
    //   title: '公告板标题',
    //   content: '公告板内容',
    // },

    /* 过渡动画 @see https://theme-plume.vuejs.press/config/basic/#transition */
    // transition: {
    //   page: true,        // 启用 页面间跳转过渡动画
    //   postList: true,    // 启用 博客文章列表过渡动画
    //   appearance: 'fade',  // 启用 深色模式切换过渡动画, 或配置过渡动画类型
    // },
});
