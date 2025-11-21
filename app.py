import streamlit as st
import datetime
import json
import random
import pandas as pd
import google.generativeai as genai

# ==========================================
# CONFIGURATION
# ==========================================
GEMINI_API_KEY = "YOUR_GEMINI_API_KEY_HERE" # Paste key here
PAGE_TITLE = "JEE WAR ROOM // PRO"
ICON = "🍎"

# ==========================================
# ADVANCED STYLING ENGINE (CSS)
# ==========================================
def inject_custom_css():
    st.markdown("""
        <style>
        /* --- GLOBAL FONTS & RESET --- */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;800&display=swap');
        
        html, body, [class*="css"] {
            font-family: 'Inter', sans-serif;
            -webkit-font-smoothing: antialiased;
        }

        /* --- LIQUID BACKGROUND --- */
        .stApp {
            background: #000000;
            background-image: 
                radial-gradient(at 0% 0%, hsla(253,16%,7%,1) 0, transparent 50%), 
                radial-gradient(at 50% 0%, hsla(225,39%,30%,1) 0, transparent 50%), 
                radial-gradient(at 100% 0%, hsla(339,49%,30%,1) 0, transparent 50%);
            background-attachment: fixed;
            background-size: cover;
        }
        
        /* Floating Orbs Animation (Simulated Liquid) */
        @keyframes float {
            0% { transform: translate(0px, 0px) scale(1); }
            33% { transform: translate(30px, -50px) scale(1.1); }
            66% { transform: translate(-20px, 20px) scale(0.9); }
            100% { transform: translate(0px, 0px) scale(1); }
        }

        /* --- GLASSMORPHISM CARD --- */
        .glass-card {
            background: rgba(255, 255, 255, 0.03);
            border-radius: 20px;
            box-shadow: 0 4px 30px rgba(0, 0, 0, 0.1);
            backdrop-filter: blur(12px);
            -webkit-backdrop-filter: blur(12px);
            border: 1px solid rgba(255, 255, 255, 0.08);
            padding: 20px;
            margin-bottom: 20px;
            transition: transform 0.2s ease, border-color 0.2s ease;
        }
        .glass-card:hover {
            transform: translateY(-2px);
            border-color: rgba(255, 255, 255, 0.2);
            box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
        }

        /* --- STREAMLIT WIDGET OVERRIDES --- */
        /* Inputs */
        .stTextInput input, .stNumberInput input, .stSelectbox div[data-baseweb="select"] {
            background-color: rgba(0, 0, 0, 0.3) !important;
            border: 1px solid rgba(255, 255, 255, 0.1) !important;
            border-radius: 12px !important;
            color: white !important;
            backdrop-filter: blur(5px);
        }
        .stTextInput input:focus {
            border-color: #6366f1 !important;
            box-shadow: 0 0 15px rgba(99, 102, 241, 0.3);
        }

        /* Buttons */
        div.stButton > button {
            background: linear-gradient(135deg, #6366f1 0%, #a855f7 100%);
            color: white;
            border: none;
            border-radius: 12px;
            padding: 10px 24px;
            font-weight: 600;
            transition: all 0.3s ease;
            box-shadow: 0 4px 15px rgba(99, 102, 241, 0.4);
        }
        div.stButton > button:hover {
            transform: scale(1.02);
            box-shadow: 0 6px 20px rgba(99, 102, 241, 0.6);
        }
        div.stButton > button:active {
            transform: scale(0.98);
        }

        /* Tabs */
        .stTabs [data-baseweb="tab-list"] {
            background-color: rgba(255,255,255,0.05);
            border-radius: 16px;
            padding: 5px;
            gap: 5px;
        }
        .stTabs [data-baseweb="tab"] {
            border-radius: 12px;
            color: #94a3b8;
        }
        .stTabs [aria-selected="true"] {
            background-color: rgba(255,255,255,0.1) !important;
            color: white !important;
            backdrop-filter: blur(10px);
        }

        /* Dataframe/Tables */
        [data-testid="stDataFrame"] {
            background: transparent;
        }
        
        /* Typography */
        h1, h2, h3 {
            letter-spacing: -0.5px;
            background: -webkit-linear-gradient(eee, #999);
            -webkit-background-clip: text;
        }
        
        .gradient-text {
            background: linear-gradient(to right, #818cf8, #c084fc, #f472b6);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-weight: 800;
        }
        </style>
    """, unsafe_allow_html=True)

# ==========================================
# DATA ENGINE
# ==========================================

PHY_LIST = ["Current Electricity", "Electrostatics", "Ray Optics", "Magnetism", "Thermodynamics", "Rotational Motion", "Gravitation", "Fluids", "Semiconductors", "Work Power Energy", "Laws of Motion", "Kinematics", "AC & EMI", "Nuclear Physics", "Oscillations", "Waves"]
CHEM_LIST = ["GOC", "Coordination Compounds", "Bonding", "Thermodynamics", "Electrochemistry", "Atomic Structure", "Solutions", "Hydrocarbons", "Kinetics", "Biomolecules", "Mole Concept", "Periodic Table", "Equilibrium"]
MATH_LIST = ["3D Geometry", "Vectors", "Integration", "Functions", "Probability", "PnC", "Calculus", "Complex Numbers", "Quadratics", "Conic Sections", "Trigonometry", "Matrices"]

def init_session():
    if "data" not in st.session_state:
        st.session_state.data = {
            "syllabus": {
                "Physics": {t: False for t in PHY_LIST},
                "Chemistry": {t: False for t in CHEM_LIST},
                "Maths": {t: False for t in MATH_LIST}
            },
            "tasks": [],
            "scores": [],
            "streak": 1,
            "locked": True
        }

def ai_generator():
    # Simulation of AI for UI demo purposes
    quotes = ["Dream big. Work hard.", "Silence is the best answer.", "Focus on the process.", "You are your only limit."]
    return random.choice(quotes)

# ==========================================
# UI COMPONENTS (Custom HTML)
# ==========================================

def glass_metric(label, value, icon="⚡"):
    st.markdown(f"""
    <div class="glass-card" style="text-align: center; padding: 15px;">
        <div style="font-size: 24px; margin-bottom: 5px;">{icon}</div>
        <div style="color: #94a3b8; font-size: 12px; text-transform: uppercase; letter-spacing: 1px;">{label}</div>
        <div style="font-size: 28px; font-weight: 700; color: white;">{value}</div>
    </div>
    """, unsafe_allow_html=True)

def glass_header():
    st.markdown("""
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 30px;">
        <div>
            <h1 style="margin:0; font-size: 32px;">WAR <span class="gradient-text">ROOM</span></h1>
            <p style="margin:0; color: #64748b; font-size: 14px;">SYSTEM ACTIVE // TARGET 2026</p>
        </div>
        <div style="text-align: right;">
            <div style="background: rgba(16, 185, 129, 0.2); color: #34d399; padding: 5px 12px; border-radius: 20px; font-size: 12px; border: 1px solid rgba(16, 185, 129, 0.3);">
                ● ONLINE
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ==========================================
# MAIN APP
# ==========================================

st.set_page_config(page_title=PAGE_TITLE, page_icon=ICON, layout="wide", initial_sidebar_state="collapsed")
inject_custom_css()
init_session()

# --- LOCK SCREEN UI ---
if st.session_state.data["locked"]:
    # Centering Mechanism
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<br><br><br>", unsafe_allow_html=True)
        st.markdown("""
        <div class="glass-card" style="text-align: center; padding: 40px;">
            <div style="font-size: 60px; margin-bottom: 20px;">🔒</div>
            <h2 style="margin-bottom: 10px;">System Locked</h2>
            <p style="color: #94a3b8; margin-bottom: 30px;">Enter security clearance to access dashboard.</p>
        </div>
        """, unsafe_allow_html=True)
        
        password = st.text_input("Passcode", type="password", label_visibility="collapsed", placeholder="Enter Password")
        
        if st.button("UNLOCK SYSTEM", use_container_width=True):
            st.session_state.data["locked"] = False
            st.rerun()
            
    st.stop()

# --- DASHBOARD UI ---

glass_header()

# Metrics Row
c1, c2, c3, c4 = st.columns(4)
with c1:
    rem_days = (datetime.datetime(2026, 1, 21) - datetime.datetime.now()).days
    glass_metric("Time Remaining", f"{rem_days}d", "⏳")
with c2:
    glass_metric("Streak", f"{st.session_state.data['streak']} Days", "🔥")
with c3:
    score = 0
    if st.session_state.data["scores"]:
        score = st.session_state.data["scores"][-1]['Total']
    glass_metric("Last Score", str(score), "📈")
with c4:
    glass_metric("Status", "Elite", "🛡️")

# Main Content Tabs
st.markdown("<br>", unsafe_allow_html=True)
tab1, tab2, tab3 = st.tabs(["TRACKER", "OPERATIONS", "INTEL"])

with tab1:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown("### 🧬 Syllabus Progress")
    
    subj = st.selectbox("Select Module", ["Physics", "Chemistry", "Maths"])
    
    # Custom progress bar visualization
    progress = random.randint(20, 80)
    st.markdown(f"""
    <div style="margin-top: 10px; margin-bottom: 20px;">
        <div style="display:flex; justify-content:space-between; color:#94a3b8; font-size: 12px; margin-bottom: 5px;">
            <span>COMPLETION</span>
            <span>{progress}%</span>
        </div>
        <div style="width: 100%; height: 8px; background: rgba(255,255,255,0.1); border-radius: 10px; overflow: hidden;">
            <div style="width: {progress}%; height: 100%; background: linear-gradient(90deg, #6366f1, #ec4899);"></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Data Editor styled
    df = pd.DataFrame([{"Chapter": k, "Complete": v} for k, v in st.session_state.data["syllabus"][subj].items()])
    edited = st.data_editor(
        df, 
        column_config={"Complete": st.column_config.CheckboxColumn(required=True)}, 
        use_container_width=True,
        hide_index=True
    )
    st.markdown('</div>', unsafe_allow_html=True)

with tab2:
    col_input, col_list = st.columns([1, 1.5])
    
    with col_input:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown("### ⚔️ New Directive")
        task_txt = st.text_input("Objective", placeholder="e.g. Solve 50 PYQs")
        if st.button("ADD DIRECTIVE", use_container_width=True):
            if task_txt:
                st.session_state.data["tasks"].append({"name": task_txt, "done": False})
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    with col_list:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown("### 📋 Active Operations")
        if not st.session_state.data["tasks"]:
            st.markdown("*No active directives.*")
        else:
            for i, t in enumerate(st.session_state.data["tasks"]):
                cols = st.columns([0.1, 0.8, 0.1])
                done = cols[0].checkbox("", value=t["done"], key=f"t{i}")
                
                # Styled Task Text
                style = "text-decoration: line-through; color: #555;" if done else "color: white;"
                cols[1].markdown(f"<span style='{style}'>{t['name']}</span>", unsafe_allow_html=True)
                
                if cols[2].button("×", key=f"d{i}"):
                    st.session_state.data["tasks"].pop(i)
                    st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

with tab3:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown("### 📊 Performance Analytics")
    
    # Dummy Chart for visuals
    chart_data = pd.DataFrame({
        'Test': ['Test 1', 'Test 2', 'Test 3', 'Test 4'],
        'Physics': [random.randint(40,90) for _ in range(4)],
        'Maths': [random.randint(40,90) for _ in range(4)]
    })
    
    st.line_chart(chart_data.set_index('Test'), color=["#6366f1", "#ec4899"])
    st.markdown('</div>', unsafe_allow_html=True)

# Sidebar Footer
with st.sidebar:
    st.markdown("### WAR ROOM SETTINGS")
    if st.button("🔒 LOCK SYSTEM"):
        st.session_state.data["locked"] = True
        st.rerun()
    
    st.markdown("---")
    quote = ai_generator()
    st.markdown(f"<div style='color: #94a3b8; font-style: italic; font-size: 12px;'>“{quote}”</div>", unsafe_allow_html=True)
