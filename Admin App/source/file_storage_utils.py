"""
File Storage Utilities - Handles saving data to new or existing files
"""

import os
import pandas as pd
from datetime import datetime
import json


class FileStorageManager:
    """Manages storage of user data to new or existing files."""
    
    @staticmethod
    def save_user_data(data_dict, storage_option, file_path, data_type="user"):
        """
        Save user data based on storage option.
        
        Args:
            data_dict: Dictionary containing user data
            storage_option: "new" or "existing"
            file_path: Path to folder (for new) or file (for existing)
            data_type: "user" or "password_change" for different naming
            
        Returns:
            tuple: (success, message, files_created)
        """
        try:
            files_created = []
            
            if storage_option == "new":
                return FileStorageManager._save_to_new_files(
                    data_dict, file_path, data_type
                )
            elif storage_option == "existing":
                return FileStorageManager._save_to_existing_file(
                    data_dict, file_path
                )
            else:
                return False, "Invalid storage option", []
                
        except Exception as e:
            return False, f"Error saving data: {str(e)}", []
    
    @staticmethod
    def _save_to_new_files(data_dict, folder_path, data_type):
        """Save data to new files in specified folder."""
        files_created = []
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        try:
            # Create DataFrame
            df = pd.DataFrame([data_dict])
            
            # Create individual file based on type
            if data_type == "user":
                individual_filename = f"user_credentials_{timestamp}.xlsx"
                consolidated_filename = "all_users_data.csv"
            elif data_type == "password_change":
                individual_filename = f"password_change_{timestamp}.xlsx"
                consolidated_filename = "all_password_changes.csv"
            else:
                individual_filename = f"data_{timestamp}.xlsx"
                consolidated_filename = "all_data.csv"
            
            # Save individual Excel file
            individual_filepath = os.path.join(folder_path, individual_filename)
            df.to_excel(individual_filepath, index=False)
            files_created.append(individual_filename)
            
            # Save/update consolidated CSV file
            consolidated_filepath = os.path.join(folder_path, consolidated_filename)
            if os.path.exists(consolidated_filepath):
                # Append to existing consolidated file
                existing_df = pd.read_csv(consolidated_filepath)
                updated_df = pd.concat([existing_df, df], ignore_index=True)
                updated_df.to_csv(consolidated_filepath, index=False)
            else:
                # Create new consolidated file
                df.to_csv(consolidated_filepath, index=False)
            files_created.append(consolidated_filename)
            
            success_message = (
                f"✅ Data saved successfully!\n\n"
                f"📄 Individual file: {individual_filename}\n"
                f"📊 Consolidated file: {consolidated_filename}\n\n"
                f"📁 Location: {folder_path}"
            )
            
            return True, success_message, files_created
            
        except Exception as e:
            return False, f"Error creating new files: {str(e)}", files_created
    
    @staticmethod
    def _save_to_existing_file(data_dict, file_path):
        """Save data to existing file."""
        try:
            # Create DataFrame
            new_df = pd.DataFrame([data_dict])
            
            # Get file extension
            file_ext = os.path.splitext(file_path)[1].lower()
            
            if file_ext == '.csv':
                # Handle CSV files
                if os.path.exists(file_path):
                    # Read existing data and append
                    existing_df = pd.read_csv(file_path)
                    updated_df = pd.concat([existing_df, new_df], ignore_index=True)
                else:
                    # File doesn't exist, create new
                    updated_df = new_df
                
                updated_df.to_csv(file_path, index=False)
                
            elif file_ext in ['.xlsx', '.xls']:
                # Handle Excel files
                if os.path.exists(file_path):
                    # Read existing data and append
                    existing_df = pd.read_excel(file_path)
                    updated_df = pd.concat([existing_df, new_df], ignore_index=True)
                else:
                    # File doesn't exist, create new
                    updated_df = new_df
                
                updated_df.to_excel(file_path, index=False)
                
            else:
                # Unsupported format, default to CSV
                if not file_path.endswith('.csv'):
                    file_path = file_path + '.csv'
                
                if os.path.exists(file_path):
                    existing_df = pd.read_csv(file_path)
                    updated_df = pd.concat([existing_df, new_df], ignore_index=True)
                else:
                    updated_df = new_df
                
                updated_df.to_csv(file_path, index=False)
            
            filename = os.path.basename(file_path)
            folder_path = os.path.dirname(file_path)
            
            success_message = (
                f"✅ Data updated successfully!\n\n"
                f"📄 Updated file: {filename}\n\n"
                f"📁 Location: {folder_path}"
            )
            
            return True, success_message, [filename]
            
        except Exception as e:
            return False, f"Error updating existing file: {str(e)}", []
    
    @staticmethod
    def prepare_user_data(name, email, password, role):
        """Prepare user data dictionary with timestamp."""
        return {
            "Name": name,
            "Email": email,
            "Password": password,
            "Role": role,
            "Created": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
    
    @staticmethod
    def prepare_password_change_data(name, email, old_password, new_password):
        """Prepare password change data dictionary with timestamp."""
        return {
            "Name": name,
            "Email": email,
            "Old_Password": old_password if old_password else "N/A",
            "New_Password": new_password,
            "Changed_Date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "Changed_Time": datetime.now().strftime("%H:%M:%S")
        }
    
    @staticmethod
    def get_file_info(file_path):
        """Get information about an existing file."""
        try:
            if not os.path.exists(file_path):
                return {"exists": False}
            
            file_stats = os.stat(file_path)
            file_ext = os.path.splitext(file_path)[1].lower()
            
            # Try to read the file to get row count
            row_count = 0
            try:
                if file_ext == '.csv':
                    df = pd.read_csv(file_path)
                elif file_ext in ['.xlsx', '.xls']:
                    df = pd.read_excel(file_path)
                else:
                    df = None
                
                if df is not None:
                    row_count = len(df)
            except:
                pass
            
            return {
                "exists": True,
                "size": file_stats.st_size,
                "modified": datetime.fromtimestamp(file_stats.st_mtime).strftime("%Y-%m-%d %H:%M:%S"),
                "row_count": row_count,
                "extension": file_ext
            }
            
        except Exception as e:
            return {"exists": False, "error": str(e)}