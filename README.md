# NailTrend BR

巴西穿戴甲选品 Demo。打开根目录 `index.html` 即可离线查看。

## 开发

需要 Python 3.10+。从仓库根目录运行 `python outputs/build_unified.py`，然后打开 `outputs/market_dashboard.html`。有 Node.js 时运行 `node work/check_combined.cjs` 检查当前样本与交互。运行 `python build_pages.py outputs/market_dashboard.html` 生成根目录九个栏目页及共享样式、脚本。打开根目录 index.html，导航会在独立页面之间切换。发布时一起提交生成的页面和共享文件。

- `outputs/*_template.html`、`channel_extension.html`：页面源码。
- `build_unified.py`、`enrich_channels.py`：合并与生成。
- `crawl_market.py`、`retry_public_channels.py`、`parse_public_retry.py`、`fetch_video_details.py`：采集与复采入口。
- 商品、评论和视频样本随仓库提交。评论处理脚本的原始检索快照、网页缓存和本机配置在本地。默认构建可直接使用整理好的样本。
- `work/sites/nailtrend-br-demo/dist`：早期模拟数据界面。

## 建议交接任务

优先分给同事：商品渠道采集。负责虾皮、美客多的公开数据或授权接口，把结果映射到现有商品结构。验收包括来源链接、采集时间、BRL 价格、销量口径、去重键和访问失败日志。准备可复跑的样例，验证重跑不会重复计数。

并行模块：社媒内容与评论，负责 YouTube / TikTok 的内容字段和授权采集；看板模块负责筛选、趋势图和导出。每个模块从 main 开分支，通过 PR 合并。TikTok 巴西评论及真实成交价格带仍待补。
