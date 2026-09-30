# FitBuddy Project Notes

## Reference mapping

Reference requirement → implementation:

- 7-day personalized workout with offline fallback → `app/gemini_generator.py`
- Nutrition/recovery tip with offline fallback → `app/gemini_flash_generator.py`
- Feedback-based update with local recovery/cardio adjustments → `app/updated_plan.py`
- User/plan persistence → `app/database.py` + `app/models.py`
- FastAPI routing → `app/routes.py`
- Jinja2 UI → `templates/`
- Admin/coach view → `templates/all_users.html`
- Local deployment → Uvicorn
- Cloud deployment preparation → `render.yaml`

## Simple architecture explanation for presentation

```text
User
  |
  v
HTML + Jinja2
  |
  v
FastAPI routes.py
  |
  +--------------------+
  |                    |
  v                    v
Gemini or local    SQLite Database
plan generator
  |                    |
  +----------+---------+
             |
             v
       Result / Updated Plan
```

## Viva explanation

"When the user submits fitness details, FastAPI validates the input. If Gemini is configured and available, it generates the workout and nutrition tip; otherwise FitBuddy returns built-in guidance so the user still gets a plan. User information and the plan are saved through SQLAlchemy into SQLite, then rendered with Jinja2. Feedback is sent to Gemini when available, with a local recovery/cardio adjustment fallback. The revised plan is stored separately so the original plan is preserved."

## Suggested presentation screens

1. Home / input page
2. Generated 7-day plan
3. Nutrition/recovery tip
4. Feedback update
5. Updated plan
6. Coach dashboard
7. FastAPI `/docs`
8. Database file / architecture explanation

## Future improvements

- Authentication for admin dashboard
- Multiple feedback revisions/history
- User login and profile
- Progress tracking
- Exercise library
- Goal history and charts
- PostgreSQL for production
- Rate limiting
- Audit logging
- PDF export
- Multilingual UI
- Voice input
- More granular fitness preferences
