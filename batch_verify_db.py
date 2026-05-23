#!/usr/bin/env python3
"""Batch verify dragonball character images using doubao_vision API."""
import subprocess, json, sys, os, time
from pathlib import Path

CHARACTERS = [
    'super-17', 'kami', 'mr-popo', 'nail', 'android-16', 'jaco',
    'oolong', 'puar', 'launch', 'ox-king', 'grandpa-gohan', 'vegito',
    'gogeta', 'nuova-shenron', 'eis-shenron', 'general-rilldo', 'ribrianne',
    'anilaza', 'bardock-dbs', 'gine', 'tarble', 'king-vegeta', 'paragus',
    'cheelai', 'monaka', 'fortuneteller-baba', 'nam', 'king-chappa'
]

IMAGE_DIR = Path('/root/my-first-site30/dragonball-site/images')
DOUBAO = '/root/my-first-site30/shared/doubao_vision.py'
OUTFILE = '/tmp/doubao_vision_output.txt'
REPORT = '/root/my-first-site30/dragonball_image_audit.json'
PROMPT = 'What character from what series is this image showing? Just answer: character name, series name'


def find_image(name):
    """Find image file for character, trying extensions and separators."""
    for ext in ['.png', '.jpg', '.webp']:
        # try original (mostly hyphen-separated)
        f = IMAGE_DIR / f'{name}{ext}'
        if f.exists():
            return str(f)
        # try underscore variant
        f = IMAGE_DIR / f'{name.replace("-", "_")}{ext}'
        if f.exists():
            return str(f)
        # try dotted variant (e.g. mr.-popo)
        if '.' in name:
            f = IMAGE_DIR / f'{name}{ext}'
            if f.exists():
                return str(f)
    return None


def parse_result(text):
    """Parse doubao_vision output into (identified_as, series)."""
    text = text.strip()
    # If no character identified
    no_char = [
        'no character', 'not a character', 'not depict', 'there is no',
        'this is not', 'cannot identify', 'unable to identify',
        'no recognizable', 'no clear', 'not sure', 'does not appear',
        'i cannot', 'no specific character', 'no known character'
    ]
    if any(p in text.lower() for p in no_char):
        return None, None

    # Parse "name, series" format
    if ',' in text:
        parts = [p.strip().rstrip('.').strip() for p in text.split(',', 1)]
        return parts[0], parts[-1]

    # Fallback: first line, unknown series
    first_line = text.split('\n')[0].strip().rstrip('.')
    return first_line, 'unknown'


def normalize(s):
    return s.lower().replace('-', ' ').replace('_', ' ').strip()


def check_match(char_name, identified, series):
    """Check if identified character matches expected."""
    if identified is None:
        return False, 'No character identified'

    ne = normalize(char_name)
    ni = normalize(identified)

    if ne == ni:
        return True, f'Correct: {identified} from {series}'

    # Partial match: check if significant words overlap
    we = set(ne.split())
    wi = set(ni.split())
    common = we & wi
    if common and len(common) >= min(len(we), len(wi)):
        return True, f'Partial match: {identified} from {series}'

    return False, f'Wrong: identified as {identified} from {series}'


def main():
    results = []
    correct = wrong = errors = 0

    print(f'Batch verifying {len(CHARACTERS)} characters...\n')

    for i, ch in enumerate(CHARACTERS, 1):
        print(f'[{i}/{len(CHARACTERS)}] {ch}...', end=' ', flush=True)

        img = find_image(ch)
        if not img:
            print('FILE NOT FOUND')
            results.append({
                'name': ch, 'file': None, 'exists': False,
                'identified_as': None, 'series': None,
                'match': False, 'note': 'Image file not found'
            })
            errors += 1
            continue

        # Call doubao_vision
        try:
            r = subprocess.run(
                ['python3', DOUBAO, img, PROMPT],
                capture_output=True, text=True, timeout=120
            )
            if r.returncode != 0:
                raise RuntimeError(
                    f'doubao_vision exit {r.returncode}: {r.stderr[:200]}'
                )
        except subprocess.TimeoutExpired:
            print('TIMEOUT')
            results.append({
                'name': ch, 'file': os.path.basename(img), 'exists': True,
                'identified_as': None, 'series': None, 'match': False,
                'note': 'API timeout'
            })
            errors += 1
            continue
        except Exception as e:
            print(f'ERROR: {e}')
            results.append({
                'name': ch, 'file': os.path.basename(img), 'exists': True,
                'identified_as': None, 'series': None, 'match': False,
                'note': f'Subprocess error: {str(e)[:100]}'
            })
            errors += 1
            continue

        # Read output
        if not os.path.exists(OUTFILE):
            print('NO OUTPUT')
            results.append({
                'name': ch, 'file': os.path.basename(img), 'exists': True,
                'identified_as': None, 'series': None, 'match': False,
                'note': 'No output file generated'
            })
            errors += 1
            continue

        with open(OUTFILE, 'r') as f:
            raw_text = f.read().strip()

        identified, series = parse_result(raw_text)
        match, note = check_match(ch, identified, series)

        if match:
            correct += 1
            status = 'OK'
        elif identified is None:
            errors += 1
            status = 'ERR'
        else:
            wrong += 1
            status = 'MISMATCH'

        print(f'{status}: {identified or "N/A"} / {series or "N/A"}')

        results.append({
            'name': ch,
            'file': os.path.basename(img),
            'exists': True,
            'identified_as': identified,
            'series': series,
            'match': match,
            'note': note
        })

        time.sleep(1)

    # Write report
    report = {
        'characters': results,
        'correct': correct,
        'wrong': wrong,
        'error': errors,
        'total': len(CHARACTERS)
    }
    with open(REPORT, 'w') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    print(f'\nReport written to: {REPORT}')
    print(f'Results: {correct} correct, {wrong} wrong, {errors} errors / {len(CHARACTERS)} total')


if __name__ == '__main__':
    main()
