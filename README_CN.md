# Image Craft

> [English](README.md) | 中文

> **TL;DR** - Image Craft 是面向 AI Agent 的通用图片生成技能，通过 `gpt-image-2`、Azure 兼容端点、Right Codes 等 OpenAI 兼容 API 支持文生图和图编辑。它内置 54 种艺术风格、119 个提示词模板和 50 套配色，并提供本地搜索和提示词增强。
>
> **适用场景：** 需要在 Agent CLI 中生成或编辑图片，但不想手写图片 API 请求体。
> **安装：** `git clone https://github.com/Chelase/image-craft.git ~/.agents/skills/image-craft`
> **一条命令：** `python scripts/image_craft.py generate --prompt "cyberpunk Tokyo street" --style-name cyberpunk --output outputs/tokyo.png`

AI Agent 通用图片生成技能 - 支持 OpenAI 兼容 API 的文生图和图编辑

## 功能特性

- **文生图**: 通过文本提示词生成图片
- **图编辑**: 通过文本指令编辑现有图片
- **多接口**: 同时支持 PowerShell 和 Python 脚本
- **OpenAI 兼容**: 支持 Right Codes、OpenAI、Azure 等兼容端点

## 前置要求

**使用此技能前，你必须配置：**

1. **API Key** - 用于身份验证
2. **Base URL** - API 端点地址

缺少这些配置，技能将无法工作。

## 安装

### OpenCode Agent

1. 克隆仓库到技能目录：
   ```bash
   git clone https://github.com/Chelase/image-craft.git ~/.agents/skills/image-craft
   ```

2. 配置 API（见[配置说明](#配置说明)）

3. 当你请求生成图片时，技能会自动可用

### 其他 AI Agent

将 `SKILL.md` 文件内容复制到你的 Agent 技能系统中，并确保脚本可访问。

## 配置说明

### 必需配置

在技能根目录创建 `private_config.json` 文件：

```json
{
  "api_key": "你的API密钥",
  "base_url": "https://你的API端点.com"
}
```

或设置环境变量：

```bash
export IMAGE_CRAFT_API_KEY="你的API密钥"
export IMAGE_CRAFT_BASE_URL="https://你的API端点.com"
```

### 可选配置

```json
{
  "api_key": "你的API密钥",
  "base_url": "https://你的API端点.com",
  "model": "gpt-image-2"
}
```

```bash
export IMAGE_CRAFT_MODEL="gpt-image-2"  # 可选，默认为 gpt-image-2
```

**优先级顺序：**
1. 脚本参数 (`-Model`, `-BaseUrl`)
2. 环境变量 (`IMAGE_CRAFT_MODEL`, `IMAGE_CRAFT_BASE_URL`, `IMAGE_CRAFT_API_KEY`)
3. `private_config.json`
4. 默认值（仅 `model` 有默认值：`gpt-image-2`）

## 使用方法

### PowerShell

```powershell
# 生成图片
pwsh -File scripts/image_craft.ps1 -Command generate -Prompt "一只可爱的猫咪" -Output outputs/cat.png

# 转换图片
pwsh -File scripts/image_craft.ps1 -Command transform -Prompt "改成水彩画风" -InputImage input.png -Output outputs/watercolor.png

# 按目标风格强度迁移图片风格
pwsh -File scripts/image_craft.ps1 -Command transform -Prompt "保留人物构图" -InputImage input.png -StyleName "watercolor" -StyleStrength 0.65 -Output outputs/watercolor-migration.png

# 使用风格生成（按名称）
pwsh -File scripts/image_craft.ps1 -Command generate -Prompt "东京街头" -StyleName "赛博朋克" -Output outputs/cyberpunk.png

# 获取风格建议
pwsh -File scripts/image_craft.ps1 -Command suggest -Prompt "赛博朋克城市"

# 获取机器可读的 JSON 建议
pwsh -File scripts/image_craft.ps1 -Command suggest -Prompt "cyberpunk" -Limit 1 -Format json

# 只预览最终增强提示词，不调用图片 API
pwsh -File scripts/image_craft.ps1 -Command prompt -Prompt "3d风格未来科幻城市，16:9，城市高空俯瞰" -StyleId 3d -Negative -Format json

# 预览模板变量和配色组合后的提示词
pwsh -File scripts/image_craft.ps1 -Command prompt -Prompt "东京街头" -Template "urban landscape" -Var city=Tokyo,time_of_day=night -Color "midnight blue" -StyleName cyberpunk -Format json

# 按权重混合多个风格
pwsh -File scripts/image_craft.ps1 -Command prompt -Prompt "未来城市" -StyleMix "cyberpunk:0.7,blender-render:0.3" -Negative -Format json

# 预览同一提示词的多风格批量生成计划，不调用图片 API
pwsh -File scripts/image_craft.ps1 -Command batch -Prompt "未来城市" -Styles "cyberpunk,watercolor,blender-render" -OutputDir outputs/batch -AbLabel A,B,C -DryRun -Format json
```

### Python

```bash
# 生成图片
python scripts/image_craft.py generate --prompt "一只可爱的猫咪" --output outputs/cat.png

# 转换图片
python scripts/image_craft.py transform --prompt "改成水彩画风" --input input.png --output outputs/watercolor.png

# 按目标风格强度迁移图片风格
python scripts/image_craft.py transform --prompt "保留人物构图" --input input.png --style-name "watercolor" --style-strength 0.65 --output outputs/watercolor-migration.png

# 使用风格生成（按名称或ID）
python scripts/image_craft.py generate --prompt "东京街头" --style-name "赛博朋克" --output outputs/cyberpunk.png

# 包含负面提示词（避免常见缺陷）
python scripts/image_craft.py generate --prompt "东京街头" --style-name "赛博朋克" --negative --output outputs/cyberpunk.png

# 获取风格建议
python scripts/image_craft.py suggest "赛博朋克城市"

# 以 JSON 搜索全部本地库
python scripts/image_craft.py suggest "赛博朋克未来城市" --domain all --format json

# 只预览最终增强提示词，不生成图片
python scripts/image_craft.py prompt --prompt "3d风格未来科幻城市，16:9，城市高空俯瞰" --style-id 3d --negative --format json

# 按权重混合多个风格
python scripts/image_craft.py prompt --prompt "未来城市" --style-mix "cyberpunk:0.7,blender-render:0.3" --negative --format json

# 预览同一提示词的多风格批量生成计划，不调用图片 API
python scripts/image_craft.py batch --prompt "未来城市" --styles "cyberpunk,watercolor,blender-render" --output-dir outputs/batch --ab-label A --ab-label B --ab-label C --dry-run --format json

# 根据本地搜索推荐风格生成探索计划
python scripts/image_craft.py batch --prompt "赛博朋克城市" --explore --limit 3 --output-dir outputs/explore --dry-run --format json

# 使用提示词模板和配色方案生成
python scripts/image_craft.py generate --prompt "东京街头" --template "urban landscape" --var city="Tokyo" --var "time of day=night" --color "midnight blue" --style-name "cyberpunk" --output outputs/tokyo.png
```

## 风格系统

内置 54 种艺术风格，覆盖 8 个分类（传统、数码、插画、摄影、3D、特殊等）。所有命令自动注入质量关键词，可选包含负面提示词。

使用 `--style-name` 或 `--style-id` 应用风格。`--style-id 3d` 这类分类别名会自动解析到更实用的默认风格（如 `blender-render`），便于生成专业 3D 渲染效果。使用 `suggest` 命令探索本地 `data/*.csv` 中的风格、提示词模板和配色方案。

统一搜索后端支持：

- `--domain style|prompt|color|all`
- `--design-system` 返回风格 + 模板 + 配色组合建议
- `--random` 随机推荐
- `--format json` 输出机器可读结果

使用 `batch` 可以基于同一个提示词创建多个风格变体。通过 `--styles "cyberpunk,watercolor"` 指定风格，或使用 `--explore --limit 3` 从本地搜索后端自动选择推荐风格。`--dry-run` 会输出 JSON 批量计划，包含增强后的提示词、输出路径和 A/B 标签，但不会调用图片 API。

## 提示词增强

生成相关命令会自动把 `16:9` 等常见画幅写法规范化为专业构图短语，并注入质量关键词（`masterpiece, best quality, high resolution, detailed, professional, trending on artstation`）。添加 `--negative` 参数可包含负面提示词，避免常见缺陷（`lowres, bad anatomy, blurry` 等）。使用 `prompt` 命令可以只预览最终增强提示词，不调用图片 API。

使用 `--style-mix` 可以按权重混合多个风格，例如 `cyberpunk:0.7,blender-render:0.3`。权重最高的风格作为主模板，其余风格会作为加权影响描述加入提示词，并合并各自的负面提示词。

如果同时提供 `--style-mix` 和 `--style-id` / `--style-name`，会优先使用风格混合配置。

对于图编辑 / 图生图转换，使用 `--style-strength` 搭配 `--style-id` 或 `--style-name` 可以把输入图迁移到目标风格，同时保留原图结构和主体身份。例如 `--style-name watercolor --style-strength 0.65` 表示 65% 水彩风格迁移，并保留 35% 原图结构。

## 可用模型

| 模型 | 说明 |
|------|------|
| `gpt-image-2` | 默认模型，适用于标准图片生成和编辑 |
| `gpt-image-2-vip` | 适用于复杂提示词，如多主体、精确文字渲染、复杂风格混合 |

## API 端点

### 文生图

```
POST /v1/images/generations
```

请求体：
```json
{
  "model": "gpt-image-2",
  "prompt": "你的提示词"
}
```

### 图片转换

```
POST /v1/chat/completions
```

请求体：
```json
{
  "model": "gpt-image-2",
  "messages": [
    {
      "role": "user",
      "content": [
        {"type": "text", "text": "你的指令"},
        {"type": "image_url", "image_url": {"url": "data:image/png;base64,..."}}
      ]
    }
  ]
}
```

## 故障排除

- **缺少 API Key 或 Base URL**：检查 `private_config.json` 或环境变量是否正确设置。
- **认证失败**：检查 `IMAGE_CRAFT_API_KEY` 是否正确且未过期。
- **连接失败**：检查 `IMAGE_CRAFT_BASE_URL` 是否正确且可访问。

## 安全说明

- 切勿提交 `private_config.json` 文件
- `.gitignore` 已配置排除此文件
- 生产环境建议使用环境变量

## 许可证

MIT

## 支持

如有问题或建议，请在 GitHub 提交 Issue。
