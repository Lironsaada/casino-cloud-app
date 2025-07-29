from flask import Flask, render_template, request, redirect, url_for, session, flash, Response
import random
import json
import os
import time
import functools
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
app = Flask(__name__)
# Use environment variable for secret key, fallback to a secure default
app.secret_key = os.environ.get('SECRET_KEY', 'your-secret-key-change-this-in-production')

# Use environment variable for admin password - never hardcode passwords!
ADMIN_PASS = os.environ.get('ADMIN_PASSWORD', 'change-this-default-password-immediately')

# Prometheus metrics
REQUEST_COUNT = Counter('casino_requests_total', 'Total casino requests', ['method', 'endpoint', 'status'])
REQUEST_DURATION = Histogram('casino_request_duration_seconds', 'Casino request duration')
ACTIVE_USERS = Gauge('casino_active_users', 'Number of active users')
GAMES_PLAYED = Counter('casino_games_played_total', 'Total games played', ['game_type', 'result'])
USER_BALANCE = Gauge('casino_user_balance', 'User balance', ['username'])

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

# Metrics tracking decorator
import time
import functools

def track_metrics(f):
    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        start_time = time.time()
        try:
            response = f(*args, **kwargs)
            status = getattr(response, 'status_code', 200) if hasattr(response, 'status_code') else 200
            REQUEST_COUNT.labels(method=request.method, endpoint=request.endpoint, status=status).inc()
            return response
        except Exception as e:
            status = 500
            REQUEST_COUNT.labels(method=request.method, endpoint=request.endpoint, status=status).inc()
            raise
        finally:
            REQUEST_DURATION.observe(time.time() - start_time)
    return decorated_function

def current_user():
    if "username" in session:
        user = next((u for u in users if u["username"] == session["username"]), None)
        if user:
            # Update last active timestamp
            user["last_active"] = time.time()
        return user
    return None

def require_login():
    if "username" not in session:
        return redirect(url_for("login"))

@app.route("/", methods=["GET", "POST"])
@track_metrics
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
        
        # Update last active timestamp
        user["last_active"] = time.time()
        save_users()
        
        session["username"] = username
        session["is_admin"] = user["is_admin"]
        return redirect(url_for("menu"))
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

@app.route("/menu")
@track_metrics
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
        to_username = request.form.get("username", "").strip()
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
        
        # Log the transactions
        log_transaction(user["username"], "tip_sent", -amount, f"Tip sent to {to_username}", "sent")
        log_transaction(to_user["username"], "tip_received", amount, f"Tip received from {user['username']}", "received")
        
        flash(f"Tipped {amount} coins to {to_username}")
        return redirect(url_for("menu"))
    return render_template("tip.html", balance=user["balance"])

@app.route("/admin_auth", methods=["GET", "POST"])
def admin_auth():
    if request.method == "POST":
        password = request.form.get("password")
        if password == ADMIN_PASS:
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
        amount_str = request.form.get("amount", "0")
        
        # Debug logging
        print(f"DEBUG Admin Form Data: username={username}, action={action}, amount={amount_str}")
        print(f"DEBUG Form keys: {list(request.form.keys())}")
        
        try:
            amount = int(amount_str)
        except ValueError:
            flash("Invalid amount provided.", "error")
            return redirect(url_for("admin"))
        
        user = next((u for u in users if u["username"] == username), None)

        if not user:
            flash(f"User '{username}' not found.", "error")
            return redirect(url_for("admin"))
            
        if not action:
            flash("No action specified.", "error")
            return redirect(url_for("admin"))
            
        old_balance = user["balance"]
        print(f"DEBUG: User {username} old balance: {old_balance}")
        
        if action == "add":
            user["balance"] += amount
            log_transaction(username, "admin_add", amount, f"Admin added {amount} coins")
            flash(f"✅ Successfully added {amount:,} coins to {username}'s balance. New balance: {user['balance']:,}", "success")
        elif action == "subtract":
            if user["balance"] < amount:
                flash(f"⚠️ Cannot subtract {amount:,} coins. {username} only has {user['balance']:,} coins.", "warning")
                return redirect(url_for("admin"))
            user["balance"] -= amount
            log_transaction(username, "admin_subtract", -amount, f"Admin subtracted {amount} coins")
            flash(f"✅ Successfully removed {amount:,} coins from {username}'s balance. New balance: {user['balance']:,}", "success")
        elif action == "set":
            if amount < 0:
                flash("Balance cannot be negative.", "error")
                return redirect(url_for("admin"))
            user["balance"] = amount
            balance_change = amount - old_balance
            log_transaction(username, "admin_set", balance_change, f"Admin set balance to {amount} coins")
            flash(f"✅ Successfully set {username}'s balance to {amount:,} coins.", "success")
        else:
            flash(f"Unknown action: {action}", "error")
            return redirect(url_for("admin"))
            
        print(f"DEBUG: User {username} new balance: {user['balance']}")
        save_users()
        print("DEBUG: Users saved successfully")
        return redirect(url_for("admin"))

    return render_template("admin.html", users=users)

@app.route("/admin_logout")
def admin_logout():
    session.pop("admin_authenticated", None)
    flash("Admin session ended.", "info")
    return redirect(url_for("menu"))

@app.route("/metrics")
def metrics():
    # Update active users gauge
    ACTIVE_USERS.set(len([u for u in users if u.get('last_active', 0) > time.time() - 3600]))
    
    # Update user balance metrics
    for user in users:
        USER_BALANCE.labels(username=user['username']).set(user['balance'])
    
    return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)

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
@track_metrics
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
        dealer_hand = bj["dealer_hand"]
        
        # Handle split vs normal hands
        is_split = "is_split" in bj and bj["is_split"]
        if is_split:
            # Always get a fresh copy of the current hand to avoid reference issues
            player_hand = bj["player_hands"][bj["current_hand"]].copy()
            print(f"DEBUG: Loading hand {bj['current_hand']}: {player_hand}")
            print(f"DEBUG: All hands in session: {bj['player_hands']}")
        else:
            player_hand = bj["player_hand"]

        if request.method == "POST":
            action = request.form.get("action")
            if action == "hit":
                new_card = deck.pop()
                player_hand.append(new_card)
                player_val = hand_value(player_hand)
                
                # Debug logging for hits
                if is_split:
                    print(f"DEBUG: Hit - Current hand {bj['current_hand']}: added {new_card}")
                    print(f"DEBUG: Hit - Hand after hit: {player_hand}")
                    print(f"DEBUG: Hit - All hands: {bj['player_hands']}")
                else:
                    print(f"DEBUG: Hit - Single hand: added {new_card}, hand: {player_hand}")
                if player_val > 21:
                    # Handle bust for split hands
                    if is_split:
                        bj["player_hands"][bj["current_hand"]] = player_hand.copy()
                        print(f"DEBUG: Bust - Hand {bj['current_hand']} busted with: {player_hand}")
                        print(f"DEBUG: Bust - All hands before transition: {bj['player_hands']}")
                        # Move to next hand or finish
                        if bj["current_hand"] < len(bj["player_hands"]) - 1:
                            bj["current_hand"] += 1
                            print(f"DEBUG: Bust - Moved to hand {bj['current_hand']}")
                            # Update session immediately and redirect to reload the new hand
                            bj["deck"] = deck
                            session["blackjack"] = bj
                            return redirect(url_for("blackjack_bet"))
                        else:
                            bj["state"] = "dealer_turn"
                    else:
                        bj["state"] = "finished"  # Bust - automatic loss
                elif player_val == 21:
                    # Handle 21 for split hands
                    if is_split:
                        bj["player_hands"][bj["current_hand"]] = player_hand.copy()
                        print(f"DEBUG: 21 - Hand {bj['current_hand']} got 21 with: {player_hand}")
                        # Move to next hand or go to dealer turn
                        if bj["current_hand"] < len(bj["player_hands"]) - 1:
                            bj["current_hand"] += 1
                            print(f"DEBUG: 21 - Moved to hand {bj['current_hand']}")
                            # Update session immediately and redirect to reload the new hand
                            bj["deck"] = deck
                            session["blackjack"] = bj
                            return redirect(url_for("blackjack_bet"))
                        else:
                            bj["state"] = "dealer_turn"
                    else:
                        bj["state"] = "dealer_turn"  # 21 - go to dealer turn
            elif action == "stand":
                if is_split:
                    bj["player_hands"][bj["current_hand"]] = player_hand.copy()
                    print(f"DEBUG: Stand - Hand {bj['current_hand']} stood with: {player_hand}")
                    # Move to next hand or go to dealer turn
                    if bj["current_hand"] < len(bj["player_hands"]) - 1:
                        bj["current_hand"] += 1
                        print(f"DEBUG: Stand - Moved to hand {bj['current_hand']}")
                        # Update session immediately and redirect to reload the new hand
                        bj["deck"] = deck
                        session["blackjack"] = bj
                        return redirect(url_for("blackjack_bet"))
                    else:
                        bj["state"] = "dealer_turn"
                else:
                    bj["state"] = "dealer_turn"
            elif action == "double":
                # Double down: double the bet, take one card, then stand
                current_bet = bj["split_bets"][bj["current_hand"]] if is_split else bj["bet"]
                if len(player_hand) == 2 and user["balance"] >= current_bet:
                    user["balance"] -= current_bet  # Deduct additional bet
                    if is_split:
                        bj["split_bets"][bj["current_hand"]] *= 2  # Double the bet for this hand
                    else:
                        bj["bet"] *= 2  # Double the bet
                    bj["balance"] = user["balance"]  # Update balance in session
                    player_hand.append(deck.pop())  # Take exactly one card
                    player_val = hand_value(player_hand)
                    
                    if is_split:
                        bj["player_hands"][bj["current_hand"]] = player_hand.copy()
                        print(f"DEBUG: Double - Hand {bj['current_hand']} doubled with: {player_hand}")
                        # Move to next hand or go to dealer turn
                        if bj["current_hand"] < len(bj["player_hands"]) - 1:
                            bj["current_hand"] += 1
                            print(f"DEBUG: Double - Moved to hand {bj['current_hand']}")
                            # Update session immediately and redirect to reload the new hand
                            bj["deck"] = deck
                            session["blackjack"] = bj
                            return redirect(url_for("blackjack_bet"))
                        else:
                            bj["state"] = "dealer_turn"
                    else:
                        if player_val > 21:
                            bj["state"] = "finished"  # Bust after double down
                        else:
                            bj["state"] = "dealer_turn"  # Go to dealer turn regardless of value
                    save_users()  # Save the balance change immediately
            elif action == "split":
                # Split: split pair into two hands, requires additional bet
                if (not is_split and len(player_hand) == 2 and player_hand[0][:-1] == player_hand[1][:-1] 
                    and user["balance"] >= bj["bet"]):
                    user["balance"] -= bj["bet"]  # Deduct additional bet for second hand
                    bj["balance"] = user["balance"]  # Update balance in session
                    
                    # Create two hands from the split
                    # Ensure deck has enough cards and is properly shuffled
                    if len(deck) < 10:  # Reshuffle if running low
                        deck = create_deck()
                        random.shuffle(deck)
                    
                    # Deal cards for split hands
                    first_new_card = deck.pop()
                    second_new_card = deck.pop()
                    
                    first_hand = [player_hand[0], first_new_card]  # First original card + new card
                    second_hand = [player_hand[1], second_new_card]  # Second original card + new card
                    
                    # Debug logging
                    print(f"DEBUG: Split - Original cards: {player_hand[0]}, {player_hand[1]}")
                    print(f"DEBUG: Split - New cards: {first_new_card}, {second_new_card}")
                    print(f"DEBUG: Split - First hand: {first_hand}")
                    print(f"DEBUG: Split - Second hand: {second_hand}")
                    print(f"DEBUG: Split - Deck remaining: {len(deck)}")
                    
                    # Store split hands in session (ensure they're independent lists)
                    bj["player_hands"] = [first_hand.copy(), second_hand.copy()]  # Array of hands
                    bj["current_hand"] = 0  # Which hand we're playing (0 or 1)
                    bj["split_bets"] = [bj["bet"], bj["bet"]]  # Bet for each hand
                    bj["is_split"] = True
                    
                    # Remove the original single hand
                    del bj["player_hand"]
                    
                    save_users()  # Save the balance change immediately

            # Update the appropriate hand (only if we haven't already returned)
            if is_split:
                bj["player_hands"][bj["current_hand"]] = player_hand.copy()  # Ensure we store a copy
                print(f"DEBUG: Updated hand {bj['current_hand']} to: {bj['player_hands'][bj['current_hand']]}")
                print(f"DEBUG: All hands after update: {bj['player_hands']}")
            else:
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
            template_vars = {
                "dealer_hand": dealer_hand,
                "dealer_value": hand_value(dealer_hand),
                "balance": bj["balance"],
                "bj": bj,
                "bj_state": bj["state"]
            }
            
            # Handle split vs normal hands for template
            if is_split:
                hand_values = [hand_value(hand) for hand in bj["player_hands"]]
                template_vars.update({
                    "player_hands": bj["player_hands"],
                    "current_hand": bj["current_hand"],
                    "player_hand": bj["player_hands"][bj["current_hand"]],  # Current active hand
                    "player_value": hand_value(bj["player_hands"][bj["current_hand"]]),
                    "hand_values": hand_values,
                    "is_split": True,
                    "split_bets": bj["split_bets"]
                })
            else:
                template_vars.update({
                    "player_hand": player_hand,
                    "player_value": hand_value(player_hand),
                    "is_split": False
                })
            
            return render_template("blackjack_play.html", **template_vars)

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
        dealer_hand = bj["dealer_hand"]
        dealer_val = hand_value(dealer_hand)
        balance = bj["balance"]
        
        # Handle split vs normal hands
        is_split = "is_split" in bj and bj["is_split"]
        
        if is_split:
            # Handle split hands
            results = []
            total_winnings = 0
            
            for i, hand in enumerate(bj["player_hands"]):
                hand_val = hand_value(hand)
                bet = bj["split_bets"][i]
                hand_result = ""
                hand_winnings = 0
                
                # Check for natural blackjack (21 with first 2 cards)
                player_blackjack = len(hand) == 2 and hand_val == 21
                dealer_blackjack = len(dealer_hand) == 2 and dealer_val == 21
                
                if hand_val > 21:
                    hand_result = f"Hand {i+1}: Busted! Lost {bet} coins."
                    hand_winnings = 0
                elif player_blackjack and dealer_blackjack:
                    hand_result = f"Hand {i+1}: Both have blackjack! Push - {bet} coins returned."
                    hand_winnings = bet
                elif player_blackjack and not dealer_blackjack:
                    hand_result = f"Hand {i+1}: Blackjack! Won {int(bet * 2.5)} coins."
                    hand_winnings = int(bet * 2.5)  # 3:2 payout for blackjack
                elif dealer_val > 21:
                    hand_result = f"Hand {i+1}: Dealer busted! Won {bet * 2} coins."
                    hand_winnings = bet * 2
                elif hand_val > dealer_val:
                    hand_result = f"Hand {i+1}: Won {bet * 2} coins."
                    hand_winnings = bet * 2
                elif hand_val == dealer_val:
                    hand_result = f"Hand {i+1}: Push - {bet} coins returned."
                    hand_winnings = bet
                else:
                    hand_result = f"Hand {i+1}: Lost {bet} coins."
                    hand_winnings = 0
                
                results.append(hand_result)
                total_winnings += hand_winnings
            
            result = " | ".join(results)
            winnings = total_winnings
        else:
            # Handle single hand (original logic)
            player_hand = bj["player_hand"]
            bet = bj["bet"]
            
            player_val = hand_value(player_hand)
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
        
        # Log the transaction
        if is_split:
            total_bet = sum(bj["split_bets"])
            transaction_result = "won" if winnings > total_bet else "lost" if winnings == 0 else "push"
            net_amount = winnings - total_bet  # Net gain/loss
            details = f"Blackjack split bet: {total_bet} coins (2 hands)"
        else:
            transaction_result = "won" if winnings > bet else "lost" if winnings == 0 else "push"
            net_amount = winnings - bet  # Net gain/loss
            details = f"Blackjack bet: {bet} coins"
            if player_blackjack and not dealer_blackjack:
                details += " (Natural Blackjack)"
        log_transaction(user["username"], "blackjack", net_amount, details, transaction_result)
        
        # Track game metrics
        GAMES_PLAYED.labels(game_type="blackjack", result=transaction_result).inc()
        
        session.pop("blackjack")  # Clear game session

        # Prepare template variables for result page
        result_vars = {
            "dealer_hand": dealer_hand,
            "dealer_val": dealer_val,
            "result": result,
            "balance": user["balance"],
            "is_split": is_split
        }
        
        if is_split:
            result_vars.update({
                "player_hands": bj["player_hands"],
                "hand_values": [hand_value(hand) for hand in bj["player_hands"]],
                "split_bets": bj["split_bets"]
            })
        else:
            result_vars.update({
                "player_hand": player_hand,
                "player_val": player_val
            })
        
        return render_template("blackjack_result.html", **result_vars)

#########################
# Roulette implementation
#########################

@app.route("/roulette", methods=["GET", "POST"])
@track_metrics
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
        transaction_result = "won" if win else "lost"
        net_amount = winnings - bet_amount if win else -bet_amount
        log_transaction(user["username"], "roulette", net_amount, 
                       f"Roulette bet on {bet_color}: {bet_amount} coins", transaction_result)
        
        # Track game metrics
        GAMES_PLAYED.labels(game_type="roulette", result=transaction_result).inc()

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
@track_metrics
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
            # Enhanced validation
            if bet_amount <= 0:
                error_msg = "Bet amount must be positive"
            elif bet_amount > user["balance"]:
                error_msg = "Insufficient balance"
            elif bet_amount > 10000:  # Maximum bet limit
                error_msg = "Bet amount exceeds maximum limit of 10,000"
            else:
                error_msg = None
                
            if error_msg:
                if request.is_json:
                    return {"error": error_msg}, 400
                flash(error_msg)
                return render_template("slots.html", balance=user["balance"])
        except (ValueError, TypeError):
            error_msg = "Invalid bet amount format"
            if request.is_json:
                return {"error": error_msg}, 400
            flash(error_msg)
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
        transaction_result = "won" if win else "lost"
        net_amount = winnings - bet_amount if win else -bet_amount
        log_transaction(user["username"], "slots", net_amount, 
                       f"Slots bet: {bet_amount} coins", transaction_result)
        
        # Track game metrics
        GAMES_PLAYED.labels(game_type="slots", result=transaction_result).inc()

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

