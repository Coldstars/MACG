# MACG Channel Finder

`tools/channel-finder` 是 `channel-discovery` workflow 的执行工具，用于根据 `profile.md` 自动发现、清洗、去重、评分和展示渠道候选。

它默认会向上查找最近的 `profile.md`，读取其中的行业关键词、产品线、目标用户、使用场景和官网信息，并用这些信息生成搜索关键词和评分上下文。也可以通过 `--profile-path` 指定其他 profile。

发现规则会优先利用 `profile.md` 中的 `Main Competitors / Reference Sites`：

- 先生成 `竞品名 + tutorial / review / alternative / comparison / sponsor / newsletter / youtube` 等查询。
- 优先发现已经覆盖、评测、教程、赞助或对比过竞品的渠道。
- 竞品官网或官方频道本身会被标记为参考对象，不默认作为 outreach 候选。

联系方式提取会尽量使用公开信息：

- 普通网页正文和 `mailto:` 链接中的邮箱。
- 常见混淆邮箱，例如 `name [at] domain [dot] com`。
- 公开 contact / about / advertise / sponsor / media kit 页面。
- YouTube 公开视频描述中的邮箱。
- 如果没有邮箱，则保留可人工继续联系或查找的公开入口，例如 contact/about 页面、赞助页、media kit、频道主页、GitHub profile、项目主页、作者网站或公开社交主页。
- 不绕过登录、验证码或平台隐藏邮箱。

默认模式不要求 API key。它会优先使用免费公开来源：

- DuckDuckGo 搜索结果（`ddgs`，默认关闭；部分 macOS 环境可能触发底层 TLS 崩溃）
- YouTube 公开搜索元数据（`yt-dlp`，不下载视频）
- GitHub 未认证公开搜索 API
- seed URL 爬取和公开联系方式抽取
- manual seed 兜底

它会生成：

```text
workspaces/channel-discovery/index.html
workspaces/channel-discovery/data/master-candidates.json
workspaces/channel-discovery/data/all-candidates.json
workspaces/channel-discovery/data/all-candidates.csv
workspaces/channel-discovery/data/review-queue.json
workspaces/channel-discovery/data/runs/<run-id>.json
workspaces/channel-discovery/<campaign-slug>/data/runs/<run-id>.json
workspaces/channel-discovery/<campaign-slug>/data/master-candidates.json
workspaces/channel-discovery/<campaign-slug>/data/selected-50.json
workspaces/channel-discovery/<campaign-slug>/data/selected-50.csv
```

用户日常只需要打开：

```text
workspaces/channel-discovery/index.html
```

Agent / Codex 后续分析读取：

```text
workspaces/channel-discovery/data/
workspaces/channel-discovery/<campaign-slug>/data/
```

## Install

在 MACG 仓库根目录执行：

```bash
cd tools/channel-finder
python -m venv .venv
# Windows PowerShell:
.venv\Scripts\Activate.ps1
# macOS / Linux:
# source .venv/bin/activate
pip install -r requirements.txt
```

如果本机 Python/PyPI 证书校验失败，可在确认网络环境可信后重试：

```bash
pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org -r requirements.txt
```

也可以使用你信任的镜像源，例如：

```bash
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt
```

可选：如果你有 YouTube Data API 或 SERP API，再创建 `.env`：

```env
YOUTUBE_API_KEY=your_youtube_api_key
```

`YOUTUBE_API_KEY` 不是强制的。没有它时工具会继续使用 `yt-dlp`、`ddgs`、GitHub、seed URLs 和 manual seeds。

## Run

### 最小本地验证

这个命令只跑 manual/demo，不访问外网。先在 `config/sources.yaml` 中临时设置：

```yaml
demo_mode: true
```

然后运行：

```bash
python src/main.py \
  --providers manual \
  --selected-count 3
```

运行后会更新全局中文 HTML 和 `data/`，用于确认工具链、评分、导出和报告页面能闭环。

### 真实抓取

```bash
python src/main.py \
  --channel-types "youtube,newsletter,technical_blog" \
  --providers auto \
  --max-results-per-keyword 10 \
  --selected-count 50
```

运行后打开：

```text
workspaces/channel-discovery/index.html
```

`auto` 会尝试使用启用中的公开来源、YouTube 公开元数据、GitHub API、seed URLs 和 manual seeds。它需要当前网络能访问 YouTube、GitHub 和配置的 seed URL。`ddgs` 默认关闭；如果你确认本机环境可用，可以在 `config/sources.yaml` 中把 `ddgs.enabled` 改为 `true`。

可选参数：

```bash
python src/main.py \
  --profile-path ../../profile.md \
  --product-name "Your Product" \
  --campaign-slug your-product-channel-discovery \
  --keywords "custom keyword one,custom keyword two" \
  --providers auto
```

## Config Files

```text
config/keywords.yaml        fallback campaign、关键词、渠道类型
config/scoring-rules.yaml   评分权重、fallback 关键词组、合作建议模板
config/sources.yaml         free providers、seed URLs、SERP API template、manual seeds
```

## Data Design

### 全局 `workspaces/channel-discovery/index.html`

用户唯一需要查看的中文渠道库看板。每次新抓取后都会合并所有 campaign 的 master 数据、查重，并刷新这个文件。

### 全局 `data/master-candidates.json`

保存跨 campaign、跨多次 run 的长期渠道池。

### 全局 `data/all-candidates.json`

当前全局 HTML 展示使用的去重候选合集。

### 全局 `data/all-candidates.csv`

方便导入 Excel、飞书、多维表格。

### Campaign `data/runs/<run-id>.json`

保存单次抓取完整数据：

- input
- profile_context
- raw_candidates
- normalized_candidates
- scored_candidates
- selected_50
- review_queue
- summary

### Campaign `data/master-candidates.json`

保存跨多次 run 的长期渠道池：

- 去重后的候选渠道
- first_seen_run_id
- last_seen_run_id
- seen_count
- best_score
- last_score
- status
- notes

### Campaign `data/selected-50.json`

当前 campaign 单次筛选出的 50 个候选渠道。全局 HTML 不直接读取这个文件，而是读取合并后的全局数据。

### Campaign `data/selected-50.csv`

方便导入 Excel、飞书、多维表格。

### `data/review-queue.json`

人工复核队列，默认状态为 `new`。建议人工复核时只维护这些字段：

- review_status: `new` / `shortlisted` / `rejected` / `contacted` / `approved`
- review_notes
- notes

## Safety Rules

- 只使用公开数据。
- 不绕过登录、验证码、付费墙或平台限制。
- 不抓取私人数据。
- 不自动发送邮件。
- 缺失信息显示 `Unknown`，不猜测。
- API key 只能放在 `.env` 或环境变量中，不要提交到 Git。
- `yt-dlp` 只用于公开搜索元数据，不下载视频，不使用 cookies。
- GitHub 默认使用未认证公开接口，遇到 rate limit 会跳过。

## Troubleshooting

### No candidates generated

检查：

1. 是否已安装 `requirements.txt` 中的依赖。
2. 当前网络是否能访问 DuckDuckGo、YouTube、GitHub 或 seed URLs。
3. `config/sources.yaml` 中是否有 `manual_seed_candidates` 或 seed URLs。
4. `--channel-types` 是否包含 `youtube`、`newsletter`、`technical_blog`。
5. GitHub 或搜索源是否触发 rate limit。

同时查看 HTML 顶部的 provider status，或读取：

```text
workspaces/channel-discovery/<campaign-slug>/data/runs/<run-id>.json
```

其中 `summary.provider_statuses` 会说明 provider 是成功、失败，还是因为依赖缺失、配置关闭、缺少 API key 或缺少 SERP template 被跳过。

### HTML report is empty

查看：

```text
workspaces/channel-discovery/<campaign-slug>/data/runs/<run-id>.json
```

确认 `raw_candidates` 是否为空。

### Need to analyze multiple runs

让 Codex / Agent 读取：

```text
workspaces/channel-discovery/<campaign-slug>/data/runs/*.json
workspaces/channel-discovery/<campaign-slug>/data/master-candidates.json
```

可以分析：

- 哪些渠道重复出现
- 哪些关键词找到高质量渠道
- 哪些渠道有联系方式
- 哪些渠道适合优先联系
