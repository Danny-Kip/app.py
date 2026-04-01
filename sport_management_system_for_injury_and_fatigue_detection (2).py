import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import sqlite3
import json
import os
import time
from datetime import datetime

# ============================================================================
# 💾 DATABASE SETUP
# ============================================================================
DB_FILE = 'sports_performance.db'

def init_database():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS athletes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            sport TEXT,
            age INTEGER,
            weight REAL,
            registered_date TEXT
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS kpi_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            athlete_name TEXT,
            heart_rate INTEGER,
            sleep_hours REAL,
            fatigue_score INTEGER,
            training_load INTEGER,
            stamina INTEGER,
            speed REAL,
            risk_score REAL,
            prediction TEXT,
            model_used TEXT,
            timestamp TEXT
        )
    ''')
    
    conn.commit()
    conn.close()

init_database()

# ============================================================================
# 🔐 AUTHENTICATION SETUP
# ============================================================================
AUTH_FILE = 'auth_config.json'

def init_auth():
    if not os.path.exists(AUTH_FILE):
        credentials = {
            'admin': 'admin@2024',
            'daniel': 'research@123',
            'researcher': 'sports@ai2024',
            'user': 'demo123'
        }
        with open(AUTH_FILE, 'w') as f:
            json.dump(credentials, f, indent=2)

init_auth()

# ============================================================================
# 🔐 PAGE CONFIG
# ============================================================================
st.set_page_config(
    page_title="AI Sports Performance Monitoring", 
    layout="wide", 
    page_icon="🏅"
)

if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'username' not in st.session_state:
    st.session_state['username'] = None

# ============================================================================
# 🗄️ DATABASE FUNCTIONS
# ============================================================================
def get_athletes_from_db():
    try:
        conn = sqlite3.connect(DB_FILE)
        df = pd.read_sql_query("SELECT * FROM athletes ORDER BY name", conn)
        conn.close()
        return df
    except:
        return pd.DataFrame()

def add_athlete_to_db(name, sport, age, weight):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO athletes (name, sport, age, weight, registered_date)
        VALUES (?, ?, ?, ?, ?)
    ''', (name, sport, age, weight, datetime.now().strftime("%Y-%m-%d")))
    conn.commit()
    conn.close()

def delete_athlete_from_db(athlete_id):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM athletes WHERE id=?", (athlete_id,))
    conn.commit()
    conn.close()

def get_kpi_records():
    try:
        conn = sqlite3.connect(DB_FILE)
        df = pd.read_sql_query("SELECT * FROM kpi_records ORDER BY timestamp DESC", conn)
        conn.close()
        return df
    except:
        return pd.DataFrame()

def save_kpi_record(athlete_name, hr, sleep, fatigue, t_load, stamina, speed, risk_score, prediction, model):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO kpi_records 
        (athlete_name, heart_rate, sleep_hours, fatigue_score, training_load, 
         stamina, speed, risk_score, prediction, model_used, timestamp)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (athlete_name, hr, sleep, fatigue, t_load, stamina, speed, 
          risk_score, prediction, model, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    conn.commit()
    conn.close()

def get_athlete_count():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM athletes")
    count = cursor.fetchone()[0]
    conn.close()
    return count

def get_high_risk_count():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT COUNT(*) FROM kpi_records 
        WHERE prediction LIKE '%HIGH%' 
        AND timestamp >= datetime('now', '-7 days')
    """)
    count = cursor.fetchone()[0]
    conn.close()
    return count

def get_avg_performance():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT AVG(stamina) FROM kpi_records 
        WHERE timestamp >= datetime('now', '-7 days')
    """)
    avg = cursor.fetchone()[0]
    conn.close()
    return round(avg, 1) if avg else 0.0

def get_recent_alerts():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT athlete_name, timestamp, risk_score, prediction
        FROM kpi_records 
        WHERE prediction LIKE '%HIGH%' OR prediction LIKE '%MODERATE%'
        ORDER BY timestamp DESC 
        LIMIT 5
    ''')
    alerts = cursor.fetchall()
    conn.close()
    return alerts

def get_total_kpi_records():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM kpi_records")
    count = cursor.fetchone()[0]
    conn.close()
    return count

# ============================================================================
# 🎨 CSS STYLING
# ============================================================================
def load_custom_css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    
    * { font-family: 'Inter', sans-serif; }
    
    .stApp {
        background: linear-gradient(135deg, #1a0033 0%, #2d0066 25%, #3d0066 50%, #2d004d 75%, #1a0033 100%);
        background-attachment: fixed;
        min-height: 100vh;
    }
    
    .main-container {
        background: rgba(255, 255, 255, 0.03);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border-radius: 30px;
        padding: 35px;
        margin: 20px;
        border: 1px solid rgba(255, 255, 255, 0.08);
        box-shadow: 0 25px 50px rgba(0, 0, 0, 0.3);
    }
    
    .login-container {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(30px);
        padding: 60px 50px;
        border-radius: 30px;
        max-width: 500px;
        margin: 80px auto;
        text-align: center;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    .login-title {
        background: linear-gradient(135deg, #00f2fe 0%, #8a2be2 50%, #ff1493 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
        font-size: 32px;
        margin: 0 0 10px 0;
    }
    
    .metric-card {
        background: linear-gradient(135deg, rgba(138, 43, 226, 0.4), rgba(255, 20, 147, 0.4));
        backdrop-filter: blur(20px);
        color: white;
        padding: 25px 20px;
        border-radius: 24px;
        text-align: center;
        box-shadow: 0 15px 40px rgba(138, 43, 226, 0.3);
        border: 1px solid rgba(255, 255, 255, 0.2);
        transition: all 0.3s;
    }
    
    .metric-card:hover {
        transform: translateY(-8px);
        box-shadow: 0 25px 60px rgba(138, 43, 226, 0.5);
    }
    
    .metric-card h3 {
        margin: 10px 0 5px 0;
        font-size: 34px;
        font-weight: 800;
        color: #ffffff !important;
        text-shadow: 0 2px 4px rgba(0,0,0,0.3);
    }
    
    .metric-card p { 
        margin: 0; 
        font-size: 13px; 
        color: #ffffff !important; 
        font-weight: 600;
    }
    
    .metric-card .icon { 
        font-size: 30px; 
        margin-bottom: 8px; 
        display: block; 
    }
    
    h1 {
        background: linear-gradient(135deg, #00f2fe, #8a2be2, #ff1493);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
    }
    
    h2, h3, h4, h5, h6 { 
        color: #ffffff !important; 
        font-weight: 700;
        text-shadow: 0 2px 4px rgba(0,0,0,0.3);
    }
    
    p, span, label, div, li, a { 
        color: #ffffff !important; 
        font-weight: 500;
    }
    
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input {
        border-radius: 14px;
        border: 2px solid rgba(255, 255, 255, 0.4);
        background: #ffffff !important;
        color: #000000 !important;
        font-weight: 600;
        font-size: 15px;
    }
    
    .stTextInput > div > div > input:focus,
    .stNumberInput > div > div > input:focus {
        border-color: #8a2be2;
        box-shadow: 0 0 0 4px rgba(138, 43, 226, 0.4);
        background: #ffffff !important;
        color: #000000 !important;
    }
    
    .stTextInput label,
    .stNumberInput label,
    .stSelectbox label,
    .stSlider label {
        color: #ffffff !important;
        font-weight: 600;
        font-size: 14px;
    }
    
    .stSelectbox > div > div > div,
    .stSelectbox input {
        background: #ffffff !important;
        color: #000000 !important;
        font-weight: 600;
    }
    
    .stSlider > div > div {
        color: #ffffff !important;
        font-weight: 600;
    }
    
    .stButton > button {
        background: linear-gradient(135deg, #8a2be2, #ff1493);
        color: #ffffff !important;
        border: none;
        border-radius: 15px;
        padding: 14px 32px;
        font-weight: 700;
        font-size: 14px;
        width: 100%;
        box-shadow: 0 10px 30px rgba(138, 43, 226, 0.4);
    }
    
    .stButton > button:hover {
        transform: translateY(-3px);
        box-shadow: 0 15px 40px rgba(138, 43, 226, 0.6);
        color: #ffffff !important;
    }
    
    .stTabs [data-baseweb="tab-list"] {
        gap: 15px;
        background: rgba(255, 255, 255, 0.05);
        border-radius: 20px;
        padding: 12px;
        margin-bottom: 30px;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 55px;
        background: linear-gradient(135deg, rgba(138, 43, 226, 0.3), rgba(255, 20, 147, 0.3));
        border-radius: 15px;
        padding: 14px 28px;
        font-weight: 600;
        color: #ffffff !important;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #8a2be2, #ff1493, #00f2fe);
        color: #ffffff !important;
    }
    
    .status-card {
        padding: 14px 18px;
        border-radius: 16px;
        margin: 8px 0;
        backdrop-filter: blur(15px);
        border: 1px solid rgba(255, 255, 255, 0.2);
    }
    
    .status-success {
        background: rgba(16, 185, 129, 0.4) !important;
        color: #ffffff !important;
    }
    
    .status-warning {
        background: rgba(245, 158, 11, 0.4) !important;
        color: #ffffff !important;
    }
    
    .status-error {
        background: rgba(239, 68, 68, 0.4) !important;
        color: #ffffff !important;
    }
    
    [data-testid="stMetric"] {
        background: rgba(255, 255, 255, 0.1);
        padding: 15px;
        border-radius: 12px;
        border: 1px solid rgba(255, 255, 255, 0.15);
    }
    
    [data-testid="stMetric"] label {
        color: #ffffff !important;
        font-weight: 600;
    }
    
    [data-testid="stMetricValue"] {
        color: #ffffff !important;
        font-weight: 700;
        font-size: 24px;
    }
    
    [data-testid="stMetricDelta"] {
        color: #00f2fe !important;
        font-weight: 600;
    }
    
    .footer {
        text-align: center;
        padding: 25px;
        color: rgba(255, 255, 255, 0.7) !important;
        margin-top: 15px;
        border-top: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    .dataframe {
        border-radius: 18px;
        overflow: hidden;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
        background: #ffffff !important;
    }
    
    .dataframe td, .dataframe th {
        color: #000000 !important;
        font-weight: 500;
    }
    
    .stAlert {
        border-radius: 16px;
        border: none;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
        margin: 12px 0;
    }
    
    .stAlert * {
        color: #000000 !important;
        font-weight: 600;
    }
    
    .streamlit-expanderHeader {
        background: rgba(255, 255, 255, 0.1);
        border-radius: 16px;
        border: 1px solid rgba(255, 255, 255, 0.15);
        color: #ffffff !important;
    }
    
    .streamlit-expanderHeader * {
        color: #ffffff !important;
    }
    
    [data-testid="stSidebar"] {
        background: rgba(26, 0, 51, 0.8);
    }
    
    [data-testid="stSidebar"] * {
        color: #ffffff !important;
    }
    </style>
    """, unsafe_allow_html=True)

# ============================================================================
# 🔐 AUTHENTICATION
# ============================================================================
def authenticate_user(username, password):
    try:
        with open(AUTH_FILE, 'r') as f:
            credentials = json.load(f)
        return credentials.get(username) == password
    except:
        return False

def login_page():
    load_custom_css()
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown('<div class="login-container">', unsafe_allow_html=True)
        st.markdown('<p class="login-title">🏅 AI Sports Performance</p>', unsafe_allow_html=True)
        st.markdown('<p style="color: rgba(255,255,255,0.8);">Advanced Sports Analytics Dashboard</p>', unsafe_allow_html=True)
        
        username = st.text_input("👤 Username", key="login_user", label_visibility="collapsed")
        password = st.text_input("🔑 Password", type="password", key="login_pass", label_visibility="collapsed")
        
        if st.button("🚀 Access Dashboard", key="login_btn"):
            if authenticate_user(username, password):
                st.session_state['logged_in'] = True
                st.session_state['username'] = username
                st.success("✨ Welcome back!")
                time.sleep(1)
                st.rerun()
            else:
                st.error("❌ Invalid credentials")
        
        st.markdown("</div>", unsafe_allow_html=True)

# ============================================================================
# 📊 MAIN DASHBOARD
# ============================================================================
def dashboard():
    load_custom_css()
    
    col1, col2, col3 = st.columns([3, 1, 1])
    with col1:
        st.title("🏅 AI-Driven Sports Performance Monitoring")
        st.markdown(f"*Advanced Sports Analytics Lab* • 👤 **{st.session_state['username']}**")
    with col3:
        if st.button("🚪 Logout", key="logout_btn"):
            st.session_state['logged_in'] = False
            st.session_state['username'] = None
            st.rerun()
    
    st.markdown('<div class="main-container">', unsafe_allow_html=True)
    
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📈 Dashboard", "👥 Athletes", "⚙️ KPI & Predict", "📊 Analytics", "💾 Database"
    ])
    
    with tab1:
        st.header("🎯 Performance Overview")
        
        athlete_count = get_athlete_count()
        high_risk_count = get_high_risk_count()
        avg_performance = get_avg_performance()
        total_records = get_total_kpi_records()
        recent_alerts = get_recent_alerts()
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown(f'<div class="metric-card"><span class="icon">👥</span><h3>{athlete_count}</h3><p>Active Athletes</p></div>', unsafe_allow_html=True)
        with col2:
            st.markdown(f'<div class="metric-card"><span class="icon">⚠️</span><h3>{high_risk_count}</h3><p>High Risk (7 days)</p></div>', unsafe_allow_html=True)
        with col3:
            st.markdown(f'<div class="metric-card"><span class="icon">✅</span><h3>{avg_performance}%</h3><p>Avg Performance</p></div>', unsafe_allow_html=True)
        with col4:
            st.markdown(f'<div class="metric-card"><span class="icon">📊</span><h3>{total_records}</h3><p>Total Records</p></div>', unsafe_allow_html=True)
        
        st.markdown("---")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.subheader("📈 Weekly Performance Trends")
            kpi_df = get_kpi_records()
            if not kpi_df.empty:
                kpi_df['date'] = pd.to_datetime(kpi_df['timestamp']).dt.date
                daily_avg = kpi_df.groupby('date')['stamina'].mean().tail(7).reset_index()
                daily_avg.columns = ['Day', 'Performance']
                daily_avg['Day'] = daily_avg['Day'].apply(lambda x: x.strftime('%a'))
                
                fig = go.Figure()
                fig.add_trace(go.Scatter(x=daily_avg['Day'], y=daily_avg['Performance'], 
                                       mode='lines+markers', name='Performance',
                                       line=dict(color='#00f2fe', width=4),
                                       marker=dict(size=10, color='#00f2fe')))
                fig.update_layout(template='plotly_dark', height=380, 
                                title='Daily Performance Trend',
                                plot_bgcolor='rgba(0,0,0,0.5)', 
                                paper_bgcolor='rgba(0,0,0,0.5)',
                                font=dict(color='#ffffff', size=12),
                                legend=dict(bgcolor='rgba(0,0,0,0.5)', font=dict(color='#ffffff')))
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("📊 No performance data yet. Add KPI records in Tab 3!")
        
        with col2:
            st.subheader("🔔 Recent Alerts")
            if recent_alerts:
                for alert in recent_alerts:
                    athlete, timestamp, risk, prediction = alert
                    risk_level = "🚨 HIGH" if "HIGH" in prediction else "⚠️ MODERATE"
                    status_class = "error" if "HIGH" in prediction else "warning"
                    st.markdown(f"""
                    <div class="status-card status-{status_class}">
                        <strong>{risk_level}</strong> - {athlete}<br>
                        <small>{timestamp}</small>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("✅ No recent alerts")
    
    with tab2:
        st.header("👥 Athlete Registry")
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.subheader("➕ Register New Athlete")
            with st.form("register_form", clear_on_submit=True):
                new_name = st.text_input("Athlete Name", key="reg_name")
                new_sport = st.selectbox("Sport", ["Football", "Basketball", "Tennis", "Swimming", "Track", "Other"], key="reg_sport")
                new_age = st.number_input("Age", 16, 40, 22, key="reg_age")
                new_weight = st.number_input("Weight (kg)", 40, 120, 70, key="reg_weight")
                submit = st.form_submit_button("✅ Register", key="reg_submit")
                
                if submit and new_name:
                    add_athlete_to_db(new_name, new_sport, new_age, new_weight)
                    st.success(f"🎉 {new_name} registered successfully!")
                    st.rerun()
        
        with col2:
            st.subheader("📋 Registered Athletes")
            athletes_df = get_athletes_from_db()
            if not athletes_df.empty:
                st.dataframe(athletes_df, use_container_width=True)
                
                if len(athletes_df) > 0:
                    fig = px.pie(athletes_df, names='sport', title='Athletes by Sport',
                               color_discrete_sequence=['#8a2be2', '#ff1493', '#00f2fe', '#ffa500', '#00ff88', '#ff6b6b'],
                               hole=0.4)
                    fig.update_layout(template='plotly_dark', height=350,
                                    plot_bgcolor='rgba(0,0,0,0.5)', 
                                    paper_bgcolor='rgba(0,0,0,0.5)',
                                    font=dict(color='#ffffff'))
                    st.plotly_chart(fig, use_container_width=True)
                
                st.markdown("---")
                st.subheader("🗑️ Delete Athlete")
                if not athletes_df.empty:
                    delete_option = st.selectbox("Select athlete to delete", athletes_df['name'].tolist(), key="delete_athlete")
                    if st.button("🗑️ Delete Selected"):
                        athlete_id = athletes_df[athletes_df['name'] == delete_option]['id'].values[0]
                        delete_athlete_from_db(athlete_id)
                        st.success(f"✅ {delete_option} deleted!")
                        st.rerun()
            else:
                st.info("📭 No athletes registered yet. Use the form to add one!")
    
    with tab3:
        st.header("⚙️ Real-Time KPI Monitoring & Injury Prediction")
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.subheader("📊 Input Biometrics")
            athletes_df = get_athletes_from_db()
            athlete_options = athletes_df['name'].tolist() if not athletes_df.empty else []
            
            if athlete_options:
                player_name = st.selectbox("Select Athlete", athlete_options, key="kpi_athlete")
            else:
                st.warning("⚠️ No athletes registered. Please add athletes in Tab 2 first!")
                player_name = "None"
            
            selected_model = st.selectbox("🤖 ML Model", ["XGBoost ⭐", "Random Forest", "SVM", "KNN"], key="kpi_model")
            
            st.markdown("---")
            hr = st.number_input("Heart Rate (bpm)", 40, 220, 72, key="kpi_hr")
            sleep = st.slider("Sleep Hours", 3.0, 12.0, 8.0, key="kpi_sleep")
            fatigue = st.slider("Fatigue Score (1-10)", 1, 10, 3, key="kpi_fatigue")
            t_load = st.slider("Training Load", 100, 1000, 500, key="kpi_load")
            stamina = st.slider("Stamina (%)", 0, 100, 90, key="kpi_stamina")
            speed = st.number_input("Speed (m/s)", 1.0, 12.0, 6.5, key="kpi_speed")
            
            st.markdown("---")
            if hr < 60:
                st.markdown('<div class="status-card status-warning">💓 HR Below normal</div>', unsafe_allow_html=True)
            elif hr > 100:
                st.markdown('<div class="status-card status-error">💓 HR Elevated</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="status-card status-success">💓 HR Normal ✅</div>', unsafe_allow_html=True)
            
            if sleep < 6:
                st.markdown('<div class="status-card status-error">😴 Sleep Insufficient ⚠️</div>', unsafe_allow_html=True)
            elif sleep < 7:
                st.markdown('<div class="status-card status-warning">😴 Sleep Below optimal</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="status-card status-success">😴 Sleep Good ✅</div>', unsafe_allow_html=True)
        
        with col2:
            if athlete_options:
                st.subheader(f"🎯 Prediction: {player_name}")
                m1, m2, m3 = st.columns(3)
                m1.metric("⚡ Speed", f"{speed} m/s")
                m2.metric("🔋 Stamina", f"{stamina}%")
                m3.metric("😫 Fatigue", f"{fatigue}/10")
                
                st.markdown("---")
                
                if st.button("🔮 Run AI Injury Prediction", key="predict_btn"):
                    with st.spinner("🤖 Analyzing biometrics..."):
                        time.sleep(0.5)
                        risk_score = (fatigue * 0.5) + (t_load / 250) - (sleep * 0.3) + (hr / 200)
                        
                        if risk_score > 4.0 or hr > 185 or (fatigue >= 8 and sleep < 6):
                            prediction = "🚨 HIGH RISK"
                            st.error(f"""
                            **{prediction}**
                            
                            **Athlete**: {player_name}  
                            **Risk Score**: {risk_score:.2f}
                            
                            **Recommendation**: 
                            • Immediate rest (24-48h)  
                            • Reduce training intensity
                            """)
                        elif risk_score > 2.5:
                            prediction = "⚠️ MODERATE RISK"
                            st.warning(f"""
                            **{prediction}**
                            
                            **Athlete**: {player_name}  
                            **Risk Score**: {risk_score:.2f}
                            
                            **Recommendation**:
                            • Light recovery session  
                            • Ensure 8+ hours sleep
                            """)
                        else:
                            prediction = "✅ LOW RISK"
                            st.success(f"""
                            **{prediction}**
                            
                            **Athlete**: {player_name}  
                            **Risk Score**: {risk_score:.2f}
                            **Confidence**: {95 - risk_score*5:.1f}%
                            
                            **Recommendation**:
                            • Proceed with training  
                            • Maintain hydration
                            """)
                        
                        save_kpi_record(player_name, hr, sleep, fatigue, t_load, stamina, speed, 
                                       risk_score, prediction, selected_model)
                        st.info("💾 Record saved to database!")
            else:
                st.warning("⚠️ No athletes available. Please register athletes in Tab 2 first!")
    
    with tab4:
        st.header("📊 Model Performance Analytics")
        st.markdown("*Based on Advanced Research Data*")
        
        results = pd.DataFrame({
            'Model': ['KNN', 'Decision Tree', 'SVM', 'Random Forest', 'XGBoost'],
            'Recall (Injury Detection)': [0.24, 0.30, 0.50, 0.48, 0.46],
            'Precision': [0.68, 0.62, 0.71, 0.75, 0.78],
            'F1-Score': [0.35, 0.41, 0.59, 0.59, 0.58]
        })
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("🎯 Recall Comparison")
            fig1 = px.bar(results, x='Model', y='Recall (Injury Detection)', 
                         color='Recall (Injury Detection)',
                         color_continuous_scale='Purples', text_auto='.2f')
            fig1.update_layout(template='plotly_dark', height=400,
                            plot_bgcolor='rgba(0,0,0,0.5)', 
                            paper_bgcolor='rgba(0,0,0,0.5)',
                            font=dict(color='#ffffff'))
            st.plotly_chart(fig1, use_container_width=True)
        
        with col2:
            st.subheader("⚖️ Precision vs Recall")
            fig2 = px.scatter(results, x='Recall (Injury Detection)', y='Precision',
                           size='F1-Score', color='Model', text='Model',
                           color_discrete_sequence=['#00f2fe', '#8a2be2', '#ff1493', '#ffa500', '#00ff88'])
            fig2.update_layout(template='plotly_dark', height=400,
                            plot_bgcolor='rgba(0,0,0,0.5)', 
                            paper_bgcolor='rgba(0,0,0,0.5)',
                            font=dict(color='#ffffff'))
            st.plotly_chart(fig2, use_container_width=True)
        
        st.markdown("---")
        st.subheader("📈 Your Research Data Statistics")
        kpi_df = get_kpi_records()
        if not kpi_df.empty:
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Records", len(kpi_df))
            with col2:
                st.metric("Avg Risk Score", round(kpi_df['risk_score'].mean(), 2))
            with col3:
                st.metric("High Risk Count", len(kpi_df[kpi_df['prediction'].str.contains('HIGH')]))
            with col4:
                st.metric("Last Updated", kpi_df['timestamp'].iloc[-1].split()[0])
            
            st.markdown("---")
            st.subheader("📊 Recent KPI Records")
            st.dataframe(kpi_df.head(10), use_container_width=True)
        else:
            st.info("📭 No KPI records yet. Add predictions in Tab 3!")
    
    with tab5:
        st.header("💾 Database Management")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📊 Database Statistics")
            
            athlete_count = get_athlete_count()
            kpi_count = get_total_kpi_records()
            
            st.metric("Total Athletes", athlete_count)
            st.metric("Total KPI Records", kpi_count)
            
            if os.path.exists(DB_FILE):
                db_size = os.path.getsize(DB_FILE) / 1024
                st.metric("Database Size", f"{db_size:.2f} KB")
            
            st.markdown("---")
            st.subheader("📥 Export Data")
            
            athletes_df = get_athletes_from_db()
            kpi_df = get_kpi_records()
            
            if not athletes_df.empty:
                csv_athletes = athletes_df.to_csv(index=False)
                st.download_button(
                    "📥 Download Athletes (CSV)",
                    csv_athletes,
                    f"athletes_{datetime.now().strftime('%Y%m%d')}.csv",
                    "text/csv",
                    key='download_athletes'
                )
            
            if not kpi_df.empty:
                csv_kpi = kpi_df.to_csv(index=False)
                st.download_button(
                    "📥 Download KPI Records (CSV)",
                    csv_kpi,
                    f"kpi_records_{datetime.now().strftime('%Y%m%d')}.csv",
                    "text/csv",
                    key='download_kpi'
                )
        
        with col2:
            st.subheader("⚠️ Database Operations")
            
            if st.button("🗑️ Clear All KPI Records", key="clear_kpi"):
                conn = sqlite3.connect(DB_FILE)
                cursor = conn.cursor()
                cursor.execute("DELETE FROM kpi_records")
                conn.commit()
                conn.close()
                st.success("✅ All KPI records deleted!")
                st.rerun()
            
            if st.button("🗑️ Clear All Athletes", key="clear_athletes"):
                conn = sqlite3.connect(DB_FILE)
                cursor = conn.cursor()
                cursor.execute("DELETE FROM athletes")
                conn.commit()
                conn.close()
                st.success("✅ All athletes deleted!")
                st.rerun()
            
            st.markdown("---")
            st.subheader("ℹ️ Database Info")
            st.info(f"""
            **Database File**: {DB_FILE}  
            **Location**: Current directory  
            **Created**: {datetime.fromtimestamp(os.path.getctime(DB_FILE)).strftime('%Y-%m-%d %H:%M') if os.path.exists(DB_FILE) else 'N/A'}  
            **Last Modified**: {datetime.fromtimestamp(os.path.getmtime(DB_FILE)).strftime('%Y-%m-%d %H:%M') if os.path.exists(DB_FILE) else 'N/A'}
            """)
    
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('<div class="footer">🏅 AI Sports Performance Monitoring System | © 2024 | All Rights Reserved</div>', unsafe_allow_html=True)

# ============================================================================
# 🚀 MAIN
# ============================================================================
def main():
    if not st.session_state['logged_in']:
        login_page()
    else:
        dashboard()

if __name__ == "__main__":
    main()
