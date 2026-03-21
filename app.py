import streamlit as st
import joblib
import numpy as np
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import hashlib

# ──────────────────────────────────────────────────────
# PAGE CONFIG  (must be first Streamlit call)
# ──────────────────────────────────────────────────────
st.set_page_config(
    page_title="Intelligent Air Quality Analysis",
    page_icon="🌍",
    layout="centered"
)

# ──────────────────────────────────────────────────────
# CSS
# ──────────────────────────────────────────────────────
st.markdown("""
<style>
body, [data-testid="stAppViewContainer"], [data-testid="stMain"] {
    background-color: #0e1117;
    color: #ffffff;
}
[data-testid="stHeader"] { background: transparent; }
#MainMenu, footer { visibility: hidden; }

div.stButton > button {
    background: linear-gradient(135deg, #00b09b, #96c93d);
    color: white;
    border: none;
    border-radius: 10px;
    padding: 0.6rem 1.2rem;
    font-weight: 700;
    font-size: 1rem;
    width: 100%;
    cursor: pointer;
}
div.stButton > button:hover { opacity: 0.85; }

.result-box {
    border-radius: 12px;
    padding: 1.2rem 1.5rem;
    text-align: center;
    margin: 1rem 0;
    font-size: 1.4rem;
    font-weight: 800;
    color: #ffffff;
}
.good        { background: #1a7a3c; }
.moderate    { background: #7a6500; }
.sensitive   { background: #8a5000; }
.unhealthy   { background: #8a1000; }
.very        { background: #5a0080; }
.hazardous   { background: #3a0000; border: 2px solid #ff4444; }

.metric-card {
    background: rgba(255,255,255,0.07);
    border: 1px solid rgba(255,255,255,0.12);
    border-radius: 14px;
    padding: 1.2rem 1rem;
    text-align: center;
    margin-bottom: 0.5rem;
}
.metric-card .m-label {
    font-size: 0.78rem;
    font-weight: 600;
    color: rgba(255,255,255,0.5);
    text-transform: uppercase;
    letter-spacing: 1px;
}
.metric-card .m-value {
    font-size: 2rem;
    font-weight: 800;
    color: #96c93d;
    margin-top: 0.3rem;
}
.metric-card .m-sub {
    font-size: 0.78rem;
    color: rgba(255,255,255,0.35);
    margin-top: 0.2rem;
}
.nav-tab {
    display: inline-block;
    padding: 0.4rem 1.1rem;
    border-radius: 20px;
    font-size: 0.85rem;
    font-weight: 600;
    cursor: pointer;
    margin-right: 0.4rem;
    border: 1px solid rgba(255,255,255,0.15);
    color: rgba(255,255,255,0.6);
    background: transparent;
}
.nav-tab.active {
    background: linear-gradient(135deg, #00b09b, #96c93d);
    color: white;
    border-color: transparent;
}
</style>
""", unsafe_allow_html=True)

# ──────────────────────────────────────────────────────
# USER STORE
# ──────────────────────────────────────────────────────
def _h(p): return hashlib.sha256(p.encode()).hexdigest()

if "users" not in st.session_state:
    st.session_state.users = {"admin": _h("admin123"), "demo": _h("demo123")}

# ──────────────────────────────────────────────────────
# SESSION DEFAULTS
# ──────────────────────────────────────────────────────
for k, v in [("logged_in", False), ("username", ""),
             ("page", "login"), ("result", None), ("msg", ""),
             ("active_tab", "predict")]:
    if k not in st.session_state:
        st.session_state[k] = v

# ──────────────────────────────────────────────────────
# LOAD MODELS
# ──────────────────────────────────────────────────────
@st.cache_resource
def load_models():
    return (joblib.load("rf_model.pkl"),
            joblib.load("gb_model.pkl"),
            joblib.load("scaler.pkl"),
            joblib.load("label_encoder.pkl"))

try:
    rf, gb, sc, le = load_models()
    models_ok = True
except Exception as e:
    models_ok = False
    model_error = str(e)

# ──────────────────────────────────────────────────────
# HELPERS
# ──────────────────────────────────────────────────────
COLOR_MAP = {
    "Good": "good",
    "Moderate": "moderate",
    "Unhealthy for Sensitive Groups": "sensitive",
    "Unhealthy": "unhealthy",
    "Very Unhealthy": "very",
    "Hazardous": "hazardous",
}
ICON_MAP = {
    "Good": "🟢", "Moderate": "🟡",
    "Unhealthy for Sensitive Groups": "🟠",
    "Unhealthy": "🔴", "Very Unhealthy": "🟣", "Hazardous": "⚫",
}

def predict(pm25, pm10, no2, so2, co, temp):
    import pandas as pd
    x = pd.DataFrame([[pm25, pm10, no2, so2, co, temp]],
                     columns=["PM2.5","PM10","NO2","SO2","CO","Temperature"])
    xs = sc.transform(x)
    prob = (rf.predict_proba(xs) + gb.predict_proba(xs)) / 2
    return le.inverse_transform([prob.argmax(axis=1)[0]])[0]

def send_email(name, to_email, result):
    try:
        sender = "Shrika2005@gmail.com"
        pw     = "hcamivojwnjqxiyd"
        msg    = MIMEMultipart()
        msg["From"]    = sender
        msg["To"]      = to_email
        msg["Subject"] = "Your AQI Prediction Report"
        body = f"""Hello {name},

Your Air Quality Prediction Result: {ICON_MAP.get(result,'')} {result}

What this means:
- Good: Air quality is satisfactory.
- Moderate: Acceptable; minor risk for sensitive people.
- Unhealthy for Sensitive Groups: At-risk groups should reduce outdoor activity.
- Unhealthy: Everyone may begin to experience effects.
- Very Unhealthy: Health alert for everyone.
- Hazardous: Emergency conditions.

Stay safe!
— AQI Detection System
"""
        msg.attach(MIMEText(body, "plain"))
        s = smtplib.SMTP("smtp.gmail.com", 587)
        s.starttls()
        s.login(sender, pw)
        s.send_message(msg)
        s.quit()
        return True, "✅ Report sent successfully!"
    except Exception as e:
        return False, f"❌ Email failed: {e}"

# ──────────────────────────────────────────────────────
# MODEL PERFORMANCE (computed once, cached)
# ──────────────────────────────────────────────────────
@st.cache_resource
def compute_performance():
    import pandas as pd
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import (accuracy_score, precision_score,
                                  recall_score, f1_score, confusion_matrix,
                                  classification_report)

    try:
        df = pd.read_csv("aqi_dataset.csv")

        feature_cols = ["PM2.5", "PM10", "NO2", "SO2", "CO", "Temperature"]
        X = df[feature_cols]
        y = df["AQI_Category"] if "AQI_Category" in df.columns else df[df.columns[-1]]

        X_scaled = sc.transform(X)
        y_enc    = le.transform(y)

        _, X_test, _, y_test = train_test_split(
            X_scaled, y_enc, test_size=0.2, random_state=42)

        rf_pred  = rf.predict(X_test)
        gb_pred  = gb.predict(X_test)
        rf_prob  = rf.predict_proba(X_test)
        gb_prob  = gb.predict_proba(X_test)
        hy_prob  = (rf_prob + gb_prob) / 2
        hy_pred  = hy_prob.argmax(axis=1)

        results = {}
        for name, pred in [("Random Forest", rf_pred),
                            ("Gradient Boosting", gb_pred),
                            ("Hybrid Ensemble", hy_pred)]:
            results[name] = {
                "accuracy":  round(accuracy_score(y_test, pred) * 100, 2),
                "precision": round(precision_score(y_test, pred, average="weighted", zero_division=0) * 100, 2),
                "recall":    round(recall_score(y_test, pred, average="weighted", zero_division=0) * 100, 2),
                "f1":        round(f1_score(y_test, pred, average="weighted", zero_division=0) * 100, 2),
            }

        classes = le.classes_
        cm      = confusion_matrix(y_test, hy_pred)
        report  = classification_report(y_test, hy_pred,
                                        target_names=classes, output_dict=True)
        return results, classes, cm, report, None

    except Exception as e:
        return None, None, None, None, str(e)

# ══════════════════════════════════════════════════════
# PAGE: LOGIN
# ══════════════════════════════════════════════════════
def page_login():
    st.markdown("## 🌍 AQI Detection System")
    st.markdown("---")
    st.markdown("### 🔐 Sign In")

    if st.session_state.msg:
        st.success(st.session_state.msg)
        st.session_state.msg = ""

    username = st.text_input("Username", placeholder="Enter username")
    password = st.text_input("Password", type="password", placeholder="Enter password")
    st.markdown("")

    if st.button("Sign In"):
        if not username or not password:
            st.error("Please fill in both fields.")
        elif st.session_state.users.get(username) == _h(password):
            st.session_state.logged_in = True
            st.session_state.username  = username
            st.session_state.page      = "app"
            st.rerun()
        else:
            st.error("❌ Wrong username or password.")

    st.markdown("---")
    st.caption("No account?")
    if st.button("Create Account →"):
        st.session_state.page = "register"
        st.rerun()

    st.markdown("")
    st.info("💡 Demo:  **admin** / admin123   |   **demo** / demo123")

# ══════════════════════════════════════════════════════
# PAGE: REGISTER
# ══════════════════════════════════════════════════════
def page_register():
    st.markdown("## 🌍 AQI Detection System")
    st.markdown("---")
    st.markdown("### 📝 Create Account")

    uname = st.text_input("Choose a Username")
    email = st.text_input("Email Address")
    pw1   = st.text_input("Password",         type="password")
    pw2   = st.text_input("Confirm Password", type="password")
    st.markdown("")

    if st.button("Create Account"):
        if not uname or not email or not pw1 or not pw2:
            st.error("Please fill in all fields.")
        elif len(pw1) < 6:
            st.error("Password must be at least 6 characters.")
        elif pw1 != pw2:
            st.error("Passwords do not match.")
        elif uname in st.session_state.users:
            st.error("Username already taken.")
        else:
            st.session_state.users[uname] = _h(pw1)
            st.session_state.msg  = f"✅ Account created! Welcome, {uname}. Please sign in."
            st.session_state.page = "login"
            st.rerun()

    st.markdown("---")
    if st.button("← Back to Sign In"):
        st.session_state.page = "login"
        st.rerun()

# ══════════════════════════════════════════════════════
# PAGE: MAIN APP  (shown after login)
# ══════════════════════════════════════════════════════
def page_app():
    # ── navbar ──
    col1, col2 = st.columns([8, 2])
    with col1:
        st.markdown("## 🌍 AQI Detection System")
        st.caption(f"Logged in as **{st.session_state.username}**")
    with col2:
        st.markdown("")
        st.markdown("")
        if st.button("Sign Out"):
            st.session_state.logged_in   = False
            st.session_state.username    = ""
            st.session_state.page        = "login"
            st.session_state.result      = None
            st.session_state.active_tab  = "predict"
            st.rerun()

    st.markdown("---")

    if not models_ok:
        st.error(f"⚠️ Could not load models: {model_error}")
        st.info("Make sure you ran `python3 main.py` first and all .pkl files are in the same folder as app.py.")
        return

    # ── Tab navigation ──
    t1, t2 = st.columns(2)
    with t1:
        if st.button("🔍 Predict AQI", key="tab_predict"):
            st.session_state.active_tab = "predict"
    with t2:
        if st.button("📈 Model Performance", key="tab_perf"):
            st.session_state.active_tab = "performance"

    st.markdown("---")

    # ════════════════════════════════
    # TAB 1 — PREDICT
    # ════════════════════════════════
    if st.session_state.active_tab == "predict":

        st.markdown("### 📊 Enter Pollutant Values")
        st.caption("Fill in the measurements below and click Predict.")

        col_a, col_b = st.columns(2)
        with col_a:
            pm25 = st.number_input("PM2.5 (μg/m³)",   min_value=0.0,   max_value=600.0, value=10.0, step=0.1)
            pm10 = st.number_input("PM10 (μg/m³)",    min_value=0.0,   max_value=700.0, value=20.0, step=0.1)
            no2  = st.number_input("NO2 (ppb)",        min_value=0.0,   max_value=300.0, value=15.0, step=0.1)
        with col_b:
            so2  = st.number_input("SO2 (ppb)",        min_value=0.0,   max_value=300.0, value=10.0, step=0.1)
            co   = st.number_input("CO (ppm)",          min_value=0.0,   max_value=60.0,  value=1.0,  step=0.01)
            temp = st.number_input("Temperature (°C)", min_value=-50.0, max_value=60.0,  value=25.0, step=0.1)

        st.markdown("")
        if st.button("🔍 Predict AQI Category"):
            with st.spinner("Analysing pollutant values..."):
                st.session_state.result = predict(pm25, pm10, no2, so2, co, temp)

        if st.session_state.result:
            r   = st.session_state.result
            css = COLOR_MAP.get(r, "good")
            ico = ICON_MAP.get(r, "🔵")
            st.markdown(
                f'<div class="result-box {css}">{ico}&nbsp; Predicted Category: {r}</div>',
                unsafe_allow_html=True
            )

        st.markdown("---")

        # ── EMAIL ──
        st.markdown("### 📧 Send Report via Email")
        st.caption("Enter your details below to receive the prediction report in your inbox.")

        col_c, col_d = st.columns(2)
        with col_c:
            name     = st.text_input("Your Name",     placeholder="e.g. Ravi Kumar")
        with col_d:
            to_email = st.text_input("Email Address", placeholder="you@example.com")

        st.markdown("")
        if st.button("📨 Send Report"):
            if not st.session_state.result:
                st.warning("⚠️ Please run a prediction first.")
            elif not name or not to_email:
                st.error("Please enter your name and email address.")
            else:
                with st.spinner("Sending email..."):
                    ok, msg = send_email(name, to_email, st.session_state.result)
                if ok:
                    st.success(msg)
                else:
                    st.error(msg)

        st.markdown("---")

        # ── AQI REFERENCE TABLE ──
        st.markdown("### 📋 AQI Category Reference")
        st.table({
            "Category": [
                "🟢 Good", "🟡 Moderate",
                "🟠 Unhealthy for Sensitive Groups",
                "🔴 Unhealthy", "🟣 Very Unhealthy", "⚫ Hazardous"
            ],
            "PM2.5 (μg/m³)": [
                "0 – 12", "12.1 – 35.4", "35.5 – 55.4",
                "55.5 – 150.4", "150.5 – 250.4", "250.5+"
            ],
            "Health Impact": [
                "Air quality is satisfactory",
                "Acceptable; minor risk for sensitive people",
                "Sensitive groups may experience effects",
                "General public may experience effects",
                "Health alert — serious effects for all",
                "Emergency conditions — everyone affected"
            ]
        })

    # ════════════════════════════════
    # TAB 2 — MODEL PERFORMANCE
    # ════════════════════════════════
    elif st.session_state.active_tab == "performance":

        st.markdown("### 📈 Model Performance Dashboard")
        st.caption("Evaluated on 20% held-out test data using the hybrid ensemble approach.")

        with st.spinner("Computing model metrics..."):
            results, classes, cm, report, err = compute_performance()

        if err:
            st.error(f"⚠️ Could not compute metrics: {err}")
            st.info("Make sure **aqi_dataset.csv** is in the same folder as app.py.")
            return

        # ── Accuracy cards for all 3 models ──
        st.markdown("#### 🏆 Model Accuracy Comparison")
        c1, c2, c3 = st.columns(3)
        for col, (model_name, emoji) in zip(
            [c1, c2, c3],
            [("Random Forest","🌲"), ("Gradient Boosting","⚡"), ("Hybrid Ensemble","🔬")]
        ):
            with col:
                acc = results[model_name]["accuracy"]
                st.markdown(
                    f'<div class="metric-card">'
                    f'<div class="m-label">{emoji} {model_name}</div>'
                    f'<div class="m-value">{acc}%</div>'
                    f'<div class="m-sub">Accuracy</div>'
                    f'</div>',
                    unsafe_allow_html=True
                )

        st.markdown("---")

        # ── Detailed metrics for Hybrid ──
        st.markdown("#### 🔬 Hybrid Ensemble — Detailed Metrics")
        hm = results["Hybrid Ensemble"]
        m1, m2, m3, m4 = st.columns(4)
        for col, label, val, emoji in zip(
            [m1, m2, m3, m4],
            ["Accuracy", "Precision", "Recall", "F1-Score"],
            [hm["accuracy"], hm["precision"], hm["recall"], hm["f1"]],
            ["🎯", "🔍", "📡", "⚖️"]
        ):
            with col:
                st.markdown(
                    f'<div class="metric-card">'
                    f'<div class="m-label">{emoji} {label}</div>'
                    f'<div class="m-value">{val}%</div>'
                    f'</div>',
                    unsafe_allow_html=True
                )

        st.markdown("---")

        # ── Per-class metrics table ──
        st.markdown("#### 📊 Per-Class Performance (Hybrid Ensemble)")
        import pandas as pd
        rows = []
        for cls in classes:
            if cls in report:
                r = report[cls]
                rows.append({
                    "Category":  cls,
                    "Precision": f"{r['precision']*100:.1f}%",
                    "Recall":    f"{r['recall']*100:.1f}%",
                    "F1-Score":  f"{r['f1-score']*100:.1f}%",
                    "Support":   int(r['support'])
                })
        st.table(pd.DataFrame(rows))

        st.markdown("---")

        # ── Confusion Matrix ──
        st.markdown("#### 🔢 Confusion Matrix (Hybrid Ensemble)")
        st.caption("Rows = Actual class &nbsp;|&nbsp; Columns = Predicted class")
        cm_df = pd.DataFrame(cm, index=classes, columns=classes)
        st.dataframe(cm_df.style.background_gradient(cmap="Greens"), use_container_width=True)

        st.markdown("---")

        # ── Full comparison table ──
        st.markdown("#### 📋 All Models — Full Comparison")
        comp_rows = []
        for m in ["Random Forest", "Gradient Boosting", "Hybrid Ensemble"]:
            comp_rows.append({
                "Model":     m,
                "Accuracy":  f"{results[m]['accuracy']}%",
                "Precision": f"{results[m]['precision']}%",
                "Recall":    f"{results[m]['recall']}%",
                "F1-Score":  f"{results[m]['f1']}%",
            })
        st.table(pd.DataFrame(comp_rows))


# ══════════════════════════════════════════════════════
# ROUTER
# ══════════════════════════════════════════════════════
if not st.session_state.logged_in:
    if st.session_state.page == "register":
        page_register()
    else:
        page_login()
else:
    page_app()