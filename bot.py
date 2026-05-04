import logging
import random
import json
import os
from datetime import datetime
import pytz
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# ========== CONFIG ==========
TOKEN = "8272954567:AAHvGwWyUIjDkfxmO8MImyyuPeczMxfhVak"
SCORES_FILE = "scores.json"
FOOTBALL_API_KEY = "YOUR_FOOTBALL_API_KEY"  # Optionnel

# ========== LOGGING ==========
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
    uid = str(user_id)
    return scores.get(uid, {}).get("score", 0)

# ========== MOTS JUMBLE ==========
WORDS = [
    "elephant", "football", "telegram", "python", "musique",
    "vacances", "ordinateur", "riviere", "montagne", "champion",
    "victoire", "journee", "soleil", "famille", "bonheur",
    "cuisine", "aventure", "librairie", "galaxie", "caramel"
]

QUIZ_QUESTIONS = [
    {"q": "Quelle est la capitale de la France ?", "a": "paris"},
    {"q": "Combien de joueurs dans une équipe de foot ?", "a": "11"},
    {"q": "Quel pays a remporté la Coupe du Monde 2018 ?", "a": "france"},
    {"q": "Quelle est la planète la plus proche du soleil ?", "a": "mercure"},
    {"q": "Combien de continents y a-t-il sur Terre ?", "a": "7"},
    {"q": "Qui a peint la Joconde ?", "a": "leonard de vinci"},
    {"q": "Quelle est la plus grande planète du système solaire ?", "a": "jupiter"},
    {"q": "En quelle année a eu lieu la première Coupe du Monde ?", "a": "1930"},
    {"q": "Quel est l'animal le plus rapide du monde ?", "a": "guepard"},
    {"q": "Combien de cordes a une guitare classique ?", "a": "6"},
]

# Stockage en mémoire des sessions de jeu
jumble_sessions = {}
quiz_sessions = {}

# ========== COMMANDES ==========

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = (
        "👋 *Bienvenue sur DutaBot !*\n\n"
        "Voici les commandes disponibles :\n\n"
        "🎮 *Jeux*\n"
        "/jumble — Devinez le mot mélangé\n"
        "/quiz — Répondez à une question\n\n"
        "🏆 *Scores*\n"
        "/score — Voir votre score\n"
        "/top — Classement général\n\n"
        "⚽ *Football*\n"
        "/foot — Scores de foot du jour\n\n"
        "🕐 *Heure*\n"
        "/time london — Heure dans une ville\n\n"
        "Bonne chance ! 🍀"
    )
    await update.message.reply_text(msg, parse_mode="Markdown")

# ========== JUMBLE ==========
async def jumble(update: Update, context: ContextTypes.DEFAULT_TYPE):
    word = random.choice(WORDS)
    shuffled = list(word)
    random.shuffle(shuffled)
    while "".join(shuffled) == word:
        random.shuffle(shuffled)
    shuffled_word = "".join(shuffled)

    user_id = update.effective_user.id
    jumble_sessions[user_id] = word

    await update.message.reply_text(
        f"🔀 *JUMBLE !*\n\n"
        f"Remettez les lettres dans le bon ordre :\n\n"
        f"➡️  `{shuffled_word.upper()}`\n\n"
        f"Tapez votre réponse directement !",
        parse_mode="Markdown"
    )

async def handle_jumble_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user = update.effective_user
    text = update.message.text.strip().lower()

    if user_id in jumble_sessions:
        correct = jumble_sessions[user_id]
        if text == correct:
            del jumble_sessions[user_id]
            add_score(user_id, user.first_name, 10)
            score = get_user_score(user_id)
            await update.message.reply_text(
                f"✅ *Bravo !* C'était bien *{correct.upper()}* !\n"
                f"🏆 +10 points ! Votre score : *{score} pts*\n\n"
                f"Tapez /jumble pour rejouer !",
                parse_mode="Markdown"
            )
        else:
            await update.message.reply_text(
                f"❌ Mauvaise réponse ! Essayez encore... ou tapez /jumble pour un nouveau mot.",
                parse_mode="Markdown"
            )
    elif user_id in quiz_sessions:
        correct = quiz_sessions[user_id]
        if text == correct.lower():
            del quiz_sessions[user_id]
            add_score(user_id, user.first_name, 15)
            score = get_user_score(user_id)
            await update.message.reply_text(
                f"✅ *Correct !* Bonne réponse !\n"
                f"🏆 +15 points ! Votre score : *{score} pts*\n\n"
                f"Tapez /quiz pour une nouvelle question !",
                parse_mode="Markdown"
            )
        else:
            await update.message.reply_text(
                f"❌ Mauvaise réponse ! Essayez encore ou tapez /quiz pour une nouvelle question.",
            )

# ========== QUIZ ==========
async def quiz(update: Update, context: ContextTypes.DEFAULT_TYPE):
    question = random.choice(QUIZ_QUESTIONS)
    user_id = update.effective_user.id
    quiz_sessions[user_id] = question["a"]

    await update.message.reply_text(
        f"🎯 *QUIZ !*\n\n"
        f"❓ {question['q']}\n\n"
        f"Tapez votre réponse directement !",
        parse_mode="Markdown"
    )

# ========== SCORE ==========
async def score(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user = update.effective_user
    s = get_user_score(user_id)
    await update.message.reply_text(
        f"🏆 *Votre score*\n\n"
        f"👤 {user.first_name}\n"
        f"⭐ {s} points",
        parse_mode="Markdown"
    )

# ========== CLASSEMENT ==========
async def top(update: Update, context: ContextTypes.DEFAULT_TYPE):
    scores = load_scores()
    if not scores:
        await update.message.reply_text("Aucun score enregistré pour le moment !")
        return

    sorted_scores = sorted(scores.items(), key=lambda x: x[1]["score"], reverse=True)[:10]
    medals = ["🥇", "🥈", "🥉"] + ["🏅"] * 7

    lines = ["🏆 *CLASSEMENT GÉNÉRAL*\n"]
    for i, (uid, data) in enumerate(sorted_scores):
        lines.append(f"{medals[i]} {data['username']} — *{data['score']} pts*")

    await update.message.reply_text("\n".join(lines), parse_mode="Markdown")

# ========== HEURE MONDIALE ==========
CITY_TIMEZONES = {
    "london": "Europe/London",
    "paris": "Europe/Paris",
    "new york": "America/New_York",
    "new_york": "America/New_York",
    "newyork": "America/New_York",
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
    "rome": "Europe/Rome",
    "moscou": "Europe/Moscow",
    "moscow": "Europe/Moscow",
    "beijing": "Asia/Shanghai",
    "sydney": "Australia/Sydney",
    "los angeles": "America/Los_Angeles",
    "los_angeles": "America/Los_Angeles",
    "sao paulo": "America/Sao_Paulo",
    "kinshasa": "Africa/Kinshasa",
    "accra": "Africa/Accra",
    "addis ababa": "Africa/Addis_Ababa",
}

async def time_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text(
            "📍 Usage : `/time london` ou `/time paris`",
            parse_mode="Markdown"
        )
        return

    city = " ".join(context.args).lower()
    tz_name = CITY_TIMEZONES.get(city)

    if not tz_name:
        await update.message.reply_text(
            f"❌ Ville *{city}* non trouvée.\n\n"
            f"Villes disponibles : london, paris, tokyo, dubai, lagos, dakar, new york, moscow, sydney...",
            parse_mode="Markdown"
        )
        return

    tz = pytz.timezone(tz_name)
    now = datetime.now(tz)
    time_str = now.strftime("%H:%M")
    date_str = now.strftime("%A %d %B %Y")

    await update.message.reply_text(
        f"🕐 *{city.title()}*\n\n"
        f"⏰ {time_str}\n"
        f"📅 {date_str}",
        parse_mode="Markdown"
    )

# ========== FOOT ==========
async def foot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "⚽ *Scores de foot*\n\n"
        "Cette fonctionnalité utilise une API externe.\n"
        "Voici les grands matchs d'aujourd'hui :\n\n"
        "🔄 Chargement en cours...\n\n"
        "_(Pour activer les vrais scores, ajoutez une clé API football-data.org)_",
        parse_mode="Markdown"
    )
    # Pour activer : créez un compte gratuit sur https://www.football-data.org/
    # et remplacez YOUR_FOOTBALL_API_KEY dans le code

# ========== MAIN ==========
def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("jumble", jumble))
    app.add_handler(CommandHandler("quiz", quiz))
    app.add_handler(CommandHandler("score", score))
    app.add_handler(CommandHandler("top", top))
    app.add_handler(CommandHandler("time", time_cmd))
    app.add_handler(CommandHandler("foot", foot))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_jumble_answer))

    print("✅ Bot démarré !")
    app.run_polling()

if __name__ == "__main__":
    main()
