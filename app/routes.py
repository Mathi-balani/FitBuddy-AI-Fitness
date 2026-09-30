import json
import logging
from datetime import datetime

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from pydantic import ValidationError
from sqlalchemy.orm import Session
from sqlalchemy import select

from .database import get_db
from .models import User, Plan
from .schemas import UserInput, FeedbackRequest
from .gemini_generator import generate_workout_gemini
from .gemini_flash_generator import generate_nutrition_tip_with_flash
from .updated_plan import update_workout_plan

router = APIRouter()
logger = logging.getLogger(__name__)

def plan_to_json(plan: dict) -> str:
    return json.dumps(plan, ensure_ascii=False, indent=2)

@router.get("/", response_class=HTMLResponse)
def home(request: Request):
    return request.app.state.templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"error": None}
    )

@router.get("/health")
def health():
    return {"status": "ok", "service": "FitBuddy"}

@router.post("/generate-workout", response_class=HTMLResponse)
def generate_workout(
    request: Request,
    user_id: str = Form(...),
    name: str = Form(...),
    age: int = Form(...),
    weight: float = Form(...),
    goal: str = Form(...),
    intensity: str = Form(...),
    db: Session = Depends(get_db),
):
    try:
        data = UserInput(
            user_id=user_id.strip(),
            name=name.strip(),
            age=age,
            weight=weight,
            goal=goal.strip(),
            intensity=intensity,
        )

        workout_plan = generate_workout_gemini(
            data.name, data.age, data.weight, data.goal, data.intensity
        )
        nutrition_tip = generate_nutrition_tip_with_flash(data.goal)

        user = db.scalar(select(User).where(User.user_id == data.user_id))
        if user is None:
            user = User(
                user_id=data.user_id,
                name=data.name,
                age=data.age,
                weight=data.weight,
                goal=data.goal,
                intensity=data.intensity,
            )
            db.add(user)
            db.flush()
        else:
            user.name = data.name
            user.age = data.age
            user.weight = data.weight
            user.goal = data.goal
            user.intensity = data.intensity

        plan = user.plan
        if plan is None:
            plan = Plan(
                user_id=user.id,
                original_plan=plan_to_json(workout_plan),
                nutrition_tip=nutrition_tip,
            )
            db.add(plan)
        else:
            plan.original_plan = plan_to_json(workout_plan)
            plan.updated_plan = None
            plan.feedback = None
            plan.nutrition_tip = nutrition_tip
            plan.updated_at = None

        db.commit()
        db.refresh(user)
        db.refresh(plan)

        return request.app.state.templates.TemplateResponse(
            request=request,
            name="result.html",
            context={
                "user": user,
                "plan": workout_plan,
                "nutrition_tip": nutrition_tip,
                "updated_plan": None,
                "feedback": None,
            }
        )
    except ValidationError:
        db.rollback()
        return request.app.state.templates.TemplateResponse(
            request=request,
            name="index.html",
            context={"error": "Check your details: use an ID and name of at least 2 characters, age 13-100, weight 20-300 kg, and a listed intensity."},
            status_code=422,
        )
    except Exception:
        logger.exception("Workout plan request failed")
        db.rollback()
        return request.app.state.templates.TemplateResponse(
            request=request,
            name="index.html",
            context={"error": "We couldn't save your plan just now. Please try again."},
            status_code=500,
        )

@router.post("/submit-feedback", response_class=HTMLResponse)
def submit_feedback(
    request: Request,
    user_id: str = Form(...),
    feedback: str = Form(...),
    db: Session = Depends(get_db),
):
    try:
        data = FeedbackRequest(user_id=user_id.strip(), feedback=feedback.strip())
        user = db.scalar(select(User).where(User.user_id == data.user_id))
        if user is None or user.plan is None:
            return request.app.state.templates.TemplateResponse(
                request=request,
                name="index.html",
                context={"error": "User ID not found. Generate a plan first."}
            )

        original = json.loads(user.plan.original_plan)
        updated = update_workout_plan(original, data.feedback)

        user.plan.updated_plan = plan_to_json(updated)
        user.plan.feedback = data.feedback
        user.plan.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(user)

        return request.app.state.templates.TemplateResponse(
            request=request,
            name="result.html",
            context={
                "user": user,
                "plan": original,
                "nutrition_tip": user.plan.nutrition_tip,
                "updated_plan": updated,
                "feedback": data.feedback,
                "revision_notice": updated.get("_revision_note"),
            }
        )
    except ValidationError:
        db.rollback()
        return request.app.state.templates.TemplateResponse(
            request=request,
            name="index.html",
            context={"error": "Enter a valid user ID and feedback of at least 3 characters."},
            status_code=422,
        )
    except Exception:
        logger.exception("Workout plan feedback update failed")
        db.rollback()
        return request.app.state.templates.TemplateResponse(
            request=request,
            name="index.html",
            context={"error": "We couldn't update that plan just now. Please try again."},
            status_code=500,
        )

@router.get("/view-all-users", response_class=HTMLResponse)
def view_all_users(request: Request, db: Session = Depends(get_db)):
    users = db.scalars(select(User).order_by(User.created_at.desc())).all()
    return request.app.state.templates.TemplateResponse(
        request=request,
        name="all_users.html",
        context={"users": users}
    )

@router.post("/delete-user/{user_id}")
def delete_user(user_id: str, db: Session = Depends(get_db)):
    user = db.scalar(select(User).where(User.user_id == user_id))
    if user:
        db.delete(user)
        db.commit()
    return RedirectResponse(url="/view-all-users", status_code=303)
