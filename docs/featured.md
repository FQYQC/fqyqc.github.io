# 首页精选

<!-- 自动生成，请勿手改：由 scripts/sync_featured.py 根据文章开头的 featured 标记生成，运行 ./scripts/check.sh 时自动更新。 -->

首页实际以文章里的标记为准，本文件只供参考。

- **设为精选**：在文章开头加一行 `featured: true`，中英文任一版本即可，按发布日期从新到旧排。
  写数字如 `featured: 15` 则按数字从小到大排在所有 `true` 前面；用 10、20、30 留间隔，插入新文章时不用改其他文章。
- **封面**：在文章开头加一行 `cover: <文章里某张图片的路径>`（从正文的图片语法里复制，如
  `/assets/local-assets/posts/<文章>/01.jpg`），构建时从图床下载并自动压缩；下载失败时退回文字卡。
  也可以把图片命名为 `<文章文件名>.jpg`（或 `.png`、`.webp`）放进 `assets/images/covers/`，本地图片优先。
- **主卡底色**：自动取封面主色并淡化，无需设置。

| 顺序 | 文章 | 标记 | 发布日期 | 封面 |
|---|---|---|---|---|
| 1 | `travel-L001-PK-HZ.03` | `10` | 2025-11-14 | 图床 `/assets/local-assets/posts/travel-L001-PK-HZ/100.jpg` |
| 2 | `what-ai-brings-us` | `20` | 2026-08-01 | 无，显示文字卡 |
| 3 | `travel-C008-eugene` | `30` | 2025-12-12 | 图床 `/assets/local-assets/posts/travel-C008-eugene/C008-alaska_paint.jpeg` |
| 4 | `travel-L002-Abu` | `40` | 2025-09-10 | 图床 `/assets/local-assets/posts/travel-L002-Abu/15-mosque_fav.jpeg` |
