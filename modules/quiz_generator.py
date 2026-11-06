
"""Question generation using Gemini API with an offline fallback."""

import json
import os
import random
import re


class QuizError(Exception):
    """Raised with a user-friendly message."""


LETTERS = "ABCD"

# Default and fallback models
DEFAULT_MODEL = "gemini-3.8-flash"

FALLBACK_MODELS = [
    "gemini-3.5-flash-lite"
]

BUSY_CODES = (500, 502, 503, 504)


def _build_prompt(content, keywords, n, difficulty, is_topic):
    source = (
        f'The topic "{content}"'
        if is_topic
        else "the following study material:\n\"\"\"\n"
        + content[:12000] + "\n\"\"\""
    )

    hint = (
        f"\nImportant keywords: {', '.join(keywords)}"
        if keywords and not is_topic else ""
    )

    level = {
        "Easy": "basic definitions and facts",
        "Medium": "understanding and application",
        "Hard": "analysis and comparison",
    }.get(difficulty, "understanding and application")

    return f"""You are an expert exam-question writer.

Create exactly {n} multiple-choice questions from {source}{hint}

Difficulty: {difficulty} ({level}).

Rules:
- Each question must have exactly 4 options.
- Only one answer must be correct.
- Distractors must be plausible.
- Avoid 'all of the above'.
- Randomize correct answer positions.
- Provide a short explanation.
- Return ONLY valid JSON.

Format:
{{"questions":[
{{"question":"Question?",
"options":["A","B","C","D"],
"answer":"A",
"explanation":"Explanation"}}
]}}"""


def _call_gemini(prompt, api_key, model, attempts=3):
    """Send request to Gemini API."""

    import time
    import requests

    url = (
        "https://generativelanguage.googleapis.com/"
        f"v1beta/models/{model}:generateContent"
    )

    body = {
        "contents": [
            {"parts": [{"text": prompt}]}
        ],
        "generationConfig": {
            "temperature": 0.7,
            "responseMimeType": "application/json",
        },
    }

    response = None

    for attempt in range(attempts):
        try:
            response = requests.post(
                url,
                headers={
                    "x-goog-api-key": api_key,
                    "Content-Type": "application/json",
                },
                json=body,
                timeout=90,
            )

        except requests.RequestException as error:
            raise QuizError(
                f"Could not connect to Gemini API: {error}"
            )

        if response.status_code in BUSY_CODES or response.status_code == 429:
            if attempt < attempts - 1:
                time.sleep(2 * (attempt + 1))
                continue

        break

    if response is None:
        raise QuizError("Gemini did not respond.")

    if response.status_code in (400, 401, 403):
        raise QuizError(
            "Gemini rejected the request. Check your API key."
        )

    if response.status_code == 404:
        raise QuizError(
            f"MODEL_NOT_FOUND: Model '{model}' is unavailable."
        )

    if response.status_code == 429:
        raise QuizError("BUSY: Gemini rate limit reached.")

    if response.status_code in BUSY_CODES:
        raise QuizError("BUSY: Gemini server is overloaded.")

    if not response.ok:
        raise QuizError(
            f"Gemini API error: {response.status_code}"
        )

    try:
        return (
            response.json()["candidates"][0]
            ["content"]["parts"][0]["text"]
        )
    except (KeyError, IndexError, TypeError, ValueError):
        raise QuizError("Gemini returned an empty response.")


def validate_questions(raw, n):
    """Validate and parse generated JSON questions."""

    raw = re.sub(
        r"^```(?:json)?\s*|```\s*$",
        "",
        raw.strip(),
        flags=re.IGNORECASE | re.MULTILINE,
    ).strip()

    try:
        data = json.loads(raw)

    except json.JSONDecodeError:
        match = re.search(r"\{.*\}|\[.*\]", raw, re.DOTALL)

        if not match:
            raise QuizError("Invalid JSON response from Gemini.")

        try:
            data = json.loads(match.group(0))
        except json.JSONDecodeError:
            raise QuizError("Could not parse Gemini response.")

    items = (
        data.get("questions", [])
        if isinstance(data, dict)
        else data
    )

    if not isinstance(items, list):
        raise QuizError("Invalid questions format.")

    clean = []

    for item in items:
        try:
            question = str(item["question"]).strip()

            options = [
                re.sub(
                    r"^[A-Da-d][\).:]\s+",
                    "",
                    str(option).strip(),
                )
                for option in item["options"]
            ]

            answer = str(item["answer"]).strip()

            if (
                not question
                or len(options) != 4
                or any(not option for option in options)
                or len(set(x.lower() for x in options)) != 4
            ):
                continue

            if answer[:1].upper() in LETTERS and (
                len(answer) == 1
                or answer[1] in ").: "
            ):
                index = LETTERS.index(answer[0].upper())

            elif answer in options:
                index = options.index(answer)

            else:
                continue

            clean.append({
                "question": question,
                "options": options,
                "answer": index,
                "explanation": str(
                    item.get("explanation", "")
                ).strip() or "No explanation provided.",
            })

        except (KeyError, TypeError, AttributeError):
            continue

    if not clean:
        raise QuizError("Gemini did not generate valid questions.")

    return clean[:n]


def generate_offline(processed, n):
    """Generate questions from pasted notes without Gemini."""

    sentences = [
        sentence
        for sentence in processed.get("sentences", [])
        if 6 <= len(sentence.split()) <= 40
    ]

    keywords = processed.get("keywords", [])

    if len(keywords) < 4 or not sentences:
        raise QuizError(
            "Offline mode needs longer study notes. "
            "Add a Gemini API key to generate questions from topics."
        )

    random.shuffle(sentences)

    questions = []
    used = set()

    for sentence in sentences:

        found = [
            keyword
            for keyword in keywords
            if re.search(
                rf"\b{re.escape(keyword)}\b",
                sentence,
                re.IGNORECASE,
            )
            and keyword.lower() not in used
        ]

        if not found:
            continue

        answer = found[0]
        used.add(answer.lower())

        distractors = [
            keyword
            for keyword in keywords
            if keyword.lower() != answer.lower()
        ]

        if len(distractors) < 3:
            continue

        options = [
            word.capitalize()
            for word in random.sample(distractors, 3)
        ]

        options.append(answer.capitalize())
        random.shuffle(options)

        blank = re.sub(
            rf"\b{re.escape(answer)}\b",
            "_____",
            sentence,
            count=1,
            flags=re.IGNORECASE,
        )

        questions.append({
            "question": f"Fill in the blank: {blank}",
            "options": options,
            "answer": options.index(answer.capitalize()),
            "explanation": f'Original sentence: "{sentence}"',
        })

        if len(questions) >= n:
            break

    if not questions:
        raise QuizError(
            "Could not generate offline questions. Try longer notes."
        )

    return questions


def generate_quiz(
    content,
    processed,
    n,
    difficulty,
    api_key="",
    model="",
):
    """Generate quiz using Gemini, then fallback models."""

    is_topic = len(content.split()) < 15

    api_key = (
        api_key or os.getenv("GEMINI_API_KEY", "")
    ).strip()

    # Correctly initialize the model inside the function.
    selected_model = (
        model or os.getenv("GEMINI_MODEL", DEFAULT_MODEL)
    ).strip()

    if not selected_model:
        selected_model = DEFAULT_MODEL

    # No API key: use offline generation.
    if not api_key:
        return generate_offline(processed, n), "Offline mode"

    source = (
        content.strip()
        if is_topic
        else processed.get("cleaned_text", content)
    )

    prompt = _build_prompt(
        source,
        processed.get("keywords", []),
        n,
        difficulty,
        is_topic,
    )

    # Build model list without duplicates.
    models = [selected_model]

    for fallback in FALLBACK_MODELS:
        if fallback not in models:
            models.append(fallback)

    last_error = None

    for current_model in models:

        try:
            raw = _call_gemini(
                prompt,
                api_key,
                current_model,
            )

            questions = validate_questions(raw, n)

            return questions, f"Gemini ({current_model})"

        except QuizError as error:

            last_error = error
            message = str(error)

            # Authentication/network errors cannot be fixed
            # by trying another model.
            if (
                "rejected the request" in message
                or "Could not connect" in message
            ):
                break

            # Continue to the next model for other errors.
            continue

    # If Gemini is busy, attempt offline generation.
    if last_error and str(last_error).startswith("BUSY"):

        if not is_topic:
            try:
                return (
                    generate_offline(processed, n),
                    "Offline mode (Gemini busy)",
                )
            except QuizError:
                pass

        raise QuizError(
            "Gemini is busy. Wait a minute and try again."
        )

    if last_error:
        raise last_error

    raise QuizError("Quiz generation failed. Check your settings.")
