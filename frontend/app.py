import streamlit as st
from api_client import APIClient
from views.cameras_view import render_cameras
from views.emergencies_view import render_emergencies
from views.analytics_view import render_analytics

st.set_page_config(
    page_title="Smart Traffic Dashboard",
    page_icon="🚦",
    layout="wide",
)

@st.cache_resource
def get_api_client():
    return APIClient(base_url="http://localhost:8000/api/v1")

def main():
    st.sidebar.title("🚦 Smart Traffic Admin")
    client = get_api_client()
    
    page = st.sidebar.radio(
        "Navigation",
        ["📹 Live Cameras", "🚨 Emergencies", "📈 Analytics"]
    )
    
    if page == "📹 Live Cameras":
        render_cameras(client)
    elif page == "🚨 Emergencies":
        render_emergencies(client)
    elif page == "📈 Analytics":
        render_analytics(client)

if __name__ == "__main__":
    main()
