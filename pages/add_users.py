"""
Add Users Page - Add single or multiple users to the system
"""
import streamlit as st
import pandas as pd
import bcrypt
from datetime import datetime
from database import get_db_connection
from utils import gen_password


def add_users_page():
    """Display add users interface."""
    st.markdown("## ➕ Add New Users")
    
    st.markdown("""
    <div class='info-message'>
        📝 Add single or multiple users. Passwords will be generated automatically and saved to an Excel file.
    </div>
    """, unsafe_allow_html=True)
    
    # Input method selection
    input_method = st.radio("Choose input method:", ["Single User", "Multiple Users (Bulk)"], horizontal=True)
    
    if input_method == "Single User":
        with st.form("single_user_form"):
            col1, col2 = st.columns(2)
            with col1:
                email = st.text_input("📧 Email Address", placeholder="user@example.com")
            with col2:
                name = st.text_input("👤 Full Name", placeholder="John Doe")
            
            submit = st.form_submit_button("➕ Add User", use_container_width=True)
            
            if submit:
                if email and name:
                    users = [(email, name)]
                    process_users(users)
                else:
                    st.error("❌ Please fill in all fields!")
    
    else:  # Multiple users
        st.markdown("### Enter multiple users (one per line)")
        st.markdown("Format: `email,name` (e.g., `john@example.com,John Doe`)")
        
        user_input = st.text_area("📝 User List", height=200, placeholder="user1@example.com,User One\nuser2@example.com,User Two")
        
        if st.button("➕ Add All Users", use_container_width=True):
            if user_input:
                lines = user_input.strip().split('\n')
                users = []
                for line in lines:
                    if ',' in line:
                        parts = line.split(',')
                        if len(parts) >= 2:
                            users.append((parts[0].strip(), parts[1].strip()))
                
                if users:
                    process_users(users)
                else:
                    st.error("❌ No valid users found. Please check the format.")
            else:
                st.error("❌ Please enter at least one user!")


def process_users(users):
    """Process and add users to database."""
    with st.spinner("Processing users..."):
        # Remove duplicates
        users = list(dict.fromkeys(users))
        
        # Build DataFrame
        df = pd.DataFrame(users, columns=["email", "name"])
        df["password"] = df["name"].apply(gen_password)
        df["bcrypt_password"] = df["password"].apply(lambda p: bcrypt.hashpw(p.encode(), bcrypt.gensalt()).decode())
        
        # Save to Excel
        output_file = f"user_credentials-{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        df.to_excel(output_file, index=False)
        
        # Insert into MySQL
        conn = get_db_connection()
        if not conn:
            return
        
        try:
            cursor = conn.cursor()
            success_count = 0
            failed = []
            
            for _, row in df.iterrows():
                try:
                    cursor.callproc("sp_insert_user", (
                        row["email"],
                        row["name"],
                        row["bcrypt_password"],
                        "user"
                    ))
                    success_count += 1
                except Exception as e:
                    failed.append((row['email'], str(e)))
            
            conn.commit()
            
            st.markdown(f"""
            <div class='success-message'>
                ✅ Successfully added {success_count}/{len(df)} users!<br>
                📄 Credentials saved to: <b>{output_file}</b>
            </div>
            """, unsafe_allow_html=True)
            
            if failed:
                st.warning(f"⚠️ {len(failed)} user(s) failed to add")
            
            # Show credentials
            st.markdown("### 📋 Generated Credentials")
            display_df = df[["email", "name", "password"]].copy()
            st.dataframe(display_df, use_container_width=True, hide_index=True)
            
            cursor.close()
            conn.close()
            
        except Exception as e:
            st.error(f"❌ Database error: {e}")
