# -*- coding: utf-8 -*-
import logging
import random
import json
import os
import unicodedata
import asyncio
from datetime import datetime
import pytz
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes

TOKEN = "8272954567:AAHvGwWyUIjDkfxmO8MImyyuPeczMxfhVak"
SCORES_FILE = "scores.json"
logging.basicConfig(level=logging.INFO)

# ========== UTILITAIRES ==========
def normalize(text):
    text = text.lower().strip()
    return ''.join(
        c for c in unicodedata.normalize('NFD', text)
        if unicodedata.category(c) != 'Mn'
    )

def can_form_word(word, letters):
    letters = list(letters.lower())
    for c in word.lower():
        if c in letters:
            letters.remove(c)
        else:
            return False
    return True

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

# ========== JUMBLE DATA ==========
JUMBLE_SETS = [
    "ABDNEATUER",
    "SOMELICART",
    "TNEPLIAMOS",
    "RACEBOTINF",
    "DELACTIRMO",
    "PATIOSNECR",
    "FORMALBENIT",
    "CASTLERIPON",
    "VITRACEOLMS",
    "GRANDPOTILE",
]

# ========== QUIZ DATA (100 questions sans repetition) ==========
ALL_QUIZ_QUESTIONS = [
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
    {"q": "Quelle est la capitale du Cameroun ?", "a": "yaounde"},
    {"q": "Quelle est la capitale du Senegal ?", "a": "dakar"},
    {"q": "Quelle est la capitale de la Cote d Ivoire ?", "a": "abidjan"},
    {"q": "Quelle est la capitale du Nigeria ?", "a": "abuja"},
    {"q": "Quel est le fleuve le plus long du monde ?", "a": "nil"},
    {"q": "Quelle est la capitale du Bresil ?", "a": "brasilia"},
    {"q": "Quel pays a remporte la Coupe du Monde 2022 ?", "a": "argentine"},
    {"q": "Combien de joueurs dans une equipe de basket ?", "a": "5"},
    {"q": "Quelle est la capitale de l Espagne ?", "a": "madrid"},
    {"q": "Quelle est la capitale de l Allemagne ?", "a": "berlin"},
    {"q": "Quelle est la capitale de l Italie ?", "a": "rome"},
    {"q": "Quelle est la capitale du Portugal ?", "a": "lisbonne"},
    {"q": "Quel pays a remporte la Coupe du Monde 2014 ?", "a": "allemagne"},
    {"q": "Combien de minutes dure un match de foot ?", "a": "90"},
    {"q": "Quelle est la capitale du Maroc ?", "a": "rabat"},
    {"q": "Quelle est la capitale de l Algerie ?", "a": "alger"},
    {"q": "Quelle est la capitale de la Tunisie ?", "a": "tunis"},
    {"q": "Quelle est la capitale du Ghana ?", "a": "accra"},
    {"q": "Quelle est la capitale du Mali ?", "a": "bamako"},
    {"q": "Quelle est la capitale du Togo ?", "a": "lome"},
    {"q": "Quelle est la capitale du Gabon ?", "a": "libreville"},
    {"q": "Quelle est la capitale de la RDC ?", "a": "kinshasa"},
    {"q": "Quel pays a remporte la Coupe du Monde 2010 ?", "a": "espagne"},
    {"q": "Quel pays a remporte la Coupe du Monde 2006 ?", "a": "italie"},
    {"q": "Quel pays a remporte la Coupe du Monde 2002 ?", "a": "bresil"},
    {"q": "Qui a invente le telephone ?", "a": "graham bell"},
    {"q": "Quelle est la capitale du Japon ?", "a": "tokyo"},
    {"q": "Quelle est la capitale de la Chine ?", "a": "pekin"},
    {"q": "Quelle est la capitale de l Inde ?", "a": "new delhi"},
    {"q": "Quelle est la capitale de l Australie ?", "a": "canberra"},
    {"q": "Combien d os dans le corps humain ?", "a": "206"},
    {"q": "Quelle est la capitale du Canada ?", "a": "ottawa"},
    {"q": "Quel est l ocean le plus grand du monde ?", "a": "pacifique"},
    {"q": "Combien de pays en Afrique ?", "a": "54"},
    {"q": "Quelle est la capitale de l Argentine ?", "a": "buenos aires"},
    {"q": "Quelle est la capitale du Mexique ?", "a": "mexico"},
    {"q": "Combien de secondes dans une heure ?", "a": "3600"},
    {"q": "Quel est le metal le plus precieux ?", "a": "or"},
    {"q": "Combien de jours dans une annee bissextile ?", "a": "366"},
    {"q": "Quelle est la capitale de la Russie ?", "a": "moscou"},
    {"q": "Quel est le sport le plus populaire au monde ?", "a": "football"},
    {"q": "Combien de grammes dans un kilogramme ?", "a": "1000"},
    {"q": "Quel est le plus grand desert du monde ?", "a": "sahara"},
    {"q": "Combien de couleurs dans l arc en ciel ?", "a": "7"},
    {"q": "Quelle est la capitale de la Belgique ?", "a": "bruxelles"},
    {"q": "Quelle est la capitale des Pays Bas ?", "a": "amsterdam"},
    {"q": "Quelle est la capitale de la Suisse ?", "a": "berne"},
    {"q": "Quel animal est le symbole de la paix ?", "a": "colombe"},
    {"q": "Combien de metres dans un kilometre ?", "a": "1000"},
    {"q": "Quelle est la capitale du Royaume Uni ?", "a": "londres"},
    {"q": "Quel est le plus grand pays d Afrique ?", "a": "algerie"},
    {"q": "Combien de joueurs dans une equipe de rugby ?", "a": "15"},
    {"q": "Quelle est la capitale de l Egypte ?", "a": "le caire"},
    {"q": "Quelle est la capitale du Kenya ?", "a": "nairobi"},
    {"q": "Qui a peint la Joconde ?", "a": "leonard de vinci"},
    {"q": "Combien de planetes dans le systeme solaire ?", "a": "8"},
    {"q": "Quel est le plus grand mammifere marin ?", "a": "baleine bleue"},
    {"q": "Combien de lettres dans l alphabet francais ?", "a": "26"},
    {"q": "Quelle est la capitale de la Turquie ?", "a": "ankara"},
    {"q": "Quel est le plus haut sommet du monde ?", "a": "everest"},
    {"q": "Quelle est la capitale de la Grece ?", "a": "athenes"},
    {"q": "Combien de faces a un cube ?", "a": "6"},
    {"q": "Quel est le plus petit pays du monde ?", "a": "vatican"},
    {"q": "Combien de minutes dans une journee ?", "a": "1440"},
    {"q": "Quelle est la capitale de la Pologne ?", "a": "varsovie"},
    {"q": "Quel est l element chimique de l eau ?", "a": "h2o"},
    {"q": "Quelle est la capitale de la Suede ?", "a": "stockholm"},
    {"q": "Combien de joueurs dans une equipe de volleyball ?", "a": "6"},
    {"q": "Quel est le plus grand continent ?", "a": "asie"},
    {"q": "Quelle est la capitale du Zimbabwe ?", "a": "harare"},
    {"q": "Quel pays a la plus grande population au monde ?", "a": "inde"},
    {"q": "Quelle est la monnaie du Japon ?", "a": "yen"},
    {"q": "Quelle est la monnaie du Royaume Uni ?", "a": "livre sterling"},
    {"q": "Quelle est la monnaie des USA ?", "a": "dollar"},
    {"q": "Quel est le pays le plus peuple d Afrique ?", "a": "nigeria"},
    {"q": "Combien de zeros dans un million ?", "a": "6"},
    {"q": "Quel est le plus long fleuve d Afrique ?", "a": "nil"},
    {"q": "Quelle est la capitale du Burkina Faso ?", "a": "ouagadougou"},
    {"q": "Quelle est la capitale du Niger ?", "a": "niamey"},
    {"q": "Quelle est la capitale du Tchad ?", "a": "ndjamena"},
    {"q": "Combien de mois dans une annee ?", "a": "12"},
    {"q": "Quel pays a gagné l Euro 2020 ?", "a": "italie"},
    {"q": "Combien de buts Ronaldo a marque en carriere en clubs (approximatif) ?", "a": "700"},
    {"q": "Quel club a gagne le plus de Champions League ?", "a": "real madrid"},
    {"q": "En quelle annee a ete cree Facebook ?", "a": "2004"},
    {"q": "Qui a fonde Apple ?", "a": "steve jobs"},
    {"q": "En quelle annee a ete lance le premier iPhone ?", "a": "2007"},
]

# Sessions
jumble_sessions = {}
quiz_sessions = {}
quiz_used_questions = {}  # Par user : questions deja posees

# ========== CITY TIMEZONES ==========
CITY_TIMEZONES = {
    "london": "Europe/London", "angleterre": "Europe/London", "uk": "Europe/London",
    "paris": "Europe/Paris", "france": "Europe/Paris",
    "tokyo": "Asia/Tokyo", "japon": "Asia/Tokyo",
    "dubai": "Asia/Dubai", "eau": "Asia/Dubai",
    "lagos": "Africa/Lagos", "nigeria": "Africa/Lagos", "abuja": "Africa/Lagos",
    "dakar": "Africa/Dakar", "senegal": "Africa/Dakar",
    "abidjan": "Africa/Abidjan", "cote d ivoire": "Africa/Abidjan", "ivory coast": "Africa/Abidjan",
    "casablanca": "Africa/Casablanca", "maroc": "Africa/Casablanca", "rabat": "Africa/Casablanca",
    "nairobi": "Africa/Nairobi", "kenya": "Africa/Nairobi",
    "cairo": "Africa/Cairo", "egypte": "Africa/Cairo", "le caire": "Africa/Cairo",
    "berlin": "Europe/Berlin", "allemagne": "Europe/Berlin",
    "madrid": "Europe/Madrid", "espagne": "Europe/Madrid",
    "rome": "Europe/Rome", "italie": "Europe/Rome",
    "moscou": "Europe/Moscow", "moscow": "Europe/Moscow", "russie": "Europe/Moscow",
    "beijing": "Asia/Shanghai", "chine": "Asia/Shanghai", "pekin": "Asia/Shanghai", "shanghai": "Asia/Shanghai",
    "sydney": "Australia/Sydney", "australie": "Australia/Sydney",
    "kinshasa": "Africa/Kinshasa", "rdc": "Africa/Kinshasa", "congo": "Africa/Kinshasa",
    "accra": "Africa/Accra", "ghana": "Africa/Accra",
    "new york": "America/New_York", "usa": "America/New_York", "etats unis": "America/New_York",
    "los angeles": "America/Los_Angeles", "miami": "America/New_York",
    "montreal": "America/Toronto", "canada": "America/Toronto", "toronto": "America/Toronto", "ottawa": "America/Toronto",
    "yaounde": "Africa/Douala", "douala": "Africa/Douala", "cameroun": "Africa/Douala", "cameroon": "Africa/Douala",
    "addis ababa": "Africa/Addis_Ababa", "ethiopie": "Africa/Addis_Ababa",
    "tunis": "Africa/Tunis", "tunisie": "Africa/Tunis",
    "alger": "Africa/Algiers", "algerie": "Africa/Algiers",
    "bamako": "Africa/Bamako", "mali": "Africa/Bamako",
    "lome": "Africa/Lome", "togo": "Africa/Lome",
    "cotonou": "Africa/Porto-Novo", "benin": "Africa/Porto-Novo",
    "niamey": "Africa/Niamey", "niger": "Africa/Niamey",
    "ouagadougou": "Africa/Ouagadougou", "burkina": "Africa/Ouagadougou",
    "libreville": "Africa/Libreville", "gabon": "Africa/Libreville",
    "brazzaville": "Africa/Brazzaville",
    "ndjamena": "Africa/Ndjamena", "tchad": "Africa/Ndjamena",
    "johannesburg": "Africa/Johannesburg", "afrique du sud": "Africa/Johannesburg",
    "lisbonne": "Europe/Lisbon", "portugal": "Europe/Lisbon",
    "amsterdam": "Europe/Amsterdam", "pays bas": "Europe/Amsterdam",
    "bruxelles": "Europe/Brussels", "belgique": "Europe/Brussels",
    "berne": "Europe/Zurich", "suisse": "Europe/Zurich", "geneve": "Europe/Zurich",
    "vienne": "Europe/Vienna", "autriche": "Europe/Vienna",
    "varsovie": "Europe/Warsaw", "pologne": "Europe/Warsaw",
    "stockholm": "Europe/Stockholm", "suede": "Europe/Stockholm",
    "oslo": "Europe/Oslo", "norvege": "Europe/Oslo",
    "copenhague": "Europe/Copenhagen", "danemark": "Europe/Copenhagen",
    "seoul": "Asia/Seoul", "coree": "Asia/Seoul",
    "singapour": "Asia/Singapore", "singapore": "Asia/Singapore",
    "bangkok": "Asia/Bangkok", "thailande": "Asia/Bangkok",
    "mumbai": "Asia/Kolkata", "inde": "Asia/Kolkata", "new delhi": "Asia/Kolkata",
    "karachi": "Asia/Karachi", "pakistan": "Asia/Karachi",
    "lima": "America/Lima", "perou": "America/Lima",
    "bogota": "America/Bogota", "colombie": "America/Bogota",
    "buenos aires": "America/Argentina/Buenos_Aires", "argentine": "America/Argentina/Buenos_Aires",
    "sao paulo": "America/Sao_Paulo", "bresil": "America/Sao_Paulo",
    "mexico": "America/Mexico_City", "mexique": "America/Mexico_City",
    "ankara": "Europe/Istanbul", "turquie": "Europe/Istanbul", "istanbul": "Europe/Istanbul",
    "athenes": "Europe/Athens", "grece": "Europe/Athens",
    "harare": "Africa/Harare", "zimbabwe": "Africa/Harare",
    "lusaka": "Africa/Lusaka", "zambie": "Africa/Lusaka",
    "maputo": "Africa/Maputo", "mozambique": "Africa/Maputo",
}

# ========== COMMANDES ==========
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Bienvenue sur DutaBot!\n\n"
        "Commandes:\n\n"
        "/jumble - Formez le max de mots en 30s\n"
        "/quiz - Question avec chrono 30s (+15 pts)\n"
        "/score - Votre score personnel\n"
        "/top - Classement general de tous les joueurs\n"
        "/time paris - Heure dans un pays ou ville\n"
        "/foot - Scores et championnats de foot\n\n"
        "Bonne chance!"
    )

# ========== JUMBLE ==========
async def jumble(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    letters = random.choice(JUMBLE_SETS)
    jumble_sessions[user_id] = {"letters": letters, "found_words": [], "active": True}
    await update.message.reply_text(
        f"JUMBLE! Vous avez 30 secondes!\n\n"
        f"Lettres: >>> {letters} <<<\n\n"
        f"Formez le max de mots avec ces lettres!\n"
        f"Chaque mot valide = 1 point\n\n"
        f"C est parti!"
    )
    await asyncio.sleep(30)
    if user_id in jumble_sessions and jumble_sessions[user_id]["active"]:
        session = jumble_sessions[user_id]
        session["active"] = False
        found = session["found_words"]
        points = len(found)
        if points > 0:
            add_score(user_id, update.effective_user.first_name, points)
            total = get_user_score(user_id)
            mots_str = ", ".join(found)
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=(
                    f"Temps ecoule!\n\n"
                    f"Mots trouves ({points}): {mots_str}\n"
                    f"+{points} points!\n"
                    f"Score total: {total} pts\n\n"
                    f"/jumble pour rejouer!"
                )
            )
        else:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="Temps ecoule! Aucun mot trouve.\n/jumble pour reessayer!"
            )
        del jumble_sessions[user_id]

# ========== QUIZ AVEC CHRONO ET SANS REPETITION ==========
async def quiz(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if user_id not in quiz_used_questions:
        quiz_used_questions[user_id] = []

    used = quiz_used_questions[user_id]
    available = [q for q in ALL_QUIZ_QUESTIONS if q["q"] not in used]

    if not available:
        quiz_used_questions[user_id] = []
        available = ALL_QUIZ_QUESTIONS[:]

    question = random.choice(available)
    quiz_used_questions[user_id].append(question["q"])
    quiz_sessions[user_id] = {"answer": question["a"], "active": True}

    await update.message.reply_text(
        f"QUIZ! Vous avez 30 secondes!\n\n"
        f"{question['q']}\n\n"
        f"Tapez votre reponse!"
    )

    await asyncio.sleep(30)

    if user_id in quiz_sessions and quiz_sessions[user_id]["active"]:
        correct = quiz_sessions[user_id]["answer"]
        quiz_sessions[user_id]["active"] = False
        del quiz_sessions[user_id]
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"Temps ecoule! La reponse etait: {correct.upper()}\n\n/quiz pour une nouvelle question!"
        )

# ========== SCORE PERSONNEL ==========
async def score(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    s = get_user_score(user_id)
    name = update.effective_user.first_name
    await update.message.reply_text(
        f"Votre score:\n\n"
        f"Joueur: {name}\n"
        f"Score: {s} points"
    )

# ========== CLASSEMENT GENERAL ==========
async def top(update: Update, context: ContextTypes.DEFAULT_TYPE):
    scores = load_scores()
    if not scores:
        await update.message.reply_text("Aucun joueur enregistre pour le moment!")
        return
    sorted_scores = sorted(scores.items(), key=lambda x: x[1]["score"], reverse=True)
    medals = ["1.", "2.", "3.", "4.", "5.", "6.", "7.", "8.", "9.", "10."]
    lines = ["CLASSEMENT GENERAL\n"]
    for i, (uid, data) in enumerate(sorted_scores[:10]):
        lines.append(f"{medals[i]} {data['username']} - {data['score']} pts")
    lines.append(f"\nTotal joueurs: {len(scores)}")
    await update.message.reply_text("\n".join(lines))

# ========== TIME ==========
async def time_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: /time paris\nEx: /time cameroun, /time london, /time dakar")
        return
    city = " ".join(context.args).lower().strip()
    city_norm = normalize(city)
    tz_name = None
    for key, val in CITY_TIMEZONES.items():
        if normalize(key) == city_norm:
            tz_name = val
            break
    if not tz_name:
        await update.message.reply_text(
            f"'{city}' non trouve.\n\nExemples:\n/time paris\n/time london\n/time cameroun\n/time dakar\n/time dubai\n/time new york"
        )
        return
    tz = pytz.timezone(tz_name)
    now = datetime.now(tz)
    await update.message.reply_text(
        f"Heure a {city.title()}:\n"
        f"{now.strftime('%H:%M')} - {now.strftime('%d/%m/%Y')}"
    )

# ========== FOOT ==========
async def foot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("Champions League", callback_data="foot_cl")],
        [InlineKeyboardButton("Premier League", callback_data="foot_pl")],
        [InlineKeyboardButton("Liga (Espagne)", callback_data="foot_liga")],
        [InlineKeyboardButton("Serie A (Italie)", callback_data="foot_seria")],
        [InlineKeyboardButton("Bundesliga (Allemagne)", callback_data="foot_bundesliga")],
        [InlineKeyboardButton("Ligue 1 (France)", callback_data="foot_ligue1")],
        [InlineKeyboardButton("Europa League", callback_data="foot_europa")],
        [InlineKeyboardButton("Coupe du Monde", callback_data="foot_cdm")],
    ]
    await update.message.reply_text("Choisissez un championnat:", reply_markup=InlineKeyboardMarkup(keyboard))

async def foot_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    leagues = {
        "foot_cl": "Champions League",
        "foot_pl": "Premier League",
        "foot_liga": "Liga - Espagne",
        "foot_seria": "Serie A - Italie",
        "foot_bundesliga": "Bundesliga - Allemagne",
        "foot_ligue1": "Ligue 1 - France",
        "foot_europa": "Europa League",
        "foot_cdm": "Coupe du Monde",
    }
    league_name = leagues.get(query.data, "Championnat")
    await query.edit_message_text(
        f"{league_name}\n\n"
        f"Pour les scores en direct:\n"
        f"www.livescore.com\n"
        f"www.flashscore.com\n"
        f"www.sofascore.com"
    )

# ========== HANDLER REPONSES ==========
async def handle_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text.strip()
    text_norm = normalize(text)
    name = update.effective_user.first_name

    # JUMBLE
    if user_id in jumble_sessions and jumble_sessions[user_id]["active"]:
        session = jumble_sessions[user_id]
        letters = session["letters"]
        found = session["found_words"]
        if len(text) < 2:
            return
        if text_norm in [normalize(w) for w in found]:
            await update.message.reply_text(f"'{text}' deja trouve!")
            return
        if can_form_word(text_norm, normalize(letters)):
            found.append(text)
            await update.message.reply_text(f"'{text}' - Valide! {len(found)} mot(s) trouve(s)!")
        else:
            await update.message.reply_text(f"'{text}' - Impossible avec ces lettres!")
        return

    # QUIZ
    if user_id in quiz_sessions and quiz_sessions[user_id]["active"]:
        correct = quiz_sessions[user_id]["answer"]
        if text_norm == normalize(correct):
            quiz_sessions[user_id]["active"] = False
            del quiz_sessions[user_id]
            add_score(user_id, name, 15)
            s = get_user_score(user_id)
            await update.message.reply_text(
                f"Correct! Bonne reponse!\n"
                f"+15 points! Score: {s} pts\n\n"
                f"/quiz pour une nouvelle question!"
            )
        else:
            await update.message.reply_text("Mauvaise reponse! Essayez encore!")
        return

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
    app.add_handler(CallbackQueryHandler(foot_callback, pattern="^foot_"))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_answer))
    print("Bot demarre!")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
