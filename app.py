import streamlit as st
import json
import os
from datetime import datetime, date

# --- Configuration ---
DATA_FILE = "data.json"
Q1_START = date(2026, 1, 1)
Q1_END = date(2026, 3, 31)

USER_COLORS = {
    "Javier": "#FF4B4B",   # Red
    "Ricardo": "#00FF00",  # Green
    "Robert": "#FFD700",   # Gold
    "Jesus": "#1E90FF",    # Blue
    "Angel": "#9400D3"     # Purple
}

# --- Initial Data Seed ---
INITIAL_DATA = {
    "users": {
        "Robert": { 
            "goals": { 
                "Facturación": { "target": 2000, "current": 0, "unit": "USD" },
                "Contenido": { "target": 36, "current": 0, "unit": "Piezas" },
                "Libros": { "target": 12, "current": 0, "unit": "Libros" }
            } 
        },
        "Javier": { 
            "goals": { 
                "Peso a Perder": { "target": 12, "current": 0, "unit": "Kg" },
                "Capital Neto": { "target": 2500, "current": 0, "unit": "USD" },
                "Cursos Platzi": { "target": 7, "current": 0, "unit": "Cursos" }
            } 
        },
        "Jesus": { 
            "goals": { 
                "Vocabulario Inglés": { "target": 900, "current": 0, "unit": "Palabras" },
                "Python Scripts": { "target": 3, "current": 0, "unit": "Scripts" },
                "Protocolo Salud Mental": { "target": 90, "current": 0, "unit": "Días" }
            } 
        },
        "Ricardo": { 
            "goals": { 
                "Capital": { "target": 250, "current": 0, "unit": "USD" },
                "Educación": { "target": 425, "current": 0, "unit": "Clases" },
                "Escritura": { "target": 172, "current": 0, "unit": "Escritos" }
            } 
        },
        "Angel": { 
            "goals": { 
                "Soundbank Presets": { "target": 50, "current": 0, "unit": "Presets" }
            } 
        }
    },
    "history": []
}

# --- Data Functions ---
def load_data():
    if not os.path.exists(DATA_FILE):
        save_data(INITIAL_DATA)
        return INITIAL_DATA
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError:
        return INITIAL_DATA

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# --- Logic Functions ---
def get_time_progress():
    today = date.today()
    if today < Q1_START:
        return 0.0, (Q1_END - Q1_START).days
    if today > Q1_END:
        return 1.0, 0
    
    total_days = (Q1_END - Q1_START).days
    days_passed = (today - Q1_START).days
    days_left = (Q1_END - today).days
    
    return days_passed / total_days, days_left

def calculate_status(current, target, time_progress):
    if target == 0: return "🟢" # Avoid div by zero
    goal_progress = current / target
    # If goal progress is lagging behind time progress -> Red (Alert)
    if goal_progress < time_progress and goal_progress < 1.0:
        return "🔴"
    return "🟢"

def get_daily_mvp(history):
    today_str = date.today().strftime("%Y-%m-%d")
    counts = {}
    for entry in history:
        # Check if entry maps to today. History format: "YYYY-MM-DD HH:MM"
        if entry['time'].startswith(today_str):
            u = entry['user']
            counts[u] = counts.get(u, 0) + 1
            
    if not counts:
        return None, 0
        
    mvp_user = max(counts, key=counts.get)
    return mvp_user, counts[mvp_user]

# --- UI ---
st.set_page_config(page_title="Accountability Tracker", page_icon="🚀", layout="wide")

# Load Data
data = load_data()

# Sidebar - Registration
st.sidebar.title("📝 Registrar Avance")
selected_user = st.sidebar.selectbox("Usuario", list(data["users"].keys()))

# Feature: User Theme in Sidebar
user_color = USER_COLORS.get(selected_user, "#FFFFFF")
st.sidebar.markdown(
    f"<div style='border-left: 5px solid {user_color}; padding-left: 10px; margin-bottom: 20px;'>"
    f"<h3 style='margin: 0; color: {user_color};'>Hola, {selected_user}</h3></div>", 
    unsafe_allow_html=True
)

user_goals = data["users"][selected_user]["goals"]
selected_goal_name = st.sidebar.selectbox("Objetivo", list(user_goals.keys()))

amount_to_add = st.sidebar.number_input("Cantidad a sumar", min_value=0.0, step=0.5)
victory_note = st.sidebar.text_area("¿Cuál fue la Victoria de hoy?")

if st.sidebar.button("Guardar Avance"):
    if amount_to_add > 0:
        # Update Data
        current_val = data["users"][selected_user]["goals"][selected_goal_name]["current"]
        new_val = current_val + amount_to_add
        data["users"][selected_user]["goals"][selected_goal_name]["current"] = new_val
        
        # Add History
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        full_note = f"Sumó {amount_to_add} {user_goals[selected_goal_name]['unit']} a '{selected_goal_name}'"
        if victory_note:
            full_note += f" - Nota: {victory_note}"
            
        data["history"].append({
            "time": timestamp,
            "user": selected_user,
            "note": full_note
        })
        
        save_data(data)
        st.sidebar.success("Guardado exitosamente!")
        st.rerun()
    else:
        st.sidebar.warning("Ingresa una cantidad mayor a 0.")


# Main Dashboard
st.title("🚀 Accountability Tracker")

# Feature: MVP del Día
mvp_user, mvp_count = get_daily_mvp(data["history"])
if mvp_user:
    st.info(f"🏆 **MVP del Día: {mvp_user}** — Ha registrado {mvp_count} avances hoy. ¡Fuego! 🔥")

time_pct, days_left = get_time_progress()
st.markdown(f"### ⏳ Días Restantes Q1: **{days_left}**")
st.progress(time_pct, text=f"Tiempo Transcurrido: {int(time_pct*100)}%")

st.markdown("---")
st.subheader("🏆 Leaderboard")

# Create a grid layout
cols = st.columns(len(data["users"]))

# Display Users
for idx, (username, user_data) in enumerate(data["users"].items()):
    with cols[idx]:
        # Feature: User Theme in Leaderboard
        u_color = USER_COLORS.get(username, "#FAFAFA")
        st.markdown(f"<h3 style='color: {u_color};'>{username}</h3>", unsafe_allow_html=True)
        
        for goal_name, goal_data in user_data["goals"].items():
            current = goal_data['current']
            target = goal_data['target']
            unit = goal_data['unit']
            
            # Calc percentages
            pct = min(current / target, 1.0) if target > 0 else 0.0
            status_icon = calculate_status(current, target, time_pct)
            
            st.write(f"**{goal_name}** {status_icon}")
            st.caption(f"{current} / {target} {unit}")
            
            st.progress(pct)
            st.markdown("---")

st.markdown("### 📜 Feed de Actividad")
# Show last 10 entries reversed
for entry in reversed(data["history"][-10:]):
    st.info(f"**{entry['time']}** - **{entry['user']}**: {entry['note']}")
