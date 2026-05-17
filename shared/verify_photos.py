"""Fetch real Unsplash photo IDs via source.unsplash.com redirects per category."""
import json, sys, urllib.request, time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

CATEGORY_KEYWORDS = {
    "pets": [
        "dog+playing", "cat+closeup", "puppy", "kitten+sleeping",
        "aquarium+fish", "parrot+bird", "hamster+pet", "rabbit+bunny",
        "guinea+pig", "turtle+pet", "horse", "lizard+reptile",
        "dog+training", "cat+window", "golden+retriever", "hedgehog",
        "ferret", "dog+beach", "black+dog", "white+cat",
        "dog+portrait", "cat+playing", "puppy+cute", "exotic+pet",
        "vet+animal", "dog+walking", "cat+face", "fish+tank",
        "bird+cage", "dog+ball", "cat+toy", "small+pet",
        "rescue+dog", "shelter+cat", "pet+care",
    ],
    "health": [
        "salad+bowl", "fresh+vegetables", "fruit+basket", "green+smoothie",
        "healthy+breakfast", "avocado+toast", "grilled+chicken", "yoga+outdoor",
        "running+shoes", "meditation", "gym+workout", "water+bottle",
        "green+tea", "vitamins", "doctor+office", "dental+care",
        "healthy+grains", "eggs+protein", "mushroom+dish", "kitchen+cooking",
        "weight+scale", "hiking+trail", "cycling", "swimming+pool",
        "stretching", "mental+health", "skincare", "dental+hygiene",
        "blood+test", "treadmill", "legumes", "brown+rice",
        "fish+oil", "nuts+seeds", "berries+fruit",
    ],
    "home": [
        "modern+kitchen", "houseplants+indoor", "gardening", "backyard+garden",
        "living+room", "bedroom+design", "bathroom+spa", "home+office+desk",
        "dining+room", "smart+home", "interior+plants", "bookshelf+decor",
        "patio+outdoor", "lighting+fixture", "wall+art", "minimal+decor",
        "house+exterior", "kitchen+counter", "renovation", "garden+flowers",
        "paint+colors", "closet+organization", "laundry+room", "curtains+window",
        "fireplace+cozy", "kitchen+modern", "vacuum+cleaning", "rug+carpet",
        "cushion+pillow", "wall+paint", "garage", "attic+space",
        "roof", "fence+garden", "greenhouse",
    ],
    "finance": [
        "coins+money", "finance+chart", "piggy+bank", "credit+cards",
        "stock+market", "dollar+bills", "gold+bars", "bitcoin+crypto",
        "online+banking", "retirement", "tax+form", "investment",
        "real+estate", "insurance", "savings+jar", "trading+desk",
        "mobile+payment", "financial+advisor", "mortgage+home", "budget",
        "compound+interest", "emergency+fund", "debt+free", "car+loan",
        "scholarship", "passive+income", "wealth+management", "college+savings",
        "cash", "payroll", "wallet", "safe+deposit",
        "stock+ticker", "house+keys", "startup",
    ],
    "tech": [
        "circuit+board", "laptop+desk", "computer+coffee", "electronics",
        "server+room", "fiber+optic", "vr+headset", "smartphone+screen",
        "drone+flying", "coding+screen", "wifi+router", "tablet+device",
        "mechanical+keyboard", "wireless+charger", "smartwatch", "printer+office",
        "usb+hub", "webcam", "ssd+hard+drive", "monitor+setup",
        "gaming+PC", "motherboard", "headphones", "camera+lens",
        "bluetooth+speaker", "ethernet+cable", "projector", "e-reader+kindle",
        "3d+printer", "satellite", "robot+vacuum", "ram+memory",
        "cpu+processor", "gpu+graphics", "network+switch",
    ],
    "travel": [
        "mountain+hiking", "tropical+beach", "city+skyline", "paris+eiffel",
        "tokyo+street", "venice+canals", "safari+africa", "camping+tent",
        "road+trip", "cruise+ship", "ski+resort", "desert+landscape",
        "northern+lights", "great+wall", "machu+picchu", "santorini+greece",
        "pyramids+egypt", "cherry+blossom", "bali+rice", "sydney+opera",
        "aurora+borealis", "petra+jordan", "taj+mahal", "amazon+rainforest",
        "swiss+alps", "hawaii+volcano", "iceland+waterfall", "angkor+wat",
        "maldives+overwater", "grand+canyon", "amsterdam+canals", "hot+air+balloon",
        "backpacker+travel", "train+travel", "snorkeling",
    ],
}

SITE_CATEGORY = {
    "sub-pets": "pets", "sub-healthy": "health", "sub-home": "home",
    "sub-finance": "finance", "sub-tech": "tech", "sub-travel": "travel",
}


def resolve_photos():
    all_photos = {}
    for category, keywords in CATEGORY_KEYWORDS.items():
        photos = []
        for kw in keywords:
            url = f"https://source.unsplash.com/1200x630/?{kw}"
            try:
                req = urllib.request.Request(url, method="HEAD")
                resp = urllib.request.urlopen(req, timeout=10)
                final_url = resp.geturl()
                # Extract photo ID from redirect URL
                # Format: https://images.unsplash.com/photo-XXXXXXXXXX?...
                import re
                m = re.search(r'photo-([a-zA-Z0-9_-]+)', final_url)
                if m:
                    photo_id = m.group(1)
                    if photo_id not in [p for p in photos]:
                        photos.append(photo_id)
                        print(f"  {category}: {kw} → {photo_id}")
                time.sleep(0.3)
            except Exception as e:
                print(f"  {category}: {kw} FAILED ({e})")
                time.sleep(0.5)
        all_photos[category] = photos
        print(f"{category}: {len(photos)} photos resolved")
    return all_photos


def main():
    print("Resolving real Unsplash photo IDs via source.unsplash.com...")
    all_photos = resolve_photos()

    outfile = ROOT / "shared" / "verified_photos.json"
    outfile.write_text(json.dumps(all_photos, indent=2), encoding="utf-8")
    print(f"\nSaved to {outfile}")
    print(f"Total: {sum(len(v) for v in all_photos.values())} photos across {len(all_photos)} categories")


if __name__ == "__main__":
    main()
