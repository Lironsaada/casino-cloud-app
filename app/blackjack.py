import random

suits = ['♠', '♥', '♦', '♣']
values = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']

def create_deck():
    return [v + s for s in suits for v in values]

def draw_card(deck):
    card = random.choice(deck)
    deck.remove(card)
    return card

def card_value(card):
    val = card[:-1]  # all chars except last (suit)
    if val in ['J', 'Q', 'K']:
        return 10
    elif val == 'A':
        return 11
    else:
        return int(val)

def hand_value(hand):
    total = 0
    aces = 0
    for card in hand:
        v = card_value(card)
        total += v
        if card[:-1] == 'A':
            aces += 1
    while total > 21 and aces > 0:
        total -= 10
        aces -= 1
    return total

def initial_hands(deck):
    player_hand = [draw_card(deck), draw_card(deck)]
    dealer_hand = [draw_card(deck), draw_card(deck)]
    return player_hand, dealer_hand

def can_split(hand):
    return len(hand) == 2 and hand[0][:-1] == hand[1][:-1]
