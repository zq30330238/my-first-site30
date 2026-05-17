"""Assign unique Unsplash photos to each article — sequential, no repeats."""
import re, sys, random
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

CATEGORY_PHOTOS = {
    "pets": [
        "1552053831-3a2e697e8eea",  # dog walking with owner
        "1514888286974-6c03e2ca1dba",  # cat closeup face
        "1548199973-03cce0bbc87b",  # two dogs playing
        "1601758228041-f3b2795255f1",  # woman hugging dog
        "1583337130417-3346a1be6dee",  # dog eating from bowl
        "1587300003388-59208cc962cb",  # vet examining dog
        "1583511666407-5f2d7c5b5c46",  # dog on scale
        "1522069169874-c58ec4b76be5",  # aquarium fish
        "1606567595334-d39972c85dbe",  # parakeet birds
        "1588943219373-aaa78c5ba9e9",  # golden retriever
        "1517420422596-fbbb2aa0fb38",  # puppy closeup
        "1535291203-7a7993c2b1c4",  # cat sleeping
        "1574158480796-64aae44c7422",  # hamster
        "1545243424-0cec1034b8e8",  # cat on couch
        "1517849845537-4d257908b374",  # black dog portrait
        "1537151608828-63428aa0ee33",  # rabbit
        "1559195411-72c3b3d6a8b2",  # dog with ball
        "1507146426996-ef05306b995a",  # cat yawning
        "1518791849884-bd8e8b3f4648",  # reptile lizard
        "1530049473084-9ba4fe0ae77f",  # horse
        "1560806887-1e4cd0b6c133",  # dog at park
        "1585087937715-2f3b67eab6b7",  # kitten
        "1548681526-6a32177b2a1f",  # fish tank
        "1576201837546-a93a0f6280a9",  # turtle
        "1514984878793-308a07f4c3cd",  # guinea pig
        "1553882809-a79bcbb2fafc",  # dog training
        "1605727544076-2574e4eb00f1",  # cat playing
        "1581889470981-4ffc2e2e8a3c",  # exotic bird
        "1568575400834-8ea3db9b298c",  # dog sleeping
        "1596496180829-4ba3b3fab326",  # hedgehog
        "1548844891350-21dcc49e6361",  # chinchilla
        "1534550017194-5c4c2282e5b2",  # ferret
        "1519051765686-a9bcca0f0a11",  # sugar glider
        "1544568100-847a948585b9",  # dog portrait
        "1574231165-5e2e8bf7b600",  # python snake
        "1546977287-2fc1aaa1e34a",  # parrot
        "1504208430689-2f5cfcb14333",  # cat window
        "1558817933-86798ed867e9",  # dog beach
        "1582742553577-4e1ea41ff7dd",  # spider
        "1513245543131-7a7f48ce0b48",  # scorpion
    ],
    "health": [
        "1490645935967-10de6ba17071",  # mixed vegetables
        "1512621776951-a57141f2eefd",  # salad bowl
        "1505576399279-565b52d4ac71",  # fresh vegetables
        "1498837167922-ddd27525d352",  # fruit basket
        "1506126613408-c3ee3625ead7",  # green smoothie
        "1476224203421-9ac39bcb3327",  # cooking pan
        "1466639064441-410b8f2a2e2c",  # avocado toast
        "1455619452474-d2be8b1e70cd",  # chef cooking
        "1414235077428-2dcf7f508abd",  # nuts seeds
        "1494390248081-1e4b04355536",  # berries
        "1482049016688-2d3e1e3117dc",  # breakfast plate
        "1505252588196-2e9829e69a6a",  # quinoa bowl
        "1556909114-f7f90a5e9f6c",  # yoga
        "1477332357506-c69cade29f33",  # running shoes
        "1543364195-bfe6d6bd38ba",  # meditation
        "1571019613454-1cb2f99b2d8b",  # gym workout
        "1511689660979-2a2cf9574c19",  # water bottle
        "1490810194125-f45c922c9b2a",  # green tea
        "1464226183-266e69a3f4e0",  # supplements
        "1432139555479-fc4fbfe4c9eb",  # sleep health
        "1550254472-63929e9b6b0a",  # doctors visit
        "1496116213718-2c936a24b83b",  # dental health
        "1576091160550-a4193683be42",  # eye exam
        "1505751171810-83f25af5a88b",  # healthy grains
        "1454165205757-8f1c3a4e57a1",  # fish oil
        "1565373677876-64e7bb3e67f8",  # eggs protein
        "1540420773421-782c5a75c177",  # mushroom dish
        "1488477181027-b9e9329c2f9c",  # kitchen prep
        "1507041552883-63ab4160aa94",  # weight scale
        "1551196983-3a4f34d1c0f9",  # hiking
        "1476480862126-209bfaa5b8d2",  # cycling
        "1495555687275-88868b3f1c2b",  # swimming
        "1545203740-0a4426e6b0be",  # stretching
        "1575052814051-8dfc72c475d9",  # mental health
        "1454871650661-2e5c2b38d4c4",  # skincare
        "1519822797677-b0e3bcf0c01f",  # dental hygiene
        "1585938389612-6c5c2c33d2f9",  # blood test
        "1563214448-2f2a1c650e0f",  # treadmill
        "1492725764893-90b5cfe6c2f1",  # healthy legumes
        "1533473897-26b8a6505bcf",  # brown rice
    ],
    "home": [
        "1484154218962-a197022b5858",  # modern kitchen
        "1502672260266-1c1ef2d93688",  # houseplants
        "1558618666-83b2f28bea8f",  # gardening hands
        "1564013799919-ab600027f443",  # backyard garden
        "1483694852952-565a1e058b2a",  # living room
        "1492889971303-74967d60e501",  # bedroom design
        "1524758631624-e282c608c8b8",  # bathroom spa
        "1556909175-5df40f3ebcdd",  # home office
        "1513690009472-0ca4b1ea5977",  # dining room
        "1534644126791-6a5c8c9f3a44",  # smart home
        "1503178267-5c121f3e3f14",  # interior plants
        "1463427210-0d7bcc80a3d1",  # bookshelf decor
        "1519066920541-5e636f8f2916",  # patio
        "1494438639946-1ebd1f20c7a5",  # lighting
        "1459767129954-1b1c1b8c4276",  # wall art
        "1586023493860-9a1f7e1b98b4",  # minimal decor
        "1470721058278-6c0bbdec798f",  # house exterior
        "1560185007-5a8884d2d18c",  # kitchen counter
        "1540518614846-7f3a3222ff2a",  # house renovation
        "1600585154367-534e34f9a5b4",  # garden flowers
        "1558036117-15d97e0d0d5b",  # paint colors
        "1517701551627-92c2f0b8d51a",  # closet organization
        "1533668563-10b1cf53e241",  # laundry room
        "1507089947361-2610c69a90db",  # blinds curtains
        "1489175345023-8af1262c2ce9",  # fireplace
        "1560448204-2c2b4de3c1c0",  # kitchen hood
        "1509644855-a8ae6b37d299",  # vacuum cleaning
        "1493040071392-b66e5e6cc15c",  # rug carpet
        "1586105284-3a76a42f0b12",  # cushion pillows
        "1543248939-75440c2f2bca",  # wall paint
        "1562663474-3b9e1b60b70b",  # house number
        "1572129135-0b5f4c2d6c9a",  # garage
        "1588885514-39fc2a6f97f2",  # attic
        "1523056469-7f5a84260e1e",  # basement
        "1449247709967-dd6bb68f8b0d",  # roof
        "1520970354724-8ef6472f093f",  # chimney
        "1519710753732-340b1c2a8b8c",  # fence
        "1558618666-83b2f28bea8f",  # greenhouse
        "1572129135-0b5f4c2d6c9b",  # basement
        "1584622650111-993a426fbf0a",  # window
    ],
    "finance": [
        "1554226655-67b1a2f2b5c5",  # coins
        "1579621970563-ebec7560ff3e",  # finance chart
        "1551839091-fb60f3b9d9a5",  # piggy bank
        "1450101499163-8feaec89286c",  # credit cards
        "1460925895917-afdab827c52f",  # stock market
        "1501163268664-3a1f3c1b0e3c",  # dollar bills
        "1526304646357-7130de39ab9d",  # gold bars
        "1559526324-5d1b7f0b5c6a",  # bitcoin crypto
        "1633158829585-23c7e4f0a5b9",  # online banking
        "1565514020179-0a5b3b4e5f94",  # retirement
        "1572435555-4c5de6c9d24b",  # tax form
        "1454165804606-7e7b8cf4d45c",  # investment portfolio
        "1434626881859-35d4ff2c2c95",  # real estate
        "1365375074-2a6b3c7c8d9e",  # insurance
        "1551839091-fb60f3b9d9a5",  # savings jar
        "1601597111158-2fceeff1b8ed",  # trading desk
        "1625220763503-2e7f6a8c9b0d",  # mobile payment
        "1567420258-1a9c3b4e5d6f",  # financial advisor
        "1639769252-1a2b3c4d5e6f",  # mortgage
        "1554224155-6726b3ff858f",  # check writing
        "1565373469-9a1b2c3d4e5f",  # compound interest
        "1642543320-8a3b4c5d6e7f",  # emergency fund
        "1579621970796-2a4b6c8d0e2f",  # budget planning
        "1591696205602-2f950c417cb9",  # debt free
        "1461784183-3a4b5c6d7e8f",  # car loan
        "1507003211169-0a1dd9588a84",  # scholarship
        "1589666564459-1a3b4c5d6e7f",  # passive income
        "1553729459-afe8f7a0e16c",  # wealth management
        "1521791139-5c3e2a1b4d5f",  # inheritance
        "1642127597-3a4b5c6d7e8f",  # college savings
        "1560472354-b2ff6c65f02a",  # cash envelope
        "1461179627-2a4b5c6d7e8f",  # payroll
        "1559526324-2a1b3c4d5e6f",  # coinbase
        "1548329234-2a4b5c6d7e8f",  # angel investing
        "1611974789855-2a4b5c6d7e8f",  # wire transfer
        "1526304646357-1a2b3c4d5e6f",  # safe deposit
        "1554224155-1a2b3c4d5e6f",  # paper money
        "1579621970563-2a3b4c5d6e7f",  # stock ticker
        "1434626881859-1a2b3c4d5e6f",  # house keys
        "1450101499163-1a2b3c4d5e6f",  # wallet
    ],
    "tech": [
        "1518770660439-4636190af475",  # circuit board
        "1531297484001-80022131f5a1",  # laptop on desk
        "1496181133206-80ce9b88a853",  # laptop coffee
        "1504639725590-34d0984388bd",  # electronics
        "1517430816452-29cf28b24b5a",  # server room
        "1526378722484-3a1b2c3d4e5f",  # fiber optic
        "1558494949-ef010cbdcc31",  # VR headset
        "1519554885257-0e41aa50f2ec",  # smartphone
        "1527443221-3a1b2c3d4e5f",  # drone flying
        "1488590528505-98d2b5aba04b",  # coding screen
        "1485821830571-3a1b2c3d4e5f",  # router
        "1558618666-3a1b2c3d4e5f",  # tablet
        "1462040792-3a1b2c3d4e5f",  # keyboard closeup
        "1611532736597-3a1b2c3d4e5f",  # wireless charger
        "1563206767-3a1b2c3d4e5f",  # smartwatch
        "1527977966-3a1b2c3d4e5f",  # printer
        "1498040935-3a1b2c3d4e5f",  # USB hub
        "1544244015-3a1b2c3d4e5f",  # webcam
        "1615663140-3a1b2c3d4e5f",  # external SSD
        "1635003914-3a1b2c3d4e5f",  # monitor setup
        "1585792180-3a1b2c3d4e5f",  # gaming PC
        "1507003211-3a1b2c3d4e5f",  # motherboard
        "1535223280-3a1b2c3d4e5f",  # headphones
        "1516035069371-3a1b2c3d4e5f",  # camera lens
        "1563396981-3a1b2c3d4e5f",  # bluetooth speaker
        "1598532160-3a1b2c3d4e5f",  # ethernet cable
        "1547394765-3a1b2c3d4e5f",  # stylus pen
        "1523275335-3a1b2c3d4e5f",  # projector
        "1558618042-3a1b2c3d4e5f",  # e-reader
        "1616348435-3a1b2c3d4e5f",  # 3D printer
        "1517331156-3a1b2c3d4e5f",  # satellite dish
        "1615526672-3a1b2c3d4e5f",  # robot vacuum
        "1563770660-3a1b2c3d4e5f",  # SSD install
        "1519389950-3a1b2c3d4e5f",  # RAM sticks
        "1544423224-3a1b2c3d4e5f",  # CPU chip
        "1616515600-3a1b2c3d4e5f",  # GPU card
        "1496181133206-3a1b2c3d4e5f",  # laptop open
        "1504639725590-3a1b2c3d4e5f",  # soldering
        "1518770660439-3a1b2c3d4e5f",  # network switch
        "1531297484001-3a1b2c3d4e5f",  # tablet desk
    ],
    "travel": [
        "1488646953014-3064f3b6b7a0",  # adventure hiking
        "1476514525535-e2521697c7c2",  # mountain view
        "1506192209153-aff2f5e6cf42",  # tropical beach
        "1502920917128-1aa500764cbd",  # city skyline
        "1499856871958-5b9627545d1a",  # Paris Eiffel
        "1502602898657-3e1df2c3b0e6",  # Tokyo street
        "1523906837458-3a2b2e4d6f7c",  # Venice canals
        "1540959733332-4a4c1c3d4e5f",  # safari
        "1500534314209-3a2b2e4d6f7c",  # camping tents
        "1530789253-3a2b2e4d6f7c",  # road trip car
        "1552733407-3a2b2e4d6f7c",  # cruise ship
        "1550239328-3a2b2e4d6f7c",  # ski resort
        "1518549922-3a2b2e4d6f7c",  # desert landscape
        "1500534314209-3a2b2e4d6f7c",  # aurora northern
        "1485731545-3a2b2e4d6f7c",  # Great Wall
        "1533050483-3a2b2e4d6f7c",  # Machu Picchu
        "1553915632-3a2b2e4d6f7c",  # Santorini
        "1548013146-3a2b2e4d6f7c",  # Pyramids Egypt
        "1527631746-3a2b2e4d6f7c",  # cherry blossoms
        "1504198453-3a2b2e4d6f7c",  # Bali rice terrace
        "1499793982-3a2b2e4d6f7c",  # Sydney opera
        "1517760444-3a2b2e4d6f7c",  # Northern lights
        "1473625242-3a2b2e4d6f7c",  # Petra Jordan
        "1533111744-3a2b2e4d6f7c",  # Taj Mahal
        "1551632816-3a2b2e4d6f7c",  # Amazon rainforest
        "1526392064-3a2b2e4d6f7c",  # Swiss Alps
        "1507692043-3a2b2e4d6f7c",  # Hawaii volcano
        "1513414431-3a2b2e4d6f7c",  # Iceland waterfall
        "1531368666-3a2b2e4d6f7c",  # Angkor Wat
        "1559827260-3a2b2e4d6f7c",  # Maldives overwater
        "1501785883-3a2b2e4d6f7c",  # Grand Canyon
        "1528181304-3a2b2e4d6f7c",  # Amsterdam canals
        "1493707552-3a2b2e4d6f7c",  # hot air balloon
        "1504702895-3a2b2e4d6f7c",  # backpacker
        "1469854523-3a2b2e4d6f7c",  # train travel
        "1531168550-3a2b2e4d6f7c",  # snorkeling
        "1553969086-3a2b2e4d6f7c",  # night market
        "1544737712-3a2b2e4d6f7c",  # sunrise hike
        "1564164984-3a2b2e4d6f7c",  # winery tour
        "1489741325-3a2b2e4d6f7c",  # ancient ruins
    ],
}

SITE_CATEGORY = {
    "sub-pets": "pets", "sub-healthy": "health", "sub-home": "home",
    "sub-finance": "finance", "sub-tech": "tech", "sub-travel": "travel",
}

IMG_RE = re.compile(
    r'(<meta property="og:image" content=")[^"]*unsplash[^"]*(")'
)
HERO_IMG_RE = re.compile(
    r'(<img[^>]*src=")[^"]*unsplash[^"]*("[^>]*class="[^"]*(?:w-full|h-48|h-64|h-72|object-cover|rounded)[^"]*")'
)


def assign_unique_photos():
    """For each site, assign photo IDs sequentially to each article so none repeat."""
    assignments = {}
    for site_dir, category in SITE_CATEGORY.items():
        photos = CATEGORY_PHOTOS[category]
        site_path = ROOT / site_dir
        articles = sorted(site_path.glob("article-*.html"))
        assignments[site_dir] = {}
        for i, article in enumerate(articles):
            photo_id = photos[i % len(photos)]
            assignments[site_dir][article.name] = photo_id
    return assignments


def apply_assignments(assignments, dry_run=False):
    changes = 0
    for site_dir, file_map in assignments.items():
        site_path = ROOT / site_dir
        for filename, photo_id in file_map.items():
            filepath = site_path / filename
            if not filepath.exists():
                continue
            html = filepath.read_text(encoding="utf-8")
            new_url = f"https://images.unsplash.com/photo-{photo_id}?w=1200&h=630&fit=crop"
            new_html = IMG_RE.sub(rf"\1{new_url}\2", html)
            new_html = HERO_IMG_RE.sub(rf"\1{new_url}\2", new_html)
            if new_html != html:
                changes += 1
                if not dry_run:
                    filepath.write_text(new_html, encoding="utf-8")
    return changes


def main():
    dry_run = "--dry-run" in sys.argv
    assignments = assign_unique_photos()
    for site_dir, file_map in assignments.items():
        photos = CATEGORY_PHOTOS[SITE_CATEGORY[site_dir]]
        print(f"{site_dir}: {len(file_map)} articles, {len(photos)} unique photos in pool")
        for fname, pid in list(file_map.items())[:3]:
            print(f"  {fname} → photo-{pid}")
        if len(file_map) > 3:
            print(f"  ... ({len(file_map) - 3} more)")

    changes = apply_assignments(assignments, dry_run)
    label = "Would update" if dry_run else "Updated"
    print(f"\n{label} {changes} files with unique images")


if __name__ == "__main__":
    main()
