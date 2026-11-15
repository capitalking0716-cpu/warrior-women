"""Warrior Women — visual design system.

One shared look for every view: a professional workout-app feel
(Strong / Fitbod polish) in the Warrior Women brand — black, deep
purple, gold. Pure presentation: CSS plus small HTML builders for the
top identity bar, the hero card and the week strip. No behaviour,
no data, no Streamlit state lives here except ``inject_css``.
"""

import html as _html

import streamlit as st

# Brand tokens (also used by the HTML builders below).
BG = "#0A0A10"
PANEL = "#14141E"
PANEL_BORDER = "#2A2A40"
PURPLE = "#7C3AED"
DEEP_PURPLE = "#4C1D95"
GOLD = "#E9B44C"
TEXT = "#F4F4F8"
MUTED = "#A8A8BE"

CSS = """
<style>
/* ---- App chrome ---------------------------------------------------- */
.stApp { background: #0A0A10; color: #F4F4F8; }
.block-container { padding-top: 1.1rem; padding-bottom: 2.5rem; max-width: 46rem; }
section[data-testid="stSidebar"],
div[data-testid="stSidebarCollapsedControl"] { display: none; }
header[data-testid="stHeader"] { background: transparent; }
h1 { font-size: 1.9rem; font-weight: 800; letter-spacing: .01em; }
h2 { font-size: 1.35rem; font-weight: 700; margin-top: 1.2rem; }
h3 { font-size: 1.1rem; font-weight: 700; }
p, li, label { font-size: 1rem; }
[data-testid="stCaptionContainer"] p { color: #A8A8BE; font-size: .92rem; }

/* ---- Buttons -------------------------------------------------------- */
.stButton > button, .stLinkButton > a, .stFormSubmitButton > button,
.stDownloadButton > button {
  width: 100%; min-height: 52px; font-size: 1.05rem; font-weight: 600;
  border-radius: 14px; background: #1C1C2A; color: #F4F4F8;
  border: 1px solid #34344E;
}
.stButton > button:hover, .stLinkButton > a:hover,
.stFormSubmitButton > button:hover, .stDownloadButton > button:hover {
  border-color: #E9B44C; color: #FFFFFF;
}
.stButton > button[kind="primary"], .stLinkButton > a[kind="primary"],
.stFormSubmitButton > button[kind="primary"] {
  background: linear-gradient(135deg, #7C3AED 0%, #4C1D95 100%);
  border: 1px solid #C9962E; color: #FFFFFF;
}
.stButton > button[kind="primary"]:hover, .stLinkButton > a[kind="primary"]:hover {
  background: linear-gradient(135deg, #8B4BF0 0%, #5B21B6 100%); color: #FFFFFF;
}

/* ---- Cards (bordered containers + expanders) ------------------------ */
div[data-testid="stVerticalBlockBorderWrapper"] {
  background: #14141E; border: 1px solid #2A2A40 !important;
  border-radius: 18px; padding: .35rem .35rem;
}
div[data-testid="stExpander"] {
  background: #14141E; border: 1px solid #2A2A40; border-radius: 14px;
}
div[data-testid="stExpander"] summary { font-size: 1.02rem; font-weight: 600; }

/* ---- Metrics --------------------------------------------------------- */
div[data-testid="stMetric"] {
  background: #14141E; border: 1px solid #2A2A40; border-radius: 16px;
  padding: .8rem 1rem;
}
div[data-testid="stMetric"] label { color: #A8A8BE; }
div[data-testid="stMetricValue"] { color: #F4F4F8; font-weight: 800; }

/* ---- Inputs ---------------------------------------------------------- */
.stTextInput input, .stNumberInput input, .stTextArea textarea {
  font-size: 1.05rem; border-radius: 12px;
}
div[data-baseweb="select"] > div { border-radius: 12px; }

/* ---- Nav pills (horizontal radio) ------------------------------------ */
div[data-testid="stRadio"] > label { display: none; }
div[data-testid="stRadio"] [role="radiogroup"] {
  display: flex; flex-wrap: wrap; gap: .45rem;
}
div[data-testid="stRadio"] [role="radiogroup"] label {
  background: #1A1A28; border: 1px solid #2E2E48; border-radius: 999px;
  padding: .5rem 1rem; margin: 0; cursor: pointer; min-height: 44px;
  display: flex; align-items: center;
}
div[data-testid="stRadio"] [role="radiogroup"] label > div:first-child { display: none; }
div[data-testid="stRadio"] [role="radiogroup"] label p {
  font-size: .98rem; font-weight: 600; color: #D8D8E6;
}
div[data-testid="stRadio"] [role="radiogroup"] label:has(input:checked) {
  background: linear-gradient(135deg, #7C3AED, #4C1D95);
  border-color: #E9B44C;
}
div[data-testid="stRadio"] [role="radiogroup"] label:has(input:checked) p { color: #FFF; }

/* ---- Tabs (auth) ------------------------------------------------------ */
button[data-baseweb="tab"] { font-size: 1.02rem; font-weight: 600; padding: .6rem .4rem; }
button[data-baseweb="tab"][aria-selected="true"] { color: #E9B44C; }
div[data-baseweb="tab-highlight"] { background-color: #E9B44C; }

/* ---- Progress bar ------------------------------------------------------ */
div[data-testid="stProgress"] > div > div > div {
  background: linear-gradient(90deg, #7C3AED, #E9B44C);
}

/* ---- Custom HTML pieces ------------------------------------------------ */
.kw-topbar {
  display: flex; align-items: center; justify-content: space-between;
  gap: .6rem; padding: .55rem .2rem .7rem .2rem;
  border-bottom: 1px solid #26263C; margin-bottom: 1rem;
}
.kw-brand { display: flex; align-items: center; gap: .55rem; min-width: 0; }
.kw-brand .kw-icon { font-size: 1.55rem; line-height: 1; }
.kw-brand .kw-name {
  font-size: 1.28rem; font-weight: 800; color: #F4F4F8;
  letter-spacing: .02em; white-space: nowrap;
}
.kw-brand .kw-name span { color: #E9B44C; }
.kw-member { display: flex; align-items: center; gap: .5rem; min-width: 0; }
.kw-avatar {
  width: 38px; height: 38px; border-radius: 50%; flex: none;
  background: linear-gradient(135deg, #7C3AED, #4C1D95);
  border: 1px solid #E9B44C; color: #FFF; font-weight: 800;
  display: flex; align-items: center; justify-content: center; font-size: 1rem;
}
.kw-member .kw-who { line-height: 1.15; min-width: 0; }
.kw-member .kw-who .kw-mname {
  font-weight: 700; font-size: .95rem; color: #F4F4F8;
  white-space: nowrap; overflow: hidden; text-overflow: ellipsis; max-width: 9.5rem;
}
.kw-badge {
  display: inline-block; font-size: .68rem; font-weight: 800;
  letter-spacing: .06em; color: #0A0A10; background: #E9B44C;
  border-radius: 999px; padding: .12rem .5rem; text-transform: uppercase;
}
.kw-badge.purple { background: #7C3AED; color: #FFF; }

.kw-hero {
  background: linear-gradient(150deg, #1D1038 0%, #14141E 55%, #191204 130%);
  border: 1px solid #4A3577; border-radius: 20px;
  padding: 1.15rem 1.15rem 1rem 1.15rem; margin-bottom: .4rem;
}
.kw-hero .kw-kicker {
  font-size: .74rem; font-weight: 800; letter-spacing: .14em;
  color: #E9B44C; text-transform: uppercase; margin-bottom: .35rem;
}
.kw-hero .kw-title { font-size: 1.65rem; font-weight: 800; line-height: 1.15; color: #FFF; }
.kw-hero .kw-focus { color: #C9C9DC; font-size: 1rem; margin-top: .3rem; }
.kw-chips { display: flex; flex-wrap: wrap; gap: .45rem; margin-top: .8rem; }
.kw-chip {
  background: rgba(255,255,255,.06); border: 1px solid #3B3B58;
  color: #EDEDF4; border-radius: 999px; padding: .3rem .75rem;
  font-size: .88rem; font-weight: 600;
}
.kw-chip.gold { border-color: #C9962E; color: #F5CD6B; }

.kw-week { display: flex; gap: .4rem; margin: .35rem 0 .2rem 0; }
.kw-day {
  flex: 1; text-align: center; border-radius: 14px; padding: .5rem 0 .45rem 0;
  background: #14141E; border: 1px solid #2A2A40; color: #A8A8BE;
}
.kw-day .kw-dletter { font-size: .95rem; font-weight: 800; display: block; }
.kw-day .kw-dnum { font-size: .78rem; display: block; margin-top: .1rem; }
.kw-day .kw-dmark { font-size: .78rem; display: block; height: 1em; margin-top: .15rem; }
.kw-day.done { border-color: #C9962E; color: #F5CD6B; }
.kw-day.today {
  background: linear-gradient(160deg, #7C3AED, #4C1D95);
  border-color: #E9B44C; color: #FFF;
}
.kw-day.rest { opacity: .55; }

.kw-feature { padding: .2rem .1rem; }
.kw-feature .kw-ficon { font-size: 1.45rem; }
.kw-feature .kw-ftitle { font-weight: 700; font-size: 1.02rem; margin: .25rem 0 .15rem 0; }
.kw-feature .kw-ftext { color: #B9B9CC; font-size: .93rem; line-height: 1.35; }

.kw-price { text-align: center; padding: .4rem 0 .2rem 0; }
.kw-price .kw-amount { font-size: 2.6rem; font-weight: 800; color: #FFF; line-height: 1; }
.kw-price .kw-per { color: #A8A8BE; font-size: 1rem; font-weight: 600; }

.kw-land-hero { text-align: center; padding: 1.2rem .4rem .2rem .4rem; }
.kw-land-hero .kw-land-icon { font-size: 3rem; }
.kw-land-hero .kw-land-name {
  font-size: 2.4rem; font-weight: 800; letter-spacing: .02em; color: #FFF;
  line-height: 1.1; margin-top: .2rem;
}
.kw-land-hero .kw-land-name span { color: #E9B44C; }
.kw-land-hero .kw-land-tag {
  font-size: 1.15rem; font-weight: 600; color: #C9A7F5; margin-top: .35rem;
}
.kw-land-hero .kw-land-frame { color: #B9B9CC; max-width: 34rem; margin: .7rem auto 0 auto; }

.kw-exhead { display: flex; align-items: baseline; gap: .55rem; flex-wrap: wrap; }
.kw-exhead .kw-exname { font-size: 1.12rem; font-weight: 700; color: #FFF; }
.kw-exhead .kw-exnum { color: #E9B44C; font-weight: 800; }
.kw-footer { text-align: center; color: #83839C; font-size: .85rem; margin-top: 1.4rem; }
</style>
"""


def inject_css():
    st.markdown(CSS, unsafe_allow_html=True)


def _esc(text):
    return _html.escape(str(text))


def topbar_html(icon, name_a, name_b, member_name=None, badge=None, badge_purple=False):
    """The identity bar: brand left, member chip right (when signed in)."""
    right = ""
    if member_name:
        initial = _esc((member_name.strip()[:1] or "?").upper())
        badge_html = ""
        if badge:
            cls = "kw-badge purple" if badge_purple else "kw-badge"
            badge_html = f'<span class="{cls}">{_esc(badge)}</span>'
        right = (
            f'<div class="kw-member"><div class="kw-avatar">{initial}</div>'
            f'<div class="kw-who"><div class="kw-mname">{_esc(member_name)}</div>'
            f"{badge_html}</div></div>"
        )
    return (
        f'<div class="kw-topbar"><div class="kw-brand">'
        f'<div class="kw-icon">{icon}</div>'
        f'<div class="kw-name">{_esc(name_a)} <span>{_esc(name_b)}</span></div>'
        f"</div>{right}</div>"
    )


def hero_html(kicker, title, focus=None, chips=()):
    """The Today's Workout hero card body (buttons are real widgets,
    rendered by the caller inside the same bordered container)."""
    focus_html = f'<div class="kw-focus">{_esc(focus)}</div>' if focus else ""
    chips_html = ""
    if chips:
        inner = "".join(
            f'<span class="kw-chip{" gold" if gold else ""}">{_esc(text)}</span>'
            for text, gold in chips
        )
        chips_html = f'<div class="kw-chips">{inner}</div>'
    return (
        f'<div class="kw-hero"><div class="kw-kicker">{_esc(kicker)}</div>'
        f'<div class="kw-title">{_esc(title)}</div>{focus_html}{chips_html}</div>'
    )


def week_strip_html(days):
    """days: list of dicts {letter, num, state, mark} — state is one of
    'done', 'today', 'rest', '' (upcoming)."""
    cells = []
    for d in days:
        cls = f'kw-day {d.get("state", "")}'.strip()
        cells.append(
            f'<div class="{cls}"><span class="kw-dletter">{_esc(d["letter"])}</span>'
            f'<span class="kw-dnum">{_esc(d["num"])}</span>'
            f'<span class="kw-dmark">{_esc(d.get("mark", ""))}</span></div>'
        )
    return f'<div class="kw-week">{"".join(cells)}</div>'
