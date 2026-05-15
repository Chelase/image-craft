# Image Craft

> English | [中文](README_CN.md)

A universal skill for AI agents to generate and edit images using OpenAI-compatible GPT image APIs.

## Features

- **Text-to-image generation**: Create images from text prompts
- **Image transformation**: Edit existing images with text instructions
- **Multiple interfaces**: Both PowerShell and Python scripts included
- **OpenAI-compatible API**: Works with Right Codes, OpenAI, Azure, and other compatible endpoints

## Installation

### For OpenCode Agents

1. Clone this repository to your skills directory:
   ```bash
   git clone https://github.com/Chelase/image-craft.git ~/.agents/skills/image-craft
   ```

2. Configure your API key (see [Configuration](#configuration))

3. The skill will be automatically available when you ask to generate images

### For Other AI Agents

Copy the `SKILL.md` file content to your agent's skill system, and ensure the scripts are accessible.

## Configuration

Create a `private_config.json` file in the skill root directory:

```json
{
  "api_key": "YOUR_API_KEY_HERE",
  "base_url": "https://right.codes/draw",
  "model": "gpt-image-2"
}
```

Or set environment variables:

```bash
export IMAGE_CRAFT_API_KEY="your-api-key"
export IMAGE_CRAFT_BASE_URL="https://right.codes/draw"  # Optional
export IMAGE_CRAFT_MODEL="gpt-image-2"                  # Optional
```

**Priority order:**
1. Script parameters (`-Model`, `-BaseUrl`)
2. Environment variables (`IMAGE_CRAFT_MODEL`, `IMAGE_CRAFT_BASE_URL`)
3. `private_config.json`
4. Default values (`gpt-image-2`, `https://right.codes/draw`)

## Usage

### PowerShell

```powershell
# Generate an image
pwsh -File scripts/image_craft.ps1 -Command generate -Prompt "一只可爱的猫咪" -Output outputs/cat.png

# Transform an image
pwsh -File scripts/image_craft.ps1 -Command transform -Prompt "改成水彩画风" -InputImage input.png -Output outputs/watercolor.png
```

### Python

```bash
# Generate an image
python scripts/image_craft.py generate --prompt "一只可爱的猫咪" --output outputs/cat.png

# Transform an image
python scripts/image_craft.py transform --prompt "改成水彩画风" --input input.png --output outputs/watercolor.png
```

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

## Security

- Never commit your `private_config.json` file
- The `.gitignore` is configured to exclude this file
- Use environment variables in production environments

## License

MIT

## Support

For issues or questions, please open an issue on GitHub.
