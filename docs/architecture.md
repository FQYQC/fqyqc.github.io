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

render hook 内联了主题 `plugin/img.html` 的链接分支（懒加载与 lightgallery），但不输出 `data-srcset`：主题把同一个文件同时标为 1.5x 和 2x，高像素密度屏幕上浏览器会按图片像素宽度的一半显示，较窄的图片因此比正文窄。去掉后图片按 `max-width: 100%` 撑满正文。图片的 `alt` 使用图注文字而不是 URL。

### 目录跳转与图片懒加载

主题的 `plugin/img.html` 用 lazysizes 懒加载图片，远程图片没有宽高，加载前只占 60px 的占位图。点击目录或直接打开带 `#标题` 的链接后，目标上方的照片陆续加载，会把标题向下推；没有 CSS 滚动锚定的浏览器（Safari）因此停在错误位置，长游记里可偏离数千像素。主题的 `scroll-margin-top`（顶栏高度 + 0.5rem）已经负责避开固定顶栏，这里不改。

`assets/js/stable-anchor.js` 通过 `hugo.toml` 的 `params.page.library.js` 加载（LoveIt 从 `params.page` 读取页面库，不读 `params.library`）。脚本在同页锚点点击或首次打开带 hash 的 URL 时“钉住”目标：页面高度变化（`ResizeObserver`，在绘制前执行）或滚动停下时，把目标重新对齐到它的 `scroll-margin-top`。浏览器自身的平滑滚动保持不变；滚动进行中发生的变化在滚动停下后修正。读者滚轮、触摸、点击、按键，或在没有布局变化时自行移动了位置，都会立即解除钉住；最长钉住 20 秒。刷新和前进/后退不处理，以保留浏览器恢复的阅读位置。

验证：在无滚动锚定（模拟 Safari）且图片延迟 1.5 至 5 秒的条件下，修复前目标最终偏离 3000 至 12000px，修复后稳定在 72px（顶栏 64px 下方）。若以后为图片补上宽高或 `aspect-ratio`，可以减少布局偏移，但本脚本仍可保留作为兜底。

### 友链

友链数据保存在 `data/friends.toml`，每个 `[[friends]]` 条目包含必填的 `name`、`url`，以及可选的 `icon`、`iconFill` 和双语 `description`。图标下载到 `static/images/friends/` 后随站点发布，页面不直接请求对方服务器；没有图标时显示名字首字母。`layouts/shortcodes/friends.html` 是站点新增的 shortcode，不覆盖主题文件；`content/friends.en.md` 与 `content/friends.zh-cn.md` 调用它，分别生成 `/friends/` 和 `/zh-cn/friends/`。顶部菜单和各语言页脚 `params.footer.custom` 只链接到对应语言的友链页。新增朋友时只修改数据文件。

`scripts/check_friends.py` 由 `scripts/check.sh` 调用，校验数据字段、URL 协议、重复项和图标文件，并确认两种语言的友链页都包含全部链接。

### 主题和模板覆盖

`themes/LoveIt` 固定在 `.gitmodules` 与 Git index 记录的 commit。根目录当前有三类覆盖：

- `layouts/_default/summary.html`：优先用 front matter 的 `abstract` 生成列表摘要。
- `layouts/partials/assets.html`：为主题的页面配置补齐默认值。
- `layouts/_default/_markup/render-image.html`：实现图片 URL 映射和统一图注。

前两个文件基于主题模板的完整副本。更新主题后必须与新的同路径文件进行三方比较，避免遗漏主题修复。

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
