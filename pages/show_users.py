"""
Show Users Page - Display all users with search functionality
"""
import streamlit as st
from database import get_all_users


def show_users_page():
    """Display all users with search functionality."""
    st.markdown("## 👥 All Users")
    
    df = get_all_users()
    
    if not df.empty:
        st.markdown(f"<h3 style='color: #ffffff !important;'>Found {len(df)} users</h3>", unsafe_allow_html=True)
        
        # Search functionality
        search = st.text_input("🔍 Search by name or email", placeholder="Type to search...")
        
        if search:
            df = df[df["Name"].str.contains(search, case=False) | df["Email"].str.contains(search, case=False)]
        
        st.dataframe(df, use_container_width=True, hide_index=True)
        
        st.markdown("""
        <div class='info-message'>
            ℹ️ Passwords are encrypted with bcrypt and cannot be displayed. Use "Change Password" to set a new password.
        </div>
        """, unsafe_allow_html=True)
    else:
        st.info("📭 No users found in the database.")
