"""fix_images.py — Replace duplicate Unsplash images with unique picsum.photos images."""
import os, re, hashlib

ROOT = os.path.dirname(os.path.abspath(__file__))

# Articles with duplicate images + their categories
AFFECTED = {
    # TIER 1: 6-way duplicates
    "sub-healthy/article-32.html": "mindful eating meditation food",
    "sub-pets/article-32.html": "flea tick prevention dog cat",
    "sub-home/article-30.html": "garage wall storage organization",
    "sub-finance/article-12.html": "investment portfolio diversification finance",
    "sub-tech/article-35.html": "speed up old laptop computer",
    "sub-travel/article-25.html": "book hotels lowest rates travel",

    "sub-healthy/article-28.html": "detox diets debunked science",
    "sub-pets/article-30.html": "introduce dog to resident cat",
    "sub-home/article-27.html": "indoor herb garden year round",
    "sub-finance/article-10.html": "gig worker freelancer finance",
    "sub-tech/article-33.html": "budget laptops under 500 dollars",
    "sub-travel/article-22.html": "street food safety travel abroad",

    "sub-healthy/article-30.html": "food expiration dates guide",
    "sub-pets/article-31.html": "aquarium fish care beginner",
    "sub-home/article-28.html": "bathroom renovation under 500 budget",
    "sub-finance/article-11.html": "identity theft protection finance",
    "sub-tech/article-2.html": "home office setup productivity workspace",
    "sub-travel/article-23.html": "beach destinations digital nomad 2026",

    "sub-healthy/article-19.html": "mediterranean diet beginner guide",
    "sub-pets/article-25.html": "interactive dog toys mental sharpness",
    "sub-home/article-26.html": "lower home energy costs year round",
    "sub-finance/article-1.html": "investing basics stock market beginner",
    "sub-tech/article-17.html": "clean digital footprint online privacy",
    "sub-travel/article-21.html": "best travel backpacks 2026",

    # TIER 2: 4-way duplicates
    "sub-healthy/article-4.html": "truth about sugar health effects",
    "sub-pets/article-4.html": "pet insurance plans compared 2026",
    "sub-finance/article-15.html": "retirement savings 30s catch up",
    "sub-tech/article-4.html": "cybersecurity basics protect online",

    "sub-healthy/article-3.html": "build balanced plate every meal",
    "sub-pets/article-3.html": "care for new puppy first month",
    "sub-finance/article-14.html": "real estate investing beginners",
    "sub-tech/article-36.html": "smart home security block hackers",

    "sub-healthy/article-5.html": "plant based vs mediterranean diet",
    "sub-pets/article-6.html": "small pets rabbit hamster guinea pig care",
    "sub-finance/article-16.html": "best budgeting methods compared 50 30 20 zero based envelope",
    "sub-tech/article-5.html": "smart home devices worth buying 2026",

    "sub-healthy/article-20.html": "sleep affects metabolism weight",
    "sub-pets/article-33.html": "household pet poison prevention dangerous items",
    "sub-finance/article-13.html": "freelancer gig worker financial planning",
    "sub-tech/article-3.html": "AI tools change daily workflow",

    # TIER 3: 3-way duplicates
    "sub-healthy/article-7.html": "intermittent fasting complete beginner guide",
    "sub-finance/article-16.html": None,  # already in TIER 2
    "sub-tech/article-6.html": "laptop buying guide how to choose",

    # TIER 4: 2-way duplicates
    "sub-healthy/article-9.html": "high protein foods weight loss",
    "sub-finance/article-17.html": "digital nomad finance tips",

    "sub-healthy/article-8.html": "read nutrition labels like pro",
    "sub-finance/article-17.html": None,  # already handled

    "sub-home/article-7.html": "seasonal home maintenance checklist",
    "sub-tech/article-15.html": "home wifi fix dead zones boost speed",

    "sub-finance/article-7.html": "travel rewards credit cards points miles",
    "sub-tech/article-14.html": "best streaming services 2026",

    "sub-healthy/article-10.html": "gut health diet foods heal digestive system",
    "sub-finance/article-31.html": "financial planning freelancers gig workers",

    "sub-healthy/article-1.html": "superfoods eat every day optimal health",
    "sub-finance/article-30.html": "protect finances from identity theft",
}

# Some articles appear in multiple tiers — deduplicate
seen = set()
unique_affected = {}
for path, keywords in AFFECTED.items():
    if keywords is None:
        continue
    if path in seen:
        continue
    seen.add(path)
    unique_affected[path] = keywords


def get_unique_image_url(filepath, keywords):
    """Generate a unique image URL based on article path."""
    # Use file path hash as seed for guaranteed uniqueness
    seed = hashlib.md5(filepath.encode()).hexdigest()[:12]
    # Use keywords to make image relevant
    kw_clean = re.sub(r'[^a-z0-9]', '-', keywords.lower())[:50]
    return f"https://picsum.photos/seed/{kw_clean}-{seed}/800/600"


def fix_images():
    """Replace all duplicate images with unique ones."""
    fixed = 0
    for rel_path, keywords in sorted(unique_affected.items()):
        filepath = os.path.join(ROOT, "..", rel_path)
        if not os.path.isfile(filepath):
            print(f"  MISSING: {rel_path}")
            continue

        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()

        # Find all Unsplash image URLs (img src and background-image)
        old_urls = re.findall(r'https://images\.unsplash\.com/photo-[a-f0-9]+[^\s"\')\\]*', content)
        if not old_urls:
            print(f"  NO UNSPLASH: {rel_path}")
            continue

        # Replace each Unsplash URL with unique picsum URL
        for old_url in old_urls:
            new_url = get_unique_image_url(rel_path, keywords)
            content = content.replace(old_url, new_url)

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)

        print(f"  FIXED: {rel_path} ({len(old_urls)} image(s))")
        fixed += 1

    print(f"\nTotal fixed: {fixed} files")
    return fixed


if __name__ == "__main__":
    fix_images()
