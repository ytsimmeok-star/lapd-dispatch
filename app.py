import streamlit as st
from supabase import create_client

# --- VERBINDUNG (Deine Daten hier eintragen!) ---
URL = "https://djygnispywljflrhxwyv.supabase.co"
KEY = "sb_publishable_sRR_KUa2ujLYxCaktLhRWQ_trkT8vXY"
supabase = create_client(URL, KEY)

st.set_page_config(page_title="LAPD Dispatch Web", layout="wide")

# --- UI HEADER ---
st.title("🚨 LAPD MDC - Web Dispatch")

# --- SIDEBAR: EINHEITEN HINZUFÜGEN ---
with st.sidebar:
    st.header("Unit Deployment")
    call = st.text_input("Callsign (z.B. 1-A-12)")
    offi = st.text_input("Officers")
    if st.button("DEPLOY UNIT"):
        if call and offi:
            try:
                supabase.table("units").insert({"callsign": call, "officers": offi, "status": "AVAILABLE"}).execute()
                st.success("Einheit hinzugefügt!")
                st.rerun()
            except Exception as e:
                st.error(f"Fehler: {e}")

# --- HAUPTBEREICH: EINHEITEN ANZEIGEN ---
st.subheader("Aktive Einheiten im Feld")

try:
    res = supabase.table("units").select("*").execute()
    for unit in res.data:
        # Eine Box für jede Einheit
        with st.container(border=True):
            col1, col2, col3 = st.columns([3, 2, 1])
            
            with col1:
                st.write(f"**Unit:** {unit['callsign']}")
                st.write(f"**Crew:** {unit['officers']}")
            
            with col2:
                # Status Dropdown
                status_options = ["AVAILABLE", "EN ROUTE", "BUSY", "OFF DUTY"]
                # Sucht den aktuellen Index des Status in der Liste
                current_idx = status_options.index(unit['status']) if unit['status'] in status_options else 0
                
                new_status = st.selectbox(
                    "Status ändern", 
                    status_options, 
                    index=current_idx, 
                    key=f"status_{unit['id']}"
                )
                
                # Update bei Änderung
                if new_status != unit['status']:
                    supabase.table("units").update({"status": new_status}).eq("id", unit['id']).execute()
                    st.rerun()
            
            with col3:
                # Lösch-Button
                if st.button("LÖSCHEN", key=f"del_{unit['id']}", type="primary"):
                    supabase.table("units").delete().eq("id", unit['id']).execute()
                    st.rerun()

except Exception as e:
    st.info("Noch keine Einheiten in der Datenbank oder Verbindungsproblem.")
