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
    page_title="SIRA - Enterprise HSE Incident Analyzer",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -----------------------------------------------------------------------------
# 2. DATABASE INITIALIZATION & OPERATIONAL QUERIES
# -----------------------------------------------------------------------------
def init_db():
    conn = sqlite3.connect('sira_hse_logs.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS incident_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME,
            username TEXT,
            facility TEXT,
            department TEXT,
            severity_est TEXT,
            narrative TEXT,
            prediction TEXT
        )
    ''')
    conn.commit()
    conn.close()

def log_incident(username, facility, department, severity_est, narrative, prediction):
    conn = sqlite3.connect('sira_hse_logs.db')
    c = conn.cursor()
    c.execute(
        """INSERT INTO incident_logs 
           (timestamp, username, facility, department, severity_est, narrative, prediction) 
           VALUES (?, ?, ?, ?, ?, ?, ?)""",
        (
            datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            username,
            facility,
            department,
            severity_est,
            narrative,
            prediction
        )
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
# 3. ENTERPRISE CSS STYLING & BRAND WHITE-LABELING
# -----------------------------------------------------------------------------
CUSTOM_CSS = """
<style>
    /* Suppress Streamlit Framework UI Headers & Footers */
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}

    /* Global App Container */
    .stApp { 
        background-color: #F8FAFC; 
        font-family: 'Inter', system-ui, -apple-system, sans-serif;
    }

    /* Standardized Form Containers */
    div[data-testid="stForm"] {
        background-color: #FFFFFF;
        border-radius: 8px;
        padding: 2rem;
        box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.05);
        border: 1px solid #E2E8F0;
    }

    /* Enterprise Typography */
    .main-title {
        font-size: 1.8rem;
        font-weight: 700;
        color: #0F172A;
        letter-spacing: -0.02em;
    }
    .sub-title {
        font-size: 0.95rem;
        color: #475569;
    }
    .user-greeting {
        font-size: 0.8rem;
        font-weight: 600;
        color: #2563EB;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }

    /* Status & Security Badging */
    .status-badge {
        background-color: #F1F5F9;
        color: #334155;
        padding: 4px 10px;
        border-radius: 4px;
        font-size: 0.75rem;
        font-weight: 600;
        border: 1px solid #CBD5E1;
        display: inline-block;
        margin-left: 5px;
    }
    .role-badge {
        background-color: #E2E8F0;
        color: #1E293B;
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 0.8rem;
        font-weight: 600;
        display: inline-block;
    }
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 4. AUTHENTICATION SYSTEM & USER PROFILES
# -----------------------------------------------------------------------------
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
        st.error("Invalid credentials provided.")

def logout_user():
    st.session_state["authenticated"] = False
    st.session_state["username"] = ""
    st.rerun()

# --- LOGIN VIEW ---
if not st.session_state["authenticated"]:
    _, col_center, _ = st.columns([1, 1.2, 1])
    
    with col_center:
        st.write("##")
        st.markdown("<h2 style='text-align: center; color: #0F172A;'>SIRA Portal</h2>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #64748B;'>Smart Incident Report Analyzer | Oil & Gas Safety</p>", unsafe_allow_html=True)
        
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
# 6. SIDEBAR NAVIGATION & TELEMETRY
# -----------------------------------------------------------------------------
is_admin = st.session_state["username"] == "admin"

with st.sidebar:
    st.markdown("### SIRA Control")
    st.caption("Industrial Safety & HSE Intelligence")
    st.divider()
    
    st.write(f"**User:** {current_user['name']}")
    st.markdown(f"**Role:** <span class='role-badge'>{current_user['role']}</span>", unsafe_allow_html=True)
    st.write(" ")
    
    if st.button("Log Out", type="secondary", use_container_width=True):
        logout_user()
        
    st.divider()
    
    # Navigation Options
    st.markdown("##### Application Navigation")
    if is_admin:
        nav_choice = st.radio(
            "Select View:",
            ["Incident Classifier Engine", "HSE Analytics Dashboard", "Account Settings"],
            index=0,
            label_visibility="collapsed"
        )
    else:
        nav_choice = st.radio(
            "Select View:",
            ["Incident Classifier Engine", "My Submitted Logs", "Account Settings"],
            index=0,
            label_visibility="collapsed"
        )

# -----------------------------------------------------------------------------
# 7. MAIN DASHBOARD HEADER
# -----------------------------------------------------------------------------
if not model_loaded:
    st.error(f"Failed to load NLP classification engine: {model_error}")
    st.stop()

# Enterprise Header with Live System Telemetry
head_col1, head_col2 = st.columns([3, 1.2])

with head_col1:
    st.markdown(f"<div class='user-greeting'>AUTHENTICATED SESSION: {current_user['name']}</div>", unsafe_allow_html=True)
    st.markdown("<div class='main-title'>SIRA | Smart Incident Report Analyzer</div>", unsafe_allow_html=True)
    st.markdown("<div class='sub-title'>Automated NLP classification engine for oil & gas operational safety reports.</div>", unsafe_allow_html=True)

with head_col2:
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("<span class='status-badge'>🟢 SYSTEM: OPERATIONAL</span>", unsafe_allow_html=True)
    st.markdown("<span class='status-badge'>🔒 ISO 45001 COMPLIANT</span>", unsafe_allow_html=True)

st.divider()

# -----------------------------------------------------------------------------
# 8. VIEW ROUTING
# -----------------------------------------------------------------------------

# --- VIEW 1: INCIDENT CLASSIFIER ENGINE ---
if nav_choice == "Incident Classifier Engine":
    if is_admin:
        tab_single, tab_batch = st.tabs(["Single Log Entry", "Batch CSV Processing"])
    else:
        tab_single, = st.tabs(["Single Log Entry"])

    with tab_single:
        with st.container(border=True):
            st.markdown("##### Operational Incident Entry")
            st.caption("Provide mandatory site operational metadata alongside the incident narrative text.")
            
            # Operational Metadata Inputs
            meta_col1, meta_col2, meta_col3 = st.columns(3)
            with meta_col1:
                facility = st.selectbox("Facility / Site Location:", [
                    "Offshore Platform Alpha", 
                    "Block B Manifold Station", 
                    "Refinery Unit 4", 
                    "Onshore Pipeline Segment C"
                ])
            with meta_col2:
                department = st.selectbox("Reporting Department:", [
                    "Operations & Production", 
                    "Maintenance & Integrity", 
                    "HSE & Compliance", 
                    "Logistics & Marine"
                ])
            with meta_col3:
                severity_est = st.selectbox("Preliminary Risk Level:", [
                    "Low (Minor Observation)", 
                    "Medium (Near Miss / Asset Damage)", 
                    "High (Critical / Safety Stand-Down)"
                ])

            # Narrative Input Text
            st.markdown("**Incident Description Narrative**")
            user_input = st.text_area(
                "Narrative Text",
                height=130,
                placeholder="Enter detailed incident description (e.g., Gas leak detected near pressure control valve in Block B manifold...)",
                label_visibility="collapsed"
            )

            col_btn, col_info = st.columns([1, 3])
            with col_btn:
                classify_clicked = st.button("Submit & Classify", type="primary", use_container_width=True)
            with col_info:
                st.caption("⚡ Submissions are processed in real-time and logged to the central HSE audit database.")

            if classify_clicked:
                if user_input.strip():
                    with st.spinner("Executing NLP classification and feature extraction..."):
                        prediction = service.predict_single(user_input)
                        log_incident(
                            st.session_state['username'], 
                            facility, 
                            department, 
                            severity_est, 
                            user_input, 
                            prediction
                        )
                    
                    st.markdown("---")
                    st.markdown("##### Analysis Output")
                    
                    res_col1, res_col2 = st.columns(2)
                    with res_col1:
                        st.info(f"**Predicted HSE Category:** `{prediction}`")
                    with res_col2:
                        st.success("✅ Log entry recorded in master HSE compliance repository.")
                else:
                    st.warning("Please enter a valid report narrative prior to classification.")

    if is_admin:
        with tab_batch:
            with st.container(border=True):
                st.markdown("##### Batch Processing (CSV)")
                st.caption("Upload structured logs containing multiple report text entries for bulk model inference.")
                
                uploaded_file = st.file_uploader("Upload CSV File", type=["csv"], label_visibility="collapsed")

                if uploaded_file is not None:
                    batch_df = pd.read_csv(uploaded_file)
                    st.markdown("---")
                    text_column = st.selectbox("Select Target Narrative Column:", batch_df.columns)

                    if st.button("Execute Batch Classification", type="primary"):
                        with st.spinner("Processing bulk records..."):
                            batch_df["Predicted_Category"] = batch_df[text_column].apply(
                                lambda x: service.predict_single(str(x))
                            )
                            
                            conn = sqlite3.connect('sira_hse_logs.db')
                            c = conn.cursor()
                            now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                            logs_to_insert = [
                                (
                                    now_str, 
                                    st.session_state['username'], 
                                    "Batch Upload", 
                                    "Operations & Production", 
                                    "Unspecified", 
                                    str(row[text_column]), 
                                    str(row['Predicted_Category'])
                                )
                                for _, row in batch_df.iterrows()
                            ]
                            c.executemany(
                                """INSERT INTO incident_logs 
                                   (timestamp, username, facility, department, severity_est, narrative, prediction) 
                                   VALUES (?, ?, ?, ?, ?, ?, ?)""", 
                                logs_to_insert
                            )
                            conn.commit()
                            conn.close()

                        st.success("Batch classification completed and committed to database.")
                        st.dataframe(batch_df, use_container_width=True)

                        csv_data = batch_df.to_csv(index=False).encode("utf-8")
                        st.download_button(
                            "Export Processed Results (CSV)",
                            data=csv_data,
                            file_name="sira_batch_classified.csv",
                            mime="text/csv",
                            type="secondary"
                        )

# --- VIEW 2: HSE ANALYTICS DASHBOARD ---
elif nav_choice == "HSE Analytics Dashboard" and is_admin:
    with st.container(border=True):
        st.markdown("##### Executive Risk Analytics")
        st.caption("Real-time telemetry and risk distribution across operational units.")
        
        df_logs = fetch_logs()
        
        if not df_logs.empty:
            m1, m2, m3, m4 = st.columns(4)
            with m1:
                st.metric("Total Incident Logs", len(df_logs))
            with m2:
                st.metric("Active System Users", df_logs['username'].nunique())
            with m3:
                st.metric("Monitored Facilities", df_logs['facility'].nunique() if 'facility' in df_logs else 1)
            with m4:
                top_category = df_logs['prediction'].mode()[0] if not df_logs['prediction'].empty else "N/A"
                st.metric("Primary Identified Risk", top_category)
            
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
                    color_discrete_sequence=['#0F172A', '#1E293B', '#2563EB', '#475569', '#64748B']
                )
                fig_pie.update_layout(margin=dict(t=10, b=10, l=10, r=10))
                st.plotly_chart(fig_pie, use_container_width=True)
                
            with chart_col2:
                st.markdown("**Submissions by Facility Site**")
                facility_col = 'facility' if 'facility' in df_logs else 'username'
                fac_counts = df_logs[facility_col].value_counts().reset_index()
                fac_counts.columns = ['Facility/Source', 'Log Count']
                fig_bar = px.bar(
                    fac_counts, 
                    x='Facility/Source', 
                    y='Log Count', 
                    text_auto=True, 
                    color_discrete_sequence=['#0F172A']
                )
                fig_bar.update_layout(margin=dict(t=10, b=10, l=10, r=10))
                st.plotly_chart(fig_bar, use_container_width=True)
                
            st.markdown("---")
            st.markdown("##### Master HSE Audit Trail")
            st.dataframe(df_logs, use_container_width=True)
            
            csv_audit = df_logs.to_csv(index=False).encode("utf-8")
            st.download_button(
                "Export Master Audit Log (CSV)",
                data=csv_audit,
                file_name=f"HSE_Master_Audit_{datetime.datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                mime="text/csv",
                type="primary"
            )
        else:
            st.info("No logs present in database.")

# --- VIEW 3: MY SUBMITTED LOGS ---
elif nav_choice == "My Submitted Logs":
    with st.container(border=True):
        st.markdown("##### Personal Submission History")
        st.caption("Review incident records logged under your authenticated session.")
        
        df_user_logs = fetch_logs(username=st.session_state['username'])
        
        if not df_user_logs.empty:
            st.metric("Total Submitted Reports", len(df_user_logs))
            st.dataframe(df_user_logs, use_container_width=True)
        else:
            st.info("No submissions recorded under your user profile.")

# --- VIEW 4: ACCOUNT SETTINGS ---
elif nav_choice == "Account Settings":
    with st.container(border=True):
        st.markdown("##### User Account Parameters")
        st.caption("Manage authentication parameters and user profile identity.")
        st.markdown("---")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**User Profile Information**")
            
            with st.form("edit_profile_form"):
                st.text_input("System Identifier", value=st.session_state["username"], disabled=True)
                st.text_input("Access Permission Level", value=current_user["role"], disabled=True)
                
                updated_name = st.text_input("Full Name", value=current_user["name"])
                updated_password = st.text_input("New Password", type="password", placeholder="Leave blank to retain current")
                
                submit_profile_update = st.form_submit_button("Save Changes", type="primary")
                
                if submit_profile_update:
                    if updated_name.strip():
                        username = st.session_state["username"]
                        st.session_state["user_profiles"][username]["name"] = updated_name.strip()
                        
                        if updated_password.strip():
                            st.session_state["user_profiles"][username]["password"] = updated_password.strip()
                            st.success("Profile details and password updated.")
                        else:
                            st.success("Profile details updated.")
                            
                        st.rerun()
                    else:
                        st.error("Name field cannot be left blank.")
            
        with col2:
            st.markdown("**Session Security Status**")
            st.success(f"Active Session: **{current_user['name']}**")
            st.info("Roles and system permissions are maintained by enterprise administration.")