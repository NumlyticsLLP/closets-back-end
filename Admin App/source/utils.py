"""
Utility functions for password generation and other helpers
"""
import sys
import os
import random
import string
from config import SPECIAL_CHARS


def resource_path(relative_path: str) -> str:
    """Get absolute path to a resource — works for dev and PyInstaller frozen EXE."""
    if getattr(sys, 'frozen', False):
        base = sys._MEIPASS
    else:
        base = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base, relative_path)


def gen_password(name):
    """Generate a random password based on user's name."""
    parts = name.strip().split()
    
    if len(parts) >= 2:
        base_source = random.choice([parts[0], parts[1]])
    else:
        base_source = parts[0] if parts else "usr"
    
    name_part = base_source[:3].capitalize()
    digit = random.choice(string.digits)
    special = random.choice(SPECIAL_CHARS)
    rand_char = random.choice(string.ascii_lowercase + string.digits)
    
    others = [digit, special, rand_char]
    insert_position = random.randint(0, 3)
    parts_combined = others[:insert_position] + [name_part] + others[insert_position:]
    
    return ''.join(parts_combined)
