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
