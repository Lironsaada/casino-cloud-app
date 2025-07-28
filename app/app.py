from flask import Flask, render_template, request, redirect, url_for, session, flash
import random
import json
import os
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
# Use environment variable for secret key, fallback to a secure default
app.secret_key = os.environ.get('SECRET_KEY', 'your-secret-key-change-this-in-production')

USERS_FILE = "users.json"
BALANCE_HISTORY_FILE = "balance_history.json"

# Load users from JSON file
def load_users():
    if os.path.exists(USERS_FILE):
        try:
            with open(USERS_FILE, "r") as f:
                data = json.load(f)
                users_list = []
                if isinstance(data, dict):  # Handle old format
                    users_list = [{"username": k, **v} for k, v in data.items()]
                elif isinstance(data, list):
                    users_list = data

                # Ensure all users have an 'is_admin' key
                for user in users_list:
                    user.setdefault("is_admin", False)
                
                return users_list
        except (json.JSONDecodeError, AttributeError):
            return []
    return []

# Save users to JSON file
def save_users():
    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=4)

def load_balance_history():
    if os.path.exists(BALANCE_HISTORY_FILE):
        try:
            with open(BALANCE_HISTORY_FILE, "r") as f:
                return json.load(f)
        except json.JSONDecodeError:
            return {}
    return {}

def save_balance_history():
    with open(BALANCE_HISTORY_FILE, "w") as f:
        json.dump(balance_history, f, indent=4)

def log_transaction(username, transaction_type, amount, details, result=None):
    if username not in balance_history:
        balance_history[username] = []
    
    user = next((u for u in users if u["username"] == username), None)
    balance_after = user['balance'] if user else 'N/A'

    balance_history[username].append({
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "type": transaction_type,
        "details": details,
        "amount": amount,
        "result": result,
        "balance_after": balance_after
    })
    save_balance_history()

users = load_users()
balance_history = load_balance_history()

def current_user():
    if "username" in session:
        return next((u for u in users if u["username"] == session["username"]), None)
    return None

def require_login():
    if "username" not in session:
        return redirect(url_for("login"))

@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"]
        
        user = next((u for u in users if u["username"] == username), None)

        if user:
            if not check_password_hash(user["password"], password):
                flash("Incorrect password")
                return redirect(url_for("login"))
        else:
            # Register new user with 1000 coins
            user = {"username": username, "password": generate_password_hash(password), "balance": 1000, "is_admin": False}
            users.append(user)
            save_users()
            flash(f"Account created for {username} with 1000 coins")
        
        session["username"] = username
        session["is_admin"] = user["is_admin"]
        return redirect(url_for("menu"))
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

@app.route("/menu")
def menu():
    if not current_user():
        return redirect(url_for("login"))
    return render_template("menu.html", balance=current_user()["balance"], username=session["username"])

@app.route("/balance")
def check_balance():
    user = current_user()
    if not user:
        return redirect(url_for("login"))
    return render_template("balance.html", balance=user["balance"])

@app.route("/tip", methods=["GET", "POST"])
def tip():
    user = current_user()
    if not user:
        return redirect(url_for("login"))

    if request.method == "POST":
        to_username = request.form.get("to_user", "").strip()
        amount = request.form.get("amount", "0").strip()
        
        to_user = next((u for u in users if u["username"] == to_username), None)

        if not to_user:
            flash("User does not exist")
            return redirect(url_for("tip"))
        try:
            amount = int(amount)
            if amount <= 0:
                raise ValueError()
        except ValueError:
            flash("Invalid amount")
            return redirect(url_for("tip"))
        if amount > user["balance"]:
            flash("Insufficient balance")
            return redirect(url_for("tip"))
        if to_username == session["username"]:
            flash("Cannot tip yourself")
            return redirect(url_for("tip"))
        # Transfer coins
        user["balance"] -= amount
        to_user["balance"] += amount
        save_users()
        flash(f"Tipped {amount} coins to {to_username}")
        return redirect(url_for("menu"))
    return render_template("tip.html")

@app.route("/admin_auth", methods=["GET", "POST"])
def admin_auth():
    if request.method == "POST":
        password = request.form.get("password")
        if password == "admin":
            session["admin_authenticated"] = True
            flash("Admin access granted!", "success")
            return redirect(url_for("admin"))
        else:
            flash("Invalid admin password!", "error")
    
    return render_template("admin_auth.html")

@app.route("/admin", methods=["GET", "POST"])
def admin():
    # Check if user is authenticated as admin
    if not session.get("admin_authenticated"):
        return redirect(url_for("admin_auth"))

    if request.method == "POST":
        username = request.form.get("username")
        action = request.form.get("action")
        amount = int(request.form.get("amount", 0))
        
        user = next((u for u in users if u["username"] == username), None)

        if user:
            old_balance = user["balance"]
            if action == "add":
                user["balance"] += amount
                log_transaction(username, "admin_add", amount, f"Admin added {amount} coins")
                flash(f"Successfully added {amount} coins to {username}'s balance.")
            elif action == "subtract":
                user["balance"] -= amount
                log_transaction(username, "admin_subtract", -amount, f"Admin subtracted {amount} coins")
                flash(f"Successfully removed {amount} coins from {username}'s balance.")
            elif action == "set":
                user["balance"] = amount
                balance_change = amount - old_balance
                log_transaction(username, "admin_set", balance_change, f"Admin set balance to {amount} coins")
                flash(f"Successfully set {username}'s balance to {amount} coins.")
            save_users()
        else:
            flash("User not found.")
        return redirect(url_for("admin"))

    return render_template("admin.html", users=users)

@app.route("/admin_logout")
def admin_logout():
    session.pop("admin_authenticated", None)
    flash("Admin session ended.", "info")
    return redirect(url_for("menu"))

##############################
# Blackjack helper functions #
##############################

suits = ['♠', '♥', '♦', '♣']
values = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']

def create_deck():
    return [v + s for s in suits for v in values]

def card_value(card):
    val = card[:-1]
    if val in ['J', 'Q', 'K']:
        return 10
    if val == 'A':
        return 11
    return int(val)

def hand_value(hand):
    total = 0
    aces = 0
    for card in hand:
        v = card_value(card)
        total += v
        if card[:-1] == 'A':
            aces += 1
    while total > 21 and aces:
        total -= 10
        aces -= 1
    return total

@app.route("/blackjack_bet", methods=["GET", "POST"])
def blackjack_bet():
    user = current_user()
    if not user:
        return redirect(url_for("login"))

    if "blackjack" not in session:
        # Start a new game
        deck = create_deck()
        random.shuffle(deck)
        session["blackjack"] = {
            "deck": deck,
            "player_hand": [deck.pop(), deck.pop()],
            "dealer_hand": [deck.pop(), deck.pop()],
            "bet": 0,
            "balance": user["balance"],
            "state": "betting",  # betting, playing, dealer_turn, finished
        }
        return render_template("blackjack_bet.html", balance=user["balance"])

    bj = session["blackjack"]

    if bj["state"] == "betting":
        if request.method == "POST":
            bet = request.form.get("bet", "0")
            try:
                bet = int(bet)
                if bet <= 0 or bet > user["balance"]:
                    flash("Invalid bet amount")
                    return render_template("blackjack_bet.html", balance=user["balance"])
            except ValueError:
                flash("Invalid bet amount")
                return render_template("blackjack_bet.html", balance=user["balance"])

            bj["bet"] = bet
            bj["balance"] = user["balance"] - bet
            bj["state"] = "playing"
            session["blackjack"] = bj
            return redirect(url_for("blackjack_bet"))
        return render_template("blackjack_bet.html", balance=user["balance"])

    if bj["state"] == "playing":
        deck = bj["deck"]
        player_hand = bj["player_hand"]
        dealer_hand = bj["dealer_hand"]

        if request.method == "POST":
            action = request.form.get("action")
            if action == "hit":
                player_hand.append(deck.pop())
                player_val = hand_value(player_hand)
                if player_val > 21:
                    bj["state"] = "finished"  # Bust - automatic loss
                elif player_val == 21:
                    bj["state"] = "dealer_turn"  # 21 - go to dealer turn
            elif action == "stand":
                bj["state"] = "dealer_turn"
            elif action == "double":
                # Double down: double the bet, take one card, then stand
                if len(player_hand) == 2 and user["balance"] >= bj["bet"]:
                    user["balance"] -= bj["bet"]  # Deduct additional bet
                    bj["bet"] *= 2  # Double the bet
                    bj["balance"] = user["balance"]  # Update balance in session
                    player_hand.append(deck.pop())  # Take exactly one card
                    player_val = hand_value(player_hand)
                    if player_val > 21:
                        bj["state"] = "finished"  # Bust after double down
                    else:
                        bj["state"] = "dealer_turn"  # Go to dealer turn regardless of value
                    save_users()  # Save the balance change immediately

            bj["player_hand"] = player_hand
            bj["deck"] = deck
            session["blackjack"] = bj
            return redirect(url_for("blackjack_bet"))
        else:
            # Check for natural blackjack (21 with first 2 cards)
            player_val = hand_value(player_hand)
            dealer_val = hand_value(dealer_hand)
            
            # If player has natural blackjack and dealer doesn't show ace or 10
            if len(player_hand) == 2 and player_val == 21:
                if len(dealer_hand) == 2 and hand_value(dealer_hand) == 21:
                    # Both have blackjack - push
                    bj["state"] = "finished"
                    session["blackjack"] = bj
                    return redirect(url_for("blackjack_bet"))
                else:
                    # Player has blackjack, dealer doesn't
                    bj["state"] = "finished"
                    session["blackjack"] = bj
                    return redirect(url_for("blackjack_bet"))
            
            # GET request: render game state page
            return render_template("blackjack_play.html",
                                   player_hand=player_hand,
                                   dealer_hand=dealer_hand,
                                   dealer_value=hand_value(dealer_hand),
                                   player_value=hand_value(player_hand),
                                   balance=bj["balance"],
                                   bj=bj,
                                   bj_state=bj["state"])

    if bj["state"] == "dealer_turn":
        deck = bj["deck"]
        dealer_hand = bj["dealer_hand"]

        while hand_value(dealer_hand) < 17:
            dealer_hand.append(deck.pop())

        bj["dealer_hand"] = dealer_hand
        bj["state"] = "finished"
        session["blackjack"] = bj
        return redirect(url_for("blackjack_bet"))

    if bj["state"] == "finished":
        player_hand = bj["player_hand"]
        dealer_hand = bj["dealer_hand"]
        bet = bj["bet"]
        balance = bj["balance"]

        player_val = hand_value(player_hand)
        dealer_val = hand_value(dealer_hand)
        result = ""
        winnings = 0

        # Check for natural blackjack (21 with first 2 cards)
        player_blackjack = len(player_hand) == 2 and player_val == 21
        dealer_blackjack = len(dealer_hand) == 2 and dealer_val == 21

        if player_val > 21:
            result = "You busted! You lose."
            winnings = 0
        elif player_blackjack and dealer_blackjack:
            result = "Both have blackjack! Push - your bet is returned."
            winnings = bet
        elif player_blackjack and not dealer_blackjack:
            result = f"Blackjack! You won {int(bet * 2.5)} coins."
            winnings = int(bet * 2.5)  # 3:2 payout for blackjack
        elif dealer_val > 21:
            result = f"Dealer busted! You win {bet * 2} coins."
            winnings = bet * 2
        elif player_val > dealer_val:
            result = f"You win! You won {bet * 2} coins."
            winnings = bet * 2
        elif player_val == dealer_val:
            result = "Push. Your bet is returned."
            winnings = bet
        else:
            result = "You lose."
            winnings = 0

        user["balance"] = balance + winnings
        save_users()
        session.pop("blackjack")  # Clear game session

        return render_template("blackjack_result.html",
                               player_hand=player_hand,
                               dealer_hand=dealer_hand,
                               player_val=player_val,
                               dealer_val=dealer_val,
                               result=result,
                               balance=user["balance"])

#########################
# Roulette implementation
#########################

@app.route("/roulette", methods=["GET", "POST"])
def roulette():
    user = current_user()
    if not user:
        return redirect(url_for("login"))

    colors = ['red', 'black', 'green']
    wheel = ['red', 'black', 'red', 'black', 'red', 'black', 'red',
             'green', 'black', 'red', 'black', 'red', 'black', 'red', 'black']

    if request.method == "POST":
        # Handle both JSON (AJAX) and form data
        if request.is_json:
            data = request.get_json()
            bet_color = data.get("color")
            bet_amount = data.get("bet", "0")
        else:
            bet_color = request.form.get("color")
            bet_amount = request.form.get("bet", "0")

        try:
            bet_amount = int(bet_amount)
            if bet_amount <= 0 or bet_amount > user["balance"]:
                if request.is_json:
                    return {"error": "Invalid bet amount"}, 400
                flash("Invalid bet amount")
                return render_template("roulette.html", balance=user["balance"])
        except (ValueError, TypeError):
            if request.is_json:
                return {"error": "Invalid bet amount"}, 400
            flash("Invalid bet amount")
            return render_template("roulette.html", balance=user["balance"])

        if bet_color not in colors:
            if request.is_json:
                return {"error": "Invalid color choice"}, 400
            flash("Invalid color choice")
            return render_template("roulette.html", balance=user["balance"])

        user["balance"] -= bet_amount

        # Spin wheel
        winning_color = random.choice(wheel)

        # Determine winnings
        win = False
        if bet_color == winning_color:
            if winning_color == "green":
                multiplier = 14
            else:
                multiplier = 2
            winnings = bet_amount * multiplier
            user["balance"] += winnings
            result = f"You won {winnings} coins! The ball landed on {winning_color}."
            win = True
        else:
            result = f"You lost. The ball landed on {winning_color}."

        save_users()
        
        # Log the transaction
        log_transaction(user["username"], "roulette", -bet_amount if not win else winnings - bet_amount, 
                       f"Roulette bet on {bet_color}, landed on {winning_color}", result)

        # Return JSON for AJAX requests
        if request.is_json:
            return {
                "message": result,
                "result_color": winning_color,
                "balance": user["balance"],
                "win": win
            }

        return render_template("roulette_result.html", result=result, balance=user["balance"])

    return render_template("roulette.html", balance=user["balance"])

#########################
# Slot Machine implementation
#########################

@app.route("/slots", methods=["GET", "POST"])
def slots():
    user = current_user()
    if not user:
        return redirect(url_for("login"))

    symbols = ["🍒", "🔔", "🍋", "⭐", "💎", "7️⃣"]

    if request.method == "POST":
        # Handle both JSON (AJAX) and form data
        if request.is_json:
            data = request.get_json()
            bet_amount = data.get("bet", "0")
        else:
            bet_amount = request.form.get("bet", "0")
            
        try:
            bet_amount = int(bet_amount)
            if bet_amount <= 0 or bet_amount > user["balance"]:
                if request.is_json:
                    return {"error": "Invalid bet amount"}, 400
                flash("Invalid bet amount")
                return render_template("slots.html", balance=user["balance"])
        except (ValueError, TypeError):
            if request.is_json:
                return {"error": "Invalid bet amount"}, 400
            flash("Invalid bet amount")
            return render_template("slots.html", balance=user["balance"])

        user["balance"] -= bet_amount

        # Spin reels
        a = random.choice(symbols)
        b = random.choice(symbols)
        c = random.choice(symbols)

        win = False
        winnings = 0
        message = ""

        if a == b == c:
            multipliers = {"🍒": 3, "🔔": 5, "🍋": 2, "⭐": 10, "💎": 15, "7️⃣": 25}
            winnings = bet_amount * multipliers.get(a, 0)
            win = True
            message = f"Jackpot! Three {a}! You won {winnings} coins."
        elif a == b or b == c or a == c:
            multipliers = {"🍒": 2, "🔔": 2, "🍋": 1, "⭐": 3, "💎": 5, "7️⃣": 10}
            # Use the most common symbol in two matches
            matched_symbol = a if a == b else b if b == c else a
            winnings = bet_amount * multipliers.get(matched_symbol, 0)
            win = True
            message = f"Nice! Two {matched_symbol}! You won {winnings} coins."
        else:
            message = f"No match. You lost {bet_amount} coins."

        if win:
            user["balance"] += winnings

        save_users()
        
        # Log the transaction
        log_transaction(user["username"], "slots", -bet_amount if not win else winnings - bet_amount, 
                       f"Slots game: {a} {b} {c}", message)

        # Return JSON for AJAX requests
        if request.is_json:
            return {
                "message": message,
                "reels": [a, b, c],
                "balance": user["balance"],
                "win": win
            }

        return render_template("slots.html", 
                             balance=user["balance"], 
                             result=message, 
                             win=win,
                             reels=[a, b, c])

    return render_template("slots.html", balance=user["balance"])

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)

