import unittest
from unittest.mock import patch

from app.gemini_flash_generator import generate_nutrition_tip_with_flash
from app.gemini_generator import generate_workout_gemini
from app.main import app
from app.updated_plan import update_workout_plan


class OfflineGenerationTests(unittest.TestCase):
    def test_app_imports(self):
        self.assertEqual(app.title, "FitBuddy – AI Fitness Plan Generator")

    @patch("app.gemini_generator.client", None)
    def test_workout_fallback_has_seven_days(self):
        plan = generate_workout_gemini("Test User", 28, 70, "Strength", "Medium")

        self.assertEqual(len(plan["days"]), 7)
        self.assertEqual(plan["_source"], "built-in fallback")
        self.assertTrue(all(day["exercises"] for day in plan["days"]))

    @patch("app.gemini_flash_generator.client", None)
    def test_nutrition_fallback_returns_guidance(self):
        tip = generate_nutrition_tip_with_flash("General Wellness")

        self.assertTrue(tip)
        self.assertIn("sleep", tip.lower())

    @patch("app.updated_plan.client", None)
    def test_feedback_fallback_applies_cardio_and_recovery(self):
        with patch("app.gemini_generator.client", None):
            original = generate_workout_gemini("Test User", 28, 70, "Strength", "Medium")

        updated = update_workout_plan(original, "Add cardio and one extra rest day")

        self.assertEqual(len(updated["days"]), 7)
        self.assertEqual(updated["_source"], "built-in fallback")
        self.assertEqual(updated["days"][5]["focus"], "Rest and recovery")
        self.assertIn("cardio", " ".join(updated["days"][0]["exercises"]).lower())

if __name__ == "__main__":
    unittest.main()