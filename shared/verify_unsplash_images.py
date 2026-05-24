"""Batch download Unsplash candidate images and verify with doubao vision.
Usage: py shared/verify_unsplash_images.py

For each candidate photo ID, this script:
1. Downloads the image from Unsplash
2. Runs doubao_vision.py to verify topic relevance
3. Reports pass/fail
4. Removes failed/unmatched images
"""

import os
import sys
import subprocess
import urllib.request
import json
from pathlib import Path

CANDIDATES = {
    "rightsdaily": {  # Legal / Justice
        "ids": [
            # Courtroom, gavel, justice
            ("_ksc72z_rcI", "judge gaveling in courtroom"),
            ("6TcMkFODsw8", "scales of justice and gavel"),
            ("q7sJWE4pUFE", "judge and lawyer in courtroom"),
            ("l7xInzFp06w", "woman holding law book and scale of justice"),
            # Law books, legal documents
            ("6ZpEM4768jQ", "abstract person with fingerprint legal"),
            ("1j3MHz9_zVU", "chains handcuffs justice illustration"),
            ("pqIGOZ1AVao", "prison facility correctional"),
            ("3yVwrflw6Ig", "prison cell bars"),
            # Common free legal-themed images
            ("MW2kLAOWzoc", "law books on shelf"),
            ("rBENhh-LHnI", "handshake agreement contract"),
        ],
        "topic": "law, justice, courtroom, legal, gavel, court, lawyer, judge",
    },
    "dailymedadvice": {  # Health & Medical
        "ids": [
            ("ykaX_yNW6pE", "doctor examines patient in hospital room"),
            ("hx8VUzrUQCs", "doctor holding stethoscope behind back"),
            ("Hg5Sbs4Vbjg", "medical team with newborn baby"),
            ("5nW7DxxTmak", "doctors performing operation"),
            ("AECiOEX_-DE", "doctor holding senior cancer patient hand"),
            ("onxaOSNRLPM", "woman injecting insulin abdomen"),
            ("FXXCZQL06zo", "doctor examines blood with stethoscope"),
            ("wVhwJcgwsaE", "closeup of heart and stethoscope"),
            ("Kp8FQiwk_lM", "medical tools on hospital table"),
            ("00heEp9LFP0", "stethoscope on pile of books"),
            ("v74BLXAd-OY", "african american doctor with stethoscope"),
            ("mmzuzrieEXg", "stethoscope on stack of money"),
        ],
        "topic": "doctor, hospital, medical, healthcare, health, medicine, stethoscope, patient",
    },
    "entertainment": {  # Entertainment
        "ids": [
            ("nlsLaOYD8qw", "man singing into microphone on stage"),
            ("z0R4XB25ozI", "crowd with hands up at bright concert"),
            ("MfIKAV5Lu2s", "group playing instruments on stage"),
            ("QfZGVaansQ4", "audience watching movie in theater"),
            ("xyg2_Rg8jeg", "people in 3D glasses watching movie"),
            ("bdKbtHuBk4s", "grand staircase with red carpet"),
            ("UOJCdSmf-dg", "people celebrating under red lights concert"),
            ("7tpGVKWFesM", "two women laughing enjoying concert"),
            ("V0_gHwsrCg4", "man crowd surfing at concert"),
            ("jNZ97-wyGbA", "textured deep red background carpet"),
            # Additional entertainment
            ("6g3Mvq3I2YI", "popcorn and movie theater seat"),
            ("H0L7iMx1Scs", "stage performance theater lights"),
        ],
        "topic": "concert, movie, theater, cinema, entertainment, music, stage, performance, celebrity, red carpet",
    },
}

TEMP_DIR = Path("d:/tmp/unsplash_verify")
TEMP_DIR.mkdir(parents=True, exist_ok=True)

RESULTS = {}


def download_photo(photo_id, site_name):
    """Download photo from Unsplash. Returns path if success, None if fail."""
    url = f"https://images.unsplash.com/photo-{photo_id}?w=800"
    dest = TEMP_DIR / f"{site_name}_{photo_id}.jpg"
    if dest.exists():
        return dest
    try:
        req = urllib.request.Request(url, headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        })
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = resp.read()
        if len(data) < 1000:
            print(f"  TOO SMALL ({len(data)} bytes): {photo_id}")
            return None
        dest.write_bytes(data)
        print(f"  Downloaded: {photo_id} ({len(data)} bytes)")
        return dest
    except Exception as e:
        print(f"  FAIL download: {photo_id} → {e}")
        return None


def verify_with_doubao(image_path, expected_topic):
    """Use doubao_vision.py to check if image matches expected topic."""
    prompt = f"Is this image related to {expected_topic}? Answer YES or NO and explain briefly in one sentence."
    try:
        result = subprocess.run(
            ["python", "shared/doubao_vision.py", str(image_path), prompt],
            capture_output=True, text=True, timeout=60,
            cwd="d:/AI网站文件夹"
        )
        # doubao writes result to temp file, not stdout
        outfile = os.path.join(os.environ.get('TEMP', os.environ.get('TMP', '/tmp')), 'doubao_vision_output.txt')
        verify_output = ""
        if os.path.exists(outfile):
            with open(outfile, 'r', encoding='utf-8') as f:
                verify_output = f.read().strip()
            os.unlink(outfile)

        # Fatal doubao API error → stop immediately
        if verify_output.startswith("ERROR:FATAL_DOUBAO_ERROR:") or result.returncode != 0:
            err_detail = verify_output.replace("ERROR:FATAL_DOUBAO_ERROR:", "").strip() if verify_output.startswith("ERROR:") else "doubao_vision.py failed"
            raise RuntimeError(f"DOUBAO_API_FATAL: {err_detail}")

        if not verify_output:
            return False, "doubao returned empty"
        is_relevant = verify_output.strip().upper().startswith("YES")
        return is_relevant, verify_output[:200]
    except RuntimeError:
        raise
    except subprocess.TimeoutExpired:
        return False, "Timeout"
    except Exception as e:
        return False, str(e)


def main():
    print("=" * 60)
    print("Unsplash Image Verification Pipeline")
    print("=" * 60)

    for site_name, site_data in CANDIDATES.items():
        print(f"\n--- {site_name} (topic: {site_data['topic']}) ---")
        site_results = []
        for photo_id, desc in site_data["ids"]:
            print(f"\n  Checking {photo_id} ({desc})...")
            path = download_photo(photo_id, site_name)
            if not path:
                site_results.append((photo_id, desc, "FAIL_DOWNLOAD"))
                continue

            passed, info = verify_with_doubao(path, site_data["topic"])
            if passed:
                site_results.append((photo_id, desc, "PASS", info))
                print(f"  ✓ PASS: {photo_id}")
            else:
                site_results.append((photo_id, desc, "FAIL_VERIFY", info))
                print(f"  ✗ FAIL: {photo_id} → {info}")
                # Delete failed images
                path.unlink(missing_ok=True)
                print(f"    Deleted: {path.name}")

        RESULTS[site_name] = site_results

    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    for site_name, results in RESULTS.items():
        passed = [r for r in results if r[2] == "PASS"]
        failed = [r for r in results if r[2] != "PASS"]
        print(f"\n{site_name}: {len(passed)} passed, {len(failed)} failed")
        if passed:
            print("  PASSED IDs:")
            for r in passed:
                print(f"    - {r[0]} ({r[1]})")
        if failed:
            print("  FAILED IDs:")
            for r in failed:
                print(f"    - {r[0]} ({r[1]}) → {r[2]}: {r[3]}")

    # Output JSON for programmatic use
    result_json = {}
    for site_name, results in RESULTS.items():
        result_json[site_name] = {
            "passed": [r[0] for r in results if r[2] == "PASS"],
            "failed": [{"id": r[0], "reason": r[2]} for r in results if r[2] != "PASS"],
        }

    out_path = TEMP_DIR / "verification_results.json"
    out_path.write_text(json.dumps(result_json, indent=2))
    print(f"\nResults saved to: {out_path}")


if __name__ == "__main__":
    main()
