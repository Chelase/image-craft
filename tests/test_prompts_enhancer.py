import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from prompts_enhancer import enhance, normalize_visual_prompt, style_migration_instruction  # noqa: E402
from image_craft import build_batch_plan, build_parser, prepare_prompt, render_template, resolve_style_mix  # noqa: E402


class PromptEnhancerTests(unittest.TestCase):
    def test_3d_category_alias_resolves_to_blender_render(self) -> None:
        result = enhance("future city, 16:9, aerial view", style_id="3d", include_negative=True)

        self.assertEqual(result["style_id"], "blender-render")
        self.assertIn("Blender 3D render style", result["enhanced_prompt"])
        self.assertIn("16:9 widescreen cinematic aspect ratio", result["enhanced_prompt"])
        self.assertIn("cartoon, flat, 2d", result["negative_prompt"])

    def test_chinese_scene_terms_are_normalized_before_template_insertion(self) -> None:
        prompt = (
            "3d风格未来科幻城市，宏大场景，飞行汽车，16:9，"
            "傍晚蓝调时分，阴天，高楼林立，雾蒙蒙，灰色天空，"
            "一望无际，半空场景，城市高空俯瞰，霓虹灯占比不多，城市灯光"
        )

        result = enhance(prompt, style_id="3d", include_negative=True)

        self.assertIn("futuristic sci-fi city", result["enhanced_prompt"])
        self.assertIn("subtle restrained neon accents", result["enhanced_prompt"])
        self.assertIn("16:9 widescreen cinematic aspect ratio, in Blender", result["enhanced_prompt"])
        self.assertNotIn("3D render style, in Blender 3D render style", result["enhanced_prompt"])

    def test_generic_style_phrase_can_be_suppressed(self) -> None:
        prompt = "3d风格未来科幻城市，16:9"

        normalized = normalize_visual_prompt(prompt, suppress_generic_style=True)

        self.assertEqual(
            normalized,
            "futuristic sci-fi city, 16:9 widescreen cinematic aspect ratio",
        )

    def test_template_variables_accept_shell_safe_aliases(self) -> None:
        template = {
            "template": "An urban landscape of {city}, {time of day}",
            "variables": "city,time of day",
        }

        rendered = render_template(template, "Tokyo street", {"city": "Tokyo", "time_of_day": "night"})

        self.assertEqual(rendered, "An urban landscape of Tokyo, night")

    def test_style_mix_merges_weighted_styles_and_negatives(self) -> None:
        style_mix = resolve_style_mix("cyberpunk:0.7,blender-render:0.3")

        result = enhance(
            "future city, 16:9",
            style_dicts=style_mix,
            include_negative=True,
        )

        self.assertEqual(result["style_id"], "cyberpunk,blender-render")
        self.assertIn("cyberpunk style", result["enhanced_prompt"])
        self.assertIn("blended style mix", result["enhanced_prompt"])
        self.assertIn("70% Cyberpunk influence", result["enhanced_prompt"])
        self.assertIn("30% Blender Render influence", result["enhanced_prompt"])
        self.assertIn("natural", result["negative_prompt"])
        self.assertIn("cartoon", result["negative_prompt"])

    def test_style_mix_resolves_category_aliases(self) -> None:
        style_mix = resolve_style_mix("digital:2,3d:1")

        self.assertEqual([style.get("id") for style, _ in style_mix], ["cyberpunk", "blender-render"])

    def test_style_migration_instruction_preserves_source_with_partial_strength(self) -> None:
        style = resolve_style_mix("watercolor:1")[0][0]

        instruction = style_migration_instruction("preserve the portrait", style, 0.35)

        self.assertIn("preserve the portrait", instruction)
        self.assertIn("target style: Watercolor", instruction)
        self.assertIn("style migration strength: 35%", instruction)
        self.assertIn("preserve 65% of the source image", instruction)
        self.assertIn("watercolor,soft,translucent,flowing", instruction)

    def test_prompt_preview_accepts_style_migration_strength(self) -> None:
        args = build_parser().parse_args([
            "prompt",
            "--prompt", "preserve the portrait",
            "--style-name", "watercolor",
            "--style-strength", "0.35",
            "--format", "json",
        ])

        enhanced_prompt, _, style, style_mix = prepare_prompt(args)

        self.assertEqual(style_mix, [])
        self.assertEqual(style.get("id"), "watercolor")
        self.assertIn("style migration strength: 35%", enhanced_prompt)
        self.assertIn("preserve 65% of the source image", enhanced_prompt)

    def test_prompt_preview_rejects_out_of_range_style_migration_strength(self) -> None:
        args = build_parser().parse_args([
            "prompt",
            "--prompt", "preserve the portrait",
            "--style-name", "watercolor",
            "--style-strength", "1.5",
        ])

        with self.assertRaises(SystemExit):
            prepare_prompt(args)

    def test_batch_plan_builds_style_variants_with_ab_labels(self) -> None:
        args = build_parser().parse_args([
            "batch",
            "--prompt", "future city",
            "--styles", "cyberpunk,watercolor",
            "--output-dir", "outputs/batch",
            "--ab-label", "A",
            "--ab-label", "B",
            "--dry-run",
            "--format", "json",
        ])

        plan = build_batch_plan(args)

        self.assertEqual([variant["style_id"] for variant in plan["variants"]], ["cyberpunk", "watercolor"])
        self.assertEqual([variant["ab_label"] for variant in plan["variants"]], ["A", "B"])
        self.assertEqual([variant["output"] for variant in plan["variants"]], [
            "outputs/batch/01-cyberpunk.png",
            "outputs/batch/02-watercolor.png",
        ])
        self.assertIn("cyberpunk style", plan["variants"][0]["enhanced_prompt"])

    def test_batch_plan_explore_mode_uses_style_search(self) -> None:
        args = build_parser().parse_args([
            "batch",
            "--prompt", "cyberpunk city",
            "--explore",
            "--limit", "2",
            "--output-dir", "outputs/explore",
            "--dry-run",
        ])

        plan = build_batch_plan(args)

        self.assertEqual(len(plan["variants"]), 2)
        self.assertEqual(plan["mode"], "explore")


if __name__ == "__main__":
    unittest.main()
