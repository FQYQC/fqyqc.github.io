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

### 目录跳转与图片懒加载

主题的 `plugin/img.html` 用 lazysizes 懒加载图片，远程图片没有宽高，加载前只占 60px 的占位图。点击目录或直接打开带 `#标题` 的链接后，目标上方的照片陆续加载，会把标题向下推；没有 CSS 滚动锚定的浏览器（Safari）因此停在错误位置，长游记里可偏离数千像素。主题的 `scroll-margin-top`（顶栏高度 + 0.5rem）已经负责避开固定顶栏，这里不改。

`assets/js/stable-anchor.js` 通过 `hugo.toml` 的 `params.page.library.js` 加载（LoveIt 从 `params.page` 读取页面库，不读 `params.library`）。脚本在同页锚点点击或首次打开带 hash 的 URL 时“钉住”目标：页面高度变化（`ResizeObserver`，在绘制前执行）或滚动停下时，把目标重新对齐到它的 `scroll-margin-top`。浏览器自身的平滑滚动保持不变；滚动进行中发生的变化在滚动停下后修正。读者滚轮、触摸、点击、按键，或在没有布局变化时自行移动了位置，都会立即解除钉住；最长钉住 20 秒。刷新和前进/后退不处理，以保留浏览器恢复的阅读位置。

验证：在无滚动锚定（模拟 Safari）且图片延迟 1.5 至 5 秒的条件下，修复前目标最终偏离 3000 至 12000px，修复后稳定在 72px（顶栏 64px 下方）。若以后为图片补上宽高或 `aspect-ratio`，可以减少布局偏移，但本脚本仍可保留作为兜底。

### 友链

友链数据保存在 `data/friends.toml`，每个 `[[friends]]` 条目包含必填的 `name`、`url`，以及可选的 `icon`、`iconFill` 和双语 `description`。图标下载到 `static/images/friends/` 后随站点发布，页面不直接请求对方服务器；没有图标时显示名字首字母。`layouts/shortcodes/friends.html` 是站点新增的 shortcode，不覆盖主题文件；`content/friends.en.md` 与 `content/friends.zh-cn.md` 调用它，分别生成 `/friends/` 和 `/zh-cn/friends/`。顶部菜单和各语言页脚 `params.footer.custom` 只链接到对应语言的友链页。新增朋友时只修改数据文件。

`scripts/check_friends.py` 由 `scripts/check.sh` 调用，校验数据字段、URL 协议、重复项和图标文件，并确认两种语言的友链页都包含全部链接。

### 视觉样式

站点外观采用极简黑白方向：几乎不用颜色，靠字号、字重和留白建立层级，照片是唯一的色彩来源。样式在主题之上用两份文件定制，均不修改主题子模块：

- `assets/css/_override.scss`：覆盖主题同名占位文件，重设颜色、字体等 SCSS 变量。主题在 `_variables` 之后导入它，直接赋值即可。
- `assets/css/_custom.scss`：主题最后导入的自定义样式，负责排版、首页介绍、封面位、文章摘要、页面标题和友链卡片。

Inter 与 Noto Sans SC 通过 `hugo.toml` 中 `params.library.css.googleFonts` 加载。主题的标题入场动画在 `_custom.scss` 中被关闭。

### 首页精选

精选由文章开头的 `featured` 标记决定，中英文任一版本加了即可：`featured: true` 按发布日期从新到旧；`featured: 15` 这类数字按从小到大排在所有 `true` 前面，建议用 10、20、30 留间隔，插入新文章时不必改其他文章。`layouts/partials/home/featured-pages.html` 收集并排序当前语言的精选文章，`layouts/partials/home/featured.html` 渲染卡片，`layouts/index.html` 把它们从下方列表中排除。

封面由 `layouts/partials/home/featured-cover.html` 解析，两种来源：优先使用本地 `assets/images/covers/<文章文件名>.jpg`（或 `.png`、`.webp`，文件名不带语言后缀）；否则读取文章开头的 `cover`，可写正文中已有的图片路径（经 `data/assets_mapping.json` 映射到图床）或完整 URL，构建时用 `resources.GetRemote` 下载。两种来源都会被缩放到最宽 1400px 并转为 JPEG，同时用 `.Colors` 取调色板，从中选色度最高的颜色（而不是面积最大的，避免深色地面或阴天天空胜出），只保留色相和有上限的饱和度，亮度固定为 93%（浅色）和 14%（深色），生成主卡底色；整体偏灰的图片保持中性灰。远程下载失败时用 `try` 捕获，该文章退回文字卡，不影响构建。正文照片仍走图床：本地原图库约 886MB，不适合进入仓库；封面数量少、压缩后体积小，两种来源都可接受。

[docs/featured.md](featured.md) 由 `scripts/sync_featured.py` 根据标记自动生成，列出当前精选的顺序、标记值和有无封面，只作参考；`scripts/check.sh` 每次运行都会刷新它，模板不读取这个文件。

布局：第一篇是带浅灰底的主卡，其余每行三张（六列网格，每张占两列），最后一行只剩两张时各占三列，只剩一张时占满整行并改为左图右文。排法由首页内容宽度的容器查询决定：不小于 640px 时主卡左图右文、与下方三列共用列线；更窄时全部单列，小卡改为左图右文横条。主题按屏幕比例设定内容宽度，在 960px 附近会出现屏幕变宽、内容反而变窄的情况，因此首页和归档类页面（文章列表、分类、标签）改为固定上限宽度（约 864px），只覆盖左右内边距；文章页仍沿用主题宽度以容纳右侧目录。分类总览页由主题的居中 flex 改为顶部对齐的两列网格。

### 文章页样式

目录去掉每项前的竖线，当前阅读位置用墨色加粗，中等宽度下的折叠目录改为细边框。`render-image.html` 给图注写了行内 `color: #555`，深色模式下几乎看不见，`_custom.scss` 用 `!important` 改为次要文字色。

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
