
CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:wght@500;700;800&family=Figtree:wght@400;500;600&display=swap');
@import url('https://fonts.googleapis.com/css2?family=Material+Symbols+Rounded');

html, body, [class*="st-"], .stApp {
    font-family: 'Figtree', sans-serif;
}

/* Fix Streamlit Material icons */
.material-symbols-rounded,
span[data-testid="stIconMaterial"],
[data-testid="stIconMaterial"] {
    font-family: 'Material Symbols Rounded' !important;
    font-weight: normal !important;
    font-style: normal !important;
    font-size: 24px;
    line-height: 1;
    white-space: nowrap;
    font-feature-settings: 'liga';
    -webkit-font-smoothing: antialiased;
}

h1, h2, h3, .display {
    font-family: 'Bricolage Grotesque', sans-serif !important;
    letter-spacing: -0.02em;
    color: #1B1B3A;
}

#MainMenu, footer { visibility: hidden; }
.block-container { padding-top: 2rem; max-width: 1100px; }

.stButton > button, .stFormSubmitButton > button {
    border-radius: 12px;
    font-weight: 600;
    padding: .6rem 1.1rem;
    border: 1.5px solid #D9D6F0;
    background: #fff;
    color: #2E2A7A;
    transition: all .15s ease;
}

.stButton > button:hover, .stFormSubmitButton > button:hover {
    border-color: #4338CA;
    color: #4338CA;
}

.stButton > button[kind="primary"],
.stFormSubmitButton > button[kind="primary"] {
    background: #4338CA;
    color: #fff;
    border-color: #4338CA;
    box-shadow: 0 6px 18px rgba(67,56,202,.28);
}

.stButton > button[kind="primary"]:hover,
.stFormSubmitButton > button[kind="primary"]:hover {
    background: #3730A3;
    color: #fff;
}

:focus-visible {
    outline: 3px solid #F5B301 !important;
    outline-offset: 2px;
}

.stTextInput input, .stTextArea textarea,
.stSelectbox div[data-baseweb="select"] > div {
    border-radius: 12px !important;
    border: 1.5px solid #D9D6F0 !important;
    background: #fff !important;
}

.hero {
    background: #1E1B4B;
    color: #F4F2FF;
    border-radius: 28px;
    padding: 2.6rem 2.4rem;
    min-height: 560px;
    position: relative;
    overflow: hidden;
}

.hero::after {
    content: "";
    position: absolute;
    right: -80px;
    bottom: -80px;
    width: 300px;
    height: 300px;
    border-radius: 50%;
    background: radial-gradient(circle at 30% 30%, #F5B301 0%, rgba(245,179,1,0) 70%);
    opacity: .55;
}

.hero .brand {
    font-family: 'Bricolage Grotesque';
    font-weight: 800;
    font-size: 1.25rem;
    display: flex;
    gap: .6rem;
    align-items: center;
}

.hero .logo {
    width: 36px;
    height: 36px;
    border-radius: 10px;
    background: #F5B301;
    color: #1E1B4B;
    display: grid;
    place-items: center;
    font-weight: 800;
}

.hero h1 {
    color: #fff !important;
    font-size: 2.5rem;
    line-height: 1.08;
    margin: 2.2rem 0 1rem;
}

.hero p {
    color: #C9C5F5;
    font-size: 1.05rem;
    max-width: 34ch;
    line-height: 1.55;
}

.sample {
    margin-top: 2rem;
    background: rgba(255,255,255,.08);
    border: 1px solid rgba(255,255,255,.18);
    border-radius: 16px;
    padding: 1rem 1.1rem;
    max-width: 360px;
    position: relative;
    z-index: 2;
}

.sample .q {
    font-weight: 600;
    margin-bottom: .6rem;
    font-size: .95rem;
}

.sample .o {
    padding: .4rem .7rem;
    border-radius: 9px;
    margin: .25rem 0;
    font-size: .88rem;
    background: rgba(255,255,255,.07);
}

.sample .o.right {
    background: #F5B301;
    color: #1E1B4B;
    font-weight: 600;
}

.auth-head {
    margin: .4rem 0 .2rem;
    font-size: 1.9rem;
    font-weight: 800;
    font-family: 'Bricolage Grotesque';
    color: #1B1B3A;
}

.auth-sub {
    color: #6B6A8C;
    margin-bottom: 1rem;
}

.page-title {
    font-size: 2rem;
    font-weight: 800;
    margin: 0;
}

.page-sub {
    color: #6B6A8C;
    margin: .2rem 0 1.4rem;
}

.stat {
    background: #fff;
    border: 1px solid #E6E3F7;
    border-radius: 18px;
    padding: 1.1rem 1.3rem;
}

.stat .n {
    font-family: 'Bricolage Grotesque';
    font-size: 2rem;
    font-weight: 800;
    color: #4338CA;
    line-height: 1;
}

.stat .l {
    color: #6B6A8C;
    font-size: .9rem;
    margin-top: .35rem;
}

.q-meta {
    display: flex;
    justify-content: space-between;
    color: #6B6A8C;
    font-weight: 600;
    font-size: .92rem;
    margin-bottom: .5rem;
}

.pill {
    background: #EDEBFF;
    color: #3730A3;
    border-radius: 999px;
    padding: .15rem .75rem;
    font-weight: 600;
    font-size: .82rem;
}

.q-card {
    background: #fff;
    border: 1px solid #E6E3F7;
    border-left: 6px solid #4338CA;
    border-radius: 18px;
    padding: 1.5rem 1.7rem;
    margin: .7rem 0 1rem;
    font-family: 'Bricolage Grotesque';
    font-size: 1.45rem;
    font-weight: 700;
    line-height: 1.35;
    color: #1B1B3A;
}

div[role="radiogroup"] { gap: .6rem; }

div[role="radiogroup"] > label {
    background: #fff;
    border: 1.5px solid #D9D6F0;
    border-radius: 14px;
    padding: .85rem 1rem;
    width: 100%;
    transition: all .12s;
}

div[role="radiogroup"] > label:hover {
    border-color: #4338CA;
    background: #F7F6FF;
}

div[role="radiogroup"] > label:has(input:checked) {
    border-color: #4338CA;
    background: #EDEBFF;
}

.ring {
    width: 190px;
    height: 190px;
    border-radius: 50%;
    display: grid;
    place-items: center;
    margin: 0 auto;
}

.ring .inner {
    width: 140px;
    height: 140px;
    border-radius: 50%;
    background: #fff;
    display: grid;
    place-items: center;
    text-align: center;
}

.ring .pct {
    font-family: 'Bricolage Grotesque';
    font-size: 2.2rem;
    font-weight: 800;
    color: #1B1B3A;
    line-height: 1;
}

.ring .sub {
    color: #6B6A8C;
    font-size: .85rem;
}

.rev {
    border-radius: 16px;
    padding: 1rem 1.2rem;
    margin-bottom: .8rem;
    border: 1px solid;
}

.rev.ok {
    background: #F0FBF4;
    border-color: #BDE8CC;
}

.rev.bad {
    background: #FFF4F2;
    border-color: #F5C6BE;
}

.rev.skip {
    background: #FFF9E8;
    border-color: #F2DE9B;
}

.rev .rq {
    font-weight: 700;
    margin-bottom: .4rem;
    color: #1B1B3A;
}

.rev .ra {
    font-size: .93rem;
    color: #34335A;
    margin: .15rem 0;
}

.rev .ex {
    margin-top: .5rem;
    font-size: .9rem;
    color: #55547A;
}

section[data-testid="stSidebar"] {
    background: #1E1B4B;
}

section[data-testid="stSidebar"] * {
    color: #E8E6FF;
}

section[data-testid="stSidebar"] .stButton > button {
    background: rgba(255,255,255,.08);
    border-color: rgba(255,255,255,.18);
    color: #fff;
    width: 100%;
}

section[data-testid="stSidebar"] .stButton > button:hover {
    background: #F5B301;
    color: #1E1B4B;
    border-color: #F5B301;
}

section[data-testid="stSidebar"] input {
    color: #1B1B3A !important;
}

.side-user {
    display: flex;
    gap: .7rem;
    align-items: center;
    margin: .3rem 0 1.2rem;
}

.avatar {
    width: 42px;
    height: 42px;
    border-radius: 50%;
    background: #F5B301;
    color: #1E1B4B !important;
    display: grid;
    place-items: center;
    font-weight: 800;
}

@media (prefers-reduced-motion: reduce) {
    * { transition: none !important; }
}
</style>
"""
