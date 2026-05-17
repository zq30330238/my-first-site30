"""Douyin-optimized video generator — kinetic typography, 9:16, algorithm-aware.

Key Douyin ranking factors baked in:
- 7-15s sweet spot for completion rate
- First 0.5s hook (text appears instantly)
- Word-by-word reveal to hold attention
- CTA card at end to drive engagement
"""

import json, os, sys, textwrap, math
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import imageio

W, H = 1080, 1920
# imageio wants macro_block_size=16 compatible; 1080 is not divisible by 16
# Use 1088x1920 for encoding, then we don't care about the slight difference
FPS = 30

FONT_CACHE = {}

def get_font(size):
    if size not in FONT_CACHE:
        for fp in ["C:/Windows/Fonts/msyh.ttc", "C:/Windows/Fonts/simhei.ttf",
                    "C:/Windows/Fonts/simsun.ttc", "C:/Windows/Fonts/STKAITI.TTF"]:
            if os.path.exists(fp):
                FONT_CACHE[size] = ImageFont.truetype(fp, size)
                return FONT_CACHE[size]
        FONT_CACHE[size] = ImageFont.load_default()
    return FONT_CACHE[size]

def wrap_line(text, font, max_w, draw):
    lines, cur = [], ""
    for ch in text:
        test = cur + ch
        if draw.textbbox((0, 0), test, font=font)[2] <= max_w:
            cur = test
        else:
            if cur: lines.append(cur)
            cur = ch
    if cur: lines.append(cur)
    return lines

def render_text_frame(lines, font, bg=(18, 18, 18), fg=(255, 255, 255),
                       line_spacing=8, accent_words=None, progress=1.0):
    """Render centered text. progress < 1.0 means partial reveal (word-by-word)."""
    img = Image.new("RGB", (W, H), bg)
    draw = ImageDraw.Draw(img)
    wrapped = []
    for line in lines:
        wrapped.extend(wrap_line(line, font, W - 160, draw))
    total_h = len(wrapped) * (font.size + line_spacing) - line_spacing
    y0 = max(60, (H - total_h) // 2)

    # Determine how many chars to show
    all_text = "".join(wrapped)
    char_count = int(len(all_text) * progress)

    count = 0
    for i, line in enumerate(wrapped):
        tw = draw.textbbox((0, 0), line, font=font)[2]
        x = (W - tw) // 2
        y = y0 + i * (font.size + line_spacing)
        visible = ""
        for ch in line:
            if count < char_count:
                visible += ch
                count += 1
            else:
                break
        if visible:
            draw.text((x + 2, y + 2), visible, font=font, fill=(40, 40, 40))
            draw.text((x, y), visible, font=font, fill=fg)
    return img

def generate_douyin_video(config_dict, output_file):
    """Generate optimized Douyin video from config dict.

    config_dict keys:
        title: str
        scenes: [{"text": str or list, "duration": float, "animate": bool}]
        bg_color: [r,g,b]
        text_color: [r,g,b]
        font_size: int
        cta: str (optional end card call-to-action)
    """
    title = config_dict.get("title", "douyin")
    scenes = config_dict.get("scenes", [])
    bg = tuple(config_dict.get("bg_color", [18, 18, 18]))
    fg = tuple(config_dict.get("text_color", [255, 255, 255]))
    font_size = config_dict.get("font_size", 52)
    cta = config_dict.get("cta", "")
    font = get_font(font_size)

    print(f"Generating: {title} — {len(scenes)} scenes")

    frames = []

    # Scene 0: Instant hook (first 0.3s, full text appears)
    for scene in scenes:
        text = scene.get("text", "")
        if isinstance(text, str):
            text = [text]
        animate = scene.get("animate", False)
        duration = scene.get("duration", 2.5)
        n_frames = int(duration * FPS)

        if animate:
            # Word-by-word reveal across the scene duration
            for fi in range(n_frames):
                progress = (fi + 1) / n_frames
                frame = render_text_frame(text, font, bg=bg, fg=fg, progress=progress)
                frames.append(frame)
        else:
            # Static text for entire duration
            frame = render_text_frame(text, font, bg=bg, fg=fg, progress=1.0)
            for _ in range(n_frames):
                frames.append(frame)

    # CTA end card
    if cta:
        cta_font = get_font(44)
        cta_duration = 2.0
        cta_frames = int(cta_duration * FPS)
        cta_img = Image.new("RGB", (W, H), bg)
        draw = ImageDraw.Draw(cta_img)
        tw = draw.textbbox((0, 0), cta, font=cta_font)[2]
        x = (W - tw) // 2
        y = H - 200
        draw.text((x, y), cta, font=cta_font, fill=(200, 200, 200))
        for _ in range(cta_frames):
            frames.append(cta_img)

    if not frames:
        print("ERROR: No frames generated")
        return None

    if os.path.exists(output_file):
        os.remove(output_file)

    writer = imageio.get_writer(output_file, fps=FPS, format="FFMPEG",
                                 codec="libx264", quality=8)
    for frame in frames:
        writer.append_data(np.array(frame))
    writer.close()

    duration = len(frames) / FPS
    print(f"Done: {output_file} — {len(frames)} frames, {duration:.1f}s")
    return output_file

def ai_money_script(topic, hook, points, cta="关注我，每天一个AI搞钱技巧"):
    """Factory for AI-money-niche videos — the bread and butter format."""
    scenes = [
        {"text": hook, "duration": 2.0, "animate": False},  # instant hook
    ]
    for p in points:
        scenes.append({"text": p, "duration": 2.5, "animate": True})
    return {
        "title": topic,
        "scenes": scenes,
        "font_size": 52,
        "bg_color": [10, 10, 10],
        "text_color": [240, 240, 240],
        "cta": cta,
    }

def quote_script(topic, quote_text):
    """Factory for life-philosophy quote videos."""
    sentences = [s.strip() + "。" for s in quote_text.replace("！", "。").replace("？", "。").split("。") if s.strip()]
    scenes = []
    for i, s in enumerate(sentences):
        scenes.append({"text": s, "duration": 2.0 + len(s) * 0.03, "animate": True})
    return {
        "title": topic,
        "scenes": scenes,
        "font_size": 48,
        "bg_color": [15, 15, 25],
        "text_color": [255, 255, 240],
        "cta": "双击屏幕，收藏这句话",
    }

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python douyin_video.py --ai 'topic' 'hook' 'point1|point2|point3'")
        print("  python douyin_video.py --quote 'topic' 'quote text here'")
        print("  python douyin_video.py script.json output.mp4")
        sys.exit(1)

    cmd = sys.argv[1]
    out_dir = "d:/AI网站文件夹/videos"
    os.makedirs(out_dir, exist_ok=True)

    if cmd == "--ai" and len(sys.argv) >= 5:
        topic, hook, points_str = sys.argv[2], sys.argv[3], sys.argv[4]
        points = [p.strip() for p in points_str.split("|") if p.strip()]
        cfg = ai_money_script(topic, hook, points)
        out = f"{out_dir}/ai_{topic[:8].replace(' ','_')}.mp4"
        generate_douyin_video(cfg, out)
        print(f"Output: {out}")

    elif cmd == "--quote" and len(sys.argv) >= 4:
        topic, quote = sys.argv[2], sys.argv[3]
        cfg = quote_script(topic, quote)
        out = f"{out_dir}/quote_{topic[:8].replace(' ','_')}.mp4"
        generate_douyin_video(cfg, out)
        print(f"Output: {out}")

    elif cmd.endswith(".json"):
        out = sys.argv[2] if len(sys.argv) > 2 else f"{out_dir}/output.mp4"
        with open(cmd, "r", encoding="utf-8") as f:
            cfg = json.load(f)
        generate_douyin_video(cfg, out)
        print(f"Output: {out}")

    else:
        print(f"Unknown command: {cmd}")
