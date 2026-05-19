# Image Craft

> English | [中文](README_CN.md)

A universal skill for AI agents to generate and edit images using OpenAI-compatible GPT image APIs.

## Features

- **Text-to-image generation**: Create images from text prompts
- **Image transformation**: Edit existing images with text instructions
- **Multiple interfaces**: Both PowerShell and Python scripts included
- **OpenAI-compatible API**: Works with Right Codes, OpenAI, Azure, and other compatible endpoints

## Prerequisites

**Before using this skill, you MUST configure:**

1. **API Key** - Required for authentication
2. **Base URL** - Required API endpoint URL

Without these configurations, the skill will not work.

## Installation

### For OpenCode Agents

1. Clone this repository to your skills directory:
   ```bash
   git clone https://github.com/Chelase/image-craft.git ~/.agents/skills/image-craft
   ```

2. Configure your API (see [Configuration](#configuration))

3. The skill will be automatically available when you ask to generate images

### For Other AI Agents

Copy the `SKILL.md` file content to your agent's skill system, and ensure the scripts are accessible.

## Configuration

### Required Settings

Create a `private_config.json` file in the skill root directory:

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

```bash
export IMAGE_CRAFT_MODEL="gpt-image-2"  # Optional, defaults to gpt-image-2
```

**Priority order:**
1. Script parameters (`-Model`, `-BaseUrl`)
2. Environment variables (`IMAGE_CRAFT_MODEL`, `IMAGE_CRAFT_BASE_URL`, `IMAGE_CRAFT_API_KEY`)
3. `private_config.json`
4. Default values (only `model` has default: `gpt-image-2`)

## Usage

### PowerShell

```powershell
# Generate an image
pwsh -File scripts/image_craft.ps1 -Command generate -Prompt "一只可爱的猫咪" -Output outputs/cat.png

# Transform an image
pwsh -File scripts/image_craft.ps1 -Command transform -Prompt "改成水彩画风" -InputImage input.png -Output outputs/watercolor.png

# Generate with a style (by name)
pwsh -File scripts/image_craft.ps1 -Command generate -Prompt "东京街头" -StyleName "赛博朋克" -Output outputs/cyberpunk.png

# Get style suggestions
pwsh -File scripts/image_craft.ps1 -Command suggest -Prompt "赛博朋克城市"

# Get machine-readable style suggestions
pwsh -File scripts/image_craft.ps1 -Command suggest -Prompt "cyberpunk" -Limit 1 -Format json

# Preview the final enhanced prompt without calling the image API
pwsh -File scripts/image_craft.ps1 -Command prompt -Prompt "3d风格未来科幻城市，16:9，城市高空俯瞰" -StyleId 3d -Negative -Format json

# Preview with template variables and a color palette
pwsh -File scripts/image_craft.ps1 -Command prompt -Prompt "东京街头" -Template "urban landscape" -Var city=Tokyo,time_of_day=night -Color "midnight blue" -StyleName cyberpunk -Format json
```

### Python

```bash
# Generate an image
python scripts/image_craft.py generate --prompt "一只可爱的猫咪" --output outputs/cat.png

# Transform an image
python scripts/image_craft.py transform --prompt "改成水彩画风" --input input.png --output outputs/watercolor.png

# Generate with a style (by name or ID)
python scripts/image_craft.py generate --prompt "东京街头" --style-name "赛博朋克" --output outputs/cyberpunk.png

# Include negative prompts (avoids common defects)
python scripts/image_craft.py generate --prompt "东京街头" --style-name "赛博朋克" --negative --output outputs/cyberpunk.png

# Get style suggestions for a prompt
python scripts/image_craft.py suggest "赛博朋克城市"

# Search all local libraries as JSON
python scripts/image_craft.py suggest "赛博朋克未来城市" --domain all --format json

# Preview the final enhanced prompt without generating an image
python scripts/image_craft.py prompt --prompt "3d风格未来科幻城市，16:9，城市高空俯瞰" --style-id 3d --negative --format json

# Generate with a prompt template and color palette
python scripts/image_craft.py generate --prompt "东京街头" --template "urban landscape" --var city="Tokyo" --var "time of day=night" --color "midnight blue" --style-name "cyberpunk" --output outputs/tokyo.png
```

## Style System

The skill includes 54 art styles across 8 categories (traditional, digital, illustration, photography, 3d, special). Styles are auto-enhanced with quality terms and per-style negative prompts.

Use `--style-name` or `--style-id` to apply a style. Category aliases such as `--style-id 3d` resolve to a practical default style (`blender-render`) for professional 3D rendering. Use `suggest` command to explore styles, prompt templates, and color palettes from the local `data/*.csv` libraries.

The unified search backend supports:

- `--domain style|prompt|color|all`
- `--design-system` for combined style + template + palette recommendations
- `--random` for random recommendations
- `--format json` for machine-readable output

## Prompt Enhancement

All generation-oriented commands automatically normalize common visual descriptors such as `16:9` into professional composition phrases, inject quality terms (`masterpiece, best quality, high resolution, detailed, professional, trending on artstation`), and apply style templates. Pass `--negative` to include negative prompts that avoid common artifacts (`lowres, bad anatomy, blurry, etc.`). Use `prompt` to preview the final enhanced prompt without calling the image API.

## Models

| Model | Description |
|-------|-------------|
| `gpt-image-2` | Default model for standard image generation and edits |
| `gpt-image-2-vip` | For complex prompts with multiple subjects, precise text rendering, or elaborate styles |

## API Endpoints

### Text-to-Image

```
POST /v1/images/generations
```

Request body:
```json
{
  "model": "gpt-image-2",
  "prompt": "your prompt here"
}
```

### Image Transformation

```
POST /v1/chat/completions
```

Request body:
```json
{
  "model": "gpt-image-2",
  "messages": [
    {
      "role": "user",
      "content": [
        {"type": "text", "text": "your instruction"},
        {"type": "image_url", "image_url": {"url": "data:image/png;base64,..."}}
      ]
    }
  ]
}
```

## Troubleshooting

- **Missing API key or base URL**: Verify `private_config.json` or environment variables are set correctly.
- **Authentication fails**: Check if `IMAGE_CRAFT_API_KEY` is correct and not expired.
- **Connection fails**: Verify `IMAGE_CRAFT_BASE_URL` is correct and accessible.

## Security

- Never commit your `private_config.json` file
- The `.gitignore` is configured to exclude this file
- Use environment variables in production environments

## License

MIT

## Support

For issues or questions, please open an issue on GitHub.
