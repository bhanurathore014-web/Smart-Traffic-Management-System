import streamlit as st
import pandas as pd

def render_emergencies(client):
    st.header("🚨 Active Emergencies")
    
    try:
        emergencies = client.get_active_emergencies()
    except Exception as e:
        st.error(f"Failed to fetch emergencies: {e}")
        return
        
    if not emergencies:
        st.success("No active emergencies at the moment. Traffic is flowing smoothly!")
        return
        
    st.metric("Active Emergencies", len(emergencies))
    
    for em in emergencies:
        with st.container():
            st.error(f"Priority {em.get('priority', 'N/A')} {em.get('emergency_type', 'Unknown').upper()} detected!")
            cols = st.columns(3)
            with cols[0]:
                st.write(f"**Camera ID:** {em.get('camera_id')}")
                st.write(f"**Time:** {em.get('timestamp')}")
            with cols[1]:
                st.write(f"**Confidence:** {em.get('detection_confidence', 'N/A')}")
                st.write(f"**Green Corridor:** {'Yes' if em.get('green_corridor_activated') else 'No'}")
            with cols[2]:
                if st.button("Resolve", key=f"resolve_{em.get('id')}"):
                    try:
                        client.resolve_emergency(em.get('id'), "Resolved by Admin via Dashboard")
                        st.success("Emergency resolved!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Failed to resolve: {e}")
            st.divider()
