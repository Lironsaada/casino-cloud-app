from flask import Flask, render_template, request, redirect, url_for, session, flash
import random
import json
import os

app = Flask(__name__)
app.secret_key = "your_secret_key_here"  # Change this to a secure secret key

USERS_FILE = "/data/users.json"
ADMIN_PASS = "12345"

# Load or create users data
if os.path.exists(USERS_FILE):
    with open(USERS_FILE, "r") as f:
        users = json.load(f)
else:
    users = {}

def save_users():
    with open(USERS_FILE, "w") as f:
        json.dump(users, f)

def current_user():
    username = session.get("username")
    if username:
        return users.get(username)
    return None

def require_login():
    if "username" not in session:
        return redirect(url_for("login"))

@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"]
        if username in users:
            if users[username]["password"] != password:
                flash("Incorrect password")
                return redirect(url_for("login"))
        else:
            # Register new user with 1000 coins
            users[username] = {"password": password, "balance": 1000}
            save_users()
            flash(f"Account created for {username} with 1000 coins")
        session["username"] = username
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
        to_user = request.form.get("to_user", "").strip()
        amount = request.form.get("amount", "0").strip()
        if to_user not in users:
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
        if to_user == session["username"]:
            flash("Cannot tip yourself")
            return redirect(url_for("tip"))
        # Transfer coins
        user["balance"] -= amount
        users[to_user]["balance"] += amount
        save_users()
        flash(f"Tipped {amount} coins to {to_user}")
        return redirect(url_for("menu"))
    return render_template("tip.html")

@app.route("/admin", methods=["GET", "POST"])
def admin():
    user = current_user()
    if not user:
        return redirect(url_for("login"))

    if "admin_authenticated" not in session:
        if request.method == "POST":
            password = request.form.get("password", "")
            if password == ADMIN_PASS:
                session["admin_authenticated"] = True
                return redirect(url_for("admin"))
            else:
                flash("Incorrect admin password")
        return render_template("admin_login.html")

    if request.method == "POST":
        action = request.form.get("action")
        if action == "change_balance":
            target_user = request.form.get("target_user", "").strip()
            new_balance = request.form.get("new_balance", "").strip()
            if target_user not in users:
                flash("User not found")
            else:
                try:
                    new_balance = int(new_balance)
                    if new_balance < 0:
                        raise ValueError()
                    users[target_user]["balance"] = new_balance
                    save_users()
                    flash(f"Balance of {target_user} set to {new_balance}")
                except ValueError:
                    flash("Invalid balance")
        # Reload the admin page to show users
    return render_template("admin.html", users=users)

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

@app.route("/blackjack", methods=["GET", "POST"])
def blackjack():
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
            return redirect(url_for("blackjack"))
        return render_template("blackjack_bet.html", balance=user["balance"])

    if bj["state"] == "playing":
        deck = bj["deck"]
        player_hand = bj["player_hand"]
        dealer_hand = bj["dealer_hand"]

        if request.method == "POST":
            action = request.form.get("action")
            if action == "hit":
                player_hand.append(deck.pop())
                if hand_value(player_hand) > 21:
                    bj["state"] = "finished"
            elif action == "stand":
                bj["state"] = "dealer_turn"

            bj["player_hand"] = player_hand
            bj["deck"] = deck
            session["blackjack"] = bj
            return redirect(url_for("blackjack"))
        else:
            # GET request: render game state page
            return render_template("blackjack_play.html",
                                   player_hand=player_hand,
                                   dealer_hand=dealer_hand,
                                   player_value=hand_value(player_hand),
                                   balance=bj["balance"])

    if bj["state"] == "dealer_turn":
        deck = bj["deck"]
        dealer_hand = bj["dealer_hand"]

        while hand_value(dealer_hand) < 17:
            dealer_hand.append(deck.pop())

        bj["dealer_hand"] = dealer_hand
        bj["state"] = "finished"
        session["blackjack"] = bj
        return redirect(url_for("blackjack"))

    if bj["state"] == "finished":
        player_hand = bj["player_hand"]
        dealer_hand = bj["dealer_hand"]
        bet = bj["bet"]
        balance = bj["balance"]

        player_val = hand_value(player_hand)
        dealer_val = hand_value(dealer_hand)
        result = ""
        winnings = 0

        if player_val > 21:
            result = "You busted! You lose."
        elif dealer_val > 21 or player_val > dealer_val:
            result = f"You win! You won {bet * 2} coins."
            winnings = bet * 2
        elif player_val == dealer_val:
            result = "Push. Your bet is returned."
            winnings = bet
        else:
            result = "You lose."

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
        bet_color = request.form.get("color")
        bet_amount = request.form.get("bet")

        try:
            bet_amount = int(bet_amount)
            if bet_amount <= 0 or bet_amount > user["balance"]:
                flash("Invalid bet amount")
                return render_template("roulette.html", balance=user["balance"])
        except ValueError:
            flash("Invalid bet amount")
            return render_template("roulette.html", balance=user["balance"])

        if bet_color not in colors:
            flash("Invalid color choice")
            return render_template("roulette.html", balance=user["balance"])

        user["balance"] -= bet_amount

        # Spin wheel
        winning_color = random.choice(wheel)

        # Determine winnings
        if bet_color == winning_color:
            if winning_color == "green":
                multiplier = 14
            else:
                multiplier = 2
            winnings = bet_amount * multiplier
            user["balance"] += winnings
            result = f"You won {winnings} coins! The ball landed on {winning_color}."
        else:
            result = f"You lost. The ball landed on {winning_color}."

        save_users()
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
        bet_amount = request.form.get("bet")
        try:
            bet_amount = int(bet_amount)
            if bet_amount <= 0 or bet_amount > user["balance"]:
                flash("Invalid bet amount")
                return render_template("slots.html", balance=user["balance"])
        except ValueError:
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
            message = f"Jackpot! You won {winnings} coins."
        elif a == b or b == c or a == c:
            multipliers = {"🍒": 2, "🔔": 2, "🍋": 1, "⭐": 3, "💎": 5, "7️⃣": 10}
            # Use the most common symbol in two matches
            matched_symbol = a if a == b else b if b == c else a
            winnings = bet_amount * multipliers.get(matched_symbol, 0)
            win = True
            message = f"Nice! You won {winnings} coins."
        else:
            message = "No match. You lost your bet."

        if win:
            user["balance"] += winnings

        save_users()
        return render_template("slots_result.html", reels=[a,b,c], message=message, balance=user["balance"])

    return render_template("slots.html", balance=user["balance"])

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)

