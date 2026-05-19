#!/usr/bin/env python3
"""Call the Image Craft API and save the returned image."""

from __future__ import annotations

import argparse
import base64
import json
import mimetypes
import os
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path

from prompts_enhancer import enhance, is_simple_prompt, load_styles
from search import (
    format_color,
    format_prompt,
    format_style,
    get_design_system,
    get_random_colors,
    get_random_prompts,
    get_random_styles,
    search_colors,
    search_prompts,
    search_styles,
)

DEFAULT_MODEL = "gpt-image-2"

CATEGORY_DEFAULT_STYLE_IDS = {
    "3d": "blender-render",
    "digital": "cyberpunk",
    "photography": "film-noir",
    "illustration": "isometric",
    "traditional": "oil-painting",
    "effect": "double-exposure",
    "special": "double-exposure",
}


def skill_dir() -> Path:
    return Path(__file__).resolve().parents[1]


def load_config() -> dict:
    config_path = skill_dir() / "private_config.json"
    config: dict = {}
    if config_path.exists():
        config = json.loads(config_path.read_text(encoding="utf-8"))

    base_url = os.environ.get("IMAGE_CRAFT_BASE_URL") or config.get("base_url")
    api_key = os.environ.get("IMAGE_CRAFT_API_KEY") or config.get("api_key")
    model = os.environ.get("IMAGE_CRAFT_MODEL") or config.get("model") or DEFAULT_MODEL

    if not base_url:
        raise SystemExit(
            "Missing base URL. Set IMAGE_CRAFT_BASE_URL, or add base_url to private_config.json."
        )

    if not api_key:
        raise SystemExit(
            "Missing API key. Set IMAGE_CRAFT_API_KEY or add api_key to private_config.json."
        )

    return {"base_url": base_url.rstrip("/"), "api_key": api_key, "model": model}


def post_json(url: str, payload: dict, api_key: str) -> dict:
    data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=180) as response:
            body = response.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        error_body = exc.read().decode("utf-8", errors="replace")
        raise SystemExit(f"API request failed with HTTP {exc.code}: {error_body}") from exc
    except urllib.error.URLError as exc:
        raise SystemExit(f"API request failed: {exc}") from exc

    try:
        return json.loads(body)
    except json.JSONDecodeError as exc:
        raise SystemExit(f"API returned non-JSON response: {body[:500]}") from exc


def image_data_url(path: Path) -> str:
    mime_type = mimetypes.guess_type(path.name)[0] or "image/png"
    encoded = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:{mime_type};base64,{encoded}"


def extract_image_b64(response: dict) -> tuple[str, str | None]:
    data = response.get("data")
    if isinstance(data, list) and data:
        first = data[0]
        if isinstance(first, dict) and first.get("b64_json"):
            return first["b64_json"], first.get("revised_prompt")

    choices = response.get("choices")
    if isinstance(choices, list) and choices:
        message = choices[0].get("message", {}) if isinstance(choices[0], dict) else {}
        content = message.get("content") if isinstance(message, dict) else None
        if isinstance(content, str):
            match = re.search(r"data:image/[a-zA-Z0-9.+-]+;base64,([A-Za-z0-9+/=\r\n]+)", content)
            if match:
                return re.sub(r"\s+", "", match.group(1)), None

    raise SystemExit("Could not find image base64 in API response.")


def save_image(image_b64: str, output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_bytes(base64.b64decode(image_b64))


def resolve_style(style_name: str | None = None, style_id: str | None = None) -> dict | None:
    """Resolve a style by name or ID, returning the style dict or None."""
    if not style_name and not style_id:
        return None

    styles = load_styles()
    if style_id:
        normalized_style_id = style_id.lower().strip()
        for s in styles:
            if s.get("id", "") == normalized_style_id:
                return s
        default_style_id = CATEGORY_DEFAULT_STYLE_IDS.get(normalized_style_id)
        if default_style_id:
            for s in styles:
                if s.get("id", "") == default_style_id:
                    return s
    if style_name:
        # Search by name (supports Chinese and English)
        name_lower = style_name.lower()
        default_style_id = CATEGORY_DEFAULT_STYLE_IDS.get(name_lower)
        if default_style_id:
            for s in styles:
                if s.get("id", "") == default_style_id:
                    return s
        for s in styles:
            if name_lower in s.get("name_cn", "").lower() or name_lower in s.get("name_en", "").lower():
                return s
        # Fuzzy match via the unified Phase 2 search backend.
        matches = search_styles(style_name, limit=1)
        if matches:
            return matches[0]
    return None


def parse_vars(values: list[str] | None) -> dict[str, str]:
    """Parse repeated key=value CLI arguments."""
    parsed: dict[str, str] = {}
    for value in values or []:
        if "=" not in value:
            raise SystemExit(f"Invalid --var value '{value}'. Use key=value.")
        key, raw = value.split("=", 1)
        key = key.strip()
        if not key:
            raise SystemExit(f"Invalid --var value '{value}'. Variable name is empty.")
        parsed[key] = raw.strip()
    return parsed


def resolve_template(template: str | None) -> dict | None:
    """Resolve a prompt template by ID/name/query using search.py."""
    if not template:
        return None
    matches = search_prompts(template, limit=10)
    template_lower = template.lower()
    for match in matches:
        if template_lower in {match.get("id", "").lower(), match.get("name", "").lower()}:
            return match
    return matches[0] if matches else None


def render_template(template: dict, prompt: str, variables: dict[str, str]) -> str:
    """Render a prompt template, using the prompt as the default subject-like value."""
    rendered = template.get("template", "")
    if not rendered:
        return prompt

    variable_names = [name.strip() for name in template.get("variables", "").split(",") if name.strip()]
    for name in variable_names:
        value = variables.get(name)
        if value is None:
            value = variables.get(name.replace(" ", "_"))
        if value is None:
            value = variables.get(name.replace(" ", "-"))
        if value is None and name in {"subject", "product", "location", "city", "items"}:
            value = prompt
        if value is not None:
            rendered = rendered.replace("{" + name + "}", value)
    return rendered


def resolve_color(color: str | None) -> dict | None:
    """Resolve a color palette query using search.py."""
    if not color:
        return None
    matches = search_colors(color, limit=1)
    return matches[0] if matches else None


def apply_template_and_color(args: argparse.Namespace) -> tuple[str, dict | None, dict | None]:
    """Build the base prompt from a template and optional color palette."""
    variables = parse_vars(getattr(args, "var", None))
    template = resolve_template(getattr(args, "template", None))
    color = resolve_color(getattr(args, "color", None))

    prompt = args.prompt
    if template:
        prompt = render_template(template, prompt, variables)
    if color and color.get("prompt_description"):
        prompt = f"{prompt}, {color['prompt_description']}"

    return prompt, template, color


def prepare_prompt(args: argparse.Namespace) -> tuple[str, str | None, dict | None]:
    """Enhance the prompt and return (final_prompt, negative_prompt, style_dict)."""
    style = resolve_style(style_name=args.style_name, style_id=args.style_id)
    prompt, _, _ = apply_template_and_color(args)

    result = enhance(
        prompt=prompt,
        style_id=args.style_id,
        style_dict=style,
        include_negative=args.negative,
        inject_quality_terms=not args.no_quality,
    )

    return result["enhanced_prompt"], result["negative_prompt"] if args.negative else None, style


def generate(args: argparse.Namespace) -> None:
    config = load_config()
    model = args.model or config["model"]

    enhanced_prompt, negative_prompt, style = prepare_prompt(args)
    _, template, color = apply_template_and_color(args)

    payload: dict = {"model": model, "prompt": enhanced_prompt}
    if negative_prompt:
        payload["negative_prompt"] = negative_prompt

    response = post_json(
        f"{config['base_url']}/v1/images/generations",
        payload,
        config["api_key"],
    )
    image_b64, revised_prompt = extract_image_b64(response)
    save_image(image_b64, args.output)

    output_info = {
        "output": str(args.output),
        "model": model,
        "revised_prompt": revised_prompt,
    }
    if style:
        output_info["style_id"] = style.get("id", "")
        output_info["style_name_cn"] = style.get("name_cn", "")
    if template:
        output_info["template_id"] = template.get("id", "")
    if color:
        output_info["color_id"] = color.get("id", "")
    if negative_prompt:
        output_info["negative_prompt"] = negative_prompt

    print(json.dumps(output_info, ensure_ascii=False))


def transform(args: argparse.Namespace) -> None:
    config = load_config()
    model = args.model or config["model"]

    enhanced_prompt, negative_prompt, style = prepare_prompt(args)
    _, template, color = apply_template_and_color(args)

    payload: dict = {
        "model": model,
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": enhanced_prompt},
                    {"type": "image_url", "image_url": {"url": image_data_url(args.input)}},
                ],
            }
        ],
    }
    if negative_prompt:
        payload["negative_prompt"] = negative_prompt

    response = post_json(
        f"{config['base_url']}/v1/chat/completions",
        payload,
        config["api_key"],
    )
    image_b64, revised_prompt = extract_image_b64(response)
    save_image(image_b64, args.output)

    output_info = {
        "output": str(args.output),
        "model": model,
        "revised_prompt": revised_prompt,
    }
    if style:
        output_info["style_id"] = style.get("id", "")
        output_info["style_name_cn"] = style.get("name_cn", "")
    if template:
        output_info["template_id"] = template.get("id", "")
    if color:
        output_info["color_id"] = color.get("id", "")
    if negative_prompt:
        output_info["negative_prompt"] = negative_prompt

    print(json.dumps(output_info, ensure_ascii=False))


def suggest(args: argparse.Namespace) -> None:
    """Print search suggestions without generating an image."""
    if args.design_system:
        print(json.dumps(get_design_system(args.prompt, category=args.category), ensure_ascii=False, indent=2))
        return

    if args.random:
        output = {}
        if args.domain in {"style", "all"}:
            output["styles"] = get_random_styles(args.limit)
        if args.domain in {"prompt", "all"}:
            output["prompts"] = get_random_prompts(args.limit)
        if args.domain in {"color", "all"}:
            output["colors"] = get_random_colors(args.limit)
    else:
        output = {}
        if args.domain in {"style", "all"}:
            output["styles"] = search_styles(args.prompt, limit=args.limit, category=args.category)
        if args.domain in {"prompt", "all"}:
            output["prompts"] = search_prompts(args.prompt, limit=args.limit, category=args.category)
        if args.domain in {"color", "all"}:
            output["colors"] = search_colors(args.prompt, limit=args.limit, category=args.category)

    if args.format == "json":
        print(json.dumps(output, ensure_ascii=False, indent=2))
        return

    print(f"Suggestions for: {args.prompt}")
    print(f"(Detected as {'simple' if is_simple_prompt(args.prompt) else 'detailed'} prompt)\n")
    for style in output.get("styles", []):
        print(format_style(style))
    for prompt in output.get("prompts", []):
        print(format_prompt(prompt))
    for color in output.get("colors", []):
        print(format_color(color))


def preview_prompt(args: argparse.Namespace) -> None:
    """Print the final prompt payload without calling the image API."""
    enhanced_prompt, negative_prompt, style = prepare_prompt(args)
    prompt, template, color = apply_template_and_color(args)
    output = {
        "original_prompt": args.prompt,
        "base_prompt": prompt,
        "enhanced_prompt": enhanced_prompt,
        "negative_prompt": negative_prompt or "",
    }
    if style:
        output["style_id"] = style.get("id", "")
        output["style_name_cn"] = style.get("name_cn", "")
        output["style_name_en"] = style.get("name_en", "")
    if template:
        output["template_id"] = template.get("id", "")
        output["template_name"] = template.get("name", "")
    if color:
        output["color_id"] = color.get("id", "")
        output["color_name"] = color.get("name", "")

    if args.format == "json":
        print(json.dumps(output, ensure_ascii=False, indent=2))
        return

    print("=" * 60)
    print("PROMPT PREVIEW")
    print("=" * 60)
    print(f"Original: {output['original_prompt']}")
    print(f"Base:     {output['base_prompt']}")
    print(f"Final:    {output['enhanced_prompt']}")
    if output["negative_prompt"]:
        print(f"Negative: {output['negative_prompt']}")
    if style:
        print(f"Style:    {output.get('style_name_cn', '')} ({output.get('style_id', '')})")
    print("=" * 60)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Generate or transform images with the Image Craft API.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # ----- generate -----
    gen = subparsers.add_parser("generate", help="Generate an image from text.")
    gen.add_argument("--prompt", required=True)
    gen.add_argument("--output", required=True, type=Path)
    gen.add_argument("--model", default=None)
    gen.add_argument("--style-id", default=None, help="Style ID to apply (e.g. cyberpunk)")
    gen.add_argument("--style-name", default=None, help="Style name to search and auto-apply")
    gen.add_argument("--template", default=None, help="Prompt template ID/name/query to render before generation")
    gen.add_argument("--var", action="append", default=[], help="Template variable in key=value form; repeat as needed")
    gen.add_argument("--color", default=None, help="Color palette name/query to append to the prompt")
    gen.add_argument("--negative", action="store_true", help="Include negative prompt")
    gen.add_argument("--no-quality", action="store_true", help="Skip quality term injection")
    gen.set_defaults(func=generate)

    # ----- transform -----
    trans = subparsers.add_parser("transform", help="Transform an input image with a text instruction.")
    trans.add_argument("--prompt", required=True)
    trans.add_argument("--input", required=True, type=Path)
    trans.add_argument("--output", required=True, type=Path)
    trans.add_argument("--model", default=None)
    trans.add_argument("--style-id", default=None)
    trans.add_argument("--style-name", default=None)
    trans.add_argument("--template", default=None)
    trans.add_argument("--var", action="append", default=[])
    trans.add_argument("--color", default=None)
    trans.add_argument("--negative", action="store_true")
    trans.add_argument("--no-quality", action="store_true")
    trans.set_defaults(func=transform)

    # ----- suggest -----
    sugg = subparsers.add_parser("suggest", help="Suggest styles for a prompt without generating.")
    sugg.add_argument("prompt", help="The prompt to get style suggestions for")
    sugg.add_argument("-n", "--limit", type=int, default=5, help="Max suggestions")
    sugg.add_argument("--domain", choices=["style", "prompt", "color", "all"], default="style")
    sugg.add_argument("--category", default=None)
    sugg.add_argument("--design-system", action="store_true", help="Return style + prompt + color recommendations")
    sugg.add_argument("--random", action="store_true", help="Return random recommendations")
    sugg.add_argument("-f", "--format", choices=["text", "json"], default="text")
    sugg.set_defaults(func=suggest)

    # ----- prompt preview -----
    prev = subparsers.add_parser("prompt", help="Preview the enhanced prompt without generating an image.")
    prev.add_argument("--prompt", required=True)
    prev.add_argument("--style-id", default=None, help="Style ID or category to apply (e.g. blender-render or 3d)")
    prev.add_argument("--style-name", default=None, help="Style name or category to search and auto-apply")
    prev.add_argument("--template", default=None, help="Prompt template ID/name/query to render before preview")
    prev.add_argument("--var", action="append", default=[], help="Template variable in key=value form; repeat as needed")
    prev.add_argument("--color", default=None, help="Color palette name/query to append to the prompt")
    prev.add_argument("--negative", action="store_true", help="Include negative prompt")
    prev.add_argument("--no-quality", action="store_true", help="Skip quality term injection")
    prev.add_argument("-f", "--format", choices=["text", "json"], default="text")
    prev.set_defaults(func=preview_prompt)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)
    return 0


if __name__ == "__main__":
    sys.exit(main())
