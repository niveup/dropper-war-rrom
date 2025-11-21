import customtkinter as ctk
import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
import datetime
import random
import threading
import google.generativeai as genai

# ==========================================
# CONFIGURATION & CONSTANTS
# ==========================================

# !!! PASTE YOUR API KEY HERE !!!
GEMINI_API_KEY = "YOUR_GEMINI_API_KEY_HERE"

# THEME COLORS
COLOR_BG = "#0f172a"       # Slate 900
COLOR_PANEL = "#1e293b"    # Slate 800
COLOR_PRIMARY = "#6366f1"  # Indigo 500
COLOR_MATH = "#00E5FF"     # Cyan/Teal
COLOR_PHY = "#3b82f6"      # Blue 500
COLOR_CHEM = "#f59e0b"     # Amber 500
COLOR_TEXT = "#f1f5f9"     # Slate 100
COLOR_MUTED = "#94a3b8"    # Slate 400
COLOR_RED = "#ef4444"      # Red 500
COLOR_GREEN = "#10b981"    # Emerald 500

# DATA LISTS (PRESERVED EXACTLY)
PHY_LIST = ["Current Electricity ⬇", "Electrostatics ⬆", "Ray Optics ⬆⬆", "Magnetic Effects of Current", "Thermodynamics ⬆", "Dual Nature of Matter", "Atomic Physics ⬇", "Rotational Motion ⬆⬆", "Gravitation ⬇⬇", "Mechanical Properties of Fluids", "Semiconductors", "Work Power Energy", "Units and Dimensions ⬆", "Wave Optics", "Laws of Motion ⬇⬇", "Motion In One Dimension⬇", "Alternating Current ⬇⬇", "Capacitance", "Electromagnetic Induction ⬇⬇", "Nuclear Physics ⬇", "Kinetic Theory of Gases ⬇", "Oscillations", "Electromagnetic Waves", "Motion In Two Dimensions ⬇", "Mechanical Properties of Solids", "Waves and Sound", "Mathematics in Physics", "Center of Mass Momentum", "Thermal Properties of Matter", "Magnetic Properties of Matter", "Experimental Physics"]
CHEM_LIST = ["General Organic Chemistry ⬇", "Coordination Compounds", "Chemical Bonding", "d and f Block Elements", "Thermodynamics (C) ⬆", "Electrochemistry", "Structure of Atom", "Solutions", "Hydrocarbons", "Amines", "p Block Elements ⬇", "Chemical Kinetics ⬆", "Biomolecules", "Mole Concept ⬆", "Aldehydes and Ketones", "Periodic Table ⬆", "Haloalkanes and Haloarenes ⬇", "Alcohols Phenols and Ethers ⬇", "Ionic Equilibrium ⬆", "Redox Reactions ⬇", "Chemical Equilibrium", "Practical Chemistry", "Carboxylic Acid Derivatives"]
MATH_LIST = ["Three-Dimensional Geometry ⬇", "Sequences and Series ⬇", "Matrices Determinants ⬇", "Vector Algebra ⬇", "Definite Integration", "Functions", "Binomial Theorem", "Differential Equations", "Probability", "Permutation Combination", "Straight Lines ⬆", "Area Under Curves", "Complex Number", "Application of Derivatives ⬇", "Sets and Relations", "Quadratic Equation", "Circle ⬇", "Statistics ⬇", "Limits", "Parabola ⬆", "Hyperbola", "Continuity and Differentiability", "Ellipse ⬆", "Inverse Trigonometric Functions", "Indefinite Integration", "Trigonometric Equations", "Differentiation", "Trigonometric Ratios & Identities", "Basic of Mathematics"]

# OFFLINE FALLBACK POOL
QUIZ_POOL = [
  {"q": "Unit of Magnetic Flux?", "a": "Weber"},
  {"q": "Hybridization of CH4?", "a": "sp3"},
  {"q": "Shape of XeF4?", "a": "Square Planar"},
  {"q": "Derivative of ln(x)?", "a": "1/x"},
  {"q": "Atomic Number of Iron (Fe)?", "a": "26"},
  {"q": "Value of sin(90)?", "a": "1"},
  {"q": "Formula for Kinetic Energy?", "a": "1/2mv^2"},
  {"q": "pH of pure water at 25C?", "a": "7"},
  {"q": "Dimension of Force?", "a": "MLT-2"},
  {"q": "Value of G power? (10^?)", "a": "-11"},
  {"q": "Pi bonds in Benzene?", "a": "3"},
  {"q": "Integral of cos(x)?", "a": "sin(x)"},
  {"q": "Oxidation state of O in H2O2?", "a": "-1"},
  {"q": "Slope of x-t graph?", "a": "Velocity"},
  {"q": "Coordination number in FCC?", "a": "12"}
]

MOTIVATION_QUOTES = [
  "Your competition is studying right now.", "The pain of discipline or the pain of regret.",
  "IIT is a state of mind.", "Stop when you're done.", "Physics is simple. Nature is complex.",
  "Rank 1 is for the relentless.", "Consistency beats intensity.", "Don't just float; swim."
]

# ==========================================
# AI ENGINE
# ==========================================

class AIEngine:
    def __init__(self):
        self.enabled = False
        if GEMINI_API_KEY and "YOUR_GEMINI_API_KEY" not in GEMINI_API_KEY:
            try:
                genai.configure(api_key=GEMINI_API_KEY)
                self.model = genai.GenerativeModel('gemini-1.5-flash')
                self.enabled = True
            except Exception as e:
                print(f"AI Init Error: {e}")

    def generate_question(self, subject="General Science"):
        if not self.enabled:
            return random.choice(QUIZ_POOL)
        
        try:
            prompt = f"Generate 1 hard one-word answer question for JEE Mains {subject}. Return strictly valid JSON format: {{'q': 'question text', 'a': 'answer'}}. Do not include markdown formatting."
            response = self.model.generate_content(prompt)
            # Clean potential markdown
            text = response.text.strip()
            if text.startswith("```json"): text = text[7:]
            if text.endswith("```"): text = text[:-3]
            return json.loads(text)
        except:
            return random.choice(QUIZ_POOL)

    def get_quote(self):
        if not self.enabled:
            return {"quote": random.choice(MOTIVATION_QUOTES), "author": "War Room Offline"}
        
        try:
            prompt = "Generate a brutal, stoic, 10-word max motivational quote for JEE aspirants. Return JSON: {'quote': '...', 'author': '...'}"
            response = self.model.generate_content(prompt)
            text = response.text.strip()
            if text.startswith("```json"): text = text[7:]
            if text.endswith("```"): text = text[:-3]
            return json.loads(text)
        except:
            return {"quote": random.choice(MOTIVATION_QUOTES), "author": "War Room Offline"}

# ==========================================
# DATA MANAGER
# ==========================================

class DataManager:
    FILE = "data.json"
    
    @staticmethod
    def load_data():
        default_data = {
            "syllabus": {
                "physics": [{"name": n, "th": 0, "rev": 0, "p23": 0, "p24": 0, "p25": 0} for n in PHY_LIST],
                "chemistry": [{"name": n, "th": 0, "rev": 0, "p23": 0, "p24": 0, "p25": 0} for n in CHEM_LIST],
                "maths": [{"name": n, "th": 0, "rev": 0, "p23": 0, "p24": 0, "p25": 0} for n in MATH_LIST]
            },
            "tasks": [],
            "scores": [],
            "last_login": "",
            "streak": 0,
            "view_mode_syllabus": "horizontal",
            "view_mode_tasks": "side"
        }
        
        if not os.path.exists(DataManager.FILE):
            return default_data
            
        try:
            with open(DataManager.FILE, 'r') as f:
                data = json.load(f)
                # Merge logic to ensure new chapters appear if list changed
                for subj, default_list in default_data["syllabus"].items():
                    if subj not in data["syllabus"]:
                        data["syllabus"][subj] = default_list
                    else:
                        existing_names = {i["name"] for i in data["syllabus"][subj]}
                        for item in default_list:
                            if item["name"] not in existing_names:
                                data["syllabus"][subj].append(item)
                return data
        except:
            return default_data

    @staticmethod
    def save_data(data):
        with open(DataManager.FILE, 'w') as f:
            json.dump(data, f, indent=2)

# ==========================================
# UI COMPONENTS
# ==========================================

class FocusModeWindow(ctk.CTkToplevel):
    def __init__(self, parent, ai_engine):
        super().__init__(parent)
        self.ai_engine = ai_engine
        self.attributes("-fullscreen", True)
        self.attributes("-topmost", True)
        self.configure(fg_color="black")
        self.overrideredirect(True) # Removes title bar
        
        self.question_data = self.ai_engine.generate_question("Physics/Chemistry/Maths")
        
        self.main_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.main_frame.place(relx=0.5, rely=0.5, anchor="center")
        
        # Header
        ctk.CTkLabel(self.main_frame, text="LOCKED", font=("Impact", 80), text_color=COLOR_RED).pack(pady=10)
        ctk.CTkLabel(self.main_frame, text="GATEKEEPER PROTOCOL ACTIVE", font=("Roboto", 20, "bold"), text_color=COLOR_RED).pack(pady=(0, 40))
        
        # Question
        ctk.CTkLabel(self.main_frame, text="SECURITY QUESTION:", font=("Roboto Mono", 14), text_color=COLOR_MUTED).pack()
        ctk.CTkLabel(self.main_frame, text=self.question_data['q'], font=("Roboto", 28, "bold"), wraplength=800, text_color="white").pack(pady=20)
        
        # Input
        self.answer_entry = ctk.CTkEntry(self.main_frame, placeholder_text="ENTER ANSWER", width=400, height=50, 
                                       font=("Roboto Mono", 20), justify="center", fg_color="#111", border_color=COLOR_MUTED)
        self.answer_entry.pack(pady=20)
        self.answer_entry.bind("<Return>", self.check_answer)
        self.answer_entry.focus()
        
        self.status_label = ctk.CTkLabel(self.main_frame, text="", text_color=COLOR_RED, font=("Roboto Mono", 14))
        self.status_label.pack(pady=10)
        
        ctk.CTkButton(self.main_frame, text="UNLOCK SYSTEM", fg_color=COLOR_PANEL, hover_color="#333", 
                      command=self.check_answer, width=200, height=40).pack(pady=10)

    def check_answer(self, event=None):
        user_ans = self.answer_entry.get().strip().lower()
        correct_ans = self.question_data['a'].strip().lower()
        
        # Basic fuzzy check
        if user_ans == correct_ans or user_ans in correct_ans or correct_ans in user_ans:
            self.destroy()
        else:
            self.status_label.configure(text="ACCESS DENIED. INCORRECT ANSWER.")
            self.answer_entry.delete(0, 'end')
            self.configure(fg_color="#220000") # Flash red bg
            self.after(200, lambda: self.configure(fg_color="black"))

class SyllabusTab(ctk.CTkFrame):
    def __init__(self, parent, data, save_callback):
        super().__init__(parent, fg_color="transparent")
        self.data = data
        self.save_callback = save_callback
        self.view_mode = data.get("view_mode_syllabus", "horizontal")
        
        self.ctrl_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.ctrl_frame.pack(fill="x", pady=(0, 10))
        
        self.btn_view = ctk.CTkButton(self.ctrl_frame, text=f"View: {self.view_mode.title()}", 
                                      width=100, fg_color=COLOR_PANEL, command=self.toggle_view)
        self.btn_view.pack(side="right")
        
        self.content_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.content_frame.pack(fill="both", expand=True)
        
        self.render()

    def toggle_view(self):
        self.view_mode = "vertical" if self.view_mode == "horizontal" else "horizontal"
        self.data["view_mode_syllabus"] = self.view_mode
        self.btn_view.configure(text=f"View: {self.view_mode.title()}")
        self.save_callback()
        self.render()

    def render(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()
            
        subjects = [
            ("PHYSICS", self.data["syllabus"]["physics"], COLOR_PHY),
            ("CHEMISTRY", self.data["syllabus"]["chemistry"], COLOR_CHEM),
            ("MATHS", self.data["syllabus"]["maths"], COLOR_MATH)
        ]
        
        if self.view_mode == "horizontal":
            self.content_frame.grid_columnconfigure((0,1,2), weight=1, uniform="grp")
            for i, (name, chapters, color) in enumerate(subjects):
                col = SyllabusColumn(self.content_frame, name, chapters, color, self.save_callback, mode="compact")
                col.grid(row=0, column=i, sticky="nsew", padx=5)
        else:
            self.content_frame.grid_columnconfigure(0, weight=1)
            for i, (name, chapters, color) in enumerate(subjects):
                col = SyllabusColumn(self.content_frame, name, chapters, color, self.save_callback, mode="full")
                col.pack(fill="x", pady=5)

class SyllabusColumn(ctk.CTkFrame):
    def __init__(self, parent, title, chapters, color, save_cb, mode="compact"):
        super().__init__(parent, fg_color=COLOR_PANEL, corner_radius=10)
        self.chapters = chapters
        self.save_cb = save_cb
        self.mode = mode
        
        # Header
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=10, pady=10)
        ctk.CTkLabel(header, text=title, font=("Roboto", 16, "bold"), text_color=color).pack(side="left")
        
        # Column headers
        cols = ["TH", "RV", "23", "24", "25"] if mode == "compact" else ["Theory", "Revision", "PYQ 23", "PYQ 24", "PYQ 25"]
        h_frame = ctk.CTkFrame(self, fg_color="transparent")
        h_frame.pack(fill="x", padx=10, pady=(0,5))
        
        # Spacer for name
        ctk.CTkLabel(h_frame, text="", width=150 if mode=="full" else 100).pack(side="left", fill="x", expand=True)
        
        for c in cols:
            ctk.CTkLabel(h_frame, text=c, width=30, font=("Roboto Mono", 10), text_color=COLOR_MUTED).pack(side="left", padx=2)
            
        # List
        scroll = ctk.CTkScrollableFrame(self, fg_color="transparent", height=500 if mode=="compact" else 250)
        scroll.pack(fill="both", expand=True, padx=5, pady=5)
        
        for idx, chap in enumerate(chapters):
            row = ctk.CTkFrame(scroll, fg_color="transparent")
            row.pack(fill="x", pady=2)
            
            lbl = ctk.CTkLabel(row, text=chap['name'], font=("Roboto", 12), anchor="w")
            lbl.pack(side="left", fill="x", expand=True)
            
            keys = ["th", "rev", "p23", "p24", "p25"]
            for key in keys:
                # Custom check command with closure
                def toggle(c=chap, k=key):
                    c[k] = 1 if c[k] == 0 else 0
                    self.save_cb()
                
                chk = ctk.CTkCheckBox(row, text="", width=20, height=20, 
                                      corner_radius=4, border_width=1,
                                      fg_color=color, hover_color=color,
                                      command=toggle)
                if chap[key]: chk.select()
                chk.pack(side="left", padx=4)

class CommandCenterTab(ctk.CTkFrame):
    def __init__(self, parent, data, save_callback):
        super().__init__(parent, fg_color="transparent")
        self.data = data
        self.save_callback = save_callback
        self.layout = data.get("view_mode_tasks", "side")
        
        # Input Area
        input_frame = ctk.CTkFrame(self, fg_color=COLOR_PANEL)
        input_frame.pack(fill="x", pady=(0, 15), ipady=5)
        
        self.type_var = ctk.StringVar(value="Daily")
        ctk.CTkSegmentedButton(input_frame, values=["Daily", "Weekly"], variable=self.type_var, width=150).pack(side="left", padx=10)
        
        self.entry = ctk.CTkEntry(input_frame, placeholder_text="New Operation Objective...", font=("Roboto", 14))
        self.entry.pack(side="left", fill="x", expand=True, padx=10)
        self.entry.bind("<Return>", self.add_task)
        
        ctk.CTkButton(input_frame, text="ASSIGN", width=100, fg_color=COLOR_PRIMARY, command=self.add_task).pack(side="left", padx=10)
        
        # Switch Layout Btn
        ctk.CTkButton(self, text="⇄ Switch Layout", width=80, height=20, fg_color="transparent", 
                      text_color=COLOR_MUTED, command=self.toggle_layout).pack(anchor="e")

        self.lists_container = ctk.CTkFrame(self, fg_color="transparent")
        self.lists_container.pack(fill="both", expand=True)
        self.render_lists()

    def toggle_layout(self):
        self.layout = "stack" if self.layout == "side" else "side"
        self.data["view_mode_tasks"] = self.layout
        self.save_callback()
        self.render_lists()

    def add_task(self, event=None):
        txt = self.entry.get().strip()
        if not txt: return
        
        task = {
            "id": str(datetime.datetime.now().timestamp()),
            "text": txt,
            "type": self.type_var.get().lower(),
            "created": datetime.datetime.now().timestamp(),
            "done": False
        }
        self.data["tasks"].insert(0, task)
        self.save_callback()
        self.entry.delete(0, 'end')
        self.render_lists()

    def render_lists(self):
        for w in self.lists_container.winfo_children(): w.destroy()
        
        daily_tasks = [t for t in self.data["tasks"] if t["type"] == "daily"]
        weekly_tasks = [t for t in self.data["tasks"] if t["type"] == "weekly"]
        
        if self.layout == "side":
            self.lists_container.grid_columnconfigure((0, 1), weight=1, uniform="a")
            self.create_task_list(self.lists_container, "Daily Operations", daily_tasks).grid(row=0, column=0, sticky="nsew", padx=5)
            self.create_task_list(self.lists_container, "Weekly Strategy", weekly_tasks).grid(row=0, column=1, sticky="nsew", padx=5)
        else:
            self.create_task_list(self.lists_container, "Daily Operations", daily_tasks).pack(fill="x", pady=5)
            self.create_task_list(self.lists_container, "Weekly Strategy", weekly_tasks).pack(fill="x", pady=5)

    def create_task_list(self, parent, title, tasks):
        frame = ctk.CTkFrame(parent, fg_color=COLOR_PANEL)
        
        header = ctk.CTkFrame(frame, fg_color="transparent")
        header.pack(fill="x", padx=10, pady=10)
        ctk.CTkLabel(header, text=title, font=("Roboto", 14, "bold")).pack(side="left")
        pending = len([t for t in tasks if not t["done"]])
        ctk.CTkLabel(header, text=f"{pending} PENDING", font=("Roboto Mono", 10), text_color=COLOR_MUTED).pack(side="right")
        
        scroll = ctk.CTkScrollableFrame(frame, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=5, pady=5)
        
        for t in tasks:
            self.render_task_item(scroll, t)
            
        return frame

    def render_task_item(self, parent, task):
        # Check overdue
        is_overdue = False
        if not task["done"]:
            elapsed = datetime.datetime.now().timestamp() - task["created"]
            limit = 86400 if task["type"] == "daily" else 604800
            if elapsed > limit: is_overdue = True
            
        color = COLOR_RED if is_overdue else COLOR_TEXT
        if task["done"]: color = COLOR_MUTED
        
        row = ctk.CTkFrame(parent, fg_color="transparent", border_width=1 if is_overdue else 0, border_color=COLOR_RED)
        row.pack(fill="x", pady=2)
        
        def toggle(tk=task):
            tk["done"] = not tk["done"]
            self.save_callback()
            self.render_lists()
            
        def delete(tk=task):
            self.data["tasks"].remove(tk)
            self.save_callback()
            self.render_lists()

        chk = ctk.CTkCheckBox(row, text="", width=20, height=20, command=toggle, 
                              fg_color=COLOR_GREEN, hover_color=COLOR_GREEN)
        if task["done"]: chk.select()
        chk.pack(side="left", padx=5, pady=5)
        
        lbl = ctk.CTkLabel(row, text=task["text"], text_color=color, font=("Roboto", 12))
        lbl.pack(side="left", padx=5)
        
        if is_overdue and not task["done"]:
             ctk.CTkLabel(row, text="OVERDUE", text_color=COLOR_RED, font=("Roboto", 8, "bold")).pack(side="left", padx=5)
             
        ctk.CTkButton(row, text="×", width=25, height=25, fg_color="transparent", text_color=COLOR_MUTED, 
                      hover_color=COLOR_RED, command=delete).pack(side="right", padx=5)

class ScoreboardTab(ctk.CTkFrame):
    def __init__(self, parent, data, save_callback):
        super().__init__(parent, fg_color="transparent")
        self.data = data
        self.save_callback = save_callback
        
        # Input Row
        in_frame = ctk.CTkFrame(self, fg_color=COLOR_PANEL)
        in_frame.pack(fill="x", pady=(0, 15), padx=0)
        
        self.e_name = ctk.CTkEntry(in_frame, placeholder_text="Test Name", width=200)
        self.e_name.pack(side="left", padx=10, pady=10)
        
        self.e_phy = ctk.CTkEntry(in_frame, placeholder_text="Phy", width=60, justify="center")
        self.e_phy.pack(side="left", padx=5)
        self.e_chem = ctk.CTkEntry(in_frame, placeholder_text="Chem", width=60, justify="center")
        self.e_chem.pack(side="left", padx=5)
        self.e_math = ctk.CTkEntry(in_frame, placeholder_text="Math", width=60, justify="center")
        self.e_math.pack(side="left", padx=5)
        
        ctk.CTkButton(in_frame, text="ADD SCORE", fg_color=COLOR_PRIMARY, command=self.add_score).pack(side="left", padx=20)
        
        # Table (Using Treeview styled)
        table_frame = ctk.CTkFrame(self, fg_color=COLOR_PANEL)
        table_frame.pack(fill="both", expand=True)
        
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", background=COLOR_BG, foreground="white", fieldbackground=COLOR_BG, borderwidth=0, rowheight=30)
        style.configure("Treeview.Heading", background=COLOR_PANEL, foreground="white", font=("Roboto", 10, "bold"))
        style.map("Treeview", background=[('selected', COLOR_PRIMARY)])
        
        columns = ("date", "name", "phy", "chem", "math", "total")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", selectmode="browse")
        
        self.tree.heading("date", text="DATE")
        self.tree.heading("name", text="TEST NAME")
        self.tree.heading("phy", text="PHY")
        self.tree.heading("chem", text="CHEM")
        self.tree.heading("math", text="MATH")
        self.tree.heading("total", text="TOTAL")
        
        self.tree.column("date", width=100, anchor="center")
        self.tree.column("name", width=200)
        self.tree.column("phy", width=60, anchor="center")
        self.tree.column("chem", width=60, anchor="center")
        self.tree.column("math", width=60, anchor="center")
        self.tree.column("total", width=80, anchor="center")
        
        self.tree.pack(fill="both", expand=True, padx=10, pady=10)
        
        del_btn = ctk.CTkButton(table_frame, text="Delete Selected", fg_color=COLOR_RED, height=25, command=self.delete_score)
        del_btn.pack(pady=5, anchor="e", padx=10)
        
        # Stats Footer
        self.stats_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.stats_frame.pack(fill="x", pady=10)
        
        self.update_table()

    def add_score(self):
        try:
            p = int(self.e_phy.get())
            c = int(self.e_chem.get())
            m = int(self.e_math.get())
            name = self.e_name.get()
            if not name: return
            
            rec = {
                "id": str(datetime.datetime.now().timestamp()),
                "date": datetime.datetime.now().strftime("%Y-%m-%d"),
                "name": name,
                "phy": p, "chem": c, "math": m
            }
            self.data["scores"].insert(0, rec)
            self.save_callback()
            self.e_name.delete(0, 'end')
            self.e_phy.delete(0, 'end')
            self.e_chem.delete(0, 'end')
            self.e_math.delete(0, 'end')
            self.update_table()
        except ValueError:
            pass

    def delete_score(self):
        sel = self.tree.selection()
        if sel:
            idx = self.tree.index(sel[0])
            # Treeview order matches list order because we insert 0
            # But let's be safe, actually find by values not reliable if duplicates
            # Simple approach: map selection to data index
            # Since we render list in order, tree index i = list index i
            del self.data["scores"][idx]
            self.save_callback()
            self.update_table()

    def update_table(self):
        for i in self.tree.get_children():
            self.tree.delete(i)
            
        total_p, total_c, total_m = 0,0,0
        count = len(self.data["scores"])
        
        for s in self.data["scores"]:
            tot = s["phy"] + s["chem"] + s["math"]
            self.tree.insert("", "end", values=(s["date"], s["name"], s["phy"], s["chem"], s["math"], tot))
            total_p += s["phy"]
            total_c += s["chem"]
            total_m += s["math"]
            
        # Update stats
        for w in self.stats_frame.winfo_children(): w.destroy()
        
        self.stats_frame.grid_columnconfigure((0,1,2,3), weight=1)
        
        def mk_stat(col, title, val, color):
            f = ctk.CTkFrame(self.stats_frame, fg_color=COLOR_PANEL)
            f.grid(row=0, column=col, padx=5, sticky="ew")
            ctk.CTkLabel(f, text=title, font=("Roboto", 10, "bold"), text_color=color).pack(pady=(5,0))
            ctk.CTkLabel(f, text=str(val), font=("Roboto", 20, "bold")).pack(pady=(0,5))

        avg_p = round(total_p/count, 1) if count else 0
        avg_c = round(total_c/count, 1) if count else 0
        avg_m = round(total_m/count, 1) if count else 0
        avg_t = round((total_p+total_c+total_m)/count, 1) if count else 0
        
        mk_stat(0, "AVG PHY", avg_p, COLOR_PHY)
        mk_stat(1, "AVG CHEM", avg_c, COLOR_CHEM)
        mk_stat(2, "AVG MATH", avg_m, COLOR_MATH)
        mk_stat(3, "AVG TOTAL", avg_t, COLOR_TEXT)


# ==========================================
# MAIN APPLICATION
# ==========================================

class JEEWarRoomApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("JEE War Room - Pro 2026")
        self.geometry("1200x800")
        
        ctk.set_appearance_mode("Dark")
        ctk.set_default_color_theme("dark-blue")
        
        self.data = DataManager.load_data()
        self.ai = AIEngine()
        
        self.setup_ui()
        self.start_countdown()
        self.check_streak()
        
        # Motivation Quote on Startup
        self.after(1000, self.show_motivation)

    def save_data(self):
        DataManager.save_data(self.data)

    def setup_ui(self):
        # --- HEADER ---
        header = ctk.CTkFrame(self, height=80, fg_color=COLOR_PANEL, corner_radius=0)
        header.pack(fill="x")
        
        # Logo
        title_frame = ctk.CTkFrame(header, fg_color="transparent")
        title_frame.pack(side="left", padx=20)
        ctk.CTkLabel(title_frame, text="JEE WAR ROOM", font=("Impact", 24), text_color="white").pack(anchor="w")
        ctk.CTkLabel(title_frame, text="TARGET 2026 // ELITE BATCH", font=("Roboto Mono", 10), text_color=COLOR_PRIMARY).pack(anchor="w")
        
        # Countdown
        self.lbl_countdown = ctk.CTkLabel(header, text="Loading...", font=("Roboto Mono", 20, "bold"))
        self.lbl_countdown.pack(side="left", expand=True)
        
        # Right Controls
        ctrl_frame = ctk.CTkFrame(header, fg_color="transparent")
        ctrl_frame.pack(side="right", padx=20)
        
        self.lbl_streak = ctk.CTkLabel(ctrl_frame, text=f"🔥 {self.data.get('streak', 0)} DAY STREAK", 
                                       text_color=COLOR_GREEN, font=("Roboto", 12, "bold"))
        self.lbl_streak.pack(side="right", padx=10)
        
        ctk.CTkButton(ctrl_frame, text="⛔ FOCUS MODE", fg_color=COLOR_RED, hover_color="#991b1b", 
                      command=self.activate_focus).pack(side="right")

        # --- TABS ---
        self.tab_view = ctk.CTkTabview(self, fg_color="transparent")
        self.tab_view.pack(fill="both", expand=True, padx=20, pady=10)
        
        self.tab_view.add("SYLLABUS")
        self.tab_view.add("COMMAND CENTER")
        self.tab_view.add("PERFORMANCE")
        
        # Populate Tabs
        SyllabusTab(self.tab_view.tab("SYLLABUS"), self.data, self.save_data).pack(fill="both", expand=True)
        CommandCenterTab(self.tab_view.tab("COMMAND CENTER"), self.data, self.save_data).pack(fill="both", expand=True)
        ScoreboardTab(self.tab_view.tab("PERFORMANCE"), self.data, self.save_data).pack(fill="both", expand=True)

    def start_countdown(self):
        target = datetime.datetime(2026, 1, 21)
        
        def update():
            now = datetime.datetime.now()
            rem = target - now
            if rem.total_seconds() > 0:
                d = rem.days
                h, remainder = divmod(rem.seconds, 3600)
                m, s = divmod(remainder, 60)
                txt = f"{d}d : {h:02d}h : {m:02d}m : {s:02d}s"
                self.lbl_countdown.configure(text=txt)
            else:
                self.lbl_countdown.configure(text="EXAM STARTED")
            self.after(1000, update)
            
        update()

    def check_streak(self):
        today = datetime.date.today().strftime("%Y-%m-%d")
        last = self.data.get("last_login", "")
        
        if last != today:
            if last:
                last_date = datetime.datetime.strptime(last, "%Y-%m-%d").date()
                yesterday = datetime.date.today() - datetime.timedelta(days=1)
                if last_date == yesterday:
                    self.data["streak"] += 1
                elif last_date < yesterday:
                    self.data["streak"] = 1
            else:
                self.data["streak"] = 1
            
            self.data["last_login"] = today
            self.save_data()
            if hasattr(self, 'lbl_streak'):
                self.lbl_streak.configure(text=f"🔥 {self.data['streak']} DAY STREAK")

    def show_motivation(self):
        # Fetch in thread to avoid freezing UI
        def fetch():
            q_data = self.ai.get_quote()
            self.after(0, lambda: self._display_modal(q_data))
            
        threading.Thread(target=fetch, daemon=True).start()

    def _display_modal(self, q_data):
        # A custom pseudo-modal using a frame overlay
        overlay = ctk.CTkFrame(self, fg_color="black", bg_color="black")
        overlay.place(relx=0, rely=0, relwidth=1, relheight=1)
        overlay.lift()
        
        ctk.CTkLabel(overlay, text="WAR ROOM INTELLIGENCE", font=("Roboto Mono", 12), text_color=COLOR_PRIMARY).pack(pady=(150, 20))
        ctk.CTkLabel(overlay, text=f'"{q_data["quote"]}"', font=("Roboto", 32, "bold"), wraplength=800).pack(pady=20)
        ctk.CTkLabel(overlay, text=f"- {q_data.get('author', 'Unknown')}", font=("Roboto", 16), text_color=COLOR_MUTED).pack()
        
        ctk.CTkButton(overlay, text="ACKNOWLEDGE", fg_color="white", text_color="black", hover_color="#ddd",
                      command=overlay.destroy).pack(pady=50)

    def activate_focus(self):
        FocusModeWindow(self, self.ai)


if __name__ == "__main__":
    app = JEEWarRoomApp()
    app.mainloop()
