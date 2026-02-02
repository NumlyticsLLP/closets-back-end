"""
Dashboard Page - Display system statistics and recent users
"""
import streamlit as st
from database import get_db_connection, get_all_users, get_user_count, get_today_users_count, get_updated_today_count


def show_dashboard():
    """Display dashboard with metrics and recent users."""
    st.markdown("## 🏠 Dashboard")
    
    col1, col2, col3, col4 = st.columns(4)
    
    conn = get_db_connection()
    if conn:
        try:
            # Get metrics
            total_users = get_user_count(conn)
            today_users = get_today_users_count(conn)
            updated_today = get_updated_today_count(conn)
            
            with col1:
                st.metric("👥 Total Users", total_users)
            with col2:
                st.metric("➕ Added Today", today_users)
            with col3:
                st.metric("🔄 Updated Today", updated_today)
            with col4:
                st.metric("🔐 Security", "Bcrypt")
            
            conn.close()
            
            st.markdown("---")
            
            # Recent users
            st.markdown("### 📋 Recent Users")
            df = get_all_users()
            if not df.empty:
                st.dataframe(df.head(10), use_container_width=True, hide_index=True)
            else:
                st.info("No users found in the system.")
                
        except Exception as e:
            st.error(f"Error loading dashboard: {e}")
