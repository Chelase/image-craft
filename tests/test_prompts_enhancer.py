import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from prompts_enhancer import enhance, normalize_visual_prompt  # noqa: E402
from image_craft import render_template  # noqa: E402


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


if __name__ == "__main__":
    unittest.main()
