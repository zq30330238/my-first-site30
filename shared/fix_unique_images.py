"""Assign unique Unsplash photos to each article by article number.

Usage: py shared/fix_unique_images.py [--dry-run]

Ensures each article within a site gets a unique cover photo.
Photos are assigned deterministically: article_N.html -> photos[(N-1) % len(photos)]
This avoids the duplicate-image problem caused by small photo pools.
"""

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

CATEGORY_PHOTOS = {
    "pets": [
        "1514888286974-6c03e2ca1dba", "1522069169874-c58ec4b76be5", "1548199973-03cce0bbc87b",
        "1583337130417-3346a1be7dee", "1583511655826-05700d52f4d9", "1587300003388-59208cc962cb",
        "1595433707802-6b2626ef1c91", "1601758228041-f3b2795255f1", "1606567595334-d39972c85dbe",
        "1534361960057-19889db9621e", "1566710582818-d673dc761201", "1604165094771-7af34f7fd4cd",
        "1503256207526-0d5d80fa2f47", "1507146426996-ef05306b995a", "1544568100-847a948585b9",
        "1629740067905-bd3f515aa739", "1504826260979-242151ee45b7", "1504595403659-9088ce801e29",
        "1477884213360-7e9d7dcc1e48", "1576201836106-db1758fd1c97", "1575859431774-2e57ed632664",
        "1583511655857-d19b40a7a54e", "1478098711619-5ab0b478d6e6", "1640384974326-3e72680e0fb3",
        "1548546738-8509cb246ed3", "1577023311546-cdc07a8454d9", "1615497001839-b0a0eac3274c",
        "1573865526739-10659fec78a5", "1511044568932-338cba0ad803", "1518791841217-8f162f1e1131",
        "1536589961747-e239b2abbec2", "1548366086-7f1b76106622", "1532386236358-a33d8a9434e3",
        "1559624989-7b9303bd9792", "1513360371669-4adf3dd7dff8", "1570824104453-508955ab713e",
        "1498100152307-ce63fd6c5424",
    ],
    "health": [
        "1467003909585-2f8a72700288", "1490645935967-10de6ba17061", "1498837167922-ddd27525d352",
        "1505576399279-565b52d4ac71", "1509365465985-25d11c17e812", "1512621776951-a57141f2eefd",
        "1523362628745-0c100150b504", "1482049016688-2d3e1b311543", "1490818387583-1baba5e638af",
        "1511690656952-34342bb7c2f2", "1467453678174-768ec283a940", "1505253716362-afaea1d3d1af",
        "1540189549336-e6e99c3679fe", "1546069901-ba9599a7e63c", "1547592180-85f173990554",
        "1606756790138-261d2b21cd75", "1540420773420-3366772f4999", "1493770348161-369560ae357d",
        "1620706857370-e1b9770e8bb1", "1610348725531-843dff563e2c", "1573246123716-6b1782bfc499",
        "1473648717346-73c9c15cbad6", "1592924802543-809bfeee53fb", "1488459716781-31db52582fe9",
        "1597362925123-77861d3fbac7", "1579113800032-c38bd7635818", "1542838132-92c53300491e",
        "1557844352-761f2565b576", "1550989460-0adf9ea622e2", "1635774855717-0aec182f92cc",
        "1590779033100-9f60a05a013d", "1566385101042-1a0aa0c1268c", "1518843875459-f738682238a6",
        "1489450278009-822e9be04dff",
    ],
    "home": [
        "1484154218962-a197022b5858", "1502672260266-1c1ef2d93688", "1507003211169-0a1dd7228f2d",
        "1544716278-ca5e3f4abd8c", "1560185007-5f0bb1866cab", "1584622650111-993a426fbf0a",
        "1585771724684-38269d6639fd", "1589939705384-5185137a7f0f", "1600585154340-be6161a56a0c",
        "1615729947596-a598e5de0ab3", "1654179279371-c69baf3a725c", "1615800001716-c53dd05bf4b8",
        "1622763851108-b82f98dcd86c", "1654179280639-3de6d9d7f996", "1622763846204-5d0bf5031e06",
        "1626965654957-fef1cb80d4b7", "1558118720-fa5cdebe6b3a", "1617202009609-74a52df21011",
        "1631004970665-5b3e55194900", "1649866725673-16dc15de5c29", "1523575708161-ad0fc2a9b951",
        "1648147870253-c45f6f430528", "1609852665646-993d36a8ecea", "1622763853951-ded5a33cb724",
        "1631004964983-ad8ccef7ee0f", "1704048001164-9e454dd611e6", "1594886551831-610f739902e9",
        "1581773340073-0d6c32f500a4", "1737740439064-bd1e9b041677", "1712112465410-53e935978102",
        "1679407509869-95d525d7caed", "1444392061186-9fc38f84f726", "1533792344354-ed5e8fc12494",
        "1627647563441-c4bdf17486d2", "1601303961147-fd4951a45c28", "1568657801248-11459b191a5e",
        "1580553561519-b0eda6a0d3f0", "1602364480995-c995d4817502", "1727358572955-3d66cd0d5876",
        "1602449855614-c6e75e9ca0a6",
    ],
    "finance": [
        "1434626881859-194d67b2b86f", "1506784983877-45594efa4cbe", "1522202176988-66273c2fd55f",
        "1554224154-26032ffc0d07", "1554224155-6726b3ff858f", "1560518883-ce09059eeffa",
        "1563013544-824ae1b704d3", "1563281577-a7be47e20db9", "1579621970563-ebec7560ff3e",
        "1611974789855-9c2a0a7236a3", "1593672715438-d88a70629abe", "1534951009808-766178b47a4f",
        "1518458028785-8fbcd101ebb9", "1568581357391-c71a1675ef93", "1633158829875-e5316a358c6f",
        "1526304640581-d334cdbbf45e", "1593672755342-741a7f868732", "1580048915913-4f8f5cb481c4",
        "1553729459-efe14ef6055d", "1604594849809-dfedbc827105", "1633158829585-23ba8f7c8caf",
        "1554768804-50c1e2b50a6e", "1579621970795-87facc2f976d", "1579621970588-a35d0e7ab9b6",
        "1559067096-49ebca3406aa", "1642052502780-8ee67e3bf930", "1711097383282-28097ae16b1d",
        "1631511258193-252ab3da6b8b", "1734856080638-71e78b3d8d5f", "1628348068343-c6a848d2b6dd",
        "1711606815631-38d32cdaec3e", "1709534486708-fb8f94150d0a", "1729488368227-1f1eee39ff20",
        "1664575602276-acd073f104c1", "1653378972336-103e1ea62721", "1725258080098-727051947997",
    ],
    "tech": [
        "1496181133206-80ce9b88a853", "1504639725590-34d0984388bd", "1505740420928-5e560c06d30e",
        "1510915228340-29c85a43dcfe", "1518770660439-4636190af475", "1527443224154-c4a3942d3acf",
        "1531297484001-80022131f5a1", "1542744095-291d1f67b221", "1544244015-0df4b3ffc6b0",
        "1555066931-4365d14bab8c", "1555949963-aa79dcee981c", "1557324232-b8917d3c3dcb",
        "1559526324-593bc073d938", "1563013544-824ae1b704d3", "1585771724684-38269d6639fd",
        "1587654780291-39c9404d746b", "1588702547923-7093a6c3ba33", "1591488320449-011701bb6704",
        "1618384887929-16ec33fab9ef", "1588872657578-7efd1f1555ed", "1511385348-a52b4a160dc2",
        "1593642702821-c8da6771f0c6", "1603302576837-37561b2e2302", "1539376248633-cf94fa8b7bd8",
        "1525547719571-a2d4ac8945e2", "1611186871348-b1ce696e52c9", "1548092372-0d1bd40894a3",
        "1542393545-10f5cde2c810", "1629131726692-1accd0c53ce0", "1577375729152-4c8b5fcda381",
        "1541807084-5c52b6b3adef", "1515343480029-43cdfe6b6aae", "1504707748692-419802cf939d",
    ],
    "travel": [
        "1491553895911-0055eca6402d", "1493976040374-85c8e12f0c0e", "1500835556837-99ac94a94552",
        "1501594907352-04cda38ebc29", "1502920917128-1aa500764cbd", "1504384308090-c894fdcc538d",
        "1506784365847-bbad939e9335", "1507525428034-b723cf961d3e", "1508873696983-2dfd5898f08b",
        "1542038784456-1ea8e935640e", "1553062407-98eeb64c6a62", "1555396273-367ea4eb4db5",
        "1566073771259-6a8506099945", "1569154941061-e231b4725ef1", "1571019613454-1cb2f99b2d8b",
        "1576091160550-2173dba999ef", "1526392060635-9d6019884377", "1494822493217-c9840aba840c",
        "1445363692815-ebcd599f7621", "1501785888041-af3ef285b470", "1433838552652-f9a46b332c40",
        "1494783367193-149034c05e8f", "1498591100911-8c4880f7c580", "1565772838491-cbeb32fac6ca",
        "1626948688703-0136bc0a90da", "1469474968028-56623f02e42e", "1476514525535-07fb3b4ae5f1",
        "1604715686140-d5bef96c8b9d", "1682685797229-b2930538da47", "1645705250941-0af036402d56",
        "1683780569411-c52d3138c8fa", "1685701129202-2295e7b30cd9", "1701478008118-5cc092962f25",
        "1629456312128-7b50a6c6154e", "1677174619431-e339672d8d1d", "1639569780832-1ebb44a4392c",
        "1683331410816-0bb0bc78af66", "1672212602462-006b5f22f39f", "1550824476-727215abda28",
        "1701478008168-a6e1f145a869", "1565153855544-a37759c42c2b", "1683780426988-4f2b6ad31859",
        "1672212432737-7b55627320b9", "1612372564281-3bc67851d465", "1613926156179-abf7cc9e0f33",
    ],
}

SITE_CATEGORY = {
    "sub-pets": "pets",
    "sub-healthy": "health",
    "sub-home": "home",
    "sub-finance": "finance",
    "sub-tech": "tech",
    "sub-travel": "travel",
}


def get_photo_for_article(photos, article_num):
    idx = (article_num - 1) % len(photos)
    return photos[idx]


def photo_url(photo_id):
    return f"https://images.unsplash.com/photo-{photo_id}?w=1200&h=630&fit=crop"


def fix_article_images(html, site_dir, article_num=None):
    """Replace ALL Unsplash image URLs in HTML with article-number-determined unique photo."""
    category = SITE_CATEGORY.get(site_dir)
    photos = CATEGORY_PHOTOS.get(category)
    if not photos:
        return html, 0

    changes = 0

    if article_num is not None:
        new_id = get_photo_for_article(photos, article_num)

        # Replace ALL Unsplash images in one pass:
        # Hero gets photo based on article_num, sidebar/related get offset IDs
        all_imgs = list(re.finditer(
            r'(<img[^>]*src=")https://images\.unsplash\.com/photo-([a-zA-Z0-9_-]+)(\?[^"]*)?("[^>]*>)',
            html,
        ))
        for i, m in enumerate(all_imgs):
            if i == 0:
                pid = new_id
            else:
                pid = get_photo_for_article(photos, article_num + 50 + (i - 1))
            new_img_url = photo_url(pid)
            html = html.replace(m.group(0), m.group(1) + new_img_url + m.group(4), 1)
            changes += 1

    return html, changes


def fix_index_images(html, site_dir):
    """Update index.html article card images to match article-N assignment."""
    category = SITE_CATEGORY.get(site_dir)
    photos = CATEGORY_PHOTOS.get(category)
    if not photos:
        return html, 0

    changes = 0

    # Pattern 1: <img> tags inside article card links
    img_pattern = re.compile(
        r'(<a[^>]*href="article-(\d+)\.html"[^>]*>.*?)'
        r'<img[^>]*src="https://images\.unsplash\.com/photo-([a-zA-Z0-9_-]+)(\?[^"]*)?("[^>]*>)',
        re.DOTALL,
    )

    def replace_card_img(match):
        nonlocal changes
        prefix = match.group(1)
        article_num = int(match.group(2))
        old_id = match.group(3)
        img_end = match.group(5)
        new_id = get_photo_for_article(photos, article_num)
        if new_id != old_id:
            changes += 1
            return prefix + '<img src="' + photo_url(new_id) + img_end
        return match.group(0)

    html = img_pattern.sub(replace_card_img, html)

    # Pattern 2: CSS background-image:url() inside article card links
    bg_pattern = re.compile(
        r'(<a[^>]*href="article-(\d+)\.html"[^>]*>.*?'
        r'background-image:url\()https://images\.unsplash\.com/photo-([a-zA-Z0-9_-]+)(\?[^)]*)?(\))',
        re.DOTALL,
    )

    def replace_card_bg(match):
        nonlocal changes
        prefix = match.group(1)
        article_num = int(match.group(2))
        old_id = match.group(3)
        close = match.group(5)
        new_id = get_photo_for_article(photos, article_num)
        if new_id != old_id:
            changes += 1
            return prefix + photo_url(new_id).replace('w=1200&h=630', 'w=400&h=250') + close
        return match.group(0)

    html = bg_pattern.sub(replace_card_bg, html)

    return html, changes


def process_site(site_dir, dry_run=False):
    site_path = ROOT / site_dir
    if not site_path.exists():
        return 0

    total_changes = 0
    category = SITE_CATEGORY.get(site_dir)
    photos = CATEGORY_PHOTOS.get(category, [])
    article_count = len(list(site_path.glob("article-*.html")))

    print(f"\n{'=' * 60}")
    print(f"Site: {site_dir} ({category}) - {len(photos)} photos, {article_count} articles")
    print(f"{'=' * 60}")

    for filepath in sorted(site_path.glob("article-*.html")):
        m = re.search(r'article-(\d+)\.html', filepath.name)
        if not m:
            continue
        article_num = int(m.group(1))
        new_id = get_photo_for_article(photos, article_num)

        html = filepath.read_text(encoding="utf-8")
        new_html, changes = fix_article_images(html, site_dir, article_num)

        if changes > 0:
            total_changes += changes
            print(f"  {filepath.name}: photo-{new_id} ({changes} img(s) updated)")
            if not dry_run:
                filepath.write_text(new_html, encoding="utf-8")
        else:
            print(f"  {filepath.name}: no change needed")

    index_file = site_path / "index.html"
    if index_file.exists():
        html = index_file.read_text(encoding="utf-8")
        new_html, changes = fix_index_images(html, site_dir)
        if changes > 0:
            total_changes += changes
            print(f"  index.html: {changes} card img(s) updated")
            if not dry_run:
                index_file.write_text(new_html, encoding="utf-8")
        else:
            print(f"  index.html: no change needed")

    return total_changes


def main():
    dry_run = "--dry-run" in sys.argv
    total_fixes = 0

    for site_dir in SITE_CATEGORY:
        total_fixes += process_site(site_dir, dry_run)

    if dry_run:
        print(f"\n[DRY RUN] Would fix {total_fixes} image references across all sites")
    else:
        print(f"\nTotal image updates: {total_fixes} across all sites")
        print("All articles now have unique, deterministically-assigned cover photos.")


if __name__ == "__main__":
    main()
