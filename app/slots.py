import random

SYMBOLS = ["🍒", "🔔", "🍋", "⭐", "💎", "7️⃣"]

# Weighted symbols for more realistic frequency
WEIGHTS = [5, 4, 4, 3, 2, 1]

def spin_reels():
    reels = random.choices(SYMBOLS, weights=WEIGHTS, k=3)
    return reels

def calculate_payout(bet, reels):
    # 3 of the same symbol
    if reels[0] == reels[1] == reels[2]:
        symbol = reels[0]
        payouts = {
            "🍒": 3,
            "🔔": 5,
            "🍋": 2,
            "⭐": 10,
            "💎": 15,
            "7️⃣": 25
        }
        return bet * payouts.get(symbol, 0)

    # 2 of the same symbol
    if reels[0] == reels[1] or reels[1] == reels[2] or reels[0] == reels[2]:
        symbol = reels[1]  # middle symbol for simplicity
        payouts = {
            "🍒": 2,
            "🔔": 2,
            "🍋": 1,
            "⭐": 3,
            "💎": 5,
            "7️⃣": 10
        }
        return bet * payouts.get(symbol, 0)

    # No matches
    return 0
