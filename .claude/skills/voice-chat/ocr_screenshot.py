"""截图文字识别 - 基于 EasyOCR，支持中英文"""
import sys, json, os

_reader = None

def get_reader():
    global _reader
    if _reader is None:
        import easyocr
        _reader = easyocr.Reader(['ch_sim', 'en'], gpu=False)
    return _reader

def ocr(image_path):
    reader = get_reader()
    results = reader.readtext(image_path)
    texts = []
    for bbox, text, confidence in results:
        if confidence > 0.3:
            texts.append({"text": text, "confidence": round(confidence, 2)})
    return {
        "status": "success",
        "image": os.path.basename(image_path),
        "lines": texts,
        "full_text": "\n".join([t["text"] for t in texts])
    }

if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else None
    if not path or not os.path.exists(path):
        print(json.dumps({"status": "error", "error": "请提供有效截图路径"}, ensure_ascii=False))
        sys.exit(1)
    print(json.dumps(ocr(path), ensure_ascii=False, indent=2))
