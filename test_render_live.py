"""Stress & Long-Text Test Script for Live Render Service.

Tests:
1. Long multi-sentence paragraphs (AI, Tech, Culture, Business).
2. 15+ individual sequential requests across all supported languages.
3. Telemetry tracking: Latency, Success Rate, Server RAM stability.
"""

import json
import time
import urllib.request

RENDER_URL = "https://translation-temporary.onrender.com"

# Diverse collection of long paragraphs and individual sentences
TEST_SUITE = [
    # --- LONG PARAGRAPHS (Stress testing token buffers & neural compute) ---
    {
        "category": "Long Paragraph - Technology & AI",
        "target": "English",
        "text": (
            "Trí tuệ nhân tạo và học máy đang định hình lại phương thức con người tương tác với công nghệ. "
            "Từ các ứng dụng dịch thuật tự động cho đến hệ thống xe tự lái, chúng ta đang chứng kiến sự "
            "phát triển vượt bậc của các mô hình mạng nơ-ron hiện đại. Những công nghệ này không chỉ giúp "
            "tiết kiệm thời gian mà còn mở ra nhiều cơ hội đột phá cho tương lai của nhân loại."
        ),
    },
    {
        "category": "Long Paragraph - Work & Software Engineering",
        "target": "French",
        "text": (
            "Dự án mới của chúng tôi tại công ty công nghệ đang bước vào giai đoạn kiểm thử quan trọng. "
            "Toàn bộ đội ngũ kỹ sư đã làm việc chăm chỉ trong suốt những tháng qua để tối ưu hóa hiệu năng "
            "và giảm thiểu mức tiêu thụ tài nguyên máy chủ. Mọi người đều háo hức chờ đợi ngày sản phẩm chính thức ra mắt."
        ),
    },
    {
        "category": "Long Paragraph - Culture & Tourism",
        "target": "Japanese",
        "text": (
            "Việt Nam là một đất nước có bề dày lịch sử và văn hóa ẩm thực vô cùng phong phú, độc đáo. "
            "Du khách quốc tế khi đến đây luôn ấn tượng sâu sắc trước sự nồng hậu, thân thiện của người dân bản địa "
            "cùng với những danh lam thắng cảnh tuyệt đẹp trải dài khắp mọi miền đất nước."
        ),
    },
    {
        "category": "Long Paragraph - Business & Collaboration",
        "target": "German",
        "text": (
            "Chúng tôi rất trân trọng cơ hội hợp tác chiến lược cùng quý đối tác trong năm nay. "
            "Sự phối hợp chặt chẽ giữa hai bên đã giúp giải quyết rất nhiều thách thức phức tạp và đem lại "
            "kết quả tăng trưởng vượt ngoài kỳ vọng ban đầu. Hy vọng mối quan hệ này sẽ tiếp tục phát triển bền vững."
        ),
    },
    {
        "category": "Long Paragraph - Environment & Sustainability",
        "target": "Spanish",
        "text": (
            "Bảo vệ môi trường tự nhiên và chuyển dịch sang năng lượng tái tạo là mục tiêu cấp thiết của toàn cầu. "
            "Việc ứng dụng các giải pháp kỹ thuật tiên tiến vào quản lý tài nguyên sẽ góp phần duy trì một hệ sinh thái "
            "xanh, sạch và bền vững cho các thế hệ tương lai."
        ),
    },
    {
        "category": "Long Paragraph - Education & Lifelong Learning",
        "target": "Chinese",
        "text": (
            "Việc học tập một ngôn ngữ mới không chỉ mở mang tri thức mà còn kết nối những nền văn hóa khác nhau. "
            "Nhờ có sự đồng hành của các công nghệ dịch thuật thông minh, mọi rào cản giao tiếp đang dần được xóa nhòa."
        ),
    },

    # --- INDIVIDUAL DIVERSE REQUESTS (Sustained load & rapid language rotation) ---
    {"category": "Individual #1", "target": "English", "text": "Hôm nay là một ngày tuyệt vời để bắt đầu những dự định mới."},
    {"category": "Individual #2", "target": "English", "text": "Hệ thống máy chủ đang hoạt động rất ổn định với mức tiêu thụ RAM thấp."},
    {"category": "Individual #3", "target": "French",  "text": "Chúc mừng bạn đã hoàn thành xuất sắc nhiệm vụ được giao."},
    {"category": "Individual #4", "target": "French",  "text": "Tôi muốn đặt một tách cà phê sữa đá vào sáng sớm mai."},
    {"category": "Individual #5", "target": "Japanese","text": "Cảm ơn bạn đã luôn đồng hành và hỗ trợ chúng tôi trong suốt thời gian qua."},
    {"category": "Individual #6", "target": "Japanese","text": "Thời tiết mùa xuân ở Tokyo có hoa anh đào nở rất rực rỡ."},
    {"category": "Individual #7", "target": "Spanish", "text": "Hẹn gặp lại bạn vào buổi hội thảo công nghệ cuối tuần này nhé."},
    {"category": "Individual #8", "target": "Spanish", "text": "Chúng tôi cam kết mang lại dịch vụ tốt nhất cho mọi khách hàng."},
    {"category": "Individual #9", "target": "German",  "text": "Chúc bạn một ngày làm việc tràn đầy năng lượng và hiệu quả cao."},
    {"category": "Individual #10", "target": "German", "text": "Độ chính xác và độ tin cậy là ưu tiên hàng đầu của chúng tôi."},
    {"category": "Individual #11", "target": "Chinese", "text": "Hợp tác hữu nghị là nền tảng cho sự thành công lâu dài."},
    {"category": "Individual #12", "target": "English", "text": "Auto_Translate là giải pháp dịch thuật thông minh và tiết kiệm tài nguyên."},
]


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
        with urllib.request.urlopen(req, timeout=90) as response:
            latency = (time.perf_counter() - start_time) * 1000
            body = json.loads(response.read().decode("utf-8"))
            return body, latency, None
    except Exception as e:
        latency = (time.perf_counter() - start_time) * 1000
        return None, latency, str(e)


def main():
    print("=" * 75)
    print("   AUTO_TRANSLATE: LIVE RENDER STRESS & LONG-TEXT BENCHMARK")
    print(f"   Target URL: {RENDER_URL}")
    print("=" * 75)

    # 1. Baseline Health Check
    print("\n[Step 1] Checking Live Server Baseline...")
    health, lat, err = make_request("/health")
    if err:
        print(f"❌ Server connection failed: {err}")
        return

    baseline_ram = health.get("current_ram_mb", 0.0)
    print(f"  ✓ Status      : {health.get('status')}")
    print(f"  ✓ Baseline RAM: {baseline_ram} MB / 512.0 MB ({baseline_ram / 512.0 * 100:.1f}%)")
    print(f"  ✓ Ping Latency: {lat:.1f} ms\n")

    # 2. Run Test Suite
    print(f"[Step 2] Executing {len(TEST_SUITE)} Requests (Long Paragraphs & Individual Sentences)...\n")
    print("-" * 75)

    latencies = []
    peak_server_ram = baseline_ram
    passed_count = 0

    for i, item in enumerate(TEST_SUITE, start=1):
        cat = item["category"]
        target = item["target"]
        text = item["text"]

        word_count = len(text.split())
        print(f"[{i:02d}/{len(TEST_SUITE):02d}] {cat} ➔ {target} ({word_count} words)")
        print(f"     VI Text : \"{text[:75]}{'...' if len(text) > 75 else ''}\"")

        res, lat, err = make_request("/translate", {"text": text, "target": target})
        latencies.append(lat)

        if err:
            print(f"     ❌ FAILED: {err}")
        else:
            passed_count += 1
            translated = res.get("translated_text", "")
            server_ram = res.get("current_ram_mb", 0.0)
            if server_ram > peak_server_ram:
                peak_server_ram = server_ram

            print(f"     Output  : \"{translated[:80]}{'...' if len(translated) > 80 else ''}\"")
            print(f"     Latency : {lat:.1f} ms | Server RAM: {server_ram} MB (Headroom: {512.0 - server_ram:.1f} MB)")

        print("-" * 75)

    # 3. Final Summary Report
    avg_lat = sum(latencies) / len(latencies) if latencies else 0.0
    min_lat = min(latencies) if latencies else 0.0
    max_lat = max(latencies) if latencies else 0.0

    print("\n" + "=" * 75)
    print("                      BENCHMARK SUMMARY RESULTS")
    print("=" * 75)
    print(f" Total Requests Sent  : {len(TEST_SUITE)}")
    print(f" Successful Requests  : {passed_count}/{len(TEST_SUITE)} ({passed_count / len(TEST_SUITE) * 100:.1f}%)")
    print(f" Latency Min / Avg / Max : {min_lat:.1f} ms / {avg_lat:.1f} ms / {max_lat:.1f} ms")
    print(f" Peak Server RAM Hit  : {peak_server_ram:.1f} MB / 512.0 MB ({peak_server_ram / 512.0 * 100:.1f}%)")
    print(f" Minimum RAM Headroom : {512.0 - peak_server_ram:.1f} MB safely available")
    
    if passed_count == len(TEST_SUITE) and peak_server_ram < 512.0:
        print("\n 🏆 VERDICT: PERFECT STABILITY! All long paragraphs & requests completed under 512 MB.")
    else:
        print("\n ⚠️ VERDICT: Some requests failed or RAM peaked close to limit.")
    print("=" * 75)


if __name__ == "__main__":
    main()
