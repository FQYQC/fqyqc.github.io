# AGENTS.md

本文件是所有自动化 Agent 在本仓库工作的根级约定。若子目录以后出现更具体的 `AGENTS.md`，以离目标文件最近的约定为准。

## 项目目标

这是一个由 Hugo 生成并部署到 GitHub Pages 的双语个人站点。维护工作的首要目标是保持公开 URL、文章内容和构建结果稳定，同时让配置、主题覆盖和自动化能够安全演进。

## 开始工作前

1. 运行 `git status --short`，把已有改动视为用户工作，不覆盖、不清理。
2. 确认主题子模块状态：`git submodule status --recursive`。
3. 阅读 [README.md](README.md) 和 [docs/architecture.md](docs/architecture.md)。
4. 修改前运行 `./scripts/check.sh` 建立构建基线；修改后再次运行。

## 不可破坏的边界

- 除非任务明确要求编辑文章，否则 `content/posts/**` 是只读区域。基础设施、布局或样式任务不得顺手格式化 front matter 或正文。
- `content/thecove/**` 可能包含未公开草稿或仅通过直接链接访问的页面。除非任务明确涉及它们，否则不要读取、引用或修改其内容。
- `hidden: true`、不出现在菜单中或无法被搜索到都不构成访问控制。不要把秘密、凭据或真正私密的数据提交到静态站点源码。
- `public/`、`resources/_gen/`、`resources/_cache/` 和 `.hugo_build.lock` 是生成物，不应手工修改或提交。
- `assets/local-assets/` 是被忽略的本地素材库，可能很大。不要删除、移动或批量处理它，除非任务明确要求。
- `themes/LoveIt` 是 Git 子模块。站点级改动优先放在根目录 `layouts/`、`assets/`、`static/` 或配置中，不直接修改子模块工作树。

## 常用命令

```bash
git submodule update --init --recursive
./scripts/check.sh
./scripts/build.sh
hugo server --buildDrafts --disableFastRender
```

Hugo 的唯一期望版本记录在 `.hugo-version`。需要升级时，同时验证本地构建、GitHub Actions 构建和主题兼容性。

## 修改约定

- 配置变更必须保留双语站点行为，并检查菜单、永久链接、标签、分类、RSS、站点地图和搜索配置。
- 根目录 `layouts/` 中的文件会覆盖主题同路径模板。修改前先和 `themes/LoveIt/layouts/` 中的上游版本对比；升级主题时逐个复核这些覆盖。
- 图片映射由 `data/assets_mapping.json` 提供，Markdown 图片由 `layouts/_default/_markup/render-image.html` 解析。不要假定本地素材会随仓库或部署产物一起存在。
- 优先做小而可验证的改动。避免无关格式化、全仓库机械重写和未经验证的依赖大版本升级。
- 新功能应同时补充对应的架构说明、验证步骤以及必要的 CI 检查。

## 完成标准

- `./scripts/check.sh` 成功。
- `git diff --check` 没有由本次改动引入的空白错误。
- `git status --short` 中用户原有改动保持不变。
- 没有意外修改 `content/posts/**`、主题子模块或生成目录。
- 交付说明列出改动、验证结果、已知风险和后续建议。
