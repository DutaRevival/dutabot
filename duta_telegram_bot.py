
import logging
import random
import json
import os
import requests
from datetime import datetime
import pytz
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

TOKEN = "REMPLACE_PAR_TON_TOKEN"
SCORES_FILE = "scores.json"

logging.basicConfig(level=logging.INFO)

# ===== SCORES =====
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
    save_scores(scores)

# ===== JUMBLE =====
jumble_active = False
letters = ""
found_words = []

DICTIONARY = ["par","rat","tap","tape","part","rape","pet","tar","art","eat","tea","ate"]

def jumble(update: Update, context: CallbackContext):
    global jumble_active, letters, found_words

    letters = "trape"
    found_words = []
    jumble_active = True

    update.message.reply_text(f"🔤 JUMBLE\nLettres: {letters.upper()}\n⏱️ 30 sec")

    context.job_queue.run_once(end_jumble, 30, context=update.effective_chat.id)

def end_jumble(context):
    global jumble_active
    jumble_active = False
    context.bot.send_message(chat_id=context.job.context, text="⏰ Fin du jumble!")

def valid_word(word):
    temp = list(letters)
    for l in word:
        if l in temp:
            temp.remove(l)
        else:
            return False
    return True

# ===== QUIZ =====
quiz_answer = ""
quiz_active = False

def quiz(update: Update, context: CallbackContext):
    global quiz_answer, quiz_active

    res = requests.get("https://opentdb.com/api.php?amount=1&type=multiple").json()
    q = res["results"][0]

    quiz_answer = q["correct_answer"].lower()
    quiz_active = True

    update.message.reply_text(f"❓ {q['question']}\n⏱️ 20 sec")

    context.job_queue.run_once(end_quiz, 20, context=update.effective_chat.id)

def end_quiz(context):
    global quiz_active, quiz_answer
    context.bot.send_message(chat_id=context.job.context, text=f"⏰ Réponse: {quiz_answer}")
    quiz_active = False
    quiz_answer = ""

# ===== METEO =====
def weather(update: Update, context: CallbackContext):
    city = " ".join(context.args) if context.args else "Douala"

    try:
        geo = requests.get(f"https://geocoding-api.open-meteo.com/v1/search?name={city}").json()
        lat = geo["results"][0]["latitude"]
        lon = geo["results"][0]["longitude"]

        meteo = requests.get(f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true").json()

        temp = meteo["current_weather"]["temperature"]

        update.message.reply_text(f"🌦️ {city}: {temp}°C")

    except:
        update.message.reply_text("❌ Ville introuvable")

# ===== TIME =====
def time_cmd(update: Update, context: CallbackContext):
    tz = pytz.timezone("Africa/Douala")
    now = datetime.now(tz)
    update.message.reply_text(now.strftime("🕒 %H:%M - %d/%m/%Y"))

# ===== FOOTBALL =====
def foot(update: Update, context: CallbackContext):
    try:
        res = requests.get("https://www.thesportsdb.com/api/v1/json/3/eventspastleague.php?id=4328").json()
        matchs = res["events"][:5]

        txt = "⚽ Derniers matchs EPL:\n"
        for m in matchs:
            txt += f"{m['strHomeTeam']} {m['intHomeScore']} - {m['intAwayScore']} {m['strAwayTeam']}\n"

        update.message.reply_text(txt)

    except:
        update.message.reply_text("❌ erreur foot")

# ===== SCORE =====
def top(update: Update, context: CallbackContext):
    scores = load_scores()
    sorted_scores = sorted(scores.items(), key=lambda x: x[1]["score"], reverse=True)[:10]

    txt = "🏆 Classement:\n"
    for i,(uid,data) in enumerate(sorted_scores):
        txt += f"{i+1}. {data['username']} - {data['score']} pts\n"

    update.message.reply_text(txt)

# ===== MESSAGES =====
def handle(update: Update, context: CallbackContext):
    global jumble_active, quiz_active

    user_id = update.effective_user.id
    name = update.effective_user.first_name
    text = update.message.text.lower()

    # JUMBLE
    if jumble_active:
        if text not in found_words and text in DICTIONARY and valid_word(text):
            found_words.append(text)
            add_score(user_id, name, 1)
            update.message.reply_text("✔️")
        else:
            update.message.reply_text("❌")

    # QUIZ
    elif quiz_active:
        if text == quiz_answer:
            add_score(user_id, name, 5)
            update.message.reply_text("✅ Bonne réponse !")
            quiz_active = False

# ===== MAIN =====
def main():
    updater = Updater(TOKEN)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("jumble", jumble))
    dp.add_handler(CommandHandler("quiz", quiz))
    dp.add_handler(CommandHandler("weather", weather))
    dp.add_handler(CommandHandler("time", time_cmd))
    dp.add_handler(CommandHandler("foot", foot))
    dp.add_handler(CommandHandler("top", top))

    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle))

    print("Bot lancé 🔥")
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
