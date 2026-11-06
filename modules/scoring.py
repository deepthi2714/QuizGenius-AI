"""Score calculation and performance feedback."""


def feedback_for(pct: float):
    if pct >= 90:
        return "Outstanding", "You have a firm grip on this material. Try a Hard quiz next."
    if pct >= 75:
        return "Strong work", "You know most of it. Review the questions you missed to close the gaps."
    if pct >= 50:
        return "Getting there", "You have the basics. Read the explanations below and retake the quiz."
    return "Needs more practice", "Revisit the material, then retake the quiz. Start with the explanations below."


def evaluate(questions, answers: dict) -> dict:
    details, correct, unanswered = [], 0, 0
    for i, q in enumerate(questions):
        chosen = answers.get(i)
        ok = chosen == q["answer"]
        correct += ok
        unanswered += chosen is None
        details.append({"question": q["question"], "options": q["options"], "answer": q["answer"],
                        "chosen": chosen, "correct": ok, "explanation": q["explanation"]})
    total = len(questions)
    pct = round(correct / total * 100, 1) if total else 0.0
    title, msg = feedback_for(pct)
    return {"total": total, "correct": correct, "incorrect": total - correct - unanswered,
            "unanswered": unanswered, "percentage": pct, "title": title, "message": msg, "details": details}
