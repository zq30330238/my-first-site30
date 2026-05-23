"""Add legal disclaimers to article HTML files in sub-finance and sub-healthy."""
import os, glob

BASE = "d:/AI网站文件夹"

FINANCE_DISCLAIMER = '''    <!-- Disclaimer -->
    <div class="max-w-6xl mx-auto px-4 py-4">
        <div class="bg-blue-50 border-l-4 border-blue-500 p-4 rounded-r-lg">
            <p class="text-xs text-gray-700 leading-relaxed">
                <strong>Disclaimer:</strong> The content on this site is for informational and educational purposes only and does not constitute financial advice. Always consult a licensed financial professional before making investment decisions.
            </p>
        </div>
    </div>'''

HEALTHY_DISCLAIMER = '''    <!-- Disclaimer -->
    <div class="max-w-6xl mx-auto px-4 py-4">
        <div class="bg-green-50 border-l-4 border-green-500 p-4 rounded-r-lg">
            <p class="text-xs text-gray-700 leading-relaxed">
                <strong>Disclaimer:</strong> The content on this site is for informational and educational purposes only and is not a substitute for professional medical advice. Always consult a healthcare provider with any questions about your health.
            </p>
        </div>
    </div>'''

SITES = {
    "sub-finance": FINANCE_DISCLAIMER,
    "sub-healthy": HEALTHY_DISCLAIMER,
}

modified = []
skipped = []

for subdir, disclaimer in SITES.items():
    pattern = os.path.join(BASE, subdir, "article-*.html")
    files = sorted(glob.glob(pattern))
    for fp in files:
        with open(fp, "r", encoding="utf-8") as f:
            content = f.read()

        if "Disclaimer:" in content:
            skipped.append(fp)
            continue

        # Insert disclaimer right before the <footer tag
        new_content = content.replace("<footer", f"{disclaimer}\n\n    <footer", 1)

        if new_content == content:
            skipped.append(fp)  # <footer not found
            continue

        with open(fp, "w", encoding="utf-8") as f:
            f.write(new_content)
        modified.append(fp)

print(f"=== Results ===")
print(f"Modified: {len(modified)} files")
for p in modified:
    print(f"  + {os.path.relpath(p, BASE)}")
print(f"Skipped: {len(skipped)} files")
for p in skipped:
    print(f"  - {os.path.relpath(p, BASE)}")
