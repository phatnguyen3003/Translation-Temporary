"""User-friendly Translation & RAM Memory Test Runner.

Easily edit the TEST_CASES list below and run:
    python run_tests.py

To run each test in a completely isolated process (measures standalone RAM):
    python run_tests.py --isolated
"""

import os
import sys
import time
import argparse
import subprocess
import psutil
from typing import List, Tuple

# ==============================================================================
# --- EDIT YOUR TEST CASES HERE ---
# Format: ("Vietnamese Text", "Target Language")
# Supported languages: English, French, German, Spanish, Chinese, Japanese
# ==============================================================================
from typing import List, Tuple

from typing import List, Tuple

TEST_CASES: List[Tuple[str, str]] = [
    (
        "Xin chào, rất vui được gặp bạn hôm nay. Dạo này công việc và cuộc sống của bạn thế nào rồi? "
        "Tôi nghe nói bạn vừa chuyển sang một dự án mới rất thú vị ở công ty công nghệ. "
        "Hy vọng mọi thứ đều diễn ra suôn sẻ và bạn vẫn giữ gìn sức khỏe thật tốt. "
        "Thời gian trôi qua nhanh thật, mới đó mà đã gần nửa năm kể từ lần cuối chúng ta trò chuyện trực tiếp. "
        "Hôm trước tôi có gặp lại vài người bạn cũ thời đại học và mọi người đều nhắc đến bạn rất nhiều. "
        "Ai cũng ngưỡng mộ tinh thần làm việc chăm chỉ và sự nhiệt huyết của bạn trong mọi việc. "
        "Dạo gần đây tôi cũng đang bận rộn hoàn thiện một số kế hoạch cá nhân nên ít có dịp ra ngoài tụ tập. "
        "Tuy nhiên, tôi luôn cố gắng cân bằng giữa công việc và cuộc sống để không bị quá tải. "
        "Việc dành thời gian cho bản thân và những người thân yêu thực sự rất quan trọng sau những giờ làm việc căng thẳng. "
        "Cuối tuần này nếu bạn có thời gian rảnh, chúng ta hãy cùng hẹn nhau đi uống cà phê ở quán quen nhé. "
        "Tôi rất muốn được nghe bạn chia sẻ thêm về những trải nghiệm và định hướng sắp tới của bạn. "
        "Hãy nhắn lại cho tôi biết lịch trình của bạn để chúng ta sắp xếp một buổi gặp mặt thật trọn vẹn.",
        "English"
    ),
    (
        "Hôm nay thời tiết ở thành phố thật sự rất dễ chịu với bầu trời trong xanh và ánh nắng nhẹ nhàng. "
        "Những cơn gió mùa thu thổi qua làm cho không khí trở nên mát mẻ hơn hẳn sau nhiều ngày oi bức. "
        "Từ sáng sớm, từng tia nắng ấm áp đã len lỏi qua những tán cây xanh dọc theo các con phố lớn. "
        "Đây là thời điểm lý tưởng để đi dạo trong công viên hoặc ngồi đọc sách bên ban công yên tĩnh. "
        "Nhiều người dân địa phương cũng tranh thủ ra ngoài từ sớm để tập thể dục và tận hưởng khung cảnh tuyệt đẹp này. "
        "Các quán cà phê vỉa hè trở nên nhộn nhịp hơn khi ai cũng muốn tìm một góc nhỏ ngắm nhìn phố phường. "
        "Không khí trong lành giúp tinh thần của mọi người trở nên phấn chấn và tràn đầy năng lượng tích cực. "
        "Những hàng cây bắt đầu chuyển màu lá nhẹ, tạo nên một bức tranh thiên nhiên vô cùng lãng mạn và bình yên. "
        "Vào buổi chiều, nhiệt độ giảm nhẹ khiến việc di chuyển ngoài trời càng thêm phần thoải mái và thư thái. "
        "Dự báo thời tiết cho biết trạng thái dễ chịu này sẽ còn kéo dài đến hết tuần trước khi có đợt không khí lạnh mới. "
        "Những ngày đẹp trời như thế này luôn mang lại cảm giác nhẹ nhõm sau nhịp sống hối hả thường nhật. "
        "Nếu có cơ hội, bạn hãy tạm gác lại màn hình máy tính một lát để bước ra ngoài hít thở bầu không khí tuyệt vời này.",
        "French"
    ),
    (
        "Tôi đang tập trung học lập trình Python để phát triển các ứng dụng trí tuệ nhân tạo và xử lý dữ liệu lớn. "
        "Ngôn ngữ này có cú pháp rất rõ ràng, dễ đọc và sở hữu một hệ sinh thái thư viện mã nguồn mở vô cùng phong phú. "
        "Mỗi ngày tôi đều dành ra ít nhất hai tiếng để luyện tập giải thuật và xây dựng các dự án nhỏ mang tính thực tế. "
        "Ban đầu việc làm quen với các khái niệm bất đồng bộ, quản lý bộ nhớ và tối ưu hiệu năng có chút khó khăn. "
        "Tuy nhiên, càng tìm hiểu sâu thì tôi càng thấy việc lập trình trở nên hấp dẫn, logic và hữu ích hơn rất nhiều. "
        "Tôi thường xuyên đọc tài liệu chính thức và tham gia các diễn đàn công nghệ để học hỏi kinh nghiệm từ cộng đồng. "
        "Việc tự tay viết ra các công cụ tự động hóa giúp tôi tiết kiệm được hàng giờ đồng hồ cho những tác vụ lặp đi lặp lại. "
        "Ngoài ra, tôi cũng đang nghiên cứu cách triển khai các mô hình học máy gọn nhẹ để chạy mượt mà trên thiết bị cá nhân. "
        "Kiểm thử phần mềm và viết mã sạch là hai kỹ năng quan trọng mà tôi luôn cố gắng rèn luyện trong từng dòng code. "
        "Mỗi khi khắc phục được một lỗi phức tạp, tôi lại cảm thấy tự tin hơn vào khả năng giải quyết vấn đề của mình. "
        "Trong tương lai gần, tôi dự định sẽ đóng góp mã nguồn cho một vài dự án cộng đồng để nâng cao trình độ chuyên môn. "
        "Hành trình chinh phục công nghệ chắc chắn còn dài, nhưng sự kiên trì mỗi ngày sẽ tạo nên nền tảng vững chắc.",
        "German"
    ),
    (
        "Chúc bạn có một ngày làm việc mới tràn đầy năng lượng, niềm vui và đạt được nhiều kết quả thật tốt đẹp. "
        "Đừng quên dành chút thời gian nghỉ ngơi ngắn giữa giờ để đôi mắt và tinh thần luôn được thư giãn. "
        "Một ly nước ấm hoặc vài động tác vươn vai nhẹ nhàng sẽ giúp cơ thể bạn duy trì sự tỉnh táo suốt buổi sáng. "
        "Nếu gặp phải bất kỳ khó khăn nào trong quá trình xử lý công việc, hãy cứ bình tĩnh phân tích và giải quyết từng bước một. "
        "Sự kiên nhẫn, tỉ mỉ và tập trung cao độ chắc chắn sẽ giúp bạn vượt qua mọi thử thách một cách dễ dàng. "
        "Đừng ngần ngại trao đổi với đồng nghiệp khi cần thêm góc nhìn mới, vì tinh thần hợp tác luôn tạo ra sức mạnh tập thể. "
        "Mỗi nhiệm vụ hoàn thành hôm nay đều là một bước tiến quan trọng giúp bạn tiến gần hơn tới mục tiêu lớn của mình. "
        "Hãy luôn giữ vững thái độ lạc quan và tin tưởng vào năng lực cũng như kinh nghiệm mà bạn đã tích lũy được. "
        "Khi bước vào giờ nghỉ trưa, bạn nên thưởng thức một bữa ăn đầy đủ dinh dưỡng để nạp lại năng lượng cho buổi chiều. "
        "Buổi chiều thường trôi qua rất nhanh, vì vậy việc sắp xếp thứ tự ưu tiên cho các đầu việc sẽ giúp bạn chủ động hơn. "
        "Hy vọng đến cuối ngày bạn sẽ hoàn thành xuất sắc tất cả các kế hoạch đã đề ra với tâm trạng thật hài lòng. "
        "Chúc mọi điều may mắn và thuận lợi nhất sẽ luôn đồng hành cùng bạn trong suốt ngày hôm nay.",
        "Spanish"
    ),
    (
        "Cảm ơn bạn rất nhiều vì đã luôn nhiệt tình hỗ trợ, lắng nghe và đồng hành cùng tôi trong suốt thời gian qua. "
        "Nếu không có những lời khuyên chân thành và sự giúp đỡ kịp thời của bạn, chắc chắn tôi đã gặp rất nhiều trở ngại. "
        "Tôi thực sự trân trọng khoảng thời gian mà hai chúng ta đã cùng nhau nỗ lực hết mình để hoàn thành nhiệm vụ chung. "
        "Sự tận tâm, chuyên nghiệp và tinh thần trách nhiệm của bạn là nguồn động lực lớn giúp tôi cố gắng hơn mỗi ngày. "
        "Trong những lúc áp lực nhất, sự bình tĩnh và lạc quan của bạn đã giúp cả nhóm giữ vững tinh thần để đi đến đích. "
        "Tôi đã học hỏi được rất nhiều kỹ năng quý giá từ cách bạn tổ chức công việc và xử lý các tình huống phát sinh. "
        "Một người đồng hành đáng tin cậy như bạn thực sự là điều may mắn mà không phải ai cũng dễ dàng có được. "
        "Tôi luôn ghi nhớ những đóng góp thầm lặng nhưng vô cùng quan trọng mà bạn đã dành cho dự án lần này. "
        "Sự thành công của kết quả ngày hôm nay mang đậm dấu ấn từ sự phối hợp ăn ý giữa tất cả chúng ta. "
        "Mong rằng trong tương lai chúng ta sẽ còn nhiều cơ hội để tiếp tục hợp tác, học hỏi và chia sẻ cùng nhau. "
        "Nếu có bất cứ việc gì cần đến sự hỗ trợ từ phía tôi, bạn đừng ngần ngại liên hệ bất cứ lúc nào nhé. "
        "Một lần nữa xin gửi tới bạn lời cảm ơn sâu sắc nhất cùng lời chúc sức khỏe và thành công rực rỡ.",
        "Chinese"
    ),
    (
        "Tôi có một niềm đam mê đặc biệt với việc đi du lịch và khám phá những nền văn hóa mới lạ trên khắp thế giới. "
        "Mỗi vùng đất đi qua đều mang lại cho tôi những trải nghiệm quý giá về ẩm thực, lịch sử và con người bản địa. "
        "Tôi thường thích tự lên lịch trình chi tiết và tìm đến những địa điểm ít người biết để cảm nhận trọn vẹn nhịp sống địa phương. "
        "Việc thưởng thức các món ăn truyền thống tại những khu chợ địa phương luôn là phần thú vị nhất trong mỗi hành trình của tôi. "
        "Qua những cuộc trò chuyện ngắn với người dân bản xứ, tôi hiểu thêm nhiều câu chuyện văn hóa mà sách báo ít khi nhắc tới. "
        "Những bức ảnh, tấm vé tàu và các món quà lưu niệm nhỏ thu thập được sau mỗi chuyến đi luôn là kỷ niệm vô giá. "
        "Du lịch không chỉ giúp tôi mở mang tầm mắt mà còn dạy tôi cách thích nghi linh hoạt trước mọi thay đổi bất ngờ. "
        "Có những chuyến đi gặp thời tiết không thuận lợi, nhưng chính điều đó lại tạo nên những ký ức khó quên nhất. "
        "Mỗi lần trở về từ một hành trình dài, tôi lại cảm thấy tâm hồn mình được làm mới và có thêm nhiều cảm hứng sáng tạo. "
        "Tôi cũng thường viết lại nhật ký hành trình để lưu giữ cảm xúc và chia sẻ kinh nghiệm thực tế cho những người cùng sở thích. "
        "Trong năm tới, mục tiêu lớn nhất của tôi là có thể đặt chân đến ít nhất ba quốc gia mới ở cả châu Á và châu Âu. "
        "Thế giới rộng lớn ngoài kia luôn ẩn chứa vô vàn điều kỳ diệu đang chờ đợi những bước chân khám phá không ngừng nghỉ.",
        "Japanese"
    ),
]

# Hard limit budget (Megabytes)
RAM_LIMIT_MB = 512.0


def get_current_ram_mb() -> float:
    """Return resident set size (RSS) memory in Megabytes."""
    return psutil.Process(os.getpid()).memory_info().rss / (1024 * 1024)


def run_single_test_isolated(text: str, target: str, index: int, total: int) -> bool:
    """Run an individual test in a separate, isolated subprocess to measure pure standalone RAM."""
    code = f"""
import time, os, psutil
from src.auto_translate.translator import Translator

def ram(): return psutil.Process(os.getpid()).memory_info().rss / (1024 * 1024)

base_ram = ram()
start_t = time.perf_counter()
t = Translator()
output = t.translate({repr(text)}, {repr(target)})
latency = (time.perf_counter() - start_t) * 1000
peak_ram = ram()

print(f"OUTPUT:{{output}}")
print(f"LATENCY:{{latency:.1f}}")
print(f"BASE_RAM:{{base_ram:.1f}}")
print(f"PEAK_RAM:{{peak_ram:.1f}}")
"""
    result = subprocess.run(
        [sys.executable, "-c", code],
        capture_output=True,
        text=True,
        encoding="utf-8",
        cwd=os.path.dirname(os.path.abspath(__file__)),
    )

    if result.returncode != 0:
        print(f"\n❌ [TEST {index}/{total}] VI -> {target} FAILED TO EXECUTE:")
        print(result.stderr)
        return False

    data = {}
    for line in result.stdout.splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            data[k.strip()] = v.strip()

    output = data.get("OUTPUT", "")
    latency = float(data.get("LATENCY", 0.0))
    peak_ram = float(data.get("PEAK_RAM", 0.0))
    headroom = RAM_LIMIT_MB - peak_ram
    passed = peak_ram < RAM_LIMIT_MB

    status_icon = "✅ PASS" if passed else "❌ FAILED (EXCEEDED 512MB)"

    print(f"\n┌── [TEST {index}/{total}] Vietnamese ➔ {target} (Isolated Process)")
    print(f"│ Input   : {text}")
    print(f"│ Output  : {output}")
    print(f"│ Latency : {latency:.1f} ms")
    print(f"│ Peak RAM: {peak_ram:.1f} MB  (Headroom: {headroom:.1f} MB remaining)")
    print(f"│ Status  : {status_icon}")
    print("└─────────────────────────────────────────────────────────────────")
    return passed


def run_sequential_tests():
    """Run tests sequentially in the current process, tracking cumulative memory."""
    print("=================================================================")
    print("        AUTO_TRANSLATE: MEMORY & ACCURACY TEST RUNNER           ")
    print(f"        RAM Budget Ceiling: {RAM_LIMIT_MB:.0f} MB               ")
    print("=================================================================")

    start_ram = get_current_ram_mb()
    print(f"[*] Starting process base RAM: {start_ram:.1f} MB")
    print("[*] Initializing translator engine...")

    from src.auto_translate.translator import Translator
    translator = Translator()

    loaded_ram = get_current_ram_mb()
    print(f"[*] Base VI->EN Model loaded. Current RAM: {loaded_ram:.1f} MB")
    print(f"[*] Total test cases to run: {len(TEST_CASES)}\n")

    passed_count = 0
    max_peak_ram = loaded_ram

    for i, (vietnamese_text, target_lang) in enumerate(TEST_CASES, start=1):
        ram_before = get_current_ram_mb()
        t_start = time.perf_counter()

        translated = translator.translate(vietnamese_text, target_lang)
        latency_ms = (time.perf_counter() - t_start) * 1000

        ram_after = get_current_ram_mb()
        if ram_after > max_peak_ram:
            max_peak_ram = ram_after

        headroom = RAM_LIMIT_MB - ram_after
        passed = ram_after < RAM_LIMIT_MB
        if passed:
            passed_count += 1

        status_tag = "✅ PASS" if passed else "❌ FAIL (>512MB)"

        print(f"┌── [TEST {i}/{len(TEST_CASES)}] VI ➔ {target_lang}")
        print(f"│ Input      : {vietnamese_text}")
        print(f"│ Output     : {translated}")
        print(f"│ Latency    : {latency_ms:.1f} ms")
        print(f"│ Current RAM: {ram_after:.1f} MB  (Δ {ram_after - ram_before:+.1f} MB, {headroom:.1f} MB free)")
        print(f"│ Status     : {status_tag}")
        print("└─────────────────────────────────────────────────────────────\n")

    print("======================= SUMMARY RESULTS =======================")
    print(f"Tests Passed : {passed_count}/{len(TEST_CASES)}")
    print(f"Max Peak RAM : {max_peak_ram:.1f} MB / {RAM_LIMIT_MB:.0f} MB")
    print(f"RAM Headroom : {RAM_LIMIT_MB - max_peak_ram:.1f} MB")
    if max_peak_ram < RAM_LIMIT_MB:
        print("Final Verdict: 🏆 STRICTLY COMPLIANT WITH < 512 MB RAM REQUIREMENT!")
    else:
        print("Final Verdict: ⚠️ EXCEEDED 512 MB LIMIT!")
    print("===============================================================\n")


def main():
    parser = argparse.ArgumentParser(description="Auto_Translate User Test Runner")
    parser.add_argument(
        "--isolated",
        action="store_true",
        help="Run each test in a fresh, isolated Python subprocess (measures standalone RAM per pair)",
    )
    args = parser.parse_args()

    if args.isolated:
        print("=================================================================")
        print("    AUTO_TRANSLATE: ISOLATED PROCESS TEST RUNNER                 ")
        print("    (Each test runs in a fresh sub-process for standalone RAM)   ")
        print("=================================================================")
        all_passed = True
        for i, (text, target) in enumerate(TEST_CASES, start=1):
            ok = run_single_test_isolated(text, target, i, len(TEST_CASES))
            if not ok:
                all_passed = False

        print("\n======================= SUMMARY RESULTS =======================")
        print(f"Overall Result: {'✅ ALL TESTS PASSED' if all_passed else '❌ SOME TESTS FAILED'}")
        print("===============================================================\n")
    else:
        run_sequential_tests()


if __name__ == "__main__":
    main()
