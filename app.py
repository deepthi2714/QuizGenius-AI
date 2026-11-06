"""QuizGenius AI - AI Quiz Generator using NLP (Streamlit)."""
import html
import os
import uuid

import streamlit as st
from modules.styles import CSS

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Material+Symbols+Rounded');

.material-symbols-rounded {
    font-family: 'Material Symbols Rounded';
    font-weight: normal;
    font-style: normal;
    font-size: 24px;
    display: inline-block;
    white-space: nowrap;
    direction: ltr;
    -webkit-font-feature-settings: 'liga';
    -webkit-font-smoothing: antialiased;
}
</style>
""", unsafe_allow_html=True)

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from modules import database as db
from modules.nlp_processor import preprocess
from modules.quiz_generator import QuizError, generate_quiz
from modules.scoring import evaluate
from modules.styles import CSS

LETTERS = "ABCD"
st.set_page_config(page_title="QuizGenius AI", page_icon="🧠", layout="wide")
st.markdown(CSS, unsafe_allow_html=True)
db.init_db()

for k, v in {"user": None, "page": "home", "quiz": None, "answers": {}, "q_index": 0,
             "result": None, "api_key": "", "model": ""}.items():
    st.session_state.setdefault(k, v)

esc = html.escape


def go(page: str):
    st.session_state.page = page
    st.rerun()


# ---------------------------------------------------------------- AUTH
def auth_page():
    left, right = st.columns([1.15, 1], gap="large")
    with left:
        st.markdown(
            """<div class="hero">
              <div class="brand"><div class="logo">Q</div>QuizGenius AI</div>
              <h1>Turn your notes into practice exams.</h1>
              <p>Paste a chapter or type a topic. Get multiple-choice questions, instant answers and explanations.</p>
              <div class="sample">
                <div class="q">What is Artificial Intelligence?</div>
                <div class="o">A. A computer operating system</div>
                <div class="o right">B. Technology that enables machines to perform tasks requiring human-like intelligence</div>
                <div class="o">C. A programming language</div>
                <div class="o">D. A type of computer hardware</div>
              </div></div>""",
            unsafe_allow_html=True,
        )
    with right:
        st.markdown('<div style="height:2.2rem"></div><div class="auth-head">Start studying</div>'
                    '<div class="auth-sub">Sign in to save your scores and track progress.</div>', unsafe_allow_html=True)
        t_in, t_up = st.tabs(["Sign in", "Create account"])
        with t_in:
            with st.form("login_form"):
                email = st.text_input("Email", placeholder="you@example.com")
                pw = st.text_input("Password", type="password")
                ok = st.form_submit_button("Sign in", type="primary", use_container_width=True)
            if ok:
                user = db.verify_user(email, pw)
                if user:
                    st.session_state.user = user
                    go("home")
                else:
                    st.error("Email or password is incorrect.")
        with t_up:
            with st.form("signup_form"):
                name = st.text_input("Full name")
                email2 = st.text_input("Email", key="su_email", placeholder="you@example.com")
                pw2 = st.text_input("Password", type="password", key="su_pw", help="At least 6 characters")
                ok2 = st.form_submit_button("Create account", type="primary", use_container_width=True)
            if ok2:
                user, err = db.create_user(name, email2, pw2)
                if err:
                    st.error(err)
                else:
                    st.session_state.user = user
                    go("home")


# ---------------------------------------------------------------- SIDEBAR
def sidebar():
    u = st.session_state.user
    with st.sidebar:
        st.markdown(
            f'<div class="side-user"><div class="avatar">{esc(u["name"][:1].upper())}</div>'
            f'<div><b>{esc(u["name"])}</b><br><small>{esc(u["email"])}</small></div></div>',
            unsafe_allow_html=True,
        )
        if st.button("New quiz", use_container_width=True):
            go("home")
        if st.button("My results", use_container_width=True):
            go("history")
        st.divider()
        with st.expander("Settings"):
            st.caption("Gemini API key (free at aistudio.google.com/apikey). Leave blank for offline mode.")
            st.session_state.api_key = st.text_input("API key", value=st.session_state.api_key, type="password")
            st.session_state.model = st.text_input("Model", value=st.session_state.model or os.getenv("GEMINI_MODEL", "gemini-2.5-flash"))
        if st.button("Sign out", use_container_width=True):
            for k in ("user", "quiz", "result"):
                st.session_state[k] = None
            st.session_state.answers, st.session_state.q_index, st.session_state.page = {}, 0, "home"
            st.rerun()


# ---------------------------------------------------------------- HOME
def home_page():
    u = st.session_state.user
    st.markdown(f'<h1 class="page-title">Hi {esc(u["name"].split()[0])}, what are you studying?</h1>'
                '<div class="page-sub">Enter a topic or paste your notes, then choose how many questions you want.</div>',
                unsafe_allow_html=True)
    s = db.get_stats(u["id"])
    cols = st.columns(4)
    for c, (n, l) in zip(cols, [(s["quizzes"], "Quizzes taken"), (s["questions"], "Questions answered"),
                                (f'{s["average"]}%', "Average score"), (f'{s["best"]}%', "Best score")]):
        c.markdown(f'<div class="stat"><div class="n">{n}</div><div class="l">{l}</div></div>', unsafe_allow_html=True)
    st.markdown("<div style='height:1.2rem'></div>", unsafe_allow_html=True)

    main, side = st.columns([1.7, 1], gap="large")
    with main:
        mode = st.radio("Input type", ["Topic", "Paste notes"], horizontal=True, label_visibility="collapsed")
        if mode == "Topic":
            content = st.text_input("Topic", placeholder="e.g. Machine Learning, Photosynthesis, World War II")
        else:
            content = st.text_area("Study notes", height=230, placeholder="Paste a paragraph or chapter here (at least a few sentences)...")
    with side:
        n = st.slider("Number of questions", 3, 20, 5)
        diff = st.select_slider("Difficulty", ["Easy", "Medium", "Hard"], value="Easy")
        st.caption("Gemini API: " + ("connected" if (st.session_state.api_key or os.getenv("GEMINI_API_KEY")) else "no key, using offline mode"))
        go_btn = st.button("Generate quiz", type="primary", use_container_width=True)

    if go_btn:
        if not content.strip():
            st.warning("Enter a topic or paste some notes first.")
            return
        try:
            with st.spinner("Reading your material and writing questions..."):
                processed = preprocess(content)
                questions, engine = generate_quiz(content, processed, n, diff, st.session_state.api_key, st.session_state.model)
        except QuizError as e:
            st.error(str(e))
            return
        topic = content.strip() if len(content.split()) < 15 else " ".join(content.split()[:8]) + "..."
        st.session_state.quiz = {"id": uuid.uuid4().hex[:8], "topic": topic, "difficulty": diff,
                                 "questions": questions, "engine": engine}
        st.session_state.answers, st.session_state.q_index, st.session_state.result = {}, 0, None
        go("quiz")


# ---------------------------------------------------------------- QUIZ
def quiz_page():
    quiz = st.session_state.quiz
    if not quiz:
        return go("home")
    qs, i = quiz["questions"], st.session_state.q_index
    q = qs[i]
    st.markdown(f'<h1 class="page-title">{esc(quiz["topic"])}</h1>', unsafe_allow_html=True)
    st.progress((i + 1) / len(qs))
    st.markdown(f'<div class="q-meta"><span>Question {i + 1} of {len(qs)}</span>'
                f'<span class="pill">{quiz["difficulty"]}</span></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="q-card">{esc(q["question"])}</div>', unsafe_allow_html=True)

    choice = st.radio("Options", list(range(4)), index=st.session_state.answers.get(i),
                      format_func=lambda x: f"{LETTERS[x]}.  {q['options'][x]}",
                      key=f"radio_{quiz['id']}_{i}", label_visibility="collapsed")
    if choice is not None:
        st.session_state.answers[i] = choice

    answered = len(st.session_state.answers)
    st.caption(f"{answered} of {len(qs)} answered")
    b1, b2, b3 = st.columns([1, 1, 2])
    if i > 0 and b1.button("Previous", use_container_width=True):
        st.session_state.q_index -= 1
        st.rerun()
    if i < len(qs) - 1:
        if b2.button("Next", type="primary", use_container_width=True):
            st.session_state.q_index += 1
            st.rerun()
    else:
        if b2.button("Submit quiz", type="primary", use_container_width=True):
            res = evaluate(qs, st.session_state.answers)
            db.save_result(st.session_state.user["id"], quiz["topic"], quiz["difficulty"], res)
            st.session_state.result = res
            go("result")
        if answered < len(qs):
            b3.warning(f"{len(qs) - answered} unanswered. They count as incorrect.")


# ---------------------------------------------------------------- RESULT
def result_page():
    res, quiz = st.session_state.result, st.session_state.quiz
    if not res:
        return go("home")
    pct = res["percentage"]
    color = "#16A34A" if pct >= 75 else "#F5B301" if pct >= 50 else "#DC2626"
    st.markdown(f'<h1 class="page-title">{esc(res["title"])}</h1><div class="page-sub">{esc(res["message"])}</div>', unsafe_allow_html=True)
    c1, c2 = st.columns([1, 2], gap="large")
    with c1:
        st.markdown(f'<div class="ring" style="background:conic-gradient({color} {pct * 3.6}deg,#E6E3F7 0deg)">'
                    f'<div class="inner"><div><div class="pct">{pct:g}%</div><div class="sub">{res["correct"]} of {res["total"]}</div></div></div></div>',
                    unsafe_allow_html=True)
    with c2:
        m = st.columns(3)
        for col, (n, l) in zip(m, [(res["correct"], "Correct"), (res["incorrect"], "Incorrect"), (res["unanswered"], "Skipped")]):
            col.markdown(f'<div class="stat"><div class="n">{n}</div><div class="l">{l}</div></div>', unsafe_allow_html=True)
        st.markdown("<div style='height:.8rem'></div>", unsafe_allow_html=True)
        a, b = st.columns(2)
        if a.button("Retake this quiz", use_container_width=True):
            st.session_state.quiz["id"] = uuid.uuid4().hex[:8]
            st.session_state.answers, st.session_state.q_index, st.session_state.result = {}, 0, None
            go("quiz")
        if b.button("Create a new quiz", type="primary", use_container_width=True):
            go("home")

    st.markdown("### Review your answers")
    for n, d in enumerate(res["details"], 1):
        kind = "skip" if d["chosen"] is None else "ok" if d["correct"] else "bad"
        icon = {"ok": "Correct", "bad": "Incorrect", "skip": "Skipped"}[kind]
        mine = "No answer" if d["chosen"] is None else f'{LETTERS[d["chosen"]]}. {d["options"][d["chosen"]]}'
        st.markdown(
            f'<div class="rev {kind}"><div class="rq">{n}. {esc(d["question"])}</div>'
            f'<div class="ra"><b>{icon}.</b> Your answer: {esc(mine)}</div>'
            f'<div class="ra">Correct answer: <b>{LETTERS[d["answer"]]}. {esc(d["options"][d["answer"]])}</b></div>'
            f'<div class="ex">{esc(d["explanation"])}</div></div>', unsafe_allow_html=True)


# ---------------------------------------------------------------- HISTORY
def history_page():
    st.markdown('<h1 class="page-title">My results</h1><div class="page-sub">Every quiz you have submitted.</div>', unsafe_allow_html=True)
    rows = db.get_results(st.session_state.user["id"])
    if not rows:
        st.info("No results yet. Generate your first quiz to see your scores here.")
        if st.button("Create a quiz", type="primary"):
            go("home")
        return
    st.line_chart({"Score %": [r["percentage"] for r in reversed(rows)]}, height=220)
    st.dataframe(
        [{"Date": r["created_at"].replace("T", " "), "Topic": r["topic"], "Difficulty": r["difficulty"],
          "Score": f'{r["correct"]}/{r["total"]}', "Percentage": f'{r["percentage"]:g}%'} for r in rows],
        use_container_width=True, hide_index=True)


# ---------------------------------------------------------------- ROUTER
if not st.session_state.user:
    auth_page()
else:
    sidebar()
    {"home": home_page, "quiz": quiz_page, "result": result_page, "history": history_page}[st.session_state.page]()
