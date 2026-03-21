import streamlit as st
import joblib
import numpy as np
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import hashlib

# ─────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="AQI Prediction System",
    page_icon="🌍",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# ─────────────────────────────────────────────
# CSS
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap');

*, *::before, *::after { box-sizing: border-box; margin: 0; }

html, body,
[data-testid="stAppViewContainer"],
[data-testid="stMain"],
section.main {
    background: linear-gradient(135deg, #0f2027 0%, #203a43 50%, #2c5364 100%) !important;
    min-height: 100vh;
    font-family: 'Inter', sans-serif;
    color: #fff;
}

[data-testid="stHeader"],
[data-testid="stToolbar"],
[data-testid="stDecoration"] { display: none !important; }
#MainMenu, footer { visibility: hidden; }

[data-testid="stMainBlockContainer"] {
    padding-top: 1.5rem !important;
    padding-bottom: 2rem !important;
    max-width: 860px;
}

/* ── Inputs ── */
[data-testid="stTextInput"] label,
[data-testid="stNumberInput"] label {
    color: rgba(255,255,255,0.82) !important;
    font-weight: 600 !important;
    font-size: 0.85rem !important;
    letter-spacing: 0.01em !important;
}
[data-testid="stTextInput"] input,
[data-testid="stNumberInput"] input {
    background: rgba(255,255,255,0.07) !important;
    border: 1px solid rgba(255,255,255,0.16) !important;
    border-radius: 10px !important;
    color: #fff !important;
    font-size: 0.93rem !important;
}
[data-testid="stTextInput"] input::placeholder,
[data-testid="stNumberInput"] input::placeholder {
    color: rgba(255,255,255,0.25) !important;
}
[data-testid="stTextInput"] input:focus,
[data-testid="stNumberInput"] input:focus {
    border-color: rgba(150,201,61,0.55) !important;
    box-shadow: 0 0 0 2px rgba(150,201,61,0.12) !important;
}

/* ── Default buttons (gradient) ── */
.stButton > button {
    background: linear-gradient(135deg, #00b09b, #96c93d) !important;
    color: #fff !important;
    border: none !important;
    border-radius: 12px !important;
    padding: 0.62rem 1.4rem !important;
    font-weight: 700 !important;
    font-size: 0.95rem !important;
    width: 100% !important;
    white-space: nowrap !important;
    transition: opacity 0.18s, transform 0.12s !important;
}
.stButton > button:hover { opacity: 0.87 !important; transform: translateY(-1px) !important; }

/* ── Sign-Out pill button (column key trick) ── */
[data-testid="stHorizontalBlock"] > div:last-child .stButton > button {
    background: rgba(255,255,255,0.09) !important;
    border: 1px solid rgba(255,255,255,0.22) !important;
    color: rgba(255,255,255,0.78) !important;
    font-size: 0.8rem !important;
    font-weight: 600 !important;
    padding: 0.32rem 1rem !important;
    border-radius: 20px !important;
    width: auto !important;
    white-space: nowrap !important;
    min-width: 80px !important;
}
[data-testid="stHorizontalBlock"] > div:last-child .stButton > button:hover {
    background: rgba(255,255,255,0.15) !important;
    transform: none !important;
}

/* ── Number input stepper buttons ── */
[data-testid="stNumberInput"] button {
    background: rgba(255,255,255,0.09) !important;
    border: 1px solid rgba(255,255,255,0.18) !important;
    color: #fff !important;
    width: auto !important;
    border-radius: 6px !important;
}

/* ── HR ── */
hr {
    border: none !important;
    border-top: 1px solid rgba(255,255,255,0.10) !important;
    margin: 1rem 0 !important;
}

/* ── Markdown text ── */
.stMarkdown p, [data-testid="stMarkdownContainer"] p {
    color: rgba(255,255,255,0.72) !important;
}
.stCaption, [data-testid="stCaptionContainer"] p {
    color: rgba(255,255,255,0.38) !important;
    font-size: 0.79rem !important;
}

/* ── Table ── */
[data-testid="stTable"] table {
    background: rgba(255,255,255,0.03) !important;
    color: rgba(255,255,255,0.82) !important;
}
[data-testid="stTable"] th {
    background: rgba(255,255,255,0.09) !important;
    color: #fff !important;
    font-weight: 700 !important;
}
[data-testid="stTable"] td { border-color: rgba(255,255,255,0.07) !important; }

/* ── AQI badge ── */
.aqi-result {
    border-radius: 14px;
    padding: 1.1rem 1.4rem;
    text-align: center;
    margin: 1rem 0 0.2rem 0;
}
.aqi-result .lbl {
    color: rgba(255,255,255,0.65);
    font-size: 0.72rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 1.8px;
}
.aqi-result .val {
    color: #fff;
    font-size: 1.6rem;
    font-weight: 800;
    margin-top: 0.35rem;
}
.aqi-hazardous { background: linear-gradient(135deg,#7b0000,#cc0000); }
.aqi-very      { background: linear-gradient(135deg,#6a0099,#9b27af); }
.aqi-unhealthy { background: linear-gradient(135deg,#a83200,#e05a00); }
.aqi-sensitive { background: linear-gradient(135deg,#7a5c00,#e6a817); }
.aqi-moderate  { background: linear-gradient(135deg,#7a6500,#d4b800); }
.aqi-good      { background: linear-gradient(135deg,#1a6b3c,#2ecc71); }

/* ── Section cards ── */
.sc {
    background: rgba(255,255,255,0.05);
    border: 1px solid rgba(255,255,255,0.09);
    border-radius: 16px;
    padding: 1.5rem 1.8rem 1.8rem;
    margin-bottom: 1.1rem;
}
.sc-title {
    color: rgba(255,255,255,0.9);
    font-size: 0.97rem;
    font-weight: 700;
    margin-bottom: 1rem;
}

/* ── Navbar HTML block ── */
.nb {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0.5rem 0 1rem 0;
    border-bottom: 1px solid rgba(255,255,255,0.09);
    margin-bottom: 1.2rem;
}
.nb-brand {
    font-size: 1.12rem;
    font-weight: 800;
    color: #fff;
}
.nb-right { display: flex; align-items: center; gap: 0.65rem; }
.ub {
    background: rgba(150,201,61,0.14);
    border: 1px solid rgba(150,201,61,0.32);
    border-radius: 20px;
    padding: 0.28rem 0.85rem;
    color: #96c93d;
    font-size: 0.8rem;
    font-weight: 700;
    white-space: nowrap;
}

/* ── Login ── */
.lt { font-size:1.9rem; font-weight:800; color:#fff; text-align:center; line-height:1.2; }
.ls { font-size:0.87rem; color:rgba(255,255,255,0.38); text-align:center; margin-top:0.25rem; margin-bottom:1.7rem; }
.dh { text-align:center; color:rgba(255,255,255,0.27); font-size:0.75rem; margin-top:0.5rem; }
.dh b { color:rgba(255,255,255,0.48); }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# SESSION STATE
# ─────────────────────────────────────────────
def hash_pw(pw):
    return hashlib.sha256(pw.encode()).hexdigest()

if "users" not in st.session_state:
    st.session_state.users = {
        "admin":  hash_pw("admin123"),
        "farmer": hash_pw("farmer123"),
    }

for k, v in [("logged_in",False),("username",""),("page","login"),
             ("prediction_result",None),("auth_message","")]:
    if k not in st.session_state:
        st.session_state[k] = v

def register_user(u, p):
    if u in st.session_state.users:
        return False, "Username already exists."
    st.session_state.users[u] = hash_pw(p)
    return True, "Account created! Please log in."

def verify_user(u, p):
    return st.session_state.users.get(u) == hash_pw(p)

# ─────────────────────────────────────────────
# LOAD MODELS
# ─────────────────────────────────────────────
@st.cache_resource
def load_models():
    return (joblib.load("rf_model.pkl"), joblib.load("gb_model.pkl"),
            joblib.load("scaler.pkl"),   joblib.load("label_encoder.pkl"))

rf_model, gb_model, scaler, label_encoder = load_models()

AQI_COLORS = {
    "Good":"aqi-good","Moderate":"aqi-moderate",
    "Unhealthy for Sensitive Groups":"aqi-sensitive",
    "Unhealthy":"aqi-unhealthy","Very Unhealthy":"aqi-very","Hazardous":"aqi-hazardous",
}
AQI_ICONS = {"Good":"🟢","Moderate":"🟡","Unhealthy for Sensitive Groups":"🟠",
             "Unhealthy":"🔴","Very Unhealthy":"🟣","Hazardous":"⚫"}

# ─────────────────────────────────────────────
# EMAIL
# ─────────────────────────────────────────────
def send_email(name, email, result):
    try:
        s_email = "Shrika2005@gmail.com"
        s_pw    = "hcamivojwnjqxiyd"
        msg = MIMEMultipart()
        msg["From"] = s_email; msg["To"] = email
        msg["Subject"] = "Your AQI Prediction Report"
        msg.attach(MIMEText(
            f"Hello {name},\n\nAQI Result: {AQI_ICONS.get(result,'')} {result}\n\n"
            f"Stay safe!\n— AQI Prediction System", "plain"))
        srv = smtplib.SMTP("smtp.gmail.com", 587)
        srv.starttls(); srv.login(s_email, s_pw)
        srv.send_message(msg); srv.quit()
        return True
    except Exception as e:
        return str(e)

# ═══════════════════════════════════════════════
# LOGIN
# ═══════════════════════════════════════════════
def page_login():
    _, col, _ = st.columns([1, 2, 1])
    with col:
        st.markdown('<div class="lt">🌍 AQI Prediction System</div>', unsafe_allow_html=True)
        st.markdown('<div class="ls">Sign in to continue</div>', unsafe_allow_html=True)

        if st.session_state.auth_message:
            st.success(st.session_state.auth_message)
            st.session_state.auth_message = ""

        username = st.text_input("Username", key="login_user", placeholder="Enter username")
        password = st.text_input("Password", type="password", key="login_pw", placeholder="Enter password")
        st.markdown("<br>", unsafe_allow_html=True)

        if st.button("Sign In", key="btn_login"):
            if not username or not password:
                st.error("Please fill in all fields.")
            elif verify_user(username, password):
                st.session_state.logged_in = True
                st.session_state.username  = username
                st.session_state.page      = "app"
                st.rerun()
            else:
                st.error("❌ Invalid username or password.")

        st.markdown("---")
        st.caption("Don't have an account?")
        if st.button("Create Account →", key="goto_register"):
            st.session_state.page = "register"
            st.rerun()

        st.markdown(
            "<div class='dh'>Demo: <b>admin</b> / admin123 &nbsp;|&nbsp; <b>farmer</b> / farmer123</div>",
            unsafe_allow_html=True)

# ═══════════════════════════════════════════════
# REGISTER
# ═══════════════════════════════════════════════
def page_register():
    _, col, _ = st.columns([1, 2, 1])
    with col:
        st.markdown('<div class="lt">🌍 Create Account</div>', unsafe_allow_html=True)
        st.markdown('<div class="ls">Join the AQI Prediction platform</div>', unsafe_allow_html=True)

        nu = st.text_input("Choose a Username", key="reg_user",  placeholder="e.g. john_doe")
        ne = st.text_input("Email Address",     key="reg_email", placeholder="you@example.com")
        p1 = st.text_input("Password",  type="password", key="reg_pw",  placeholder="Min 6 characters")
        p2 = st.text_input("Confirm Password", type="password", key="reg_pw2", placeholder="Repeat password")
        st.markdown("<br>", unsafe_allow_html=True)

        if st.button("Create Account", key="btn_register"):
            if not nu or not ne or not p1 or not p2:
                st.error("Please fill in all fields.")
            elif len(p1) < 6:
                st.error("Password must be at least 6 characters.")
            elif p1 != p2:
                st.error("Passwords do not match.")
            else:
                ok, msg = register_user(nu, p1)
                if ok:
                    st.session_state.auth_message = msg
                    st.session_state.page = "login"
                    st.rerun()
                else:
                    st.error(msg)

        st.markdown("---")
        st.caption("Already have an account?")
        if st.button("← Back to Sign In", key="goto_login"):
            st.session_state.page = "login"
            st.rerun()

# ═══════════════════════════════════════════════
# MAIN APP
# ═══════════════════════════════════════════════
def page_app():

    # ── Navbar: brand + user badge on left/center, Sign Out pill on right ──
    # Use 3 columns: brand (wide) | user badge (auto) | sign-out (narrow)
    c1, c2, c3 = st.columns([5, 2, 1])

    with c1:
        st.markdown(
            f'<div style="display:flex;align-items:center;gap:0.6rem;padding:0.4rem 0 0.6rem 0;">'
            f'<span style="font-size:1.12rem;font-weight:800;color:#fff;">🌍 AQI Prediction System</span>'
            f'</div>',
            unsafe_allow_html=True
        )
    with c2:
        st.markdown(
            f'<div class="ub" style="margin-top:0.4rem;">👤 {st.session_state.username}</div>',
            unsafe_allow_html=True
        )
    with c3:
        if st.button("Sign Out", key="btn_logout"):
            st.session_state.logged_in         = False
            st.session_state.username          = ""
            st.session_state.page              = "login"
            st.session_state.prediction_result = None
            st.rerun()

    st.markdown("<hr>", unsafe_allow_html=True)

    # ─── SECTION 1: PREDICTION ───
    st.markdown('<div class="sc">', unsafe_allow_html=True)
    st.markdown('<div class="sc-title">📊 Enter Pollutant Values</div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        pm25 = st.number_input("PM2.5 (μg/m³)",   min_value=0.0,   max_value=600.0, value=0.0,  step=0.1)
        pm10 = st.number_input("PM10 (μg/m³)",    min_value=0.0,   max_value=700.0, value=0.0,  step=0.1)
        no2  = st.number_input("NO2 (ppb)",        min_value=0.0,   max_value=300.0, value=0.0,  step=0.1)
    with col2:
        so2  = st.number_input("SO2 (ppb)",        min_value=0.0,   max_value=300.0, value=0.0,  step=0.1)
        co   = st.number_input("CO (ppm)",          min_value=0.0,   max_value=60.0,  value=0.0,  step=0.01)
        temp = st.number_input("Temperature (°C)", min_value=-50.0, max_value=60.0,  value=25.0, step=0.1)

    st.markdown("<br>", unsafe_allow_html=True)

    if st.button("🔍 Predict AQI Category", key="btn_predict"):
        features        = np.array([[pm25, pm10, no2, so2, co, temp]])
        features_scaled = scaler.transform(features)
        rf_prob         = rf_model.predict_proba(features_scaled)
        gb_prob         = gb_model.predict_proba(features_scaled)
        hybrid_prob     = (rf_prob + gb_prob) / 2
        predicted_class = int(hybrid_prob.argmax(axis=1)[0])
        st.session_state.prediction_result = label_encoder.inverse_transform([predicted_class])[0]

    if st.session_state.prediction_result:
        r   = st.session_state.prediction_result
        css = AQI_COLORS.get(r, "aqi-good")
        ico = AQI_ICONS.get(r, "🔵")
        st.markdown(
            f'<div class="aqi-result {css}">'
            f'<div class="lbl">Predicted Air Quality Category</div>'
            f'<div class="val">{ico} {r}</div>'
            f'</div>',
            unsafe_allow_html=True
        )

    st.markdown('</div>', unsafe_allow_html=True)

    # ─── SECTION 2: EMAIL ───
    st.markdown('<div class="sc">', unsafe_allow_html=True)
    st.markdown('<div class="sc-title">📧 Email Prediction Report</div>', unsafe_allow_html=True)

    ca, cb = st.columns(2)
    with ca:
        name  = st.text_input("Your Name",     key="email_name", placeholder="e.g. Ravi Kumar")
    with cb:
        email = st.text_input("Email Address", key="email_addr", placeholder="you@example.com")

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("📨 Send Email Report", key="btn_email"):
        if not st.session_state.prediction_result:
            st.warning("⚠️ Please run a prediction first.")
        elif not name or not email:
            st.error("Please enter your name and email address.")
        else:
            with st.spinner("Sending email..."):
                status = send_email(name, email, st.session_state.prediction_result)
            if status is True:
                st.success("✅ Report sent successfully!")
            else:
                st.error(f"❌ Email failed: {status}")

    st.markdown('</div>', unsafe_allow_html=True)

    # ─── SECTION 3: REFERENCE TABLE ───
    st.markdown('<div class="sc">', unsafe_allow_html=True)
    st.markdown('<div class="sc-title">📋 AQI Category Reference</div>', unsafe_allow_html=True)
    st.markdown("""
| Category | PM2.5 (μg/m³) | Health Implication |
|---|---|---|
| 🟢 Good | 0 – 12 | Air quality is satisfactory |
| 🟡 Moderate | 12.1 – 35.4 | Acceptable; some risk for sensitive people |
| 🟠 Unhealthy for Sensitive Groups | 35.5 – 55.4 | Sensitive groups may be affected |
| 🔴 Unhealthy | 55.5 – 150.4 | General public may experience effects |
| 🟣 Very Unhealthy | 150.5 – 250.4 | Health alert — serious effects |
| ⚫ Hazardous | 250.5+ | Emergency conditions |
""")
    st.markdown('</div>', unsafe_allow_html=True)


# ═══════════════════════════════════════════════
# ROUTER
# ═══════════════════════════════════════════════
if not st.session_state.logged_in:
    if st.session_state.page == "register":
        page_register()
    else:
        page_login()
else:
    page_app()