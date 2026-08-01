# Yilue's Blog

这是 [ylqian.com](https://ylqian.com/) 的 Hugo 源码仓库。站点使用 LoveIt 主题子模块，提供英文和简体中文内容，并通过 GitHub Actions 部署到 GitHub Pages。

## 本地开始

需要 Git，以及 `.hugo-version` 中指定版本的 Hugo extended。

```bash
git clone --recurse-submodules https://github.com/FQYQC/fqyqc.github.io.git
cd fqyqc.github.io
./scripts/check.sh
hugo server --buildDrafts --disableFastRender
```

如果已经克隆但主题目录为空：

```bash
git submodule update --init --recursive
```

## 验证与构建

```bash
# 在临时目录完成生产构建，不污染 public/
./scripts/check.sh

# 生成生产站点到 public/
./scripts/build.sh
```

脚本会检查 Hugo 版本、extended 版本和主题子模块，再执行启用垃圾回收、压缩和 warning 失败策略的生产构建。

## 目录说明

| 路径 | 用途 |
| --- | --- |
| `content/` | 页面与文章源文件 |
| `assets/` | Hugo Pipes 处理的样式和本地素材 |
| `data/assets_mapping.json` | Markdown 图片路径到远程资源的映射 |
| `layouts/` | 对 LoveIt 主题的站点级模板覆盖 |
| `static/` | 原样复制到站点根目录的静态文件 |
| `themes/LoveIt` | 固定 commit 的 Git 子模块 |
| `scripts/` | 本地和 CI 共用的构建检查入口 |
| `public/`, `resources/` | 可重新生成且不提交的构建产物 |

详细的数据流、模板覆盖和扩展位置见 [docs/architecture.md](docs/architecture.md)。Agent 在修改前应先阅读 [AGENTS.md](AGENTS.md)。

## 内容与隐私

基础设施改动默认不编辑 `content/posts/**`。静态站点没有服务端权限控制：隐藏页面、未加入菜单的页面和 `robots.txt` 都不能保护秘密信息。

## 自动化

- Pull Request 会运行隔离的完整生产构建。
- 推送到 `main` 后，GitHub Pages 工作流构建并部署站点。
- Dependabot 每月检查 GitHub Actions 的版本更新。
