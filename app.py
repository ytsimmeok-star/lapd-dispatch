import streamlit as st
from supabase import create_client

# --- VERBINDUNG ZU DEINER DB ---
# Ersetze die xxxx mit deinen Daten aus Supabase
URL = "https://xxxx.supabase.co"
KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." 
supabase = create_client(URL, KEY)

st.set_page_config(page_title="LAPD Dispatch Web", layout="wide")

# --- STYLING ---
st.markdown("""
    <style>
    .main { background-color: #001D3D; color: white; }
    .stButton>button { background-color: #FFD700; color: black; font-weight: bold; }
    </style>
    """, unsafe_allow_content_html=True)

st.title("🚨 LAPD MDC - Web Dispatch")

# --- EINHEIT HINZUFÜGEN ---
with st.sidebar:
    st.header("Unit Deployment")
    call = st.text_input("Callsign (z.B. 1-A-12)")
    offi = st.text_input("Officers")
    if st.button("DEPLOY UNIT"):
        if call and offi:
            supabase.table("units").insert({"callsign": call, "officers": offi, "status": "AVAILABLE"}).execute()
            st.rerun()

# --- EINHEITEN ANZEIGEN ---
st.subheader("Aktive Einheiten im Feld")
res = supabase.table("units").select("*").execute()

for unit in res.data:
    with st.container(border=True):
        col1, col2, col3 = st.columns([3, 2, 1])
        col1.write(f"**{unit['callsign']}** | {unit['officers']}")
        
        # Status Dropdown
        status_options = ["AVAILABLE", "EN ROUTE", "BUSY", "OFF DUTY"]
        idx = status_options.index(unit['status']) if unit['status'] in status_options else 0
        new_status = col2.selectbox("Status", status_options, index=idx, key=f"s_{unit['id']}")
        
        if new_status != unit['status']:
            supabase.table("units").update({"status": new_status}).eq("id", unit['id']).execute()
            st.rerun()
            
        if col3.button("LÖSCHEN", key=f"d_{unit['id']}"):
            supabase.table("units").delete().eq("id", unit['id']).execute()
            st.rerun()
