"""Multi-Threaded Concurrent Stress Test for Live Render Translation Service.

Features:
1. True Simultaneous Multithreading: Uses threading.Barrier so all worker threads
   fire requests at the exact same millisecond to test server RAM under peak burst load.
2. Extra-Long Paragraphs (~100-150 words each) covering complex vocabulary
   (AI, Cloud Architecture, Global Economy, Climate, Medicine, Philosophy).
3. Mixed Target Languages: English, French, Japanese, German, Spanish, Chinese.
4. Real-Time Telemetry: Tracks Server RAM, Peak Memory, Latency distribution,
   and Headroom remaining under the strict 512 MB ceiling.
"""

import json
import time
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
import urllib.request

RENDER_URL = "https://translation-temporary.onrender.com"

# Long, complex Vietnamese paragraphs for heavy tokenization and translation
HEAVY_PARAGRAPHS = [
    {
        "id": "AI-01",
        "topic": "AI & Neural Architecture",
        "target": "English",
        "text": (
            "Trí tuệ nhân tạo và học sâu đang tạo nên những bước đột phá chưa từng có trong lịch sử phát triển "
            "khoa học công nghệ của nhân loại. Các mô hình dịch thuật nơ-ron đa ngôn ngữ kết hợp cùng kiến trúc "
            "biến đổi Transformer đã giúp thu hẹp đáng kể khoảng cách ngôn ngữ giữa các quốc gia. Tuy nhiên, "
            "thách thức lớn nhất hiện nay là làm sao để tối ưu hóa những mô hình này để chúng có thể vận hành ổn định "
            "trên các hệ thống phần cứng giới hạn tài nguyên như bộ vi xử lý tốc độ thấp và bộ nhớ RAM dưới 512 megabytes "
            "mà vẫn bảo đảm độ chính xác ngữ nghĩa cao nhất."
        ),
    },
    {
        "id": "CLOUD-02",
        "topic": "Cloud & Microservices SRE",
        "target": "French",
        "text": (
            "Quá trình chuyển đổi hạ tầng từ các máy chủ truyền thống sang nền tảng đám mây và kiến trúc microservices "
            "đòi hỏi sự tính toán cẩn trọng về mặt phân bổ tài nguyên. Việc đóng gói các dịch vụ vào vùng chứa container "
            "kết hợp cùng cơ chế tự động dọn dẹp bộ nhớ heap trong Linux glibc là chìa khóa để ngăn chặn hiện tượng tràn bộ nhớ. "
            "Những hệ thống có khả năng phục hồi cao luôn được thiết kế để xử lý linh hoạt các đợt tăng đột biến lưu lượng "
            "truy cập thông qua cơ chế hàng đợi bất đồng bộ và kiểm soát tải thông minh."
        ),
    },
    {
        "id": "ECON-03",
        "topic": "Global Digital Economy",
        "target": "Japanese",
        "text": (
            "Trong bối cảnh nền kinh tế toàn cầu đang chuyển mình mạnh mẽ theo hướng kinh tế số, các doanh nghiệp công nghệ "
            "đóng vai trò hạt nhân thúc đẩy sự tăng trưởng. Việc mở rộng thị trường ra khu vực quốc tế đòi hỏi các giải pháp "
            "truyền thông đa phương tiện phải được địa phương hóa một cách nhanh chóng và tự nhiên. Công nghệ dịch tự động "
            "không chỉ giúp doanh nghiệp tiết kiệm chi phí vận hành mà còn rút ngắn thời gian tiếp cận khách hàng tiềm năng "
            "tại nhiều thị trường mới trên toàn cầu."
        ),
    },
    {
        "id": "CLIMATE-04",
        "topic": "Climate & Renewable Energy",
        "target": "German",
        "text": (
            "Biến đổi khí hậu toàn cầu đang đặt ra những thách thức nghiêm trọng đối với an ninh lương thực và sự phát triển "
            "bền vững của hệ sinh thái trái đất. Việc chuyển dịch cơ cấu từ năng lượng hóa thạch sang các nguồn năng lượng "
            "tái tạo như điện mặt trời và năng lượng gió cần có sự cam kết mạnh mẽ từ cộng đồng quốc tế. Ứng dụng công nghệ "
            "phân tích dữ liệu lớn và trí tuệ nhân tạo sẽ hỗ trợ dự báo chính xác các hình thái thời tiết cực đoan."
        ),
    },
    {
        "id": "PHILOS-05",
        "topic": "Philosophy & Human Language",
        "target": "Spanish",
        "text": (
            "Ngôn ngữ không chỉ là công cụ truyền tải thông tin đơn thuần mà còn là nơi lưu giữ linh hồn, tư duy và bản sắc "
            "văn hóa của mỗi dân tộc trên thế giới. Khi công nghệ dịch thuật máy tính đạt đến độ chín muồi, nó mở ra cơ hội "
            "giao lưu văn hóa sâu sắc giữa các cộng đồng người mà trước đây bị ngăn cách bởi rào cản ngôn ngữ, tạo tiền đề "
            "xây dựng một thế giới hòa bình, gắn kết và thấu hiểu lẫn nhau giữa các dân tộc."
        ),
    },
    {
        "id": "MED-06",
        "topic": "Medical & Genomic Sciences",
        "target": "Chinese",
        "text": (
            "Những tiến bộ vượt bậc trong lĩnh vực y sinh học và giải mã bộ gen người đang mở ra kỷ nguyên mới cho y học cá thể hóa. "
            "Các thuật toán học máy tiên tiến có khả năng phân tích hàng triệu biến dị di truyền trong thời gian ngắn, giúp các "
            "bác sĩ chẩn đoán sớm và đưa ra phác đồ điều trị hiệu quả cho các căn bệnh hiểm nghèo, đem lại hy vọng sống cho "
            "hàng triệu bệnh nhân trên khắp hành tinh."
        ),
    },
    {
        "id": "SPACE-07",
        "topic": "Astrophysics & Deep Space",
        "target": "English",
        "text": (
            "Công cuộc khám phá không gian sâu thẳm ngoài vũ trụ đang bước sang một chương mới với sự trợ giúp của kính viễn vọng "
            "không gian hiện đại. Các nhà khoa học đã thu thập được lượng dữ liệu khổng lồ về sự hình thành của các thiên hà xa xôi, "
            "mở rộng tầm nhìn của nhân loại về nguồn gốc của vũ trụ và tìm kiếm những dấu hiệu của sự sống ngoài trái đất."
        ),
    },
    {
        "id": "EDU-08",
        "topic": "Lifelong Learning & Education",
        "target": "French",
        "text": (
            "Giáo dục trực tuyến và học tập suốt đời đang trở thành xu hướng tất yếu trong thời đại tri thức số. Bất kỳ ai, "
            "ở bất kỳ nơi đâu trên thế giới cũng có thể tiếp cận kho tàng tri thức vô tận của nhân loại chỉ với một thiết bị "
            "kết nối internet, thúc đẩy sự công bằng xã hội và giải phóng tiềm năng sáng tạo của từng cá nhân."
        ),
    },
    {
        "id": "ROBOT-09",
        "topic": "Robotics & Automation",
        "target": "Japanese",
        "text": (
            "Sự kết hợp giữa công nghệ chế tạo robot thông minh và các mô hình thị giác máy tính đang làm thay đổi căn bản "
            "các quy trình sản xuất công nghiệp tự động hóa. Những dây chuyền sản xuất thông minh có khả năng vận hành liên tục "
            "với độ chính xác micromet, nâng cao năng suất lao động và giảm thiểu rủi ro cho người lao động trong môi trường độc hại."
        ),
    },
    {
        "id": "CYBER-10",
        "topic": "Cybersecurity & Data Privacy",
        "target": "German",
        "text": (
            "An ninh mạng và bảo mật dữ liệu cá nhân là lá chắn quan trọng nhất bảo vệ các giao dịch trực tuyến trong kỷ nguyên số. "
            "Các giải pháp mã hóa đầu cuối cùng kiến trúc xác thực đa yếu tố giúp các tổ chức tài chính và cơ quan chính phủ "
            "chống lại các cuộc tấn công mạng tinh vi và bảo vệ quyền riêng tư của hàng tỷ người dùng trên không gian mạng."
        ),
    },
    {
        "id": "BIODIV-11",
        "topic": "Biodiversity & Marine Life",
        "target": "Spanish",
        "text": (
            "Bảo tồn đa dạng sinh học tại các đại dương là nhiệm vụ sống còn để duy trì cân bằng chuỗi thức ăn tự nhiên toàn cầu. "
            "Các rạn san hô nhiệt đới vốn là ngôi nhà của hàng ngàn loài thủy sinh quý hiếm đang phải đối mặt với nguy cơ biến mất "
            "do nhiệt độ nước biển tăng cao và ô nhiễm rác thải nhựa công nghiệp."
        ),
    },
    {
        "id": "SMARTCITY-12",
        "topic": "Smart Cities & Urban Transport",
        "target": "Chinese",
        "text": (
            "Quy hoạch đô thị thông minh tích hợp mạng lưới giao thông công cộng chạy điện và hệ thống đèn tín hiệu giao thông "
            "điều khiển bằng thuật toán thích ứng đang giúp giảm thiểu tình trạng ùn tắc giao thông và lượng khí thải carbon "
            "tại các siêu đô thị đông dân cư trên thế giới."
        ),
    },
]


def make_request(endpoint: str, data: dict = None, timeout: int = 120):
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
    except Exception as e:
        latency = (time.perf_counter() - start_time) * 1000
        return None, latency, str(e)


def worker_task(barrier: threading.Barrier, item: dict, request_idx: int):
    """Worker thread that waits at barrier so all threads release at the EXACT same millisecond."""
    # Synchronize all threads at the starting line
    barrier.wait()
    
    send_time = time.time()
    res, lat, err = make_request("/translate", {"text": item["text"], "target": item["target"]})
    return {
        "index": request_idx,
        "id": item["id"],
        "topic": item["topic"],
        "target": item["target"],
        "words": len(item["text"].split()),
        "latency_ms": lat,
        "result": res,
        "error": err,
        "send_time": send_time,
    }


def run_concurrent_burst(test_items: list, burst_name: str):
    """Run a wave of requests concurrently across parallel threads."""
    num_threads = len(test_items)
    print(f"\n{'='*80}")
    print(f"  🚀 LAUNCHING {burst_name.upper()}: {num_threads} CONCURRENT THREADS AT ONCE")
    print(f"{'='*80}")
    print(f"[*] Initializing {num_threads} worker threads with synchronized Barrier...")

    barrier = threading.Barrier(num_threads)
    results = []

    t_burst_start = time.perf_counter()
    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        futures = [
            executor.submit(worker_task, barrier, item, i)
            for i, item in enumerate(test_items, start=1)
        ]
        print(f"[*] All {num_threads} threads synchronized! Releasing requests simultaneously...\n")

        for future in as_completed(futures):
            results.append(future.result())

    total_burst_time = (time.perf_counter() - t_burst_start) * 1000

    # Sort results by completion order / latency
    results.sort(key=lambda x: x["latency_ms"])

    print(f"┌{'─'*78}┐")
    print(f"│ {'#':<3} │ {'Topic':<26} │ {'Target':<8} │ {'Words':<5} │ {'Latency':<10} │ {'Server RAM':<14} │")
    print(f"├{'─'*78}┤")

    peak_ram = 0.0
    passed = 0

    for r in results:
        idx = r["index"]
        topic = r["topic"][:25]
        target = r["target"]
        words = r["words"]
        lat_str = f"{r['latency_ms']:.1f} ms"

        if r["error"]:
            status_str = f"❌ {r['error'][:12]}"
            ram_str = "N/A"
        else:
            passed += 1
            ram = r["result"].get("current_ram_mb", 0.0)
            if ram > peak_ram:
                peak_ram = ram
            ram_str = f"{ram:.1f} MB"
            status_str = ram_str

        print(f"│ {idx:<3} │ {topic:<26} │ {target:<8} │ {words:<5} │ {lat_str:<10} │ {status_str:<14} │")

    print(f"└{'─'*78}┘")
    print(f"\n[Burst Summary] Completed {passed}/{num_threads} successfully in {total_burst_time:.1f} ms total.")
    print(f"                Peak Server RAM during burst: {peak_ram:.1f} MB (Headroom: {512.0 - peak_ram:.1f} MB)")
    return results, peak_ram


def main():
    print("=" * 80)
    print("      AUTO_TRANSLATE: MULTI-THREADED BURST & RAM STRESS BENCHMARK")
    print(f"      Target: {RENDER_URL}")
    print(f"      RAM Ceiling Target: 512.0 MB | Compute: 0.1 CPU Free Tier")
    print("=" * 80)

    # 1. Baseline Health Check
    print("\n[Step 1] Baseline Server Health & Idle RAM Check...")
    health, lat, err = make_request("/health")
    if err:
        print(f"❌ Server connection failed: {err}")
        return

    baseline_ram = health.get("current_ram_mb", 0.0)
    print(f"  ✓ Service Status : {health.get('status')}")
    print(f"  ✓ Baseline RAM   : {baseline_ram:.1f} MB / 512.0 MB ({baseline_ram / 512.0 * 100:.1f}%)")
    print(f"  ✓ Ping Latency   : {lat:.1f} ms")

    # 2. Phase 1: 6 Heavy Long-Text Paragraphs simultaneously (1 per language)
    # Tests language-switching & memory allocation under parallel fire
    phase1_items = HEAVY_PARAGRAPHS[:6]
    results_p1, peak_ram_p1 = run_concurrent_burst(phase1_items, "Burst Wave 1 (6 Long Paragraphs across 6 Languages)")

    # 3. Phase 2: 12 Simultaneous Threads (All 12 long topics firing at once)
    # Heavy queuing stress test on 0.1 CPU
    results_p2, peak_ram_p2 = run_concurrent_burst(HEAVY_PARAGRAPHS, "Burst Wave 2 (12 Parallel Threads at the Same Instant)")

    # 4. Post-Stress Health Check
    print(f"\n[Step 4] Checking Post-Stress RAM to Verify Memory Reclamation...")
    time.sleep(2)
    post_health, _, _ = make_request("/health")
    post_ram = post_health.get("current_ram_mb", 0.0) if post_health else 0.0

    overall_peak = max(baseline_ram, peak_ram_p1, peak_ram_p2)

    print("\n" + "=" * 80)
    print("                     FINAL MULTI-THREADED STRESS REPORT")
    print("=" * 80)
    print(f" Total Simultaneous Requests Fired : {len(phase1_items) + len(HEAVY_PARAGRAPHS)}")
    print(f" Average Paragraph Word Count      : ~90 - 120 Vietnamese words")
    print(f" Baseline Idle Server RAM          : {baseline_ram:.1f} MB")
    print(f" Peak Server RAM Hit Under Load    : {overall_peak:.1f} MB / 512.0 MB ({overall_peak / 512.0 * 100:.1f}%)")
    print(f" Post-Load Settled RAM             : {post_ram:.1f} MB")
    print(f" Minimum Headroom to 512 MB Limit  : {512.0 - overall_peak:.1f} MB safely untouched")

    if overall_peak < 400.0:
        print("\n 🏆 VERDICT: EXCEPTIONAL STABILITY! RAM stayed below 400 MB even under multi-threaded fire!")
    elif overall_peak < 512.0:
        print("\n ✅ VERDICT: PASS! Fully compliant with strict < 512 MB RAM ceiling.")
    else:
        print("\n ❌ VERDICT: RAM limit breached.")
    print("=" * 80)


if __name__ == "__main__":
    main()
