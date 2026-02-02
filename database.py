"""
Database connection and operations
"""
import streamlit as st
import mysql.connector
import pandas as pd
from config import DB_CONFIG


def get_db_connection():
    """Establish database connection."""
    try:
        return mysql.connector.connect(**DB_CONFIG)
    except Exception as e:
        st.error(f"Database connection error: {e}")
        return None


def get_all_users():
    """Retrieve all users from database."""
    conn = get_db_connection()
    if not conn:
        return pd.DataFrame()
    
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT id, email, name, role, created_at, updated_at FROM users ORDER BY name")
        users = cursor.fetchall()
        df = pd.DataFrame(users, columns=["ID", "Email", "Name", "Role", "Created", "Updated"])
        cursor.close()
        conn.close()
        return df
    except Exception as e:
        st.error(f"Error retrieving users: {e}")
        return pd.DataFrame()


def get_user_count(conn):
    """Get total count of users."""
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM users")
        count = cursor.fetchone()[0]
        cursor.close()
        return count
    except:
        return 0


def get_today_users_count(conn):
    """Get count of users added today."""
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM users WHERE DATE(created_at) = CURDATE()")
        count = cursor.fetchone()[0]
        cursor.close()
        return count
    except:
        return 0


def get_updated_today_count(conn):
    """Get count of users updated today."""
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM users WHERE DATE(updated_at) = CURDATE()")
        count = cursor.fetchone()[0]
        cursor.close()
        return count
    except:
        return 0
