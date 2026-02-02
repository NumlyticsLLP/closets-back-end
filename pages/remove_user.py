"""
Remove User Page - Delete users from the system
"""
import streamlit as st
from database import get_db_connection, get_all_users


def remove_user_page():
    """Display remove user interface."""
    st.markdown("## 🗑️ Remove User")
    
    st.markdown("""
    <div class='error-message'>
        ⚠️ <b>Warning:</b> This action cannot be undone. The user will be permanently deleted.
    </div>
    """, unsafe_allow_html=True)
    
    # Get all users
    df = get_all_users()
    
    if df.empty:
        st.warning("⚠️ No users found in the database.")
        return
    
    with st.form("remove_user_form"):
        user_options = [f"{row['Name']} ({row['Email']})" for _, row in df.iterrows()]
        selected_user = st.selectbox("👤 Select User to Remove", user_options)
        
        # Extract email
        email = selected_user.split('(')[1].strip(')')
        
        confirm = st.checkbox("✅ I confirm I want to delete this user")
        
        submit = st.form_submit_button("🗑️ Delete User", use_container_width=True)
        
        if submit:
            if not confirm:
                st.error("❌ Please confirm the deletion by checking the box above.")
                return
            
            conn = get_db_connection()
            if not conn:
                return
            
            try:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM users WHERE email = %s", (email,))
                conn.commit()
                
                if cursor.rowcount > 0:
                    st.markdown(f"""
                    <div class='success-message'>
                        ✅ User '{email}' has been successfully removed!
                    </div>
                    """, unsafe_allow_html=True)
                    st.balloons()
                else:
                    st.warning(f"⚠️ User '{email}' not found.")
                
                cursor.close()
                conn.close()
                
            except Exception as e:
                st.error(f"❌ Error removing user: {e}")
