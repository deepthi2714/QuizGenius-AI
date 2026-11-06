# QuizGenius AI - AI Quiz Generator using NLP

Turn a topic or study notes into multiple-choice quizzes with answers, explanations and scores.

## Features
- Sign in / Create account (salted PBKDF2 password hashing, SQLite)
- Topic or pasted-notes input, 3-20 questions, Easy / Medium / Hard
- NLTK preprocessing: sentence tokenization, stop-word removal, keyword extraction
- Gemini API question generation as structured JSON, with validation and retry
- Offline mode (no API key): fill-in-the-blank questions built from pasted notes
- One-question-at-a-time quiz with Previous / Next / Submit
- Result page: score ring, percentage, correct/incorrect/skipped, feedback, answer review with explanations
- Dashboard stats and result history with a progress chart

## Run
```bash
python -m venv venv
venv\Scripts\activate        # Windows   (Mac/Linux: source venv/bin/activate)
pip install -r requirements.txt
copy .env.example .env       # Mac/Linux: cp .env.example .env  -> add GEMINI_API_KEY
streamlit run app.py
```
Get a free Gemini key at https://aistudio.google.com/apikey. You can also paste it in the app under Settings.
If a model name stops working, change it in Settings or `GEMINI_MODEL` in `.env`.

## Structure
```
app.py                      Streamlit UI and page routing
modules/database.py         Users and results (SQLite)
modules/nlp_processor.py    Module 2: NLP processing
modules/quiz_generator.py   Module 3: Gemini + validation + offline fallback
modules/scoring.py          Module 5: score and feedback
modules/styles.py           Theme and CSS
.streamlit/config.toml      Theme config
```
