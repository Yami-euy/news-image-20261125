# THE WEDNESDAY GLOBE v4 — story data for Wednesday 25 November 2026.
# Rebuilt on the shared concept of the competition's top 1-3 entries
# (3 big illustrated lead cards + ~10 small illustrated cards + big-number
# stat strip + UTC timeline + region counts + how-sure badges + map with
# numbered pins + numbered IN BRIEF list + DATE CHECK footer).
# All facts ONLY from ~/workspace/makefun/news25-research.md (57 verified
# stories; this edition keeps the same 50 as v3). Caveats honoured: US
# Wednesday session not closed (Tuesday closes + Wed pre-market futures
# only), UCL fixtures tonight with NO scores, IRGC and casualty figures
# attributed, Ebola figures given with their source dates.
# Timeline hours are only those in the research file (Beijing/ET/CET
# times converted to UTC by arithmetic, original zone noted).

MASTHEAD_TITLE = "THE WEDNESDAY GLOBE"
MASTHEAD_DATE = "WEDNESDAY 25 NOVEMBER 2026"
MASTHEAD_TAG = "THE WORLD'S NEWS IN ONE PAGE"

# Big-number stat strip: (big number, caption).
STATS = [
    ("50,018.70", "first close above 50,000"),
    ("2,091", "Russian losses in a day"),
    ("36%", "Bangladesh garment wage rise"),
    ("26", "Miners trapped in Bogor mine"),
    ("~$90-91", "Brent, down 1.5% Wed"),
    ("11,613", "Ebola cases, WHO (17 Nov)"),
]

# Region counts: (name, count, colour key). Sums to 50.
REGION_COUNTS = [
    ("EUROPE", 12),
    ("MIDDLE EAST", 5),
    ("AFRICA", 3),
    ("ASIA", 9),
    ("AMERICAS", 4),
    ("GLOBAL", 17),
]

# Timeline: only hours from the research file.
TIMELINE = [
    ("NIGHT", "Samara refineries hit"),
    ("EARLY", "Gaza strike kills Hamas chief"),
    ("03:56 UTC", "Shenzhou-24 docks"),
    ("09:32 UTC", "US futures slide"),
    ("17:45 UTC", "UCL Matchday 5 begins"),
]

# How-sure badges: OFFICIAL = government/agency/company statement;
# CONFIRMED = two or more major outlets; REPORTED = one outlet's
# reporting; CLAIM = one side's word, unverified.
LEADS = [
    {
        "num": 1,
        "kicker": "MIDDLE EAST  —  THE LEAD",
        "location": "STRAIT OF HORMUZ · GULF",
        "headline": "HORMUZ IN FLAMES",
        "body": (
            "Iran's Revolutionary Guards say three oil tankers under US air "
            "escort hit mines in the Strait of Hormuz; UK officials confirmed "
            "three vessels struck on Monday."
        ),
        "badge": "CLAIM",
        "scene": "hormuz",
        "chip": "3 TANKERS",
    },
    {
        "num": 2,
        "kicker": "UKRAINE WAR",
        "location": "SAMARA REGION, RUSSIA · WAR",
        "headline": "UKRAINE HITS TWO ROSNEFT REFINERIES",
        "body": (
            "Overnight, Ukrainian drones struck the Syzran and Kuibyshev "
            "refineries, about 800 km from the border; large fires reported, "
            "one killed. Putin vowed \u201cinevitable\u201d retaliation."
        ),
        "badge": "CONFIRMED",
        "scene": "refineries",
        "chip": "2 REFINERIES",
    },
    {
        "num": 3,
        "kicker": "GAZA",
        "location": "GAZA CITY · WAR",
        "headline": "ISRAEL KILLS SECOND HAMAS SECURITY CHIEF IN 24 HOURS",
        "body": (
            "An Israeli airstrike killed Hamas security chief Mohammad "
            "Abuelouf, his wife and two daughters, 13 and 15, in Gaza City — "
            "the second such killing in 24 hours."
        ),
        "badge": "REPORTED",
        "scene": "gaza",
        "chip": "2ND IN 24 H",
    },
]

# Small illustrated cards: (num, location, headline, body, badge, scene).
CARDS = [
    (4, "JIUQUAN, CHINA · SPACE",
     "FIRST FOREIGNER BOARDS TIANGONG",
     "Muhammad Zeeshan Ali, 40, docks with Shenzhou-24; stays 5–10 days.",
     "CONFIRMED", "tiangong"),
    (5, "BOGOR, JAVA · DISASTER",
     "26 TRAPPED IN FLOODED GOLD MINE",
     "Three bodies recovered in Pongkor; 26 still in the 100 m shaft.",
     "CONFIRMED", "mine"),
    (6, "DHAKA · LABOUR",
     "GARMENT WORKERS WIN 36% PAY RISE",
     "Minimum wage rises to 17,000 taka after weeks of violent protests.",
     "REPORTED", "garment"),
    (7, "SANTA CLARA · TECH",
     "NVIDIA BUYS HUGGING FACE",
     "$12.9bn deal, a day after Huang's return as CEO.",
     "OFFICIAL", "chip"),
    (8, "NEW YORK · MARKETS",
     "DOW TOPS 50,000",
     "First close above 50,000: +0.85% to 50,018.70 as tech slides.",
     "CONFIRMED", "dow"),
    (9, "CIKANDE, JAVA · DISASTER",
     "CANDY FACTORY FIRE: 26 DEAD",
     "Death toll rises in Cikande, Serang; 28 workers still unaccounted for.",
     "REPORTED", "fire"),
    (10, "CANBERRA · SECURITY",
     "SOLOMONS DUMPS CHINA PACT",
     "Signs security treaty with Australia; no foreign bases.",
     "OFFICIAL", "treaty"),
    (11, "CARTAGENA · COLOMBIA",
     "HOSTAGES FREED IN CARTAGENA",
     "Forces storm a supermarket after a day-long siege; one captor killed.",
     "REPORTED", "hostages"),
    (12, "SAN FRANCISCO · AI",
     "GPT-6 DESIGNS PROTEINS",
     "OpenAI says its models design new protein shapes by reasoning alone.",
     "CLAIM", "protein"),
    (13, "BLUE NILE, SUDAN · WAR",
     "RSF DRONES KILL 19 CIVILIANS",
     "Strikes in Damazin and Roseires kill 19, wound 20.",
     "REPORTED", "drones"),
]

# IN BRIEF: remaining 37 stories, one line each (num, text).
BRIEF = [
    (14, "Zaporizhzhia — flats hit, 2 dead, 44 hurt"),
    (15, "War tally: 2,091 lost in a day (Kyiv claim)"),
    (16, "Merkury sinking was self-defence, Kyiv says"),
    (17, "Merz: Russia is \u201cescalating\u201d everywhere"),
    (18, "UK warns firms of Russian sabotage"),
    (19, "EU proposes 22nd sanctions package"),
    (20, "Murmansk governor arrested"),
    (21, "NATO vows space defence"),
    (22, "Kushner warns Israel over isolation"),
    (23, "Iran vows \u201call available means\u201d"),
    (24, "Phosphate shock: fertiliser supply −40%"),
    (25, "DR Congo rebels retreat"),
    (26, "Ebola: 11,613 cases (WHO, 17 Nov)"),
    (27, "Shanghai party chief purged"),
    (28, "N Korea expels Swiss diplomat"),
    (29, "Russian jets enter Korean zone"),
    (30, "Qianfan: China's answer to Starlink"),
    (31, "Futures slide into PCE day"),
    (32, "Bitcoin below $60,000"),
    (33, "Gold near $3,550"),
    (34, "UK: bills soar, cap +26% from January"),
    (35, "Germany's growth revised down"),
    (36, "Consumer confidence jumps"),
    (37, "Huang: \u201ccompletely untrue\u201d"),
    (38, "Anthropic below IPO price"),
    (39, "Huawei convicted"),
    (40, "GPT-6.2 Sol ships; Claude desktop apps"),
    (41, "Anthropic's Siren honeypot"),
    (42, "Muse enters Instagram DMs"),
    (43, "Pope laments COP31 failure"),
    (44, "COP31: the flop, in numbers"),
    (45, "Indigenous left empty-handed"),
    (46, "\u00c1brego Garc\u00eda leaves for Spain"),
    (47, "Army to detonate toxic explosive"),
    (48, "Mississippi: six dead in crash"),
    (49, "Champions League tonight (no scores)"),
    (50, "Astra finds exoplanet candidates"),
]

# World-map pins: (story number, longitude, latitude, nudge_x, nudge_y).
# Nudges separate the two Java pins (stories 5 and 9), which would
# otherwise sit on top of each other.
PINS = [
    (1, 56.5, 26.5, 0, 0),
    (2, 50.1, 53.2, 0, 0),
    (3, 34.5, 31.5, 0, 0),
    (4, 98.5, 39.8, 0, 0),
    (5, 106.5, -6.4, -11, -9),
    (9, 107.6, -6.9, 11, 9),
    (10, 160.0, -9.0, 0, 0),
    (11, -75.5, 10.4, 0, 0),
    (13, 34.5, 11.8, 0, 0),
    (14, 35.2, 47.8, 0, 0),
    (26, 30.0, 0.7, 0, 0),
    (27, 121.5, 31.2, 0, 0),
    (48, -89.0, 30.0, 0, 0),
]

# Footer.
DATE_CHECK = (
    "DATE CHECK — Not yet out at research time, so not in this paper: "
    "Wednesday's US market close and the PCE + Q3 GDP results (due 8:30 ET); "
    "UCL Matchday 5 scores (matches kick off tonight). Everything here was "
    "first reported on Wednesday 25 November 2026."
)
SOURCES = (
    "Sources: Reuters, AP, Kyiv Independent, ISW, WFP, WHO, UKMTO, BBC, "
    "CBS, UEFA, Zacks, Investors.com — drawings original, drawn in code."
)
LEGEND = (
    "HOW SURE:  OFFICIAL = government, agency or company statement  •  "
    "CONFIRMED = two or more major outlets  •  REPORTED = one outlet's "
    "reporting  •  CLAIM = one side's word, unverified"
)

# Count check: 3 leads + 10 cards + 37 in brief = 50 stories.
STORY_COUNT = 50
