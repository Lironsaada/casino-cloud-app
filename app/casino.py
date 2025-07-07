import os
import getpass
import json

USERS_DIR = ".users"
ADMIN_PASS = "Liron1136"

# Make sure the user data directory exists
os.makedirs(USERS_DIR, exist_ok=True)

def get_user_file(username):
    return os.path.join(USERS_DIR, f".{username}.json")

def login():
    print("Welcome to the Casino! Please log in.")
    username = input("Enter your username: ").strip()
    password = getpass.getpass("Enter your password: ")

    user_file = get_user_file(username)

    if os.path.isfile(user_file):
        with open(user_file, "r") as f:
            user_data = json.load(f)
        if user_data["password"] != password:
            print("Incorrect password.")
            exit(1)
        else:
            print("Login successful.")
            return username, user_data
    else:
        # Create new user with 1000 coins balance
        user_data = {"password": password, "balance": 1000}
        with open(user_file, "w") as f:
            json.dump(user_data, f)
        print("Account created with 1000 coins.")
        return username, user_data

def save_balance(username, user_data):
    user_file = get_user_file(username)
    with open(user_file, "w") as f:
        json.dump(user_data, f)

def main():
    username, user_data = login()
    print(f"Your balance is {user_data['balance']} coins")
    
    # Example: deduct 100 coins and save
    user_data['balance'] -= 100
    save_balance(username, user_data)
    print(f"After deducting 100 coins, your balance is {user_data['balance']} coins")

if __name__ == "__main__":
    main()
