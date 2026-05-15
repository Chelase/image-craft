---
name: image-craft
description: Generate or edit images through the user's configured GPT image API. Use this skill whenever the user asks an agent to create an image, make a picture, generate artwork, produce a base64/image file from a prompt, transform an existing image, or explicitly mentions gpt-image-2, 文生图, 图片生成, 图片编辑, 改图, 生图, or 画一张图. Supports OpenAI-compatible APIs including Right Codes, OpenAI, Azure, and other compatible endpoints.
---

# Image Craft

Use this skill to call the user's configured GPT image API and save generated images as local files.

## Capabilities

- Text-to-image generation with `POST /v1/images/generations`.
- Image transformation through the OpenAI-compatible chat endpoint with a data URL image input.
- Optional direct API calls for custom payloads when the bundled script is too narrow.

## Security

The API key is stored in `private_config.json`, which should stay local and should not be pasted into normal responses. If the config is missing, ask the user to provide or restore `IMAGE_CRAFT_API_KEY`.

When reporting results, mention the output image path, model, and prompt summary. Do not print the API key.

## Quick Start

Use the bundled PowerShell script from this skill directory:

```powershell
pwsh -File .\scripts\image_craft.ps1 -Command generate -Prompt "画一只可爱的猫咪" -Output .\outputs\cat.png
```

For an image-to-image transformation:

```powershell
pwsh -File .\scripts\image_craft.ps1 -Command transform -Prompt "改成水彩画风" -InputImage .\input.png -Output .\outputs\watercolor.png
```

Or use the Python script:

```bash
python scripts/image_craft.py generate --prompt "画一只可爱的猫咪" --output outputs/cat.png
python scripts/image_craft.py transform --prompt "改成水彩画风" --input input.png --output outputs/watercolor.png
```

The script reads configuration in this order:

1. `-BaseUrl` script parameter.
2. `IMAGE_CRAFT_API_KEY` and `IMAGE_CRAFT_BASE_URL` environment variables.
3. `private_config.json` in this skill directory.

## Model Selection

Default model: `gpt-image-2`.

Available models:

- `gpt-image-2`: Use by default for normal image generation and straightforward edits.
- `gpt-image-2-vip`: Use when the user's image request is unusually complex, such as multiple subjects with detailed relationships, exact composition constraints, high-fidelity commercial/product output, precise text rendering, elaborate style mixing, or a difficult image transformation.

If the user explicitly requests a model, honor it. Otherwise choose `gpt-image-2` unless the prompt complexity clearly justifies `gpt-image-2-vip`.

## Workflow

1. Create a clear prompt from the user's request. Preserve user-provided names, brands, languages, and style constraints.
2. Choose `generate` for prompt-only requests and `transform` when the user provides an image path or image content to edit.
3. Save outputs to a concrete image path. Use a descriptive filename and create the output directory if needed.
4. Decode the returned `b64_json` or markdown data URL into the requested image file.
5. Tell the user where the image was saved. Include a short note if the API returned a revised prompt.

## API Notes

Default base URL:

```text
https://right.codes/draw
```

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

- If authentication fails, verify `private_config.json` or `IMAGE_CRAFT_API_KEY`.
- The script supports `data[0].b64_json`, `data.url`, direct data URLs, and markdown image links such as `![image](data:image/png;base64,...)` or `![image](https://...)`.
- If the network is blocked by the runtime, request permission to run the command with network access rather than trying to work around the restriction.
