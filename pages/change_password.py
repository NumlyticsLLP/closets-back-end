"""
Change Password Page - Update user passwords
"""
import streamlit as st
import pandas as pd
import bcrypt
from datetime import datetime
from database import get_db_connection, get_all_users
from utils import gen_password


def change_password_page():
    """Display change password interface."""
    st.markdown("## 🔑 Change Password")
    
    # Get all users for dropdown
    df = get_all_users()
    
    if df.empty:
        st.warning("⚠️ No users found in the database.")
        return
    
    with st.form("change_password_form"):
        # User selection
        user_options = [f"{row['Name']} ({row['Email']})" for _, row in df.iterrows()]
        selected_user = st.selectbox("👤 Select User", user_options)
        
        # Extract email
        email = selected_user.split('(')[1].strip(')')
        
        # Info about password generation
        st.info("🎲 A random password will be generated based on the user's name")
        
        submit = st.form_submit_button("🔄 Change Password", use_container_width=True)
        
        if submit:
            conn = get_db_connection()
            if not conn:
                return
            
            try:
                cursor = conn.cursor()
                cursor.execute("SELECT name FROM users WHERE email = %s", (email,))
                result = cursor.fetchone()
                
                if not result:
                    st.error(f"⚠️ User not found")
                    return
                
                name = result[0]
                
                # Generate random password
                new_password = gen_password(name)
                
                # Hash password
                hashed_password = bcrypt.hashpw(new_password.encode(), bcrypt.gensalt()).decode()
                
                # Update database
                cursor.execute("UPDATE users SET password = %s WHERE email = %s", (hashed_password, email))
                conn.commit()
                
                # Save to Excel
                output_file = f"password_change-{email.split('@')[0]}-{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
                change_df = pd.DataFrame([[email, name, new_password, hashed_password]], 
                                       columns=["email", "name", "password", "bcrypt_password"])
                change_df.to_excel(output_file, index=False)
                
                st.markdown(f"""
                <div class='success-message'>
                    ✅ Password changed successfully!<br>
                    📄 Credentials saved to: <b>{output_file}</b>
                </div>
                """, unsafe_allow_html=True)
                
                # Show new password
                col1, col2 = st.columns(2)
                with col1:
                    st.info(f"**New Password:** `{new_password}`")
                with col2:
                    st.code(new_password, language=None)
                
                cursor.close()
                conn.close()
                
            except Exception as e:
                st.error(f"❌ Error changing password: {e}")
