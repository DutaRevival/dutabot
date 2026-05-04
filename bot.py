import logging
import random
import json
import os
from datetime import datetime
import pytz
import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# ========== CONFIG ==========
TOKEN = "8272954567:AAHvGwWyUIjDkfxmO8MImyyuPeczMxfhVak"
SCORES_FILE = "scores.json"

logging.basicConfig(level=logging.INFO)

# ========== SCORES ==========
def load_scores():
    if os.path.exists(SCORES_FILE):
        with open(SCORES_FILE, "r") as f:
            return json.load(f)
    return {}

def save_scores(scores):
    with open(SCORES_FILE, "w") as f:
        json.dump(scores, f)

def add_score(user_id, username, points):
    scores = load_scores()
    uid = str(user_id)
    if uid not in scores:
        scores[uid] = {"username": username, "score": 0}
    scores[uid]["score"] += points
    scores[uid]["username"] = username
    save_scores(scores)

def get_user_score(user_id):
    scores = load_scores()
    return scores.get(str(user_id), {}).get("score", 0)

# ========== DONNÉES ==========
WORDS = [
    "elephant", "football", "telegram", "python", "musique",
    "vacances", "ordinateur", "riviere", "montagne", "champion",
    "victoire", "journee", "soleil", "famille", "bonheur",
    "cuisine", "aventure", "galaxie", "caramel", "bibliotheque"
]

QUIZ_QUESTIONS = [
    {"q": "Quelle est la capitale de la France ?", "a": "paris"},
    {"q": "Combien de joueurs dans une equipe de foot ?", "a": "11"},
    {"q": "Quel pays a remporte la Coupe du Monde 2018 ?", "a": "france"},
    {"q": "Quelle est la planete la plus proche du soleil ?", "a": "mercure"},
    {"q": "Combien de continents y a-t-il sur Terre ?", "a": "7"},
    {"q": "Quelle est la plus grande planete du systeme solaire ?", "a": "jupiter"},
    {"q": "En quelle annee a eu lieu la premiere Coupe du Monde ?", "a": "1930"},
    {"q": "Quel est l animal le plus rapide du monde ?", "a": "guepard"},
    {"q": "Combien de cordes a une guitare classique ?", "a": "6"},
    {"q": "Quel est le pays le plus grand du monde ?", "a": "russie"},
]

CITY_TIMEZONES = {
    "london": "Europe/London",
    "paris": "Europe/Paris",
    "new york": "America/New_York",
    "tokyo": "Asia/Tokyo",
    "dubai": "Asia/Dubai",
    "lagos": "Africa/Lagos",
    "dakar": "Africa/Dakar",
    "abidjan": "Africa/Abidjan",
    "casablanca": "Africa/Casablanca",
    "nairobi": "Africa/Nairobi",
    "cairo": "Africa/Cairo",
    "berlin": "Europe/Berlin",
    "madrid": "Europe/Madrid",
    "moscou": "Europe/Moscow",
    "moscow": "Europe/Moscow",
    "beijing": "Asia/Shanghai",
    "sydney": "Australia/Sydney",
    "kinshasa": "Africa/Kinshasa",
    "accra": "Africa/Accra",
}

jumble_sessions = {}
quiz_sessions = {}

# ========== COMMANDES ==========
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = (
        "Bienvenue sur DutaBot!\n\n"
        "Commandes disponibles:\n\n"
        "/jumble - Mot melange a deviner (+10 pts)\n"
        "/quiz - Question culture generale (+15 pts)\n"
        "/score - Votre score\n"
        "/top - Classement general\n"
        "/time london - Heure dans une ville\n"
        "/foot - Scores de foot\n\n"
        "Bonne chance!"
    )
    await update.message.reply_text(msg)

async def jumble(update: Update, context: ContextTypes.DEFAULT_TYPE):
    word = random.choice(WORDS)
    shuffled = list(word)
    random.shuffle(shuffled)
    while "".join(shuffled) == word:
        random.shuffle(shuffled)
    shuffled_word = "".join(shuffled).upper()
    user_id = update.effective_user.id
    jumble_sessions[user_id] = word
    await update.message.reply_text(
        f"JUMBLE!\n\nRemettez les lettres dans le bon ordre:\n\n>>> {shuffled_word} <<<\n\nTapez votre reponse!"
    )

async def quiz(update: Update, context: ContextTypes.DEFAULT_TYPE):
    question = random.choice(QUIZ_QUESTIONS)
    user_id = update.effective_user.id
    quiz_sessions[user_id] = question["a"]
    await update.message.reply_text(
        f"QUIZ!\n\n{question['q']}\n\nTapez votre reponse!"
    )

async def score(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    s = get_user_score(user_id)
    name = update.effective_user.first_name
    await update.message.reply_text(f"Votre score:\n{name}: {s} points")

async def top(update: Update, context: ContextTypes.DEFAULT_TYPE):
    scores = load_scores()
    if not scores:
        await update.message.reply_text("Aucun score pour le moment!")
        return
    sorted_scores = sorted(scores.items(), key=lambda x: x[1]["score"], reverse=True)[:10]
    medals = ["1.", "2.", "3.", "4.", "5.", "6.", "7.", "8.", "9.", "10."]
    lines = ["CLASSEMENT GENERAL\n"]
    for i, (uid, data) in enumerate(sorted_scores):
        lines.append(f"{medals[i]} {data['username']} - {data['score']} pts")
    await update.message.reply_text("\n".join(lines))

async def time_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: /time london")
        return
    city = " ".join(context.args).lower()
    tz_name = CITY_TIMEZONES.get(city)
    if not tz_name:
        await update.message.reply_text(
            f"Ville '{city}' non trouvee.\nVilles disponibles: london, paris, tokyo, dubai, lagos, dakar, moscow, sydney, kinshasa, accra, abidjan, casablanca..."
        )
        return
    tz = pytz.timezone(tz_name)
    now = datetime.now(tz)
    await update.message.reply_text(
        f"Heure a {city.title()}:\n{now.strftime('%H:%M')} - {now.strftime('%d/%m/%Y')}"
    )

async def foot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Scores de foot - Fonctionnalite bientot disponible!"
    )

async def handle_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text.strip().lower()
    name = update.effective_user.first_name

    if user_id in jumble_sessions:
        correct = jumble_sessions[user_id]
        if text == correct:
            del jumble_sessions[user_id]
            add_score(user_id, name, 10)
            s = get_user_score(user_id)
            await update.message.reply_text(
                f"Bravo! C etait {correct.upper()}!\n+10 points! Votre score: {s} pts\n\nTapez /jumble pour rejouer!"
            )
        else:
            await update.message.reply_text("Mauvaise reponse! Essayez encore ou /jumble pour un nouveau mot.")

    elif user_id in quiz_sessions:
        correct = quiz_sessions[user_id]
        if text == correct.lower():
            del quiz_sessions[user_id]
            add_score(user_id, name, 15)
            s = get_user_score(user_id)
            await update.message.reply_text(
                f"Correct!\n+15 points! Votre score: {s} pts\n\nTapez /quiz pour une nouvelle question!"
            )
        else:
            await update.message.reply_text("Mauvaise reponse! Essayez encore ou /quiz pour une nouvelle question.")

# ========== MAIN ==========
def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("jumble", jumble))
    app.add_handler(CommandHandler("quiz", quiz))
    app.add_handler(CommandHandler("score", score))
    app.add_handler(CommandHandler("top", top))
    app.add_handler(CommandHandler("time", time_cmd))
    app.add_handler(CommandHandler("foot", foot))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_answer))
    print("Bot demarre!")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
