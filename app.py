import streamlit as st
import pandas as pd
import datetime
import json
import time

# ==========================================
# 1. PAGE CONFIGURATION & CSS (THE "LIQUID GLASS" LOOK)
# ==========================================

st.set_page_config(
    page_title="JEE WAR ROOM // PRO",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for Glassmorphism, Neon Glows, and Fonts
st.markdown("""
<style>
    /* IMPORT INTER FONT */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;800&family=JetBrains+Mono:wght@400;700&display=swap');

    /* BACKGROUND & RESET */
    .stApp {
        background-color: #050505;
        background-image: 
            radial-gradient(at 0% 0%, hsla(253,16%,7%,1) 0, transparent 50%), 
            radial-gradient(at 50% 0%, hsla(225,39%,30%,1) 0, transparent 50%), 
            radial-gradient(at 100% 0%, hsla(339,49%,30%,1) 0, transparent 50%);
        color: #e2e8f0;
        font-family: 'Inter', sans-serif;
    }

    /* REMOVE DEFAULT ELEMENTS */
    header {visibility: hidden;}
    .stDeployButton {display:none;}
    footer {visibility: hidden;}

    /* GLASS CARDS */
    .glass-card {
        background: rgba(25, 25, 35, 0.4);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 0 4px 30px rgba(0, 0, 0, 0.3);
    }

    /* NEON TEXT & HEADERS */
    h1, h2, h3 {
        font-family: 'Inter', sans-serif;
        font-weight: 800;
        letter-spacing: -1px;
    }
    .neon-text {
        background: linear-gradient(to right, #4f46e5, #ec4899);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    /* INPUT FIELDS STYLING */
    div[data-baseweb="input"] > div {
        background-color: rgba(0,0,0,0.5) !important;
        border: 1px solid #333 !important;
        color: white !important;
        border-radius: 8px !important;
    }
    
    /* DATAFRAME / TABLE STYLING */
    [data-testid="stDataFrame"] {
        background-color: rgba(0,0,0,0.2);
        border: 1px solid #333;
        border-radius: 10px;
    }

    /* CUSTOM BUTTONS */
    div.stButton > button {
        background: #1e1b4b; 
        color: #818cf8;
        border: 1px solid #4338ca;
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    div.stButton > button:hover {
        background: #4338ca;
        color: white;
        box-shadow: 0 0 15px rgba(67, 56, 202, 0.5);
    }
    
    /* LOCK SCREEN STYLES */
    .lock-title {
        font-family: 'JetBrains Mono', monospace;
        color: #ef4444;
        font-size: 80px;
        text-align: center;
        letter-spacing: 10px;
        text-shadow: 0 0 20px rgba(239, 68, 68, 0.5);
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. DATA INITIALIZATION & CONSTANTS
# ==========================================

# Lists exactly from your request context
PHY_CHAPTERS = ["Current Electricity", "Electrostatics", "Ray Optics", "Magnetic Effects", "Thermodynamics", "Dual Nature", "Rotational Motion", "Gravitation", "Fluids", "Semiconductors", "Work Power Energy", "Units & Dims", "Wave Optics", "Laws of Motion", "1D Motion", "AC", "Capacitance", "EMI", "Nuclear Phy", "KTG", "Oscillations", "EM Waves", "2D Motion", "Solids", "Waves", "Math in Phy", "CoM", "Thermal Prop", "Mag Prop", "Exp Phy"]
CHEM_CHAPTERS = ["GOC", "Coordination Cmpds", "Chem Bonding", "d-f Block", "Thermodynamics", "Electrochem", "Atomic Structure", "Solutions", "Hydrocarbons", "Amines", "p-Block", "Kinetics", "Biomolecules", "Mole Concept", "Ald/Ketones", "Periodic Table", "Haloalkanes", "Alcohols", "Ionic Eq", "Redox", "Chem Eq", "Practical Chem", "Carboxylic Acids"]
MATH_CHAPTERS = ["3D Geometry", "Seq & Series", "Matrices", "Vectors", "Definite Int", "Functions", "Binomial", "Diff Eq", "Probability", "PnC", "Straight Lines", "Area", "Complex No", "AOD", "Sets & Rel", "Quadratics", "Circles", "Statistics", "Limits", "Parabola", "Hyperbola", "Continuity", "Ellipse", "Inv Trig", "Indefinite Int", "Trig Eq", "Differentiation", "Trig Ratios", "Basic Math"]

def init_state():
    if "data" not in st.session_state:
        # Initialize Syllabus DataFrames
        phy_data = [{"Chapter": c, "Theory": False, "Revision": False, "PYQ 23": False, "PYQ 24": False, "PYQ 25": False} for c in PHY_CHAPTERS]
        chem_data = [{"Chapter": c, "Theory": False, "Revision": False, "PYQ 23": False, "PYQ 24": False, "PYQ 25": False} for c in CHEM_CHAPTERS]
        math_data = [{"Chapter": c, "Theory": False, "Revision": False, "PYQ 23": False, "PYQ 24": False, "PYQ 25": False} for c in MATH_CHAPTERS]

        st.session_state.data = {
            "syllabus": {
                "Physics": pd.DataFrame(phy_data),
                "Chemistry": pd.DataFrame(chem_data),
                "Maths": pd.DataFrame(math_data)
            },
            "tasks": [],
            "scores": [],
            "streak": 1,
            "locked": True,
            "lock_question": {"q": "Derivative of ln(x)?", "a": "1/x"}
        }

init_state()

# ==========================================
# 3. HELPER FUNCTIONS
# ==========================================

def get_countdown():
    # Target: Jan 21, 2026 (Example)
    target = datetime.datetime(2026, 1, 21)
    now = datetime.datetime.now()
    rem = target - now
    return rem.days, rem.seconds // 3600, (rem.seconds // 60) % 60

def save_syllabus_changes(subject, edited_df):
    st.session_state.data["syllabus"][subject] = edited_df

# ==========================================
# 4. GATEKEEPER (LOCK SCREEN)
# ==========================================

if st.session_state.data["locked"]:
    # Vertical spacer
    st.markdown("<br><br><br><br>", unsafe_allow_html=True)
    
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        st.markdown('<div class="lock-title">LOCKED</div>', unsafe_allow_html=True)
        st.markdown('<p style="text-align:center; color:#94a3b8; font-family:monospace; margin-bottom: 40px;">HYPER-FOCUS PROTOCOL ACTIVE</p>', unsafe_allow_html=True)
        
        # Security Card
        st.markdown(f"""
        <div class="glass-card" style="text-align:center;">
            <p style="color:#ef4444; font-weight:bold;">SECURITY GATEKEEPER</p>
            <h3 style="margin: 20px 0;">{st.session_state.data['lock_question']['q']}</h3>
        </div>
        """, unsafe_allow_html=True)
        
        ans = st.text_input("Answer", placeholder="Enter Answer...", label_visibility="collapsed")
        
        if st.button("VERIFY IDENTITY", use_container_width=True):
            correct = st.session_state.data['lock_question']['a']
            if ans.strip() == correct:
                st.session_state.data["locked"] = False
                st.rerun()
            else:
                st.error("ACCESS DENIED")
    
    st.stop() # Stops the app here so the rest doesn't load

# ==========================================
# 5. MAIN APP HEADER & METRICS
# ==========================================

# Top Bar
h1, h2, h3 = st.columns([3, 2, 1])
with h1:
    st.markdown("# JEE WAR <span class='neon-text'>ROOM</span>", unsafe_allow_html=True)
    st.markdown("<p style='color: #64748b; margin-top: -15px;'>TARGET 2026 // ELITE DROPPER BATCH</p>", unsafe_allow_html=True)

with h2:
    # Countdown Visuals
    d, h, m = get_countdown()
    st.markdown(f"""
    <div style="display:flex; gap: 20px; justify-content: center; align-items: center; background: rgba(0,0,0,0.5); padding: 10px; border-radius: 10px; border: 1px solid #333;">
        <div style="text-align:center;"><span style="font-size:24px; font-weight:bold; color:white;">{d}</span><br><span style="font-size:10px; color:#64748b;">DAYS</span></div>
        <div style="font-size:20px; color:#333;">:</div>
        <div style="text-align:center;"><span style="font-size:24px; font-weight:bold; color:white;">{h}</span><br><span style="font-size:10px; color:#64748b;">HRS</span></div>
        <div style="font-size:20px; color:#333;">:</div>
        <div style="text-align:center;"><span style="font-size:24px; font-weight:bold; color:#06b6d4;">{m}</span><br><span style="font-size:10px; color:#64748b;">MIN</span></div>
    </div>
    """, unsafe_allow_html=True)

with h3:
    if st.button("🔴 ACTIVATE FOCUS", use_container_width=True):
        st.session_state.data["locked"] = True
        st.rerun()

st.divider()

# ==========================================
# 6. TABS & FEATURES
# ==========================================

tab_syllabus, tab_command, tab_score = st.tabs(["📘 PRO SYLLABUS", "⚔️ COMMAND CENTER", "📊 SCORE TRACKER"])

# --- TAB 1: SYLLABUS TRACKER ---
with tab_syllabus:
    st.markdown("### <span style='color:#06b6d4'>CHAPTER TRACKING</span>", unsafe_allow_html=True)
    
    # Subject Selector
    subj_choice = st.radio("Select Subject", ["Physics", "Chemistry", "Maths"], horizontal=True, label_visibility="collapsed")
    
    st.write("") # Spacer
    
    # Data Editor (The Grid)
    # We use data_editor to allow clicking checkboxes directly
    current_df = st.session_state.data["syllabus"][subj_choice]
    
    edited_df = st.data_editor(
        current_df,
        column_config={
            "Chapter": st.column_config.TextColumn("Chapter", disabled=True, width="large"),
            "Theory": st.column_config.CheckboxColumn("Theory", width="small"),
            "Revision": st.column_config.CheckboxColumn("Revision", width="small"),
            "PYQ 23": st.column_config.CheckboxColumn("PYQ 23", width="small"),
            "PYQ 24": st.column_config.CheckboxColumn("PYQ 24", width="small"),
            "PYQ 25": st.column_config.CheckboxColumn("PYQ 25", width="small"),
        },
        hide_index=True,
        use_container_width=True,
        height=600,
        key=f"editor_{subj_choice}" # Unique key per subject
    )
    
    # Save changes immediately to session state
    st.session_state.data["syllabus"][subj_choice] = edited_df

# --- TAB 2: COMMAND CENTER ---
with tab_command:
    st.markdown("### <span style='color:#a855f7'>OPERATIONAL DIRECTIVES</span>", unsafe_allow_html=True)
    
    # Input Area
    with st.container():
        c_in1, c_in2, c_in3 = st.columns([1, 4, 1])
        with c_in1:
            task_type = st.selectbox("Type", ["Daily", "Weekly"], label_visibility="collapsed")
        with c_in2:
            task_input = st.text_input("New Objective", placeholder="Enter new objective...", label_visibility="collapsed")
        with c_in3:
            if st.button("ASSIGN", use_container_width=True):
                if task_input:
                    st.session_state.data["tasks"].insert(0, {"desc": task_input, "type": task_type, "done": False})
                    st.rerun()

    st.write("")
    
    # Task Lists Layout
    col_d, col_w = st.columns(2)
    
    # Daily Column
    with col_d:
        st.markdown("""<div class="glass-card"><h4 style="margin:0;">DAILY OPERATIONS</h4><hr style="border-color:#333;">""", unsafe_allow_html=True)
        daily_tasks = [t for t in st.session_state.data["tasks"] if t["type"] == "Daily"]
        
        if not daily_tasks:
            st.markdown("<p style='color:#64748b; font-size:12px;'>NO OBJECTIVES ASSIGNED</p>", unsafe_allow_html=True)
        
        for i, t in enumerate(st.session_state.data["tasks"]):
            if t["type"] == "Daily":
                c1, c2, c3 = st.columns([0.1, 0.8, 0.1])
                # Checkbox
                done = c1.checkbox("", t["done"], key=f"d_{i}")
                if done != t["done"]:
                    t["done"] = done
                    st.rerun()
                
                # Text
                style = "color:#4ade80; text-decoration:line-through;" if t["done"] else "color:white;"
                c2.markdown(f"<span style='{style}'>{t['desc']}</span>", unsafe_allow_html=True)
                
                # Delete
                if c3.button("×", key=f"del_{i}"):
                    st.session_state.data["tasks"].pop(i)
                    st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    # Weekly Column
    with col_w:
        st.markdown("""<div class="glass-card"><h4 style="margin:0;">WEEKLY STRATEGY</h4><hr style="border-color:#333;">""", unsafe_allow_html=True)
        weekly_tasks = [t for t in st.session_state.data["tasks"] if t["type"] == "Weekly"]
        
        if not weekly_tasks:
            st.markdown("<p style='color:#64748b; font-size:12px;'>NO OBJECTIVES ASSIGNED</p>", unsafe_allow_html=True)

        for i, t in enumerate(st.session_state.data["tasks"]):
            if t["type"] == "Weekly":
                c1, c2, c3 = st.columns([0.1, 0.8, 0.1])
                done = c1.checkbox("", t["done"], key=f"w_{i}")
                if done != t["done"]:
                    t["done"] = done
                    st.rerun()
                    
                style = "color:#4ade80; text-decoration:line-through;" if t["done"] else "color:white;"
                c2.markdown(f"<span style='{style}'>{t['desc']}</span>", unsafe_allow_html=True)
                
                if c3.button("×", key=f"del_w_{i}"):
                    st.session_state.data["tasks"].pop(i)
                    st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

# --- TAB 3: SCORE TRACKER ---
with tab_score:
    st.markdown("### <span style='color:#ec4899'>PERFORMANCE ANALYTICS</span>", unsafe_allow_html=True)
    
    # Input Form
    with st.form("score_input"):
        c1, c2, c3, c4, c5 = st.columns([3, 1, 1, 1, 1])
        name = c1.text_input("Test Name", placeholder="e.g. Mock Test 01")
        p = c2.number_input("PHY", 0, 100, step=1)
        c = c3.number_input("CHEM", 0, 100, step=1)
        m = c4.number_input("MATH", 0, 100, step=1)
        submit = c5.form_submit_button("ADD SCORE")
        
        if submit and name:
            st.session_state.data["scores"].append({
                "Date": datetime.date.today().strftime("%Y-%m-%d"),
                "Test Name": name,
                "PHY": p, "CHEM": c, "MATH": m,
                "TOTAL": p + c + m
            })
            st.rerun()

    st.write("")

    if st.session_state.data["scores"]:
        df_scores = pd.DataFrame(st.session_state.data["scores"])
        
        # Display Table
        st.dataframe(df_scores, use_container_width=True, hide_index=True)
        
        # Calculate Averages
        avg_p = df_scores["PHY"].mean()
        avg_c = df_scores["CHEM"].mean()
        avg_m = df_scores["MATH"].mean()
        avg_t = df_scores["TOTAL"].mean()
        
        # Display Metrics in Glass Cards
        st.write("")
        m1, m2, m3, m4 = st.columns(4)
        
        def metric_card(label, val, color):
            return f"""
            <div class="glass-card" style="text-align:center; padding: 15px;">
                <div style="font-size:10px; color:#94a3b8; letter-spacing:1px;">{label}</div>
                <div style="font-size:24px; font-weight:bold; color:{color};">{val:.1f}</div>
            </div>
            """
            
        m1.markdown(metric_card("AVG PHY", avg_p, "#3b82f6"), unsafe_allow_html=True)
        m2.markdown(metric_card("AVG CHEM", avg_c, "#eab308"), unsafe_allow_html=True)
        m3.markdown(metric_card("AVG MATH", avg_m, "#ef4444"), unsafe_allow_html=True)
        m4.markdown(metric_card("AVG TOTAL", avg_t, "#06b6d4"), unsafe_allow_html=True)
        
    else:
        st.info("No test records found. Add your first score above.")

# ==========================================
# FOOTER / SAVE FUNCTIONALITY
# ==========================================
with st.sidebar:
    st.markdown("### SETTINGS")
    # Button to reset lock manually
    if st.button("Force Lock"):
        st.session_state.data["locked"] = True
        st.rerun()
    
    # Download JSON (Because Streamlit Cloud doesn't persist files permanently)
    # Convert dataframes to dicts for JSON serialization
    export_data = st.session_state.data.copy()
    export_data["syllabus"]["Physics"] = export_data["syllabus"]["Physics"].to_dict()
    export_data["syllabus"]["Chemistry"] = export_data["syllabus"]["Chemistry"].to_dict()
    export_data["syllabus"]["Maths"] = export_data["syllabus"]["Maths"].to_dict()
    
    st.download_button(
        "💾 Backup Data",
        data=json.dumps(export_data, default=str),
        file_name="war_room_backup.json",
        mime="application/json"
    )
