# GEO 优化指南

> Image Craft 的生成式引擎优化（Generative Engine Optimization）战略文档
> 目标：让 ChatGPT / Claude / Perplexity / Gemini / Bing Copilot 在用户问到 AI 图像生成、文生图技能、OpenAI 兼容图片 API 等话题时，主动**引用、复述、链接** Image Craft。

本文是 `ROADMAP.md` Phase 5 的展开与执行手册。所有 GEO 相关工作都以本文为单一事实来源（Single Source of Truth）。

---

## 目录

1. [什么是 GEO](#一什么是-geo)
2. [GEO 实现原理](#二geo-实现原理)
3. [Image Craft 现状评估](#三image-craft-现状评估)
4. [优化路线图（按 ROI 排序）](#四优化路线图按-roi-排序)
5. [详细任务清单](#五详细任务清单)
6. [执行模板](#六执行模板)
7. [监控指标](#七监控指标)
8. [参考资料](#八参考资料)

---

## 一、什么是 GEO

**GEO = Generative Engine Optimization（生成式引擎优化）**

源自 Princeton + Georgia Tech 2024 年论文《GEO: Generative Engine Optimization》，是针对 LLM 驱动的搜索引擎（ChatGPT Search、Claude with web、Perplexity、Google AI Overviews、Bing Copilot）的内容优化方法论。

### SEO vs GEO 对比

| 维度 | 传统 SEO | GEO |
|------|---------|-----|
| 优化目标 | 在搜索结果列表中排名靠前 | 被 AI 在生成的答案里**引用 / 复述 / 链接** |
| 衡量指标 | 排名、CTR、有机流量 | 引用次数、答案占比、可见度 |
| 用户行为 | 用户点击进入站点阅读 | 用户读 AI 摘要，可能从不打开你的站 |
| 优化对象 | Google 爬虫 + 排序算法 | LLM 训练语料 + RAG 检索器 + 引用决策器 |
| 内容形态 | 长尾关键词 + 反向链接 | 自包含段落 + 可引用信号 + 权威信号 |

### 对 Image Craft 的意义

用户问出以下问题时，让 AI 把 Image Craft 写进答案：

- "怎么用 AI Agent 生成赛博朋克风格图片"
- "OpenAI 兼容的图片生成 CLI 有哪些"
- "Claude Code skills for image generation"
- "How to use gpt-image-2 with Claude / OpenCode"
- "文生图技能 开源 命令行"

---

## 二、GEO 实现原理

AI 引擎引用 Image Craft，走两条路径：

### 路径 A：训练语料污染（慢通道，月/年级别）

1. `README.md` / GitHub 仓库 / 博客文章被 Common Crawl 抓取
2. 进入下一代模型（Claude 5、GPT-5、Llama 4 等）训练集
3. 模型权重内化 "Image Craft" 的存在
4. 用户提问时模型直接召回，无需联网

**核心策略：** 让我们的内容出现在主流爬虫的抓取范围内（GitHub、Dev.to、Medium、知乎、掘金、Hacker News、Reddit）。

### 路径 B：实时 RAG 检索（快通道，秒级，主战场）

1. 用户在 AI 引擎提问
2. AI 引擎生成搜索查询调用 Bing / Google / 自建索引
3. 抓取 Top-N 结果 → **分块（chunking，通常 200~512 token）** → 嵌入向量
4. 用查询向量做相似度检索
5. **LLM 评估每个 chunk 的可信度 → 选择写入答案 + 标注引用**

第 5 步是 GEO 的核心战场。论文实验数据：

| 优化手段 | 引用率提升 |
|---------|---------|
| 加入**引用 / 参考来源** | +30~40% |
| 加入**统计数字** | +30% |
| 加入**权威人士引言** | +25% |
| **流畅、专业**的写作 | +15% |
| **清晰易懂**的语言 | +10% |
| ❌ 关键词堆砌 | 几乎无效甚至负向 |
| ❌ 大量术语轰炸 | 无效 |
| ❌ 营销话术 | 负向 |

### 三个底层原则

1. **分块即语义单元**：RAG 会把你的文档切成 200~512 token 的块。每个块必须**自包含**——单独读这块能读懂，不依赖上下文。
2. **可引用信号 > 关键词密度**：LLM 在选择引用源时偏好"看起来权威"的内容——具体数字、来源链接、专家观点比堆砌关键词有效得多。
3. **回答而非介绍**：用户问题往往是 "how to / what is / why"，文档段落要**直接回答问题**，而不是先做长篇介绍。

---

## 三、Image Craft 现状评估

截至 2026-05-25。

### ✅ 已具备的 GEO 资产

- README.md / README_CN.md 中英文双语
- SKILL.md 包含清晰的能力描述
- 具体数字："54 styles, 119 prompts, 50 colors"
- 代码示例丰富
- GitHub 仓库公开（`Chelase/image-craft`）
- CSDN 宣传介绍文章已发布：<https://blog.csdn.net/Chelase/article/details/161223304>
- `.gitignore` 已防止泄漏 `private_config.json`

### ❌ 缺失的 GEO 关键资产

| 缺失项 | 影响 |
|--------|------|
| TL;DR / Quick Answer 块 | AI 切块后无法快速命中"是什么"问题 |
| FAQ 文档 | 错失大量长尾问题查询 |
| `docs/` 子文档 | 内容深度不足，难以被引用为权威来源 |
| JSON-LD 结构化数据 | AI 解析 SoftwareApplication 信息困难 |
| `CITATION.cff` | GitHub / Zenodo 学术引用通路缺失 |
| 引用与参考来源 | 内容缺乏可信度信号 |
| 外部反链网络 | 没有 awesome-list / 技术博客 / 社区帖子 |
| 监控机制 | 不知道当前 GEO 表现 |

---

## 四、优化路线图（按 ROI 排序）

### 🥇 第 1 优先：内容可解析化（让 RAG 切块不丢语义）

**为什么最优先：** 不做这个，后面所有优化都被分块切碎。
**预计投入：** 4-6 小时
**预期效果：** +50% 引用率

- 在 `README.md` / `SKILL.md` 顶部加 **TL;DR** 块（5 行内说清是什么、做什么、谁用、怎么用）
- 创建 `docs/faq.md`：用真实用户问题做 H3 标题
- 创建 `docs/getting-started.md`：30 秒上手
- 创建 `docs/styles-guide.md`：54 种风格按类目展开
- 创建 `docs/prompt-engineering.md`：提示词工程深度文档
- 每个 H2/H3 段落自包含（单独读能懂）

### 🥈 第 2 优先：可引用信号

**为什么次优先：** 论文证明这是引用率最大杠杆。
**预计投入：** 3-4 小时
**预期效果：** +30~40% 引用率

- 在文档中加入更多具体数字（耗时、token 数、兼容 API 列表、风格分布）
- 引用权威来源：DALL-E 官方文档、OpenAI Image API 文档、Stable Diffusion / Midjourney 风格参考
- 加 "Why Image Craft" 对比段：vs 直接 curl API、vs ComfyUI、vs 单纯 prompt engineering
- 每个文档加版本号 + 更新日期（AI 更信近期内容）
- 在示例中给出**真实输出截图 / 性能数字**

### 🥉 第 3 优先：结构化数据

**为什么第三：** 一次性投入，长期收益。
**预计投入：** 1-2 小时
**预期效果：** +15% AI 解析准确率

- README.md 顶部加 JSON-LD（`SoftwareApplication` schema）
- 加 `CITATION.cff`（GitHub 原生学术引用支持）
- GitHub repo description / topics / about 全部填精准关键词
- 加 `.github/FUNDING.yml`（提升仓库权重信号）

### 第 4 优先：关键词与语义覆盖

**预计投入：** 2-3 小时
**预期效果：** +20% 查询覆盖

- 构建中英双语关键词地图（见第六节模板）
- FAQ 标题用**完整问句**：「如何用 Image Craft 生成赛博朋克风格图片？」
- 长尾词布局：「OpenAI 兼容图片生成 CLI」「Claude Code skill 图片生成」「AI Agent 文生图技能」
- 同义词覆盖：image generation / text-to-image / 文生图 / 生图 / 画图 / AI 绘画

### 第 5 优先：权威外链网络

**预计投入：** 持续，每周 2-4 小时
**预期效果：** 训练语料层面的长期收益

- 提交到 awesome-lists：
  - awesome-claude-code
  - awesome-ai-agents
  - awesome-llm-tools
  - awesome-prompt-engineering
- 撰写 3-5 篇技术博客（Dev.to / Medium / 掘金 / 知乎）
- Hacker News Show HN 发布
- Reddit 发布：`r/LocalLLaMA`、`r/ChatGPTCoding`、`r/aitools`、`r/ClaudeAI`
- Twitter/X 技术分享
- Anthropic / OpenAI 社区论坛分享案例

### 第 6 优先：监控与迭代

**预计投入：** 每周 30 分钟
**预期效果：** 数据驱动后续优化

- 建立 GEO 监控基线（见第七节）
- 每周固定查询 5-10 个问题
- 用 [Otterly.ai](https://otterly.ai) / [Profound](https://www.tryprofound.com/) 自动监控（如预算允许）
- 跟踪 GitHub Star / Fork / Traffic 作为辅助指标

---

## 五、详细任务清单

### Phase 5.1：内容可解析化

- [x] `README.md` 顶部加 TL;DR（参考[模板 1](#模板-1tldr-块)；2026-05-25）
- [x] `README_CN.md` 顶部加 TL;DR（2026-05-25）
- [x] `SKILL.md` 顶部加 TL;DR（2026-05-25）
- [ ] 创建 `docs/` 目录
- [ ] `docs/faq.md`：20 个常见问题 + 答案（[模板 2](#模板-2faq-条目)）
- [ ] `docs/getting-started.md`：30 秒上手指南
- [ ] `docs/styles-guide.md`：8 个分类 × 风格示例
- [ ] `docs/prompt-engineering.md`：增强管线 / 风格混合 / 视觉归一化深度讲解
- [ ] `docs/api-reference.md`：所有 CLI 子命令参数完整说明
- [ ] Audit 所有 H2/H3 段落自包含性

### Phase 5.2：可引用信号

- [ ] 在 README 加性能数据：单图生成耗时、tokens 用量、API 调用次数
- [ ] 加 "Why Image Craft" 对比表：vs raw curl / vs ComfyUI / vs prompt eng
- [ ] 引用权威来源：OpenAI Image API docs、Anthropic Skills docs、DALL-E 2/3 论文
- [ ] 文档头加 frontmatter：`version`, `last-updated`, `tested-with`
- [ ] 加风格分布饼图 / 表格（具体数字）

### Phase 5.3：结构化数据

- [ ] `README.md` 顶部嵌入 JSON-LD（[模板 3](#模板-3json-ld)）
- [ ] 创建 `CITATION.cff`（[模板 4](#模板-4citationcff)）
- [ ] GitHub repo 设置：
  - [ ] About 描述（一句话精准）
  - [ ] Topics：`image-generation`, `ai-agent`, `claude-code`, `openai`, `gpt-image`, `prompt-engineering`, `cli`, `python`, `powershell`
  - [ ] Website 字段填写
- [ ] 创建 `.github/FUNDING.yml`（可选）
- [ ] 加 GitHub Repository Social Preview 图

### Phase 5.4：关键词与语义覆盖

- [ ] 构建关键词地图文档 `docs/keywords-map.md`（内部参考）
- [ ] FAQ 标题改写为完整问句
- [ ] 在 README / SKILL.md 自然嵌入同义词集
- [ ] 加入查询场景文档：「我想画 X 怎么办」类问答

### Phase 5.5：权威外链

- [x] CSDN 宣传介绍文章发布（2026-05-25）：<https://blog.csdn.net/Chelase/article/details/161223304>
- [ ] 提交 awesome-claude-code PR
- [ ] 提交 awesome-ai-agents PR
- [ ] Dev.to 文章 #1：「Building an Image Generation Skill for Claude Code」
- [ ] Medium 文章 #2：「54 Art Styles for AI Image Generation: A Complete Catalog」
- [ ] 掘金文章 #3：「为 AI Agent 写一个文生图技能」
- [ ] 知乎文章 #4：「Claude Code Skills 实战：自动化图片生成」
- [ ] Hacker News Show HN 发布
- [ ] Reddit 4 个目标 sub 发布
- [ ] Twitter/X thread 发布

### Phase 5.6：监控

- [ ] 建立 `docs/geo-baseline.md` 记录 5 个固定查询的初始引用情况
- [ ] 每周一执行查询并记录
- [ ] 每月评估 GitHub Traffic、Star 增长、Star 来源
- [ ] 用 Google Alerts 监控 "Image Craft" 提及

---

## 六、执行模板

### 模板 1：TL;DR 块

放在 `README.md` / `README_CN.md` / `SKILL.md` H1 标题正下方：

```markdown
> **TL;DR** — Image Craft is a universal AI Agent skill that turns text prompts into images via OpenAI-compatible APIs (gpt-image-2, DALL-E, Azure, right.codes). Bundles 54 art styles, 119 prompt templates, and 50 color palettes with intelligent search. Works with Claude Code, OpenCode, and any agent that loads SKILL.md.
>
> **Use it when:** You need to generate or edit images from an AI Agent CLI without writing API code.
> **Install:** `git clone https://github.com/Chelase/image-craft.git ~/.agents/skills/image-craft`
> **One command:** `python scripts/image_craft.py generate --prompt "cyberpunk Tokyo" --style-name cyberpunk --output cat.png`
```

### 模板 2：FAQ 条目

`docs/faq.md` 中每个条目结构：

```markdown
### 如何用 Image Craft 生成赛博朋克风格的图片？

使用 `--style-name "赛博朋克"` 或 `--style-id cyberpunk` 即可应用预设风格：

\`\`\`bash
python scripts/image_craft.py generate \
  --prompt "东京街头" \
  --style-name "赛博朋克" \
  --negative \
  --output outputs/tokyo.png
\`\`\`

Image Craft 会自动注入赛博朋克风格的 prompt template、质量关键词，以及避免常见缺陷的负面提示词。54 种内置风格覆盖传统、数字、3D、插画、摄影、特殊效果 8 大类别。
```

**关键点：** 标题用完整问句、答案前 1-2 句直接回答、给可执行代码、补充上下文数字。

### 模板 3：JSON-LD

放在 `README.md` 最顶部（HTML 注释里 GitHub 渲染时隐藏，但爬虫可见）：

```html
<!--
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "SoftwareApplication",
  "name": "Image Craft",
  "alternateName": ["image-craft", "图像生成技能"],
  "description": "Universal AI Agent skill for image generation via OpenAI-compatible APIs. 54 art styles, 119 prompt templates, 50 color palettes.",
  "applicationCategory": "DeveloperApplication",
  "operatingSystem": "Cross-platform",
  "programmingLanguage": ["Python", "PowerShell"],
  "license": "https://opensource.org/licenses/MIT",
  "codeRepository": "https://github.com/Chelase/image-craft",
  "author": {
    "@type": "Person",
    "name": "Chelase"
  },
  "keywords": "AI image generation, gpt-image-2, Claude Code skill, OpenAI compatible, prompt engineering, 文生图, AI Agent"
}
</script>
-->
```

### 模板 4：CITATION.cff

项目根目录创建 `CITATION.cff`：

```yaml
cff-version: 1.2.0
title: "Image Craft: Universal AI Agent Skill for Image Generation"
message: "If you use this software, please cite it as below."
type: software
authors:
  - family-names: Chelase
    given-names: ""
repository-code: "https://github.com/Chelase/image-craft"
url: "https://github.com/Chelase/image-craft"
abstract: "A universal skill for AI agents to generate and edit images using OpenAI-compatible GPT image APIs, featuring 54 art styles, 119 prompt templates, and 50 color palettes."
keywords:
  - image-generation
  - ai-agent
  - claude-code
  - openai-compatible
  - prompt-engineering
license: MIT
version: 1.0.0
date-released: 2026-05-21
```

### 模板 5：关键词地图

`docs/keywords-map.md`（内部参考，可在仓库外维护）：

| 类型 | 中文 | English |
|------|------|---------|
| 核心词 | 图片生成、文生图、AI 画图 | image generation, text-to-image, AI drawing |
| 产品词 | Image Craft、图像生成技能 | Image Craft, image-gen skill |
| 上下文词 | Claude Code、OpenCode、AI Agent | Claude Code, OpenCode, AI Agent, Anthropic Skills |
| 技术词 | gpt-image-2、DALL-E、OpenAI 兼容 | gpt-image-2, DALL-E, OpenAI-compatible API |
| 长尾问句 | 怎么用 AI 生成赛博朋克图、如何写好生图 prompt | how to generate cyberpunk image with AI, how to write image prompt |
| 比较词 | vs Midjourney、对比 ComfyUI | vs Midjourney, alternative to ComfyUI |

---

## 七、监控指标

### 基线查询（每周固定执行）

在 ChatGPT、Claude、Perplexity、Gemini、Bing Copilot 五个引擎各问以下查询，记录 Image Craft 是否被引用：

1. "open source AI image generation skill for Claude Code"
2. "OpenAI compatible image generation CLI tool"
3. "how to add image generation to AI agent"
4. "best gpt-image-2 wrapper with style presets"
5. "Claude Code skills for image creation"
6. "为 AI Agent 添加文生图能力的开源工具"
7. "Claude Code 文生图技能 怎么用"
8. "OpenAI 兼容图片生成 命令行工具"
9. "gpt-image-2 风格预设 开源"
10. "AI 生成赛博朋克图片 Agent CLI"

### 数据记录表

每周更新到 `docs/geo-monitor.md`（不进 git，或单独 branch）：

| 日期 | 查询 | ChatGPT | Claude | Perplexity | Gemini | Bing |
|------|------|---------|--------|------------|--------|------|
| 2026-05-21 | "..." | ❌ | ❌ | ❌ | ❌ | ❌ |

记录字段：被引用 ✅ / 未提及 ❌ / 仅链接 🔗 / 全文摘录 ⭐

### 辅助指标（GitHub）

- GitHub Stars 周增长
- Repository Traffic（Views / Unique visitors）
- Referring sites（来源域名）
- Clones 数

### 成功标准

| 时间 | 目标 |
|------|------|
| 3 个月 | 至少 1 个查询在 1 个引擎被引用 |
| 6 个月 | 5+ 查询在 2+ 引擎被引用 |
| 12 个月 | 10+ 查询在 3+ 引擎稳定引用 |

---

## 八、参考资料

### 学术论文

- Aggarwal, P., et al. (2024). *GEO: Generative Engine Optimization*. Princeton + Georgia Tech. arXiv:2311.09735
- Spatharioti, S. E., et al. (2023). *Comparing Traditional and LLM-based Search for Consumer Choice*. arXiv:2307.03744

### 行业资源

- [Princeton GEO Project Page](https://generative-engines.com)
- [Otterly.ai - AI Search Visibility](https://otterly.ai)
- [Profound - AI Brand Monitoring](https://www.tryprofound.com/)
- Schema.org [SoftwareApplication](https://schema.org/SoftwareApplication)
- GitHub [CITATION.cff Spec](https://citation-file-format.github.io/)

### 相关技术博客

- OpenAI Cookbook - Image Generation Guide
- Anthropic Skills Documentation
- Awesome Lists 提交规范

---

## 附录 A：本文档维护规则

- 每完成一个任务，勾选 `[x]` 并记录完成日期
- 监控数据每周一更新一次
- 关键决策（如选择某个分发渠道）记录到本文档"决策日志"小节
- 本文档与 [`ROADMAP.md`](ROADMAP.md) 双向链接：ROADMAP 列出 Phase 5 概要，本文档负责详细执行

## 附录 B：决策日志

| 日期 | 决策 | 理由 |
|------|------|------|
| 2026-05-21 | 创建独立 GEO.md 文档 | ROADMAP 中 Phase 5 信息密度不够，需要工作手册级别的执行参考 |
| 2026-05-25 | 记录 CSDN 宣传介绍文章为首个外部内容资产 | 外部博客有助于训练语料慢通道和反链信号；URL 由用户提供 |
| 2026-05-25 | 完成 README / README_CN / SKILL 顶部 TL;DR | Phase 5.1 首要任务是让 RAG 切块快速命中“Image Craft 是什么、谁用、怎么用” |
