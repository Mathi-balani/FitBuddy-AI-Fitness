import logging
from typing import List
from pydantic import BaseModel, Field
from google.genai import types

from .gemini_client import client, FITNESS_MODEL

logger = logging.getLogger(__name__)


def _build_fallback_plan(name: str, goal: str, intensity: str) -> dict:
    effort = {"Low": "2 sets", "Medium": "3 sets", "High": "3 controlled sets"}.get(
        intensity, "2 sets"
    )
    focus = goal.lower()
    if "cardio" in focus or "weight loss" in focus:
        sessions = [
            ("Cardio base", ["Brisk walk or cycle: 20-30 minutes", "Bodyweight squat: " + effort + " of 10 reps"]),
            ("Full-body strength", ["Chair or goblet squat: " + effort + " of 10 reps", "Incline push-up: " + effort + " of 8 reps", "Glute bridge: " + effort + " of 12 reps"]),
            ("Intervals", ["Easy-to-moderate intervals: 6 rounds of 1 minute brisk, 2 minutes easy", "Calf raises: " + effort + " of 12 reps"]),
            ("Mobility and recovery", ["Gentle full-body mobility: 15 minutes", "Easy walk: 10-15 minutes"]),
            ("Steady cardio", ["Comfortable walk, cycle, or swim: 25-35 minutes", "Dead bug: " + effort + " of 8 reps per side"]),
            ("Full-body circuit", ["Reverse lunge: " + effort + " of 8 reps per side", "Wall push-up: " + effort + " of 10 reps", "Bird dog: " + effort + " of 8 reps per side"]),
            ("Rest and reset", ["Rest, or take an easy walk: 15-20 minutes", "Gentle stretching: 5 minutes"]),
        ]
    elif "flex" in focus or "wellness" in focus:
        sessions = [
            ("Full-body mobility", ["Gentle hip and ankle mobility: 2 rounds", "Thoracic rotations: 8 per side", "Easy walk: 15 minutes"]),
            ("Strength and balance", ["Sit-to-stand: " + effort + " of 10 reps", "Wall push-up: " + effort + " of 8 reps", "Single-leg balance: 3 x 20 seconds per side"]),
            ("Mobility flow", ["Cat-cow: 2 x 8 reps", "Hip flexor stretch: 2 x 30 seconds per side", "Hamstring stretch: 2 x 30 seconds per side"]),
            ("Active recovery", ["Comfortable walk: 20 minutes", "Gentle full-body stretching: 10 minutes"]),
            ("Core and posture", ["Bird dog: " + effort + " of 8 reps per side", "Glute bridge: " + effort + " of 12 reps", "Wall slides: " + effort + " of 10 reps"]),
            ("Low-impact cardio", ["Easy cycle, swim, or walk: 20-30 minutes", "Calf raises: " + effort + " of 12 reps"]),
            ("Rest and reset", ["Rest, or take a relaxed walk: 15 minutes", "Choose one comfortable stretch: 2 x 30 seconds"]),
        ]
    else:
        sessions = [
            ("Lower-body strength", ["Squat to chair or goblet squat: " + effort + " of 8-10 reps", "Glute bridge: " + effort + " of 12 reps", "Calf raise: " + effort + " of 12 reps"]),
            ("Upper-body strength", ["Incline push-up: " + effort + " of 8 reps", "Backpack row: " + effort + " of 10 reps", "Dead bug: " + effort + " of 8 reps per side"]),
            ("Easy cardio", ["Brisk walk or cycle: 20-30 minutes", "Gentle shoulder and hip mobility: 5 minutes"]),
            ("Rest and recovery", ["Rest, or take an easy walk: 15-20 minutes", "Gentle stretching: 5 minutes"]),
            ("Full-body strength", ["Reverse lunge: " + effort + " of 8 reps per side", "Incline push-up: " + effort + " of 8 reps", "Backpack row: " + effort + " of 10 reps"]),
            ("Core and conditioning", ["March in place: 3 x 1 minute", "Bird dog: " + effort + " of 8 reps per side", "Glute bridge: " + effort + " of 12 reps"]),
            ("Rest and reset", ["Rest, or take a comfortable walk: 15 minutes", "Optional gentle mobility: 5 minutes"]),
        ]

    return {
        "title": f"7-Day {goal} Plan for {name}",
        "overview": f"A balanced {intensity.lower()}-effort starter week for your {goal.lower()} goal. Adjust pace to your fitness level and rest whenever needed.",
        "days": [
            {
                "day": f"Day {index}",
                "focus": day_focus,
                "warm_up": "5-10 minutes of easy movement, followed by comfortable dynamic mobility.",
                "exercises": exercises,
                "cooldown": "Slow down for 3-5 minutes and stretch gently; stop if you feel pain.",
            }
            for index, (day_focus, exercises) in enumerate(sessions, start=1)
        ],
        "safety_note": "Start at a comfortable level, use good form, and stop if you feel pain. Seek qualified professional guidance for injuries, pregnancy, or medical concerns.",
        "_source": "built-in fallback",
    }

class WorkoutDay(BaseModel):
    day: str
    focus: str
    warm_up: str
    exercises: List[str] = Field(
        description="Exercise name with sets, repetitions or duration, and rest."
    )
    cooldown: str

class WorkoutPlan(BaseModel):
    title: str
    overview: str
    days: List[WorkoutDay] = Field(min_length=7, max_length=7)
    safety_note: str

def generate_workout_gemini(
    name: str,
    age: int,
    weight: float,
    goal: str,
    intensity: str
) -> dict:
    prompt = f"""
Create a practical 7-day fitness plan for a user named {name}.
Age: {age}
Weight: {weight} kg
Fitness goal: {goal}
Preferred workout intensity: {intensity}

Requirements:
- Exactly 7 day entries.
- Each day must include a focus, 5-10 minute warm-up, main exercises
  with sets/reps or duration and rest, and a cooldown/recovery instruction.
- Match the goal and requested intensity without extreme volume or unsafe claims.
- Include rest/recovery where appropriate.
- Use clear, beginner-friendly language.
- Do not diagnose medical conditions or prescribe treatment.
- If a user mentions an injury, chronic condition, pregnancy, or other medical
  concern in later feedback, recommend professional guidance rather than diagnosis.
"""
    if client is None:
        return _build_fallback_plan(name, goal, intensity)

    try:
        response = client.models.generate_content(
            model=FITNESS_MODEL,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=WorkoutPlan,
            ),
        )
        plan = WorkoutPlan.model_validate_json(response.text).model_dump()
        plan["_source"] = "Gemini AI"
        return plan
    except Exception as exc:
        logger.warning(
            "Gemini workout request failed (%s, status=%s); using built-in fallback.",
            type(exc).__name__,
            getattr(exc, "status_code", "unknown"),
        )
        return _build_fallback_plan(name, goal, intensity)
