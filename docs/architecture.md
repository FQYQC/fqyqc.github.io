# Architecture

## 构建数据流

```text
hugo.toml + content/ + data/
              |
              v
      root layouts/assets  ---- overrides ----> themes/LoveIt
              |
              v
          Hugo extended
              |
              v
     public/ (generated artifact)
              |
              v
          GitHub Pages
```

Hugo 读取根配置和双语内容。根目录中的模板与资源优先于主题同路径文件，因此站点定制不需要修改主题子模块。GitHub Actions 使用 `.hugo-version` 固定工具版本并以 production 模式构建。

## 关键设计边界

### 内容

- `content/posts/` 保存文章正文。功能开发默认把它视为只读输入。
- `content/about.*.md` 和其他 section 是普通 Hugo 内容，可按明确需求修改。
- front matter 决定语言、日期、分类、标签、草稿和隐藏状态。变更可能影响 URL、列表页、RSS 和搜索索引。

### 图片

文章中的图片目标先经过 `layouts/_default/_markup/render-image.html`。该 render hook 查询 `data/assets_mapping.json`；有映射时使用远程 URL，没有映射时保留原始目标。被忽略的 `assets/local-assets/` 是本地素材来源，不属于可复现部署输入。

### 友链

友链数据保存在 `data/friends.toml`，每个 `[[friends]]` 条目包含必填的 `name`、`url`，以及可选的 `icon`、`iconFill` 和双语 `description`。图标下载到 `static/images/friends/` 后随站点发布，页面不直接请求对方服务器；没有图标时显示名字首字母。`layouts/shortcodes/friends.html` 是站点新增的 shortcode，不覆盖主题文件；`content/friends.en.md` 与 `content/friends.zh-cn.md` 调用它，分别生成 `/friends/` 和 `/zh-cn/friends/`。顶部菜单和各语言页脚 `params.footer.custom` 只链接到对应语言的友链页。新增朋友时只修改数据文件。

`scripts/check_friends.py` 由 `scripts/check.sh` 调用，校验数据字段、URL 协议、重复项和图标文件，并确认两种语言的友链页都包含全部链接。

### 视觉样式

站点外观采用极简黑白方向：几乎不用颜色，靠字号、字重和留白建立层级，照片是唯一的色彩来源。样式在主题之上用两份文件定制，均不修改主题子模块：

- `assets/css/_override.scss`：覆盖主题同名占位文件，重设颜色、字体等 SCSS 变量。主题在 `_variables` 之后导入它，直接赋值即可。
- `assets/css/_custom.scss`：主题最后导入的自定义样式，负责排版、首页介绍、封面位、文章摘要、页面标题和友链卡片。

Inter 与 Noto Sans SC 通过 `hugo.toml` 中 `params.library.css.googleFonts` 加载。主题的标题入场动画在 `_custom.scss` 中被关闭。

### 首页封面位

`data/featured.toml` 按顺序列出要在首页个人介绍下方突出的文章（`page` 为不带语言后缀的路径，`image` 可选）。`layouts/partials/home/featured.html` 渲染这些卡片：有图时显示图片卡，无图时显示纯文字封面；某种语言缺少该文章时自动跳过。封面图需压缩后放在 `static/images/covers/`，不引用外部图床；图片路径不存在时构建失败。布局随数量变化：1 篇单独显示，2 篇左右并排，3 篇及以上时第一篇做主卡、其余每行三张。排法由首页内容宽度的容器查询决定：不小于 640px 时主卡左图右文、小卡三列；更窄时全部单列，小卡改为左图右文横条。主题按屏幕比例设定内容宽度，在 960px 附近会出现屏幕变宽、内容反而变窄的情况，因此首页和归档类页面（文章列表、分类、标签）改为固定上限宽度（约 864px），只覆盖左右内边距，上内边距仍由主题为固定顶栏预留；文章页仍沿用主题宽度以容纳右侧目录。主卡与下方三列共用同一套列线：图片占两列、文字占一列。同一行小卡片等高，“分类 · 日期”贴底对齐。分类总览页由主题的居中 flex 改为顶部对齐的两列网格。被选入封面位的文章不会在下方列表中重复出现。

### 主题和模板覆盖

`themes/LoveIt` 固定在 `.gitmodules` 与 Git index 记录的 commit。根目录当前有四类覆盖：

- `layouts/_default/summary.html`：优先用 front matter 的 `abstract` 生成列表摘要。
- `layouts/partials/assets.html`：为主题的页面配置补齐默认值。
- `layouts/_default/_markup/render-image.html`：实现图片 URL 映射和统一图注。
- `layouts/index.html`：在个人介绍后渲染首页封面位，并从文章列表中排除封面位文章。

`summary.html`、`assets.html` 和 `index.html` 基于主题模板的完整副本。更新主题后必须与新的同路径文件进行三方比较，避免遗漏主题修复。

### 生成物

`public/`、`resources/_gen/`、`resources/_cache/` 和 Hugo lock 文件都能重新生成，并由 `.gitignore` 排除。验证脚本将输出写入安全的临时目录。

## 扩展新功能

1. 优先通过 Hugo 配置、站点级 partial/render hook 或 `assets/` 实现。
2. 若新增内容参数，给出默认行为，确保旧文章无需批量迁移也能继续构建。
3. 若覆盖新的主题模板，在文件顶部记录主题 commit、覆盖原因和本地差异。
4. 为新功能增加可自动执行的检查，并从 `scripts/check.sh` 或独立 CI job 调用。
5. 完整生产构建成功后，再人工检查受影响的英文与中文页面。

## 安全模型

这是公开静态站点。任何进入部署输入的内容都应按可公开读取处理。`hidden`、草稿状态、不可猜测 URL、菜单缺失或搜索引擎规则都不能替代身份认证和授权。
