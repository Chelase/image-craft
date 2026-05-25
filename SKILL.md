---
name: image-craft
description: "Generate or edit images through the user's configured GPT image API. Use this skill whenever the user asks an agent to create an image, make a picture, generate artwork, produce a base64/image file from a prompt, transform an existing image, or explicitly mentions gpt-image-2, 文生图, 图片生成, 图片编辑, 改图, 生图, or 画一张图. Supports OpenAI-compatible APIs including Right Codes, OpenAI, Azure, and other compatible endpoints."
version: 1.0.0
metadata:
  openclaw:
    homepage: https://github.com/Chelase/image-craft
---

# Image Craft

> **TL;DR** - Image Craft is a universal AI Agent skill for generating and editing images through OpenAI-compatible APIs such as `gpt-image-2`, Azure-compatible endpoints, and Right Codes. It bundles 54 art styles, 119 prompt templates, and 50 color palettes with local search and prompt enhancement.
>
> **Use it when:** You need image generation or image editing from an Agent CLI without writing API payload code.
> **Install:** `git clone https://github.com/Chelase/image-craft.git ~/.agents/skills/image-craft`
> **One command:** `python scripts/image_craft.py generate --prompt "cyberpunk Tokyo street" --style-name cyberpunk --output outputs/tokyo.png`

Use this skill to call the user's configured GPT image API and save generated images as local files.

## Prerequisites

**Before using this skill, you MUST configure:**

1. **API Key** - Required for authentication
2. **Base URL** - Required API endpoint URL

Without these configurations, the skill will not work.

## Capabilities

- Text-to-image generation with `POST /v1/images/generations`.
- Image transformation through the OpenAI-compatible chat endpoint with a data URL image input.
- Optional direct API calls for custom payloads when the bundled script is too narrow.

## Configuration

### Required Settings

Create a `private_config.json` file in this skill directory:

```json
{
  "api_key": "YOUR_API_KEY_HERE",
  "base_url": "https://your-api-endpoint.com"
}
```

Or set environment variables:

```bash
export IMAGE_CRAFT_API_KEY="your-api-key"
export IMAGE_CRAFT_BASE_URL="https://your-api-endpoint.com"
```

### Optional Settings

```json
{
  "api_key": "YOUR_API_KEY_HERE",
  "base_url": "https://your-api-endpoint.com",
  "model": "gpt-image-2"
}
```

**Configuration priority:**
1. Script parameters (`-BaseUrl`, `-Model`)
2. Environment variables (`IMAGE_CRAFT_BASE_URL`, `IMAGE_CRAFT_API_KEY`, `IMAGE_CRAFT_MODEL`)
3. `private_config.json`

## Security

The API key is stored in `private_config.json`, which should stay local and should not be pasted into normal responses. If the config is missing, ask the user to provide or restore `IMAGE_CRAFT_API_KEY`.

When reporting results, mention the output image path, model, and prompt summary. Do not print the API key.

## Quick Start

**Step 1: Configure your API** (see [Configuration](#configuration))

**Step 2: Use the script**

PowerShell:
```powershell
pwsh -File .\scripts\image_craft.ps1 -Command generate -Prompt "画一只可爱的猫咪" -Output .\outputs\cat.png
```

Python:
```bash
python scripts/image_craft.py generate --prompt "画一只可爱的猫咪" --output outputs/cat.png
```

For image-to-image transformation:

PowerShell:
```powershell
pwsh -File .\scripts\image_craft.ps1 -Command transform -Prompt "改成水彩画风" -InputImage .\input.png -Output .\outputs\watercolor.png
```

Python:
```bash
python scripts/image_craft.py transform --prompt "改成水彩画风" --input input.png --output outputs/watercolor.png
```

## Model Selection

Default model: `gpt-image-2` (can be configured via config file or environment variable).

Available models:

- `gpt-image-2`: Use by default for normal image generation and straightforward edits.
- `gpt-image-2-vip`: Use when the user's image request is unusually complex, such as multiple subjects with detailed relationships, exact composition constraints, high-fidelity commercial/product output, precise text rendering, elaborate style mixing, or a difficult image transformation.

If the user explicitly requests a model, honor it. Otherwise choose `gpt-image-2` unless the prompt complexity clearly justifies `gpt-image-2-vip`.

## Style System

The skill includes 54 art styles across 8 categories. Styles, prompt templates, and color palettes are searched through the unified local backend in `scripts/search.py`.

**Using a style by name:**

```
PowerShell:
pwsh -File .\scripts\image_craft.ps1 -Command generate -Prompt "东京街头" -StyleName "赛博朋克" -Output .\outputs\cyberpunk.png
pwsh -File .\scripts\image_craft.ps1 -Command suggest -Prompt "cyberpunk" -Limit 1 -Format json
pwsh -File .\scripts\image_craft.ps1 -Command prompt -Prompt "3d风格未来科幻城市，16:9，城市高空俯瞰" -StyleId 3d -Negative -Format json
pwsh -File .\scripts\image_craft.ps1 -Command prompt -Prompt "未来城市" -StyleMix "cyberpunk:0.7,blender-render:0.3" -Negative -Format json

Python:
python scripts/image_craft.py generate --prompt "东京街头" --style-name "赛博朋克" --output outputs/cyberpunk.png
```

**Using a style by ID:**

```
python scripts/image_craft.py generate --prompt "东京街头" --style-id "cyberpunk" --output outputs/cyberpunk.png
```

**Getting style suggestions (no image generated):**

```
python scripts/image_craft.py suggest "赛博朋克城市"

# Search every domain and return JSON
python scripts/image_craft.py suggest "赛博朋克未来城市" --domain all --format json

# Ask for a full design-system recommendation
python scripts/image_craft.py suggest "赛博朋克未来城市" --design-system
```

**Previewing final enhanced prompts (no API call, no image generated):**

```
python scripts/image_craft.py prompt --prompt "3d风格未来科幻城市，16:9，城市高空俯瞰" --style-id 3d --negative --format json

# Blend multiple weighted styles in the final prompt preview
python scripts/image_craft.py prompt --prompt "未来城市" --style-mix "cyberpunk:0.7,blender-render:0.3" --negative --format json
```

**Using prompt templates and color palettes:**

```
python scripts/image_craft.py generate --prompt "东京街头" --template "urban landscape" --var city="Tokyo" --var "time of day=night" --color "midnight blue" --style-name "cyberpunk" --output outputs/tokyo.png
```

**Available style categories:** traditional, digital, illustration, photography, 3d, special. Category aliases such as `--style-id 3d` resolve to practical defaults such as `blender-render`.

## Prompt Enhancement

All `generate` and `transform` commands automatically:

1. **Quality term injection** — adds `masterpiece, best quality, high resolution, detailed, professional, trending on artstation` unless `--no-quality` is passed.
2. **Negative prompt** — includes per-style negative terms plus general quality negatives (`lowres, bad anatomy, blurry, etc.`) when `--negative` is passed.
3. **Style enhancement** — if a style is specified, the style's `prompt_template` field is merged with the user's prompt (replacing any `{subject}` placeholder).
4. **Style mixing** — `--style-mix "cyberpunk:0.7,blender-render:0.3"` uses the highest-weight style as the primary template, adds weighted influence descriptors from all styles, and merges their negative prompts. When `--style-mix` is provided together with `--style-id` or `--style-name`, the style mix takes precedence.
5. **Visual phrase normalization** — common Chinese scene descriptors and aspect ratios such as `16:9` are normalized into compact English image-prompt phrases before style templates are applied.
6. **Template rendering** — `--template` searches `data/prompts.csv`, renders variables from repeated `--var key=value`, and uses the original prompt for common subject fields.
7. **Color palette injection** — `--color` searches `data/colors.csv` and appends the palette's prompt description.

**Override defaults:**

| Flag | Effect |
|------|--------|
| `--no-quality` | Skip quality term injection |
| `--negative` | Include negative prompts |
| `--style-id` or `--style-name` | Apply a style and its enhancement |
| `--style-mix style:weight,...` | Blend multiple styles with weight control |
| `--template` | Render a prompt template from the local template library |
| `--var key=value` | Fill template variables; repeat as needed |
| `--color` | Add a searched color palette description |
| `prompt` | Preview the final enhanced prompt without calling the image API |
| `suggest --domain style|prompt|color|all` | Search local style/template/color data without generating |
| `suggest --design-system` | Return combined style + prompt + color recommendations |

## Workflow

1. **Check configuration** - Ensure `base_url` and `api_key` are configured.
2. Create a clear prompt from the user's request. Preserve user-provided names, brands, languages, and style constraints.
3. Choose `generate` for prompt-only requests and `transform` when the user provides an image path or image content to edit.
4. Save outputs to a concrete image path. Use a descriptive filename and create the output directory if needed.
5. Decode the returned `b64_json` or markdown data URL into the requested image file.
6. Tell the user where the image was saved. Include a short note if the API returned a revised prompt.

## API Endpoints

Text-to-image endpoint:

```http
POST /v1/images/generations
Content-Type: application/json
Authorization: Bearer <api-key>
```

Typical body:

```json
{
  "model": "gpt-image-2",
  "prompt": "..."
}
```

OpenAI-compatible image transformation endpoint:

```http
POST /v1/chat/completions
Content-Type: application/json
Authorization: Bearer <api-key>
```

Use a `messages` array with text plus an `image_url` item:

```json
{
  "model": "gpt-image-2",
  "messages": [
    {
      "role": "user",
      "content": [
        {"type": "text", "text": "改成水彩画风"},
        {
          "type": "image_url",
          "image_url": {"url": "data:image/png;base64,..."}
        }
      ]
    }
  ]
}
```

## Troubleshooting

- **Missing API key or base URL**: Verify `private_config.json` or environment variables are set correctly.
- **Authentication fails**: Check if `IMAGE_CRAFT_API_KEY` is correct and not expired.
- **Connection fails**: Verify `IMAGE_CRAFT_BASE_URL` is correct and accessible.
- The script supports `data[0].b64_json`, `data.url`, direct data URLs, and markdown image links such as `![image](data:image/png;base64,...)` or `![image](https://...)`.
- If the network is blocked by the runtime, request permission to run the command with network access rather than trying to work around the restriction.
