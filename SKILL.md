---
name: image-craft
description: Generate or edit images through the user's configured GPT image API. Use this skill whenever the user asks an agent to create an image, make a picture, generate artwork, produce a base64/image file from a prompt, transform an existing image, or explicitly mentions gpt-image-2, 文生图, 图片生成, 图片编辑, 改图, 生图, or 画一张图. Supports OpenAI-compatible APIs including Right Codes, OpenAI, Azure, and other compatible endpoints.
---

# Image Craft

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
