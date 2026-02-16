import streamlit as st
import pandas as pd
import joblib
import re
from pathlib import Path

# ---------------- Page ----------------
st.set_page_config(page_title="IPL Winner Predictor", page_icon="🏏", layout="centered")

ASSETS = Path("assets")

# ---------------- Team Logos (OFFLINE) ----------------
TEAM_LOGO = {
    "Chennai Super Kings": ASSETS / "csk.png",
    "Mumbai Indians": ASSETS / "mi.png",
    "Royal Challengers Bengaluru": ASSETS / "rcb.png",
    "Kolkata Knight Riders": ASSETS / "kkr.png",
    "Rajasthan Royals": ASSETS / "rr.png",
    "Sunrisers Hyderabad": ASSETS / "srh.png",
    "Delhi Capitals": ASSETS / "dc.png",
    "Punjab Kings": ASSETS / "pbks.png",
    "Gujarat Titans": ASSETS / "gt.png",
    "Lucknow Super Giants": ASSETS / "lsg.png",
}

TEAM_COLORS = {
    "Chennai Super Kings": "#F9CD05",
    "Mumbai Indians": "#005DAA",
    "Royal Challengers Bengaluru": "#D71920",
    "Kolkata Knight Riders": "#3A225D",
    "Rajasthan Royals": "#EA1A8E",
    "Sunrisers Hyderabad": "#F26B1D",
    "Delhi Capitals": "#1E88E5",
    "Punjab Kings": "#D71920",
    "Gujarat Titans": "#0B1F3A",
    "Lucknow Super Giants": "#00AEEF",
}

def team_color(team): 
    return TEAM_COLORS.get(team, "#A78BFA")

def team_logo_path(team):
    p = TEAM_LOGO.get(team)
    return p if p and p.exists() else None

# ---------------- IPL / CRICKET CSS ----------------
st.markdown("""
<style>
.stApp{
  background:
    radial-gradient(circle at 10% 20%, rgba(255, 215, 0, 0.12), transparent 35%),
    radial-gradient(circle at 90% 15%, rgba(168, 85, 247, 0.18), transparent 38%),
    radial-gradient(circle at 50% 95%, rgba(0, 191, 255, 0.10), transparent 45%),
    linear-gradient(180deg, #070818 0%, #090A1C 45%, #04050F 100%);
  color: #e5e7eb;
}
.block-container{ padding-top: 1.4rem; padding-bottom: 2.8rem; max-width: 1100px; }

.banner{
  border-radius: 22px;
  padding: 18px 18px 16px 18px;
  background:
    linear-gradient(90deg, rgba(168,85,247,0.18), rgba(255,215,0,0.12)),
    rgba(255,255,255,0.05);
  border: 1px solid rgba(255,255,255,0.12);
  box-shadow: 0 18px 44px rgba(0,0,0,0.40);
  backdrop-filter: blur(10px);
  position: relative;
  overflow: hidden;
}
.banner:before{
  content:"";
  position:absolute; top:-140px; left:-120px;
  width:320px; height:320px;
  background: radial-gradient(circle, rgba(255,215,0,0.20), transparent 62%);
}
.banner:after{
  content:"";
  position:absolute; bottom:-160px; right:-140px;
  width:360px; height:360px;
  background: radial-gradient(circle, rgba(168,85,247,0.24), transparent 62%);
}
.badge{
  display:inline-block;
  padding: 6px 12px;
  border-radius: 999px;
  font-size: 0.85rem;
  background: rgba(255,215,0,0.14);
  border: 1px solid rgba(255,215,0,0.28);
  color: #ffe58f;
  font-weight: 900;
  letter-spacing: 0.3px;
}
.title{ font-size: 2.25rem; font-weight: 950; margin: 0.3rem 0 0.2rem 0; }
.sub{ color: rgba(229,231,235,0.76); margin: 0; font-size: 1rem; }

.pitch{
  margin-top: 14px;
  border-radius: 22px;
  padding: 18px;
  background:
    linear-gradient(90deg,
      rgba(16,185,129,0.12) 0%,
      rgba(16,185,129,0.06) 12%,
      rgba(16,185,129,0.12) 24%,
      rgba(16,185,129,0.06) 36%,
      rgba(16,185,129,0.12) 48%,
      rgba(16,185,129,0.06) 60%,
      rgba(16,185,129,0.12) 72%,
      rgba(16,185,129,0.06) 84%,
      rgba(16,185,129,0.12) 100%),
    rgba(255,255,255,0.05);
  border: 1px solid rgba(255,255,255,0.11);
  box-shadow: 0 16px 40px rgba(0,0,0,0.30);
  backdrop-filter: blur(10px);
  position: relative;
  overflow: hidden;
}
.pitch:before{
  content:"";
  position:absolute;
  left: 6%;
  right: 6%;
  top: 54%;
  height: 2px;
  background: rgba(255,255,255,0.16);
}

.teamCard{
  border-radius: 18px;
  padding: 14px;
  background: rgba(0,0,0,0.22);
  border: 1px solid rgba(255,255,255,0.10);
}

.vs{
  text-align:center;
  font-size: 1.3rem;
  font-weight: 950;
  color: rgba(255,215,0,0.95);
  padding-top: 1.9rem;
  text-shadow: 0 0 18px rgba(255,215,0,0.22);
}

div[data-baseweb="select"] > div,
div[data-baseweb="input"] > div { border-radius: 14px !important; }

.stButton button{
  width: 100%;
  border-radius: 16px;
  padding: 0.95rem 1rem;
  font-weight: 950;
  letter-spacing: 0.5px;
  border: 1px solid rgba(255,255,255,0.16);
  background: linear-gradient(90deg, rgba(168,85,247,0.96), rgba(255,215,0,0.92));
  color: #070818;
  box-shadow: 0 16px 34px rgba(168,85,247,0.20);
}

.scoreboard{
  margin-top: 14px;
  border-radius: 18px;
  padding: 14px;
  background: rgba(255,255,255,0.05);
  border: 1px solid rgba(255,255,255,0.10);
  box-shadow: 0 12px 32px rgba(0,0,0,0.28);
  backdrop-filter: blur(10px);
}

.trophy{
  margin-top: 14px;
  border-radius: 22px;
  padding: 16px;
  background:
    radial-gradient(circle at 20% 30%, rgba(255,215,0,0.18), transparent 55%),
    rgba(255,255,255,0.05);
  border: 1px solid rgba(255,215,0,0.25);
}

.small{ color: rgba(229,231,235,0.74); font-size: 0.92rem; }
.footer{ margin-top: 18px; color: rgba(229,231,235,0.55); font-size: 0.9rem; text-align:center; }
</style>
""", unsafe_allow_html=True)

# ---------------- Load model files ----------------
@st.cache_resource
def load_artifacts():
    model = joblib.load("ipl_model.pkl")
    scaler = joblib.load("season_scaler.pkl")
    x_cols = joblib.load("x_cols.pkl")
    return model, scaler, x_cols

model, scaler, X_COLS = load_artifacts()

# ---------------- Helpers ----------------
def options_from_prefix(prefix: str):
    p = prefix + "_"
    return sorted({c.replace(p, "", 1) for c in X_COLS if c.startswith(p)})

def build_X(season, team1, team2, venue, toss_winner, player_of_match):
    raw = pd.DataFrame([{
        "season": int(season),
        "team1": team1,
        "team2": team2,
        "venue": venue,
        "toss_winner": toss_winner,
        "player_of_match": player_of_match
    }])
    df = pd.get_dummies(raw, columns=["team1","team2","venue","toss_winner","player_of_match"])
    for col in X_COLS:
        if col not in df.columns:
            df[col] = 0
    df = df[X_COLS]
    df["season"] = scaler.transform(df[["season"]])
    return df

def clean_winner_label(label):
    return re.sub(r"^winner_", "", str(label))

# Dropdowns
TEAM1 = options_from_prefix("team1")
TEAM2 = options_from_prefix("team2")
VENUES = options_from_prefix("venue")
TOSS = options_from_prefix("toss_winner")
POM = options_from_prefix("player_of_match")

# ---------------- Header (with offline IPL logo if exists) ----------------
logo_path = ASSETS / "ipl_logo.png"
left, right = st.columns([0.12, 0.88])
with left:
    if logo_path.exists():
        st.image(str(logo_path), use_container_width=True)
with right:
    st.markdown("""
    <div class="banner">
      <span class="badge">🏏 IPL • MATCH PREDICTOR</span>
      <div class="title">IPL Winner Predictor</div>
      <p class="sub">Pitch Mode • Scoreboard Probabilities • Trophy Winner Card</p>
    </div>
    """, unsafe_allow_html=True)

# ---------------- Pitch Form ----------------
st.markdown('<div class="pitch">', unsafe_allow_html=True)

c1, c2, c3 = st.columns([1, 0.35, 1])

with c1:
    st.markdown(f"""
    <div class="teamCard" style="border-left:6px solid {team_color(TEAM1[0] if TEAM1 else '')};">
      <div style="font-weight:950;">🛡️ Team 1</div>
      <div class="small">Choose batting/fielding team</div>
    </div>
    """, unsafe_allow_html=True)

    team1 = st.selectbox("Team 1", TEAM1, index=0)

    lp = team_logo_path(team1)
    if lp:
        st.image(str(lp), width=110)

with c2:
    st.markdown('<div class="vs">VS</div>', unsafe_allow_html=True)

with c3:
    st.markdown(f"""
    <div class="teamCard" style="border-left:6px solid {team_color(TEAM2[0] if TEAM2 else '')};">
      <div style="font-weight:950;">🛡️ Team 2</div>
      <div class="small">Choose opponent team</div>
    </div>
    """, unsafe_allow_html=True)

    team2_list = [t for t in TEAM2 if t != team1] or TEAM2
    team2 = st.selectbox("Team 2", team2_list, index=0)

    lp = team_logo_path(team2)
    if lp:
        st.image(str(lp), width=110)

st.write("")
a, b = st.columns(2)
with a:
    season = st.number_input("📅 Season (Year)", min_value=2008, max_value=2100, value=2024, step=1)
    venue = st.selectbox("🏟️ Venue", VENUES, index=0)

with b:
    toss_winner = st.selectbox("🪙 Toss Winner", TOSS, index=0)
    player_of_match = st.selectbox("⭐ Player of Match", POM, index=0)

st.write("")
go = st.button("🏆 PREDICT WINNER")
st.markdown("</div>", unsafe_allow_html=True)

# ---------------- Prediction ----------------
if go:
    if team1 == team2:
        st.warning("Team 1 and Team 2 cannot be same.")
    else:
        X = build_X(season, team1, team2, venue, toss_winner, player_of_match)

        pred_label = model.predict(X)[0]
        winner = clean_winner_label(pred_label)

        # Trophy Card
        st.markdown(f"""
        <div class="trophy">
          <div style="display:flex; justify-content:space-between; gap:14px; flex-wrap:wrap;">
            <div>
              <div style="font-size:1.05rem; font-weight:950;">🏆 Predicted Winner</div>
              <div style="font-size:1.55rem; font-weight:980; margin-top:2px;">{winner}</div>
              <div class="small">Match: {team1} vs {team2}</div>
              <div class="small">Venue: {venue} • Season: {season}</div>
            </div>
            <div style="text-align:right;">
              <div class="small">Toss: {toss_winner}</div>
              <div class="small">POM: {player_of_match}</div>
            </div>
          </div>
        </div>
        """, unsafe_allow_html=True)

        # Scoreboard Probabilities
        if hasattr(model, "predict_proba"):
            probs = model.predict_proba(X)[0]
            classes = list(model.classes_)
            top_idx = sorted(range(len(probs)), key=lambda i: probs[i], reverse=True)[:3]

            st.markdown('<div class="scoreboard">', unsafe_allow_html=True)
            st.markdown("### 📊 Scoreboard: Win Probability (Top 3)")
            for i in top_idx:
                tname = clean_winner_label(classes[i])
                pct = float(probs[i]) * 100.0
                st.write(f"**{tname}** — {pct:.2f}%")
                st.progress(min(max(pct/100.0, 0.0), 1.0))
            st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<div class="footer">✨ IPL Cricket Theme (Offline Logos) • Streamlit</div>', unsafe_allow_html=True)