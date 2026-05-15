# Image Craft

> [English](README.md) | 中文

AI Agent 通用图片生成技能 - 支持 OpenAI 兼容 API 的文生图和图编辑

## 功能特性

- **文生图**: 通过文本提示词生成图片
- **图编辑**: 通过文本指令编辑现有图片
- **多接口**: 同时支持 PowerShell 和 Python 脚本
- **OpenAI 兼容**: 支持 Right Codes、OpenAI、Azure 等兼容端点

## 安装

### OpenCode Agent

1. 克隆仓库到技能目录：
   ```bash
   git clone https://github.com/Chelase/image-craft.git ~/.agents/skills/image-craft
   ```

2. 配置 API Key（见[配置说明](#配置说明)）

3. 当你请求生成图片时，技能会自动可用

### 其他 AI Agent

将 `SKILL.md` 文件内容复制到你的 Agent 技能系统中，并确保脚本可访问。

## 配置说明

在技能根目录创建 `private_config.json` 文件：

```json
{
  "api_key": "你的API密钥",
  "base_url": "https://right.codes/draw",
  "model": "gpt-image-2"
}
```

或设置环境变量：

```bash
export IMAGE_CRAFT_API_KEY="你的API密钥"
export IMAGE_CRAFT_BASE_URL="https://right.codes/draw"  # 可选
export IMAGE_CRAFT_MODEL="gpt-image-2"                  # 可选
```

**优先级顺序：**
1. 脚本参数 (`-Model`, `-BaseUrl`)
2. 环境变量 (`IMAGE_CRAFT_MODEL`, `IMAGE_CRAFT_BASE_URL`)
3. `private_config.json`
4. 默认值 (`gpt-image-2`, `https://right.codes/draw`)

## 使用方法

### PowerShell

```powershell
# 生成图片
pwsh -File scripts/image_craft.ps1 -Command generate -Prompt "一只可爱的猫咪" -Output outputs/cat.png

# 转换图片
pwsh -File scripts/image_craft.ps1 -Command transform -Prompt "改成水彩画风" -InputImage input.png -Output outputs/watercolor.png
```

### Python

```bash
# 生成图片
python scripts/image_craft.py generate --prompt "一只可爱的猫咪" --output outputs/cat.png

# 转换图片
python scripts/image_craft.py transform --prompt "改成水彩画风" --input input.png --output outputs/watercolor.png
```

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

## 安全说明

- 切勿提交 `private_config.json` 文件
- `.gitignore` 已配置排除此文件
- 生产环境建议使用环境变量

## 许可证

MIT

## 支持

如有问题或建议，请在 GitHub 提交 Issue。
