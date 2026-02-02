"""
Admin Login Page
"""
import streamlit as st
import bcrypt
from database import get_db_connection


def verify_admin_credentials(email, password):
    """Verify admin login credentials."""
    conn = get_db_connection()
    if not conn:
        return False, None
    
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT id, email, name, password, role FROM users WHERE email = %s", (email,))
        user = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if user:
            user_id, user_email, user_name, hashed_password, role = user
            
            # Verify password
            if bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8')):
                # Check if user is admin
                if role and role.lower() == 'admin':
                    return True, {"id": user_id, "email": user_email, "name": user_name, "role": role}
                else:
                    return False, {"error": "Access denied. Admin privileges required."}
        
        return False, None
    except Exception as e:
        st.error(f"Login error: {e}")
        return False, None


def show_login_page():
    """Display the admin login page."""
    
    st.markdown("""
        <div style='text-align: center; padding: 3rem 0 2rem 0; animation: fadeIn 1s ease;'>
            <div style='font-size: 5rem; margin-bottom: 1rem;'>🔐</div>
            <h1 style='font-size: 3rem; margin-bottom: 0.5rem; background: linear-gradient(135deg, #fcb900 0%, #ffd700 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent;'>
                Admin Login
            </h1>
            <p style='font-size: 1.2rem; color: #7f8c8d; font-weight: 400; margin-top: 0;'>
                🚀 User Management System - Secure Access
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Center the login form
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("""
            <div style='text-align: center; padding: 1rem 0;'>
                <h3 style='color: #2c3e50; margin-bottom: 2rem;'>🔑 Administrator Access</h3>
            </div>
        """, unsafe_allow_html=True)
        
        with st.form("login_form", clear_on_submit=False):
            email = st.text_input(
                "📧 Email Address",
                placeholder="admin@example.com",
                key="login_email"
            )
            
            password = st.text_input(
                "🔒 Password",
                type="password",
                placeholder="Enter your password",
                key="login_password"
            )
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            col_a, col_b, col_c = st.columns([1, 2, 1])
            with col_b:
                submit = st.form_submit_button("🚀 LOGIN", use_container_width=True)
            
            if submit:
                if not email or not password:
                    st.error("⚠️ Please enter both email and password")
                else:
                    with st.spinner("🔄 Authenticating..."):
                        is_valid, user_data = verify_admin_credentials(email, password)
                        
                        if is_valid:
                            # Store session data
                            st.session_state.authenticated = True
                            st.session_state.user_data = user_data
                            st.success(f"✅ Welcome back, {user_data['name']}!")
                            st.rerun()
                        elif user_data and "error" in user_data:
                            st.error(f"❌ {user_data['error']}")
                        else:
                            st.error("❌ Invalid email or password")
        
        # Info box
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.info("ℹ️ **Note:** Only users with admin role can access the management system.")
        
        st.markdown("""
            <div style='text-align: center; padding: 2rem 0 1rem 0;'>
                <p style='color: #7f8c8d; font-size: 0.9rem;'>
                    🔒 Protected by enterprise-grade encryption
                </p>
            </div>
        """, unsafe_allow_html=True)


def logout():
    """Clear session and logout user."""
    st.session_state.authenticated = False
    st.session_state.user_data = None
    st.rerun()
