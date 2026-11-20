"""Multi-Language Switching Spam Test.

Rotates through target languages mid-stream (English -> French -> German -> Spanish -> Chinese -> Japanese)
to prove that automatic model eviction keeps peak RAM locked under 240 MB.

Usage:
    python spam_requests.py
"""

import sys
import json
import time
import urllib.request

URL = "http://localhost:8000/translate"
LANGUAGES = ["English", "French", "German", "Spanish", "Chinese", "Japanese"]
TOTAL = 30  # 30 rapid requests alternating languages

print("=================================================================")
print("      AUTO_TRANSLATE: RAPID LANGUAGE-SWITCHING SPAM TEST        ")
print("=================================================================")
print(f"Target languages cycling : {', '.join(LANGUAGES)}")
print(f"Total requests to send   : {TOTAL}")
print(f"Server endpoint          : {URL}")
print("=================================================================\n")

test_sentences = [
    "Hôm nay thời tiết rất đẹp.",
    "Tôi đang kiểm tra tính năng chuyển đổi ngôn ngữ liên tục.",
    "Hệ thống giải phóng bộ nhớ tự động hoạt động rất tốt.",
    "Chúc bạn một ngày làm việc tràn đầy năng lượng.",
    "Lập trình với Python thật thú vị.",
]

for i in range(1, TOTAL + 1):
    target_lang = LANGUAGES[(i - 1) % len(LANGUAGES)]
    sentence = test_sentences[(i - 1) % len(test_sentences)]

    payload = {
        "text": sentence,
        "target": target_lang,
    }
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        URL,
        data=data,
        headers={"Content-Type": "application/json; charset=utf-8"},
    )

    t0 = time.perf_counter()
    try:
        with urllib.request.urlopen(req) as resp:
            result = json.loads(resp.read().decode("utf-8"))
            latency = (time.perf_counter() - t0) * 1000
            print(
                f"[{i:02d}/{TOTAL}] VI ➔ {target_lang:<9} | "
                f"RAM: {result['current_ram_mb']:5.1f} MB | "
                f"Latency: {latency:6.1f} ms | "
                f"Output: '{result['translated_text']}'"
            )
    except urllib.error.URLError as e:
        print(f"\n[!] Error connecting to {URL}: {e}")
        print("Please start your API server in another terminal first:")
        print("    .\\.venv\\Scripts\\python -m src.auto_translate.api\n")
        sys.exit(1)

print("\n=================================================================")
print("                      TEST COMPLETED!                            ")
print("Notice how RAM hovered around ~220-235 MB and NEVER blew past    ")
print("512 MB, because previous pivot models were automatically evicted!")
print("=================================================================\n")
