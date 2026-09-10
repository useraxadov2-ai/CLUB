import asyncio
import logging
import json
import re
import os

from aiogram import Bot, Dispatcher, F, BaseMiddleware
from aiogram.types import (
    Message, CallbackQuery, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
)
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardButton

import httpx
from dotenv import load_dotenv

from google import genai
from google.genai import types

load_dotenv()

# ==================== PREMIUM EMOJI ID LAR ====================
EMOJI_IDS = {
    "☕️":"5348559895111153311",
    "🚬": "5348192709767082803",
    "😎1" : "5323324376676850256",
    "🪽" : "5296389361158351746",
    "🍰": "5240208285528773246",
    "😀": "5967333011652350314",
    "🤖": "5258093637450866522",
    "🏘": "5257963315258204021",
    "📂": "5258514780469075716",
    "📅": "5258105663359294787",
    "⚡️": "5258152182150077732",
    "📍": "5258509201306557640",
    "💎": "5359719332542718652",
    "🍴": "5296727963495079440",
    "📰": "5249231689695115145",
    "🎮": "5258508428212445001",
    "👤": "5258362837411045098",
    "📞": "5258020476977946656",
    "🚪": "5258084656674250503",
    "⬅️": "5258236805890710909",
    "📝": "5257965174979042426",
    "🖼": "5257974976094412956",
    "🗑": "5258130763148172425",
    "✅": "5258057130228849960",
    "📌": "5258461531464539536",
    "🔢": "5226513232549664618",
    "⭐️": "5258185631355378853",
    "❌": "5258226313285607065",
    "⚽️": "5258169263235013408",
    "🐻": "5258145898612924124",
    "🪙": "5258368777350816286",
    "📖": "5258328383183396223",
    "💼": "5258260149037965799",
    "👨‍🎨": "5258450450448915742",
    "🗓": "5258105663359294787",
    "🤙": "5258337316715373336",
    "📸": "5258205968025525531",
    "👩‍🎨": "5258215635996908355",
    "📣": "5260268501515377807",
    "⛓️": "5260730055880876557",
    "📄": "5258477770735885832",
    "©": "5258507474729704350",
    "👥": "5258513401784573443",
    "✍️": "5258331647358540449",
    "↔️": "5260233433107407649",
    "🎭": "5258430848218176413",
    "📁": "5257965810634202885",
    "➡️": "5260450573768990626",
    "🎓": "5258334872878980409",
    "❤️": "5258179403652801593",
    "🚪": "5258084656674250503",
    "💡": "5258216851472654189",
    "🔒": "5258476306152038031",
    "💬": "5258215846450305872",
    "🌘": "5258011861273551368",
    "🎵": "5258289810082111221",
    "🔕": "5260264520080695245",
    "↗️": "5257991477358763590",
    "✈️": "5258115571848846212",
    "➕": "5258108352008823107",
    "🍑": "5258330865674494479",
    "🔫": "5260221883940347555",
    "👏": "5258501105293205250",
    "🔄": "5258420634785947640",
    "🌠": "5258212268742549391",
    "🔃": "5260687681733533075",
    "❗️": "5258474669769497337",
    "🤚": "5260249440450520061",
    "🗳": "5258200019495821936",
    "⬇️": "5258336354642697821",
    "🕔": "5258419835922030550",
    "⏲️": "5258258882022612173",
    "👀": "5260341314095947411",
    "⬆️": "5260652420052032852",
    "🔼": "5260379144167890225",
    "💻": "5258423306255604960",
    "ℹ️": "5258503720928288433",
    "🙂": "5258262708838472996",
    "🔇": "5258267368877989660",
    "📈": "5258391025281408576",
    "☀️": "5258089153505009279",
    "📚": "5260512129240276089",
    "📦": "5258134813302332906",
    "✋": "5258362429389152256",
    "📹": "5258077307985207053",
    "📼": "5258391252914676042",
    "🙃": "5258318251355545562",
    "🕘": "5199457120428249992",
    "🎙": "5260652149469094137",
    "💰": "5258204546391351475",
    "⚙️": "5258096772776991776",
    "♾️": "5271934788037517525",
    "🔊": "5260325873688518261",
    "🏷": "5296348778012361146",
    "🔎": "5429571366384842791",
    "👁": "5253959125838090076",
    "⛔️": "5275969776668134187",
    "🔞": "5325604415900504150",
    "🔖": "5359629206948976159",
}

# ==================== MENYU MAHSULOTLARI UCHUN PREMIUM EMOJI ID LAR ====================
# Har bir mahsulot (item_id) uchun tugmada ko'rsatiladigan premium emoji ID
PRODUCT_EMOJI_IDS = {
    "tuc": "5262667623002318450",
    "idish_qurt_assorti": "5260303767491880858",
    "lays_100_gr": "5262657534124145649",
    "anchous": "5260688716820686344",
    "keshyu": "5260660541835226955",
    "lays_140_gr": "5260300249913665054",
    "araxis": "5260383061178099475",
    "keshyu_ermak_40_gr": "5260512240909460935",
    "lays_225_gr": "5260740015910069355",
    "araxis_ermak_50_gr": "5260712240356565591",
    "kostochki": "5262540981596627764",
    "lays_70_gr": "5262598933590352279",
    "yongoq_assortisi": "5260632001777544692",
    "qurt_30_gr_zavq": "5260666786717675351",
    "pringles_165_gr": "5262546023888235255",
    "ermak_yongoq_assortisi_45_gr": "5262965521933970117",
    "qurt_ermak_30_gr": "5260229232629426314",
    "pringles_katta": "5262962322183333293",
    "bodom": "5260502053247033031",
    "qurt_ermak_60_gr": "5260220475191108521",
    "pringles_kichik": "5262652350098614260",
    "grenki": "5260500150576525267",
    "qurt_ixlos_assorti": "5262743394815354369",
    "pistashki": "5260717192453857924",
    "semechki_100_gr": "5262867772773280550",
    "pistashki_ermak_30_gr": "5262530351552570594",
    "semechki_160_gr": "5260406301246142657",
    "flint_suxariki": "5260427295046283417",
    "sirniye_palochki_suluguni": "5260331998311917842",
    "sirniye_palochki_150": "5260319890799112710",
    "sirniye_palochki_big_suluguni": "5262790871383842773",
    "tosh_qurt_30_gr_zavq": "5262868069126024561",
    "tosh_qurt_ixlos": "5262530098149498411",
    "18_plus": "5262583123815738090",
    "evian": "5262491271645143612",
    "bonaqua_gazsiz_0_5_l": "5260538899771466652",
    "barbican": "5260363102465074438",
    "gorilla": "5262558251660124572",
    "bonaqua_gazli_0_5_l": "5262836964972863265",
    "blanc_blue": "5262705392944720028",
    "pulpy": "5260568801333782866",
    "borjomi_0_5_l": "5260343624788387762",
    "chupa_chups": "5260761323242826864",
    "red_bull_0_25_l": "5260276563169029424",
    "borjomi_limonad": "5262563564534672552",
    "dovcha_green_0_5_l": "5260482416656559398",
    "rich_sharbati_1_l": "5262484043215186845",
    "kapuchino_qahva": "5260504282335061426",
    "dovcha_nok_0_5_l": "5262838210513381392",
    "royal": "5262535286469995459",
    "cola_0_25_l": "5260566623785364302",
    "dovcha_olcha_0_5_l": "5260519082792363495",
    "schweppes": "5262778617842146779",
    "cola_0_5_l": "5260296556241792479",
    "dovcha_xtra_0_33_l": "5262471682299307966",
    "americano_qahva": "5260267225910127260",
    "latte_qahva": "5262898735192522717",
    "limonad_tsitrus_marakuya_1_l": "5260456578133307238",
    "cola_1_l": "5260291939151949038",
    "limonad_mango_marakuya_0_5_l": "5262456778762794562",
    "limonad_tarxun_0_5_l": "5260338956158939828",
    "cola_jb_0_5_l": "5260528188123030137",
    "limonad_mango_marakuya_1_l": "5262683578805824180",
    "limonad_tarxun_1_l": "5262678489269577063",
    "cola_zero_0_25_l": "5260730012931237908",
    "limonad_mojito_klassik_0_5_l": "5262889977754198557",
    "mojito_0_33_l": "5260389353305190236",
    "cola_shisha": "5260684211399994981",
    "limonad_mojito_klassik_1_l": "5262917431185153361",
    "mojito_0_5_l": "5262769168914095451",
    "laymon_fresh_yashil_0_5_l": "5260422038006312286",
    "limonad_mojito_qulupnay_0_5_l": "5260352837493236772",
    "natakhtari": "5260675153313968608",
    "laymon_fresh_big": "5262991192953495372",
    "limonad_mojito_qulupnay_1_l": "5262995496510726395",
    "rich_0_2_l": "5260207238101905246",
    "laymon_fresh_shisha": "5260407070045287800",
    "limonad_tsitrus_marakuya_0_5_l": "5260214058509971911",
    "fanta_shisha": "5260589412881836579",
    "chortoq_0_5_l": "5260407602621231260",
    "sprite_0_25_l": "5260471060763030118",
    "fuze_tea_0_5_l_assorti": "5262818183080878868",
    "espresso_qahva": "5260400807982969415",
    "sprite_0_5_l": "5262831553314074151",
    "fuze_tea_1_l_assorti": "5262493818560752535",
    "sprite_1_l": "5260624519944513854",
    "fuze_tea_gazsiz": "5262934654004012262",
    "sprite_shisha": "5260690400447866000",
    "fuze_tea_gazsiz_250_ml": "5262840813263561967",
    "fanta_0_25_l": "5260504415479048656",
    "oddiy_choy": "5260759656795517540",
    "fanta_0_5_l": "5262877938960871210",
    "limonli_choy": "5262655682993234417",
    "fanta_1_l": "5262698009895939257",
    "chernogolovka_shisha": "5260275549556746022",
    "qoshimcha_limon": "5262889367868845601",
    "rezavor_tami": "5262524553346721158",
    "qoshimcha_shakar": "5260551166198068897",
    "haqiqiy_jentelmen_choyi": "5260732598501547896",
    "sokin_huzur": "5260748026024077398",
    "tropik_tam": "5262536454701098701",
    "sitrus_zarbasi": "5262817860958331723",
    "yaseminli_choy": "5262816705612128851",
    "earl_grey_cream_choyi": "5260467246832071283",
    "7_days": "5262832931998575578",
    "kitkat_mini": "5260342155909573502",
    "millenium_air": "5260577455692883162",
    "alpen_gold_max_fun": "5260299189056743439",
    "m_and_ms_sariq": "5260558536361947079",
    "millenium_gold": "5260730210499733181",
    "biscolata_stix": "5262969937160348640",
    "m_and_ms_qora": "5260547743109130157",
    "oreo": "5262600518433283859",
    "biscolata_pechenye": "5262794088314346681",
    "mars": "5260630511423890733",
    "oreo_big": "5262702794489501370",
    "bounty": "5263012951257817597",
    "merci_plitka": "5260238638607804546",
    "picnic": "5260584306165726231",
    "choco_pie_big": "5262565591759234823",
    "milka_brownie": "5260486290717062366",
    "ritter_sport": "5262772364369767521",
    "choco_pie_mini": "5260584593928531359",
    "milka_pechenye": "5260704402041253570",
    "skittles": "5260485899875040615",
    "florida_pechenye": "5262645508215709878",
    "milka_plitka": "5262868842220134966",
    "kinder_shokolad_mini": "5260600455242754097",
    "xottabich_premium": "5260471370000671783",
    "snickers": "5260675389537166630",
    "qahva_va_choy_pechenyesi": "5262498375521052845",
    "snickers_big_ormon_yongoqli": "5262926661069874636",
    "mamba": "5262699495954622749",
    "twix": "5262941723520181416",
    "marmelad": "5262563182282581138",
    "barni": "5262668597959894417",
    "shirin_yongoqchalar": "5262484923683480842",
    "kinder_bueno": "5260432625100696289",
    "pistali_yongoqchalar": "5262689153673374899",
    "kinder_delice": "5262617754137041317",
    "mevali_assorti": "5260748644499370700",
    "kinder_shokolad": "5262740272374128038",
    "xottabich": "5260519258886023419",
}

def wrap_emoji(emoji: str, text: str = None) -> str:
    """Matn ichidagi emojini premium <tg-emoji> tegi bilan o‘rab beradi."""
    if not text:
        text = emoji
    emoji_id = EMOJI_IDS.get(emoji)
    if emoji_id:
        return f'<tg-emoji emoji-id="{emoji_id}">{text}</tg-emoji>'
    return text

def replace_emojis_in_text(text: str) -> str:
    """Matndagi barcha maʼlum emojilarni premium teglar bilan almashtiradi."""
    for emoji, _ in EMOJI_IDS.items():
        if emoji in text:
            # Faqat butun emoji belgisini almashtiramiz (boshqa emojilar bilan adashmaslik uchun)
            text = text.replace(emoji, wrap_emoji(emoji))
    return text

# ==================== SOZLAMALAR ====================
BOT_TOKEN = os.getenv("BOT_TOKEN", "8647041435:AAEydQiH6qy9ytQ9-2O7s38ahcc-ykw7Sbo")
FIREBASE_DB_URL = os.getenv("FIREBASE_DB_URL", "https://injoygame-cba8a-default-rtdb.firebaseio.com/").rstrip("/")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "AQ.Ab8RN6JOYd6DcNYIYECcvWG7azASP4pmOMEoeuG9ttR-T0KC4A")
FIREBASE_AUTH = os.getenv("FIREBASE_AUTH", "AQ.Ab8RN6JOYd6DcNYIYECcvWG7azASP4pmOMEoeuG9ttR-T0KC4A")

AI_MODEL = "gemini-3-flash-preview"

# ⚠️ ADMIN_IDS endi to'plam (bir nechta admin ID qo'yish mumkin: {111, 222})
ADMIN_IDS = {5297746319}
# "Admin bilan Aloqa" bo'limidagi xabarlar shu ID'ga yuboriladi (admin shu yerdan Reply qilib javob beradi)
ADMIN_CONTACT_ID = 6147283506
MENU_ORDERS_CHAT_ID = -5171281890

# ⚠️ DIQQAT: https://t.me/+D3BdS7U0i9E2MWZi kanali uchun ID ni shu yerga yozishingiz shart.
# ID raqami -100 bilan boshlanishi kerak (Masalan: -1001234567890). Bot shu kanalga admin qilingan bo'lishi lozim!
CABIN_BOOKING_CHAT_ID = -1004401105554

# ℹ️ Rasmlar endi auto_images.json fayldan emas, FAQAT Firebase'dan olinadi.
# Kabina/mahsulot rasmi Firebase'dagi "image" maydonida saqlanadi va Admin panel
# orqali (✏️ tahrirlash > 🖼 Rasmi) istalgan vaqt yangilanishi mumkin.

FILE_ID_CACHE = {}
# "Admin bilan Aloqa" uchun: {admin_chatga_forward_qilingan_xabar_id: foydalanuvchi_id}
CONTACT_FORWARD_MAP = {}

CATEGORY_NAMES = {
    "gazaklar": "🍿 Gazaklar",
    "tamaki": "🚬 Tamaki mahsulotlari",
    "suvlar": "🥤 Suvlar",
    "choylar": "🍵 Choylar",
    "shirinliklar": "🍰 Shirinliklar"
}

MENU_SEED_ITEMS = {
    "gazaklar": [
        ("TUC", "tuc"), ("Idish qurt (assorti)", "idish_qurt_assorti"), ("Lays 100 gr", "lays_100_gr"),
        ("Anchous", "anchous"), ("Keshyu", "keshyu"), ("Lays 140 gr", "lays_140_gr"),
        ("Araxis", "araxis"), ("Keshyu Ermak 40 gr", "keshyu_ermak_40_gr"), ("Lays 225 gr", "lays_225_gr"),
        ("Araxis Ermak 50 gr", "araxis_ermak_50_gr"), ("Kostochki", "kostochki"), ("Lays 70 gr", "lays_70_gr"),
        ("Yong'oq assortisi", "yongoq_assortisi"), ("Qurt 30 gr Zavq", "qurt_30_gr_zavq"),
        ("Pringles 165 gr", "pringles_165_gr"), ("Ermak yong'oq assortisi 45 gr", "ermak_yongoq_assortisi_45_gr"),
        ("Qurt Ermak 30 gr", "qurt_ermak_30_gr"), ("Pringles katta", "pringles_katta"), ("Bodom", "bodom"),
        ("Qurt Ermak 60 gr", "qurt_ermak_60_gr"), ("Pringles kichik", "pringles_kichik"), ("Grenki", "grenki"),
        ("Qurt Ixlos (assorti)", "qurt_ixlos_assorti"), ("Pistashki", "pistashki"),
        ("Semechki 100 gr", "semechki_100_gr"), ("Pistashki Ermak 30 gr", "pistashki_ermak_30_gr"),
        ("Semechki 160 gr", "semechki_160_gr"), ("Flint suxariki", "flint_suxariki"),
        ("Sirniye palochki – Suluguni", "sirniye_palochki_suluguni"), ("Sirniye palochki 150", "sirniye_palochki_150"),
        ("Sirniye palochki Big – Suluguni", "sirniye_palochki_big_suluguni"),
        ("Tosh qurt 30 gr Zavq", "tosh_qurt_30_gr_zavq"), ("Tosh qurt Ixlos", "tosh_qurt_ixlos")
    ],
    "tamaki": [
        ("Terrea", "terrea"), ("Kalyan bonus", "kalyan_bonus"), ("Qo'shimcha ko'mir", "qoshimcha_komir"),
        ("Kola 1 L bonus", "kola_1_l_bonus"), ("Qo'shimcha kalyan chashkasi", "qoshimcha_kalyan_chashkasi"),
        ("Kalyan", "kalyan")
    ],
    "suvlar": [
        ("18+", "18_plus"), ("Evian", "evian"), ("BonAqua gazsiz 0.5 L", "bonaqua_gazsiz_0_5_l"),
        ("Barbican", "barbican"), ("Gorilla", "gorilla"), ("BonAqua gazli 0.5 L", "bonaqua_gazli_0_5_l"),
        ("Blanc Blue", "blanc_blue"), ("Pulpy", "pulpy"), ("Borjomi 0.5 L", "borjomi_0_5_l"),
        ("Chupa Chups", "chupa_chups"), ("Red Bull 0.25 L", "red_bull_0_25_l"), ("Borjomi limonad", "borjomi_limonad"),
        ("Dovcha Green 0.5 L", "dovcha_green_0_5_l"), ("Rich sharbati 1 L", "rich_sharbati_1_l"),
        ("Kapuchino (qahva)", "kapuchino_qahva"), ("Dovcha Nok 0.5 L", "dovcha_nok_0_5_l"), ("Royal", "royal"),
        ("Kola 0.25 L", "kola_0_25_l"), ("Dovcha Olcha 0.5 L", "dovcha_olcha_0_5_l"), ("Schweppes", "schweppes"),
        ("Kola 0.5 L", "kola_0_5_l"), ("Dovcha Xtra 0.33 L", "dovcha_xtra_0_33_l"),
        ("Americano (qahva)", "americano_qahva"), ("Latte (qahva)", "latte_qahva"),
        ("Limonad Tsitrus–Marakuya 1 L", "limonad_tsitrus_marakuya_1_l"), ("Kola 1 L", "kola_1_l"),
        ("Limonad Mango–Marakuya 0.5 L", "limonad_mango_marakuya_0_5_l"),
        ("Limonad Tarxun 0.5 L", "limonad_tarxun_0_5_l"), ("Kola JB 0.5 L", "kola_jb_0_5_l"),
        ("Limonad Mango–Marakuya 1 L", "limonad_mango_marakuya_1_l"), ("Limonad Tarxun 1 L", "limonad_tarxun_1_l"),
        ("Kola Zero 0.25 L", "kola_zero_0_25_l"), ("Limonad Mojito Klassik 0.5 L", "limonad_mojito_klassik_0_5_l"),
        ("Mojito 0.33 L", "mojito_0_33_l"), ("Kola (shisha)", "kola_shisha"),
        ("Limonad Mojito Klassik 1 L", "limonad_mojito_klassik_1_l"), ("Mojito 0.5 L", "mojito_0_5_l"),
        ("Laymon Fresh (yashil) 0.5 L", "laymon_fresh_yashil_0_5_l"),
        ("Limonad Mojito Qulupnay 0.5 L", "limonad_mojito_qulupnay_0_5_l"), ("Natakhtari", "natakhtari"),
        ("Laymon Fresh Big", "laymon_fresh_big"), ("Limonad Mojito Qulupnay 1 L", "limonad_mojito_qulupnay_1_l"),
        ("Rich 0.2 L", "rich_0_2_l"), ("Laymon Fresh (shisha)", "laymon_fresh_shisha"),
        ("Limonad Tsitrus–Marakuya 0.5 L", "limonad_tsitrus_marakuya_0_5_l"), ("Fanta (shisha)", "fanta_shisha"),
        ("Chortoq 0.5 L", "chortoq_0_5_l"), ("Sprite 0.25 L", "sprite_0_25_l"),
        ("Fuze Tea 0.5 L (assorti)", "fuze_tea_0_5_l_assorti"), ("Espresso (qahva)", "espresso_qahva"),
        ("Sprite 0.5 L", "sprite_0_5_l"), ("Fuze Tea 1 L (assorti)", "fuze_tea_1_l_assorti"),
        ("Sprite 1 L", "sprite_1_l"), ("Fuze Tea gazsiz", "fuze_tea_gazsiz"), ("Sprite (shisha)", "sprite_shisha"),
        ("Fuze Tea gazsiz 250 ml", "fuze_tea_gazsiz_250_ml"), ("Fanta 0.25 L", "fanta_0_25_l"),
        ("Oddiy choy", "oddiy_choy"), ("Fanta 0.5 L", "fanta_0_5_l"), ("Limonli choy", "limonli_choy"),
        ("Fanta 1 L", "fanta_1_l"), ("Chernogolovka (shisha)", "chernogolovka_shisha")
    ],
    "choylar": [
        ("Qo'shimcha limon", "qoshimcha_limon"), ("Rezavor ta'mi", "rezavor_tami"),
        ("Qo'shimcha shakar", "qoshimcha_shakar"), ("Haqiqiy Jentelmen choyi", "haqiqiy_jentelmen_choyi"),
        ("Sokin huzur", "sokin_huzur"), ("Tropik ta'm", "tropik_tam"), ("Sitrus zarbasi", "sitrus_zarbasi"),
        ("Yaseminli choy", "yaseminli_choy"), ("Earl Grey Cream choyi", "earl_grey_cream_choyi")
    ],
    "shirinliklar": [
        ("7 Days", "7_days"), ("KitKat Mini", "kitkat_mini"), ("Millenium Air", "millenium_air"),
        ("Alpen Gold Max & Fun", "alpen_gold_max_fun"), ("M&M's (sariq)", "m_and_ms_sariq"),
        ("Millenium Gold", "millenium_gold"), ("Biscolata Stix", "biscolata_stix"), ("M&M's (qora)", "m_and_ms_qora"),
        ("Oreo", "oreo"), ("Biscolata pechenye", "biscolata_pechenye"), ("Mars", "mars"), ("Oreo Big", "oreo_big"),
        ("Bounty", "bounty"), ("Merci (plitka)", "merci_plitka"), ("Picnic", "picnic"),
        ("Choco Pie Big", "choco_pie_big"), ("Milka Brownie", "milka_brownie"), ("Ritter Sport", "ritter_sport"),
        ("Choco Pie Mini", "choco_pie_mini"), ("Milka pechenye", "milka_pechenye"), ("Skittles", "skittles"),
        ("Florida pechenye", "florida_pechenye"), ("Milka (plitka)", "milka_plitka"),
        ("Kinder shokolad Mini", "kinder_shokolad_mini"), ("Xottabich Premium", "xottabich_premium"),
        ("Snickers", "snickers"), ("Qahva va choy pechenyesi", "qahva_va_choy_pechenyesi"),
        ("Snickers Big (o'rmon yong'oqli)", "snickers_big_ormon_yongoqli"), ("Mamba", "mamba"), ("Twix", "twix"),
        ("Marmelad", "marmelad"), ("Barni", "barni"), ("Shirin yong'oqchalar", "shirin_yongoqchalar"),
        ("Kinder Bueno", "kinder_bueno"), ("Pistali yong'oqchalar", "pistali_yongoqchalar"),
        ("Kinder Delice", "kinder_delice"), ("Mevali assorti", "mevali_assorti"),
        ("Kinder shokolad", "kinder_shokolad"), ("Xottabich", "xottabich")
    ]
}

DEFAULT_BONUSES_TEXT = (
    "🎁 <b>Bonuslar va Chegirmalar</b>\n\n"
    "🕐 <b>Soat 14:00 dan 18:00 gacha</b> kelgan mijozlarimiz uchun\n"
    "barcha kabina narxlariga <b>30% chegirma</b>!\n\n"
    "⏳ Shoshiling, imkoniyatni qo'ldan boy bermang!"
)
DEFAULT_NEWS_TEXT = (
    "📰 <b>Yangiliklar</b>\n\n"
    "🎮 <b>Yangi PS5 o'yinlari keldi!</b>\n\n"
    "✅ FIFA 25\n✅ GTA VI\n✅ Spider-Man 3\n\n"
    "🔥 Barchani taklif qilamiz!"
)
DEFAULT_TOURNAMENTS_TEXT = (
    "🏆 <b>Turnirlar</b>\n\n"
    "📝 Ro'yxatdan o'tish uchun adminga yozing!\n@aliakxmedov"
)
DEFAULT_CONTACT_TEXT = (
    "📍 <b>Manzil va Aloqa</b>\n\n"
    "📞 <b>Telefon:</b> +998950809009\n"
    "✈️ <b>Telegram:</b> @injoyuz\n"
    "📸 <b>Instagram:</b> @injoy_uz\n\n"
    "👨‍💼 <b>Bot bo'yicha admin:</b> @aliakxmedov\n\n"
    "🗺️ <b>Manzil:</b>\n41°17'38.8\"N 69°14'43.8\"E\n"
    "📍 <a href='https://www.google.com/maps?q=41.294106,69.245491&z=16'>Google Maps da ko'rish</a>"
)

AI_SYSTEM_PROMPT = (
    "Sen InjoyUZ o'yin klubining AI yordamchisisan. Har doim o'zbek tilida, "
    "samimiy, qisqa va do'stona uslubda javob ber. Bu klubda PS5 konsolli kabinalar "
    "ijaraga beriladi hamda gazaklar, ichimliklar va tamaki mahsulotlari sotiladi."
)

# ==================== FSM HOLATLARI ====================
class BookingStates(StatesGroup):
    choosing_cabin = State()
    choosing_room = State()
    entering_time = State()

class QuickBookingStates(StatesGroup):
    choosing_cabin = State()
    entering_time = State()

class MenuOrderStates(StatesGroup):
    entering_room = State()
    entering_quantity = State()

class AiChatStates(StatesGroup):
    chatting = State()

class AdminCabinEditStates(StatesGroup):
    waiting_value = State()

class AdminMenuStates(StatesGroup):
    waiting_name = State()
    waiting_price = State()
    waiting_image = State()
    waiting_edit_value = State()

class AdminTextStates(StatesGroup):
    waiting_text = State()

class ContactAdminStates(StatesGroup):
    chatting = State()

# ==================== FIREBASE (REST orqali, async) ====================
http_client = httpx.AsyncClient(timeout=15)

def _fb_url(path: str) -> str:
    auth_part = f"?auth={FIREBASE_AUTH}" if FIREBASE_AUTH else ""
    return f"{FIREBASE_DB_URL}/{path}.json{auth_part}"

async def fb_get(path: str):
    try:
        r = await http_client.get(_fb_url(path))
        r.raise_for_status()
        return r.json()
    except Exception:
        logging.exception("Firebase'dan o'qishda xatolik: %s", path)
        return None

async def fb_set(path: str, data):
    r = await http_client.put(_fb_url(path), json=data)
    r.raise_for_status()
    return r.json()

async def fb_update(path: str, data: dict):
    r = await http_client.patch(_fb_url(path), json=data)
    r.raise_for_status()
    return r.json()

async def fb_push(path: str, data):
    r = await http_client.post(_fb_url(path), json=data)
    r.raise_for_status()
    return r.json()

async def fb_delete(path: str):
    r = await http_client.delete(_fb_url(path))
    r.raise_for_status()
    return True

def slugify(text: str) -> str:
    text = text.strip().lower().replace("'", "").replace("’", "")
    text = re.sub(r"[^a-z0-9]+", "_", text)
    return text.strip("_") or "mahsulot"

def is_admin(user_id: int) -> bool:
    return user_id in ADMIN_IDS

async def seed_database():
    if await fb_get("cabins") is None:
        cabins_seed = {
            # ℹ️ Rasm maydoni bo'sh boshlanadi — kabina rasmini Admin panel orqali
            # (yoki to'g'ridan-to'g'ri Firebase'da) keyinroq qo'shasiz, chunki rasmlar
            # endi faqat Firebase'dan olinadi, lokal fayldan emas.
            "mini": {"name": "Mini Kabina", "emoji": "🟢", "capacity": "5 kishigacha",
                     "price": "70 000 so'm / soat", "equipment": "PS5 konsol, 4K TV",
                     "total": "4 ta Mini Kabina", "rooms": [1, 2, 3, 4], "image": ""},
            "standard": {"name": "Standard Kabina", "emoji": "🔵", "capacity": "8 kishigacha",
                         "price": "100 000 so'm / soat", "equipment": "PS5 konsol, 4K TV, ovoz tizimi",
                         "total": "3 ta Standard Kabina", "rooms": [5, 6, 7], "image": ""},
            "vip": {"name": "VIP Kabina", "emoji": "🟣", "capacity": "15 kishigacha",
                    "price": "160 000 so'm / soat", "equipment": "PS5 konsol, 4K TV, ovoz tizimi, mini-bar",
                    "total": "2 ta VIP Kabina", "rooms": [8, 9], "image": ""},
        }
        await fb_set("cabins", cabins_seed)
        logging.info("✅ Kabinalar bazaga yozildi")

    if await fb_get("room_status") is None:
        room_status_seed = {
            "mini": {"1": "band", "2": "band", "3": "bo'sh", "4": "bo'sh"},
            "standard": {"5": "bo'sh", "6": "bo'sh", "7": "bo'sh"},
            "vip": {"8": "bo'sh", "9": "bo'sh"},
        }
        await fb_set("room_status", room_status_seed)
        logging.info("✅ Xonalar holati bazaga yozildi")

    menu_data = await fb_get("menu")
    if menu_data is None or menu_data == {} or not any(menu_data.values()):
        # ℹ️ Faqat Firebase'da menyu umuman bo'lmagan holatda (birinchi ishga tushirishda)
        # boshlang'ich ro'yxat sifatida yoziladi — rasmlar bo'sh, keyin admin panelda
        # yoki to'g'ridan-to'g'ri Firebase'da to'ldiriladi.
        menu_seed = {}
        for category_key, items in MENU_SEED_ITEMS.items():
            menu_seed[category_key] = {
                item_key: {"name": name, "price": "", "image": ""}
                for name, item_key in items
            }
        await fb_set("menu", menu_seed)
        logging.info("✅ Menyu bazaga yozildi (narxlar va rasmlar bo'sh — admin panelda to'ldiring!)")

    if await fb_get("texts") is None:
        await fb_set("texts", {
            "bonuses": DEFAULT_BONUSES_TEXT,
            "news": DEFAULT_NEWS_TEXT,
            "tournaments": DEFAULT_TOURNAMENTS_TEXT,
            "contact": DEFAULT_CONTACT_TEXT,
        })
        logging.info("✅ Matnlar bazaga yozildi")

async def build_room_summary() -> str:
    cabins = await fb_get("cabins") or {}
    room_status = await fb_get("room_status") or {}
    lines = []
    for key in ("mini", "standard", "vip"):
        cab = cabins.get(key)
        if not cab:
            continue
        statuses = room_status.get(key, {})
        if isinstance(statuses, list):
            statuses = {str(i+1): v for i, v in enumerate(statuses)}
        free = [r for r, s in statuses.items() if s == "bo'sh"]
        busy = [r for r, s in statuses.items() if s == "band"]
        lines.append(
                f"{cab.get('emoji', '')} {cab.get('name', key)}: "
                f"bo'sh — {', '.join(sorted(free)) or 'yo‘q'}; "
                f"band — {', '.join(sorted(busy)) or 'yo‘q'}"
            )   
    return "\n".join(lines) if lines else "Ma'lumot topilmadi"

async def search_menu_item(query: str):
    query_norm = query.strip().lower()
    if not query_norm:
        return None, None, None
    menu = await fb_get("menu") or {}
    for category_key, items in menu.items():
        if not items:
            continue
        for item_id, item in items.items():
            name = (item or {}).get("name", "")
            if query_norm in name.lower():
                return category_key, item_id, item
    return None, None, None

# ==================== GEMINI AI ====================
ai_client = genai.Client(api_key=GEMINI_API_KEY) if GEMINI_API_KEY else None

# ==================== KLAVIATURALAR ====================

def main_menu():
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text=" AI Yordamchi",
            callback_data="ai_start",
            icon_custom_emoji_id=EMOJI_IDS.get("🤖")
        )
    )
    builder.row(
        InlineKeyboardButton(
            text=" Xonalar va Narxlar",
            callback_data="rooms_prices",
            icon_custom_emoji_id=EMOJI_IDS.get("🏘")
        ),
        InlineKeyboardButton(
            text=" Bo'sh Joylar",
            callback_data="empty_places",
            icon_custom_emoji_id=EMOJI_IDS.get("📂")
        )
    )
    builder.row(
        InlineKeyboardButton(
            text=" Joy Bron Qilish",
            callback_data="booking",
            icon_custom_emoji_id=EMOJI_IDS.get("📅")
        ),
        InlineKeyboardButton(
            text=" Tez-kor Bron",
            callback_data="quick_booking",
            icon_custom_emoji_id=EMOJI_IDS.get("⚡️")
        )
    )
    builder.row(
        InlineKeyboardButton(
            text=" Manzil va Aloqa",
            callback_data="contact",
            icon_custom_emoji_id=EMOJI_IDS.get("📍")
        ),
        InlineKeyboardButton(
            text=" Bonuslar va Chegirmalar",
            callback_data="bonuses",
            icon_custom_emoji_id=EMOJI_IDS.get("💎")
        )
    )
    builder.row(
        InlineKeyboardButton(
            text=" Menyu",
            callback_data="menu",
            icon_custom_emoji_id=EMOJI_IDS.get("🍴")
        ),
        InlineKeyboardButton(
            text=" Yangiliklar",
            callback_data="news",
            icon_custom_emoji_id=EMOJI_IDS.get("📰")
        )
    )
    builder.row(
        InlineKeyboardButton(
            text=" Turnirlar",
            callback_data="tournaments",
            icon_custom_emoji_id=EMOJI_IDS.get("🎮")
        ),
        InlineKeyboardButton(
            text=" Profil",
            callback_data="profile",
            icon_custom_emoji_id=EMOJI_IDS.get("👤")
        )
    )
    builder.row(
        InlineKeyboardButton(
            text=" Admin bilan Aloqa",
            callback_data="contact_admin",
            icon_custom_emoji_id=EMOJI_IDS.get("📞")
        )
    )
    builder.row(
    InlineKeyboardButton(
        text=(
            "Qulay buyurtma"
        ),
        url="https://t.me/uzinjoy_robot/opn?startapp=uz",
        icon_custom_emoji_id=EMOJI_IDS.get("😀")
    )
    )

    return builder.as_markup()

def cabin_types(prefix):
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="🟢 Mini Kabina", callback_data=f"{prefix}_mini"),
        InlineKeyboardButton(text="🔵 Standard Kabina", callback_data=f"{prefix}_standard"),
        InlineKeyboardButton(text="🟣 VIP Kabina", callback_data=f"{prefix}_vip")
    )
    builder.row(
        InlineKeyboardButton(
            text="⬅️ Bosh Menyu",
            callback_data="main_menu",
            icon_custom_emoji_id=EMOJI_IDS.get("⬅️")
        )
    )
    return builder.as_markup()

def select_room(cabin_type, rooms):
    builder = InlineKeyboardBuilder()
    row_buttons = []
    for room in rooms:
        row_buttons.append(
            InlineKeyboardButton(
                text=f"🚪 Q #{room}",
                callback_data=f"room_{cabin_type}_{room}",
                icon_custom_emoji_id=EMOJI_IDS.get("🚪")
            )
        )
    for i in range(0, len(row_buttons), 2):
        if i + 1 < len(row_buttons):
            builder.row(row_buttons[i], row_buttons[i + 1])
        else:
            builder.row(row_buttons[i])
    builder.row(
        InlineKeyboardButton(
            text="️ Orqaga",
            callback_data="back_rooms",
            icon_custom_emoji_id=EMOJI_IDS.get("⬅️")
        ),
        InlineKeyboardButton(
            text=" Bosh Menyu",
            callback_data="main_menu",
            icon_custom_emoji_id=EMOJI_IDS.get("🏘")
        )
    )
    return builder.as_markup()

def cabin_detail_action_keyboard(cabin_key):
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text="📅 Bron qilish",
            callback_data=f"action_book_{cabin_key}",
            icon_custom_emoji_id=EMOJI_IDS.get("📅")
        )
    )
    builder.row(
        InlineKeyboardButton(
            text="️ Orqaga",
            callback_data="back_rooms",
            icon_custom_emoji_id=EMOJI_IDS.get("⬅️")
        ),
        InlineKeyboardButton(
            text=" Bosh Menyu",
            callback_data="main_menu",
            icon_custom_emoji_id=EMOJI_IDS.get("🏘")
        )
    )
    return builder.as_markup()

def menu_categories():
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="Gazaklar", callback_data="menu_gazaklar",icon_custom_emoji_id=EMOJI_IDS.get("😎1")),
        InlineKeyboardButton(text="Tamaki", callback_data="menu_tamaki",icon_custom_emoji_id=EMOJI_IDS.get("🚬"))
    )
    builder.row(
        InlineKeyboardButton(text="Suvlar", callback_data="menu_suvlar",icon_custom_emoji_id=EMOJI_IDS.get("🪽")),
        InlineKeyboardButton(text=" Choylar", callback_data="menu_choylar",icon_custom_emoji_id=EMOJI_IDS.get("☕"))
    )
    builder.row(InlineKeyboardButton(text="Shirinliklar", callback_data="menu_shirinliklar",icon_custom_emoji_id=EMOJI_IDS.get("🍰")))
    builder.row(
        InlineKeyboardButton(
            text="️ Bosh Menyu",
            callback_data="main_menu",
            icon_custom_emoji_id=EMOJI_IDS.get("⬅️")
        )
    )
    return builder.as_markup()

def menu_items_buttons(category_key, items: dict):
    builder = InlineKeyboardBuilder()
    entries = sorted((items or {}).items(), key=lambda kv: (kv[1] or {}).get("name", ""))
    row = []
    for item_id, item in entries:
        name = (item or {}).get("name", item_id)
        emoji_id = PRODUCT_EMOJI_IDS.get(item_id)
        btn_text = f" {name}" if emoji_id else name
        row.append(InlineKeyboardButton(text=btn_text, callback_data=f"item::{category_key}::{item_id}", icon_custom_emoji_id=emoji_id))
        if len(row) == 2:
            builder.row(*row)
            row = []
    if row:
        builder.row(*row)
    builder.row(
        InlineKeyboardButton(
            text="️ Orqaga",
            callback_data="menu",
            icon_custom_emoji_id=EMOJI_IDS.get("⬅️")
        )
    )
    builder.row(
        InlineKeyboardButton(
            text=" Bosh Menyu",
            callback_data="main_menu",
            icon_custom_emoji_id=EMOJI_IDS.get("🏘")
        )
    )
    return builder.as_markup()

def back_to_menu():
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text=" Bosh Menyu",
            callback_data="main_menu",
            icon_custom_emoji_id=EMOJI_IDS.get("⬅️")
        )
    )
    return builder.as_markup()

def item_detail_keyboard(category_key, item_id):
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text="🛒 Buyurtma berish",
            callback_data=f"order::{category_key}::{item_id}"
        )
    )
    builder.row(
        InlineKeyboardButton(
            text=" Orqaga",
            callback_data=f"menu_{category_key}",
            icon_custom_emoji_id=EMOJI_IDS.get("⬅️")
        )
    )
    builder.row(
        InlineKeyboardButton(
            text=" Bosh Menyu",
            callback_data="main_menu",
            icon_custom_emoji_id=EMOJI_IDS.get("🏘")
        )
    )
    return builder.as_markup()

def admin_main_menu():
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text="🏘 Kabinalarni tahrirlash",
            callback_data="adm_cabins",
            icon_custom_emoji_id=EMOJI_IDS.get("🏘")
        )
    )
    builder.row(
        InlineKeyboardButton(
            text="🚪 Xonalar holatini boshqarish",
            callback_data="adm_rooms",
            icon_custom_emoji_id=EMOJI_IDS.get("🚪")
        )
    )
    builder.row(
        InlineKeyboardButton(
            text="🍴 Menyuni boshqarish",
            callback_data="adm_menu",
            icon_custom_emoji_id=EMOJI_IDS.get("🍴")
        )
    )
    builder.row(
        InlineKeyboardButton(
            text="📝 Matnlarni tahrirlash",
            callback_data="adm_texts",
            icon_custom_emoji_id=EMOJI_IDS.get("📝")
        )
    )
    return builder.as_markup()

def admin_cabin_detail_keyboard(cabin_key):
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="✏️ Narxi", callback_data=f"admcabfield::{cabin_key}::price")
    )
    builder.row(
        InlineKeyboardButton(text="✏️ Sig'imi", callback_data=f"admcabfield::{cabin_key}::capacity")
    )
    builder.row(
        InlineKeyboardButton(text="✏️ Jihozlari", callback_data=f"admcabfield::{cabin_key}::equipment")
    )
    builder.row(
        InlineKeyboardButton(
            text="🖼 Rasmi (link)",
            callback_data=f"admcabfield::{cabin_key}::image",
            icon_custom_emoji_id=EMOJI_IDS.get("🖼")
        )
    )
    builder.row(
        InlineKeyboardButton(
            text="⬅️ Orqaga",
            callback_data="adm_cabins",
            icon_custom_emoji_id=EMOJI_IDS.get("⬅️")
        )
    )
    return builder.as_markup()

def admin_menu_item_keyboard(category_key, item_id):
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="✏️ Nomi", callback_data=f"admitemfield::{category_key}::{item_id}::name")
    )
    builder.row(
        InlineKeyboardButton(text="✏️ Narxi", callback_data=f"admitemfield::{category_key}::{item_id}::price")
    )
    builder.row(
        InlineKeyboardButton(
            text="🖼 Rasmi (link)",
            callback_data=f"admitemfield::{category_key}::{item_id}::image",
            icon_custom_emoji_id=EMOJI_IDS.get("🖼")
        )
    )
    builder.row(
        InlineKeyboardButton(
            text="🗑 O'chirish",
            callback_data=f"admitemdel::{category_key}::{item_id}",
            icon_custom_emoji_id=EMOJI_IDS.get("🗑")
        )
    )
    builder.row(
        InlineKeyboardButton(
            text="⬅️ Orqaga",
            callback_data=f"admmenucat::{category_key}",
            icon_custom_emoji_id=EMOJI_IDS.get("⬅️")
        )
    )
    return builder.as_markup()

# ==================== BOT ====================
logging.basicConfig(level=logging.INFO)

bot = Bot(
    token=BOT_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)
dp = Dispatcher()

# ==================== RO'YXATDAN O'TISHNI TEKSHIRISH (MIDDLEWARE) ====================
def _contact_request_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="📱 Raqamni ulashish", request_contact=True)]],
        resize_keyboard=True,
        one_time_keyboard=True
    )

class RegistrationMiddleware(BaseMiddleware):
    async def __call__(self, handler, event, data):
        user = None
        if isinstance(event, Message):
            user = event.from_user
            if event.text and event.text.startswith("/start"):
                return await handler(event, data)
            if event.contact:
                return await handler(event, data)
        elif isinstance(event, CallbackQuery):
            user = event.from_user
        else:
            return await handler(event, data)

        if user is None:
            return await handler(event, data)

        # Admin(lar) va "Admin bilan Aloqa" javob beruvchi shaxs ro'yxatdan o'tishi shart emas
        if user.id == ADMIN_CONTACT_ID or is_admin(user.id):
            return await handler(event, data)

        user_data = await fb_get(f"users/{user.id}")
        if not user_data or not user_data.get("phone"):
            if isinstance(event, CallbackQuery):
                await event.answer()
                target = event.message
            else:
                target = event
            await target.answer(
                "⚠️ Avval ro'yxatdan o'ting.\nDavom etish uchun telefon raqamingizni ulashing 👇",
                reply_markup=_contact_request_keyboard()
            )
            return

        return await handler(event, data)

dp.message.middleware(RegistrationMiddleware())
dp.callback_query.middleware(RegistrationMiddleware())

# ==================== YORDAMCHI: XAVFSIZ TAHRIRLASH ====================
async def safe_edit(callback: CallbackQuery, text: str, reply_markup=None, disable_web_page_preview=None):
    # Matndagi emojilarni premium teglarga almashtiramiz
    text = replace_emojis_in_text(text)
    if callback.message.photo:
        await callback.message.delete()
        await callback.message.answer(text, reply_markup=reply_markup, disable_web_page_preview=disable_web_page_preview)
    else:
        await callback.message.edit_text(text, reply_markup=reply_markup, disable_web_page_preview=disable_web_page_preview)

async def send_product_card(message: Message, category_key: str, item_id: str, item: dict):
    name = item.get("name", item_id)
    price = item.get("price") or "Narx belgilanmagan"
    image = item.get("image", "")
    text = (
        f"📦 <b>{name}</b>\n\n"
        f"📂 Kategoriya: {CATEGORY_NAMES.get(category_key, category_key)}\n"
        f"💰 Narx: {price}\n"
    )
    text = replace_emojis_in_text(text)
    cache_key = f"item_{item_id}"
    if image and image.startswith("http"):
        photo_source = FILE_ID_CACHE.get(cache_key, image)
        sent = await message.answer_photo(
            photo=photo_source,
            caption=text,
            reply_markup=item_detail_keyboard(category_key, item_id)
        )
        if cache_key not in FILE_ID_CACHE and sent.photo:
            FILE_ID_CACHE[cache_key] = sent.photo[-1].file_id
    else:
        text += "\n⚠️ Rasm mavjud emas"
        await message.answer(text, reply_markup=item_detail_keyboard(category_key, item_id))

# ==================== RO'YXATDAN O'TISH ====================
@dp.message(Command("start"))
async def start(message: Message):
    user_data = await fb_get(f"users/{message.from_user.id}")
    if user_data and user_data.get("phone"):
        await message.answer(
            replace_emojis_in_text(
                "🎮 <b>InJoy Gaming Club</b> ga xush kelibsiz!\n\nKerakli bo'limni tanlang 👇"
            ),
            reply_markup=main_menu()
        )
    else:
        await message.answer(
            replace_emojis_in_text(
                "👋 Assalomu alaykum! <b>InJoy Gaming Club</b> botiga xush kelibsiz.\n\n"
                "Davom etish uchun telefon raqamingizni ulashing 👇"
            ),
            reply_markup=_contact_request_keyboard()
        )

@dp.message(F.contact)
async def handle_contact(message: Message):
    contact = message.contact
    if contact.user_id and contact.user_id != message.from_user.id:
        await message.answer("⚠️ Iltimos, faqat o'zingizning raqamingizni ulashing.")
        return

    await fb_set(f"users/{message.from_user.id}", {
        "phone": contact.phone_number,
        "full_name": message.from_user.full_name,
        "username": message.from_user.username or "",
    })
    await message.answer("✅ Ro'yxatdan muvaffaqiyatli o'tdingiz!", reply_markup=ReplyKeyboardRemove())
    await message.answer(
        replace_emojis_in_text(
            "🎮 <b>InJoy Gaming Club</b>\n\nKerakli bo'limni tanlang 👇"
        ),
        reply_markup=main_menu()
    )

@dp.callback_query(F.data == "main_menu")
async def back_to_main(callback: CallbackQuery):
    await callback.answer()
    await callback.message.delete()
    await callback.message.answer(
        replace_emojis_in_text(
            "🎮 <b>InJoy Gaming Club</b>\n\nKerakli bo'limni tanlang 👇"
        ),
        reply_markup=main_menu()
    )

# ==================== AI YORDAMCHI ====================
@dp.callback_query(F.data == "ai_start")
async def ai_start(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.set_state(AiChatStates.chatting)
    await state.update_data(history=[])

    if ai_client is None:
        await safe_edit(callback, text="🤖 AI yordamchi hozircha sozlanmagan (GEMINI_API_KEY yo'q).", reply_markup=back_to_menu())
        return

    greeting_text = "Salom! Men InjoyUZ AI yordamchiman 🤖 Kayfiyatingiz qanday?"
    try:
        greeting_resp = await ai_client.aio.models.generate_content(
            model=AI_MODEL,
            contents=(
                "Foydalanuvchi endigina 'AI Yordamchi' bo'limini ochdi. Salom ber, "
                "InjoyUZ o'yin klubining AI yordamchisi ekaningni ayt, kayfiyati qanday "
                "ekanligini, qanday o'yin o'ynashni va nima yeb-ichishni xohlashini so'ra. "
                "4-6 gapdan oshmasin."
            ),
            config=types.GenerateContentConfig(system_instruction=AI_SYSTEM_PROMPT, temperature=0.8),
        )
        if greeting_resp.text:
            greeting_text = greeting_resp.text
    except Exception:
        logging.exception("Gemini orqali salomlashishda xatolik")

    room_summary = await build_room_summary()
    full_text = f"{greeting_text}\n\n🪑 <b>Hozirgi holat:</b>\n{room_summary}"
    await safe_edit(callback, text=full_text, reply_markup=back_to_menu())

@dp.message(StateFilter(AiChatStates.chatting))
async def ai_chat(message: Message, state: FSMContext):
    if ai_client is None:
        await message.answer("🤖 AI yordamchi hozircha sozlanmagan.")
        return

    data = await state.get_data()
    history = data.get("history", [])
    room_summary = await build_room_summary()

    prompt = (
        f'Foydalanuvchi xabari: "{message.text}"\n\n'
        f"Hozirgi xonalar holati:\n{room_summary}\n\n"
        "Agar foydalanuvchi biror ovqat/ichimlik/gazak yemoqchi/ichmoqchi yoki "
        "buyurtma bermoqchi bo'lsa, FAQAT quyidagi JSON qaytar:\n"
        '{"type": "product_search", "query": "mahsulot nomi", "text": "qisqa javob"}\n\n'
        "Aks holda oddiy suhbat uchun FAQAT quyidagi JSON qaytar:\n"
        '{"type": "chat", "text": "javob matni"}\n\n'
        "Boshqa hech narsa yozma, faqat sof JSON."
    )

    resp = None
    parsed = {"type": "chat", "text": "Kechirasiz, hozir javob bera olmadim. Qaytadan urinib ko'ring."}
    try:
        resp = await ai_client.aio.models.generate_content(
            model=AI_MODEL,
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=AI_SYSTEM_PROMPT,
                response_mime_type="application/json",
                temperature=0.6,
            ),
        )
        resp_text = resp.text or "{}"
        json_match = re.search(r'\{.*\}', resp_text, re.DOTALL)
        if json_match:
            resp_text = json_match.group()
        parsed = json.loads(resp_text)
    except Exception:
        logging.exception("Gemini javobida xatolik")
        if resp is not None and getattr(resp, "text", None):
            parsed = {"type": "chat", "text": resp.text[:500]}

    msg_type = parsed.get("type", "chat")

    if msg_type == "product_search":
        query = parsed.get("query", message.text)
        category_key, item_id, item = await search_menu_item(query)
        if item:
            reply_text = parsed.get("text") or f"Mana, topdim: {item.get('name')}"
            await message.answer(reply_text)
            await send_product_card(message, category_key, item_id, item)
        else:
            await message.answer(parsed.get("text") or f'Kechirasiz, "{query}" nomli mahsulot topilmadi 😔')
    else:
        await message.answer(parsed.get("text", "..."))

    history.append({"role": "user", "text": message.text})
    history.append({"role": "assistant", "text": json.dumps(parsed, ensure_ascii=False)})
    await state.update_data(history=history[-10:])

# ---------- XONALAR VA NARXLAR ----------
@dp.callback_query(F.data == "rooms_prices")
async def rooms_prices(callback: CallbackQuery):
    await callback.answer()
    cabins = await fb_get("cabins") or {}
    text = "🏠 <b>Kabinalar va Narxlar</b>\n\n"
    for key in ("mini", "standard", "vip"):
        data = cabins.get(key)
        if not data:
            continue
        text += f"{data.get('emoji', '')} <b>{data.get('name', key)}</b>\n"
        text += f"├ 👥 Sig'im: {data.get('capacity', '-')}\n"
        text += f"└ 💰 Narx: {data.get('price', '-')}\n\n"
    text += "\n📌 <b>Batafsil ma'lumot uchun kabinani tanlang</b> 👇"
    await safe_edit(callback, text=text, reply_markup=cabin_types("detail"))

@dp.callback_query(F.data.startswith("detail_"))
async def cabin_detail(callback: CallbackQuery):
    await callback.answer()
    cabin_key = callback.data.split("_")[1]
    cabin = await fb_get(f"cabins/{cabin_key}") or {}

    text = f"🏠 <b>{cabin.get('name', cabin_key)} — Batafsil</b>\n\n"
    text += f"👥 Sig'im: {cabin.get('capacity', '-')}\n"
    text += f"💰 Narx: {cabin.get('price', '-')}\n"
    text += f"🎮 Jihozlar: {cabin.get('equipment', '-')}\n"
    text += f"📊 Jami: {cabin.get('total', '-')}\n"

    image = cabin.get("image", "")
    cache_key = f"cabin_{cabin_key}"
    if image and image.startswith("http"):
        try:
            await callback.message.delete()
            photo_source = FILE_ID_CACHE.get(cache_key, image)
            sent = await callback.message.answer_photo(
                photo=photo_source, caption=replace_emojis_in_text(text), reply_markup=cabin_detail_action_keyboard(cabin_key)
            )
            if cache_key not in FILE_ID_CACHE and sent.photo:
                FILE_ID_CACHE[cache_key] = sent.photo[-1].file_id
        except Exception:
            logging.exception("Kabina rasmini yuborishda xatolik: %s", image)
            FILE_ID_CACHE.pop(cache_key, None)
            await callback.message.answer(replace_emojis_in_text(text), reply_markup=cabin_detail_action_keyboard(cabin_key))
    else:
        await safe_edit(callback, text=text, reply_markup=cabin_detail_action_keyboard(cabin_key))

@dp.callback_query(F.data.startswith("action_book_"))
async def action_book_from_detail(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    cabin_key = callback.data.split("_", 2)[2]
    await state.update_data(cabin_type=cabin_key)
    await state.set_state(BookingStates.choosing_room)
    cabin = await fb_get(f"cabins/{cabin_key}") or {}
    text = f"📅 <b>{cabin.get('name', cabin_key)} — Xona Tanlang</b>\n\nQaysi xonani bronlamoqchisiz?"
    await safe_edit(callback, text=text, reply_markup=select_room(cabin_key, cabin.get("rooms", [])))

# ---------- BO'SH JOYLAR ----------
@dp.callback_query(F.data == "empty_places")
async def empty_places(callback: CallbackQuery):
    await callback.answer()
    await safe_edit(callback, text="🪑 <b>Bo'sh Joylar</b>\n\nKabina turini tanlang 👇", reply_markup=cabin_types("empty"))

@dp.callback_query(F.data.startswith("empty_"))
async def show_empty_places(callback: CallbackQuery):
    await callback.answer()
    cabin_key = callback.data.split("_")[1]
    statuses = await fb_get(f"room_status/{cabin_key}") or {}
    cabin = await fb_get(f"cabins/{cabin_key}") or {}

    if isinstance(statuses, list):
        statuses = {str(i+1): v for i, v in enumerate(statuses)}

    text = f"🪑 <b>{cabin.get('name', cabin_key)} — Bo'sh holat</b>\n\n"
    for room, status in sorted(statuses.items()):
        emoji = "🟢" if status == "bo'sh" else "🔴"
        text += f"{emoji} Kabina #{room} — <b>{status}</b>\n"
    text += "\n🟢 Bo'sh | 🔴 Band"

    await safe_edit(callback, text=text, reply_markup=cabin_types("empty"))

# ---------- BRON QILISH ----------
@dp.callback_query(F.data == "booking")
async def start_booking(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.set_state(BookingStates.choosing_cabin)
    await safe_edit(callback, text="📅 <b>Joy Bron Qilish</b>\n\nKabina turini tanlang 🎵", reply_markup=cabin_types("book"))

@dp.callback_query(F.data.startswith("book_"), StateFilter(BookingStates.choosing_cabin))
async def choose_room(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    cabin_key = callback.data.split("_")[1]
    await state.update_data(cabin_type=cabin_key)
    await state.set_state(BookingStates.choosing_room)
    cabin = await fb_get(f"cabins/{cabin_key}") or {}
    text = f"📅 <b>{cabin.get('name', cabin_key)} — Xona Tanlang</b>\n\nQaysi xonani bronlamoqchisiz?"
    await safe_edit(callback, text=text, reply_markup=select_room(cabin_key, cabin.get("rooms", [])))

@dp.callback_query(F.data.startswith("room_"), StateFilter(BookingStates.choosing_room))
async def select_time(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    _, cabin_key, room_number = callback.data.split("_")
    await state.update_data(cabin=cabin_key, room=room_number)
    await state.set_state(BookingStates.entering_time)
    cabin = await fb_get(f"cabins/{cabin_key}") or {}
    await safe_edit(
        callback,
        text=f"⏰ <b>Vaqtni kiriting</b>\n\n🏠 Kabina: {cabin.get('name', cabin_key)}\n🚪 Xona: Q #{room_number}\n\n"
             "Faqat bugungi kun uchun.\nMasalan: 14:00 yoki 18:30\n\n⌨️ Vaqtni yozib yuboring:",
        reply_markup=back_to_menu()
    )

@dp.message(StateFilter(BookingStates.entering_time))
async def confirm_booking(message: Message, state: FSMContext):
    data = await state.get_data()
    cabin = await fb_get(f"cabins/{data['cabin']}") or {}
    user = message.from_user

    await message.answer(
        replace_emojis_in_text(
            f"✅ <b>Bron tasdiqlandi!</b>\n\n🏠 Kabina: {cabin.get('name', data['cabin'])}\n"
            f"🚪 Xona: Q #{data['room']}\n⏰ Vaqt: {message.text}\n\n📞 Admin siz bilan tez orada bog'lanadi!"
        ),
        reply_markup=back_to_menu()
    )

    group_text = (
        f"📅 <b>Yangi kabina broni</b>\n\n"
        f"👤 Mijoz: {user.full_name} (@{user.username or 'username yoq'})\n🆔 ID: {user.id}\n"
        f"🏠 Kabina: {cabin.get('name', data['cabin'])}\n🚪 Xona: Q #{data['room']}\n⏰ Vaqt: {message.text}"
    )
    try:
        await bot.send_message(CABIN_BOOKING_CHAT_ID, replace_emojis_in_text(group_text))
    except Exception:
        logging.exception("Kabina bronini guruhga yuborishda xatolik")
        await notify_admins_of_group_failure("kabina broni", group_text)
    try:
        await fb_push("orders", {"type": "cabin_booking", "user_id": user.id, "cabin": data["cabin"],
                                  "room": data["room"], "time": message.text})
    except Exception:
        logging.exception("Bronni bazaga yozishda xatolik")

    await state.clear()

# ---------- TEZKOR BRON ----------
@dp.callback_query(F.data == "quick_booking")
async def quick_booking(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.set_state(QuickBookingStates.choosing_cabin)
    await safe_edit(callback, text="⚡ <b>Tez-kor Bron</b>\n\nQaysi turdagi xonani bron qilmoqchisiz?", reply_markup=cabin_types("quick"))

@dp.callback_query(F.data.startswith("quick_"), StateFilter(QuickBookingStates.choosing_cabin))
async def quick_booking_time(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    cabin_key = callback.data.split("_")[1]
    await state.update_data(cabin=cabin_key)
    await state.set_state(QuickBookingStates.entering_time)
    cabin = await fb_get(f"cabins/{cabin_key}") or {}
    await safe_edit(
        callback,
        text=f"⚡ <b>Tez-kor Bron: {cabin.get('name', cabin_key)}</b>\n\n"
             "Qaysi vaqtga bron qilmoqchisiz?\n(Faqat bugungi kun uchun. Masalan: 14:00)\n\n⌨️ Vaqtni yozib yuboring:",
        reply_markup=back_to_menu()
    )

@dp.message(StateFilter(QuickBookingStates.entering_time))
async def confirm_quick_booking(message: Message, state: FSMContext):
    data = await state.get_data()
    cabin = await fb_get(f"cabins/{data['cabin']}") or {}
    user = message.from_user

    await message.answer(
        replace_emojis_in_text(
            f"✅ <b>Tez bron tasdiqlandi!</b>\n\n🏠 Kabina: {cabin.get('name', data['cabin'])}\n"
            f"⏰ Vaqt: {message.text}\n\n📞 Admin siz bilan tez orada bog'lanadi!"
        ),
        reply_markup=back_to_menu()
    )

    group_text = (
        f"⚡ <b>Yangi tez-kor bron</b>\n\n👤 Mijoz: {user.full_name} (@{user.username or 'username yoq'})\n"
        f"🆔 ID: {user.id}\n🏠 Kabina: {cabin.get('name', data['cabin'])}\n⏰ Vaqt: {message.text}"
    )
    try:
        await bot.send_message(CABIN_BOOKING_CHAT_ID, replace_emojis_in_text(group_text))
    except Exception:
        logging.exception("Tez bronni guruhga yuborishda xatolik")
        await notify_admins_of_group_failure("tez-kor bron", group_text)
    try:
        await fb_push("orders", {"type": "quick_booking", "user_id": user.id, "cabin": data["cabin"], "time": message.text})
    except Exception:
        logging.exception("Tez bronni bazaga yozishda xatolik")

    await state.clear()

# ---------- MENYU ----------
@dp.callback_query(F.data == "menu")
async def show_menu(callback: CallbackQuery):
    await callback.answer()
    await safe_edit(callback, text="🍔 <b>Klub Menyusi</b>\n\nKategoriyani tanlang 👇", reply_markup=menu_categories())

@dp.callback_query(F.data.startswith("menu_"))
async def show_category_items(callback: CallbackQuery):
    await callback.answer()
    category_key = callback.data.split("_", 1)[1]
    category_name = CATEGORY_NAMES.get(category_key, category_key)
    items = await fb_get(f"menu/{category_key}") or {}
    await safe_edit(
        callback,
        text=f"📋 <b>{category_name}</b>\n\nMahsulotni tanlang 👇",
        reply_markup=menu_items_buttons(category_key, items)
    )

@dp.callback_query(F.data.startswith("item::"))
async def show_item_detail(callback: CallbackQuery):
    await callback.answer()
    _, category_key, item_id = callback.data.split("::")
    item = await fb_get(f"menu/{category_key}/{item_id}") or {"name": item_id}
    await callback.message.delete()
    await send_product_card(callback.message, category_key, item_id, item)

# ---------- MENYUDAN BUYURTMA BERISH ----------
@dp.callback_query(F.data.startswith("order::"))
async def start_menu_order(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    _, category_key, item_id = callback.data.split("::")
    item = await fb_get(f"menu/{category_key}/{item_id}") or {}
    item_name = item.get("name", item_id)

    await state.update_data(order_item=item_name, order_category=category_key, order_item_id=item_id)

    user_data = await fb_get(f"users/{callback.from_user.id}") or {}
    current_room = user_data.get("current_room")

    if current_room:
        await state.set_state(MenuOrderStates.entering_quantity)
        text = (f"🛒 <b>{item_name}</b>\n\n🚪 Xona: {current_room}\n\n"
                "Nechta / qancha miqdorda buyurtma qilmoqchisiz?\n⌨️ Javobingizni yozib yuboring:")
    else:
        await state.set_state(MenuOrderStates.entering_room)
        text = (f"🛒 <b>{item_name}</b>\n\nAvval qaysi xonada ekanligingizni ayting.\n"
                "⌨️ Xona raqamini yozing (masalan: 5):")

    await callback.message.answer(replace_emojis_in_text(text), reply_markup=back_to_menu())

@dp.message(StateFilter(MenuOrderStates.entering_room))
async def set_order_room(message: Message, state: FSMContext):
    room_text = message.text.strip()
    await fb_update(f"users/{message.from_user.id}", {"current_room": room_text})
    data = await state.get_data()
    await state.set_state(MenuOrderStates.entering_quantity)
    await message.answer(
        replace_emojis_in_text(
            f"🚪 Xona: {room_text}\n\n🛒 <b>{data.get('order_item')}</b>\n\n"
            "Nechta / qancha miqdorda buyurtma qilmoqchisiz?\n⌨️ Javobingizni yozib yuboring:"
        ),
        reply_markup=back_to_menu()
    )

@dp.message(StateFilter(MenuOrderStates.entering_quantity))
async def confirm_menu_order(message: Message, state: FSMContext):
    data = await state.get_data()
    user = message.from_user
    user_data = await fb_get(f"users/{user.id}") or {}
    room = user_data.get("current_room", "noma'lum")

    await message.answer(
        replace_emojis_in_text("✅ <b>Buyurtmangiz qabul qilindi!</b>\n\nAdmin tez orada siz bilan bog'lanadi."),
        reply_markup=back_to_menu()
    )

    group_text = (
        f"🛒 <b>Yangi menyu buyurtmasi</b>\n\n👤 Mijoz: {user.full_name} (@{user.username or 'username yoq'})\n"
        f"🆔 ID: {user.id}\n🚪 Xona: {room}\n📦 Mahsulot: {data.get('order_item', '-')}\n📝 Miqdor/Izoh: {message.text}"
    )
    try:
        await bot.send_message(MENU_ORDERS_CHAT_ID, replace_emojis_in_text(group_text))
    except Exception:
        logging.exception("Menyu buyurtmasini guruhga yuborishda xatolik")
        await notify_admins_of_group_failure("menyu buyurtmasi", group_text)
    try:
        await fb_push("orders", {"type": "menu", "user_id": user.id, "room": room,
                                  "item": data.get("order_item"), "note": message.text})
    except Exception:
        logging.exception("Buyurtmani bazaga yozishda xatolik")

    await state.clear()

# ---------- MATNGA ASOSLANGAN BO'LIMLAR (Firebase'dan) ----------
@dp.callback_query(F.data == "bonuses")
async def show_bonuses(callback: CallbackQuery):
    await callback.answer()
    text = await fb_get("texts/bonuses") or DEFAULT_BONUSES_TEXT
    await safe_edit(callback, text=text, reply_markup=back_to_menu())

@dp.callback_query(F.data == "contact")
async def show_contact(callback: CallbackQuery):
    await callback.answer()
    text = await fb_get("texts/contact") or DEFAULT_CONTACT_TEXT
    await safe_edit(callback, text=text, reply_markup=back_to_menu(), disable_web_page_preview=True)

@dp.callback_query(F.data == "news")
async def show_news(callback: CallbackQuery):
    await callback.answer()
    text = await fb_get("texts/news") or DEFAULT_NEWS_TEXT
    await safe_edit(callback, text=text, reply_markup=back_to_menu())

@dp.callback_query(F.data == "tournaments")
async def show_tournaments(callback: CallbackQuery):
    await callback.answer()
    text = await fb_get("texts/tournaments") or DEFAULT_TOURNAMENTS_TEXT
    await safe_edit(callback, text=text, reply_markup=back_to_menu())

# ---------- PROFIL ----------
@dp.callback_query(F.data == "profile")
async def show_profile(callback: CallbackQuery):
    await callback.answer()
    user_data = await fb_get(f"users/{callback.from_user.id}") or {}
    text = "👤 <b>Sizning profilingiz</b>\n\n"
    text += f"Ism: <b>{user_data.get('full_name', callback.from_user.full_name)}</b>\n"
    text += f"Telefon: <b>{user_data.get('phone', '-')}</b>\n"
    text += f"🚪 Joriy xona: <b>{user_data.get('current_room', 'belgilanmagan')}</b>"
    await safe_edit(callback, text=text, reply_markup=back_to_menu())

# ---------- ADMIN BILAN ALOQA (ikki tomonlama xabar almashish) ----------
@dp.callback_query(F.data == "contact_admin")
async def contact_admin(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.set_state(ContactAdminStates.chatting)
    await safe_edit(
        callback,
        text=(
            "📞 <b>Admin bilan Aloqa</b>\n\n"
            "Bot bo'yicha admin: <b>@aliakxmedov</b>\n\n"
            "✍️ Savol yoki taklifingizni shu yerga yozing — xabaringiz to'g'ridan-to'g'ri "
            "adminga yuboriladi va admin javob bergach, siz shu chatda javobni olasiz."
        ),
        reply_markup=back_to_menu()
    )

@dp.message(StateFilter(ContactAdminStates.chatting))
async def relay_user_message_to_admin(message: Message):
    user = message.from_user
    try:
        forwarded = await bot.forward_message(
            chat_id=ADMIN_CONTACT_ID,
            from_chat_id=message.chat.id,
            message_id=message.message_id
        )
        CONTACT_FORWARD_MAP[forwarded.message_id] = user.id
        await bot.send_message(
            ADMIN_CONTACT_ID,
            f"☝️ Yuqoridagi xabar foydalanuvchidan: {user.full_name} "
            f"(@{user.username or 'username yoq'}, ID: {user.id})\n\n"
            "Javob berish uchun ushbu xabarga <b>Reply</b> qiling."
        )
        await message.answer("✅ Xabaringiz adminga yuborildi. Javobni shu yerda kuting.")
    except Exception:
        logging.exception("Foydalanuvchi xabarini adminga yuborishda xatolik")
        await message.answer("⚠️ Xabaringizni yuborib bo'lmadi. Birozdan so'ng qaytadan urinib ko'ring.")

@dp.message(F.reply_to_message, F.chat.id == ADMIN_CONTACT_ID)
async def relay_admin_reply_to_user(message: Message):
    target_user_id = CONTACT_FORWARD_MAP.get(message.reply_to_message.message_id)
    if not target_user_id:
        return
    try:
        await bot.send_message(
            target_user_id,
            f"📩 <b>Admindan javob:</b>\n\n{message.text or message.caption or ''}"
        )
        await message.reply("✅ Javobingiz foydalanuvchiga yuborildi.")
    except Exception:
        logging.exception("Admin javobini foydalanuvchiga yuborishda xatolik")
        await message.reply("⚠️ Javobni yuborib bo'lmadi (foydalanuvchi botni bloklagan bo'lishi mumkin).")

async def notify_admins_of_group_failure(order_type: str, order_text: str):
    """Guruhga (menyu/kabina) xabar yuborib bo'lmasa, admin(lar)ga shaxsiy xabar beradi."""
    try:
        await bot.send_message(
            ADMIN_CONTACT_ID,
            f"⚠️ <b>Diqqat!</b> \"{order_type}\" guruhga yuborilmadi "
            f"(guruh ID noto'g'ri yoki bot guruhda emas). Buyurtma tafsilotlari:\n\n{order_text}"
        )
    except Exception:
        logging.exception("Admin(lar)ga guruh xatosi haqida xabar berib bo'lmadi")

# ---------- ORQAGA ----------
@dp.callback_query(F.data == "back_rooms")
async def back_to_rooms(callback: CallbackQuery):
    await rooms_prices(callback)

# ==================== ADMIN PANEL ====================
@dp.message(Command("admin"))
async def admin_start(message: Message):
    if not is_admin(message.from_user.id):
        await message.answer("⛔ Sizda admin huquqi yo'q.")
        return
    await message.answer("🛠 <b>Admin panel</b>", reply_markup=admin_main_menu())

@dp.callback_query(F.data == "adm_main")
async def admin_main(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer("⛔ Ruxsat yo'q", show_alert=True)
        return
    await callback.answer()
    await safe_edit(callback, text="🛠 <b>Admin panel</b>", reply_markup=admin_main_menu())

# ---- Kabinalarni tahrirlash ----
@dp.callback_query(F.data == "adm_cabins")
async def admin_cabins(callback: CallbackQuery):
    if not is_admin(callback.fromuser.id):
        await callback.answer("⛔ Ruxsat yo'q", show_alert=True)
        return
    await callback.answer()
    await safe_edit(callback, text="🏠 <b>Kabinani tanlang</b>", reply_markup=cabin_types("admcab"))

@dp.callback_query(F.data.startswith("admcab_"))
async def admin_cabin_detail(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer("⛔ Ruxsat yo'q", show_alert=True)
        return
    await callback.answer()
    cabin_key = callback.data.split("_")[1]
    cabin = await fb_get(f"cabins/{cabin_key}") or {}
    text = (f"🏠 <b>{cabin.get('name', cabin_key)}</b>\n\n💰 Narx: {cabin.get('price', '-')}\n"
            f"👥 Sig'im: {cabin.get('capacity', '-')}\n🎮 Jihozlar: {cabin.get('equipment', '-')}\n\n"
            "O'zgartirmoqchi bo'lgan maydonni tanlang:")
    await safe_edit(callback, text=text, reply_markup=admin_cabin_detail_keyboard(cabin_key))

@dp.callback_query(F.data.startswith("admcabfield::"))
async def admin_cabin_field(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        await callback.answer("⛔ Ruxsat yo'q", show_alert=True)
        return
    await callback.answer()
    _, cabin_key, field = callback.data.split("::")
    await state.update_data(cabin_key=cabin_key, field=field)
    await state.set_state(AdminCabinEditStates.waiting_value)
    field_names = {"price": "narx", "capacity": "sig'im", "equipment": "jihozlar", "image": "rasm linki"}
    await callback.message.answer(f"✏️ Yangi {field_names.get(field, field)} qiymatini yuboring:")

@dp.message(StateFilter(AdminCabinEditStates.waiting_value))
async def admin_cabin_set_value(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return
    data = await state.get_data()
    await fb_update(f"cabins/{data['cabin_key']}", {data["field"]: message.text})
    await message.answer("✅ Yangilandi!", reply_markup=admin_main_menu())
    await state.clear()

# ---- Xonalar holati ----
@dp.callback_query(F.data == "adm_rooms")
async def admin_rooms(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer("⛔ Ruxsat yo'q", show_alert=True)
        return
    await callback.answer()
    await safe_edit(callback, text="🚪 <b>Kabinani tanlang</b>", reply_markup=cabin_types("admroomcab"))

async def _render_admin_rooms(callback: CallbackQuery, cabin_key: str):
    statuses = await fb_get(f"room_status/{cabin_key}") or {}
    if isinstance(statuses, list):
        statuses = {str(i+1): v for i, v in enumerate(statuses)}
        await fb_set(f"room_status/{cabin_key}", statuses)
    cabin = await fb_get(f"cabins/{cabin_key}") or {}
    builder = InlineKeyboardBuilder()
    for room, status in sorted(statuses.items()):
        emoji = "🟢" if status == "bo'sh" else "🔴"
        builder.row(InlineKeyboardButton(text=f"{emoji} #{room} — {status} (bosib almashtiring)",
                                          callback_data=f"admtoggle::{cabin_key}::{room}"))
    builder.row(InlineKeyboardButton(text="⬅️ Orqaga", callback_data="adm_rooms"))
    await safe_edit(callback, text=f"🚪 <b>{cabin.get('name', cabin_key)} — Xonalar</b>", reply_markup=builder.as_markup())

@dp.callback_query(F.data.startswith("admroomcab_"))
async def admin_rooms_for_cabin(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer("⛔ Ruxsat yo'q", show_alert=True)
        return
    await callback.answer()
    cabin_key = callback.data.split("_")[1]
    await _render_admin_rooms(callback, cabin_key)

@dp.callback_query(F.data.startswith("admtoggle::"))
async def admin_toggle_room(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer("⛔ Ruxsat yo'q", show_alert=True)
        return
    await callback.answer()
    _, cabin_key, room = callback.data.split("::")
    statuses = await fb_get(f"room_status/{cabin_key}") or {}
    if isinstance(statuses, list):
        statuses = {str(i+1): v for i, v in enumerate(statuses)}
        await fb_set(f"room_status/{cabin_key}", statuses)
    current = statuses.get(room, "bo'sh")
    new_status = "band" if current == "bo'sh" else "bo'sh"
    await fb_set(f"room_status/{cabin_key}/{room}", new_status)
    await _render_admin_rooms(callback, cabin_key)

# ---- Menyuni boshqarish ----
@dp.callback_query(F.data == "adm_menu")
async def admin_menu_categories(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer("⛔ Ruxsat yo'q", show_alert=True)
        return
    await callback.answer()
    builder = InlineKeyboardBuilder()
    for key, name in CATEGORY_NAMES.items():
        builder.row(InlineKeyboardButton(text=name, callback_data=f"admmenucat::{key}"))
    builder.row(InlineKeyboardButton(text="⬅️ Orqaga", callback_data="adm_main"))
    await safe_edit(callback, text="🍔 <b>Menyuni boshqarish</b>\n\nKategoriyani tanlang:", reply_markup=builder.as_markup())

@dp.callback_query(F.data.startswith("admmenucat::"))
async def admin_menu_category_items(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer("⛔ Ruxsat yo'q", show_alert=True)
        return
    await callback.answer()
    _, category_key = callback.data.split("::")
    items = await fb_get(f"menu/{category_key}") or {}
    builder = InlineKeyboardBuilder()
    for item_id, item in sorted(items.items(), key=lambda kv: (kv[1] or {}).get("name", "")):
        name = (item or {}).get("name", item_id)
        price = (item or {}).get("price") or "?"
        builder.row(InlineKeyboardButton(text=f"{name} ({price})", callback_data=f"admmenuitem::{category_key}::{item_id}"))
    builder.row(InlineKeyboardButton(text="➕ Yangi mahsulot qo'shish", callback_data=f"admmenuadd::{category_key}"))
    builder.row(InlineKeyboardButton(text="⬅️ Orqaga", callback_data="adm_menu"))
    await safe_edit(callback, text=f"📋 <b>{CATEGORY_NAMES.get(category_key, category_key)}</b>", reply_markup=builder.as_markup())

@dp.callback_query(F.data.startswith("admmenuitem::"))
async def admin_menu_item_detail(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer("⛔ Ruxsat yo'q", show_alert=True)
        return
    await callback.answer()
    _, category_key, item_id = callback.data.split("::")
    item = await fb_get(f"menu/{category_key}/{item_id}") or {}
    text = f"📦 <b>{item.get('name', item_id)}</b>\n\n💰 Narx: {item.get('price') or 'belgilanmagan'}"
    await safe_edit(callback, text=text, reply_markup=admin_menu_item_keyboard(category_key, item_id))

@dp.callback_query(F.data.startswith("admitemfield::"))
async def admin_item_field(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        await callback.answer("⛔ Ruxsat yo'q", show_alert=True)
        return
    await callback.answer()
    _, category_key, item_id, field = callback.data.split("::")
    await state.update_data(category_key=category_key, item_id=item_id, field=field)
    await state.set_state(AdminMenuStates.waiting_edit_value)
    field_names = {"name": "nom", "price": "narx", "image": "rasm linki"}
    await callback.message.answer(f"✏️ Yangi {field_names.get(field, field)} qiymatini yuboring:")

@dp.message(StateFilter(AdminMenuStates.waiting_edit_value))
async def admin_item_set_value(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return
    data = await state.get_data()
    await fb_update(f"menu/{data['category_key']}/{data['item_id']}", {data["field"]: message.text})
    await message.answer("✅ Yangilandi!", reply_markup=admin_main_menu())
    await state.clear()

@dp.callback_query(F.data.startswith("admitemdel::"))
async def admin_item_delete_confirm(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer("⛔ Ruxsat yo'q", show_alert=True)
        return
    await callback.answer()
    _, category_key, item_id = callback.data.split("::")
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="✅ Ha, o'chirish", callback_data=f"admitemdelyes::{category_key}::{item_id}"))
    builder.row(InlineKeyboardButton(text="⬅️ Bekor qilish", callback_data=f"admmenuitem::{category_key}::{item_id}"))
    await safe_edit(callback, text="⚠️ Haqiqatan ham o'chirmoqchimisiz?", reply_markup=builder.as_markup())

@dp.callback_query(F.data.startswith("admitemdelyes::"))
async def admin_item_delete(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer("⛔ Ruxsat yo'q", show_alert=True)
        return
    await callback.answer()
    _, category_key, item_id = callback.data.split("::")
    await fb_delete(f"menu/{category_key}/{item_id}")
    await safe_edit(callback, text="🗑 O'chirildi.", reply_markup=admin_main_menu())

@dp.callback_query(F.data.startswith("admmenuadd::"))
async def admin_menu_add_start(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        await callback.answer("⛔ Ruxsat yo'q", show_alert=True)
        return
    await callback.answer()
    _, category_key = callback.data.split("::")
    await state.update_data(category_key=category_key)
    await state.set_state(AdminMenuStates.waiting_name)
    await callback.message.answer("📝 Yangi mahsulot nomini yuboring:")

@dp.message(StateFilter(AdminMenuStates.waiting_name))
async def admin_menu_add_name(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return
    await state.update_data(new_name=message.text.strip())
    await state.set_state(AdminMenuStates.waiting_price)
    await message.answer("💰 Narxini yuboring (masalan: 15 000 so'm):")

@dp.message(StateFilter(AdminMenuStates.waiting_price))
async def admin_menu_add_price(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return
    await state.update_data(new_price=message.text.strip())
    await state.set_state(AdminMenuStates.waiting_image)
    await message.answer("🖼 Rasm linkini yuboring (yoki \"yo'q\" deb yozing):")

@dp.message(StateFilter(AdminMenuStates.waiting_image))
async def admin_menu_add_image(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return
    data = await state.get_data()
    category_key = data["category_key"]
    name = data["new_name"]
    price = data["new_price"]
    image = "" if message.text.strip().lower() in ("yo'q", "yoq", "-") else message.text.strip()

    base_id = slugify(name)
    item_id = base_id
    existing = await fb_get(f"menu/{category_key}/{item_id}")
    suffix = 2
    while existing is not None:
        item_id = f"{base_id}_{suffix}"
        existing = await fb_get(f"menu/{category_key}/{item_id}")
        suffix += 1

    await fb_set(f"menu/{category_key}/{item_id}", {"name": name, "price": price, "image": image})
    await message.answer(f"✅ \"{name}\" mahsuloti qo'shildi!", reply_markup=admin_main_menu())
    await state.clear()

# ---- Matnlarni tahrirlash ----
TEXT_KEYS = {"bonuses": "🎁 Bonuslar", "news": "📰 Yangiliklar", "tournaments": "🏆 Turnirlar", "contact": "📍 Aloqa"}

@dp.callback_query(F.data == "adm_texts")
async def admin_texts(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer("⛔ Ruxsat yo'q", show_alert=True)
        return
    await callback.answer()
    builder = InlineKeyboardBuilder()
    for key, name in TEXT_KEYS.items():
        builder.row(InlineKeyboardButton(text=name, callback_data=f"admtext::{key}"))
    builder.row(InlineKeyboardButton(text="⬅️ Orqaga", callback_data="adm_main"))
    await safe_edit(callback, text="📝 <b>Qaysi matnni tahrirlaymiz?</b>", reply_markup=builder.as_markup())

@dp.callback_query(F.data.startswith("admtext::"))
async def admin_text_edit_start(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        await callback.answer("⛔ Ruxsat yo'q", show_alert=True)
        return
    await callback.answer()
    _, key = callback.data.split("::")
    await state.update_data(text_key=key)
    await state.set_state(AdminTextStates.waiting_text)
    await callback.message.answer(f"✏️ '{TEXT_KEYS.get(key, key)}' uchun yangi matnni yuboring (HTML formatlash mumkin):")

@dp.message(StateFilter(AdminTextStates.waiting_text))
async def admin_text_edit_save(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return
    data = await state.get_data()
    new_text = message.html_text or message.text
    await fb_set(f"texts/{data['text_key']}", new_text)
    await message.answer("✅ Matn yangilandi!", reply_markup=admin_main_menu())
    await state.clear()

# ==================== XATOLARNI USHLASH ====================
@dp.errors()
async def error_handler(event):
    logging.exception("Xatolik yuz berdi: %s", event.exception)
    return True

# ==================== ISHGA TUSHIRISH ====================
async def main():
    await seed_database()
    await bot.delete_webhook(drop_pending_updates=True)
    print("✅ Bot ishga tushdi!")
    try:
        await dp.start_polling(bot)
    finally:
        await http_client.aclose()
        if ai_client is not None:
            try:
                await ai_client.aio.aclose()
            except Exception:
                pass

if __name__ == "__main__":
    asyncio.run(main())
