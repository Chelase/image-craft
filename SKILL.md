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
- Reference image input (local files via `--image`, remote URLs via `--image-url`) for guided generation.
- Request body profiles for automatic payload construction across different API patterns.
- Optional direct API calls for custom payloads when the bundled script is too narrow.

## Request Body Strategy

The skill uses request body profiles to construct the correct API payload for different usage patterns. By default, the profile is auto-detected:

| User Intent | Default Profile | Endpoint |
|---|---|---|
| Text-to-image (no reference) | `images-generations` | `/v1/images/generations` |
| Text-to-image with reference image | `images-generations-reference` | `/v1/images/generations` |
| Image analysis / vision | `chat-completions-vision` | `/v1/chat/completions` |
| Image transformation | `chat-completions-transform` | `/v1/chat/completions` |
| Custom supplier fields | `custom` | (user-specified) |

**Agent decision rules:**
- If the user provides a reference image alongside a text prompt → use `images-generations-reference` (or `chat-completions-vision` for analysis tasks).
- If the user asks to modify/edit an existing image → use `chat-completions-transform`.
- If the API documentation does not specify the correct payload shape for a supplier → ask the user which profile to use.
- Use `--profile` to explicitly override auto-detection.

**When to ask the user:**
- The API documentation does not specify the reference image field name.
- Multiple valid payload shapes exist for the same task.
- The user requests supplier-specific advanced parameters.

**Payload override options:**
- `--payload-json` — supply a complete JSON request body, replacing the profile-built payload entirely. Use when you know the exact API shape.
- `--payload-merge` — supply a JSON fragment that is deep-merged into the profile-built payload. Use for adding supplier-specific fields like `seed`, `n`, or custom headers.

**Reference image purposes:**
Append `::purpose` to `--image` or `--image-url` values:
- `::style` — style reference (default)
- `::composition` — layout/structure reference
- `::subject` — subject/character reference
- `::palette` — color palette reference

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

# Migrate an image toward a target style with partial strength
pwsh -File .\scripts\image_craft.ps1 -Command transform -Prompt "保留人物构图" -InputImage .\input.png -StyleName "watercolor" -StyleStrength 0.65 -Output .\outputs\watercolor-migration.png
```

Python:
```bash
python scripts/image_craft.py transform --prompt "改成水彩画风" --input input.png --output outputs/watercolor.png

# Migrate an image toward a target style with partial strength
python scripts/image_craft.py transform --prompt "preserve the portrait composition" --input input.png --style-name "watercolor" --style-strength 0.65 --output outputs/watercolor-migration.png
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
pwsh -File .\scripts\image_craft.ps1 -Command batch -Prompt "未来城市" -Styles "cyberpunk,watercolor,blender-render" -OutputDir .\outputs\batch -AbLabel A,B,C -DryRun -Format json

Python:
python scripts/image_craft.py generate --prompt "东京街头" --style-name "赛博朋克" --output outputs/cyberpunk.png
python scripts/image_craft.py batch --prompt "future city" --styles "cyberpunk,watercolor,blender-render" --output-dir outputs/batch --ab-label A --ab-label B --ab-label C --dry-run --format json

**Generating a structured design brief:**
```
# Preview the brief as Markdown
python scripts/image_craft.py brief --field "主题=一杯桂花乌龙茶放在石桌上" --field "场景=中式庭院，秋天午后" --brief-type product-photography --format markdown

# Use a brief template with auto-filled defaults
python scripts/image_craft.py brief --template "产品摄影" --field "主题=一杯桂花乌龙茶" --field "背景=大理石桌面" --to-prompt --style-name photography --format json

# Convert to an enhanced prompt with style
python scripts/image_craft.py brief --field "主题=a cup of osmanthus oolong tea" --field "场景=Chinese garden, autumn afternoon" --to-prompt --style-name "photography" --format json
```
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

# Preview an image-to-image style migration prompt
python scripts/image_craft.py prompt --prompt "preserve the portrait composition" --style-name "watercolor" --style-strength 0.65 --format json

# Preview a batch plan for style exploration and A/B comparison
python scripts/image_craft.py batch --prompt "cyberpunk city" --explore --limit 3 --output-dir outputs/explore --dry-run --format json
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
5. **Style migration** — for `transform`, `--style-strength` with `--style-id` or `--style-name` migrates the source image toward the target style while preserving source structure and subject identity.
6. **Structured brief generator** — `brief --field key=value ...` accepts Chinese or English field pairs and outputs a structured design brief. Use `--to-prompt` to convert the brief into an enhanced prompt through the existing style/template/color pipeline.
7. **Batch style variants** — `batch --styles ...` or `batch --explore` creates multiple enhanced prompts and output paths from one source prompt, with optional A/B labels.
8. **Visual phrase normalization** — common Chinese scene descriptors and aspect ratios such as `16:9` are normalized into compact English image-prompt phrases before style templates are applied.
9. **Template rendering** — `--template` searches `data/prompts.csv`, renders variables from repeated `--var key=value`, and uses the original prompt for common subject fields.
10. **Color palette injection** — `--color` searches `data/colors.csv` and appends the palette's prompt description.

**Override defaults:**

| Flag | Effect |
|------|--------|
| `--no-quality` | Skip quality term injection |
| `--negative` | Include negative prompts |
| `--style-id` or `--style-name` | Apply a style and its enhancement |
| `--style-mix style:weight,...` | Blend multiple styles with weight control |
| `--style-strength 0.0..1.0` | Control image-to-image style migration strength for `transform` |
| `batch --styles ...` | Generate or preview multiple explicit style variants |
| `batch --explore --limit N` | Search recommended styles and build a style exploration batch |
| `--ab-label LABEL` | Attach A/B labels to batch variants; repeat as needed |
| `brief --field key=value` | Build a structured design brief from Chinese or English field pairs |
| `brief --template ID` | Load a brief template from data/briefs.csv with auto-filled defaults and field hints |
| `brief --to-prompt` | Convert the structured brief into an enhanced prompt |
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
