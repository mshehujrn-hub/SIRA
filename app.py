import sqlite3
import datetime
import pandas as pd
import plotly.express as px
import streamlit as st
from src.services import PredictionService

# -----------------------------------------------------------------------------
# 1. PAGE CONFIGURATION
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="SIRA - Incident Classifier",
    page_icon="🚨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -----------------------------------------------------------------------------
# 2. DATABASE INITIALIZATION & FILTERED QUERIES
# -----------------------------------------------------------------------------
def init_db():
    conn = sqlite3.connect('sira_hse_logs.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS incident_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME,
            username TEXT,
            narrative TEXT,
            prediction TEXT
        )
    ''')
    conn.commit()
    conn.close()

def log_incident(username, narrative, prediction):
    conn = sqlite3.connect('sira_hse_logs.db')
    c = conn.cursor()
    c.execute(
        "INSERT INTO incident_logs (timestamp, username, narrative, prediction) VALUES (?, ?, ?, ?)",
        (datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), username, narrative, prediction)
    )
    conn.commit()
    conn.close()

def fetch_logs(username=None):
    conn = sqlite3.connect('sira_hse_logs.db')
    if username:
        df = pd.read_sql_query(
            "SELECT * FROM incident_logs WHERE username = ? ORDER BY id DESC", 
            conn, 
            params=(username,)
        )
    else:
        df = pd.read_sql_query("SELECT * FROM incident_logs ORDER BY id DESC", conn)
    conn.close()
    return df

# Initialize SQLite database on app start
init_db()

# -----------------------------------------------------------------------------
# 3. CUSTOM UI STYLING
# -----------------------------------------------------------------------------
CUSTOM_CSS = """
<style>
    .stApp { background-color: #F8FAFC; }
    div[data-testid="stForm"] {
        background-color: #FFFFFF;
        border-radius: 10px;
        padding: 2rem;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
        border: 1px solid #E2E8F0;
    }
    .welcome-text {
        font-size: 1.25rem;
        font-weight: 600;
        color: #2563EB;
        margin-bottom: 0.2rem;
    }
    .main-title {
        font-size: 2.2rem;
        font-weight: 700;
        color: #0F172A;
        margin-bottom: 0.2rem;
    }
    .sub-title {
        font-size: 1rem;
        color: #64748B;
        margin-bottom: 1.5rem;
    }
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 4. AUTHENTICATION SYSTEM & USER PROFILES
# -----------------------------------------------------------------------------
# Initialize persistent profiles in session state
if "user_profiles" not in st.session_state:
    st.session_state["user_profiles"] = {
        "admin": {
            "password": "safety2026",
            "name": "Mubarak Mohammed",
            "role": "Administrator"
        },
        "operator": {
            "password": "sira123",
            "name": "Naseer Armiya'u Mohammed",
            "role": "Operator"
        }
    }

if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False
if "username" not in st.session_state:
    st.session_state["username"] = ""

def login_user(username, password):
    profiles = st.session_state["user_profiles"]
    if username in profiles and profiles[username]["password"] == password:
        st.session_state["authenticated"] = True
        st.session_state["username"] = username
        st.rerun()
    else:
        st.error("Invalid Username or Password")

def logout_user():
    st.session_state["authenticated"] = False
    st.session_state["username"] = ""
    st.rerun()

# --- LOGIN VIEW ---
if not st.session_state["authenticated"]:
    _, col_center, _ = st.columns([1, 1.2, 1])
    
    with col_center:
        st.write("##")
        st.markdown("<h2 style='text-align: center;'>🚨 SIRA Portal</h2>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #64748B;'>Smart Incident Report Analyzer</p>", unsafe_allow_html=True)
        
        with st.form("login_form"):
            user_input = st.text_input("Username", placeholder="e.g., admin or operator")
            pass_input = st.text_input("Password", type="password", placeholder="••••••••")
            submit_button = st.form_submit_button("Sign In", use_container_width=True, type="primary")
            
            if submit_button:
                login_user(user_input, pass_input)
                
    st.stop()

# Get current logged-in user profile
current_user = st.session_state["user_profiles"].get(st.session_state["username"], {
    "name": st.session_state["username"],
    "role": "User"
})

# -----------------------------------------------------------------------------
# 5. LOAD MODEL SERVICE
# -----------------------------------------------------------------------------
@st.cache_resource
def load_service():
    return PredictionService()

model_loaded = True
model_error = ""

try:
    service = load_service()
except Exception as e:
    model_loaded = False
    model_error = str(e)

# -----------------------------------------------------------------------------
# 6. SIDEBAR NAVIGATION
# -----------------------------------------------------------------------------
is_admin = st.session_state["username"] == "admin"

with st.sidebar:
    st.title("🚨 SIRA Control")
    st.caption("Oil & Gas Safety Analyzer")
    st.divider()
    
    st.write(f"👤 **User:** {current_user['name']}")
    st.write(f"🔑 **Role:** `{current_user['role']}`")
    
    if st.button("Log Out", type="secondary", use_container_width=True):
        logout_user()
        
    st.divider()
    
    # Navigation Options
    st.markdown("### 🧭 View Navigation")
    if is_admin:
        nav_choice = st.radio(
            "Select View:",
            ["📌 Incident Classifier Engine", "📊 HSE Analytics Dashboard", "⚙️ Account Settings"],
            index=0
        )
    else:
        nav_choice = st.radio(
            "Select View:",
            ["📌 Incident Classifier Engine", "📜 My Submitted Logs", "⚙️ Account Settings"],
            index=0
        )

# -----------------------------------------------------------------------------
# 7. MAIN DASHBOARD VIEWS
# -----------------------------------------------------------------------------
if not model_loaded:
    st.error(f"Failed to load model artifacts: {model_error}")
    st.stop()

# Header with Personalized Welcome Greeting
st.markdown(f"<div class='welcome-text'>👋 Welcome, {current_user['name']}</div>", unsafe_allow_html=True)
st.markdown("<div class='main-title'>🚨 SIRA: Smart Incident Report Analyzer</div>", unsafe_allow_html=True)
st.markdown("<div class='sub-title'>Automated NLP classification engine for oil & gas operational safety reports.</div>", unsafe_allow_html=True)

# --- VIEW 1: INCIDENT CLASSIFIER ENGINE ---
if nav_choice == "📌 Incident Classifier Engine":
    if is_admin:
        tab_single, tab_batch = st.tabs(["📝 Single Narrative Input", "📁 Batch CSV Upload"])
    else:
        tab_single, = st.tabs(["📝 Single Narrative Input"])

    with tab_single:
        with st.container(border=True):
            st.subheader("Analyze Single Log")
            st.write("Enter the narrative text of the incident report below:")
            
            user_input = st.text_area(
                "Enter Incident Report Narrative:",
                height=140,
                placeholder="e.g., Gas leak detected near pressure control valve in Block B manifold...",
                label_visibility="collapsed"
            )

            col_btn, _ = st.columns([1, 4])
            with col_btn:
                classify_clicked = st.button("Classify Incident", type="primary", use_container_width=True)

            if classify_clicked:
                if user_input.strip():
                    with st.spinner("Analyzing text..."):
                        prediction = service.predict_single(user_input)
                        log_incident(st.session_state['username'], user_input, prediction)
                    
                    st.markdown("---")
                    st.markdown("### **Prediction Result**")
                    
                    res_col1, _ = st.columns([2, 1])
                    with res_col1:
                        st.info(f"🏷️ **Predicted Category:** `{prediction}`")
                    st.caption("✅ Incident automatically logged to HSE Database.")
                else:
                    st.warning("Please enter a valid report description before analyzing.")

    if is_admin:
        with tab_batch:
            with st.container(border=True):
                st.subheader("Batch Process CSV")
                st.write("Upload a CSV file containing multiple report text entries to process predictions in bulk.")
                
                uploaded_file = st.file_uploader("Upload CSV containing report text", type=["csv"])

                if uploaded_file is not None:
                    batch_df = pd.read_csv(uploaded_file)
                    st.markdown("---")
                    st.write("### Options")
                    text_column = st.selectbox("Select Text Column to Classify:", batch_df.columns)

                    if st.button("Process Batch Predictions", type="primary"):
                        with st.spinner("Classifying reports in batch..."):
                            batch_df["Predicted_Category"] = batch_df[text_column].apply(
                                lambda x: service.predict_single(str(x))
                            )
                            
                            conn = sqlite3.connect('sira_hse_logs.db')
                            c = conn.cursor()
                            now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                            logs_to_insert = [
                                (now_str, st.session_state['username'], str(row[text_column]), str(row['Predicted_Category']))
                                for _, row in batch_df.iterrows()
                            ]
                            c.executemany(
                                "INSERT INTO incident_logs (timestamp, username, narrative, prediction) VALUES (?, ?, ?, ?)", 
                                logs_to_insert
                            )
                            conn.commit()
                            conn.close()

                        st.success("Batch classification complete & logged to HSE Audit Database!")
                        st.dataframe(batch_df, use_container_width=True)

                        csv_data = batch_df.to_csv(index=False).encode("utf-8")
                        st.download_button(
                            "📥 Download Categorized Results",
                            data=csv_data,
                            file_name="classified_incidents.csv",
                            mime="text/csv",
                            type="secondary"
                        )

# --- VIEW 2: HSE ANALYTICS DASHBOARD ---
elif nav_choice == "📊 HSE Analytics Dashboard" and is_admin:
    with st.container(border=True):
        st.subheader("HSE Incident Analytics")
        st.write("Real-time compliance tracking and incident distribution analysis across all operations.")
        
        df_logs = fetch_logs()
        
        if not df_logs.empty:
            m1, m2, m3 = st.columns(3)
            with m1:
                st.metric("Total Incident Logs", len(df_logs))
            with m2:
                st.metric("Active System Users", df_logs['username'].nunique())
            with m3:
                top_category = df_logs['prediction'].mode()[0] if not df_logs['prediction'].empty else "N/A"
                st.metric("Top Reported Risk", top_category)
            
            st.markdown("---")
            
            chart_col1, chart_col2 = st.columns(2)
            with chart_col1:
                st.markdown("**Incident Risk Distribution**")
                cat_counts = df_logs['prediction'].value_counts().reset_index()
                cat_counts.columns = ['Category', 'Count']
                fig_pie = px.pie(
                    cat_counts, 
                    names='Category', 
                    values='Count', 
                    hole=0.4, 
                    color_discrete_sequence=px.colors.sequential.RdBu
                )
                st.plotly_chart(fig_pie, use_container_width=True)
                
            with chart_col2:
                st.markdown("**Submissions by Operator**")
                usr_counts = df_logs['username'].value_counts().reset_index()
                usr_counts.columns = ['User', 'Logs Submitted']
                fig_bar = px.bar(
                    usr_counts, 
                    x='User', 
                    y='Logs Submitted', 
                    text_auto=True, 
                    color_discrete_sequence=['#0F172A']
                )
                st.plotly_chart(fig_bar, use_container_width=True)
                
            st.markdown("---")
            st.subheader("Master HSE Compliance Audit Trail")
            st.dataframe(df_logs, use_container_width=True)
            
            csv_audit = df_logs.to_csv(index=False).encode("utf-8")
            st.download_button(
                "📥 Download Master Audit Log (CSV)",
                data=csv_audit,
                file_name=f"HSE_Master_Audit_Log_{datetime.datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                mime="text/csv",
                type="primary"
            )
        else:
            st.info("No incident logs available in database yet.")

# --- VIEW 3: MY SUBMITTED LOGS ---
elif nav_choice == "📜 My Submitted Logs":
    with st.container(border=True):
        st.subheader("My Incident Submission History")
        st.write("View all incident reports submitted under your user account.")
        
        df_user_logs = fetch_logs(username=st.session_state['username'])
        
        if not df_user_logs.empty:
            st.metric("My Total Logged Incidents", len(df_user_logs))
            st.dataframe(
                df_user_logs[['id', 'timestamp', 'narrative', 'prediction']], 
                use_container_width=True
            )
        else:
            st.info("You haven't submitted any incident reports yet.")

# --- VIEW 4: EDITABLE ACCOUNT SETTINGS ---
elif nav_choice == "⚙️ Account Settings":
    with st.container(border=True):
        st.subheader("⚙️ Account Settings")
        st.write("Manage your user account parameters and profile details.")
        st.markdown("---")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### **User Profile**")
            
            with st.form("edit_profile_form"):
                # Read-only fields
                st.text_input("System Username", value=st.session_state["username"], disabled=True)
                st.text_input("Assigned Role", value=current_user["role"], disabled=True)
                
                # Editable fields
                updated_name = st.text_input("Full Name", value=current_user["name"])
                updated_password = st.text_input("New Password", type="password", placeholder="Leave blank to keep current")
                
                submit_profile_update = st.form_submit_button("Save Changes", type="primary")
                
                if submit_profile_update:
                    if updated_name.strip():
                        username = st.session_state["username"]
                        
                        # Update state memory
                        st.session_state["user_profiles"][username]["name"] = updated_name.strip()
                        
                        if updated_password.strip():
                            st.session_state["user_profiles"][username]["password"] = updated_password.strip()
                            st.success("Profile and password updated successfully!")
                        else:
                            st.success("Profile updated successfully!")
                            
                        st.rerun()
                    else:
                        st.error("Full Name field cannot be empty.")
            
        with col2:
            st.markdown("### **Account Status**")
            st.success(f"🟢 Active Session: **{current_user['name']}**")
            st.info("System Username and Assigned Role are locked. To request role elevation, contact system administrative support.")