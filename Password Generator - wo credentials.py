import pandas as pd
import bcrypt
import random
import string
import mysql.connector

# --- Input Data ---
# Example: data = [("username@cbdbarrie.com", "username"),
#                   ("username2@cbdbarrie.com", "username2")]

data = [("m.saddam@cbdbarrie.com", "Marwah Saddam")]

output_file = "user_credentials-20260130.xlsx"

# Remove duplicates
data = list(dict.fromkeys(data))

special_chars = "!@#$%&*-_?/\|+=-.,><()"

# Function to generate password
def gen_password(name):
    parts = name.strip().split()
    
    # Choose 3 letters from either first or last name
    if len(parts) >= 2:
        base_source = random.choice([parts[0], parts[1]])
    else:
        base_source = parts[0] if parts else "usr"
    
    name_part = base_source[:3].capitalize()  # Always take first 3 letters, capitalized

    # Remaining 3 characters
    digit = random.choice(string.digits)
    special = random.choice(special_chars)
    rand_char = random.choice(string.ascii_lowercase + string.digits)
    
    # Randomly position the name chunk in one of the four positions
    others = [digit, special, rand_char]
    insert_position = random.randint(0, 3)
    parts_combined = others[:insert_position] + [name_part] + others[insert_position:]
    
    return ''.join(parts_combined)

# Build DataFrame
df = pd.DataFrame(data, columns=["email", "name"])
df["password"] = df["name"].apply(gen_password)
df["bcrypt_password"] = df["password"].apply(lambda p: bcrypt.hashpw(p.encode(), bcrypt.gensalt()).decode())

# --- Save to Excel (human-readable passwords) ---
df.to_excel(output_file, index=False)
print(f"✅ Excel file saved as '{output_file}'")

# --- Insert into MySQL ---
try:
    conn = mysql.connector.connect(
        host="",
        user="",
        password="",
        database=""
    )
    cursor = conn.cursor()

    for _, row in df.iterrows():
        cursor.callproc("sp_insert_user", (
            row["email"],
            row["name"],
            row["bcrypt_password"],
            "user"
        ))

    conn.commit()
    cursor.close()
    conn.close()
    print("✅ All users inserted/updated in MySQL successfully!")

except Exception as e:
    print("❌ Error inserting into MySQL:", e)
