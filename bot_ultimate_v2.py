
import random
import unicodedata

# ===== ENHANCED DICTIONARY =====

VALID_WORDS_FR_EN = {
    "rien","son","pont","pion","parler","terre","sable","football",
    "python","quiz","telegram","camera","ordinateur","internet",
    "goal","game","player","world","victory","music","science",
    "planet","creative","viral","challenge","community","diamond",
    "gold","silver","legend","battle","jumble","reaction","ranking"
}

def normalize(word):
    word = word.lower().strip()
    word = unicodedata.normalize('NFD', word)
    word = ''.join(c for c in word if unicodedata.category(c) != 'Mn')
    return word

def is_valid_word(word):
    return normalize(word) in VALID_WORDS_FR_EN

# ===== SMART JUMBLE ENGINE =====

WORD_BANK = [
    "football","reaction","ordinateur","internet","camera",
    "telegram","python","community","creative","challenge",
    "diamond","festival","generation","competition","science",
    "musique","planet","ranking","economy","galaxie",
    "adventure","monster","victory","capital","library"
]

RECENT_JUMBLES = []

def generate_dynamic_jumble():
    for _ in range(200):
        base_word = random.choice(WORD_BANK)

        letters = list(base_word.upper())
        random.shuffle(letters)

        jumble = ''.join(letters)

        if jumble not in RECENT_JUMBLES:
            RECENT_JUMBLES.append(jumble)

            if len(RECENT_JUMBLES) > 100:
                RECENT_JUMBLES.pop(0)

            return jumble

    random_letters = list("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
    random.shuffle(random_letters)
    return ''.join(random_letters[:10])

# ===== PLAYER PROFILE SYSTEM =====

PLAYER_PROFILES = {}

def get_player_profile(user_id, username="Player"):
    if user_id not in PLAYER_PROFILES:
        PLAYER_PROFILES[user_id] = {
            "name": username,
            "xp": 0,
            "level": 1,
            "league": "Bronze",
            "coins": 100
        }

    return PLAYER_PROFILES[user_id]

# ===== HARDER QUIZ SYSTEM =====

QUIZ_QUESTIONS = [
    {
        "question":"Which country won the FIFA World Cup 2022?",
        "options":["France","Argentina","Brazil","Germany"],
        "answer":"Argentina"
    },
    {
        "question":"Which player has the most Ballon d'Or awards?",
        "options":["Cristiano Ronaldo","Lionel Messi","Pelé","Cruyff"],
        "answer":"Lionel Messi"
    },
    {
        "question":"Who created Python programming language?",
        "options":["Guido van Rossum","Elon Musk","Bill Gates","Linus Torvalds"],
        "answer":"Guido van Rossum"
    },
    {
        "question":"Which club has the most UEFA Champions League titles?",
        "options":["Barcelona","Real Madrid","Bayern Munich","Liverpool"],
        "answer":"Real Madrid"
    }
]

# ===== PAYMENT SYSTEM PLACEHOLDER =====

PAYMENT_MESSAGE = '''
⚠️ Configure your real payment gateway.
The previous payment link caused a 404 error.
Use:
- Stripe
- PayPal
- Flutterwave
- LemonSqueezy
'''

print("Bot upgraded successfully.")
