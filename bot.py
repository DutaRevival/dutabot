# -*- coding: utf-8 -*-
import logging
import random
import json
import os
import unicodedata
import asyncio
import requests
import time
from datetime import datetime
import pytz
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes

TOKEN = "8272954567:AAHvGwWyUIjDkfxmO8MImyyuPeczMxfhVak"
FOOTBALL_API_KEY = "4b559620c705450f958b5fb0548ab6d3"
SCORES_FILE = "scores.json"
logging.basicConfig(level=logging.INFO)

def normalize(text):
    text = text.lower().strip()
    return ''.join(c for c in unicodedata.normalize('NFD', text) if unicodedata.category(c) != 'Mn')

def can_form_word(word, letters):
    letters = list(normalize(letters))
    for c in normalize(word):
        if c in letters:
            letters.remove(c)
        else:
            return False
    return True

def check_word_online(word):
    """Verifie si un mot existe via API - FR et EN"""
    w = normalize(word)
    if len(w) < 2:
        return False

    # 1. Verifier en francais via Dicolink
    try:
        resp = requests.get(
            f"https://api.dicolink.com/v1/mot/{word}/definitions",
            params={"api_key": "Q4xSGGGGGGGGGGGGGGGGGGGGGGG"},
            timeout=3
        )
        if resp.status_code == 200 and len(resp.json()) > 0:
            return True
    except:
        pass

    # 2. Verifier en anglais via Free Dictionary API
    try:
        resp = requests.get(
            f"https://api.dictionaryapi.dev/api/v2/entries/en/{word}",
            timeout=3
        )
        if resp.status_code == 200:
            return True
    except:
        pass

    # 3. Fallback sur dictionnaire local si APIs indisponibles
    return normalize(word) in FALLBACK_DICT

# Dictionnaire de secours si APIs indisponibles
FALLBACK_DICT = set(normalize(w) for w in [
    "ah","ai","an","as","au","ba","be","bi","bo","bu","ca","ce","ci","da","de","du",
    "eh","el","em","en","er","es","et","eu","ex","fa","fi","go","ha","hi","ho","il",
    "in","je","la","le","li","lo","lu","ma","me","mi","mo","mu","na","ne","ni","no",
    "nu","on","or","os","ou","pa","pi","po","pu","ra","re","ri","ro","ru","sa","se",
    "si","so","su","ta","te","ti","to","tu","un","us","va","ve","vi","vo","vu","ya","yo",
    "ab","ad","ag","al","am","ar","at","aw","ax","ay","by","do","ed","ef","he","id",
    "if","is","it","jo","ka","ki","my","of","oh","oi","ok","om","op","ow","ox","oy",
    "pe","qi","sh","uh","um","up","we","wo","xi","xu","ye",
    "lit","lits","met","mets","mis","mot","mots","lot","lots","rot","pot","pots",
    "mer","amer","fer","ver","vert","net","set","jet","pet","bet","art","part","car",
    "can","ban","fan","man","ran","tan","van","pan","cap","map","nap","rap","tap",
    "cat","bat","fat","hat","mat","pat","rat","sat","bad","had","lad","mad","sad",
    "bag","lag","nag","rag","sag","tag","bit","fit","hit","kit","pit","sit","wit",
    "bog","cog","dog","fog","hog","jog","log","bon","con","don","ion","son","ton",
    "bug","dug","jug","mug","pug","rug","tug","bun","fun","gun","nun","pun","run",
    "sun","bus","but","cut","gut","hut","nut","put","rut","gel","nel","sel","tel",
    "able","acte","aide","aile","aire","ami","amie","ane","ange","arme","aube","auto",
    "beau","bien","bleu","bloc","bois","bol","bon","bord","bout","bras","cage","camp",
    "case","cent","char","chat","chef","cher","ciel","cite","clan","clou","club","code",
    "coin","cone","cote","coup","cran","cure","dame","date","demi","dent","deux","dire",
    "dome","dose","drap","dune","dure","edit","elan","etat","etre","euro","face","fait",
    "file","film","fils","fine","flot","foie","fond","fort","four","gain","gale","gare",
    "gate","gaze","gene","gite","golf","gout","grad","gras","gris","hale","halo","hate",
    "hier","home","hors","hote","ile","jade","jean","joli","joue","jour","juge","jupe",
    "lame","lard","lent","lest","leur","lieu","lime","lire","lobe","loge","loin","lors",
    "loue","loup","lune","male","malt","mare","mars","mate","mere","mine","mode","mort",
    "mule","noel","noir","note","nuit","once","onde","oral","orge","ours","page","pale",
    "pare","part","pate","peau","pere","pied","pile","pine","pire","plan","plat","plie",
    "pore","port","pose","prix","puce","rade","rale","rame","rang","rape","rare","rase",
    "rate","reel","rein","rent","ride","rire","rite","robe","role","rude","ruse","sang",
    "sans","saut","seau","sere","seve","silo","sole","sort","sous","stop","sure","tare",
    "tele","tend","tenu","tire","toit","tome","tone","tore","tort","trac","tram","trap",
    "tres","trio","trop","tube","tune","type","vale","vane","veau","vent","vers","vide",
    "vile","vine","vite","voie","voir","vole","vote","vrai","zero","zone",
    "able","acid","aged","also","area","army","away","back","ball","band","bank","base",
    "bath","bear","beat","bell","best","bird","bite","blow","blue","boat","body","bold",
    "bolt","bond","bone","book","bore","born","both","bowl","burn","came","camp","cape",
    "card","care","cart","case","cast","cave","cent","char","chat","chin","chip","cite",
    "clan","clap","clip","clot","club","clue","coal","coat","coil","cold","colt","come",
    "cord","core","corn","cost","crop","dart","data","date","deal","dean","dear","debt",
    "deck","deed","deer","deli","dent","diet","dirt","disc","dish","disk","dock","dole",
    "dome","done","door","dorm","dote","down","drag","draw","drip","drop","drum","dual",
    "duel","dune","dupe","dust","earl","earn","east","edge","edit","else","emit","epic",
    "even","ever","evil","exam","face","fact","fail","fair","fall","fame","fang","fare",
    "farm","fast","fate","fear","feat","feel","fell","felt","fend","fern","file","fill",
    "film","find","fine","fire","firm","fist","flag","flat","flaw","flea","fled","flew",
    "flip","flow","foam","fold","folk","fond","food","fool","foot","ford","fore","fork",
    "form","fort","foul","four","free","fuel","full","fume","gain","gale","game","gang",
    "gate","gave","gaze","gear","gent","germ","girl","give","glad","glee","glob","glue",
    "goal","gold","golf","gone","good","gore","gown","grab","grad","gram","gray","grew",
    "grid","grim","grin","grip","grit","grow","gulf","gust","hack","hale","half","hall",
    "halt","hand","hang","hard","hare","harm","harp","hart","hate","have","heal","heap",
    "heat","heel","held","helm","help","here","hero","hide","high","hike","hill","hint",
    "hire","hold","hole","home","hood","hook","hope","horn","host","hour","hulk","hull",
    "hump","hunt","hurt","idea","idle","inch","into","iron","isle","item","jade","jail",
    "jaws","jean","jeer","joke","jolt","jump","just","keel","keen","keep","kick","kind",
    "king","knob","knot","lace","lack","lame","lamp","land","lane","lard","lark","lash",
    "last","late","lead","leaf","lean","leap","lend","lens","lest","liar","lice","lick",
    "lied","lies","life","lift","like","lime","limp","line","link","lint","list","live",
    "load","loam","lobe","lock","loft","lone","long","look","loom","lord","lore","lose",
    "lost","loud","love","luck","made","mail","main","make","male","malt","mane","mare",
    "mark","mart","mast","mate","meal","mean","meat","meet","melt","mend","mere","mild",
    "mile","milk","mill","mind","mine","mint","mire","miss","mist","moan","mole","monk",
    "mood","moon","moor","more","mort","most","move","muck","mule","must","nail","name",
    "near","neck","need","next","nice","nick","nine","node","none","noon","norm","nose",
    "note","null","oath","odds","once","open","oral","orca","oven","over","pace","pack",
    "page","paid","pain","pair","pale","palm","pane","park","part","past","path","peak",
    "peel","peer","pelt","pick","pier","pile","pine","pink","pipe","plan","play","plod",
    "plot","plow","plum","plus","poem","poet","pole","poll","pond","pore","port","pose",
    "post","pour","prey","prod","prop","pull","pump","pure","push","race","rack","raid",
    "rail","rain","rake","ramp","rang","rank","rant","rapt","rate","read","real","reap",
    "reel","rein","rely","rend","rent","rest","rice","rich","ride","rift","ring","riot",
    "rise","risk","road","roam","roar","robe","rock","rode","role","roll","roof","room",
    "root","rope","rose","rout","rude","ruin","rule","rump","rune","ruse","rush","rust",
    "safe","sail","sake","sale","salt","same","sand","sane","sang","sank","sate","save",
    "scan","scar","seal","seam","sear","seat","self","send","shed","shin","ship","shoe",
    "shop","shot","shun","shut","sick","side","sift","sign","silk","silo","silt","sing",
    "sink","site","size","skid","skim","skin","skip","slab","slap","slat","slim","slip",
    "slob","slop","slot","slum","slur","snag","snap","snob","snow","soak","soar","sock",
    "soil","sold","sole","some","song","soot","sore","sort","soul","soup","sour","span",
    "spar","spin","spit","spot","spur","stab","stag","star","stay","stem","step","stir",
    "stop","stub","stun","suck","suit","sulk","sung","sunk","sure","surf","swam","swan",
    "swap","sway","swim","tail","tale","talk","tall","tame","tang","tank","tare","tart",
    "teal","team","tear","teem","tell","tend","tent","term","thin","tide","tile","till",
    "time","tire","toad","toil","told","toll","tome","tone","tong","tool","torn","toss",
    "tour","town","trap","tray","tree","trim","trip","trod","true","tube","tuck","tuft",
    "tune","tusk","twin","type","undo","upon","urge","used","vale","vane","vast","veil",
    "vein","vent","verb","very","vest","vial","vice","view","vile","vine","void","volt",
    "wade","wage","wail","wake","walk","wall","wand","wane","ward","ware","warm","warn",
    "warp","wart","wash","wave","weak","weal","wean","wear","weed","weld","went","west",
    "wide","wild","will","wilt","wind","wine","wing","wink","wire","wise","wish","wisp",
    "woke","wold","womb","wood","wool","word","wore","work","worm","worn","wrap","wren",
    "yell","zeal","zero","zinc","zone","zoom",
])

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

JUMBLE_SETS = [
    "ABDNEATUER","SOMELICART","TNEPLIAMOS","RACEBOTINF",
    "DELACTIRMO","PATIOSNECR","FORMALBENIT","CASTLERIPON",
    "VITRACEOLMS","GRANDPOTILE","PLANETORIES","CARBONITEMS",
]

ALL_QUIZ_QUESTIONS = [
    {"q": "Capitale de la France ?", "a": "paris", "choices": ["Madrid", "Paris", "Rome"]},
    {"q": "Joueurs dans une equipe de foot ?", "a": "11", "choices": ["9", "11", "13"]},
    {"q": "Vainqueur Coupe du Monde 2018 ?", "a": "france", "choices": ["France", "Allemagne", "Bresil"]},
    {"q": "Planete la plus proche du soleil ?", "a": "mercure", "choices": ["Venus", "Mercure", "Mars"]},
    {"q": "Combien de continents sur Terre ?", "a": "7", "choices": ["5", "6", "7"]},
    {"q": "Plus grande planete du systeme solaire ?", "a": "jupiter", "choices": ["Saturne", "Jupiter", "Neptune"]},
    {"q": "Annee de la 1ere Coupe du Monde ?", "a": "1930", "choices": ["1926", "1930", "1934"]},
    {"q": "Animal le plus rapide du monde ?", "a": "guepard", "choices": ["Lion", "Guepard", "Aigle"]},
    {"q": "Cordes sur une guitare classique ?", "a": "6", "choices": ["4", "6", "8"]},
    {"q": "Plus grand pays du monde ?", "a": "russie", "choices": ["Canada", "Chine", "Russie"]},
    {"q": "Capitale du Cameroun ?", "a": "yaounde", "choices": ["Douala", "Yaounde", "Bafoussam"]},
    {"q": "Capitale du Senegal ?", "a": "dakar", "choices": ["Dakar", "Thies", "Saint-Louis"]},
    {"q": "Capitale du Nigeria ?", "a": "abuja", "choices": ["Lagos", "Abuja", "Kano"]},
    {"q": "Fleuve le plus long du monde ?", "a": "nil", "choices": ["Amazone", "Nil", "Congo"]},
    {"q": "Capitale du Bresil ?", "a": "brasilia", "choices": ["Sao Paulo", "Rio", "Brasilia"]},
    {"q": "Vainqueur Coupe du Monde 2022 ?", "a": "argentine", "choices": ["France", "Argentine", "Bresil"]},
    {"q": "Joueurs dans une equipe de basket ?", "a": "5", "choices": ["5", "6", "7"]},
    {"q": "Capitale de l Espagne ?", "a": "madrid", "choices": ["Barcelone", "Valence", "Madrid"]},
    {"q": "Capitale de l Allemagne ?", "a": "berlin", "choices": ["Munich", "Berlin", "Hambourg"]},
    {"q": "Vainqueur Coupe du Monde 2014 ?", "a": "allemagne", "choices": ["Allemagne", "Argentine", "Bresil"]},
    {"q": "Duree d un match de foot ?", "a": "90 min", "choices": ["80 min", "90 min", "120 min"]},
    {"q": "Capitale du Maroc ?", "a": "rabat", "choices": ["Casablanca", "Marrakech", "Rabat"]},
    {"q": "Capitale du Ghana ?", "a": "accra", "choices": ["Kumasi", "Accra", "Tamale"]},
    {"q": "Vainqueur Coupe du Monde 2010 ?", "a": "espagne", "choices": ["Espagne", "Pays-Bas", "Allemagne"]},
    {"q": "Inventeur du telephone ?", "a": "graham bell", "choices": ["Thomas Edison", "Graham Bell", "Nikola Tesla"]},
    {"q": "Capitale du Japon ?", "a": "tokyo", "choices": ["Osaka", "Tokyo", "Kyoto"]},
    {"q": "Nombre d os dans le corps humain ?", "a": "206", "choices": ["186", "206", "256"]},
    {"q": "Plus grand ocean du monde ?", "a": "pacifique", "choices": ["Atlantique", "Indien", "Pacifique"]},
    {"q": "Combien de pays en Afrique ?", "a": "54", "choices": ["48", "54", "60"]},
    {"q": "Secondes dans une heure ?", "a": "3600", "choices": ["3000", "3600", "6000"]},
    {"q": "Plus grand desert du monde ?", "a": "sahara", "choices": ["Kalahari", "Sahara", "Gobi"]},
    {"q": "Couleurs dans l arc en ciel ?", "a": "7", "choices": ["5", "6", "7"]},
    {"q": "Plus grand pays d Afrique ?", "a": "algerie", "choices": ["Soudan", "Algerie", "RDC"]},
    {"q": "Joueurs dans une equipe de rugby ?", "a": "15", "choices": ["13", "15", "17"]},
    {"q": "Peintre de la Joconde ?", "a": "leonard de vinci", "choices": ["Michel-Ange", "Leonard de Vinci", "Raphael"]},
    {"q": "Planetes dans le systeme solaire ?", "a": "8", "choices": ["7", "8", "9"]},
    {"q": "Plus haut sommet du monde ?", "a": "everest", "choices": ["K2", "Everest", "Kilimandjaro"]},
    {"q": "Plus petit pays du monde ?", "a": "vatican", "choices": ["Monaco", "Vatican", "Liechtenstein"]},
    {"q": "Plus grand continent ?", "a": "asie", "choices": ["Afrique", "Asie", "Amerique"]},
    {"q": "Pays le plus peuple du monde ?", "a": "inde", "choices": ["Chine", "Inde", "USA"]},
    {"q": "Monnaie du Japon ?", "a": "yen", "choices": ["Won", "Yuan", "Yen"]},
    {"q": "Monnaie du Royaume Uni ?", "a": "livre sterling", "choices": ["Euro", "Livre Sterling", "Dollar"]},
    {"q": "Pays le plus peuple d Afrique ?", "a": "nigeria", "choices": ["Ethiopie", "Nigeria", "Egypte"]},
    {"q": "Club avec le plus de Champions League ?", "a": "real madrid", "choices": ["Real Madrid", "Barcelona", "Bayern Munich"]},
    {"q": "Annee creation de Facebook ?", "a": "2004", "choices": ["2002", "2004", "2006"]},
    {"q": "Fondateur d Apple ?", "a": "steve jobs", "choices": ["Bill Gates", "Steve Jobs", "Mark Zuckerberg"]},
    {"q": "Annee lancement du 1er iPhone ?", "a": "2007", "choices": ["2005", "2007", "2009"]},
    {"q": "Pays de naissance de Cristiano Ronaldo ?", "a": "portugal", "choices": ["Espagne", "Bresil", "Portugal"]},
    {"q": "Pays de naissance de Lionel Messi ?", "a": "argentine", "choices": ["Argentine", "Uruguay", "Chili"]},
    {"q": "Recordman du monde du 100m ?", "a": "usain bolt", "choices": ["Usain Bolt", "Tyson Gay", "Asafa Powell"]},
    {"q": "Pays de la Tour Eiffel ?", "a": "france", "choices": ["Belgique", "Suisse", "France"]},
    {"q": "Pays du Colisee ?", "a": "italie", "choices": ["Grece", "Italie", "Espagne"]},
    {"q": "Plus grande montagne d Afrique ?", "a": "kilimandjaro", "choices": ["Mont Kenya", "Kilimandjaro", "Mont Cameroun"]},
    {"q": "Debut de la 1ere Guerre Mondiale ?", "a": "1914", "choices": ["1912", "1914", "1916"]},
    {"q": "Pays inventeur du football ?", "a": "angleterre", "choices": ["France", "Angleterre", "Ecosse"]},
    {"q": "Joueurs dans une equipe de handball ?", "a": "7", "choices": ["5", "7", "9"]},
    {"q": "Capitale de l Egypte ?", "a": "le caire", "choices": ["Alexandrie", "Le Caire", "Louxor"]},
    {"q": "Os le plus long du corps ?", "a": "femur", "choices": ["Tibia", "Femur", "Humerus"]},
    {"q": "Animal au plus long cou ?", "a": "girafe", "choices": ["Elephant", "Chameau", "Girafe"]},
    {"q": "Seul mammifere qui vole ?", "a": "chauve souris", "choices": ["Ecureuil volant", "Chauve Souris", "Lemur"]},
    {"q": "Monnaie de l Europe ?", "a": "euro", "choices": ["Franc", "Euro", "Mark"]},
    {"q": "Dents d un adulte ?", "a": "32", "choices": ["28", "30", "32"]},
    {"q": "Annee homme sur la lune ?", "a": "1969", "choices": ["1965", "1969", "1972"]},
    {"q": "Inventeur de l ampoule electrique ?", "a": "thomas edison", "choices": ["Nikola Tesla", "Thomas Edison", "Benjamin Franklin"]},
    {"q": "Faces d un cube ?", "a": "6", "choices": ["4", "6", "8"]},
    {"q": "Joueurs volleyball ?", "a": "6", "choices": ["5", "6", "7"]},
    {"q": "Capitale de l Italie ?", "a": "rome", "choices": ["Milan", "Naples", "Rome"]},
    {"q": "Capitale du Portugal ?", "a": "lisbonne", "choices": ["Porto", "Lisbonne", "Faro"]},
    {"q": "Vainqueur Coupe du Monde 2006 ?", "a": "italie", "choices": ["France", "Italie", "Allemagne"]},
    {"q": "Vainqueur Coupe du Monde 2002 ?", "a": "bresil", "choices": ["Bresil", "Allemagne", "Coree du Sud"]},
    {"q": "Capitale de la Cote d Ivoire ?", "a": "abidjan", "choices": ["Yamoussoukro", "Abidjan", "Bouake"]},
    {"q": "Capitale du Mali ?", "a": "bamako", "choices": ["Tombouctou", "Bamako", "Segou"]},
    {"q": "Capitale du Togo ?", "a": "lome", "choices": ["Kara", "Lome", "Sokode"]},
    {"q": "Capitale du Gabon ?", "a": "libreville", "choices": ["Port-Gentil", "Franceville", "Libreville"]},
    {"q": "Capitale de la RDC ?", "a": "kinshasa", "choices": ["Lubumbashi", "Kinshasa", "Goma"]},
    {"q": "Zeros dans un million ?", "a": "6", "choices": ["5", "6", "7"]},
    {"q": "Element chimique de l eau ?", "a": "h2o", "choices": ["CO2", "H2O", "O2"]},
    {"q": "Compositeur de la 5eme symphonie ?", "a": "beethoven", "choices": ["Mozart", "Beethoven", "Bach"]},
    {"q": "Pays du Machu Picchu ?", "a": "perou", "choices": ["Bolivie", "Colombie", "Perou"]},
    {"q": "Jours dans une annee bissextile ?", "a": "366", "choices": ["364", "365", "366"]},
    {"q": "Sport le plus populaire au monde ?", "a": "football", "choices": ["Basketball", "Football", "Tennis"]},
    {"q": "Capitale de la Russie ?", "a": "moscou", "choices": ["Saint-Petersbourg", "Moscou", "Kazan"]},
    {"q": "Capitale de la Chine ?", "a": "pekin", "choices": ["Shanghai", "Pekin", "Canton"]},
    {"q": "Capitale de la Belgique ?", "a": "bruxelles", "choices": ["Anvers", "Bruges", "Bruxelles"]},
    {"q": "Capitale des Pays Bas ?", "a": "amsterdam", "choices": ["Rotterdam", "Amsterdam", "La Haye"]},
    {"q": "Capitale du Burkina Faso ?", "a": "ouagadougou", "choices": ["Bobo-Dioulasso", "Ouagadougou", "Koudougou"]},
    {"q": "Capitale du Niger ?", "a": "niamey", "choices": ["Zinder", "Niamey", "Maradi"]},
    {"q": "Capitale du Tchad ?", "a": "ndjamena", "choices": ["Moundou", "Ndjamena", "Sarh"]},
    {"q": "Vainqueur Euro 2020 ?", "a": "italie", "choices": ["France", "Angleterre", "Italie"]},
    {"q": "Minutes dans une journee ?", "a": "1440", "choices": ["1000", "1440", "2400"]},
    {"q": "Grammes dans un kg ?", "a": "1000", "choices": ["500", "1000", "1500"]},
]

jumble_sessions = {}
quiz_sessions = {}
quiz_used_questions = {}
quiz_timers = {}

CITY_TIMEZONES = {
    "london": "Europe/London", "angleterre": "Europe/London", "uk": "Europe/London",
    "paris": "Europe/Paris", "france": "Europe/Paris",
    "tokyo": "Asia/Tokyo", "japon": "Asia/Tokyo",
    "dubai": "Asia/Dubai",
    "lagos": "Africa/Lagos", "nigeria": "Africa/Lagos", "abuja": "Africa/Lagos",
    "dakar": "Africa/Dakar", "senegal": "Africa/Dakar",
    "abidjan": "Africa/Abidjan", "cote d ivoire": "Africa/Abidjan",
    "casablanca": "Africa/Casablanca", "maroc": "Africa/Casablanca", "rabat": "Africa/Casablanca",
    "nairobi": "Africa/Nairobi", "kenya": "Africa/Nairobi",
    "cairo": "Africa/Cairo", "egypte": "Africa/Cairo", "le caire": "Africa/Cairo",
    "berlin": "Europe/Berlin", "allemagne": "Europe/Berlin",
    "madrid": "Europe/Madrid", "espagne": "Europe/Madrid",
    "rome": "Europe/Rome", "italie": "Europe/Rome",
    "moscou": "Europe/Moscow", "russie": "Europe/Moscow",
    "beijing": "Asia/Shanghai", "chine": "Asia/Shanghai", "pekin": "Asia/Shanghai",
    "sydney": "Australia/Sydney", "australie": "Australia/Sydney",
    "kinshasa": "Africa/Kinshasa", "rdc": "Africa/Kinshasa", "congo": "Africa/Kinshasa",
    "accra": "Africa/Accra", "ghana": "Africa/Accra",
    "new york": "America/New_York", "usa": "America/New_York", "etats unis": "America/New_York",
    "los angeles": "America/Los_Angeles", "miami": "America/New_York",
    "canada": "America/Toronto", "toronto": "America/Toronto", "montreal": "America/Toronto",
    "yaounde": "Africa/Douala", "douala": "Africa/Douala", "cameroun": "Africa/Douala",
    "ethiopie": "Africa/Addis_Ababa", "addis ababa": "Africa/Addis_Ababa",
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
    "geneve": "Europe/Zurich", "suisse": "Europe/Zurich",
    "varsovie": "Europe/Warsaw", "pologne": "Europe/Warsaw",
    "stockholm": "Europe/Stockholm", "suede": "Europe/Stockholm",
    "seoul": "Asia/Seoul", "coree": "Asia/Seoul",
    "singapour": "Asia/Singapore",
    "bangkok": "Asia/Bangkok", "thailande": "Asia/Bangkok",
    "mumbai": "Asia/Kolkata", "inde": "Asia/Kolkata", "new delhi": "Asia/Kolkata",
    "lima": "America/Lima", "perou": "America/Lima",
    "bogota": "America/Bogota", "colombie": "America/Bogota",
    "buenos aires": "America/Argentina/Buenos_Aires", "argentine": "America/Argentina/Buenos_Aires",
    "sao paulo": "America/Sao_Paulo", "bresil": "America/Sao_Paulo",
    "mexico": "America/Mexico_City", "mexique": "America/Mexico_City",
    "istanbul": "Europe/Istanbul", "turquie": "Europe/Istanbul",
    "athenes": "Europe/Athens", "grece": "Europe/Athens",
    "harare": "Africa/Harare", "zimbabwe": "Africa/Harare",
}

LEAGUE_IDS = {
    "foot_cl": ("2001", "Champions League"),
    "foot_pl": ("2021", "Premier League"),
    "foot_liga": ("2014", "Liga - Espagne"),
    "foot_seria": ("2019", "Serie A - Italie"),
    "foot_bundesliga": ("2002", "Bundesliga - Allemagne"),
    "foot_ligue1": ("2015", "Ligue 1 - France"),
    "foot_europa": ("2146", "Europa League"),
    "foot_cdm": ("2000", "Coupe du Monde"),
}

def get_live_scores(league_id):
    try:
        headers = {"X-Auth-Token": FOOTBALL_API_KEY}
        url = f"https://api.football-data.org/v4/competitions/{league_id}/matches?status=LIVE"
        matches = requests.get(url, headers=headers, timeout=10).json().get("matches", [])
        if not matches:
            url2 = f"https://api.football-data.org/v4/competitions/{league_id}/matches?status=IN_PLAY,PAUSED,HALFTIME"
            matches = requests.get(url2, headers=headers, timeout=10).json().get("matches", [])
        return matches
    except:
        return None

def format_matches(matches, league_name):
    if matches is None:
        return f"{league_name}\n\nErreur de connexion. Reessayez."
    if not matches:
        return f"{league_name}\n\nPas d evenement en ce moment."
    lines = [f"{league_name} - EN DIRECT\n"]
    for m in matches[:8]:
        home = m["homeTeam"].get("shortName") or m["homeTeam"]["name"]
        away = m["awayTeam"].get("shortName") or m["awayTeam"]["name"]
        score = m.get("score", {})
        full = score.get("fullTime", {})
        hs = full.get("home")
        as_ = full.get("away")
        if hs is None:
            half = score.get("halfTime", {})
            hs = half.get("home", "?")
            as_ = half.get("away", "?")
        lines.append(f"{home} {hs} - {as_} {away}")
    return "\n".join(lines)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Bienvenue sur DutaBot!\n\n"
        "/jumble - Formez le max de mots en 3 minutes\n"
        "/quiz - QCM 3 choix de reponse\n"
        "/score - Votre score\n"
        "/top - Classement general\n"
        "/time paris - Heure dans un pays\n"
        "/foot - Scores de foot en direct\n\n"
        "Bonne chance!"
    )

async def jumble(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id

    if user_id in jumble_sessions and jumble_sessions[user_id].get("active"):
        s = jumble_sessions[user_id]
        elapsed = time.time() - s["start_time"]
        remaining = int(180 - elapsed)
        if remaining > 0:
            await update.message.reply_text(
                f"Partie en cours! Il reste {remaining}s\n"
                f"Lettres: >>> {s['letters']} <<<\n"
                f"Mots: {len(s['found_words'])} | Points: {s['total_points']}"
            )
            return

    letters = random.choice(JUMBLE_SETS)
    jumble_sessions[user_id] = {
        "letters": letters, "found_words": [], "active": True,
        "start_time": time.time(), "chat_id": chat_id,
        "username": update.effective_user.first_name, "total_points": 0
    }

    await update.message.reply_text(
        f"JUMBLE! Vous avez 3 minutes!\n\n"
        f"Lettres: >>> {letters} <<<\n\n"
        f"Points = nombre de lettres du mot\n"
        f"Ex: BON=3pts | GRAND=5pts\n\n"
        f"✅ = Valide | ❌ = Invalide\n\n"
        f"C est parti!"
    )

    asyncio.create_task(jumble_timer(user_id, chat_id, context))

async def jumble_timer(user_id, chat_id, context):
    await asyncio.sleep(180)
    if user_id not in jumble_sessions or not jumble_sessions[user_id].get("active"):
        return
    session = jumble_sessions[user_id]
    session["active"] = False
    found = session["found_words"]
    points = session["total_points"]
    username = session["username"]
    if points > 0:
        add_score(user_id, username, points)
        total = get_user_score(user_id)
        mots_str = ", ".join([f"{w}({len(normalize(w))})" for w in found])
        await context.bot.send_message(
            chat_id=chat_id,
            text=f"Temps ecoule!\n\nMots: {mots_str}\n\n+{points} points!\nScore total: {total} pts\n\n/jumble pour rejouer!"
        )
    else:
        await context.bot.send_message(
            chat_id=chat_id,
            text="Temps ecoule! Aucun mot valide.\n/jumble pour reessayer!"
        )
    del jumble_sessions[user_id]

async def quiz(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id

    # Annuler timer precedent et effacer ancienne session
    if user_id in quiz_timers:
        quiz_timers[user_id].cancel()
        del quiz_timers[user_id]
    if user_id in quiz_sessions:
        del quiz_sessions[user_id]

    if user_id not in quiz_used_questions:
        quiz_used_questions[user_id] = []
    used = quiz_used_questions[user_id]
    available = [q for q in ALL_QUIZ_QUESTIONS if q["q"] not in used]
    if not available:
        quiz_used_questions[user_id] = []
        available = ALL_QUIZ_QUESTIONS[:]

    question = random.choice(available)
    quiz_used_questions[user_id].append(question["q"])
    choices = question["choices"][:]
    random.shuffle(choices)
    session_id = str(int(time.time() * 1000))

    quiz_sessions[user_id] = {
        "answer": normalize(question["a"]),
        "active": True, "chat_id": chat_id,
        "username": update.effective_user.first_name,
        "choices_normalized": [normalize(c) for c in choices],
        "choices_display": choices,
        "session_id": session_id,
    }

    keyboard = [[InlineKeyboardButton(c, callback_data=f"qz_{user_id}_{i}_{session_id}")] for i, c in enumerate(choices)]
    await update.message.reply_text(
        f"QUIZ!\n\n{question['q']}",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

    task = asyncio.create_task(quiz_timer(user_id, chat_id, question["a"], session_id, context))
    quiz_timers[user_id] = task

async def quiz_timer(user_id, chat_id, answer, session_id, context):
    await asyncio.sleep(30)
    if user_id in quiz_sessions and quiz_sessions[user_id].get("active") and quiz_sessions[user_id].get("session_id") == session_id:
        quiz_sessions[user_id]["active"] = False
        del quiz_sessions[user_id]
        if user_id in quiz_timers:
            del quiz_timers[user_id]
        await context.bot.send_message(
            chat_id=chat_id,
            text=f"Temps ecoule! La reponse etait: {answer.upper()}\n\n/quiz pour continuer!"
        )

async def quiz_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    parts = query.data.split("_")
    if len(parts) < 4:
        await query.answer()
        return

    target_user_id = int(parts[1])
    choice_index = int(parts[2])
    session_id = parts[3]
    actual_user_id = query.from_user.id

    if actual_user_id != target_user_id:
        await query.answer("Ce n est pas votre question!", show_alert=True)
        return

    if target_user_id not in quiz_sessions or not quiz_sessions[target_user_id].get("active"):
        await query.answer()
        await query.edit_message_text("Question expiree. /quiz pour continuer!")
        return

    session = quiz_sessions[target_user_id]
    if session.get("session_id") != session_id:
        await query.answer()
        await query.edit_message_text("Question expiree. /quiz pour continuer!")
        return

    correct = session["answer"]
    username = session["username"]
    chosen_norm = session["choices_normalized"][choice_index]
    chosen_display = session["choices_display"][choice_index]

    session["active"] = False
    del quiz_sessions[target_user_id]

    if target_user_id in quiz_timers:
        quiz_timers[target_user_id].cancel()
        del quiz_timers[target_user_id]

    await query.answer()

    if chosen_norm == correct:
        add_score(target_user_id, username, 15)
        s = get_user_score(target_user_id)
        await query.edit_message_text(f"✅ {chosen_display} - Bonne reponse!\n+15 points! Score: {s} pts\n\n/quiz pour continuer!")
    else:
        await query.edit_message_text(f"❌ {chosen_display} - Mauvaise reponse!\nBonne reponse: {correct.upper()}\n\n/quiz pour continuer!")

async def score(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    s = get_user_score(user_id)
    name = update.effective_user.first_name
    await update.message.reply_text(f"Votre score:\n\n{name}: {s} points")

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
        await update.message.reply_text(f"'{city}' non trouve.\nEx: /time paris, /time cameroun, /time dakar, /time london")
        return
    tz = pytz.timezone(tz_name)
    now = datetime.now(tz)
    await update.message.reply_text(f"Heure a {city.title()}:\n{now.strftime('%H:%M')} - {now.strftime('%d/%m/%Y')}")

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
    league_data = LEAGUE_IDS.get(query.data)
    if not league_data:
        return
    league_id, league_name = league_data
    await query.edit_message_text("Recherche en cours...")
    matches = get_live_scores(league_id)
    await query.edit_message_text(format_matches(matches, league_name))

async def handle_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text.strip()
    text_norm = normalize(text)

    if user_id not in jumble_sessions or not jumble_sessions[user_id].get("active"):
        return

    session = jumble_sessions[user_id]
    elapsed = time.time() - session["start_time"]
    if elapsed >= 180:
        return

    letters = session["letters"]
    found = session["found_words"]
    remaining = int(180 - elapsed)

    if len(text) < 2:
        return

    if text_norm in [normalize(w) for w in found]:
        await update.message.reply_text(f"'{text}' deja trouve!\nLettres: >>> {letters} <<< | {remaining}s")
        return

    if not can_form_word(text_norm, normalize(letters)):
        await update.message.reply_text(f"❌ '{text}' - Impossible avec ces lettres!\nLettres: >>> {letters} <<< | {remaining}s")
        return

    # Verification via API + dictionnaire local
    await update.message.reply_text(f"Verification de '{text}'...")
    valid = await asyncio.get_event_loop().run_in_executor(None, check_word_online, text)

    if valid:
        pts = len(text_norm)
        found.append(text)
        session["total_points"] += pts
        await update.message.reply_text(
            f"✅ '{text}' +{pts}pts\n"
            f"Mots: {len(found)} | Total: {session['total_points']}pts | {remaining}s\n"
            f"Lettres: >>> {letters} <<<"
        )
    else:
        await update.message.reply_text(f"❌ '{text}' - Mot non reconnu!\nLettres: >>> {letters} <<< | {remaining}s")

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("jumble", jumble))
    app.add_handler(CommandHandler("quiz", quiz))
    app.add_handler(CommandHandler("score", score))
    app.add_handler(CommandHandler("top", top))
    app.add_handler(CommandHandler("time", time_cmd))
    app.add_handler(CommandHandler("foot", foot))
    app.add_handler(CallbackQueryHandler(quiz_callback, pattern="^qz_"))
    app.add_handler(CallbackQueryHandler(foot_callback, pattern="^foot_"))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_answer))
    print("Bot demarre!")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
