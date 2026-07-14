import streamlit as st
import pandas as pd
import plotly.express as px

def render_analytics(client):
    st.header("📈 Hourly Traffic Analytics")
    
    try:
        cameras = client.get_active_cameras()
    except Exception as e:
        st.error(f"Failed to fetch cameras: {e}")
        return
        
    if not cameras:
        st.warning("No active cameras available for analytics.")
        return
        
    camera_map = {cam["name"]: cam["id"] for cam in cameras}
    selected_cam = st.selectbox("Select Camera", options=list(camera_map.keys()))
    hours_to_fetch = st.slider("Hours History", min_value=1, max_value=72, value=24)
    
    cam_id = camera_map[selected_cam]
    
    try:
        data = client.get_analytics_trend(cam_id, hours=hours_to_fetch)
    except Exception as e:
        st.error(f"Failed to fetch analytics: {e}")
        return
        
    if not data:
        st.info("No analytics data available for this camera in the selected timeframe.")
        return
        
    df = pd.DataFrame(data)
    df['hour_bucket'] = pd.to_datetime(df['hour_bucket'])
    df = df.sort_values('hour_bucket')
    
    st.subheader("Vehicle Volume Trend")
    fig_vol = px.line(df, x='hour_bucket', y='total_vehicles', title='Total Vehicles per Hour', markers=True)
    st.plotly_chart(fig_vol, use_container_width=True)
    
    st.subheader("Average Speed Trend")
    fig_spd = px.bar(df, x='hour_bucket', y='avg_speed_kmh', title='Average Speed (km/h) per Hour')
    st.plotly_chart(fig_spd, use_container_width=True)
