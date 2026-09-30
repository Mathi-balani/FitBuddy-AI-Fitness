import logging
from copy import deepcopy
from pydantic import BaseModel, Field
from typing import List
from google.genai import types

from .gemini_client import client, FITNESS_MODEL
from .gemini_generator import WorkoutDay

logger = logging.getLogger(__name__)

class UpdatedWorkoutPlan(BaseModel):
    title: str
    overview: str
    days: List[WorkoutDay] = Field(min_length=7, max_length=7)
    safety_note: str


def _build_fallback_revision(original_plan: dict, feedback: str) -> dict:
    revised = deepcopy(original_plan)
    request = feedback.lower()
    days = revised.get("days", [])
    changes = []

    if any(term in request for term in ("rest", "recovery", "day off")) and len(days) >= 6:
        days[5].update({
            "focus": "Rest and recovery",
            "exercises": ["Rest, or take an easy walk: 15-20 minutes", "Gentle mobility: 5 minutes"],
            "cooldown": "Keep movement comfortable and prioritize sleep and hydration.",
        })
        changes.append("added a recovery day")

    if any(term in request for term in ("cardio", "aerobic", "conditioning")):
        for day in (days[0], days[2], days[4]):
            exercises = day.setdefault("exercises", [])
            if not any("cardio" in exercise.lower() or "walk" in exercise.lower() for exercise in exercises):
                exercises.append("Easy-to-moderate cardio: 10-15 minutes")
        changes.append("added short cardio options")

    if any(term in request for term in ("easier", "lower intensity", "less intense", "beginner")):
        revised["overview"] += " Keep every set easy and stop well before fatigue." 
        changes.append("reduced the suggested effort")

    if changes:
        change_summary = ", ".join(changes)
        revised["overview"] += f" Local revision: {change_summary}."
    else:
        revised["overview"] += " Your feedback was saved; the original structure was kept because AI revision is offline."

    revised["_source"] = "built-in fallback"
    revised["_revision_note"] = (
        f"AI is offline. Applied local changes: {', '.join(changes)}."
        if changes else "AI is offline. Your feedback was saved, but no automatic schedule changes were made."
    )
    return revised


def update_workout_plan(original_plan: dict, feedback: str) -> dict:
    prompt = f"""
Update the following 7-day fitness plan based on the user's feedback.

ORIGINAL PLAN:
{original_plan}

USER FEEDBACK:
{feedback}

Rules:
- Keep exactly 7 days.
- Apply reasonable requested changes while preserving a balanced schedule.
- Do not create extreme training volume or unsafe instructions.
- Use clear exercise, sets/reps/duration, rest, warm-up and cooldown details.
- If the feedback raises a medical or injury concern, advise professional guidance
  instead of diagnosing or prescribing treatment.
"""
    if client is None:
        return _build_fallback_revision(original_plan, feedback)

    try:
        response = client.models.generate_content(
            model=FITNESS_MODEL,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=UpdatedWorkoutPlan,
            ),
        )
        plan = UpdatedWorkoutPlan.model_validate_json(response.text).model_dump()
        plan["_source"] = "Gemini AI"
        return plan
    except Exception as exc:
        logger.warning(
            "Gemini plan revision failed (%s, status=%s); using built-in fallback.",
            type(exc).__name__,
            getattr(exc, "status_code", "unknown"),
        )
        return _build_fallback_revision(original_plan, feedback)
