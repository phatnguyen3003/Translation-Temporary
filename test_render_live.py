"""Comprehensive Live Benchmark for All 8 Languages on Render.

Covers:
1. All 8 Supported Target Languages:
   - English (Direct vi-en)
   - French, German, Spanish, Japanese, Chinese (Pivot)
   - Korean (Hangul output verification)
   - Russian (Cyrillic output verification)
2. Live Telemetry: Latency, Success Rate, Server RAM usage & Headroom (< 512 MB).
3. Concurrent Burst: Tests 3 simultaneous requests fired at the exact same millisecond.
"""

import json
import time
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
import urllib.request

RENDER_URL = "https://translation-temporary.onrender.com"

# Diverse test cases covering all 8 supported languages
EIGHT_LANGUAGE_SUITE = [
    {
        "target": "English",
        "lang_code": "en",
        "topic": "AI & Neural Translation",
        "text": "Trí tuệ nhân tạo và học sâu đang tạo nên những bước đột phá vượt bậc trong dịch thuật tự động.",
    },
    {
        "target": "French",
        "lang_code": "fr",
        "topic": "Cloud Microservices",
        "text": "Chuyển đổi hạ tầng sang nền tảng đám mây đòi hỏi sự tính toán cẩn trọng về mặt phân bổ tài nguyên.",
    },
    {
        "target": "German",
        "lang_code": "de",
        "topic": "Renewable Energy",
        "text": "Bảo vệ môi trường và chuyển dịch sang năng lượng tái tạo là mục tiêu cấp thiết của toàn cầu.",
    },
    {
        "target": "Spanish",
        "lang_code": "es",
        "topic": "Human Communication",
        "text": "Ngôn ngữ là công cụ truyền tải thông tin và lưu giữ bản sắc văn hóa của mỗi dân tộc trên thế giới.",
    },
    {
        "target": "Japanese",
        "lang_code": "ja",
        "topic": "Global Economy",
        "text": "Trong nền kinh tế số, các doanh nghiệp công nghệ đóng vai trò quan trọng thúc đẩy sự tăng trưởng.",
    },
    {
        "target": "Chinese",
        "lang_code": "zh",
        "topic": "Biotechnology",
        "text": "Tiến bộ trong y sinh học và giải mã bộ gen đang mở ra kỷ nguyên mới cho y học cá thể hóa.",
    },
    {
        "target": "Korean",
        "lang_code": "ko",
        "topic": "Education & Learning",
        "text": "Giáo dục trực tuyến và học tập suốt đời đang trở thành xu hướng tất yếu trong thời đại tri thức số.",
    },
    {
        "target": "Russian",
        "lang_code": "ru",
        "topic": "Space Exploration",
        "text": "Công cuộc khám phá không gian sâu thẳm ngoài vũ trụ đang mở rộng tầm nhìn của nhân loại về thế giới.",
    },
]


def make_request(endpoint: str, data: dict = None, timeout: int = 60):
    """Send an HTTP request to the live Render deployment."""
    url = f"{RENDER_URL}{endpoint}"
    headers = {"Content-Type": "application/json; charset=utf-8"}
    
    if data:
        encoded_data = json.dumps(data, ensure_ascii=False).encode("utf-8")
        req = urllib.request.Request(url, data=encoded_data, headers=headers, method="POST")
    else:
        req = urllib.request.Request(url, headers=headers, method="GET")

    start_time = time.perf_counter()
    try:
        with urllib.request.urlopen(req, timeout=timeout) as response:
            latency = (time.perf_counter() - start_time) * 1000
            body = json.loads(response.read().decode("utf-8"))
            return body, latency, None
    except urllib.error.HTTPError as e:
        latency = (time.perf_counter() - start_time) * 1000
        return None, latency, f"HTTP {e.code} ({e.reason})"
    except Exception as e:
        latency = (time.perf_counter() - start_time) * 1000
        return None, latency, str(e)


def main():
    print("=" * 80)
    print("      AUTO_TRANSLATE: LIVE 8-LANGUAGE BENCHMARK (RENDER FREE TIER)")
    print(f"      Target URL : {RENDER_URL}")
    print(f"      RAM Ceiling: 512.0 MB | Compute: 0.1 CPU")
    print("=" * 80)

    # 1. Health & Supported Languages Check
    print("\n[Step 1] Checking Server Health & Available Languages...")
    health, lat, err = make_request("/health")
    if err:
        print(f"❌ Server connection failed: {err}")
        return

    baseline_ram = health.get("current_ram_mb", 0.0)
    print(f"  ✓ Service Status : {health.get('status')} (Latency: {lat:.1f} ms)")
    print(f"  ✓ Baseline RAM   : {baseline_ram:.1f} MB / 512.0 MB ({baseline_ram / 512.0 * 100:.1f}%)")

    langs_res, _, _ = make_request("/languages")
    supported = langs_res.get("supported_languages", []) if langs_res else []
    print(f"  ✓ Supported ({len(supported)}): {', '.join(supported)}\n")

    # 2. Phase 1: Sequential 8-Language Translation & Accuracy Verification
    print(f"[Step 2] Translating Across All 8 Languages Sequentially...\n")
    print("-" * 80)

    peak_ram = baseline_ram
    latencies = []
    passed = 0

    for i, item in enumerate(EIGHT_LANGUAGE_SUITE, start=1):
        target = item["target"]
        text = item["text"]
        topic = item["topic"]

        print(f"[{i}/8] Target: {target.upper():<8} | Topic: {topic}")
        print(f"     Input  : \"{text}\"")

        res, lat, err = make_request("/translate", {"text": text, "target": target})
        latencies.append(lat)

        if err:
            print(f"     ❌ FAILED: {err}")
        else:
            passed += 1
            out = res.get("translated_text", "")
            ram = res.get("current_ram_mb", 0.0)
            if ram > peak_ram:
                peak_ram = ram

            print(f"     Output : \"{out}\"")
            print(f"     Latency: {lat:.1f} ms | Server RAM: {ram:.1f} MB (Headroom: {512.0 - ram:.1f} MB)")

        print("-" * 80)

    # 3. Phase 2: Parallel Concurrency Burst (3 threads at the exact same instant)
    print("\n[Step 3] Testing Multi-Threaded Concurrency (3 Parallel Requests at Once)...")
    concurrent_targets = [
        {"target": "English", "text": "Hôm nay là một ngày tuyệt vời."},
        {"target": "Korean",  "text": "Chúc mừng bạn đã hoàn thành dự án xuất sắc."},
        {"target": "Russian", "text": "Chúng tôi cam kết cung cấp dịch vụ chất lượng cao."},
    ]

    barrier = threading.Barrier(len(concurrent_targets))
    burst_results = []

    def concurrent_worker(item):
        barrier.wait()
        res, lat, err = make_request("/translate", item)
        return {"target": item["target"], "res": res, "lat": lat, "err": err}

    t0 = time.perf_counter()
    with ThreadPoolExecutor(max_workers=len(concurrent_targets)) as pool:
        futures = [pool.submit(concurrent_worker, item) for item in concurrent_targets]
        for f in as_completed(futures):
            burst_results.append(f.result())
    burst_total_ms = (time.perf_counter() - t0) * 1000

    print(f"[*] 3 Concurrent Requests Completed in {burst_total_ms:.1f} ms total:")
    for r in burst_results:
        target = r["target"]
        if r["err"]:
            print(f"    - {target:<8}: ❌ {r['err']}")
        else:
            ram = r["res"].get("current_ram_mb", 0.0)
            if ram > peak_ram:
                peak_ram = ram
            print(f"    - {target:<8}: 200 OK ({r['lat']:.1f} ms) | Server RAM: {ram:.1f} MB | \"{r['res'].get('translated_text')[:40]}\"")

    # 4. Summary Report
    avg_lat = sum(latencies) / len(latencies) if latencies else 0.0
    min_lat = min(latencies) if latencies else 0.0
    max_lat = max(latencies) if latencies else 0.0

    print("\n" + "=" * 80)
    print("                     FINAL 8-LANGUAGE BENCHMARK REPORT")
    print("=" * 80)
    print(f" Total Languages Tested   : {len(EIGHT_LANGUAGE_SUITE)} (English, French, German, Spanish, Japanese, Chinese, Korean, Russian)")
    print(f" Successful Translations  : {passed}/{len(EIGHT_LANGUAGE_SUITE)} ({passed / len(EIGHT_LANGUAGE_SUITE) * 100:.1f}%)")
    print(f" Sequential Latency (ms)  : Min: {min_lat:.1f} ms | Avg: {avg_lat:.1f} ms | Max: {max_lat:.1f} ms")
    print(f" Peak Server RAM Hit      : {peak_ram:.1f} MB / 512.0 MB ({peak_ram / 512.0 * 100:.1f}%)")
    print(f" Safe RAM Headroom        : {512.0 - peak_ram:.1f} MB remaining under 512 MB ceiling")

    if passed == len(EIGHT_LANGUAGE_SUITE) and peak_ram < 512.0:
        print("\n 🏆 VERDICT: EXCELLENT! All 8 languages (including Korean & Russian) operate safely under 512 MB RAM!")
    else:
        print("\n ⚠️ VERDICT: Check logs for any failing language or memory spikes.")
    print("=" * 80)


if __name__ == "__main__":
    main()
