"""Add AutoPulse option between TripRoute and RightsDaily in sub-auto footer."""
import os, glob

html_dir = r"d:\AI网站文件夹\sub-auto"
files = sorted(glob.glob(os.path.join(html_dir, "*.html")))

trip_line = '                    <option value="https://travel.jycsd.com">TripRoute</option>'
auto_line = '                    <option value="https://auto.jycsd.com">AutoPulse</option>'
rights_line = '                    <option value="https://rightsdaily.com">RightsDaily</option>'

modified = 0
skipped_already = 0
skipped_no_match = 0

for fp in files:
    with open(fp, "r", encoding="utf-8") as f:
        content = f.read()

    # Skip if auto.jycsd.com already appears in footer context
    if auto_line in content:
        skipped_already += 1
        continue

    # Check pattern exists
    if trip_line not in content or rights_line not in content:
        skipped_no_match += 1
        continue

    # Replace: after TripRoute line, add AutoPulse line
    old = trip_line + "\n" + rights_line
    new = trip_line + "\n" + auto_line + "\n" + rights_line
    new_content = content.replace(old, new)

    with open(fp, "w", encoding="utf-8") as f:
        f.write(new_content)

    modified += 1
    print(f"  [MODIFIED] {os.path.basename(fp)}")

print(f"\nDone. Modified: {modified}, Already had it: {skipped_already}, No match: {skipped_no_match}")
