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


DEFAULT_MODEL = "gpt-image-2"
DEFAULT_BASE_URL = "https://right.codes/gpt"


def skill_dir() -> Path:
    return Path(__file__).resolve().parents[1]


def load_config() -> dict:
    config_path = skill_dir() / "private_config.json"
    config: dict = {}
    if config_path.exists():
        config = json.loads(config_path.read_text(encoding="utf-8"))

    base_url = os.environ.get("IMAGE_CRAFT_BASE_URL") or config.get("base_url") or DEFAULT_BASE_URL
    api_key = os.environ.get("IMAGE_CRAFT_API_KEY") or config.get("api_key")

    if not api_key:
        raise SystemExit(
            "Missing API key. Set IMAGE_CRAFT_API_KEY or create private_config.json in the skill directory."
        )

    return {"base_url": base_url.rstrip("/"), "api_key": api_key}


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


def generate(args: argparse.Namespace) -> None:
    config = load_config()
    payload = {"model": args.model, "prompt": args.prompt}
    response = post_json(
        f"{config['base_url']}/v1/images/generations",
        payload,
        config["api_key"],
    )
    image_b64, revised_prompt = extract_image_b64(response)
    save_image(image_b64, args.output)
    print(json.dumps({"output": str(args.output), "revised_prompt": revised_prompt}, ensure_ascii=False))


def transform(args: argparse.Namespace) -> None:
    config = load_config()
    payload = {
        "model": args.model,
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": args.prompt},
                    {"type": "image_url", "image_url": {"url": image_data_url(args.input)}},
                ],
            }
        ],
    }
    response = post_json(
        f"{config['base_url']}/v1/chat/completions",
        payload,
        config["api_key"],
    )
    image_b64, revised_prompt = extract_image_b64(response)
    save_image(image_b64, args.output)
    print(json.dumps({"output": str(args.output), "revised_prompt": revised_prompt}, ensure_ascii=False))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Generate or transform images with the Image Craft API.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    generate_parser = subparsers.add_parser("generate", help="Generate an image from text.")
    generate_parser.add_argument("--prompt", required=True)
    generate_parser.add_argument("--output", required=True, type=Path)
    generate_parser.add_argument("--model", default=DEFAULT_MODEL)
    generate_parser.set_defaults(func=generate)

    transform_parser = subparsers.add_parser("transform", help="Transform an input image with a text instruction.")
    transform_parser.add_argument("--prompt", required=True)
    transform_parser.add_argument("--input", required=True, type=Path)
    transform_parser.add_argument("--output", required=True, type=Path)
    transform_parser.add_argument("--model", default=DEFAULT_MODEL)
    transform_parser.set_defaults(func=transform)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)
    return 0


if __name__ == "__main__":
    sys.exit(main())
