#!/usr/bin/env python3
"""
Password Migration Script
This script converts plain text passwords to hashed passwords in users.json
Run this once before deploying the updated application.
"""

import json
import os
from werkzeug.security import generate_password_hash

def migrate_passwords():
    users_file = "users.json"
    backup_file = "users.json.backup"
    
    if not os.path.exists(users_file):
        print("No users.json file found. Nothing to migrate.")
        return
    
    # Create backup
    if os.path.exists(backup_file):
        print("Backup file already exists. Remove it first if you want to re-run migration.")
        return
    
    with open(users_file, 'r') as f:
        data = json.load(f)
    
    # Create backup
    with open(backup_file, 'w') as f:
        json.dump(data, f, indent=4)
    print(f"Created backup: {backup_file}")
    
    # Convert format and hash passwords
    users_list = []
    
    if isinstance(data, dict):  # Old format: {"username": {"password": "...", ...}}
        for username, user_data in data.items():
            password = user_data.get('password', '')
            # Check if password is already hashed (starts with hash method prefix)
            if not password.startswith(('pbkdf2:', 'scrypt:', 'bcrypt')):
                hashed_password = generate_password_hash(password)
                print(f"Hashing password for user: {username}")
            else:
                hashed_password = password
                print(f"Password already hashed for user: {username}")
            
            users_list.append({
                'username': username,
                'password': hashed_password,
                'balance': user_data.get('balance', 1000),
                'is_admin': user_data.get('is_admin', False)
            })
    
    elif isinstance(data, list):  # New format: [{"username": "...", "password": "...", ...}]
        for user in data:
            password = user.get('password', '')
            if not password.startswith(('pbkdf2:', 'scrypt:', 'bcrypt')):
                hashed_password = generate_password_hash(password)
                print(f"Hashing password for user: {user.get('username', 'unknown')}")
            else:
                hashed_password = password
                print(f"Password already hashed for user: {user.get('username', 'unknown')}")
            
            user['password'] = hashed_password
            user.setdefault('is_admin', False)
        users_list = data
    
    # Save updated data
    with open(users_file, 'w') as f:
        json.dump(users_list, f, indent=4)
    
    print(f"Migration completed. Updated {len(users_list)} users.")
    print("Original file backed up as users.json.backup")

if __name__ == "__main__":
    migrate_passwords() 