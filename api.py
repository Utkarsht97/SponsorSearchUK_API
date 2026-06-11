#app2.py (Main Interface script run via streamlit on anaconda prompt)
# -*- coding: utf-8 -*-

import os
import sys
import shutil
import subprocess
import pandas as pd
import streamlit as st
import stripe

try:
    import profile_capture
except ModuleNotFoundError:
    import profilecapture as profile_capture
    sys.modules["profile_capture"] = profile_capture

from profile_capture import render_profile_capture

st.set_page_config(
    page_title="SponsorSearchUK.com",
    page_icon="🇬🇧",
    layout="wide",
    initial_sidebar_state="expanded"
)


BASE_DIR = os.path.dirname(os.path.abspath(__file__))

SPONSOR_SCRIPT = os.path.join(BASE_DIR, "sponsorsearch.py")

GENERATED_PROFILE_DIR = os.path.join(
    BASE_DIR,
    "Repository",
    "Profile",
    "Generated"
)

ACTIVE_PROFILE_PATH = os.path.join(
    BASE_DIR,
    "Repository",
    "Profile",
    "profile_JSON.json"
)

RECOMMENDATIONS_CSV = os.path.join(
    BASE_DIR,
    "CompanyDiscovery",
    "Outputs",
    "ranked_company_recommendations.csv"
)

EXTENSION_ZIP_PATH = os.path.join(
    BASE_DIR,
    "Extension",
    "Applyassist.zip"
)

st.markdown(
    """
    <style>
    
    /* Make placeholder examples visible */
        input::placeholder,
        textarea::placeholder {
            color: #94A3B8 !important;
            opacity: 1 !important;
            font-style: italic !important;
        }

        div[data-baseweb="input"] input::placeholder,
        div[data-baseweb="textarea"] textarea::placeholder {
            color: #94A3B8 !important;
            opacity: 1 !important;
            font-style: italic !important;
        }
    
        input,
        textarea,
        div[data-baseweb="input"] input,
        div[data-baseweb="textarea"] textarea {
            caret-color: #111827 !important;
        }
        
    /* Hide Streamlit menu */
        #MainMenu {
            visibility: hidden;
        }
        
    /* Hide footer */
        footer {
            visibility: hidden;
        }
        
    /* Hide header */
        header {
            visibility: hidden;
        }
        
    /* Hide Streamlit deploy button */
        [data-testid="stToolbar"] {
            display: none !important;
        }
        
    /* Hide bottom-right Streamlit status/badge */
        [data-testid="stStatusWidget"] {
            display: none !important;
        }
        
    /* Hide decoration */
        [data-testid="stDecoration"] {
            display: none !important;
        }
        
        [data-testid="stStatusWidget"],
        [data-testid="stStatusWidget"] *,
        [data-testid="stAppDeployButton"],
        [data-testid="stAppDeployButton"] *,
        [data-testid="stToolbar"],
        [data-testid="stToolbar"] *,
        [data-testid="stDecoration"],
        [data-testid="stDecoration"] * {
        display: none !important;
        visibility: hidden !important;
        height: 0 !important;
        width: 0 !important;
        opacity: 0 !important;
        pointer-events: none !important;
        }
    
        iframe[title="streamlitInfo"],
        iframe[src*="streamlit"],
        a[href*="streamlit.io"],
        a[href*="github.com"] {
        display: none !important;
        visibility: hidden !important;
        }
        
        .stApp {
            background: #ffffff;
            color: #111827;
        }

        .block-container {
            max-width: 1120px;
            padding-top: 2rem;
            padding-bottom: 4rem;
        }

        h1, h2, h3, h4, h5, h6, p, label, span {
            color: #111827 !important;
        }

        section[data-testid="stSidebar"] {
            background: #F3F4F6;
            border-right: 1px solid #E5E7EB;
        }

        section[data-testid="stSidebar"] * {
            color: #111827 !important;
        }

        .brand-title {
            font-size: 2.35rem;
            font-weight: 800;
            letter-spacing: -0.04em;
            color: #0F172A !important;
            margin-bottom: 0.45rem;
        }

        .brand-subtitle {
            font-size: 1.05rem;
            line-height: 1.6;
            color: #334155 !important;
            max-width: 850px;
            margin-bottom: 2rem;
        }

        .hero-card {
            background: #F8FAFC;
            border: 1px solid #CBD5E1;
            border-radius: 16px;
            padding: 1.5rem 1.75rem;
            margin-bottom: 2rem;
        }

        .hero-title {
            font-size: 1.35rem;
            font-weight: 750;
            color: #0F172A !important;
            margin-bottom: 0.4rem;
        }

        .hero-copy {
            font-size: 1rem;
            line-height: 1.6;
            color: #334155 !important;
        }

        input,
        textarea {
            background: #FFFFFF !important;
            color: #111827 !important;
            border: 1px solid #111827 !important;
            border-radius: 2px !important;
        }

        div[data-baseweb="input"] input,
        div[data-baseweb="textarea"] textarea {
            background: #FFFFFF !important;
            color: #111827 !important;
            border-radius: 2px !important;
        }

        div[data-baseweb="select"] > div {
            background: #F3F4F6 !important;
            border: 1px solid #CBD5E1 !important;
            border-radius: 8px !important;
            color: #111827 !important;
        }

        div[data-baseweb="select"] * {
            color: #111827 !important;
        }

        div[data-baseweb="popover"],
        div[data-baseweb="popover"] *,
        ul[role="listbox"],
        li[role="option"],
        li[role="option"] * {
            background: #FFFFFF !important;
            color: #111827 !important;
        }

        li[role="option"]:hover {
            background: #F3F4F6 !important;
        }
        
    /* Profile capture expander headers */
        div[data-testid="stExpander"] details summary {
        background: #F8FAFC !important;
        border: 1px solid #CBD5E1 !important;
        border-radius: 12px !important;
        padding: 1rem 1.1rem !important;
        margin-bottom: 0.75rem !important;
    }
                
        [data-testid="stExpander"] summary {
            font-size: 20px !important;
            font-weight: 700 !important;
        }
        
        [data-testid="stExpander"] summary span {
            font-size: 20px !important;
            font-weight: 700 !important;
        }
        
        [data-testid="stExpander"] summary p {
            font-size: 20px !important;
            font-weight: 700 !important;
        }
        
        [data-testid="stExpander"] summary div {
            font-size: 20px !important;
            font-weight: 700 !important;
        }
        
        div[data-testid="stExpander"] details summary svg {
            fill: #0F172A !important;
            color: #0F172A !important;
        }
        
        div[data-testid="stExpander"] details[open] summary {
            background: #EFF6FF !important;
            border-color: #93C5FD !important;
        }
        
        div[data-testid="stExpander"] details[open] summary p {
            color: #0F172A !important;
        }

        .stButton > button,
        .stFormSubmitButton > button,
        .stDownloadButton > button {
        background-color: #FFFFFF !important;
        color: #111827 !important;
        border: 1px solid #111827 !important;
        border-radius: 8px !important;
        font-weight: 650 !important;
        padding: 0.65rem 1.15rem !important;
        transition: all 0.18s ease-in-out !important;
        }

        .stButton > button:hover,
        .stDownloadButton > button:hover {
            background: #F9FAFB !important;
            color: #111827 !important;
            transform: scale(1.03);
            border-color: #111827 !important;
        }

        .stButton > button *,
        .stFormSubmitButton > button *,
        .stDownloadButton > button * {
        color: #111827 !important;
        }

        .sponsor-card {
            background: #FFFFFF;
            border: 1px solid #E5E7EB;
            border-radius: 14px;
            padding: 1rem 1.15rem;
            margin-bottom: 0.85rem;
            box-shadow: 0 3px 10px rgba(0,0,0,0.03);
        }

        .sponsor-name {
            font-size: 1.05rem;
            font-weight: 750;
            color: #111827 !important;
            margin-bottom: 0.25rem;
        }

        .sponsor-meta {
            font-size: 0.92rem;
            color: #475569 !important;
            margin-bottom: 0.35rem;
        }

        .sponsor-reason {
            font-size: 0.9rem;
            color: #334155 !important;
            line-height: 1.45;
        }

        .blurred-sponsor {
            filter: blur(3px);
            opacity: 0.45;
            pointer-events: none;
            user-select: none;
        }

        .locked-note {
            background: #F8FAFC;
            border: 1px dashed #CBD5E1;
            border-radius: 12px;
            padding: 1rem;
            color: #475569 !important;
            margin: 1rem 0;
        }
        

    /* Sidebar toggle visibility */
        [data-testid="collapsedControl"] {
            background-color: #FFFFFF !important;
            border: 1px solid #CBD5E1 !important;
            border-radius: 8px !important;
        }
        
        [data-testid="collapsedControl"] svg {
            fill: #111827 !important;
            color: #111827 !important;
        }
        
        button[kind="header"] svg {
            fill: #111827 !important;
            color: #111827 !important;
        }
        
        [data-testid="stSidebarCollapseButton"] svg {
            fill: #111827 !important;
            color: #111827 !important;
        }

        .small-note {
            font-size: 0.95rem;
            color: #475569 !important;
        }
        
    /* Force Streamlit expander header styling */
        [data-testid="stExpander"] {
            border: 1px solid #CBD5E1 !important;
            border-radius: 14px !important;
            margin-bottom: 1rem !important;
            background: #FFFFFF !important;
            overflow: hidden !important;
        }
        
        [data-testid="stExpander"] summary {
            background: #EAF2FF !important;
            border-bottom: 1px solid #CBD5E1 !important;
            padding: 1rem 1.25rem !important;
            min-height: 56px !important;
        }
        
        [data-testid="stExpander"] summary p {
            font-size: 1.15rem !important;
            font-weight: 800 !important;
            color: #0F172A !important;
        }
        
        [data-testid="stExpander"] summary svg {
            fill: #0F172A !important;
            color: #0F172A !important;
        }
        
        [data-testid="stExpander"] div[role="region"] {
            background: #FFFFFF !important;
            padding: 1rem !important;
        }
        
    /* Expander title text */
        [data-testid="stExpander"] summary [data-testid="stMarkdownContainer"] p {
            font-size: 20px !important;
            font-weight: 800 !important;
            color: #0F172A !important;
            line-height: 1.3 !important;
        }
        
    /* Expander title force override */
        .css-1yy6isu p {
            font-size: 22px !important;
            font-weight: 800 !important;
            color: #0F172A !important;
            line-height: 1.3 !important;
        }
        
        div[data-baseweb="input"] {
            border-radius: 0px !important;
        }
        
        div[data-baseweb="input"] > div,
        div[data-baseweb="textarea"] > div {
            border: 1px solid #D1D5DB !important;
            border-radius: 6px !important;
            box-shadow: none !important;
        }
        
        div[data-baseweb="input"] input,
        div[data-baseweb="textarea"] textarea {
            border: none !important;
            box-shadow: none !important;
        }
        
        div[data-baseweb="input"] > div:focus-within,
        div[data-baseweb="textarea"] > div:focus-within {
            border: 1px solid #94A3B8 !important;
            box-shadow: 0 0 0 1px #E2E8F0 !important;
        }
        
        .dashboard-hero {
            background: linear-gradient(135deg,#2563EB,#7C3AED);
            border-radius: 22px;
            padding: 2.5rem;
            color: white !important;
            margin-bottom: 2rem;
        }
        
        .dashboard-hero h1 {
            color: white !important;
            font-size: 3rem;
            font-weight: 800;
            margin-bottom: 0.5rem;
        }
        
        .dashboard-hero p {
            color: rgba(255,255,255,0.9) !important;
            font-size: 1.15rem;
            margin-bottom: 0;
        }
        
        .metric-card {
            background: white;
            border: 1px solid #E2E8F0;
            border-radius: 18px;
            padding: 1.4rem;
            text-align: center;
            box-shadow: 0 4px 20px rgba(15,23,42,0.04);
        }
        
        .metric-number {
            font-size: 2rem;
            font-weight: 800;
            color: #2563EB !important;
        }
        
        .metric-label {
            color: #64748B !important;
            font-size: 0.95rem;
        }
        
        .section-card {
            background: white;
            border: 1px solid #E2E8F0;
            border-radius: 18px;
            padding: 1.5rem;
            margin-top: 1rem;
            box-shadow: 0 4px 20px rgba(15,23,42,0.04);
        }
        
        .primary-button {
            background: #2563EB;
            color: white;
            padding: 0.9rem 1.4rem;
            border-radius: 10px;
            text-decoration: none;
            font-weight: 600;
        }
   
   /* Fix file uploader visibility */
        [data-testid="stFileUploader"] section {
            background: #FFFFFF !important;
            border: 1px dashed #CBD5E1 !important;
            border-radius: 12px !important;
        }
    
        [data-testid="stFileUploader"] section * {
            color: #111827 !important;
        }
        
        [data-testid="stFileUploader"] button {
            background: #FFFFFF !important;
            color: #111827 !important;
            border: 1px solid #CBD5E1 !important;
        }
    
        [data-testid="stFileUploader"] small {
            color: #64748B !important;
        }
    
   /* Force visible black typing cursor */
        input,
        textarea,
        div[data-baseweb="input"] input,
        div[data-baseweb="textarea"] textarea {
            caret-color: #111827 !important;
        }
    
   /* Fix download buttons */
        .stDownloadButton button {
            background: #FFFFFF !important;
            color: #111827 !important;
            border: 1px solid #CBD5E1 !important;
            border-radius: 10px !important;
            font-weight: 600 !important;
        }
    
        .stDownloadButton button:hover {
            background: #F8FAFC !important;
            color: #111827 !important;
            border: 1px solid #94A3B8 !important;
        }
        
    /* Fix uploaded file chip visibility */
        [data-testid="stFileUploader"] [data-testid="stFileUploaderFile"] {
            background: #FFFFFF !important;
            color: #111827 !important;
            border: 1px solid #CBD5E1 !important;
            border-radius: 10px !important;
        }
        
        [data-testid="stFileUploader"] [data-testid="stFileUploaderFile"] * {
            color: #111827 !important;
        }
        
        [data-testid="stFileUploader"] [data-testid="stFileUploaderFileName"],
        [data-testid="stFileUploader"] [data-testid="stFileUploaderFileSize"] {
            color: #111827 !important;
        }
        
    /* Uploaded file chip */
        [data-testid="stFileUploaderFile"] {
            background-color: #E5E7EB !important;
            border: 1px solid #CBD5E1 !important;
            color: #111827 !important;
        }

    /* File name */
        [data-testid="stFileUploaderFile"] span {
            color: #111827 !important;
        }

    /* File size */
        [data-testid="stFileUploaderFile"] small {
            color: #374151 !important;
        }

    /* File icon */
        [data-testid="stFileUploaderFile"] svg {
            color: #111827 !important;
            fill: #111827 !important;
        }

    /* Remove button */
        [data-testid="stFileUploaderFile"] button {
            background: transparent !important;
            color: #111827 !important;
        }
    
    </style>
    """,
    unsafe_allow_html=True
)
                                        
st.markdown("""
<style>

/* Main page titles */
h1 {
    color: white !important;
}

/* Section headers */
h2 {
    color: white !important;
}

/* Subsection headers */
h3 {
    color: white !important;
}

/* Expander titles */
.streamlit-expanderHeader {
    color: white !important;
}

/* Markdown headings */
h4, h5, h6 {
    color: #F5F7FA !important;
}

</style>
""", unsafe_allow_html=True)



def safe_text(value):
    if pd.isna(value):
        return ""
    return str(value)


def get_generated_profiles():
    if not os.path.exists(GENERATED_PROFILE_DIR):
        return []

    return sorted([
        file for file in os.listdir(GENERATED_PROFILE_DIR)
        if file.lower().endswith(".json")
    ])

def activate_profile(profile_file):
    source_path = os.path.join(GENERATED_PROFILE_DIR, profile_file)

    if not os.path.exists(source_path):
        return False, "Selected profile could not be found."

    try:
        os.makedirs(os.path.dirname(ACTIVE_PROFILE_PATH), exist_ok=True)
        shutil.copy2(source_path, ACTIVE_PROFILE_PATH)
        return True, f"{profile_file} is now active."
    except Exception as error:
        return False, str(error)

def delete_profile(profile_file):
    profile_path = os.path.join(GENERATED_PROFILE_DIR, profile_file)

    if not os.path.exists(profile_path):
        return False, "Selected profile could not be found."

    try:
        os.remove(profile_path)
        return True, f"{profile_file} has been deleted."
    except Exception as error:
        return False, str(error)

def run_sponsor_discovery():
    env_api_key = os.environ.get("GEMINI_API_KEY", "")

    if not env_api_key:
        return False, "Gemini API key was not found. Please set GEMINI_API_KEY in your environment."

    if not os.path.exists(SPONSOR_SCRIPT):
        return False, "Sponsor search script could not be found."

    sub_env = os.environ.copy()
    sub_env["GEMINI_API_KEY"] = env_api_key

    process = subprocess.run(
        [sys.executable, SPONSOR_SCRIPT],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        env=sub_env
    )

    if process.returncode != 0:
        return False, process.stdout + "\n" + process.stderr

    return True, process.stdout


def load_recommendations():
    if not os.path.exists(RECOMMENDATIONS_CSV):
        return None

    try:
        df = pd.read_csv(RECOMMENDATIONS_CSV, dtype=str)
        df = df.fillna("")
        return df
    except Exception:
        return None

def get_secret_value(key, default=""):
    try:
        if key in st.secrets:
            return st.secrets[key]
    except Exception:
        pass

    return os.environ.get(key, default)


def create_checkout_session():
    stripe.api_key = get_secret_value("STRIPE_SECRET_KEY")
    price_id = get_secret_value("STRIPE_PRICE_ID")
    app_url = get_secret_value("APP_URL")

    if not stripe.api_key or not price_id or not app_url:
        return None, "Stripe secrets are not fully configured."

    try:
        session = stripe.checkout.Session.create(
            mode="payment",
            line_items=[{"price": price_id, "quantity": 1}],
            success_url=f"{app_url}?session_id={{CHECKOUT_SESSION_ID}}",
            cancel_url=app_url
        )
        return session.url, None
    except Exception as error:
        return None, str(error)


def verify_paid_session():
    stripe.api_key = get_secret_value("STRIPE_SECRET_KEY")
    session_id = st.query_params.get("session_id")

    if not session_id:
        return False

    try:
        session = stripe.checkout.Session.retrieve(session_id)
        return session.payment_status == "paid"
    except Exception:
        return False

APPLICATIONS_CSV = os.path.join(
    BASE_DIR,
    "ApplicationManager",
    "applications.csv"
)


def save_application_record(record):
    os.makedirs(os.path.dirname(APPLICATIONS_CSV), exist_ok=True)

    new_df = pd.DataFrame([record])

    if os.path.exists(APPLICATIONS_CSV):
        existing_df = pd.read_csv(APPLICATIONS_CSV, dtype=str).fillna("")
        final_df = pd.concat([existing_df, new_df], ignore_index=True)
    else:
        final_df = new_df

    final_df.to_csv(APPLICATIONS_CSV, index=False)


def load_application_records():
    if not os.path.exists(APPLICATIONS_CSV):
        return pd.DataFrame()

    try:
        return pd.read_csv(APPLICATIONS_CSV, dtype=str).fillna("")
    except Exception:
        return pd.DataFrame()

def render_sponsor_card(row, blurred=False):
    organisation = safe_text(row.get("organisationName", ""))
    industry = safe_text(row.get("industry", ""))
    town = safe_text(row.get("town", ""))
    website = safe_text(row.get("website", ""))
    score = safe_text(row.get("matchScore", ""))
    confidence = safe_text(row.get("confidence", ""))
    reason = safe_text(row.get("matchReason", ""))

    blur_class = " blurred-sponsor" if blurred else ""
    website_text = website if website.strip() else "Not available"

    if blurred:
        reason = "Additional recommendation available in the full results."

    st.markdown(
        f"""
        <div class="sponsor-card{blur_class}">
            <div class="sponsor-name">{organisation}</div>
            <div class="sponsor-meta">{industry} • {town} • Match Score: {score} • Confidence: {confidence}</div>
            <div class="sponsor-meta">Website: {website_text}</div>
            <div class="sponsor-reason">{reason}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

with st.sidebar:

    st.markdown("## SponsorSearchUK.com")
        
    page = st.radio(
        "Navigation",
        ["Home", "Profile Builder", "Sponsor Search", "Application Manager"],
        label_visibility="collapsed"
    )
    
    if page == "Home":
        st.caption("Dashboard")

    elif page == "Profile Builder":
        st.caption("Build and manage your candidate profile")
    
    elif page == "Sponsor Search":
        st.caption("Generate sponsor matches from your active profile")
        
    elif page == "Application Manager":
        st.caption("Track job URLs and open them with the Autofill Assistant")
    
    if "page_redirect" in st.session_state:
        page = st.session_state["page_redirect"]
        del st.session_state["page_redirect"]

    st.markdown("---")
    st.markdown("### Active Profile")

    profiles = get_generated_profiles()

    if profiles:
    
        selected_profile = st.selectbox(
            "Choose profile",
            profiles
        )
    
        col1, col2 = st.columns(2)
    
        with col1:
            if st.button("Use"):
                success, message = activate_profile(selected_profile)
    
                if success:
                    st.success(message)
                else:
                    st.error(message)
    
        with col2:
            if st.button("Delete"):
                success, message = delete_profile(selected_profile)
    
                if success:
                    st.success(message)
                    st.rerun()
                else:
                    st.error(message)
                    
            if st.button("Edit Selected Profile", key="edit_selected_profile_button"):
                st.session_state["profile_to_edit_path"] = os.path.join(
                    GENERATED_PROFILE_DIR,
                    selected_profile
                )
                st.session_state["page_redirect"] = "Profile Builder"
                st.rerun()
    
        st.markdown("---")
    
        if os.path.exists(EXTENSION_ZIP_PATH):
            with open(EXTENSION_ZIP_PATH, "rb") as file:
                st.download_button(
                    label="Download Autofill Assistant",
                    data=file,
                    file_name="ProjectAPPRun_Extension.zip",
                    mime="application/zip"
                )
        else:
            st.caption("Autofill Assistant not available yet.")
    
    else:
        st.info("Create a profile first.")

if page == "Home":

    st.markdown(
    """
    <div class="dashboard-hero">
    
    <h1 style="font-size:3rem;font-weight:800;color:#E0F2FE !important;margin-bottom:10px;text-shadow: 0 2px 10px rgba(0,0,0,0.15)">
    <img src="https://flagcdn.com/gb.svg"
         width="40"
         style="vertical-align:middle;margin-right:12px;">
    SponsorSearchUK
    </h1>
    
    <p style="font-size:1.2rem;color:white;">
    Find Relevant UK Sponsors Faster.
    <br>
    Profile-first sponsor discovery powered by AI.
    </p>
    
    </div>
    """,
    unsafe_allow_html=True
    )

    c1, c2 = st.columns(2)

    with c1:
        if st.button("Build Profile"):
            st.session_state["page_redirect"] = "Profile Builder"
            st.rerun()

    with c2:
        if st.button("Discover Sponsors"):
            st.session_state["page_redirect"] = "Sponsor Search"
            st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)

    m1, m2, m3 = st.columns(3)

    with m1:
        st.markdown(
            """
            <div class="metric-card">
                <div class="metric-number">150,000+</div>
                <div class="metric-label">Registered Sponsors</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with m2:
        st.markdown(
            """
            <div class="metric-card">
                <div class="metric-number">AI</div>
                <div class="metric-label">Profile Matching</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with m3:
        st.markdown(
            """
            <div class="metric-card">
                <div class="metric-number">Minutes</div>
                <div class="metric-label">Instead Of Weeks</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown("<br>", unsafe_allow_html=True)
        
    st.markdown(
    """
    <div class="section-card">
    <h3 style="margin-top:0;">How It Works</h3>
    
    <p><strong>1. Build Your Profile</strong><br>
    Create a reusable candidate profile once.</p>
    
    <p><strong>2. Generate Sponsor Matches</strong><br>
    AI identifies relevant UK sponsor companies.</p>
    
    <p><strong>3. Apply Faster</strong><br>
    Use your profile and extension to streamline applications.</p>
    </div>
    """,
    unsafe_allow_html=True
    )

if page == "Profile Builder":

    render_profile_capture()

if page == "Sponsor Search":

    st.markdown(
        """
        <div class="dashboard-hero">
            <h1>Sponsor Discovery</h1>
            <p>
                Generate AI-ranked sponsor matches using your active profile.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    # KEEP ALL YOUR EXISTING SPONSOR SEARCH LOGIC BELOW THIS LINE

    run_button = st.button("Generate Sponsor Matches")

    if run_button:
        with st.spinner("Finding relevant sponsor companies..."):
            success, message = run_sponsor_discovery()

        if success:
            st.success("Sponsor Search completed successfully.")
        else:
            st.error("Sponsor Search could not be completed.")
            with st.expander("Show details"):
                st.code(message, language="text")

    recommendations = load_recommendations()

    if recommendations is not None and not recommendations.empty:
        st.markdown("### Recommended Sponsor Companies")
        st.markdown(
            "<p class='small-note'>Showing your top 5 recommended sponsor companies. Additional matches are previewed below.</p>",
            unsafe_allow_html=True
        )

        visible_count = 5
        preview_count = 5

    top_visible = recommendations.head(visible_count)

    locked_preview = recommendations.iloc[
        visible_count:visible_count + preview_count
    ]

    for _, row in top_visible.iterrows():
        render_sponsor_card(row, blurred=False)
    
    if not locked_preview.empty:

        st.markdown(
        """
        <div class="locked-note">
            Previewing additional matches. Unlock the full CSV to view your complete matched sponsor list.
        </div>
        """,
        unsafe_allow_html=True
    )
    
    for _, row in locked_preview.iterrows():
        render_sponsor_card(row, blurred=True)
    
    paid = verify_paid_session()
    
    if paid:
        csv_data = recommendations.to_csv(index=False)
    
        st.success("Payment verified. Your matched sponsor list is ready.")
    
        st.download_button(
            label="📥 Download Matched Sponsor List CSV",
            data=csv_data,
            file_name="matched_sponsor_list.csv",
            mime="text/csv"
        )
    
    else:
        checkout_url, checkout_error = create_checkout_session()
    
        if checkout_url:
            st.markdown(
                f"""
                <a href="{checkout_url}" target="_blank" style="
                    display:inline-block;
                    padding:0.75rem 1.2rem;
                    border-radius:10px;
                    background:#2563EB;
                    color:#FFFFFF;
                    text-decoration:none;
                    font-weight:700;
                    margin-top:1rem;
                ">
                    Unlock Full Sponsor List
                </a>
                """,
                unsafe_allow_html=True
            )
        else:
            st.warning(f"Payment unlock is not available: {checkout_error}")
            
if page == "Application Manager":

    st.markdown(
        """
        <div class="dashboard-hero">
            <h1>Application Manager</h1>
            <p>
                Save job opportunities, track application status and open roles with the Autofill Assistant.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    col1, col2 = st.columns([1, 3])

    with col1:
    
        if os.path.exists(EXTENSION_ZIP_PATH):
            with open(EXTENSION_ZIP_PATH, "rb") as file:
                st.download_button(
                    label="⬇ Download Autofill Extension",
                    data=file,
                    file_name="ProjectAPPRun_Extension.zip",
                    mime="application/zip",
                    key="download_extension_application_manager"
                )
        else:
            st.info("Autofill Extension is not available yet.")
    
    with col2:
    
        st.info(
            "Install the SponsorSearchUK Autofill Assistant to automatically populate application forms."
        )

    st.markdown("### Add New Application")

    with st.form("application_manager_form"):

        job_url = st.text_input(
            "Job URL",
            placeholder="Example: https://company.com/careers/job-123"
        )

        col1, col2 = st.columns(2)

        with col1:
            company_name = st.text_input(
                "Company Name",
                placeholder="Example: Deloitte"
            )

            role_title = st.text_input(
                "Role Title",
                placeholder="Example: Business Analyst"
            )

        with col2:
            application_status = st.selectbox(
                "Application Status",
                [
                    "Saved",
                    "Sign-in Required",
                    "Ready to Autofill",
                    "Submitted",
                    "Rejected"
                ]
            )

            final_form_url = st.text_input(
                "Final Form URL",
                placeholder="Optional. Paste the URL after sign-in if different."
            )

            notes = st.text_area(
                "Notes",
                placeholder="Example: Requires Workday sign-in before reaching the form."
            )
    
        save_application = st.form_submit_button("Save Application")

    if save_application:
    
        if not job_url.strip():
            st.error("Please enter a Job URL before saving.")
        else:
            record = {
                "created_at": pd.Timestamp.now().isoformat(),
                "job_url": job_url.strip(),
                "final_form_url": final_form_url.strip(),
                "company_name": company_name.strip(),
                "role_title": role_title.strip(),
                "application_status": application_status,
                "notes": notes.strip()
            }
    
            save_application_record(record)
    
            st.success("Application saved.")
    
    applications = load_application_records()
    
    if not applications.empty:
    
        st.markdown("### Saved Applications")
    
        for index, row in applications.iloc[::-1].iterrows():
    
            display_title = row.get("role_title", "") or "Untitled Role"
            display_company = row.get("company_name", "") or "Unknown Company"
            display_status = row.get("application_status", "Saved")
            open_url = row.get("final_form_url", "") or row.get("job_url", "")
    
            st.markdown(
                f"""
                <div class="sponsor-card">
                    <div class="sponsor-name">{display_title}</div>
                    <div class="sponsor-meta">{display_company} • {display_status}</div>
                    <div class="sponsor-reason">{row.get("notes", "")}</div>
                </div>
                """,
                unsafe_allow_html=True
            )
    
            if open_url:
                st.markdown(
                    f"""
                    <a href="{open_url}" target="_blank" style="
                        display:inline-block;
                        padding:0.65rem 1rem;
                        border-radius:10px;
                        background:#2563EB;
                        color:#FFFFFF;
                        text-decoration:none;
                        font-weight:700;
                        margin-bottom:1rem;
                    ">
                        Open Job Page
                    </a>
                    """,
                    unsafe_allow_html=True
                )
    
    else:
        st.info("No applications saved yet.")
