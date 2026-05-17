#!/usr/bin/env python3
"""Search engine for Image Craft skill data."""

from __future__ import annotations

import argparse
import csv
import json
import random
import sys
from pathlib import Path
from typing import Any


def data_dir() -> Path:
    return Path(__file__).resolve().parents[1] / "data"


def load_csv(filename: str) -> list[dict[str, Any]]:
    """Load a CSV file and return list of dicts."""
    filepath = data_dir() / filename
    if not filepath.exists():
        return []
    with open(filepath, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return list(reader)


def search_styles(query: str, limit: int = 10) -> list[dict[str, Any]]:
    """Search styles by keyword."""
    styles = load_csv("styles.csv")
    results = []
    query_lower = query.lower()
    
    for style in styles:
        score = 0
        # Check name matches
        if query_lower in style.get("name_en", "").lower():
            score += 10
        if query_lower in style.get("name_cn", "").lower():
            score += 10
        # Check category
        if query_lower in style.get("category", "").lower():
            score += 5
        # Check keywords
        keywords = style.get("keywords", "").lower()
        if query_lower in keywords:
            score += 8
        # Check description
        if query_lower in style.get("description", "").lower():
            score += 3
        
        if score > 0:
            results.append({"style": style, "score": score})
    
    results.sort(key=lambda x: x["score"], reverse=True)
    return [r["style"] for r in results[:limit]]


def search_prompts(query: str, limit: int = 10) -> list[dict[str, Any]]:
    """Search prompt templates by keyword."""
    prompts = load_csv("prompts.csv")
    results = []
    query_lower = query.lower()
    
    for prompt in prompts:
        score = 0
        # Check name matches
        if query_lower in prompt.get("name", "").lower():
            score += 10
        # Check category
        if query_lower in prompt.get("category", "").lower():
            score += 5
        # Check tags
        tags = prompt.get("tags", "").lower()
        if query_lower in tags:
            score += 8
        # Check template
        if query_lower in prompt.get("template", "").lower():
            score += 3
        
        if score > 0:
            results.append({"prompt": prompt, "score": score})
    
    results.sort(key=lambda x: x["score"], reverse=True)
    return [r["prompt"] for r in results[:limit]]


def search_colors(query: str, limit: int = 10) -> list[dict[str, Any]]:
    """Search color palettes by keyword."""
    colors = load_csv("colors.csv")
    results = []
    query_lower = query.lower()
    
    for color in colors:
        score = 0
        # Check name matches
        if query_lower in color.get("name_en", "").lower():
            score += 10
        if query_lower in color.get("name_cn", "").lower():
            score += 10
        # Check emotion
        if query_lower in color.get("emotion", "").lower():
            score += 5
        # Check use_cases
        if query_lower in color.get("use_cases", "").lower():
            score += 5
        # Check description
        if query_lower in color.get("description", "").lower():
            score += 3
        
        if score > 0:
            results.append({"color": color, "score": score})
    
    results.sort(key=lambda x: x["score"], reverse=True)
    return [r["color"] for r in results[:limit]]


def get_random_styles(count: int = 5) -> list[dict[str, Any]]:
    """Get random style recommendations."""
    styles = load_csv("styles.csv")
    return random.sample(styles, min(count, len(styles)))


def get_random_prompts(count: int = 5) -> list[dict[str, Any]]:
    """Get random prompt templates."""
    prompts = load_csv("prompts.csv")
    return random.sample(prompts, min(count, len(prompts)))


def get_random_colors(count: int = 5) -> list[dict[str, Any]]:
    """Get random color palettes."""
    colors = load_csv("colors.csv")
    return random.sample(colors, min(count, len(colors)))


def get_design_system(query: str) -> dict[str, Any]:
    """Generate a complete design system recommendation."""
    styles = search_styles(query, limit=3)
    prompts = search_prompts(query, limit=3)
    colors = search_colors(query, limit=3)
    
    # If no results, get random recommendations
    if not styles:
        styles = get_random_styles(3)
    if not prompts:
        prompts = get_random_prompts(3)
    if not colors:
        colors = get_random_colors(3)
    
    return {
        "query": query,
        "recommended_styles": styles,
        "recommended_prompts": prompts,
        "recommended_colors": colors
    }


def format_style(style: dict[str, Any]) -> str:
    """Format a style for display."""
    return f"""🎨 {style.get('name_en', '')} ({style.get('name_cn', '')})
   Category: {style.get('category', '')}
   Description: {style.get('description', '')}
   Keywords: {style.get('keywords', '')}
   Prompt Template: {style.get('prompt_template', '')}
   Example: {style.get('example_prompt', '')}
   Difficulty: {style.get('difficulty', '')}"""


def format_prompt(prompt: dict[str, Any]) -> str:
    """Format a prompt template for display."""
    return f"""📝 {prompt.get('name', '')}
   Category: {prompt.get('category', '')}
   Template: {prompt.get('template', '')}
   Variables: {prompt.get('variables', '')}
   Tags: {prompt.get('tags', '')}
   Quality: {'⭐' * int(prompt.get('quality', 1))}"""


def format_color(color: dict[str, Any]) -> str:
    """Format a color palette for display."""
    return f"""🎨 {color.get('name_en', '')} ({color.get('name_cn', '')})
   Primary: {color.get('primary_color', '')}
   Secondary: {color.get('secondary_color', '')}
   Accent: {color.get('accent_color', '')}
   Emotion: {color.get('emotion', '')}
   Use Cases: {color.get('use_cases', '')}"""


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Search engine for Image Craft skill data.")
    parser.add_argument("query", nargs="?", help="Search query")
    parser.add_argument("--domain", choices=["style", "prompt", "color", "all"], default="all",
                        help="Search domain")
    parser.add_argument("--random", action="store_true", help="Get random recommendations")
    parser.add_argument("--design-system", action="store_true", help="Generate complete design system")
    parser.add_argument("-n", "--limit", type=int, default=5, help="Max results")
    parser.add_argument("-f", "--format", choices=["text", "json"], default="text", help="Output format")
    
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    
    if args.random:
        if args.domain == "style" or args.domain == "all":
            styles = get_random_styles(args.limit)
            print("\n🎲 Random Style Recommendations:")
            for style in styles:
                print(format_style(style))
        
        if args.domain == "prompt" or args.domain == "all":
            prompts = get_random_prompts(args.limit)
            print("\n🎲 Random Prompt Templates:")
            for prompt in prompts:
                print(format_prompt(prompt))
        
        if args.domain == "color" or args.domain == "all":
            colors = get_random_colors(args.limit)
            print("\n🎲 Random Color Palettes:")
            for color in colors:
                print(format_color(color))
        
        return 0
    
    if not args.query:
        parser.print_help()
        return 1
    
    if args.design_system:
        system = get_design_system(args.query)
        if args.format == "json":
            print(json.dumps(system, ensure_ascii=False, indent=2))
        else:
            print(f"\n🎯 Design System for: {args.query}")
            print("\n📦 Recommended Styles:")
            for style in system["recommended_styles"]:
                print(format_style(style))
            print("\n📝 Recommended Prompts:")
            for prompt in system["recommended_prompts"]:
                print(format_prompt(prompt))
            print("\n🎨 Recommended Colors:")
            for color in system["recommended_colors"]:
                print(format_color(color))
        return 0
    
    # Search mode
    if args.domain == "style" or args.domain == "all":
        styles = search_styles(args.query, args.limit)
        if styles:
            print(f"\n🔍 Style Results for '{args.query}':")
            for style in styles:
                print(format_style(style))
    
    if args.domain == "prompt" or args.domain == "all":
        prompts = search_prompts(args.query, args.limit)
        if prompts:
            print(f"\n🔍 Prompt Results for '{args.query}':")
            for prompt in prompts:
                print(format_prompt(prompt))
    
    if args.domain == "color" or args.domain == "all":
        colors = search_colors(args.query, args.limit)
        if colors:
            print(f"\n🔍 Color Results for '{args.query}':")
            for color in colors:
                print(format_color(color))
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
