---
name: right-codes-image
description: Generate or edit images through the user's Right Codes GPT image API. Use this skill whenever the user asks an agent to create an image, make a picture, generate artwork, produce a base64/image file from a prompt, transform an existing image with the Right Codes API, or explicitly mentions gpt-image-2, right.codes, Right Code, 文生图, 图片生成, 图片编辑, 改图, 生图, or 画一张图. Prefer this skill over generic image generation when the user wants to use their configured private image API.
---

# Right Codes Image API

Use this skill to call the user's configured Right Codes GPT image API and save generated images as local files for the user.

## Capabilities

- Text-to-image generation with `POST /draw/v1/images/generations`.
- Image transformation through the OpenAI-compatible chat endpoint with a data URL image input.
- Optional direct API calls for custom payloads when the bundled script is too narrow.

## Security

The API key is stored in `private_config.json`, which should stay local and should not be pasted into normal responses. If the config is missing, ask the user to provide or restore `RIGHT_CODES_API_KEY`.

When reporting results, mention the output image path, model, and prompt summary. Do not print the API key.

## Quick Start

Use the bundled PowerShell script from this skill directory:

```powershell
pwsh -File .\scripts\right_codes_image.ps1 -Command generate -Prompt "画一个Sam在抖音直播间带货 Right Code 的图片" -Output .\outputs\sam-right-code.png
```

For an image-to-image transformation:

```powershell
pwsh -File .\scripts\right_codes_image.ps1 -Command transform -Prompt "改成水彩画风" -InputImage .\input.png -Output .\outputs\watercolor.png
```

Or use the Python script:

```bash
python scripts/right_codes_image.py generate --prompt "画一只可爱的猫咪" --output outputs/cat.png
python scripts/right_codes_image.py transform --prompt "改成水彩画风" --input input.png --output outputs/watercolor.png
```

The script reads configuration in this order:

1. `-BaseUrl` script parameter.
2. `RIGHT_CODES_API_KEY` and `RIGHT_CODES_BASE_URL` environment variables.
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
POST /draw/v1/images/generations
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
POST /draw/v1/chat/completions
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

- If authentication fails, verify `private_config.json` or `RIGHT_CODES_API_KEY`.
- The script supports `data[0].b64_json`, `data.url`, direct data URLs, and markdown image links such as `![image](data:image/png;base64,...)` or `![image](https://...)`.
- If the network is blocked by the runtime, request permission to run the command with network access rather than trying to work around the restriction.
