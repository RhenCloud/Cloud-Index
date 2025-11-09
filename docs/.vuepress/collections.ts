import { defineUserConfig } from "vuepress";
import { plumeTheme } from "vuepress-theme-plume";

export default defineUserConfig({
    theme: plumeTheme({
        collections: [
            {
                type: "doc",
                dir: "guide",
                linkPrefix: "/guide/",
                title: "TypeScript 笔记",
                sidebar: ["basic", "types"],
            },
        ],
    }),
});
