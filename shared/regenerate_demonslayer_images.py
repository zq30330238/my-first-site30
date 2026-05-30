#!/usr/bin/env python3
"""Regenerate 27 Demon Slayer + 3 SAO + 1 Dragonball character images via Seedream 5.0."""

import json
import os
import time
import urllib.request
import urllib.error

from PIL import Image

SEEDREAM_URL = "https://ark.cn-beijing.volces.com/api/v3/images/generations"
SEEDREAM_KEY = "ark-bc9c6af0-1813-4842-ae3f-0614d354c375-98727"
SEEDREAM_MODEL = "doubao-seedream-5-0-260128"

BASE_DIR = "d:/AI网站文件夹"

characters = [
    # --- Demon Slayer (27) ---
    ("demonslayer-site/images/tanjiro-kamado.png",
     "official anime art style of Demon Slayer (Kimetsu no Yaiba), 1boy, Tanjiro Kamado, short burgundy hair, hanafuda earrings, green and black checkered haori, forehead scar, holding black nichirin katana, determined expression, high quality, clean lines, accurate character design, dark atmospheric background"),
    ("demonslayer-site/images/nezuko-kamado.png",
     "official anime art style of Demon Slayer (Kimetsu no Yaiba), 1girl, Nezuko Kamado, long black hair with orange tips, pink kimono, bamboo muzzle in mouth, small demon horns, pinkish eyes, cute demon girl, high quality, clean lines, accurate character design, dark atmospheric background"),
    ("demonslayer-site/images/zenitsu-agatsuma.png",
     "official anime art style of Demon Slayer (Kimetsu no Yaiba), 1boy, Zenitsu Agatsuma, short blonde hair with orange tips, yellow and white gradient haori, holding nichirin katana, fearful expression, lightning effects, high quality, clean lines, accurate character design, dark atmospheric background"),
    ("demonslayer-site/images/inosuke-hashibira.png",
     "official anime art style of Demon Slayer (Kimetsu no Yaiba), 1boy, Inosuke Hashibira, wild boar mask on head, blue-grey hair tips, muscular build, two serrated nichirin katanas, bare chest, aggressive stance, high quality, clean lines, accurate character design, dark atmospheric background"),
    ("demonslayer-site/images/giyu-tomioka.png",
     "official anime art style of Demon Slayer (Kimetsu no Yaiba), 1boy, Giyu Tomioka, Water Hashira, medium dark blue hair in ponytail, red and green patterned haori over blue uniform, stoic expression, holding blue nichirin katana, high quality, clean lines, accurate character design, dark atmospheric background"),
    ("demonslayer-site/images/shinobu-kocho.png",
     "official anime art style of Demon Slayer (Kimetsu no Yaiba), 1girl, Shinobu Kocho, Insect Hashira, short black hair with purple butterfly hairpin, white haori with butterfly wing pattern, gentle smile, thin stinger-like sword, high quality, clean lines, accurate character design, dark atmospheric background"),
    ("demonslayer-site/images/kyojuro-rengoku.png",
     "official anime art style of Demon Slayer (Kimetsu no Yaiba), 1boy, Kyojuro Rengoku, Flame Hashira, wild yellow and red flame-like hair, red haori with flame patterns, bright burning eyes, wide enthusiastic smile, holding katana with flame effects, high quality, clean lines, accurate character design, dark atmospheric background"),
    ("demonslayer-site/images/tengen-uzui.png",
     "official anime art style of Demon Slayer (Kimetsu no Yaiba), 1boy, Tengen Uzui, Sound Hashira, tall muscular build, white hair, many jewels on headband, red makeup around eyes, dual large cleaver swords, flashy pose, high quality, clean lines, accurate character design, dark atmospheric background"),
    ("demonslayer-site/images/mitsuri-kanroji.png",
     "official anime art style of Demon Slayer (Kimetsu no Yaiba), 1girl, Mitsuri Kanroji, Love Hashira, long pink and green ombre hair in braids, heart-shaped pupils, white uniform, thin flexible sword, blushing, high quality, clean lines, accurate character design, dark atmospheric background"),
    ("demonslayer-site/images/muichiro-tokito.png",
     "official anime art style of Demon Slayer (Kimetsu no Yaiba), 1boy, Muichiro Tokito, Mist Hashira, young boy, long straight cyan hair, blank emotionless expression, loose white uniform, holding katana, mist effects, high quality, clean lines, accurate character design, dark atmospheric background"),
    ("demonslayer-site/images/obanai-iguro.png",
     "official anime art style of Demon Slayer (Kimetsu no Yaiba), 1boy, Obanai Iguro, Serpent Hashira, short black hair, bandages covering lower face, heterochromia eyes (yellow and turquoise), white snake around neck, twisted snake sword, high quality, clean lines, accurate character design, dark atmospheric background"),
    ("demonslayer-site/images/sanemi-shinazugawa.png",
     "official anime art style of Demon Slayer (Kimetsu no Yaiba), 1boy, Sanemi Shinazugawa, Wind Hashira, wild spiky white hair, many scars on face and body, muscular, fierce expression, green nichirin katana, wind effects, high quality, clean lines, accurate character design, dark atmospheric background"),
    ("demonslayer-site/images/gyomei-himejima.png",
     "official anime art style of Demon Slayer (Kimetsu no Yaiba), 1boy, Gyomei Himejima, Stone Hashira, very large muscular bald man, blind white eyes, constantly crying tears, prayer beads, flail and axe weapon, high quality, clean lines, accurate character design, dark atmospheric background"),
    ("demonslayer-site/images/muzan-kibutsuji.png",
     "official anime art style of Demon Slayer (Kimetsu no Yaiba), 1boy, Muzan Kibutsuji, Demon King, pale white skin, curly black hair, red slit-pupil eyes (like cats), wearing white suit, elegant sinister presence, blood red background, high quality, clean lines, accurate character design"),
    ("demonslayer-site/images/kokushibo.png",
     "official anime art style of Demon Slayer (Kimetsu no Yaiba), 1boy, Kokushibo, Upper Moon 1, tall muscular demon, six eyes (three pairs arranged vertically), long ponytail, samurai armor, flesh sword with eyes, high quality, clean lines, accurate character design, dark atmospheric background"),
    ("demonslayer-site/images/doma.png",
     "official anime art style of Demon Slayer (Kimetsu no Yaiba), 1boy, Doma, Upper Moon 2, beautiful androgynous young man with rainbow-colored eyes, platinum blonde hair, red blood stain on head, holding golden fan, fake warm smile, high quality, clean lines, accurate character design, dark atmospheric background"),
    ("demonslayer-site/images/akaza.png",
     "official anime art style of Demon Slayer (Kimetsu no Yaiba), 1boy, Akaza, Upper Moon 3, muscular demon with pink short hair, blue tribal-like demon markings on body, martial arts stance, compass pattern under feet, high quality, clean lines, accurate character design, dark atmospheric background"),
    ("demonslayer-site/images/gyutaro.png",
     "official anime art style of Demon Slayer (Kimetsu no Yaiba), 1boy, Gyutaro, Upper Moon 6, very thin skeletal body, black and green mottled skin, long unkempt black hair, sickles fused to hands, hunched stance, high quality, clean lines, accurate character design, dark atmospheric background"),
    ("demonslayer-site/images/daki.png",
     "official anime art style of Demon Slayer (Kimetsu no Yaiba), 1girl, Daki, Upper Moon 6, beautiful oiran courtesan, white hair with green tips, elaborate kimono with flower patterns, ribbon belt weapons, arrogant expression, high quality, clean lines, accurate character design, dark atmospheric background"),
    ("demonslayer-site/images/enmu.png",
     "official anime art style of Demon Slayer (Kimetsu no Yaiba), 1boy, Enmu, Lower Moon 1, slender feminine-looking demon, short black hair with red tips, mouth on left hand, train conductor outfit, dreamy expression, high quality, clean lines, accurate character design, dark atmospheric background"),
    ("demonslayer-site/images/rui.png",
     "official anime art style of Demon Slayer (Kimetsu no Yaiba), 1boy, Rui, Lower Moon 5, small boy appearance, white spider-like body, red spider web markings, short white hair, spider thread weapons, high quality, clean lines, accurate character design, dark atmospheric background"),
    ("demonslayer-site/images/kanao-tsuyuri.png",
     "official anime art style of Demon Slayer (Kimetsu no Yaiba), 1girl, Kanao Tsuyuri, short black hair in ponytail with pink butterfly hairpin, pink-tinted katana, quiet expression, holding coin, high quality, clean lines, accurate character design, dark atmospheric background"),
    ("demonslayer-site/images/genya-shinazugawa.png",
     "official anime art style of Demon Slayer (Kimetsu no Yaiba), 1boy, Genya Shinazugawa, spiky black hair, facial scar, demon transformation with fangs and gun, American western-style clothing, dual pistol and sword, high quality, clean lines, accurate character design, dark atmospheric background"),
    ("demonslayer-site/images/sabito.png",
     "official anime art style of Demon Slayer (Kimetsu no Yaiba), 1boy, Sabito, peach-colored hair, fox mask on side of head, green kimono with flower pattern, holding wooden training sword, kind eyes, high quality, clean lines, accurate character design, dark atmospheric background"),
    ("demonslayer-site/images/makomo.png",
     "official anime art style of Demon Slayer (Kimetsu no Yaiba), 1girl, Makomo, short black hair, flower-patterned kimono, gentle presence, white spirit form, holding wooden sword, high quality, clean lines, accurate character design, dark atmospheric background"),
    ("demonslayer-site/images/sakonji-urokodaki.png",
     "official anime art style of Demon Slayer (Kimetsu no Yaiba), 1man, Sakonji Urokodaki, older man, tengu red mask covering face, blue cloud-patterned kimono, white hair, former Water Hashira, high quality, clean lines, accurate character design, dark atmospheric background"),
    ("demonslayer-site/images/tamayo.png",
     "official anime art style of Demon Slayer (Kimetsu no Yaiba), 1girl, Tamayo, beautiful female demon, long black hair with purple hairpin, purple kimono, calm doctor demeanor, blood demon art, high quality, clean lines, accurate character design, dark atmospheric background"),
    ("demonslayer-site/images/yushiro.png",
     "official anime art style of Demon Slayer (Kimetsu no Yaiba), 1boy, Yushiro, young demon boy, short light green hair, blindfold bandana, loyal protective stance, yukata clothing, high quality, clean lines, accurate character design, dark atmospheric background"),
    # --- SAO (3) ---
    ("sao-site/images/agil.png",
     "official anime art style of Sword Art Online, 1boy, Agil (Andrew Gilbert Mills), tall muscular dark-skinned man, bald head, wearing heavy armor, carrying giant two-handed axe, friendly smile, fantasy game setting, high quality, clean lines, accurate character design, dark atmospheric background"),
    ("sao-site/images/kikuoka.png",
     "official anime art style of Sword Art Online, 1boy, Seijiro Kikuoka, Japanese government official, short black hair, glasses, business suit, mysterious smile, VR technology background, high quality, clean lines, accurate character design, dark atmospheric background"),
    ("sao-site/images/quinella.png",
     "official anime art style of Sword Art Online Alicization, 1girl, Quinella (Administrator), beautiful woman with long silver-purple hair, flowing white goddess gown, golden crown, floating in crystal tower, divine aura, high quality, clean lines, accurate character design, dark atmospheric background"),
    # --- Dragonball (1) ---
    ("dragonball-site/images/grand-priest.png",
     "official anime art style of Dragon Ball Super, 1man, Grand Priest, tall slender being, light blue skin, white hair in a high top, angelic attire with blue and white robes, halo ring behind neck, calm all-knowing expression, high quality, clean lines, accurate character design, dark atmospheric background"),
]


def generate_image(prompt: str, img_path: str) -> bool:
    """Generate one image via Seedream, returns True on success."""
    for attempt in range(2):
        try:
            body = json.dumps({
                "model": SEEDREAM_MODEL,
                "prompt": prompt,
                "n": 1,
                "size": "2560x1440",
                "watermark": False,
            }).encode()

            req = urllib.request.Request(
                SEEDREAM_URL, data=body,
                headers={"Content-Type": "application/json",
                         "Authorization": f"Bearer {SEEDREAM_KEY}"},
                method="POST"
            )
            with urllib.request.urlopen(req, timeout=120) as resp:
                data = json.loads(resp.read().decode())

            img_url = data["data"][0]["url"]
            urllib.request.urlretrieve(img_url, img_path)

            # Resize via PIL
            img = Image.open(img_path)
            img = img.resize((1200, 675), Image.LANCZOS)
            img = img.convert("RGB")
            img.save(img_path, "JPEG", quality=85)
            return True

        except Exception as e:
            if attempt < 1:
                time.sleep(3)
            else:
                return False

    return False


def main():
    ok_count = 0
    fail_count = 0

    for rel_path, prompt in characters:
        img_path = os.path.join(BASE_DIR, rel_path)
        os.makedirs(os.path.dirname(img_path), exist_ok=True)

        name = os.path.splitext(os.path.basename(rel_path))[0]
        print(f"[...] {name} ...", end=" ", flush=True)

        if generate_image(prompt, img_path):
            print(f"OK: {name}")
            ok_count += 1
        else:
            print(f"FAIL: {name} - API error after 2 retries")
            fail_count += 1

        time.sleep(3)

    print(f"\nDone: {ok_count}/32 generated, {fail_count} failed")


if __name__ == "__main__":
    main()
