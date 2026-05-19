#!/usr/bin/env python3
"""Prompt enhancer for Image Craft - auto-enhance, inject quality keywords, and generate negative prompts."""

from __future__ import annotations

import csv
import re
import sys
from pathlib import Path
from typing import Any

from search import search_styles


# Quality keywords injected to improve model output
QUALITY_TERMS = [
    "masterpiece", "best quality", "high resolution", "detailed",
    "professional", "trending on artstation",
]
QUALITY_NEGATIVE = [
    "lowres", "bad anatomy", "bad hands", "missing fingers",
    "extra digits", "fewer digits", "cropped", "worst quality",
    "low quality", "jpeg artifacts", "blurry", "duplicate",
]


def data_dir() -> Path:
    return Path(__file__).resolve().parents[1] / "data"


def load_csv(filename: str) -> list[dict[str, Any]]:
    filepath = data_dir() / filename
    if not filepath.exists():
        return []
    with open(filepath, "r", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def load_styles() -> list[dict[str, Any]]:
    return load_csv("styles.csv")


def load_prompts() -> list[dict[str, Any]]:
    return load_csv("prompts.csv")


def load_colors() -> list[dict[str, Any]]:
    return load_csv("colors.csv")


# ----------------------------------------------------------------------
# Style detection
# ----------------------------------------------------------------------

STYLE_KEYWORDS = {
    "traditional": ["油画", "水彩", "素描", "版画", "国画", "oil", "watercolor", "sketch", "print", "ink wash", "woodcut"],
    "digital": ["像素", "赛博", "蒸汽波", "故障", "pixel", "cyberpunk", "vaporwave", "glitch", "digital"],
    "illustration": ["扁平", "等距", "日系", "美漫", "儿童", "flat", "isometric", "anime", "comic", "children"],
    "photography": ["胶片", "宝丽来", "黑白", "长曝光", "微距", "film", "polaroid", "black and white", "long exposure", "macro"],
    "3d": ["低多边形", "体素", "C4D", "blender", "low poly", "voxel", "3d render"],
    "special": ["双重曝光", "光绘", "红外", "移轴", "double exposure", "light painting", "infrared", "tilt-shift"],
}


def detect_style_category(prompt: str) -> str | None:
    """Detect which style category a prompt mentions."""
    prompt_lower = prompt.lower()
    for category, keywords in STYLE_KEYWORDS.items():
        for kw in keywords:
            if kw.lower() in prompt_lower:
                return category
    return None


# ----------------------------------------------------------------------
# Simple prompt detection
# ----------------------------------------------------------------------

def is_simple_prompt(prompt: str) -> bool:
    """Return True if the prompt is short / lacks technical descriptors."""
    # Strip placeholder syntax like {subject}
    stripped = re.sub(r"\{[^}]+\}", "", prompt).strip()
    words = stripped.split()
    if len(words) <= 8:
        return True
    technical = [
        "style", "lighting", "composition", "perspective", "texture",
        "color palette", "depth of field", "焦距", "光圈", "风格",
    ]
    return not any(t in stripped.lower() for t in technical)


def tokenize(text: str) -> set[str]:
    """Return a set of searchable tokens from text (handles CJK as characters)."""
    # Treat CJK characters as individual tokens; split ASCII on spaces/punctuation
    text_lower = text.lower()
    # Split ASCII text normally, keep each CJK char as its own token
    tokens: set[str] = set()
    current = ""
    for ch in text_lower:
        if "\u4e00" <= ch <= "\u9fff":
            if current:
                tokens.update(current.split())
                current = ""
            tokens.add(ch)
        else:
            current += ch
    if current:
        tokens.update(current.split())
    # Remove empty tokens
    tokens.discard("")
    return tokens


# ----------------------------------------------------------------------
# Enhancement
# ----------------------------------------------------------------------

def build_style_enhancement(style: dict[str, Any]) -> str:
    """Build style modifier string from a style dict."""
    parts = []

    template = style.get("prompt_template", "")
    if template:
        parts.append(template)

    keywords = style.get("keywords", "")
    if keywords:
        parts.append(f"keywords: {keywords}")

    return ", ".join(parts)


def suggest_styles_for_prompt(prompt: str, limit: int = 3) -> list[dict[str, Any]]:
    """Suggest styles via the unified Phase 2 search backend."""
    category = detect_style_category(prompt)
    results = search_styles(prompt, limit=limit, category=category)
    if results:
        return results
    # Broaden intentionally when the category hint was too restrictive.
    return search_styles(prompt, limit=limit, category=None)


def apply_style_enhancement(prompt: str, style: dict[str, Any]) -> str:
    """Merge the user's prompt with style enhancement terms."""
    template = style.get("prompt_template", "")
    if not template:
        return prompt

    # Replace {subject} placeholder with actual prompt
    subject = prompt.strip().rstrip(",.。")
    if subject.lower().startswith(("a ", "an ")):
        template = template.replace("A {subject}", "{subject}", 1)
        template = template.replace("An {subject}", "{subject}", 1)
    enhanced = template.replace("{subject}", subject)
    return enhanced


# ----------------------------------------------------------------------
# Quality injection
# ----------------------------------------------------------------------

QUALITY_POSITIVE = ", ".join(QUALITY_TERMS)

QUALITY_NEGATIVE_STR = ", ".join(QUALITY_NEGATIVE)


def inject_quality(prompt: str) -> str:
    """Append quality-positive terms to the prompt."""
    return f"{prompt.strip()}, {QUALITY_POSITIVE}"


def generate_negative_prompt(style: dict[str, Any] | None = None) -> str:
    """Generate a negative prompt.

    Always include general quality negatives.
    If a style is provided, also append the style's negative_prompt column.
    """
    parts = [QUALITY_NEGATIVE_STR]
    if style:
        style_neg = style.get("negative_prompt", "").strip()
        if style_neg:
            parts.append(style_neg)
    return ", ".join(parts)


# ----------------------------------------------------------------------
# Full enhancement pipeline
# ----------------------------------------------------------------------

def enhance(
    prompt: str,
    style_id: str | None = None,
    style_dict: dict[str, Any] | None = None,
    include_negative: bool = False,
    inject_quality_terms: bool = True,
) -> dict[str, str]:
    """Fully enhance a user prompt.

    Returns a dict with keys:
      - original_prompt
      - enhanced_prompt
      - negative_prompt
      - style_id
      - style_name_cn
    """
    # Determine style
    style: dict[str, Any] | None = None
    style_name_cn = ""
    detected_style_id = ""

    if style_dict is not None:
        style = style_dict
        detected_style_id = style.get("id", "")
        style_name_cn = style.get("name_cn", "")
    elif style_id:
        styles = load_styles()
        for s in styles:
            if s.get("id", "") == style_id:
                style = s
                detected_style_id = style_id
                style_name_cn = s.get("name_cn", "")
                break

    # Apply style enhancement
    enhanced = prompt
    if style:
        enhanced = apply_style_enhancement(prompt, style)

    # Inject quality terms
    if inject_quality_terms:
        enhanced = inject_quality(enhanced)

    # Negative prompt
    negative = generate_negative_prompt(style) if include_negative else ""

    return {
        "original_prompt": prompt,
        "enhanced_prompt": enhanced,
        "negative_prompt": negative,
        "style_id": detected_style_id,
        "style_name_cn": style_name_cn,
        "is_simple": is_simple_prompt(prompt),
    }


# ----------------------------------------------------------------------
# CLI
# ----------------------------------------------------------------------

def build_parser():
    import argparse
    parser = argparse.ArgumentParser(description="Enhance image generation prompts.")
    parser.add_argument("prompt", help="The user's prompt")
    parser.add_argument("--style-id", help="Style ID to apply (e.g. cyberpunk)")
    parser.add_argument("--style-name", help="Style name to search and auto-apply")
    parser.add_argument("--negative", action="store_true", help="Include negative prompt in output")
    parser.add_argument("--no-quality", action="store_true", help="Skip quality term injection")
    parser.add_argument("--suggest", action="store_true", help="Suggest styles for the prompt")
    parser.add_argument("-f", "--format", choices=["text", "json"], default="text")
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    style_dict = None
    style_id = args.style_id or ""

    if args.style_name:
        suggestions = suggest_styles_for_prompt(args.style_name, limit=1)
        if suggestions:
            style_dict = suggestions[0]
            style_id = style_dict.get("id", "")

    result = enhance(
        prompt=args.prompt,
        style_id=style_id or None,
        style_dict=style_dict,
        include_negative=args.negative,
        inject_quality_terms=not args.no_quality,
    )

    if args.format == "json":
        import json
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0

    print("=" * 60)
    print("PROMPT ENHANCEMENT REPORT")
    print("=" * 60)
    print(f"Original:  {result['original_prompt']}")
    print(f"Enhanced:  {result['enhanced_prompt']}")
    if result["negative_prompt"]:
        print(f"Negative:  {result['negative_prompt']}")
    print(f"Style:     {result['style_name_cn']} ({result['style_id']})")
    print(f"Detected as simple prompt: {result['is_simple']}")
    print("=" * 60)

    if args.suggest:
        suggestions = suggest_styles_for_prompt(args.prompt)
        print(f"\nStyle suggestions for this prompt ({len(suggestions)} found):")
        for i, s in enumerate(suggestions, 1):
            print(f"  {i}. {s.get('name_cn', '')} ({s.get('name_en', '')}) - {s.get('category', '')}")
            print(f"     Keywords: {s.get('keywords', '')}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
