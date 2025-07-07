import random

WHEEL = ['red', 'black', 'red', 'black', 'red', 'black', 'red', 'green', 'black', 'red', 'black', 'red', 'black', 'red', 'black']

def spin_wheel():
    return random.choice(WHEEL)

def payout(bet, color, result_color):
    if color == result_color:
        if result_color == 'green':
            return bet * 14
        else:
            return bet * 2
    else:
        return 0
