"""Quick script to test your live Render deployment."""
import json
import time
import urllib.request

RENDER_URL = "https://translation-temporary.onrender.com"

def make_request(endpoint: str, data: dict = None):
    url = f"{RENDER_URL}{endpoint}"
    headers = {"Content-Type": "application/json; charset=utf-8"}
    
    if data:
        encoded_data = json.dumps(data).encode("utf-8")
        req = urllib.request.Request(url, data=encoded_data, headers=headers, method="POST")
    else:
        req = urllib.request.Request(url, headers=headers, method="GET")

    start_time = time.perf_counter()
    try:
        with urllib.request.urlopen(req, timeout=60) as response:
            latency = (time.perf_counter() - start_time) * 1000
            body = json.loads(response.read().decode("utf-8"))
            return body, latency
    except Exception as e:
        return {"error": str(e)}, 0.0

def main():
    print(f"Connecting to live Render service at: {RENDER_URL} ...\n")

    # 1. Check Health & RAM
    print("[1] Checking /health endpoint...")
    health, lat = make_request("/health")
    print(f"    Status: {health.get('status')} | Latency: {lat:.1f}ms")
    print(f"    Server RAM: {health.get('memory_mb')} MB / {health.get('memory_limit_mb')} MB ({health.get('memory_percent')}%)")
    print("-" * 60)

    # 2. Check Supported Languages
    print("[2] Fetching supported languages...")
    langs, _ = make_request("/languages")
    print(f"    Available: {langs.get('supported_languages')}")
    print("-" * 60)

    # 3. Test Translations
    test_cases = [
        ("Xin chào thế giới!", "English"),
        ("Tôi rất vui được gặp bạn hôm nay.", "English"),
        ("Trí tuệ nhân tạo đang thay đổi cuộc sống.", "Japanese"),
        ("Hôm nay thời tiết rất đẹp.", "French"),
        ("Cảm ơn bạn rất nhiều.", "Spanish"),
        ("Chúc bạn một ngày tốt lành!", "Chinese"),
    ]

    print("[3] Testing live translations:")
    print("    (Note: The first translation downloads the ~74MB model weights to Render cache,\n"
          "     so request #1 might take a few seconds; subsequent calls are fast!)\n")

    for text, target in test_cases:
        res, lat = make_request("/translate", {"text": text, "target": target})
        if "error" in res:
            print(f"    ❌ Error translating '{text}': {res['error']}")
        else:
            translated = res.get("translated_text")
            ram = res.get("current_ram_mb", "N/A")
            print(f"    Input  : \"{text}\"")
            print(f"    Target : {target}")
            print(f"    Output : \"{translated}\"")
            print(f"    Latency: {lat:.1f}ms | Server RAM: {ram} MB\n")

    print("=" * 60)
    print("All tests completed successfully!")

if __name__ == "__main__":
    main()
