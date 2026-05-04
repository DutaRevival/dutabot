# -*- coding: utf-8 -*-
import logging
import random
import json
import os
import unicodedata
import asyncio
import requests
from datetime import datetime
import pytz
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes

TOKEN = "8272954567:AAHvGwWyUIjDkfxmO8MImyyuPeczMxfhVak"
FOOTBALL_API_KEY = "4b559620c705450f958b5fb0548ab6d3"
SCORES_FILE = "scores.json"
logging.basicConfig(level=logging.INFO)

# ========== DICTIONNAIRE ==========
# Mots français et anglais valides (2 lettres et plus)
DICTIONNAIRE = set([
    # 2 lettres FR
    "ah","ai","an","as","au","ax","ay","ba","be","bi","bo","bu","ca","ce","ci","co","da","de","du","eh","el","em","en","er","es","et","eu","ex","fa","fi","go","ha","hi","ho","il","in","is","je","la","le","li","lo","lu","ma","me","mi","mo","mu","na","ne","ni","no","nu","on","or","os","ou","pa","pi","po","pu","ra","re","ri","ro","ru","sa","se","si","so","su","ta","te","ti","to","tu","un","us","ut","va","ve","vi","vo","vu","ya","yo",
    # 2 lettres EN
    "ab","ad","ae","ag","ah","ai","al","am","an","ar","at","aw","ax","ay","ba","be","bi","bo","by","de","do","ed","ef","eh","el","em","en","er","es","et","ex","fa","fe","go","ha","he","hi","hm","ho","id","if","in","is","it","jo","ka","ki","la","li","lo","ma","me","mi","mm","mo","mu","my","na","ne","no","nu","od","oe","of","oh","oi","ok","om","on","op","or","os","ow","ox","oy","pa","pe","pi","po","qi","re","sh","si","so","ta","ti","to","uh","um","un","up","us","ut","we","wo","xi","xu","ya","ye","yo",
    # Mots FR courants
    "able","abri","acte","aide","aile","aine","aire","ajar","alma","aloe","alte","alto","amen","ami","amie","amis","amour","an","ane","ange","anis","apre","arme","arte","as","aspe","asse","atom","atre","aube","aude","auge","auto","aveu","avion","avoir","axe","bac","bal","ban","bar","bas","beau","bec","bel","belle","bien","bier","bile","bleu","bloc","bois","bol","bon","bord","bote","botte","boue","bout","bras","bric","brin","brun","bue","cage","cal","camp","cane","cap","car","care","cari","case","cent","cepe","char","chat","chef","cher","chic","chien","chou","ciel","cite","clan","clip","clou","club","code","coeur","coin","col","come","cone","cor","core","cote","coup","cour","court","crac","cran","cric","cure","dame","dans","dard","date","demi","dent","deux","dire","disc","doge","doit","dome","done","dort","dose","dote","doue","drap","droit","dune","dure","eau","ecot","eden","edit","elan","emir","ente","epee","eros","espe","este","etat","ete","etre","euro","face","fade","fair","fait","fane","fare","fate","faut","fele","fente","fer","fete","feu","fier","file","film","fils","fine","fion","flan","flat","flic","flip","flot","flux","foie","fond","font","fore","fort","four","frac","frai","fret","gain","gale","gare","gars","gate","gaze","gene","gent","gite","glas","gode","goer","golf","gore","gout","grad","gras","gril","gris","grue","gue","guet","hale","halo","hate","have","heur","hier","hile","home","hors","hote","huge","hule","ile","inde","inet","iris","isle","issu","jade","jean","joli","joue","jour","juge","jupe","juré","lame","larc","lare","lard","lare","lase","laud","lent","lest","leur","lice","lieu","lime","lire","lise","lite","lobe","loge","loin","lore","lors","lote","loue","loup","lune","lure","mage","male","malt","mare","mars","mast","mate","mele","ment","mere","mine","mode","moue","mort","mule","narc","nard","nare","nase","nati","nette","noel","noir","nome","nord","note","nuit","nule","ocre","oeil","once","onde","open","oral","orge","orme","ours","pact","page","pale","paon","pare","part","pate","pave","peau","pele","pere","pied","pile","pine","pire","pise","plan","plat","plie","plot","pneu","pore","port","pose","pote","poux","prat","pres","prit","prix","puce","rade","rale","rame","ramp","rang","rape","rare","rase","rate","raue","reel","rein","rend","rent","repo","rice","ride","riel","rire","rite","robe","roco","rôle","roma","rude","ruse","sane","sang","sans","sard","saut","seau","sede","sele","sere","sete","seve","silo","sole","sore","sort","soue","sour","sous","stir","stop","suer","sure","tare","tart","taud","tele","teme","tend","tenu","tile","tire","toit","tome","tone","tore","tors","tort","trac","tram","trap","tres","trie","trio","trop","tube","tune","ture","type","ulce","unit","vale","vane","veau","vele","vend","vent","vere","vers","vide","viel","viel","vile","vine","vire","vite","voeu","voie","voir","vole","vote","voue","vrai","zero","zone",
    # Mots EN courants
    "able","acid","aged","also","area","army","away","back","ball","band","bank","base","bath","bear","beat","been","bell","best","bird","bite","blow","blue","boat","body","bold","bolt","bond","bone","book","bore","born","both","bowl","brat","brew","brim","burn","came","camp","cape","card","care","cart","case","cast","cave","cent","chad","char","chat","chin","chip","cite","clad","clam","clan","clap","clip","clod","clog","clot","club","clue","coal","coat","coil","cold","colt","come","cord","core","corn","cost","cram","crop","dart","data","date","deal","dean","dear","debt","deck","deed","deem","deer","deli","dent","diet","dirt","disc","dish","disk","dock","dole","dome","done","door","dorm","dote","down","drab","drag","dram","drat","draw","drip","drop","drum","dual","duel","dune","dupe","dust","earl","earn","east","edge","edit","else","emit","epic","even","ever","evil","exam","face","fact","fail","fair","fall","fame","fang","fare","farm","fast","fate","fear","feat","feel","fell","felt","fend","fern","file","fill","film","find","fine","fire","firm","fist","flag","flat","flaw","flea","fled","flew","flip","flit","flog","flow","foam","fold","folk","fond","food","fool","foot","ford","fore","fork","form","fort","foul","four","free","from","fuel","full","fume","gain","gale","game","gang","gate","gave","gaze","gear","geld","gent","germ","gild","girl","give","glad","gland","glee","glen","glib","glob","glue","goal","gold","golf","gone","good","gore","gown","grab","grad","gram","gray","grew","grid","grim","grin","grip","grit","grow","gulf","gust","hack","hale","half","hall","halt","hand","hang","hard","hare","harm","harp","hart","hate","have","heal","heap","heat","heel","held","helm","help","here","hero","hide","high","hike","hill","hint","hire","hold","hole","home","hood","hook","hope","horn","host","hour","hulk","hull","hump","hunt","hurt","idea","idle","inch","into","iron","isle","item","jabs","jade","jail","jams","jane","jars","jaws","jean","jeer","jibe","jilt","jive","joke","jolt","jot","jump","just","keel","keen","keep","kern","kick","kind","king","knob","knot","lace","lack","lame","lamp","land","lane","lard","lark","lash","last","late","lead","leaf","lean","leap","lend","lens","lest","liar","lice","lick","lied","lies","life","lift","like","lime","limp","line","link","lint","list","live","load","loam","lobe","lock","loft","lone","long","look","loom","lord","lore","lorn","lose","lost","loud","love","luck","made","mail","main","make","male","malt","mane","mare","mark","mart","mast","mate","mead","meal","mean","meat","meet","melt","mend","mere","mild","mile","milk","mill","mind","mine","mint","mire","miss","mist","moan","mole","molt","monk","mood","moon","moor","more","mort","most","move","muck","mule","must","nail","name","near","neck","need","next","nice","nick","nine","node","none","noon","norm","nose","note","null","oath","oboe","odds","once","open","oral","orca","orca","oven","over","pace","pack","page","paid","pain","pair","pale","palm","pane","park","part","past","path","peak","peel","peer","pelt","perm","pick","pier","pile","pine","pink","pipe","plan","play","plod","plot","plow","plum","plus","poem","poet","pole","poll","pond","pore","port","pose","post","pour","prey","prod","prop","pull","pump","pure","push","race","rack","raid","rail","rain","rake","ramp","rang","rank","rant","rapt","rate","read","real","reap","reel","rein","rely","rend","rent","rest","rice","rich","ride","rift","ring","riot","rise","risk","road","roam","roar","robe","rock","rode","role","roll","roof","room","root","rope","rose","rout","rude","ruin","rule","rump","rune","ruse","rush","rust","safe","sail","sake","sale","salt","same","sand","sane","sang","sank","sari","sate","save","scan","scar","seal","seam","sear","seat","self","send","shed","shin","ship","shoe","shop","shot","shun","shut","sick","side","sift","sign","silk","silo","silt","sing","sink","site","size","skid","skim","skin","skip","slab","slap","slat","slim","slip","slob","slop","slot","slum","slur","snag","snap","snob","snot","snow","soak","soar","sock","soil","sold","sole","some","song","soot","sore","sort","soul","soup","sour","span","spar","spin","spit","spot","spur","stab","stag","star","stay","stem","step","stir","stop","stub","stun","suck","suit","sulk","sung","sunk","sure","surf","swam","swan","swap","sway","swim","tail","tale","talk","tall","tame","tang","tank","tare","tart","teal","team","tear","teem","tell","tend","tent","term","than","that","them","then","they","thin","this","tide","tile","till","time","tire","toad","toil","told","toll","tome","tone","tong","tool","torn","toss","tour","town","trap","tray","tree","trim","trip","trod","true","tube","tuck","tuft","tune","tusk","twin","type","undo","upon","urge","used","vale","vane","vast","veil","vein","vent","verb","very","vest","vial","vice","view","vile","vine","void","volt","vow","wade","wage","wail","wake","walk","wall","wand","wane","ward","ware","warm","warn","warp","wart","wash","wave","weak","weal","wean","wear","weed","weld","went","west","when","whim","whip","wide","wild","will","wilt","wind","wine","wing","wink","wire","wise","wish","wisp","with","woke","wold","womb","wont","wood","wool","word","wore","work","worm","worn","wrap","wren","yell","your","zeal","zero","zinc","zone","zoom",
])

def normalize(text):
    text = text.lower().strip()
    return ''.join(
        c for c in unicodedata.normalize('NFD', text)
        if unicodedata.category(c) != 'Mn'
    )

def is_valid_word(word):
    w = normalize(word)
    if len(w) < 2:
        return False
    return w in DICTIONNAIRE

def can_form_word(word, letters):
    letters = list(normalize(letters))
    for c in normalize(word):
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
    "ABDNEATUER","SOMELICART","TNEPLIAMOS","RACEBOTINF",
    "DELACTIRMO","PATIOSNECR","FORMALBENIT","CASTLERIPON",
    "VITRACEOLMS","GRANDPOTILE","PLANETORIES","CARBONITEMS",
]

# ========== QUIZ DATA ==========
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
    {"q": "Quelle est la capitale du Nigeria ?", "a": "abuja"},
    {"q": "Quel est le fleuve le plus long du monde ?", "a": "nil"},
    {"q": "Quelle est la capitale du Bresil ?", "a": "brasilia"},
    {"q": "Quel pays a remporte la Coupe du Monde 2022 ?", "a": "argentine"},
    {"q": "Combien de joueurs dans une equipe de basket ?", "a": "5"},
    {"q": "Quelle est la capitale de l Espagne ?", "a": "madrid"},
    {"q": "Quelle est la capitale de l Allemagne ?", "a": "berlin"},
    {"q": "Quel pays a remporte la Coupe du Monde 2014 ?", "a": "allemagne"},
    {"q": "Combien de minutes dure un match de foot ?", "a": "90"},
    {"q": "Quelle est la capitale du Maroc ?", "a": "rabat"},
    {"q": "Quelle est la capitale du Ghana ?", "a": "accra"},
    {"q": "Quel pays a remporte la Coupe du Monde 2010 ?", "a": "espagne"},
    {"q": "Quel pays a remporte la Coupe du Monde 2006 ?", "a": "italie"},
    {"q": "Quel pays a remporte la Coupe du Monde 2002 ?", "a": "bresil"},
    {"q": "Qui a invente le telephone ?", "a": "graham bell"},
    {"q": "Quelle est la capitale du Japon ?", "a": "tokyo"},
    {"q": "Quelle est la capitale de la Chine ?", "a": "pekin"},
    {"q": "Combien d os dans le corps humain ?", "a": "206"},
    {"q": "Quel est l ocean le plus grand du monde ?", "a": "pacifique"},
    {"q": "Combien de pays en Afrique ?", "a": "54"},
    {"q": "Combien de secondes dans une heure ?", "a": "3600"},
    {"q": "Combien de jours dans une annee bissextile ?", "a": "366"},
    {"q": "Quel est le sport le plus populaire au monde ?", "a": "football"},
    {"q": "Combien de grammes dans un kilogramme ?", "a": "1000"},
    {"q": "Quel est le plus grand desert du monde ?", "a": "sahara"},
    {"q": "Combien de couleurs dans l arc en ciel ?", "a": "7"},
    {"q": "Quel animal est le symbole de la paix ?", "a": "colombe"},
    {"q": "Combien de metres dans un kilometre ?", "a": "1000"},
    {"q": "Quel est le plus grand pays d Afrique ?", "a": "algerie"},
    {"q": "Combien de joueurs dans une equipe de rugby ?", "a": "15"},
    {"q": "Qui a peint la Joconde ?", "a": "leonard de vinci"},
    {"q": "Combien de planetes dans le systeme solaire ?", "a": "8"},
    {"q": "Quel est le plus grand mammifere marin ?", "a": "baleine bleue"},
    {"q": "Combien de lettres dans l alphabet francais ?", "a": "26"},
    {"q": "Quel est le plus haut sommet du monde ?", "a": "everest"},
    {"q": "Combien de faces a un cube ?", "a": "6"},
    {"q": "Quel est le plus petit pays du monde ?", "a": "vatican"},
    {"q": "Combien de minutes dans une journee ?", "a": "1440"},
    {"q": "Quel est l element chimique de l eau ?", "a": "h2o"},
    {"q": "Combien de joueurs dans une equipe de volleyball ?", "a": "6"},
    {"q": "Quel est le plus grand continent ?", "a": "asie"},
    {"q": "Quel pays a la plus grande population au monde ?", "a": "inde"},
    {"q": "Quelle est la monnaie du Japon ?", "a": "yen"},
    {"q": "Quelle est la monnaie du Royaume Uni ?", "a": "livre sterling"},
    {"q": "Quelle est la monnaie des USA ?", "a": "dollar"},
    {"q": "Quel est le pays le plus peuple d Afrique ?", "a": "nigeria"},
    {"q": "Combien de zeros dans un million ?", "a": "6"},
    {"q": "Quel club a gagne le plus de Champions League ?", "a": "real madrid"},
    {"q": "En quelle annee a ete cree Facebook ?", "a": "2004"},
    {"q": "Qui a fonde Apple ?", "a": "steve jobs"},
    {"q": "En quelle annee a ete lance le premier iPhone ?", "a": "2007"},
    {"q": "Quel est le vrai nom de Pelé ?", "a": "edson arantes do nascimento"},
    {"q": "Dans quel pays est ne Cristiano Ronaldo ?", "a": "portugal"},
    {"q": "Dans quel pays est ne Lionel Messi ?", "a": "argentine"},
    {"q": "Quel est le surnom de Neymar ?", "a": "ney"},
    {"q": "Combien de grammes dans une tonne ?", "a": "1000000"},
    {"q": "Quelle est la vitesse de la lumiere en km/s ?", "a": "300000"},
    {"q": "Qui a invente l ampoule electrique ?", "a": "thomas edison"},
    {"q": "En quelle annee l homme a marche sur la lune ?", "a": "1969"},
    {"q": "Quel est le plus grand ocean du monde ?", "a": "pacifique"},
    {"q": "Combien de dents a un adulte ?", "a": "32"},
    {"q": "Quelle est la plus haute montagne d Afrique ?", "a": "kilimandjaro"},
    {"q": "Quel est le plus long fleuve du monde ?", "a": "nil"},
    {"q": "En quelle annee a commence la Premiere Guerre Mondiale ?", "a": "1914"},
    {"q": "En quelle annee a commence la Deuxieme Guerre Mondiale ?", "a": "1939"},
    {"q": "Quel pays a invente le football ?", "a": "angleterre"},
    {"q": "Combien de joueurs dans une equipe de handball ?", "a": "7"},
    {"q": "Combien de sets dans un match de tennis grand chelem ?", "a": "5"},
    {"q": "Quel est le record du monde du 100m ?", "a": "9.58"},
    {"q": "Qui detient le record du monde du 100m ?", "a": "usain bolt"},
    {"q": "Dans quel pays se trouve la Tour Eiffel ?", "a": "france"},
    {"q": "Dans quel pays se trouve Big Ben ?", "a": "angleterre"},
    {"q": "Dans quel pays se trouve la Statue de la Liberte ?", "a": "usa"},
    {"q": "Dans quel pays se trouve le Colisee ?", "a": "italie"},
    {"q": "Quelle est la capitale de l Egypte ?", "a": "le caire"},
    {"q": "Combien d etoiles sur le drapeau americain ?", "a": "50"},
    {"q": "Quel est le plus grand lac du monde ?", "a": "mer caspienne"},
    {"q": "Combien de joueurs dans une equipe de baseball ?", "a": "9"},
    {"q": "Qui a compose la 5eme symphonie ?", "a": "beethoven"},
    {"q": "Dans quel pays se trouve le Machu Picchu ?", "a": "perou"},
    {"q": "Quelle est la monnaie de l Europe ?", "a": "euro"},
    {"q": "Quel est l os le plus long du corps humain ?", "a": "femur"},
    {"q": "Combien de doigts a une main ?", "a": "5"},
    {"q": "Quel animal a le plus long cou ?", "a": "girafe"},
    {"q": "Quel est le seul mammifere qui peut voler ?", "a": "chauve souris"},
]

# Sessions
jumble_sessions = {}
quiz_sessions = {}
quiz_used_questions = {}

# ========== CITY TIMEZONES ==========
CITY_TIMEZONES = {
    "london": "Europe/London", "angleterre": "Europe/London", "uk": "Europe/London",
    "paris": "Europe/Paris", "france": "Europe/Paris",
    "tokyo": "Asia/Tokyo", "japon": "Asia/Tokyo",
    "dubai": "Asia/Dubai", "eau": "Asia/Dubai",
    "lagos": "Africa/Lagos", "nigeria": "Africa/Lagos", "abuja": "Africa/Lagos",
    "dakar": "Africa/Dakar", "senegal": "Africa/Dakar",
    "abidjan": "Africa/Abidjan", "cote d ivoire": "Africa/Abidjan",
    "casablanca": "Africa/Casablanca", "maroc": "Africa/Casablanca", "rabat": "Africa/Casablanca",
    "nairobi": "Africa/Nairobi", "kenya": "Africa/Nairobi",
    "cairo": "Africa/Cairo", "egypte": "Africa/Cairo", "le caire": "Africa/Cairo",
    "berlin": "Europe/Berlin", "allemagne": "Europe/Berlin",
    "madrid": "Europe/Madrid", "espagne": "Europe/Madrid",
    "rome": "Europe/Rome", "italie": "Europe/Rome",
    "moscou": "Europe/Moscow", "moscow": "Europe/Moscow", "russie": "Europe/Moscow",
    "beijing": "Asia/Shanghai", "chine": "Asia/Shanghai", "pekin": "Asia/Shanghai",
    "sydney": "Australia/Sydney", "australie": "Australia/Sydney",
    "kinshasa": "Africa/Kinshasa", "rdc": "Africa/Kinshasa", "congo": "Africa/Kinshasa",
    "accra": "Africa/Accra", "ghana": "Africa/Accra",
    "new york": "America/New_York", "usa": "America/New_York", "etats unis": "America/New_York",
    "los angeles": "America/Los_Angeles", "miami": "America/New_York",
    "montreal": "America/Toronto", "canada": "America/Toronto", "toronto": "America/Toronto",
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
    "brazzaville": "Africa/Brazzaville", "congo brazza": "Africa/Brazzaville",
    "ndjamena": "Africa/Ndjamena", "tchad": "Africa/Ndjamena",
    "johannesburg": "Africa/Johannesburg", "afrique du sud": "Africa/Johannesburg",
    "lisbonne": "Europe/Lisbon", "portugal": "Europe/Lisbon",
    "amsterdam": "Europe/Amsterdam", "pays bas": "Europe/Amsterdam",
    "bruxelles": "Europe/Brussels", "belgique": "Europe/Brussels",
    "berne": "Europe/Zurich", "suisse": "Europe/Zurich", "geneve": "Europe/Zurich",
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
    "ankara": "Europe/Istanbul", "turquie": "Europe/Istanbul", "istanbul": "Europe/Istanbul",
    "athenes": "Europe/Athens", "grece": "Europe/Athens",
    "harare": "Africa/Harare", "zimbabwe": "Africa/Harare",
}

# ========== FOOTBALL API ==========
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
        resp = requests.get(url, headers=headers, timeout=10)
        data = resp.json()
        matches = data.get("matches", [])
        if not matches:
            # Chercher les matchs du jour
            url2 = f"https://api.football-data.org/v4/competitions/{league_id}/matches?status=IN_PLAY,PAUSED,HALFTIME"
            resp2 = requests.get(url2, headers=headers, timeout=10)
            data2 = resp2.json()
            matches = data2.get("matches", [])
        return matches
    except Exception as e:
        return None

def format_matches(matches, league_name):
    if matches is None:
        return f"{league_name}\n\nErreur de connexion. Reessayez."
    if not matches:
        return f"{league_name}\n\nPas de match en direct en ce moment."
    lines = [f"{league_name} - EN DIRECT\n"]
    for m in matches[:8]:
        home = m["homeTeam"]["shortName"] or m["homeTeam"]["name"]
        away = m["awayTeam"]["shortName"] or m["awayTeam"]["name"]
        score = m.get("score", {})
        full = score.get("fullTime", {})
        home_score = full.get("home", "?")
        away_score = full.get("away", "?")
        minute = m.get("minute", "")
        min_str = f" {minute}'" if minute else ""
        lines.append(f"{home} {home_score} - {away_score} {away}{min_str}")
    return "\n".join(lines)

# ========== COMMANDES ==========
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Bienvenue sur DutaBot!\n\n"
        "Commandes:\n\n"
        "/jumble - Formez le max de mots en 30s\n"
        "/quiz - Question avec chrono 30s\n"
        "/score - Votre score\n"
        "/top - Classement general\n"
        "/time paris - Heure dans un pays\n"
        "/foot - Scores de foot en direct\n\n"
        "Bonne chance!"
    )

async def jumble(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    letters = random.choice(JUMBLE_SETS)
    jumble_sessions[user_id] = {"letters": letters, "found_words": [], "active": True}
    await update.message.reply_text(
        f"JUMBLE! Vous avez 30 secondes!\n\n"
        f"Lettres: >>> {letters} <<<\n\n"
        f"Formez le max de mots!\n"
        f"Mot valide = ✅ +1 point\n"
        f"Mot invalide = ❌\n\n"
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
                text="Temps ecoule! Aucun mot valide trouve.\n/jumble pour reessayer!"
            )
        del jumble_sessions[user_id]

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
            text=f"Temps ecoule!\nLa reponse etait: {correct.upper()}\n\n/quiz pour continuer!"
        )

async def score(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    s = get_user_score(user_id)
    name = update.effective_user.first_name
    await update.message.reply_text(f"Votre score:\n\n{name}: {s} points")

async def top(update: Update, context: ContextTypes.DEFAULT_TYPE):
    scores = load_scores()
    if not scores:
        await update.message.reply_text("Aucun joueur enregistre!")
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
        await update.message.reply_text("Usage: /time paris\nEx: /time cameroun, /time london")
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
            f"'{city}' non trouve.\nEx: /time paris, /time cameroun, /time dakar, /time london"
        )
        return
    tz = pytz.timezone(tz_name)
    now = datetime.now(tz)
    await update.message.reply_text(
        f"Heure a {city.title()}:\n"
        f"{now.strftime('%H:%M')} - {now.strftime('%d/%m/%Y')}"
    )

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
        await query.edit_message_text("Championnat non trouve.")
        return
    league_id, league_name = league_data
    await query.edit_message_text(f"Recherche des matchs en direct pour {league_name}...")
    matches = get_live_scores(league_id)
    result = format_matches(matches, league_name)
    await query.edit_message_text(result)

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
        if not can_form_word(text_norm, normalize(letters)):
            await update.message.reply_text(f"❌ '{text}' - Impossible avec ces lettres!")
            return
        if is_valid_word(text):
            found.append(text)
            await update.message.reply_text(f"✅ '{text}' - Valide! {len(found)} mot(s)!")
        else:
            await update.message.reply_text(f"❌ '{text}' - Mot non reconnu!")
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
                f"✅ Correct!\n+15 points! Score: {s} pts\n\n/quiz pour continuer!"
            )
        else:
            await update.message.reply_text("❌ Mauvaise reponse! Essayez encore!")
        return

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
