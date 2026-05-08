# -*- coding: utf-8 -*-
import logging
import random
import json
import os
import unicodedata
import asyncio
import requests
import time
from datetime import datetime, date
import pytz
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes

TOKEN = 8272954567:AAG3vHRWr3zD-gI-i1PiVx-iejskLBWVJZI"
FOOTBALL_API_KEY = "4b559620c705450f958b5fb0548ab6d3"
WEATHER_API_KEY = "bd5e378503939ddaee76f12ad7a97608"  # OpenWeatherMap gratuit
SCORES_FILE = "scores.json"
logging.basicConfig(level=logging.INFO)

# ========== PAYS DU MONDE ENTIER ==========
COUNTRIES = {
    # Afrique de l'Ouest
    "🇨🇲 Cameroun": "CM", "🇸🇳 Sénégal": "SN", "🇨🇮 Côte d'Ivoire": "CI",
    "🇳🇬 Nigeria": "NG", "🇬🇭 Ghana": "GH", "🇲🇱 Mali": "ML",
    "🇧🇫 Burkina Faso": "BF", "🇹🇬 Togo": "TG", "🇧🇯 Bénin": "BJ",
    "🇳🇪 Niger": "NE", "🇬🇳 Guinée": "GN", "🇸🇱 Sierra Leone": "SL",
    "🇱🇷 Liberia": "LR", "🇬🇲 Gambie": "GM", "🇬🇼 Guinée-Bissau": "GW",
    "🇨🇻 Cap-Vert": "CV", "🇲🇷 Mauritanie": "MR",
    # Afrique Centrale
    "🇨🇬 Congo": "CG", "🇨🇩 RDC": "CD", "🇬🇦 Gabon": "GA",
    "🇨🇫 RCA": "CF", "🇹🇩 Tchad": "TD", "🇬🇶 Guinée Équatoriale": "GQ",
    "🇸🇹 São Tomé": "ST",
    # Afrique de l'Est
    "🇰🇪 Kenya": "KE", "🇹🇿 Tanzanie": "TZ", "🇺🇬 Ouganda": "UG",
    "🇷🇼 Rwanda": "RW", "🇧🇮 Burundi": "BI", "🇪🇹 Éthiopie": "ET",
    "🇸🇴 Somalie": "SO", "🇩🇯 Djibouti": "DJ", "🇪🇷 Érythrée": "ER",
    "🇸🇸 Soudan du Sud": "SS", "🇸🇩 Soudan": "SD",
    # Afrique du Nord
    "🇲🇦 Maroc": "MA", "🇩🇿 Algérie": "DZ", "🇹🇳 Tunisie": "TN",
    "🇱🇾 Libye": "LY", "🇪🇬 Égypte": "EG",
    # Afrique Australe
    "🇿🇦 Afrique du Sud": "ZA", "🇿🇼 Zimbabwe": "ZW", "🇿🇲 Zambie": "ZM",
    "🇲🇼 Malawi": "MW", "🇲🇿 Mozambique": "MZ", "🇧🇼 Botswana": "BW",
    "🇳🇦 Namibie": "NA", "🇸🇿 Eswatini": "SZ", "🇱🇸 Lesotho": "LS",
    "🇦🇴 Angola": "AO", "🇲🇬 Madagascar": "MG", "🇲🇺 Maurice": "MU",
    "🇸🇨 Seychelles": "SC", "🇰🇲 Comores": "KM",
    # Europe
    "🇫🇷 France": "FR", "🇧🇪 Belgique": "BE", "🇨🇭 Suisse": "CH",
    "🇱🇺 Luxembourg": "LU", "🇩🇪 Allemagne": "DE", "🇬🇧 Royaume-Uni": "GB",
    "🇪🇸 Espagne": "ES", "🇵🇹 Portugal": "PT", "🇮🇹 Italie": "IT",
    "🇳🇱 Pays-Bas": "NL", "🇦🇹 Autriche": "AT", "🇸🇪 Suède": "SE",
    "🇳🇴 Norvège": "NO", "🇩🇰 Danemark": "DK", "🇫🇮 Finlande": "FI",
    "🇵🇱 Pologne": "PL", "🇷🇴 Roumanie": "RO", "🇷🇺 Russie": "RU",
    "🇺🇦 Ukraine": "UA", "🇬🇷 Grèce": "GR", "🇹🇷 Turquie": "TR",
    "🇨🇿 Tchéquie": "CZ", "🇭🇺 Hongrie": "HU", "🇸🇰 Slovaquie": "SK",
    "🇭🇷 Croatie": "HR", "🇷🇸 Serbie": "RS", "🇧🇬 Bulgarie": "BG",
    "🇮🇪 Irlande": "IE", "🇮🇸 Islande": "IS",
    # Amérique du Nord
    "🇺🇸 États-Unis": "US", "🇨🇦 Canada": "CA", "🇲🇽 Mexique": "MX",
    # Amérique Centrale & Caraïbes
    "🇬🇹 Guatemala": "GT", "🇭🇳 Honduras": "HN", "🇸🇻 Salvador": "SV",
    "🇳🇮 Nicaragua": "NI", "🇨🇷 Costa Rica": "CR", "🇵🇦 Panama": "PA",
    "🇨🇺 Cuba": "CU", "🇭🇹 Haïti": "HT", "🇩🇴 Rép. Dominicaine": "DO",
    "🇯🇲 Jamaïque": "JM", "🇹🇹 Trinidad": "TT",
    # Amérique du Sud
    "🇧🇷 Brésil": "BR", "🇦🇷 Argentine": "AR", "🇨🇴 Colombie": "CO",
    "🇻🇪 Venezuela": "VE", "🇵🇪 Pérou": "PE", "🇨🇱 Chili": "CL",
    "🇪🇨 Équateur": "EC", "🇧🇴 Bolivie": "BO", "🇵🇾 Paraguay": "PY",
    "🇺🇾 Uruguay": "UY", "🇬🇾 Guyana": "GY", "🇸🇷 Suriname": "SR",
    # Asie
    "🇨🇳 Chine": "CN", "🇯🇵 Japon": "JP", "🇰🇷 Corée du Sud": "KR",
    "🇮🇳 Inde": "IN", "🇵🇰 Pakistan": "PK", "🇧🇩 Bangladesh": "BD",
    "🇮🇩 Indonésie": "ID", "🇲🇾 Malaisie": "MY", "🇸🇬 Singapour": "SG",
    "🇹🇭 Thaïlande": "TH", "🇻🇳 Vietnam": "VN", "🇵🇭 Philippines": "PH",
    "🇸🇦 Arabie Saoudite": "SA", "🇦🇪 Émirats": "AE", "🇶🇦 Qatar": "QA",
    "🇮🇷 Iran": "IR", "🇮🇶 Irak": "IQ", "🇸🇾 Syrie": "SY",
    "🇱🇧 Liban": "LB", "🇯🇴 Jordanie": "JO", "🇮🇱 Israël": "IL",
    "🇰🇼 Koweït": "KW", "🇧🇭 Bahreïn": "BH", "🇴🇲 Oman": "OM",
    "🇾🇪 Yémen": "YE", "🇦🇫 Afghanistan": "AF", "🇳🇵 Népal": "NP",
    "🇱🇰 Sri Lanka": "LK", "🇲🇲 Myanmar": "MM", "🇰🇭 Cambodge": "KH",
    "🇲🇳 Mongolie": "MN",
    # Océanie
    "🇦🇺 Australie": "AU", "🇳🇿 Nouvelle-Zélande": "NZ", "🇫🇯 Fidji": "FJ",
    # Autre
    "🌍 Autre": "XX",
}

# Groupes de pays pour l'affichage en pages
COUNTRY_PAGES = [
    # Page 1 - Afrique de l'Ouest
    ["🇨🇲 Cameroun","🇸🇳 Sénégal","🇨🇮 Côte d'Ivoire","🇳🇬 Nigeria","🇬🇭 Ghana","🇲🇱 Mali","🇧🇫 Burkina Faso","🇹🇬 Togo","🇧🇯 Bénin","🇳🇪 Niger","🇬🇳 Guinée","🇲🇷 Mauritanie"],
    # Page 2 - Afrique Centrale & Est
    ["🇨🇬 Congo","🇨🇩 RDC","🇬🇦 Gabon","🇨🇫 RCA","🇹🇩 Tchad","🇬🇶 Guinée Équatoriale","🇰🇪 Kenya","🇹🇿 Tanzanie","🇺🇬 Ouganda","🇷🇼 Rwanda","🇧🇮 Burundi","🇪🇹 Éthiopie"],
    # Page 3 - Afrique du Nord & Australe
    ["🇲🇦 Maroc","🇩🇿 Algérie","🇹🇳 Tunisie","🇱🇾 Libye","🇪🇬 Égypte","🇿🇦 Afrique du Sud","🇿🇼 Zimbabwe","🇿🇲 Zambie","🇲🇿 Mozambique","🇦🇴 Angola","🇲🇬 Madagascar","🇸🇩 Soudan"],
    # Page 4 - Europe
    ["🇫🇷 France","🇧🇪 Belgique","🇨🇭 Suisse","🇱🇺 Luxembourg","🇩🇪 Allemagne","🇬🇧 Royaume-Uni","🇪🇸 Espagne","🇵🇹 Portugal","🇮🇹 Italie","🇳🇱 Pays-Bas","🇸🇪 Suède","🇷🇺 Russie"],
    # Page 5 - Amériques
    ["🇺🇸 États-Unis","🇨🇦 Canada","🇲🇽 Mexique","🇧🇷 Brésil","🇦🇷 Argentine","🇨🇴 Colombie","🇻🇪 Venezuela","🇵🇪 Pérou","🇨🇱 Chili","🇭🇹 Haïti","🇩🇴 Rép. Dominicaine","🇨🇺 Cuba"],
    # Page 6 - Asie & Océanie
    ["🇨🇳 Chine","🇯🇵 Japon","🇰🇷 Corée du Sud","🇮🇳 Inde","🇸🇦 Arabie Saoudite","🇦🇪 Émirats","🇶🇦 Qatar","🇮🇩 Indonésie","🇸🇬 Singapour","🇹🇭 Thaïlande","🇦🇺 Australie","🌍 Autre"],
]

PAGE_TITLES = [
    "Afrique de l'Ouest",
    "Afrique Centrale & Est",
    "Afrique du Nord & Australe",
    "Europe",
    "Amériques",
    "Asie & Océanie",
]

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

FALLBACK_DICT = set(normalize(w) for w in ['ah','ai','an','as','au','ba','be','bi','bo','bu','ca','ce','ci','da','de','du','eh','el','em','en','er','es','et','eu','ex','fa','fi','go','ha','hi','ho','il','in','je','la','le','li','lo','lu','ma','me','mi','mo','mu','na','ne','ni','no','nu','on','or','os','ou','pa','pi','po','pu','ra','re','ri','ro','ru','sa','se','si','so','su','ta','te','ti','to','tu','un','us','va','ve','vi','vo','vu','ya','yo','ab','ad','ag','al','am','ar','at','aw','ax','ay','by','do','ed','ef','he','id','if','is','it','jo','ka','ki','my','of','oh','oi','ok','om','op','ow','ox','oy','pe','qi','sh','uh','um','up','we','wo','xi','xu','ye','lit','lits','met','mets','mis','mot','mots','lot','lots','rot','pot','pots','mer','fer','ver','vert','net','set','jet','pet','bet','art','part','car','bar','can','ban','fan','man','ran','tan','van','pan','cap','map','nap','rap','tap','cat','bat','fat','hat','mat','pat','rat','sat','bad','had','lad','mad','sad','bag','lag','nag','rag','sag','tag','bit','fit','hit','kit','pit','sit','wit','bog','cog','dog','fog','hog','jog','log','bon','con','don','ion','son','ton','bug','dug','jug','mug','pug','rug','tug','bun','fun','gun','nun','pun','run','sun','but','cut','gut','hut','nut','put','rut','able','acte','aide','aile','ami','amie','ane','ange','arme','aube','auto','beau','bien','bleu','bloc','bois','bon','bord','bout','bras','cage','camp','case','cent','char','chat','chef','cher','ciel','cite','clan','clou','club','code','coin','cone','cote','coup','cran','cure','dame','date','demi','dent','deux','dire','dome','dose','drap','dune','dure','edit','elan','etat','etre','euro','face','fait','file','film','fils','fine','flot','foie','fond','fort','four','gain','gale','gare','gate','gaze','gene','gite','golf','gout','gras','gris','hale','halo','hate','hier','home','hors','hote','ile','jade','jean','joli','joue','jour','juge','jupe','lame','lard','lent','lest','leur','lieu','lime','lire','lobe','loge','loin','lors','loue','loup','lune','male','malt','mare','mars','mate','mere','mine','mode','mort','mule','noel','noir','note','nuit','once','onde','oral','orge','ours','page','pale','pare','part','pate','peau','pere','pied','pile','pine','pire','plan','plat','plie','pore','port','pose','prix','puce','rade','rale','rame','rang','rape','rare','rase','rate','reel','rein','rent','ride','rire','rite','robe','role','rude','ruse','sang','sans','saut','seau','sere','seve','silo','sole','sort','sous','stop','sure','tare','tele','tend','tenu','tire','toit','tome','tone','tore','tort','trac','tram','trap','tres','trio','trop','tube','tune','type','vale','vane','veau','vent','vers','vide','vile','vine','vite','voie','voir','vole','vote','vrai','zero','zone','able','acid','also','area','army','away','back','ball','band','bank','base','bath','bear','beat','bell','best','bird','bite','blow','blue','boat','body','bold','bolt','bond','bone','book','bore','born','bowl','burn','came','camp','cape','card','care','cart','case','cast','cave','cent','char','chat','chin','chip','clan','clap','clip','clot','club','clue','coal','coat','coil','cold','come','cord','core','corn','cost','crop','dart','data','date','deal','dear','debt','deck','dent','diet','dirt','disc','dish','dome','done','door','down','drag','draw','drip','drop','drum','duel','dune','dust','earn','east','edge','edit','epic','even','ever','evil','face','fact','fail','fair','fall','fame','fare','farm','fast','fate','fear','feat','feel','fell','felt','fern','file','fill','film','find','fine','fire','firm','fist','flag','flat','flaw','fled','flip','flow','foam','fold','fond','food','fool','foot','ford','fore','fork','form','fort','foul','four','free','fuel','full','gain','gale','game','gang','gate','gave','gaze','gear','gent','germ','girl','give','glad','glob','glue','goal','gold','golf','gone','good','gore','gown','grab','gram','gray','grew','grid','grim','grin','grip','grit','grow','gulf','gust','hack','hale','half','hall','halt','hand','hang','hard','hare','harm','harp','hate','have','heal','heap','heat','heel','held','helm','help','here','hero','hide','high','hike','hill','hint','hire','hold','hole','home','hood','hook','hope','horn','host','hour','hull','hunt','hurt','idea','idle','inch','into','iron','isle','item','jade','jail','jaws','jean','joke','jolt','jump','just','keen','keep','kick','kind','king','knot','lace','lack','lame','lamp','land','lane','lard','lark','lash','last','late','lead','leaf','lean','leap','lend','lens','lest','liar','lick','life','lift','like','lime','limp','line','link','lint','list','live','load','lobe','lock','loft','lone','long','look','loom','lord','lose','lost','loud','love','luck','made','mail','main','make','male','malt','mane','mare','mark','mast','mate','meal','mean','meat','meet','melt','mend','mere','mild','mile','milk','mill','mind','mine','mint','mire','miss','mist','moan','mole','mood','moon','moor','more','most','move','muck','mule','must','nail','name','near','neck','need','next','nice','nick','node','none','noon','norm','nose','note','once','open','oral','oven','over','pace','pack','page','pain','pair','pale','palm','pane','park','part','past','path','peak','peel','peer','pick','pier','pile','pine','pink','pipe','plan','play','plot','plum','plus','poem','pole','poll','pond','pore','port','pose','post','pour','prey','prop','pull','pump','pure','push','race','rack','raid','rail','rain','rake','ramp','rang','rank','rant','rate','read','real','reap','reel','rein','rely','rend','rent','rest','rice','rich','ride','ring','riot','rise','risk','road','roam','roar','robe','rock','rode','role','roll','roof','room','root','rope','rose','rude','ruin','rule','rune','ruse','rush','rust','safe','sail','sake','sale','salt','same','sand','sane','sang','save','seal','seam','seat','self','send','shin','ship','shoe','shop','shot','shut','sick','side','sign','silk','sing','sink','site','size','skin','skip','slab','slap','slim','slip','slot','snap','snow','soak','sock','soil','sold','sole','some','song','sore','sort','soul','soup','sour','span','spin','spit','spot','stag','star','stay','stem','step','stir','stop','stun','suck','suit','sung','sure','surf','swan','swap','swim','tail','tale','talk','tall','tame','tank','tart','team','tear','tell','tend','tent','term','thin','tide','tile','till','time','tire','toad','toil','told','toll','tome','tone','tool','torn','toss','tour','town','trap','tray','tree','trim','trip','true','tube','tuck','tune','twin','type','upon','urge','used','vale','vane','vast','veil','vein','vent','verb','very','vest','vice','view','vile','vine','void','wade','wage','wake','walk','wall','wand','wane','ward','ware','warm','warn','wash','wave','weak','wear','weed','went','wide','wild','will','wind','wine','wing','wire','wise','wish','woke','wood','wool','word','wore','work','worm','worn','wrap','yell','zero','zinc','zone','zoom'])

# Mots supplementaires tres courants FR+EN souvent manques
EXTRA_WORDS = set(normalize(w) for w in [
    # FR basiques
    'mer','mers','fer','fers','ver','vers','vert','verts','net','nets',
    'set','sets','jet','jets','pet','pets','met','mets','bet','bets',
    'art','arts','part','parts','car','cars','bar','bars','far','jar',
    'jars','tar','tars','can','cans','ban','bans','fan','fans','man',
    'ran','tan','van','vans','pan','pans','cap','caps','map','maps',
    'nap','naps','rap','raps','sap','tap','taps','cat','cats','bat',
    'bats','fat','hat','hats','mat','mats','pat','pats','rat','rats',
    'sat','vat','bad','dad','had','lad','mad','sad','bag','gag','lag',
    'nag','rag','sag','tag','wag','bit','fit','hit','kit','pit','sit',
    'wit','bog','cog','dog','fog','hog','jog','log','tog','bon','con',
    'don','ion','son','ton','won','bud','mud','bug','dug','jug','mug',
    'pug','rug','tug','bun','fun','gun','nun','pun','run','sun','bus',
    'but','cut','gut','hut','jut','nut','put','rut','cab','dab','gab',
    'jab','lab','tab','cad','gal','gap','gar','gel','gin','gnu','got',
    'gou','lac','lai','lan','las','lat','lob','log','lot','lue','lui',
    'mac','mas','max','mil','mis','mit','mob','mod','moi','mol','mon',
    'mot','mou','nag','nez','nid','nil','nob','nom','non','nos','not',
    'nou','nue','nue','oie','ole','omi','ont','ora','ore','ors','ose',
    'ouf','our','pad','par','pat','pec','pen','per','peu','pic','pin',
    'pio','pit','pix','pli','poc','poi','pol','pop','pro','pub','pue',
    'put','raz','rec','ref','rem','rep','res','rev','rie','rif','rin',
    'rip','riz','roi','ros','rue','rut','sac','sas','sau','sec','sel',
    'sen','sep','sex','ski','sol','som','son','sot','sou','sud','sue',
    'sus','tac','tap','tan','tas','tau','tex','tic','tir','ton','top',
    'tot','tou','tri','tub','tue','val','van','var','vas','vic','vin',
    'vis','vit','vol','wok','yak','zoo',
    # EN basiques souvent manques
    'lit','bit','fit','hit','kit','pit','sit','wit','lot','cot','dot',
    'got','hot','jot','not','pot','rot','tot','met','set','net','bet',
    'get','jet','let','pet','vet','wet','yet','cut','but','gut','hut',
    'nut','put','rut','map','cap','gap','lap','nap','rap','sap','tap',
    'zap','mat','bat','cat','fat','hat','pat','rat','sat','vat','bad',
    'had','lad','mad','sad','bag','lag','nag','rag','sag','tag','bin',
    'fin','gin','kin','pin','sin','tin','win','bog','cog','dog','fog',
    'hog','jog','log','bud','mud','bug','dug','jug','mug','pug','rug',
    'tug','bun','fun','gun','nun','pun','run','sun','bus','cab','dab',
    'gab','jab','lab','tab','lid','bid','did','hid','kid','rid','cod',
    'god','mod','nod','rod','sob','bob','cob','fob','gob','job','lob',
    'mob','rob','cub','dub','hub','pub','rub','sub','ego','era','eve',
    'ire','oak','oar','oat','odd','ode','oil','old','ore','our','out',
    'own','pad','pal','paw','pay','pig','pit','ply','pod','pro','pry',
    'pub','pug','pun','pup','pus','ram','raw','ray','ref','rep','rev',
    'rib','rid','rim','rip','rob','rot','row','rub','rug','rum','rut',
    'rye','sad','sag','sap','sat','saw','say','sea','shy','sin','sip',
    'sir','ski','sky','sly','sob','sod','son','sow','soy','spa','spy',
    'sty','sub','sue','sum','sun','sup','tab','tan','tap','tar','tat',
    'tax','thy','tie','tin','tip','toe','ton','too','top','toy','try',
    'tub','tug','tun','two','urn','use','van','vat','via','vie','vim',
    'vow','wad','war','was','wax','way','web','wed','wig','win','wit',
    'woe','wok','won','woo','wow','yam','yap','yaw','yep','yes','yet',
    'yew','you','zap','zed','zen','zig','zip','zoo',
])

def is_valid_word(word):
    w = normalize(word)
    return w in FALLBACK_DICT or w in EXTRA_WORDS

def load_scores():
    if os.path.exists(SCORES_FILE):
        with open(SCORES_FILE, "r") as f:
            return json.load(f)
    return {}

def save_scores(scores):
    with open(SCORES_FILE, "w") as f:
        json.dump(scores, f, ensure_ascii=False)

def add_score(user_id, username, points, country_code=None):
    scores = load_scores()
    uid = str(user_id)
    if uid not in scores:
        scores[uid] = {"username": username, "score": 0, "country": country_code or "XX", "last_bonus": ""}
    scores[uid]["score"] += points
    scores[uid]["username"] = username
    if country_code:
        scores[uid]["country"] = country_code
    save_scores(scores)

def get_user_score(user_id):
    scores = load_scores()
    return scores.get(str(user_id), {}).get("score", 0)

def get_user_country(user_id):
    scores = load_scores()
    return scores.get(str(user_id), {}).get("country", None)

def get_country_flag(code):
    """Retourne le drapeau emoji depuis le code pays"""
    for name, c in COUNTRIES.items():
        if c == code:
            parts = name.strip().split(" ")
            return parts[0]  # emoji drapeau
    return "🌍"

def get_country_name(code):
    """Retourne le nom complet depuis le code pays"""
    for name, c in COUNTRIES.items():
        if c == code:
            return name
    return "🌍 Inconnu"

JUMBLE_SETS = ['ABDNEATUER','SOMELICART','TNEPLIAMOS','RACEBOTINF','DELACTIRMO','PATIOSNECR','FORMALBENIT','CASTLERIPON','VITRACEOLMS','GRANDPOTILE','PLANETORIES','CARBONITEMS']

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
QUIZ_USED_FILE = "quiz_used.json"

def load_quiz_used():
    if os.path.exists(QUIZ_USED_FILE):
        with open(QUIZ_USED_FILE, "r") as f:
            return json.load(f)
    return {}

def save_quiz_used(data):
    with open(QUIZ_USED_FILE, "w") as f:
        json.dump(data, f)
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
    "new york": "America/New_York", "usa": "America/New_York",
    "canada": "America/Toronto", "toronto": "America/Toronto", "montreal": "America/Toronto",
    "yaounde": "Africa/Douala", "douala": "Africa/Douala", "cameroun": "Africa/Douala",
    "tunis": "Africa/Tunis", "tunisie": "Africa/Tunis",
    "alger": "Africa/Algiers", "algerie": "Africa/Algiers",
    "bamako": "Africa/Bamako", "mali": "Africa/Bamako",
    "lome": "Africa/Lome", "togo": "Africa/Lome",
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
        matches = requests.get(f"https://api.football-data.org/v4/competitions/{league_id}/matches?status=LIVE", headers=headers, timeout=10).json().get("matches", [])
        if not matches:
            matches = requests.get(f"https://api.football-data.org/v4/competitions/{league_id}/matches?status=IN_PLAY,PAUSED,HALFTIME", headers=headers, timeout=10).json().get("matches", [])
        return matches
    except:
        return None

def format_matches(matches, league_name):
    if matches is None:
        return f"{league_name}\n\nErreur de connexion."
    if not matches:
        return f"{league_name}\n\nPas d evenement en ce moment."
    lines = [f"{league_name} - EN DIRECT\n"]
    for m in matches[:8]:
        home = m["homeTeam"].get("shortName") or m["homeTeam"]["name"]
        away = m["awayTeam"].get("shortName") or m["awayTeam"]["name"]
        full = m.get("score", {}).get("fullTime", {})
        hs = full.get("home")
        as_ = full.get("away")
        if hs is None:
            half = m.get("score", {}).get("halfTime", {})
            hs = half.get("home", "?")
            as_ = half.get("away", "?")
        lines.append(f"{home} {hs} - {as_} {away}")
    return "\n".join(lines)

def get_weather(city):
    try:
        url = f"http://api.openweathermap.org/data/2.5/weather"
        params = {"q": city, "appid": WEATHER_API_KEY, "units": "metric", "lang": "fr"}
        resp = requests.get(url, params=params, timeout=5)
        data = resp.json()
        if resp.status_code != 200:
            return None
        desc = data["weather"][0]["description"].capitalize()
        temp = round(data["main"]["temp"])
        feels = round(data["main"]["feels_like"])
        humidity = data["main"]["humidity"]
        city_name = data["name"]
        country = data["sys"]["country"]
        return f"Meteo a {city_name} ({country}):\n\n{desc}\nTemperature: {temp}°C\nRessentie: {feels}°C\nHumidite: {humidity}%"
    except:
        return None

# ========== COMMANDES ==========
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    country = get_user_country(user_id)

    if not country:
        await show_country_selection(update, context, page=0)
        return

    await update.message.reply_text(
        "Bienvenue sur DutaBot!\n\n"
        "/jumble - Formez le max de mots en 3 min\n"
        "/quiz - QCM 3 choix de reponse\n"
        "/score - Votre score\n"
        "/top - Classement pays + mondial\n"
        "/time paris - Heure dans un pays\n"
        "/meteo Douala - Meteo d une ville\n"
        "/foot - Scores de foot en direct\n"
        "/bonus - Bonus quotidien +10 pts\n"
        "/duel @joueur - Defier un joueur (Premium)\n"
        "/tournoi - Creer un tournoi (Premium)\n"
        "/premium - Passer Premium 1$/mois\n\n"
        "Gratuit: 5 parties/jour\n"
        "Premium: Illimite + Duels + Tournois\n\n"
        "Systeme XP + Ligues Bronze->Legend\n"
        "Classements mondiaux et par pays\n\n"
        "Bonne chance!"
    )

async def show_country_selection(update, context, page=0):
    countries_page = COUNTRY_PAGES[page]
    keyboard = []
    row = []
    for i, country in enumerate(countries_page):
        row.append(InlineKeyboardButton(country, callback_data=f"country_{COUNTRIES[country]}"))
        if len(row) == 2:
            keyboard.append(row)
            row = []
    if row:
        keyboard.append(row)

    nav = []
    if page > 0:
        nav.append(InlineKeyboardButton("⬅️ Precedent", callback_data=f"page_{page-1}"))
    if page < len(COUNTRY_PAGES) - 1:
        nav.append(InlineKeyboardButton("Suivant ➡️", callback_data=f"page_{page+1}"))
    if nav:
        keyboard.append(nav)

    text = f"Bienvenue! Choisissez votre pays:\n\n📍 {PAGE_TITLES[page]} ({page+1}/{len(COUNTRY_PAGES)})"

    if update.callback_query:
        await update.callback_query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
    else:
        await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard))

async def country_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data.startswith("page_"):
        page = int(query.data.split("_")[1])
        await show_country_selection(update, context, page=page)
        return

    if query.data.startswith("country_"):
        code = query.data.split("_")[1]
        user_id = query.from_user.id
        username = query.from_user.first_name

        scores = load_scores()
        uid = str(user_id)
        if uid not in scores:
            scores[uid] = {"username": username, "score": 0, "country": code, "last_bonus": ""}
        else:
            scores[uid]["country"] = code
            scores[uid]["username"] = username
        save_scores(scores)

        country_name = get_country_name(code)
        await query.edit_message_text(
            f"Parfait! Vous etes enregistre comme {country_name}\n\n"
            f"Bienvenue sur DutaBot!\n\n"
            f"/jumble - Formez le max de mots en 3 min\n"
            f"/quiz - QCM 3 choix de reponse\n"
            f"/score - Votre score\n"
            f"/top - Classement pays + mondial\n"
            f"/time paris - Heure dans un pays\n"
            f"/meteo Douala - Meteo d une ville\n"
            f"/foot - Scores de foot en direct\n"
            f"/bonus - Bonus quotidien +10 pts\n\n"
            f"Bonne chance!"
        )

async def jumble(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id

    if not await check_limit(update):
        return

    if user_id in jumble_sessions and jumble_sessions[user_id].get("active"):
        s = jumble_sessions[user_id]
        elapsed = time.time() - s["start_time"]
        remaining = int(180 - elapsed)
        if remaining > 0:
            await update.message.reply_text(f"Partie en cours! {remaining}s restantes\nLettres: >>> {s['letters']} <<<")
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
        f"Points = lettres du mot\nEx: BON=3pts | GRAND=5pts\n\n"
        f"✅ = Valide | ❌ = Invalide\n\nC est parti!"
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
        country = get_user_country(user_id)
        add_score(user_id, username, points, country)
        total = get_user_score(user_id)
        mots_str = ", ".join([f"{w}({len(normalize(w))})" for w in found])
        await context.bot.send_message(chat_id=chat_id,
            text=f"Temps ecoule!\n\nMots: {mots_str}\n\n+{points} points!\nScore total: {total} pts\n\n/jumble pour rejouer!")
    else:
        await context.bot.send_message(chat_id=chat_id, text="Temps ecoule! Aucun mot valide.\n/jumble pour reessayer!")
    del jumble_sessions[user_id]

async def quiz(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id

    if not await check_limit(update):
        return

    if user_id in quiz_timers:
        quiz_timers[user_id].cancel()
        del quiz_timers[user_id]
    if user_id in quiz_sessions:
        del quiz_sessions[user_id]

    # Charger questions utilisees depuis fichier (persistant)
    quiz_used = load_quiz_used()
    uid_str = str(user_id)
    if uid_str not in quiz_used:
        quiz_used[uid_str] = []
    used = quiz_used[uid_str]
    available = [q for q in ALL_QUIZ_QUESTIONS if q["q"] not in used]
    if not available:
        quiz_used[uid_str] = []
        available = ALL_QUIZ_QUESTIONS[:]
        save_quiz_used(quiz_used)

    question = random.choice(available)
    quiz_used[uid_str].append(question["q"])
    save_quiz_used(quiz_used)
    choices = question["choices"][:]
    random.shuffle(choices)
    session_id = str(int(time.time() * 1000))

    quiz_sessions[user_id] = {
        "answer": normalize(question["a"]), "active": True,
        "chat_id": chat_id, "username": update.effective_user.first_name,
        "choices_normalized": [normalize(c) for c in choices],
        "choices_display": choices, "session_id": session_id,
    }

    keyboard = [[InlineKeyboardButton(c, callback_data=f"qz_{user_id}_{i}_{session_id}")] for i, c in enumerate(choices)]
    await update.message.reply_text(f"QUIZ!\n\n{question['q']}", reply_markup=InlineKeyboardMarkup(keyboard))

    task = asyncio.create_task(quiz_timer(user_id, chat_id, question["a"], session_id, context))
    quiz_timers[user_id] = task

async def quiz_timer(user_id, chat_id, answer, session_id, context):
    await asyncio.sleep(30)
    if user_id in quiz_sessions and quiz_sessions[user_id].get("active") and quiz_sessions[user_id].get("session_id") == session_id:
        quiz_sessions[user_id]["active"] = False
        del quiz_sessions[user_id]
        if user_id in quiz_timers:
            del quiz_timers[user_id]
        await context.bot.send_message(chat_id=chat_id,
            text=f"Temps ecoule! La reponse etait: {answer.upper()}\n\n/quiz pour continuer!")

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
        country = get_user_country(target_user_id)
        add_score(target_user_id, username, 15, country)
        s = get_user_score(target_user_id)
        xp_earned = XP_REWARDS.get("quiz_correct", 20)
        new_xp = add_xp(target_user_id, username, xp_earned, get_user_country(target_user_id))
        league = get_league(new_xp)
        await query.edit_message_text(f"✅ {chosen_display} - Bonne reponse!\n+15 pts | +{xp_earned} XP\nScore: {s} pts | {league['emoji']} {league['name']}\n\n/quiz pour continuer!")
    else:
        await query.edit_message_text(f"❌ {chosen_display} - Mauvaise reponse!\nBonne reponse: {correct.upper()}\n\n/quiz pour continuer!")

async def score(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    s = get_user_score(user_id)
    name = update.effective_user.first_name
    country_code = get_user_country(user_id)
    country_name = get_country_name(country_code) if country_code else "Non defini"
    await update.message.reply_text(f"Votre score:\n\n{name}\nPays: {country_name}\nScore: {s} points")

async def top(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    scores = load_scores()
    if not scores:
        await update.message.reply_text("Aucun joueur enregistre!")
        return

    user_country = get_user_country(user_id)
    sorted_world = sorted(scores.items(), key=lambda x: x[1]["score"], reverse=True)

    # Classement mondial
    world_lines = ["CLASSEMENT MONDIAL 🌍\n"]
    for i, (uid, data) in enumerate(sorted_world[:10]):
        flag = get_country_flag(data.get("country", "XX"))
        world_lines.append(f"{i+1}. {flag} {data['username']} - {data['score']} pts")

    # Classement par pays
    country_lines = []
    if user_country and user_country != "XX":
        country_name = get_country_name(user_country)
        country_players = [(uid, data) for uid, data in sorted_world if data.get("country") == user_country]
        if country_players:
            country_lines.append(f"\nCLASSEMENT {country_name}\n")
            for i, (uid, data) in enumerate(country_players[:10]):
                country_lines.append(f"{i+1}. {data['username']} - {data['score']} pts")

    result = "\n".join(world_lines)
    if country_lines:
        result += "\n" + "\n".join(country_lines)
    result += f"\n\nTotal joueurs: {len(scores)}"

    await update.message.reply_text(result)

async def bonus(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    username = update.effective_user.first_name
    scores = load_scores()
    uid = str(user_id)
    today = str(date.today())

    if uid not in scores:
        scores[uid] = {"username": username, "score": 0, "country": "XX", "last_bonus": ""}
        save_scores(scores)

    last_bonus = scores[uid].get("last_bonus", "")
    if last_bonus == today:
        await update.message.reply_text(f"Vous avez deja pris votre bonus aujourd hui!\nRevenez demain pour +10 pts!")
        return

    scores[uid]["score"] += 10
    scores[uid]["last_bonus"] = today
    scores[uid]["username"] = username
    save_scores(scores)

    total = scores[uid]["score"]
    await update.message.reply_text(f"🎁 Bonus quotidien!\n\n+10 points!\nScore total: {total} pts\n\nRevenez demain pour un nouveau bonus!")

async def meteo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: /meteo Douala\nEx: /meteo Paris, /meteo Lagos, /meteo Dakar")
        return
    city = " ".join(context.args)
    result = get_weather(city)
    if not result:
        await update.message.reply_text(f"Ville '{city}' non trouvee.\nVerifiez le nom et reessayez.")
    else:
        await update.message.reply_text(result)

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
        await update.message.reply_text(f"'{city}' non trouve.\nEx: /time paris, /time cameroun, /time dakar")
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

    # Verifier si c est un mot de duel jumble
    if await handle_duel_jumble(update, text, text_norm):
        return

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

    # Anti-spam check
    if is_spam(user_id):
        return

    # Use professional dictionary
    valid, reason = check_word_pro(text)

    if valid:
        pts = len(text_norm)
        xp_earned = get_xp_for_word(pts)
        found.append(text)
        session["total_points"] += pts
        session["total_xp"] = session.get("total_xp", 0) + xp_earned
        await update.message.reply_text(
            f"✅ '{text}' +{pts}pts +{xp_earned}XP\n"
            f"Mots: {len(found)} | Total: {session['total_points']}pts | {remaining}s\n"
            f"Lettres: >>> {letters} <<<"
        )
    else:
        await update.message.reply_text(f"❌ '{text}' - {reason}\nLettres: >>> {letters} <<< | {remaining}s")


# ========== LIMITES PARTIES ==========
PARTIES_FILE = "parties.json"
MAX_FREE_PARTIES = 5

def load_parties():
    if os.path.exists(PARTIES_FILE):
        with open(PARTIES_FILE, "r") as f:
            return json.load(f)
    return {}

def save_parties(data):
    with open(PARTIES_FILE, "w") as f:
        json.dump(data, f)

def get_parties_today(user_id):
    data = load_parties()
    uid = str(user_id)
    today = str(date.today())
    if uid not in data or data[uid].get("date") != today:
        return 0
    return data[uid].get("count", 0)

def add_party(user_id):
    data = load_parties()
    uid = str(user_id)
    today = str(date.today())
    if uid not in data or data[uid].get("date") != today:
        data[uid] = {"date": today, "count": 0}
    data[uid]["count"] += 1
    save_parties(data)

def is_premium(user_id):
    scores = load_scores()
    uid = str(user_id)
    return scores.get(uid, {}).get("premium", False)

def can_play(user_id):
    if is_premium(user_id):
        return True
    return get_parties_today(user_id) < MAX_FREE_PARTIES

async def check_limit(update):
    user_id = update.effective_user.id
    if not can_play(user_id):
        left = 0
        await update.message.reply_text(
            "Limite atteinte! 5 parties gratuites/jour epuisees.\n\n"
            "Passez Premium 1$/mois pour jouer sans limite:\n/premium\n\n"
            "Revenez demain!"
        )
        return False
    add_party(user_id)
    return True

# ========== PREMIUM ==========
async def premium(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if is_premium(user_id):
        await update.message.reply_text("Vous etes deja Premium! Acces illimite actif!")
        return
    used = get_parties_today(user_id)
    keyboard = [
        [InlineKeyboardButton("Payer par carte - Stripe", callback_data="pay_stripe")],
        [InlineKeyboardButton("Payer Mobile Money - Flutterwave", callback_data="pay_flw")],
    ]
    await update.message.reply_text(
        "PREMIUM DUTABOT\n\n"
        f"Parties utilisees aujourd hui: {used}/5\n\n"
        "Gratuit: 5 parties/jour\n"
        "Premium 1$/mois: Acces illimite + Duels + Tournois\n\n"
        "Choisissez votre methode de paiement:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def pay_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    if query.data == "pay_stripe":
        stripe_link = f"https://buy.stripe.com/VOTRE_LIEN_STRIPE?client_reference_id={user_id}"
        await query.edit_message_text(
            f"Paiement Stripe (carte bancaire):\n\n"
            f"Cliquez sur ce lien:\n{stripe_link}\n\n"
            "Apres paiement, envoyez /confirmer_paiement"
        )
    elif query.data == "pay_flw":
        flw_link = f"https://flutterwave.com/pay/VOTRE_LIEN_FLW?meta={user_id}"
        await query.edit_message_text(
            f"Paiement Flutterwave (Mobile Money, cartes africaines):\n\n"
            f"Cliquez sur ce lien:\n{flw_link}\n\n"
            "Apres paiement, envoyez /confirmer_paiement"
        )

async def confirmer_paiement(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    username = update.effective_user.first_name
    ADMIN_ID = "VOTRE_ID_TELEGRAM"
    await update.message.reply_text(
        "Demande envoyee! L admin va verifier et activer votre compte.\n"
        "Merci de votre patience!"
    )
    try:
        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=f"DEMANDE PREMIUM\n\nUtilisateur: {username}\nID: {user_id}\n\nPour activer:\n/activer_premium {user_id}"
        )
    except:
        pass

async def activer_premium(update: Update, context: ContextTypes.DEFAULT_TYPE):
    ADMIN_ID = "VOTRE_ID_TELEGRAM"
    if str(update.effective_user.id) != str(ADMIN_ID):
        await update.message.reply_text("Commande admin uniquement.")
        return
    if not context.args:
        await update.message.reply_text("Usage: /activer_premium USER_ID")
        return
    target_id = context.args[0]
    scores = load_scores()
    if target_id in scores:
        scores[target_id]["premium"] = True
        save_scores(scores)
        await update.message.reply_text(f"Premium active pour {target_id}!")
        try:
            await context.bot.send_message(
                chat_id=int(target_id),
                text="PREMIUM ACTIVE!\n\nFelicitations! Acces illimite + Duels + Tournois actifs!"
            )
        except:
            pass
    else:
        await update.message.reply_text("Utilisateur non trouve.")

# ========== DUELS ==========
duel_sessions = {}
duel_invites = {}

async def duel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    username = update.effective_user.first_name
    if not is_premium(user_id):
        await update.message.reply_text(
            "Les duels sont reserves aux membres Premium!\n\n"
            "Passez Premium 1$/mois:\n/premium"
        )
        return
    if not context.args:
        await update.message.reply_text(
            "Usage: /duel @username\n\n"
            "Exemple: /duel @Franklin\n\n"
            "Defiez un autre joueur en Jumble ou Quiz!"
        )
        return
    target = context.args[0].replace("@", "")
    keyboard = [
        [InlineKeyboardButton("Duel Jumble", callback_data=f"dinv_jumble_{user_id}_{target}")],
        [InlineKeyboardButton("Duel Quiz", callback_data=f"dinv_quiz_{user_id}_{target}")],
    ]
    await update.message.reply_text(
        f"Duel contre @{target}\nChoisissez le type:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def duel_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    parts = query.data.split("_")
    action = parts[0]

    if action == "dinv":
        game = parts[1]
        chal_id = int(parts[2])
        target = parts[3]
        chal_name = query.from_user.first_name
        duel_id = f"D{chal_id}{int(time.time())}"
        duel_invites[target.lower()] = {
            "id": duel_id, "challenger_id": chal_id,
            "challenger_name": chal_name, "game": game,
            "chat_id": query.message.chat_id,
        }
        keyboard = [[InlineKeyboardButton(f"Accepter le duel!", callback_data=f"dacc_{duel_id}")]]
        await query.edit_message_text(
            f"@{target}, {chal_name} vous defie en {game.upper()}!\n"
            f"Cliquez pour accepter:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    elif action == "dacc":
        duel_id = parts[1]
        acc_id = query.from_user.id
        acc_name = query.from_user.first_name
        inv = None
        for u, i in duel_invites.items():
            if i["id"] == duel_id:
                inv = i
                break
        if not inv:
            await query.edit_message_text("Ce duel a expire!")
            return
        chal_id = inv["challenger_id"]
        chal_name = inv["challenger_name"]
        game = inv["game"]
        chat_id = inv["chat_id"]
        duel_sessions[duel_id] = {
            "p1": {"id": chal_id, "name": chal_name, "score": 0},
            "p2": {"id": acc_id, "name": acc_name, "score": 0},
            "game": game, "active": True, "chat_id": chat_id,
        }
        if game == "jumble":
            letters = random.choice(JUMBLE_SETS)
            duel_sessions[duel_id]["letters"] = letters
            duel_sessions[duel_id]["found"] = set()
            await query.edit_message_text(
                f"DUEL JUMBLE!\n{chal_name} VS {acc_name}\n\n"
                f"Lettres: >>> {letters} <<<\n\n"
                f"2 minutes! Points = lettres du mot\n"
                f"Tapez vos mots! C est parti!"
            )
            asyncio.create_task(duel_end_timer(duel_id, context))
        elif game == "quiz":
            q = random.choice(ALL_QUIZ_QUESTIONS)
            choices = q["choices"][:]
            random.shuffle(choices)
            duel_sessions[duel_id]["question"] = q
            duel_sessions[duel_id]["choices"] = choices
            duel_sessions[duel_id]["answers"] = {}
            keyboard2 = [[InlineKeyboardButton(c, callback_data=f"dq_{duel_id}_{i}")] for i, c in enumerate(choices)]
            await query.edit_message_text(
                f"DUEL QUIZ!\n{chal_name} VS {acc_name}\n\n{q['q']}",
                reply_markup=InlineKeyboardMarkup(keyboard2)
            )
            asyncio.create_task(duel_end_timer(duel_id, context))

async def duel_end_timer(duel_id, context):
    await asyncio.sleep(120)
    if duel_id not in duel_sessions or not duel_sessions[duel_id].get("active"):
        return
    await finish_duel(duel_id, context)

async def finish_duel(duel_id, context):
    if duel_id not in duel_sessions:
        return
    session = duel_sessions[duel_id]
    session["active"] = False
    p1, p2 = session["p1"], session["p2"]
    chat_id = session["chat_id"]
    if p1["score"] > p2["score"]:
        winner = f"{p1['name']} gagne!"
        add_score(p1["id"], p1["name"], p1["score"] + 20)
        add_score(p2["id"], p2["name"], p2["score"])
    elif p2["score"] > p1["score"]:
        winner = f"{p2['name']} gagne!"
        add_score(p2["id"], p2["name"], p2["score"] + 20)
        add_score(p1["id"], p1["name"], p1["score"])
    else:
        winner = "Egalite!"
        add_score(p1["id"], p1["name"], p1["score"])
        add_score(p2["id"], p2["name"], p2["score"])
    await context.bot.send_message(
        chat_id=chat_id,
        text=f"DUEL TERMINE!\n\n{p1['name']}: {p1['score']} pts\n{p2['name']}: {p2['score']} pts\n\n{winner}\n+20 pts bonus au vainqueur!"
    )
    del duel_sessions[duel_id]

async def duel_quiz_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    parts = query.data.split("_")
    duel_id = parts[1]
    idx = int(parts[2])
    player_id = query.from_user.id
    if duel_id not in duel_sessions or not duel_sessions[duel_id].get("active"):
        await query.answer("Duel termine!", show_alert=True)
        return
    session = duel_sessions[duel_id]
    answers = session.get("answers", {})
    if str(player_id) in answers:
        await query.answer("Vous avez deja repondu!", show_alert=True)
        return
    correct = normalize(session["question"]["a"])
    chosen = normalize(session["choices"][idx])
    is_correct = chosen == correct
    answers[str(player_id)] = is_correct
    session["answers"] = answers
    if is_correct:
        if player_id == session["p1"]["id"]:
            session["p1"]["score"] += 15
        elif player_id == session["p2"]["id"]:
            session["p2"]["score"] += 15
    await query.answer("Bonne reponse!" if is_correct else "Mauvaise reponse!", show_alert=True)
    if len(answers) >= 2:
        await finish_duel(duel_id, context)

# Gestion des mots de duel Jumble dans handle_answer
async def handle_duel_jumble(update, text, text_norm):
    user_id = update.effective_user.id
    username = update.effective_user.first_name
    for duel_id, session in list(duel_sessions.items()):
        if session.get("game") != "jumble" or not session.get("active"):
            continue
        if user_id not in [session["p1"]["id"], session["p2"]["id"]]:
            continue
        letters = session["letters"]
        found = session["found"]
        if text_norm in found:
            await update.message.reply_text(f"'{text}' deja trouve!")
            return True
        if not can_form_word(text_norm, normalize(letters)):
            await update.message.reply_text(f"Impossible avec ces lettres: >>> {letters} <<<")
            return True
        if is_valid_word(text):
            pts = len(text_norm)
            found.add(text_norm)
            if user_id == session["p1"]["id"]:
                session["p1"]["score"] += pts
            else:
                session["p2"]["score"] += pts
            p1, p2 = session["p1"], session["p2"]
            await update.message.reply_text(
                f"DUEL: {p1['name']} {p1['score']}pts VS {p2['name']} {p2['score']}pts"
            )
        else:
            await update.message.reply_text(f"'{text}' non reconnu!")
        return True
    return False

# ========== TOURNOIS ==========
tournoi_sessions = {}

async def tournoi(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not is_premium(user_id):
        await update.message.reply_text(
            "Les tournois sont reserves aux membres Premium!\n\n"
            "Passez Premium 1$/mois:\n/premium"
        )
        return
    keyboard = [
        [InlineKeyboardButton("Tournoi Jumble", callback_data="tnew_jumble")],
        [InlineKeyboardButton("Tournoi Quiz", callback_data="tnew_quiz")],
    ]
    await update.message.reply_text(
        "TOURNOIS DUTABOT\n\n"
        "Min 2 joueurs, max 10\n"
        "Bonus: 1er +50pts, 2eme +30pts, 3eme +20pts\n\n"
        "Choisissez le type:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def tournoi_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    parts = query.data.split("_")
    action = parts[0]
    user_id = query.from_user.id
    username = query.from_user.first_name

    if action == "tnew":
        game = parts[1]
        tid = f"T{int(time.time())}"
        tournoi_sessions[tid] = {
            "creator": user_id, "game": game, "status": "waiting",
            "players": {str(user_id): {"name": username, "score": 0}},
            "chat_id": query.message.chat_id,
        }
        nb = len(tournoi_sessions[tid]["players"])
        players_txt = "\n".join([f"{i+1}. {p['name']}" for i, p in enumerate(tournoi_sessions[tid]["players"].values())])
        keyboard = [
            [InlineKeyboardButton("Rejoindre!", callback_data=f"tjoin_{tid}")],
            [InlineKeyboardButton("Lancer!", callback_data=f"tlaunch_{tid}")],
        ]
        await query.edit_message_text(
            f"TOURNOI {game.upper()} CREE!\n\nCode: {tid}\n\nJoueurs ({nb}/10):\n{players_txt}\n\nAttendez des joueurs puis lancez!",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    elif action == "tjoin":
        tid = parts[1]
        if tid not in tournoi_sessions:
            await query.edit_message_text("Tournoi non trouve!")
            return
        session = tournoi_sessions[tid]
        if session["status"] != "waiting":
            await query.answer("Tournoi deja lance!", show_alert=True)
            return
        if len(session["players"]) >= 10:
            await query.answer("Tournoi complet!", show_alert=True)
            return
        session["players"][str(user_id)] = {"name": username, "score": 0}
        nb = len(session["players"])
        players_txt = "\n".join([f"{i+1}. {p['name']}" for i, p in enumerate(session["players"].values())])
        keyboard = [
            [InlineKeyboardButton("Rejoindre!", callback_data=f"tjoin_{tid}")],
            [InlineKeyboardButton("Lancer!", callback_data=f"tlaunch_{tid}")],
        ]
        await query.edit_message_text(
            f"TOURNOI {session['game'].upper()}\n\nJoueurs ({nb}/10):\n{players_txt}",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    elif action == "tlaunch":
        tid = parts[1]
        if tid not in tournoi_sessions:
            await query.edit_message_text("Tournoi non trouve!")
            return
        session = tournoi_sessions[tid]
        if query.from_user.id != session["creator"]:
            await query.answer("Seul le createur peut lancer!", show_alert=True)
            return
        if len(session["players"]) < 2:
            await query.answer("Minimum 2 joueurs!", show_alert=True)
            return
        session["status"] = "playing"
        game = session["game"]
        players_txt = "\n".join([f"{i+1}. {p['name']}" for i, p in enumerate(session["players"].values())])
        if game == "jumble":
            letters = random.choice(JUMBLE_SETS)
            session["letters"] = letters
            session["found"] = {}
            await query.edit_message_text(
                f"TOURNOI JUMBLE LANCE!\n\nJoueurs:\n{players_txt}\n\n"
                f"Lettres: >>> {letters} <<<\n\n"
                f"3 minutes! Points = lettres du mot\nC est parti!"
            )
            asyncio.create_task(tournoi_end(tid, context))
        elif game == "quiz":
            questions = random.sample(ALL_QUIZ_QUESTIONS, min(5, len(ALL_QUIZ_QUESTIONS)))
            session["questions"] = questions
            session["current_q"] = 0
            session["q_answers"] = {}
            q = questions[0]
            choices = q["choices"][:]
            random.shuffle(choices)
            session["current_choices"] = choices
            keyboard2 = [[InlineKeyboardButton(c, callback_data=f"tq_{tid}_{i}")] for i, c in enumerate(choices)]
            await query.edit_message_text(
                f"TOURNOI QUIZ LANCE!\n\nJoueurs:\n{players_txt}\n\n"
                f"Question 1/5:\n\n{q['q']}",
                reply_markup=InlineKeyboardMarkup(keyboard2)
            )

async def tournoi_end(tid, context):
    await asyncio.sleep(180)
    if tid not in tournoi_sessions:
        return
    session = tournoi_sessions[tid]
    chat_id = session["chat_id"]
    sorted_p = sorted(session["players"].items(), key=lambda x: x[1]["score"], reverse=True)
    medals = ["1.", "2.", "3.", "4.", "5.", "6.", "7.", "8.", "9.", "10."]
    bonus = [50, 30, 20]
    lines = ["TOURNOI TERMINE!\n\nResultats finaux:\n"]
    for i, (uid, data) in enumerate(sorted_p):
        b = bonus[i] if i < 3 else 5
        lines.append(f"{medals[i]} {data['name']} - {data['score']}pts (+{b} bonus)")
        add_score(int(uid), data["name"], data["score"] + b)
    lines.append("\nBonus: 1er +50pts | 2eme +30pts | 3eme +20pts")
    await context.bot.send_message(chat_id=chat_id, text="\n".join(lines))
    del tournoi_sessions[tid]

async def tournoi_quiz_cb(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    parts = query.data.split("_")
    tid = parts[1]
    idx = int(parts[2])
    player_id = str(query.from_user.id)
    if tid not in tournoi_sessions:
        await query.answer("Tournoi termine!", show_alert=True)
        return
    session = tournoi_sessions[tid]
    if player_id not in session["players"]:
        await query.answer("Vous ne participez pas!", show_alert=True)
        return
    q_answers = session.get("q_answers", {})
    if player_id in q_answers:
        await query.answer("Vous avez deja repondu!", show_alert=True)
        return
    current_q = session["current_q"]
    question = session["questions"][current_q]
    choices = session["current_choices"]
    correct = normalize(question["a"])
    chosen = normalize(choices[idx])
    is_correct = chosen == correct
    q_answers[player_id] = is_correct
    session["q_answers"] = q_answers
    if is_correct:
        session["players"][player_id]["score"] += 15
    await query.answer("Bonne reponse! +15pts" if is_correct else "Mauvaise reponse!", show_alert=True)
    if len(q_answers) >= len(session["players"]):
        session["current_q"] += 1
        session["q_answers"] = {}
        chat_id = session["chat_id"]
        if session["current_q"] >= len(session["questions"]):
            await tournoi_end(tid, context)
        else:
            q = session["questions"][session["current_q"]]
            choices2 = q["choices"][:]
            random.shuffle(choices2)
            session["current_choices"] = choices2
            keyboard2 = [[InlineKeyboardButton(c, callback_data=f"tq_{tid}_{i}")] for i, c in enumerate(choices2)]
            qnum = session["current_q"] + 1
            await context.bot.send_message(
                chat_id=chat_id,
                text=f"Question {qnum}/5:\n\n{q['q']}",
                reply_markup=InlineKeyboardMarkup(keyboard2)
            )


# ==============================================================
# PHASE 1 UPGRADE - PROFESSIONAL GAME ENGINE
# ==============================================================

import hashlib

# ==============================================================
# MODULE 1: PROFESSIONAL DICTIONARY (15,000+ words FR+EN)
# ==============================================================

def _build_dict():
    """Build professional FR+EN dictionary"""
    import unicodedata as _ud
    def _n(w):
        w = w.lower().strip()
        return "".join(c for c in _ud.normalize("NFD", w) if _ud.category(c) != "Mn")

    FR = """le la les de du des un une et en il elle ils elles je tu nous vous ce qui que
dans sur pour avec par mais ou donc ni car si pas plus aussi tout bien alors encore comme
fait meme tres moins assez etre avoir aller voir faire dire pouvoir vouloir savoir venir
prendre partir rester tomber monter descendre sortir entrer donner parler manger boire
dormir ecouter regarder chercher trouver penser croire connaitre comprendre apprendre
aimer detester devoir falloir mettre tenir creer jouer gagner perdre commencer finir
ouvrir fermer lire ecrire est sont suis es avons avez ont etait sera serait vais vas va
allons allez vont fait fais faites font dit dis dites disent peut peux peuvent veut veux
veulent sait sais savent vient viens viennent prend prends prennent main tete pied oeil
yeux bras jambe corps coeur dos nez bouche dent oreille cheveu ventre epaule genou doigt
eau air feu terre mer ciel soleil lune etoile nuage pluie neige vent orage montagne foret
plage ile lac riviere fleuve ocean desert jungle prairie colline vallee maison ville pays
monde vie mort homme femme enfant ami amie famille frere soeur pere mere fils fille cousin
oncle tante mari bebe garcon route chemin porte fenetre table chaise lit chambre cuisine
salon bureau jardin balcon escalier pain fromage vin cafe the lait jus sucre sel beurre
huile farine oeuf viande poisson legume fruit pomme poire orange citron banane raisin
fraise cerise tomate carotte salade soupe plat dessert gateau bus train avion bateau
voiture moto velo taxi metro camion blanc blanche noir noire rouge bleu bleue vert verte
jaune gris grise rose violet brun brune grand grande petit petite vieux vieille nouveau
nouvelle beau belle long longue court courte haut haute bas basse premier premiere
dernier derniere autre meme seul seule bon bonne mauvais mauvaise fort forte faible
rapide lent chaud froid propre sale libre plein vide ouvert ferme vrai faux certain
possible probable jour nuit matin soir temps heure minute seconde semaine mois an annee
hier demain maintenant bientot tard lundi mardi mercredi jeudi vendredi samedi dimanche
janvier fevrier mars avril mai juin juillet aout septembre octobre novembre decembre
chien chat oiseau cheval lion tigre elephant singe serpent crocodile girafe zebre aigle
perroquet dauphin baleine requin grenouille lapin mouton cochon vache poule canard hibou
loup renard ours livre ecole classe prof eleve etudiant universite diplome travail emploi
reunion projet rapport contrat medecin professeur policier pompier infirmier directeur
avocat architecte ingenieur chercheur journaliste acteur ordinateur telephone internet
message email site reseau application logiciel video photo ecran clavier souris sport
football basket tennis natation course velo golf rugby boxe danse yoga fitness match
equipe joueur but musique chanson film histoire roman poeme theatre idee pensee sentiment
emotion amour haine joie tristesse peur colere surprise espoir reve souvenir politique
economie science medecine art culture religion paix guerre liberte egalite justice droit
loi gouvernement chose truc affaire probleme solution reponse question raison cause effet
resultat objectif plan debut fin milieu centre bord cote face dessus dessous couleur
forme taille poids vitesse distance duree quantite service produit client vendeur prix
offre marche nord sud est ouest droite gauche devant derriere marcher courir nager voler
lever poser porter tenir jeter attraper pousser tirer tourner retourner traverser compter
calculer mesurer peser payer acheter vendre louer montrer cacher proteger defendre
attaquer aider soigner appeler repondre expliquer raconter decrire inviter remercier
suis sommes etes etais etions etiez etaient serai seras serons serez seront ai as avait
avions aviez avaient aurai auras aura aurons aurez auront irai iras ira irons irez iront
ami art bal ban bar bas bat bec bol bon cap car cas cle col con cor cou cri dal den dey
dis dit dix dom dos dot duc eau eco ela emu ens erg eta ete eux eve fac fan far fat fax
fee fer feu fez fic fil fin fol fon for fou fur gag gai gal gap gar gaz gel gin gnu ils
ire jet jeu job lac lai lan las lat leu lev lex ley lob log lot lue lui lux mac mal mas
mat mes met mie mil mis mit mob mod moi mol mon mot mou mue mur mus nag net nez nid nil
nob nom non nos not nou nun ode oie oil oli ont ope ora ore ori ors ose ouf oui our pad
pan par pat peu pic pin pit pli poi pol pop pot pou pro pub raz rec ref rem rep res rev
riz roi rom ros rue rut sac sau sec sel sen sep ski sol som son sot sou sud sus tac tan
tap tar tas tau tic tir ton top tot tou tri tub tue val van var vas ver via vic vin vis
vit vol vue yak zoo sang sans saut seau sere seve silo sole sort sous stop suer sure tare
tele tend tenu tire toit tome tone tore tort trac tram trap tres trio trop tube tune type
vale vane veau vent vers vide vile vine vite voie voir vole vote vrai zero zone rade rale
rame rang rape rare rase rate reel rein rent ride rire rite robe role rude ruse sage sale
bloc bois bord bout bras brin brun cage camp case cent char chat chef cher ciel cite clan
clou club code coin cone cote coup cran cure dame date demi dent deux dire dome dose drap
dune dure edit elan etat etre euro face fait file film fils fine flot foie fond fort four
gain gale gare gate gaze gene gite golf gout gras gris hale halo hate hier home hors hote
jade jean joli joue jour juge jupe lame lard lent lest leur lieu lime lire lobe loge loin
lors loue loup lune male malt mare mars mate mere mine mode mort mule noel noir note nuit
once onde oral orge ours page pale pare part pate peau pere pied pile pine pire plan plat
plie pore port pose prix puce tels eux ici deja lors chez lors vers""".split()

    EN = """the be to of and in that have it for not on with he as you do at this but his by
from they we say her she or an will my one all would there their what so up out if about
who get which go me when make can like time no just him know take people into year your
good some could them see other than then now look only come its over think also back after
use two how our work first well way even new want any these give day most us great between
need large often hand high place world small number keep point right always man old long
down get come made may part take place live where by too our around every found still
below start would both those four far few more every being old turn real later little
change off always move try kind hand picture again school food water house car tree book
family black white red blue green yellow orange purple brown grey dog cat bird fish horse
lion tiger elephant monkey bread cheese wine coffee tea milk juice sugar salt bus train
plane boat bike doctor teacher police fire nurse january february march april may june
july august september october november december monday tuesday wednesday thursday friday
saturday sunday north south east west friend brother sister father mother son daughter
sport football basketball tennis swimming music song film story computer phone internet
love hate joy fear anger peace war abc abcde ab ad ag ah ai al am an ar as at aw ax ay ba
be bi bo by da de do ed ef eh el em en er es et ex fa fe go ha he hi hm ho id if in is
it jo ka ki la li lo ma me mi mm mo mu my na ne no nu od oe of oh oi ok om on op or os ow
ox oy pa pe pi po qi re sh si so ta ti to uh um un up us ut we wo xi xu ya ye yo ace act
add age ago aid aim air ale all ant ape arc are ark arm art ask ate awe axe aye bad bag
ban bar bat bay bed beg bet bid big bit bog bow box boy bud bug bun bus but buy cab can
cap car cat cob cod cog cop cow cry cub cup cut dab dam day den dew did die dig dim dip
dog dot dry dub dug dun dye ear eat egg ego elf elk elm emu end era eve ewe eye fad fan
far fat fax fay fed fen few fib fig fin fit fix fly foe fog for fox fry fun fur gag gap
gar gas gig gin gnu god got gun gut gym had ham has hat hay hem hen her hew hid him hip
his hit hob hoe hog hop hot how hub hug hum hut ice icy ill imp inn ion ivy jab jag jam
jar jaw jay jet jig job jog jot joy jug jut keg kid kin kit lab lap law lay lea led leg
let lid lip lit log lot low mad man map mar mat maw may men met mew mob mop mow mud mug
mum nab nag nap nib nil nip nit nob nod nor not now nun nut oak oar oat odd ode off oil
old ore our out owe own pad pal pan pap par pat paw pay pea peg pen pep per pet pew pie
pig pin pit ply pod pop pot pow pro pub pug pun pup pus put rag ram ran rap rat raw ray
red ref rep rev rib rid rig rip rob rod rot row rub rug rum run rut rye sad sag sap sat
saw say sea set sew shy sin sip sir sit ski sky sly sob sod son sow soy spa spy sty sub
sue sum sun tab tan tap tar tat tax ten thy tie tin tip toe ton too top toy try tub tug
tun two urn use van vat via vie vim vow wad war was wax way web wed wig win wit woe wok
won woo wow yam yap yaw yep yes yet yew you zap zed zen zig zip zoo able acid aged also
area army away back ball band bank base bath bear beat been bell best bird bite blow blue
boat body bold bolt bond bone book bore born both bowl burn came camp cape card care cart
case cast cave cent char chat chin chip clan clap clip clot club clue coal coat coil cold
colt come cord core corn cost crop dart data date deal dean dear debt deck deed deer deli
dent diet dirt disc dish disk dock dole dome done door dorm dote down drag dram draw drip
drop drum dual duel dune dupe dust earl earn east edge edit else emit epic even ever evil
exam face fact fail fair fall fame fang fare farm fast fate fear feat feel fell felt fend
fern file fill film find fine fire firm fist flag flat flaw flea fled flew flip flit flow
foam fold folk fond food fool foot ford fore fork form fort foul four free fuel full fume
gain gale game gang gate gave gaze gear gent germ gild girl give glad glee glen glob glue
goal gold golf gone good gore gown grab grad gram gray grew grid grim grin grip grit grow
gulf gust hack hale half hall halt hand hang hard hare harm harp hate have heal heap heat
heel held helm help here hero hide high hike hill hint hire hold hole home hood hook hope
horn host hour hulk hull hump hunt hurt idea idle inch into iron isle item jade jail jean
joke jolt jump just keen keep kick kind king knob knot lace lack lame lamp land lane lard
lark lash last late lead leaf lean leap lend lens lest liar lice lick lied lies life lift
like lime limp line link lint list live load loam lobe lock loft lone long look loom lord
lore lose lost loud love luck made mail main make male malt mane mare mark mart mast mate
meal mean meat meet melt mend mere mild mile milk mill mind mine mint mire miss mist moan
mole molt monk mood moon moor more mort most move muck mule must nail name near neck need
next nice nick nine node none noon norm nose note null oath odds once open oral orca oven
over pace pack page paid pain pair pale palm pane park part past path peak peel peer pelt
pick pier pile pine pink pipe plan play plod plot plow plum plus poem poet pole poll pond
pore port pose post pour prey prod prop pull pump pure push race rack raid rail rain rake
ramp rang rank rant rapt rate read real reap reel rein rely rend rent rest rice rich ride
rift ring riot rise risk road roam roar robe rock rode role roll roof room root rope rose
rout rude ruin rule rump rune ruse rush rust safe sail sake sale salt same sand sane sang
sank sate save scan scar seal seam sear seat self send shed shin ship shoe shop shot shun
shut sick side sift sign silk silo silt sing sink site size skid skim skin skip slab slap
slat slim slip slob slop slot slum slur snag snap snob snot snow soak soar sock soil sold
sole some song soot sore sort soul soup sour span spar spin spit spot spur stab stag star
stay stem step stir stop stub stun suck suit sulk sung sunk sure surf swam swan swap sway
swim tail tale talk tall tame tang tank tare tart teal team tear teem tell tend tent term
thin tide tile till time tire toad toil told toll tome tone tong tool torn toss tour town
trap tray tree trim trip trod true tube tuck tuft tune tusk twin type undo upon urge used
vale vane vast veil vein vent verb very vest vial vice view vile vine void volt wade wage
wail wake walk wall wand wane ward ware warm warn warp wart wash wave weak weal wean wear
weed weld went wide wild will wilt wind wine wing wink wire wise wish woke wold womb wood
wool word wore work worm worn wrap yell zeal zero zinc zone zoom about above abuse acre
actor adult after again agent agree ahead alarm album alert alike alive alley allow alone
along alter angel anger angle angry ankle annoy apart apple apply arena argue arise armor
aroma arrow asset audio audit avoid award aware awful basic beach beard began begin being
below bench berry birth black blade blame bland blank blast blaze bleed blend bless blind
block blood bloom blown board bonus boost booth bound brain brave bread break breed brick
bride brief bring broad broke brook brown brush buddy build built bunch burst buyer cabin
cable candy carry catch cause chain chair chaos charm chase cheap check cheek chess chest
chick chief child china civil claim class clean clear clerk click cliff climb clock clone
close cloth cloud coach coast color comic coral could count court cover craft crash crazy
cream crime cross crowd crown cruel crush curve cycle dance death delay delta depth derby
devil digit dirty disco ditch doubt draft drama dream dress drift drink drive drone drove
eagle early earth eight elite email empty enemy enjoy enter equal error essay event exact
exist extra fable faith false fancy fault feast fence fever field fifth fifty fight final
first fixed flame flash fleet flesh float flock floor flour fluid flush focus force forge
forth forum found frame frank fraud fresh front frost froze fruit fully funny ghost giant
given glass globe gloom gloss glove going grade grain grand grant grasp grass grave great
green greet grief grill groan groin gross group grove grown guard guide guilt guise gusto
happy harsh heart heavy hence honor horse hotel house human humor hurry ideal image imply
index inner input irony issue ivory jewel joint judge juice juicy kayak knock known label
labor lance large laser laugh layer learn lease leave level light limit linen liver local
lodge logic lower lucky lunch lying magic major maker manor maple march match mayor media
mercy merit metal might minor minus model money month moral motor mount mouse mouth movie
music naive naked nerve never night noble noise north noted novel nurse occur ocean offer
often opera order other outer owing owner oxide ozone paint panel panic paper patch pause
peace penny phase phone photo piano pitch pixel pizza place plain plane plant plate plaza
point polar power press price pride prime print prior prize probe prone proof prose prove
pulse punch pupil purse queen quest quick quiet quite quota quote radio raise rally range
rapid ratio reach ready realm rebel refer reign relax remix repay reply rider ridge right
risky rival river robot rocky rough round route royal rugby ruler rural salad sauce scale
scene scope score scout sense serve seven shade shake shall shame shape share shark sharp
shelf shell shift shirt shock shore short shout sight since sixth skill slate slave sleep
slice slide slope smart smell smile smoke snake solar solid solve sorry sound south space
spare spark speak spear speed spell spend spice spine split spoon sport spray squad staff
stage stain stake stall stand start state steal steam steel stick stiff still stock stone
story stout stove stuck study stump style sugar suite super surge swamp sweep sweet sword
table taste teach teeth their theme there thick thing think third those three threw throw
thumb tiger timer tired title today token total touch tough towel toxic trace track trade
trail train trait treat trend trial tribe trick tried troop truck trunk trust truth tumor
twice twist umbra uncle under union unity until upper upset urban usage usual utter valid
value video vigor viral virus visit vital voice voter waist waste watch water weary weave
weird wheat where which while white whole whose widen width witch woman women world worry
worse worst worth would wound wrath write wrote yacht yield young youth zebra""".split()

    fr = set(_n(w) for w in FR if len(w.strip()) >= 2)
    en = set(_n(w) for w in EN if len(w.strip()) >= 2)

    # Add conjugations FR
    extras_fr = set()
    for w in list(fr):
        if len(w) >= 3:
            extras_fr.add(w + "s")
            if w.endswith("er"):
                extras_fr.update([w[:-2]+"e", w[:-2]+"es", w[:-2]+"ent", w[:-2]+"ais", w[:-2]+"ait"])
            if w.endswith("ir"):
                extras_fr.update([w[:-2]+"is", w[:-2]+"it", w[:-2]+"issons"])
    fr.update(extras_fr)

    # Add conjugations EN
    extras_en = set()
    for w in list(en):
        if len(w) >= 3:
            extras_en.add(w + "s")
            if w.endswith("e"):
                extras_en.update([w+"d", w+"r", w+"s"])
            else:
                extras_en.update([w+"ed", w+"er", w+"ing", w+"s"])
            if w.endswith("y") and len(w) > 3:
                extras_en.update([w[:-1]+"ies", w[:-1]+"ied"])
    en.update(extras_en)

    return fr | en

# Build dictionary once at startup
print("Building professional dictionary...")
PROFESSIONAL_DICT = _build_dict()
print(f"Dictionary ready: {len(PROFESSIONAL_DICT)} words")

def check_word_pro(word):
    """Professional word checker - FR+EN"""
    if not word or len(word) < 2:
        return False, "Trop court"
    w = normalize(word)
    if w in PROFESSIONAL_DICT:
        return True, "OK"
    # Try online as fallback
    try:
        import requests as _req
        resp = _req.get(f"https://api.dictionaryapi.dev/api/v2/entries/en/{word}", timeout=2)
        if resp.status_code == 200:
            PROFESSIONAL_DICT.add(w)  # cache it
            return True, "OK (EN online)"
    except:
        pass
    return False, f"'{word}' non reconnu FR/EN"

# ==============================================================
# MODULE 2: INTELLIGENT JUMBLE ENGINE
# ==============================================================

import math

# Balanced letter pools for jumble generation
VOWELS = list("aeiouaeiouaeiou")  # weighted toward common vowels
CONSONANTS = list("bcdfghjklmnpqrstvwxyzbnrstlmncdrst")  # weighted toward common consonants

# Jumble difficulty config
JUMBLE_CONFIG = {
    "easy":   {"letters": 7,  "min_words": 8,  "vowel_ratio": 0.45, "xp": 10,  "label": "FACILE"},
    "medium": {"letters": 9,  "min_words": 10, "vowel_ratio": 0.40, "xp": 20,  "label": "MOYEN"},
    "hard":   {"letters": 11, "min_words": 12, "vowel_ratio": 0.36, "xp": 35,  "label": "DIFFICILE"},
    "insane": {"letters": 13, "min_words": 15, "vowel_ratio": 0.32, "xp": 60,  "label": "INSANE"},
}

# History to avoid repeats
jumble_history = []
MAX_HISTORY = 50

def generate_jumble_letters(difficulty="medium"):
    """Generate balanced letter set for jumble"""
    cfg = JUMBLE_CONFIG.get(difficulty, JUMBLE_CONFIG["medium"])
    n = cfg["letters"]
    vowel_count = max(2, int(n * cfg["vowel_ratio"]))
    consonant_count = n - vowel_count

    max_attempts = 20
    for attempt in range(max_attempts):
        letters = []
        # Add vowels
        for _ in range(vowel_count):
            letters.append(random.choice(VOWELS))
        # Add consonants
        for _ in range(consonant_count):
            letters.append(random.choice(CONSONANTS))

        random.shuffle(letters)
        letter_str = "".join(letters).upper()

        # Check not in recent history
        if letter_str not in jumble_history:
            # Quick check if enough words possible
            possible = count_possible_words(letter_str.lower(), min_check=cfg["min_words"])
            if possible >= min(3, cfg["min_words"] // 2):
                jumble_history.append(letter_str)
                if len(jumble_history) > MAX_HISTORY:
                    jumble_history.pop(0)
                return letter_str, difficulty

    # Fallback - return anyway
    return "".join(random.choices("AEIOURSTLNBCDFGM", k=n)), difficulty

def count_possible_words(letters, min_check=5):
    """Count how many dict words can be formed from letters"""
    available = list(letters.lower())
    count = 0
    # Sample a subset for speed
    sample = random.sample(list(PROFESSIONAL_DICT), min(2000, len(PROFESSIONAL_DICT)))
    for word in sample:
        if 2 <= len(word) <= len(letters):
            avail = available[:]
            ok = True
            for c in word:
                if c in avail:
                    avail.remove(c)
                else:
                    ok = False
                    break
            if ok:
                count += 1
                if count >= min_check:
                    return count
    return count

# ==============================================================
# MODULE 3: XP & LEAGUE SYSTEM
# ==============================================================

LEAGUES = [
    {"name": "Bronze",   "min_xp": 0,     "emoji": "🥉", "color": "bronze"},
    {"name": "Silver",   "min_xp": 500,   "emoji": "🥈", "color": "silver"},
    {"name": "Gold",     "min_xp": 1500,  "emoji": "🥇", "color": "gold"},
    {"name": "Diamond",  "min_xp": 5000,  "emoji": "💎", "color": "diamond"},
    {"name": "Legend",   "min_xp": 15000, "emoji": "👑", "color": "legend"},
]

XP_REWARDS = {
    "jumble_word_2": 2,   # 2-letter word
    "jumble_word_3": 4,   # 3-letter word
    "jumble_word_4": 8,   # 4-letter word
    "jumble_word_5": 15,  # 5+ letter word
    "quiz_correct": 20,
    "duel_win": 50,
    "duel_participate": 10,
    "tournament_win": 100,
    "tournament_top3": 50,
    "daily_bonus": 15,
    "streak_3": 25,
    "streak_7": 75,
    "streak_30": 300,
}

def get_xp_for_word(word_length):
    if word_length <= 2: return XP_REWARDS["jumble_word_2"]
    if word_length == 3: return XP_REWARDS["jumble_word_3"]
    if word_length == 4: return XP_REWARDS["jumble_word_4"]
    return XP_REWARDS["jumble_word_5"]

def get_league(xp):
    """Get league info from XP"""
    league = LEAGUES[0]
    for l in LEAGUES:
        if xp >= l["min_xp"]:
            league = l
    return league

def get_next_league(xp):
    """Get next league info"""
    for i, l in enumerate(LEAGUES):
        if xp < l["min_xp"]:
            return l
    return None

def add_xp(user_id, username, xp_amount, country_code=None):
    """Add XP and update league"""
    scores = load_scores()
    uid = str(user_id)
    if uid not in scores:
        scores[uid] = {"username": username, "score": 0, "xp": 0, "country": country_code or "XX", "last_bonus": "", "streak": 0}
    scores[uid]["xp"] = scores[uid].get("xp", 0) + xp_amount
    scores[uid]["username"] = username
    if country_code:
        scores[uid]["country"] = country_code
    save_scores(scores)
    return scores[uid]["xp"]

def get_user_xp(user_id):
    scores = load_scores()
    return scores.get(str(user_id), {}).get("xp", 0)

def get_world_rank(user_id):
    """Get user world rank by score"""
    scores = load_scores()
    sorted_s = sorted(scores.items(), key=lambda x: x[1].get("score", 0), reverse=True)
    for i, (uid, _) in enumerate(sorted_s):
        if uid == str(user_id):
            return i + 1
    return 0

def get_country_rank(user_id):
    """Get user rank in their country"""
    scores = load_scores()
    uid = str(user_id)
    user_country = scores.get(uid, {}).get("country", "XX")
    country_players = [(k, v) for k, v in scores.items() if v.get("country") == user_country]
    country_players.sort(key=lambda x: x[1].get("score", 0), reverse=True)
    for i, (k, _) in enumerate(country_players):
        if k == uid:
            return i + 1, len(country_players)
    return 0, 0

def get_league_badge(xp):
    league = get_league(xp)
    return f"{league['emoji']} {league['name']}"

# ==============================================================
# MODULE 4: PROFILE SYSTEM
# ==============================================================

async def profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    username = update.effective_user.first_name
    uid = str(user_id)
    scores = load_scores()
    xp_data = get_user_xp_data(user_id)
    stats = get_user_stats(user_id)
    score = scores.get(uid, {}).get("score", 0)
    country_code = scores.get(uid, {}).get("country", "XX")
    country_name = get_country_name(country_code)
    is_prem = scores.get(uid, {}).get("premium", False)
    xp = xp_data.get("xp", 0)
    league = get_league_for_xp(xp)
    next_lg = None
    for i, lg in enumerate(LEAGUES):
        if lg["name"] == league["name"] and i + 1 < len(LEAGUES):
            next_lg = LEAGUES[i+1]
            break
    all_scores = sorted(scores.items(), key=lambda x: x[1].get("score",0), reverse=True)
    world_rank = next((i+1 for i,(k,v) in enumerate(all_scores) if k==uid), "?")
    badge_display = " ".join([BADGES[b]["emoji"] for b in stats.get("badges",[]) if b in BADGES]) or "Aucun badge encore"
    progress = ""
    if next_lg:
        cur_min = league["min_xp"]
        nxt_min = next_lg["min_xp"]
        prog = min(1.0, (xp - cur_min) / max(1, nxt_min - cur_min))
        filled = int(prog * 10)
        bar = ("X" * filled) + ("-" * (10 - filled))
        pct = int(prog * 100)
        nxt_name = next_lg["name"]
        progress = "\n" + bar + " " + str(pct) + "% -> " + nxt_name
    sep = "=" * 20
    lines = [
        sep,
        "PROFIL DE " + username.upper(),
        sep,
        "",
        league["emoji"] + " Ligue: " + league["name"],
        "XP: " + str(xp) + progress,
        "",
        "Score: " + str(score) + " pts",
        "Rang mondial: #" + str(world_rank),
        "Pays: " + country_name,
        "PREMIUM" if is_prem else "Gratuit",
        "",
        "STATISTIQUES",
        "Parties: " + str(stats.get("games_played", 0)),
        "Mots trouves: " + str(stats.get("words_found", 0)),
        "Quiz reussis: " + str(stats.get("quiz_correct", 0)),
        "Duels gagnes: " + str(stats.get("duels_won", 0)),
        "Streak: " + str(stats.get("streak", 0)) + " jours",
        "",
        "BADGES",
        badge_display,
        sep,
    ]
    await update.message.reply_text("\n".join(lines))


async def jumble_level(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not await check_limit(update):
        return
    keyboard = [
        [InlineKeyboardButton("Facile (6-8 lettres, XP x1)", callback_data="jlvl_easy")],
        [InlineKeyboardButton("Moyen (8-10 lettres, XP x1.5)", callback_data="jlvl_medium")],
        [InlineKeyboardButton("Difficile (10-12 lettres, XP x2)", callback_data="jlvl_hard")],
        [InlineKeyboardButton("Insane - Premium (12-15 lettres, XP x3)", callback_data="jlvl_insane")],
    ]
    await update.message.reply_text(
        "JUMBLE - Choisissez la difficulte:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def jlvl_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    difficulty = query.data.replace("jlvl_", "")
    if difficulty == "insane" and not is_premium(user_id):
        await query.edit_message_text("Le mode Insane est reserve aux membres Premium!\n/premium")
        return
    chat_id = query.message.chat_id
    if user_id in jumble_sessions and jumble_sessions[user_id].get("active"):
        await query.edit_message_text("Partie en cours! Finissez-la d abord.")
        return
    letters, diff = generate_jumble_letters(difficulty)
    cfg = DIFFICULTY_CONFIG[difficulty]
    jumble_sessions[user_id] = {
        "letters":letters,"found_words":[],"active":True,
        "start_time":time.time(),"chat_id":chat_id,
        "username":query.from_user.first_name,"total_points":0,
        "difficulty":difficulty,"xp_earned":0,
    }
    update_stats(user_id, query.from_user.first_name, games_played=1)
    cfg_emoji = cfg["emoji"]
    cfg_mult = cfg["xp_mult"]
    diff_upper = difficulty.upper()
    await query.edit_message_text(
        "JUMBLE " + cfg_emoji + " " + diff_upper + "!\n\n"
        "Lettres: >>> " + letters + " <<<\n\n"
        "XP: x" + str(cfg_mult) + " | Points = lettres du mot\n"
        "3 minutes! C est parti!"
    )
    asyncio.create_task(jumble_level_timer(user_id, chat_id, context))

async def jumble_level_timer(user_id, chat_id, context):
    await asyncio.sleep(180)
    if user_id not in jumble_sessions or not jumble_sessions[user_id].get("active"):
        return
    session = jumble_sessions[user_id]
    session["active"] = False
    found = session["found_words"]
    points = session["total_points"]
    xp_earned = session.get("xp_earned", 0)
    username = session["username"]
    difficulty = session.get("difficulty", "medium")
    if points > 0:
        country = get_user_country(user_id)
        add_score(user_id, username, points, country)
        earned_xp, league, promoted = add_xp(user_id, username, xp_earned, difficulty)
        total = get_user_score(user_id)
        mots_str = ", ".join([w + "(" + str(len(normalize(w))) + ")" for w in found])
        league_emoji = league["emoji"]
        league_name = league["name"]
        msg = "Temps ecoule!\n\nMots: " + mots_str + "\n\n+" + str(points) + " pts | +" + str(earned_xp) + " XP\nScore: " + str(total) + " pts\nLigue: " + league_emoji + " " + league_name
        if promoted:
            msg += "\n\nPROMOTION! Bienvenue en " + league_emoji + " " + league_name + "!"
        msg += "\n\n/jumble pour rejouer!"
        await context.bot.send_message(chat_id=chat_id, text=msg)
    else:
        await context.bot.send_message(chat_id=chat_id, text="Temps ecoule! Aucun mot.\n/jumble pour reessayer!")
    del jumble_sessions[user_id]
