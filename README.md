# FitBuddy – AI Fitness Plan Generator

FitBuddy is a FastAPI + Jinja2 web application based on the supplied project reference document. It uses Gemini when a valid API key is configured to generate a personalized 7-day workout plan, a concise nutrition/recovery tip, and a revised plan from user feedback. Without Gemini access, a built-in generator keeps plan creation, nutrition guidance, and common feedback revisions available. SQLite + SQLAlchemy store user and plan data.

## Features

- Personalized 7-day workout plan
- Goal: weight loss, muscle gain, general wellness, strength, flexibility or cardio fitness
- Low / Medium / High intensity
- Warm-up, workout, cooldown and recovery guidance
- Nutrition / recovery tip
- Feedback-based AI plan update
- SQLite persistence
- Coach/Admin dashboard
- Delete user
- FastAPI `/docs` API documentation
- Responsive HTML/CSS interface
- Health endpoint
- Render deployment configuration

## Project structure

```text
FitBuddy/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── routes.py
│   ├── database.py
│   ├── models.py
│   ├── schemas.py
│   ├── gemini_client.py
│   ├── gemini_generator.py
│   ├── gemini_flash_generator.py
│   └── updated_plan.py
├── templates/
│   ├── index.html
│   ├── result.html
│   └── all_users.html
├── static/
│   └── style.css
├── .env.example
├── .gitignore
├── requirements.txt
├── render.yaml
└── README.md
```

## Windows setup

Open Command Prompt in this folder.

```cmd
py -m venv venv
venv\Scripts\python.exe -m pip install --upgrade pip
venv\Scripts\python.exe -m pip install -r requirements.txt
```

Create `.env` by copying `.env.example`. A Gemini key is optional; without one, FitBuddy uses its built-in plan generator. To enable Gemini, replace the placeholder with your API key:

```env
GEMINI_API_KEY=YOUR_REAL_KEY
FITNESS_MODEL=gemini-3.8-flash
TIP_MODEL=gemini-3.8-flash
```

Google's current recommended model is `gemini-3.8-flash`. Other supported text-generation options include `gemini-3.7-flash`, `gemini-3.6-flash`, `gemini-3.5-flash`, `gemini-3.5-flash-lite`, and `gemini-3.1-flash-lite`. Set `FITNESS_MODEL` and `TIP_MODEL` independently to choose different models.

Do NOT type those lines as Command Prompt commands.

Run:

```cmd
venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

Open:

- http://127.0.0.1:8000
- http://127.0.0.1:8000/docs
- http://127.0.0.1:8000/health
- http://127.0.0.1:8000/view-all-users

## Demo flow

1. Enter name, user ID, age, weight, goal and intensity.
2. Click Generate My 7-Day Plan.
3. Review the 7 day cards and nutrition/recovery tip.
4. Enter feedback such as "Add more cardio and one extra rest day."
5. Submit feedback.
6. Review the revised plan and its generation source.
7. Open Coach Dashboard to show stored users and original/updated plans.
8. Open `/docs` to demonstrate the FastAPI API.

## Deployment

The included `render.yaml` uses:

```text
Build: pip install -r requirements.txt
Start: uvicorn app.main:app --host 0.0.0.0 --port $PORT
Health: /health
```

On Render, add `GEMINI_API_KEY` as a secret environment variable.

## Safety note

FitBuddy is a demonstration / general wellness application. It is not a medical diagnosis, treatment, or emergency service. The generated plan should be reviewed by a qualified professional when a person has an injury, medical condition, pregnancy, significant pain, or other individual health concern.

## Important source-reference note

The supplied reference document described Gemini 1.5 Pro and Gemini Flash and used the older `google-generativeai` package. This implementation preserves the same functional architecture while using Google's current `google-genai` Python SDK and a configurable current Gemini model so the project is easier to maintain.
