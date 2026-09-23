# Learnora — Adaptive Firebase + Gemini learning app

Learnora is a Flask-based adaptive learning platform. A learner chooses a
course, supplies a syllabus (JPG/JPEG/PNG/PDF/TXT/MD/DOCX) or chooses the
General Syllabus, sees a syllabus roadmap, then takes a 7-question Gemini
capability test. The result is classified as Basic, Intermediate, or Advanced.
Lower-level content is treated as already known, so an Intermediate learner
is not sent through the Basic course again.

## Adaptive learning flow

```text
Dashboard
   |
   +-- Choose course
          |
          +-- What is your syllabus?
          |      +-- Upload JPG/JPEG/PNG/PDF/TXT/MD/DOCX
          |      +-- Paste syllabus text
          |      +-- Use General Syllabus
          |
          +-- Gemini maps syllabus to Learnora's exact curriculum topics
          |
          +-- Syllabus roadmap preview
          |
          +-- 7-question Gemini diagnostic
          |      2 Basic -> 3 Intermediate -> 2 Advanced
          |
          +-- Level classification
          |      Basic / Intermediate / Advanced
          |
          +-- Level gate
                 Basic: show difficulty 1+
                 Intermediate: show difficulty 2+
                 Advanced: show difficulty 3+

          |
          +-- Personalized roadmap + exact existing topic content
```

## Firebase authentication

Firebase Authentication handles signup/login/email verification/password
reset. Flask verifies the Firebase ID token and creates the Learnora session.
The Firebase service-account JSON is required by the server and must never be
committed to Git.

Create `serviceAccountKey.json` from Firebase Console -> Project settings ->
Service accounts -> Generate new private key.

## Gemini setup

Create a Gemini API key in Google AI Studio and put it in `.env`:

```env
GEMINI_API_KEY=your_key_here
GEMINI_MODEL=gemini-3.8-flash
```

The key stays on the Flask server. The browser never receives it.

Gemini is used for:
- syllabus/image/PDF analysis
- mapping a syllabus to Learnora's exact topic catalog
- generating the 7-question diagnostic
- interpreting the diagnostic level

If Gemini is not configured, the new syllabus/diagnostic flow will show a
clear configuration error rather than silently pretending that AI was used.

## Run on Windows

```powershell
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
python app.py
```

Open:

```text
http://127.0.0.1:5000
```

## Important files

- `app.py` — Flask routes, syllabus onboarding, diagnostic scoring and roadmap gate
- `dal.py` — SQLite data access and enrollment/assessment persistence
- `db.py` — database schema and migrations
- `config.py` — environment configuration
- `ml/gemini_learning.py` — Gemini syllabus analysis, question generation and level classification
- `ml/skill_graph.py` — curated course graph and topic difficulty
- `templates/start_skill.html` — syllabus upload/general syllabus screen
- `templates/syllabus_preview.html` — generated/generalized roadmap preview
- `templates/quiz.html` — 7-question capability test
- `templates/roadmap.html` — level-gated roadmap
- `data/curriculum.json` — exact Learnora topic catalog and difficulty levels

## Database migration

Existing SQLite databases are migrated automatically when the app starts. New
enrollment fields store syllabus source, syllabus summary, mapped roadmap,
diagnostic questions and detected learner level.

## Security

Do not commit:

```text
.env
serviceAccountKey.json
*-firebase-adminsdk-*.json
instance/syllabi/
```

If a Firebase service-account private key has ever been shared outside your
private machine/repository, revoke that key and generate a new one before
using it again.
