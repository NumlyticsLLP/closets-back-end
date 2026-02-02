"""
User Management System - Main Application Entry Point
A professional web-based user management system with password generation
"""
import streamlit as st
import os

# Import page modules
from pages.login import show_login_page, logout
from pages.dashboard import show_dashboard
from pages.add_users import add_users_page
from pages.show_users import show_users_page
from pages.change_password import change_password_page
from pages.remove_user import remove_user_page
from database import get_db_connection, get_user_count, get_today_users_count

# --- Page Configuration ---
st.set_page_config(
    page_title="User Management System",
    page_icon="🔐",
    layout="wide",
    initial_sidebar_state="expanded"
)


# --- Initialize Session State ---
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'user_data' not in st.session_state:
    st.session_state.user_data = None


# --- Load External CSS ---
def load_css():
    """Load external CSS styling."""
    css_file = os.path.join(os.path.dirname(__file__), "style.css")
    with open(css_file, "r", encoding="utf-8") as f:
        css_content = f.read()
    st.markdown(f"<style>{css_content}</style>", unsafe_allow_html=True)


load_css()


# --- Main Application ---
def main():
    """Main application logic with navigation and page routing."""
    
    # Check authentication
    if not st.session_state.authenticated:
        show_login_page()
        return
    
    # Get user data
    user_data = st.session_state.user_data
    
    # Header with logo
    st.markdown(f"""
        <div style='text-align: center; padding: 2rem 0; animation: fadeIn 1s ease;'>
            <div style='font-size: 4rem; margin-bottom: 1rem;'>🔐</div>
            <h1 style='font-size: 3rem; margin-bottom: 0.5rem; background: linear-gradient(135deg, #fcb900 0%, #ffd700 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent;'>
                User Management System
            </h1>
            <p style='font-size: 1.2rem; color: #7f8c8d; font-weight: 400; margin-top: 0;'>
                🚀 Secure Password Generator & Professional User Administration
            </p>
            <p style='font-size: 1rem; color: #2c3e50; font-weight: 500; margin-top: 0.5rem;'>
                👤 Logged in as: <strong>{user_data['name']}</strong> ({user_data['role']})
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Sidebar Navigation
    with st.sidebar:
        st.markdown(f"""
            <div style='text-align: center; padding: 1.5rem 0; border-bottom: 2px solid #fcb900; margin-bottom: 2rem;'>
                <div style='font-size: 2.5rem; margin-bottom: 0.5rem;'>⚙️</div>
                <h2 style='margin: 0; color: #2c3e50; font-size: 1.5rem;'>Control Panel</h2>
                <p style='margin: 0.5rem 0 0 0; color: #7f8c8d; font-size: 0.9rem;'>👤 {user_data['name']}</p>
                <p style='margin: 0.25rem 0 0 0; color: #95a5a6; font-size: 0.8rem;'>🔰 {user_data['role'].upper()}</p>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown("### 📋 Navigation")
        page = st.radio(
            "Select Operation:",
            ["🏠 Dashboard", "➕ Add Users", "👥 Show Users", "🔑 Change Password", "🗑️ Remove User"],
            label_visibility="collapsed"
        )
        
        st.markdown("---")
        st.markdown("### 📊 Quick Stats")
        
        # Get user count
        conn = get_db_connection()
        if conn:
            try:
                user_count = get_user_count(conn)
                st.metric("👥 Total Users", user_count)
                
                today_count = get_today_users_count(conn)
                st.metric("✨ Added Today", today_count, delta=f"+{today_count}")
                
                conn.close()
            except:
                st.metric("👥 Total Users", "N/A")
        
        st.markdown("---")
        
        # Logout button
        if st.button("🚪 LOGOUT", use_container_width=True, type="primary"):
            logout()
        
        st.markdown("""
            <div style='text-align: center; padding: 1rem; background: linear-gradient(135deg, #fcb90020 0%, #ffd70020 100%); border-radius: 12px; margin-top: 2rem;'>
                <p style='margin: 0; font-size: 0.9rem; color: #7f8c8d;'>🔒 Secured with Bcrypt</p>
                <p style='margin: 0.5rem 0 0 0; font-size: 0.8rem; color: #95a5a6;'>Enterprise-grade encryption</p>
            </div>
        """, unsafe_allow_html=True)
    
    # Page Routing
    if page == "🏠 Dashboard":
        show_dashboard()
    elif page == "➕ Add Users":
        add_users_page()
    elif page == "👥 Show Users":
        show_users_page()
    elif page == "🔑 Change Password":
        change_password_page()
    elif page == "🗑️ Remove User":
        remove_user_page()


# --- Run Application ---
if __name__ == "__main__":
    main()
