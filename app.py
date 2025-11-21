import streamlit as st
import datetime
import json
import random
import pandas as pd
import google.generativeai as genai
import time

# ==========================================
# CONFIGURATION & CONSTANTS
# ==========================================

# !!! PASTE YOUR API KEY HERE OR IN STREAMLIT SECRETS !!!
GEMINI_API_KEY = "YOUR_GEMINI_API_KEY_HERE"

# THEME COLORS (Used in Markdown)
COLOR_PRIMARY = "#6366f1"
COLOR_BG = "#0f172a"

# DATA LISTS
PHY_LIST = ["Current Electricity", "Electrostatics", "Ray Optics", "Magnetic Effects", "Thermodynamics", "Dual Nature", "Atomic Physics", "Rotational Motion", "Gravitation", "Fluids", "Semiconductors", "Work Power Energy", "Units and Dimensions", "Wave Optics", "Laws of Motion", "1D Motion", "AC", "Capacitance", "EMI", "Nuclear Physics", "KTG", "Oscillations", "EM Waves", "2D Motion", "Solids", "Waves", "Math in Physics", "CoM", "Thermal Prop", "Magnetic Prop", "Exp Physics"]
CHEM_LIST = ["GOC", "Coordination Cmpds", "Chemical Bonding", "d/f Block", "Thermodynamics", "Electrochemistry", "Structure of Atom", "Solutions", "Hydrocarbons", "Amines", "p Block", "Chem Kinetics", "Biomolecules", "Mole Concept", "Aldehydes/Ketones", "Periodic Table", "Haloalkanes", "Alcohols", "Ionic Eq", "Redox", "Chem Eq", "Practical Chem", "Carboxylic Acids"]
MATH_LIST = ["3D Geometry", "Sequence Series", "Matrices", "Vectors", "Definite Integration", "Functions", "Binomial", "Diff Eq", "Probability", "PnC", "Straight Lines", "Area", "Complex No", "AOD", "Sets Relations", "Quadratics", "Circles", "Statistics", "Limits", "Parabola", "Hyperbola", "Continuity", "Ellipse", "Inverse Trig", "Indefinite Int", "Trig Eq", "Differentiation", "Trig Ratios", "Basic Math"]

MOTIVATION_QUOTES = [
    "Your competition is studying right now.", "The pain of discipline or the pain of regret.",
    "IIT is a state of mind.", "Stop when you're done.", "Physics is simple. Nature is complex.",
    "Rank 1 is for the relentless.", "Consistency beats intensity.", "Don't just float; swim."
]

OFFLINE_QUESTIONS = [
    {"q": "Unit of Magnetic Flux?", "a": "weber"},
    {"q": "Hybridization of CH4?", "a": "sp3"},
    {"q": "Derivative of ln(x)?", "a": "1/x"},
    {"q": "Value of sin(90)?", "a": "1"},
]

# ==========================================
# AI & HELPER FUNCTIONS
# ==========================================

def get_ai_question():
    """Fetch question from Gemini or fallback to offline pool"""
    if "gemini_model" not in st.session_state:
        if GEMINI_API_KEY and "YOUR_GEMINI" not in GEMINI_API_KEY:
            try:
                genai.configure(api_key=GEMINI_API_KEY)
                st.session_state.gemini_model = genai.GenerativeModel('gemini-1.5-flash')
            except:
                st.session_state.gemini_model = None

    if st.session_state.get("gemini_model"):
        try:
            prompt = "Generate 1 hard one-word answer question for JEE Mains. Return valid JSON: {'q': 'question', 'a': 'answer'}."
            response = st.session_state.gemini_model.generate_content(prompt)
            text = response.text.strip().replace("```json", "").replace("```", "")
            return json.loads(text)
        except:
            pass
    return random.choice(OFFLINE_QUESTIONS)

def calculate_countdown():
    target = datetime.datetime(2026, 1, 21)
    now = datetime.datetime.now()
    rem = target - now
    return f"{rem.days} DAYS LEFT"

# ==========================================
# SETUP & SESSION STATE
# ==========================================

st.set_page_config(page_title="JEE War Room", page_icon="🛡️", layout="wide", initial_sidebar_state="collapsed")

# Initialize Data if not present
if "data" not in st.session_state:
    st.session_state.data = {
        "syllabus": {
            "Physics": {topic: {"TH": False, "REV": False, "PYQ": False} for topic in PHY_LIST},
            "Chemistry": {topic: {"TH": False, "REV": False, "PYQ": False} for topic in CHEM_LIST},
            "Maths": {topic: {"TH": False, "REV": False, "PYQ": False} for topic in MATH_LIST}
        },
        "tasks": [],
        "scores": [],
        "streak": 0,
        "locked": True,
        "security_question": get_ai_question()
    }

# CSS Styling for "War Room" look
st.markdown(f"""
    <style>
    .stApp {{ background-color: {COLOR_BG}; color: white; }}
    .big-font {{ font-size: 40px !important; font-weight: bold; color: #ef4444; }}
    .header-style {{ font-size: 24px; font-weight: bold; color: {COLOR_PRIMARY}; }}
    div.stButton > button:first-child {{ background-color: #1e293b; color: white; border: 1px solid #334155; }}
    div.stButton > button:hover {{ border-color: {COLOR_PRIMARY}; color: {COLOR_PRIMARY}; }}
    </style>
""", unsafe_allow_html=True)

# ==========================================
# GATEKEEPER (FOCUS MODE)
# ==========================================

if st.session_state.data["locked"]:
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 2, 1])
    
    with c2:
        st.markdown('<p class="big-font" style="text-align:center;">GATEKEEPER ACTIVE</p>', unsafe_allow_html=True)
        st.markdown(f"### **Q: {st.session_state.data['security_question']['q']}**")
        
        ans = st.text_input("Enter Security Clearance:", placeholder="Type answer here...")
        
        if st.button("UNLOCK SYSTEM", use_container_width=True):
            correct = st.session_state.data['security_question']['a'].lower().strip()
            if ans.lower().strip() == correct or ans.lower().strip() in correct:
                st.session_state.data["locked"] = False
                st.rerun()
            else:
                st.error("ACCESS DENIED. STUDY HARDER.")
    
    st.stop() # Stop execution here if locked

# ==========================================
# MAIN DASHBOARD
# ==========================================

# Header
col1, col2, col3 = st.columns([3, 1, 1])
with col1:
    st.markdown('<p class="header-style">JEE WAR ROOM // 2026 ELITE</p>', unsafe_allow_html=True)
with col2:
    st.metric("Countdown", calculate_countdown())
with col3:
    st.metric("Streak", f"🔥 {st.session_state.data['streak']}")

# Lock Button in Sidebar
with st.sidebar:
    st.title("Settings")
    if st.button("🔒 RE-ENGAGE LOCK"):
        st.session_state.data["locked"] = True
        st.session_state.data["security_question"] = get_ai_question()
        st.rerun()
    
    # Download Data (Since Cloud doesn't save files permanently)
    st.download_button(
        label="💾 Download Progress JSON",
        data=json.dumps(st.session_state.data, indent=2),
        file_name="jee_war_room_data.json",
        mime="application/json"
    )

# Tabs
tab1, tab2, tab3 = st.tabs(["📚 SYLLABUS TRACKER", "⚔️ COMMAND CENTER", "📊 PERFORMANCE"])

# --- TAB 1: SYLLABUS ---
with tab1:
    subject = st.radio("Select Sector", ["Physics", "Chemistry", "Maths"], horizontal=True)
    
    # Convert dict to dataframe for editing
    df = pd.DataFrame.from_dict(st.session_state.data["syllabus"][subject], orient='index')
    
    st.info(f"Tracking {len(df)} Chapters in {subject}")
    
    # Data Editor (Editable Grid)
    edited_df = st.data_editor(
        df,
        column_config={
            "TH": st.column_config.CheckboxColumn("Theory", help="Theory Completed"),
            "REV": st.column_config.CheckboxColumn("Revision", help="Revision Done"),
            "PYQ": st.column_config.CheckboxColumn("PYQs", help="2023-2025 PYQs Done"),
        },
        use_container_width=True,
        height=600
    )
    
    # Save changes back to session state
    st.session_state.data["syllabus"][subject] = edited_df.to_dict(orient='index')

# --- TAB 2: COMMAND CENTER (TASKS) ---
with tab2:
    st.markdown("#### OPERATION OBJECTIVES")
    
    c_in1, c_in2 = st.columns([3, 1])
    with c_in1:
        new_task = st.text_input("New Objective", placeholder="e.g. Complete Rotational Motion HCV")
    with c_in2:
        task_type = st.selectbox("Type", ["Daily", "Weekly"])
        add_btn = st.button("ASSIGN TASK", use_container_width=True)

    if add_btn and new_task:
        st.session_state.data["tasks"].insert(0, {
            "task": new_task, 
            "type": task_type, 
            "done": False, 
            "date": str(datetime.date.today())
        })
        st.rerun()

    # Display Tasks
    if not st.session_state.data["tasks"]:
        st.write("No active operations.")
    
    # Separate lists
    daily = [t for t in st.session_state.data["tasks"] if t["type"] == "Daily"]
    weekly = [t for t in st.session_state.data["tasks"] if t["type"] == "Weekly"]

    col_d, col_w = st.columns(2)
    
    with col_d:
        st.subheader("Daily Operations")
        for i, t in enumerate(st.session_state.data["tasks"]):
            if t["type"] == "Daily":
                cols = st.columns([0.1, 0.8, 0.1])
                done = cols[0].checkbox("", value=t["done"], key=f"d_{i}")
                t["done"] = done # Update state
                
                # Strikethrough if done
                txt = f"~~{t['task']}~~" if done else t['task']
                cols[1].markdown(txt)
                
                if cols[2].button("×", key=f"del_d_{i}"):
                    st.session_state.data["tasks"].pop(i)
                    st.rerun()

    with col_w:
        st.subheader("Weekly Strategy")
        for i, t in enumerate(st.session_state.data["tasks"]):
            if t["type"] == "Weekly":
                cols = st.columns([0.1, 0.8, 0.1])
                done = cols[0].checkbox("", value=t["done"], key=f"w_{i}")
                t["done"] = done
                
                txt = f"~~{t['task']}~~" if done else t['task']
                cols[1].markdown(txt)
                
                if cols[2].button("×", key=f"del_w_{i}"):
                    st.session_state.data["tasks"].pop(i)
                    st.rerun()

# --- TAB 3: SCOREBOARD ---
with tab3:
    st.markdown("#### TEST INTELLIGENCE")
    
    with st.form("score_form"):
        c1, c2, c3, c4 = st.columns([2, 1, 1, 1])
        name = c1.text_input("Test Name")
        p = c2.number_input("Phy", 0, 100)
        c = c3.number_input("Chem", 0, 100)
        m = c4.number_input("Math", 0, 100)
        submitted = st.form_submit_button("LOG DATA")
        
        if submitted and name:
            st.session_state.data["scores"].append({
                "Date": str(datetime.date.today()),
                "Test": name,
                "Phy": p, "Chem": c, "Math": m,
                "Total": p+c+m
            })
            st.success("Score Logged")
            st.rerun()

    if st.session_state.data["scores"]:
        score_df = pd.DataFrame(st.session_state.data["scores"])
        st.dataframe(score_df, use_container_width=True)
        
        # Stats
        avg_tot = score_df["Total"].mean()
        st.markdown(f"### AVERAGE SCORE: **{avg_tot:.1f}**")
        
        # Chart
        st.line_chart(score_df.set_index("Test")[["Phy", "Chem", "Math"]])
    else:
        st.info("No test data logged yet.")
