import json

PATH = "d:/AI网站文件夹/shared/anime_site_data.json"

with open(PATH, "r", encoding="utf-8") as f:
    data = json.load(f)

chars = data["dragonball"]["characters"]

# Accurate Dragon Ball lore data for all 20 characters
fields = {
    "Son Goku": {
        "power_level": "Base: 10,000 (Saiyan Saga); Super Saiyan: 150,000,000 (Namek Saga); SSJ3: 4e14; Super Saiyan God: 7e15; SSB: 2e16; Ultra Instinct: beyond mortal measurement",
        "first_appearance": "Dragon Ball Chapter 1 / Dragon Ball Episode 1 (1986)",
        "species": "Saiyan",
        "affiliations": ["Z-Fighters", "Team Universe 7", "Kame School", "Galactic Patrol (temporary)"],
        "signature_moves": ["Kamehameha", "Spirit Bomb", "Instant Transmission", "Kaioken", "Dragon Fist", "Solar Flare", "Destructo Disc"],
        "key_arcs": ["Emperor Pilaf Saga", "21st Tenkaichi Budokai", "King Piccolo Saga", "Saiyan Saga", "Frieza Saga", "Cell Saga", "Buu Saga", "Battle of Gods", "Tournament of Power", "Granolah Arc"],
        "relationships": {"Vegeta": "rival/friend", "Gohan": "son", "Krillin": "best friend", "Piccolo": "ally", "Chi-Chi": "wife", "Bardock": "father", "Raditz": "brother", "King Kai": "mentor", "Whis": "teacher", "Beerus": "rival/ally", "Frieza": "nemesis", "Bulma": "oldest friend", "Master Roshi": "first master", "Goten": "son"}
    },
    "Vegeta": {
        "power_level": "Saiyan Saga: 18,000; Namek Saga: 24,000 (post-Zarbon); Super Saiyan: 150,000,000; SSB Evolution: 2.5e16; Ultra Ego: scales with damage taken",
        "first_appearance": "Dragon Ball Z Chapter 204 / Dragon Ball Z Episode 5 (1989)",
        "species": "Saiyan",
        "affiliations": ["Z-Fighters", "Team Universe 7", "Frieza Force (former)", "Royal Saiyan Army (former)"],
        "signature_moves": ["Final Flash", "Galick Gun", "Big Bang Attack", "Final Explosion", "Dirty Fireworks", "Gamma Burst Flash", "Spirit Sword"],
        "key_arcs": ["Saiyan Saga", "Frieza Saga", "Cell Saga", "Buu Saga", "Battle of Gods", "Tournament of Power", "Granolah Arc"],
        "relationships": {"Goku": "rival/friend", "Bulma": "wife", "Trunks": "son", "Bulla": "daughter", "King Vegeta": "father", "Tarble": "brother", "Nappa": "former comrade", "Beerus": "master/rival", "Whis": "teacher", "Frieza": "nemesis", "Cabba": "mentor/student"}
    },
    "Gohan": {
        "power_level": "Base: 1 (latent); Rage Boost (Raditz): 1,307; Super Saiyan 2 (Cell Games): 3.5e14; Ultimate: 1.2e17; Beast Form: beyond current measurement",
        "first_appearance": "Dragon Ball Z Chapter 196 / Dragon Ball Z Episode 1 (1989)",
        "species": "Saiyan-Human Hybrid",
        "affiliations": ["Z-Fighters", "Team Universe 7", "Great Saiyaman (self-created)", "Kame School (former)"],
        "signature_moves": ["Masenko", "Kamehameha", "Special Beam Cannon", "Super Dragon Flight"],
        "key_arcs": ["Saiyan Saga", "Frieza Saga", "Cell Saga", "Buu Saga", "Tournament of Power", "Super Hero Arc"],
        "relationships": {"Goku": "father", "Chi-Chi": "mother", "Goten": "brother", "Piccolo": "mentor", "Videl": "wife", "Pan": "daughter", "Krillin": "family friend", "Mr. Satan": "father-in-law"}
    },
    "Piccolo": {
        "power_level": "Saiyan Saga: 3,500; Namek fusion with Nail: 1,500,000+; Super Namekian: ~1e12; Orange Piccolo: 1.8e15+",
        "first_appearance": "Dragon Ball Chapter 161 / Dragon Ball Episode 123 (1988)",
        "species": "Namekian",
        "affiliations": ["Z-Fighters", "Team Universe 7", "Demon Clan (former)"],
        "signature_moves": ["Special Beam Cannon (Makankosappo)", "Hellzone Grenade", "Light Grenade", "Explosive Demon Wave", "Multi-Form", "Regeneration", "Giant Form"],
        "key_arcs": ["King Piccolo Saga", "Saiyan Saga", "Frieza Saga", "Cell Saga", "Buu Saga", "Tournament of Power", "Super Hero Arc"],
        "relationships": {"Goku": "ally/rival", "Gohan": "student/close bond", "Kami": "other half (fused)", "Nail": "Namekian ally (fused)", "King Piccolo": "father/reincarnation", "Dende": "fellow Namekian", "Android 17": "rival/ally"}
    },
    "Frieza": {
        "power_level": "First Form: 530,000; Second Form: 1,200,000+; Final Form (50%): 60,000,000; Full Power: 120,000,000; Golden Frieza: 1e16; Black Frieza: surpasses Ultra Instinct and Ultra Ego",
        "first_appearance": "Dragon Ball Z Chapter 247 / Dragon Ball Z Episode 44 (1990)",
        "species": "Frieza Race (Mutant)",
        "affiliations": ["Frieza Force (leader)", "Team Universe 7 (temporary)"],
        "signature_moves": ["Death Beam", "Death Ball", "Supernova", "Death Saucer", "Nova Strike", "Golden Death Ball", "Emperor's Edge"],
        "key_arcs": ["Frieza Saga", "Trunks Saga (flashback)", "Resurrection F", "Tournament of Power", "Granolah Arc"],
        "relationships": {"Goku": "nemesis", "Vegeta": "nemesis", "King Cold": "father", "Cooler": "brother (non-canon)", "Zarbon": "subordinate", "Dodoria": "subordinate", "Ginyu Force": "elite squad", "Beerus": "fear/respect"}
    },
    "Cell": {
        "power_level": "Imperfect Cell (post-absorptions): ~1.5e12; Semi-Perfect Cell: 3e14; Perfect Cell: 3.8e14; Super Perfect Cell: 5e14",
        "first_appearance": "Dragon Ball Z Chapter 360 / Dragon Ball Z Episode 141 (1992)",
        "species": "Bio-Android",
        "affiliations": ["Red Ribbon Army (creation purpose)"],
        "signature_moves": ["Kamehameha", "Special Beam Cannon", "Destructo Disc", "Solar Flare", "Perfect Barrier", "Death Beam", "Instant Transmission", "Spirit Bomb (incomplete)", "Absorption"],
        "key_arcs": ["Cell Saga"],
        "relationships": {"Dr. Gero": "creator", "Android 17": "absorption target/component", "Android 18": "absorption target/component", "Goku": "target rival", "Gohan": "defeated by", "Cell Juniors": "offspring"}
    },
    "Majin Buu": {
        "power_level": "Fat Buu: 5e14; Evil Buu: 3e14; Super Buu: 1.2e16; Buutenks: 3.5e16; Buuhan: 5e16; Kid Buu: 2.8e15 (most dangerous, not strongest)",
        "first_appearance": "Dragon Ball Z Chapter 460 / Dragon Ball Z Episode 232 (1994)",
        "species": "Majin (Primordial Evil)",
        "affiliations": ["Babidi's Forces (formerly controlled)"],
        "signature_moves": ["Chocolate Beam", "Absorption", "Regeneration", "Body Manipulation", "Planet Burst", "Vice Shout", "Angry Explosion"],
        "key_arcs": ["Buu Saga"],
        "relationships": {"Bibidi": "creator (original)", "Babidi": "awakener", "Mr. Satan": "best friend (Fat Buu)", "Bee": "pet (Fat Buu)", "Goku": "enemy/fought", "Vegeta": "fought against", "Hercule/Mr. Satan": "only friend", "Kid Buu (reincarnated)": "Uub"}
    },
    "Trunks": {
        "power_level": "Base (Android Saga): 3,800,000; Super Saiyan: 150,000,000; Super Saiyan Rage: 1.5e16; Super Saiyan 2 (DBS): 8e15",
        "first_appearance": "Dragon Ball Z Chapter 330 / Dragon Ball Z Episode 119 (1991) [Future Trunks]; Dragon Ball Z Chapter 431 / Dragon Ball Z Episode 202 (1993) [Kid Trunks]",
        "species": "Saiyan-Human Hybrid",
        "affiliations": ["Z-Fighters", "Team Universe 7", "Capsule Corporation (heir)", "Time Patrol (Future)"],
        "signature_moves": ["Burning Attack", "Final Flash", "Galick Gun", "Heat Dome Attack", "Finish Buster", "Sword of Hope (Spirit Bomb Sword)"],
        "key_arcs": ["Android Saga", "Cell Saga", "Buu Saga", "Goku Black Arc (Future Trunks)", "Super Hero Arc (Kid Trunks)"],
        "relationships": {"Vegeta": "father", "Bulma": "mother", "Bulla": "sister", "Goten": "best friend/fusion partner", "Mai": "love interest (Future)", "Goku": "mentor figure", "Gohan (Future)": "mentor"}
    },
    "Bulma": {
        "power_level": "5 (standard human; intellectual genius off-scale)",
        "first_appearance": "Dragon Ball Chapter 1 / Dragon Ball Episode 1 (1986)",
        "species": "Human",
        "affiliations": ["Capsule Corporation (heir/CEO)", "Z-Fighters (support/logistics)", "Dragon Team"],
        "signature_moves": ["Dragon Radar (invention)", "Capsule technology", "Time Machine (invention)", "Super Saiyan God ritual (coordinator)", "Blutz Wave Generator"],
        "key_arcs": ["Emperor Pilaf Saga", "Frieza Saga", "Cell Saga", "Buu Saga", "Battle of Gods", "Goku Black Arc"],
        "relationships": {"Vegeta": "husband", "Trunks": "son", "Bulla": "daughter", "Goku": "oldest friend", "Dr. Brief": "father", "Yamcha": "ex-boyfriend", "Tights": "sister", "Jaco": "Galactic Patrol ally"}
    },
    "Krillin": {
        "power_level": "Saiyan Saga: 1,770; Namek Saga: 13,000 (post-Guru); Frieza Saga: 75,000 (peak); Tournament of Power: ~5e10 (skill-based), strongest pure human",
        "first_appearance": "Dragon Ball Chapter 25 / Dragon Ball Episode 14 (1986)",
        "species": "Human (Earthling)",
        "affiliations": ["Z-Fighters", "Team Universe 7", "Kame School", "Galactic Patrol (temporary)", "Police Force (occupation)"],
        "signature_moves": ["Destructo Disc (Kienzan)", "Kamehameha", "Scattering Bullet", "Solar Flare x100", "Afterimage Strike", "Scatter Kamehameha"],
        "key_arcs": ["21st Tenkaichi Budokai", "22nd Tenkaichi Budokai", "King Piccolo Saga", "Saiyan Saga", "Frieza Saga", "Cell Saga", "Buu Saga", "Tournament of Power"],
        "relationships": {"Goku": "best friend", "Android 18": "wife", "Marron": "daughter", "Master Roshi": "master", "Bulma": "long-time friend", "Gohan": "close ally", "Piccolo": "ally"}
    },
    "Beerus": {
        "power_level": "God of Destruction level. Effortlessly defeated Super Saiyan 3 Goku. Approximately 1e18+ (estimated). Ultra Instinct (incomplete) demonstrated.",
        "first_appearance": "Dragon Ball Z: Battle of Gods (2013) / Dragon Ball Super Episode 1 (2015)",
        "species": "God (Hakaishin)",
        "affiliations": ["God of Destruction of Universe 7", "Divine Hierarchy", "Team Universe 7 (nominal)"],
        "signature_moves": ["Sphere of Destruction (Hakai)", "God of Destruction's Roar", "Energy of Destruction", "Ultra Instinct (incomplete)", "Sneeze of Destruction"],
        "key_arcs": ["Battle of Gods", "Resurrection F", "Universe 6 Saga", "Tournament of Power"],
        "relationships": {"Whis": "attendant/teacher", "Goku": "rival/entertainment", "Vegeta": "student/respect", "Shin (Supreme Kai)": "life-linked partner", "Champa": "twin brother", "Zeno": "dread/obedience", "Frieza": "annihilated (later revived)"}
    },
    "Whis": {
        "power_level": "Angel tier: far surpasses Beerus. Estimated speed equivalent to 5e20+. Supreme mastery of Ultra Instinct. Top 5 strongest beings in Universe 7.",
        "first_appearance": "Dragon Ball Z: Battle of Gods (2013) / Dragon Ball Super Episode 1 (2015)",
        "species": "Angel",
        "affiliations": ["Divine Hierarchy", "Angel Corps", "Beerus's attendant", "Universe 7"],
        "signature_moves": ["Ultra Instinct (perfect mastery)", "Staff of Authority (time rewind)", "Warp", "Martial arts instruction", "Neutralization"],
        "key_arcs": ["Battle of Gods", "Resurrection F", "Universe 6 Saga", "Tournament of Power", "Granolah Arc"],
        "relationships": {"Beerus": "master (as attendant)", "Goku": "student", "Vegeta": "student", "Grand Minister": "father", "Vados": "sister", "Maracrita": "sister", "Korn": "brother"}
    },
    "Broly": {
        "power_level": "Base: ~1e14 (grew exponentially); Wrathful: 1e15+; Legendary Super Saiyan: 2.5e16+ and grows limitlessly during battle. Surpassed Goku Blue in first fight.",
        "first_appearance": "Dragon Ball Z: Broly The Legendary Super Saiyan (1993) [non-canon]; Dragon Ball Super: Broly (2018) [canon]",
        "species": "Saiyan (Mutant)",
        "affiliations": ["Frieza Force (temporarily manipulated)", "Beerus's Planet (training)", "Z-Fighters (ally)"],
        "signature_moves": ["Gigantic Roar", "Eraser Cannon", "Planet Crusher", "Omega Blaster", "Gigantic Full Blast", "Berserker Rage", "Unrestrained combat style"],
        "key_arcs": ["Broly Saga (DBS)"],
        "relationships": {"Goku": "sparring partner/friend", "Vegeta": "sparring partner/rival", "Gine": "mother", "Paragus": "father", "Cheelai": "friend/companion", "Lemo": "friend", "Frieza": "initial manipulator/target of rage", "Beerus": "training supervisor"}
    },
    "Jiren": {
        "power_level": "Surpassed his own God of Destruction (Belmod). Stronger than all Universe 11 deities. Estimated 2e18+. The mortal stronger than gods.",
        "first_appearance": "Dragon Ball Super Episode 77 / Chapter 30 (2017)",
        "species": "Alien (Unknown race, Universe 11)",
        "affiliations": ["Pride Troopers", "Team Universe 11"],
        "signature_moves": ["Overheat Magnum", "Power Impact", "Herculean Dash", "Infinity Rush", "Glare (eye-based force)", "Meditation Power-up"],
        "key_arcs": ["Tournament of Power"],
        "relationships": {"Belmod": "God of Destruction (surpassed)", "Top (Toppo)": "fellow Pride Trooper/rival", "Dyspo": "fellow Pride Trooper", "Goku": "opponent who changed his worldview", "Hit": "defeated opponent", "Gicchin": "murdered master (motivation)"}
    },
    "Tien Shinhan": {
        "power_level": "Saiyan Saga: 1,830; Cell Saga: ~5,000,000; Buu Saga: ~500,000,000. Consistently trains harder than any other human.",
        "first_appearance": "Dragon Ball Chapter 113 / Dragon Ball Episode 82 (1987)",
        "species": "Human (Triclops descent)",
        "affiliations": ["Z-Fighters", "Team Universe 7", "Tien-Shin Dojo (founder)", "Crane School (former)"],
        "signature_moves": ["Tri-Beam (Kikoho)", "Solar Flare", "Multi-Form", "Four Witches Technique", "Dodon Ray", "Volleyball Fist", "Neo Tri-Beam"],
        "key_arcs": ["22nd Tenkaichi Budokai", "King Piccolo Saga", "Saiyan Saga", "Cell Saga", "Buu Saga", "Tournament of Power"],
        "relationships": {"Chiaotzu": "best friend/lifelong partner", "Goku": "rival/ally", "Master Shen": "former master", "Master Roshi": "rival master (historical)", "Launch": "implied love interest"}
    },
    "Yamcha": {
        "power_level": "Saiyan Saga: 1,480; Cell Saga: ~3,000,000; Buu Saga: ~300,000,000. Fought from the very beginning of Dragon Ball.",
        "first_appearance": "Dragon Ball Chapter 7 / Dragon Ball Episode 5 (1986)",
        "species": "Human (Earthling)",
        "affiliations": ["Z-Fighters", "Kame School (former)", "Taitans Baseball Team"],
        "signature_moves": ["Wolf Fang Fist", "Spirit Ball", "Kamehameha", "Neo Wolf Fang Fist", "Sokidan"],
        "key_arcs": ["Emperor Pilaf Saga", "21st Tenkaichi Budokai", "King Piccolo Saga", "Saiyan Saga", "Cell Saga", "Buu Saga"],
        "relationships": {"Bulma": "ex-girlfriend", "Pu'ar": "best friend/shapeshifting companion", "Goku": "first rival/friend", "Krillin": "friend", "Master Roshi": "master", "Tien": "ally"}
    },
    "Master Roshi": {
        "power_level": "Early DB: 139; Tournament of Power (zen state): ~1e10. Skill and experience amplify combat power far beyond raw PL.",
        "first_appearance": "Dragon Ball Chapter 3 / Dragon Ball Episode 3 (1986)",
        "species": "Human (Earthling)",
        "affiliations": ["Z-Fighters", "Team Universe 7", "Kame School (founder)", "Turtle Hermit Sect"],
        "signature_moves": ["Kamehameha (original creator)", "Evil Containment Wave (Mafuba)", "Drunken Fist", "Thunder Shock Surprise", "Max Power Form (Full Power)", "Hypnosis Technique"],
        "key_arcs": ["21st Tenkaichi Budokai", "King Piccolo Saga", "Saiyan Saga (flashback)", "Tournament of Power"],
        "relationships": {"Goku": "first student", "Krillin": "student", "Turtle": "longtime companion", "Grandpa Gohan": "student", "Shen": "rival (Crane Hermit)", "Ox-King": "former student", "Bulma": "friend (started Goku's journey)", "Yamcha": "former student"}
    },
    "Android 18": {
        "power_level": "Android Saga: comparable to SSJ Vegeta (~150M); Tournament of Power: SSB-tier (through combat skill and infinite energy)",
        "first_appearance": "Dragon Ball Chapter 349 / Dragon Ball Z Episode 133 (1992)",
        "species": "Human-based Cyborg",
        "affiliations": ["Z-Fighters", "Team Universe 7", "Red Ribbon Army (origin)", "Capsule Corporation (associated)"],
        "signature_moves": ["Power Blitz", "Destructo Disc", "Infinite Energy Combat", "Hell's Hurricane", "Accel Dance (with Android 17)"],
        "key_arcs": ["Cell Saga", "Buu Saga", "Tournament of Power", "Super Hero Arc"],
        "relationships": {"Krillin": "husband", "Marron": "daughter", "Android 17": "twin brother", "Dr. Gero": "cyborg creator (hated)", "Cell": "absorption target (escaped)", "Bulma": "friend", "Master Roshi": "teammate (ToP)"}
    },
    "Goten": {
        "power_level": "Age 7 Super Saiyan: 1.5e11 (youngest SSJ ever); Base (Buu Saga): 1e10; Super Saiyan (Buu Saga): 5e13; SSJ3 (Gotenks form): 4e15",
        "first_appearance": "Dragon Ball Z Chapter 424 / Dragon Ball Z Episode 200 (1993)",
        "species": "Saiyan-Human Hybrid",
        "affiliations": ["Z-Fighters", "Son Family"],
        "signature_moves": ["Kamehameha", "Super Ghost Kamikaze Attack (Gotenks)", "Galactic Donut (Gotenks)", "Super Saiyan 3 (Gotenks)", "Continuous Kamehameha"],
        "key_arcs": ["Buu Saga", "Battle of Gods", "Super Hero Arc"],
        "relationships": {"Goku": "father", "Chi-Chi": "mother", "Gohan": "brother", "Trunks": "best friend/fusion partner", "Videl": "sister-in-law", "Pan": "niece", "Vegeta": "father's rival"}
    },
    "Chi-Chi": {
        "power_level": "23rd Budokai: 130 (peak combat years); Later years: 10 (retired martial artist). Skilled Ox-King style martial arts.",
        "first_appearance": "Dragon Ball Chapter 11 / Dragon Ball Episode 7 (1986)",
        "species": "Human (Earthling)",
        "affiliations": ["Son Family", "Ox-King Family", "Kame School (indirect)", "Turtle Hermit Sect (associated)"],
        "signature_moves": ["Flying Kick", "Ox-King Style Martial Arts", "Raging Mother Chop", "Fan (weapon)", "Kitchen Knife Strike", "Angry Aura"],
        "key_arcs": ["Emperor Pilaf Saga", "23rd Tenkaichi Budokai", "Saiyan Saga", "Cell Saga", "Buu Saga"],
        "relationships": {"Goku": "husband", "Gohan": "son", "Goten": "son", "Ox-King": "father", "Pan": "granddaughter", "Videl": "daughter-in-law", "Grandpa Gohan": "father-in-law (honorary)", "Bulma": "friend/rivalry"}
    }
}

added = 0
for char in chars:
    name = char["name"]
    if name in fields:
        for k, v in fields[name].items():
            char[k] = v
            added += 1
    else:
        print(f"WARNING: No data found for {name}")

with open(PATH, "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print(f"Done. Added {added} fields across {len(chars)} characters ({len(fields)} unique characters had data).")
print(f"File: {PATH}")
