"""Regenerate 4 failed demonslayer images with stronger prompts"""
import json, urllib.request, time, os
from PIL import Image

SEEDREAM_URL = "https://ark.cn-beijing.volces.com/api/v3/images/generations"
SEEDREAM_KEY = "ark-bc9c6af0-1813-4842-ae3f-0614d354c375-98727"
SEEDREAM_MODEL = "doubao-seedream-5-0-260128"
OUT_DIR = "d:/AI网站文件夹/demonslayer-site/images"

REQUESTS = [
    ("giyu-tomioka.png",
     "official anime art of Giyu Tomioka from Demon Slayer, 1boy, masculine male, Water Hashira, short-medium dark blue hair in low ponytail, stoic serious expression, red and green patterned haori over black uniform, holding blue nichirin katana, sharp jawline, male physique, dark misty forest background, ufotable style"),

    ("muzan-kibutsuji.png",
     "official anime art of Muzan Kibutsuji from Demon Slayer, 1boy, masculine male demon lord, pale white skin, curly black hair, red slit-pupil cat eyes, sharp male facial features, wearing white suit, elegant sinister presence, blood red background, ufotable style, strong masculine jaw"),

    ("muichiro-tokito.png",
     "official anime art of Muichiro Tokito from Demon Slayer, 1boy, young male boy, Mist Hashira, long straight cyan-turquoise hair, blank emotionless male face, loose white uniform over black corps uniform, holding katana, male body structure, mist effects, dark forest, ufotable style"),

    ("obanai-iguro.png",
     "official anime art of Obanai Iguro from Demon Slayer, 1boy, male, Serpent Hashira, short black hair, white bandages covering lower face, heterochromia eyes (yellow and turquoise), white snake around neck, twisted snake-shaped sword, black and white striped haori, dark background, ufotable style, NO hanafuda earrings, NO checkered pattern"),
]

ok = 0
fail = 0
for fname, prompt in REQUESTS:
    path = os.path.join(OUT_DIR, fname)
    body = json.dumps({
        "model": SEEDREAM_MODEL,
        "prompt": prompt,
        "n": 1,
        "size": "2560x1440",
        "watermark": False,
    }).encode()

    for attempt in range(2):
        try:
            req = urllib.request.Request(SEEDREAM_URL, data=body,
                headers={"Content-Type": "application/json", "Authorization": f"Bearer {SEEDREAM_KEY}"},
                method="POST")
            with urllib.request.urlopen(req, timeout=120) as resp:
                data = json.loads(resp.read().decode())
            img_url = data["data"][0]["url"]
            urllib.request.urlretrieve(img_url, path)

            img = Image.open(path)
            img = img.resize((1200, 675), Image.LANCZOS)
            img = img.convert("RGB")
            img.save(path, "JPEG", quality=85)

            sz = os.path.getsize(path) // 1024
            print(f"OK: {fname} ({sz}KB)")
            ok += 1
            break
        except Exception as e:
            if attempt == 0:
                print(f"Retry: {fname} - {e}")
                time.sleep(3)
            else:
                print(f"FAIL: {fname} - {e}")
                fail += 1
    time.sleep(2)

print(f"\nDone: {ok}/{len(REQUESTS)} regenerated, {fail} failed")
