import streamlit as st
import pandas as pd
from typing import List, Dict, Any

def render_cameras(client):
    st.header("📹 Live Cameras")
    
    try:
        cameras = client.get_cameras()
    except Exception as e:
        st.error(f"Failed to fetch cameras: {e}")
        return

    if not cameras:
        st.info("No cameras found in the system.")
        return
        
    st.metric("Total Cameras", len(cameras))
    
    # Create a DataFrame for easier manipulation
    df = pd.DataFrame(cameras)
    
    # Display Map
    st.subheader("Camera Locations")
    if 'latitude' in df.columns and 'longitude' in df.columns:
        map_df = df.rename(columns={'latitude': 'lat', 'longitude': 'lon'})
        st.map(map_df)
        
    st.subheader("Camera Details")
    # Display grid
    cols = st.columns(3)
    for i, cam in enumerate(cameras):
        with cols[i % 3]:
            st.markdown(f"### {cam.get('name', 'Unknown')}")
            status = cam.get("status", "unknown")
            color = "green" if status == "active" else "red" if status == "inactive" else "orange"
            st.markdown(f"**Status:** :{color}[{status.upper()}]")
            st.markdown(f"**Location:** {cam.get('location', 'N/A')}")
            st.markdown(f"**Lanes:** {cam.get('num_lanes', 'N/A')}")
            with st.expander("More Info"):
                st.write(cam)
