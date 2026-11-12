# -*- coding: utf-8 -*-
"""BKOJ: trang "Lộ trình luyện tập" dạng thẻ, song ngữ Việt / Anh, có tiến độ theo từng sinh viên."""
from django.shortcuts import render

from judge.models import Problem, ProblemType, Submission

UI = {
    "vi": {
        "page_title": "Lộ trình luyện tập lập trình",
        "page_sub": "{total} chủ đề chia thành 3 giai đoạn, sắp theo thứ tự nên học. Trong mỗi chủ đề, hãy bắt đầu từ bài "
                    "100 điểm (dễ) rồi tăng dần lên 400 điểm (khó).",
        "login_link": "Đăng nhập", "login_rest": "để theo dõi tiến độ của bạn.",
        "all": "Tất cả", "part": "Phần", "topics_count": "chủ đề", "topic": "Chủ đề",
        "problems": "bài tập", "go": "Học ngay →", "search": "Tìm kiếm bài học...",
        "empty": "Không tìm thấy chủ đề phù hợp.",
    },
    "en": {
        "page_title": "Programming practice roadmap",
        "page_sub": "{total} topics in 3 stages, ordered the way you should learn them. In each topic, start with the "
                    "100-point problems (easy) and work up to the 400-point ones (hard).",
        "login_link": "Log in", "login_rest": "to track your progress.",
        "all": "All", "part": "Part", "topics_count": "topics", "topic": "Topic",
        "problems": "problems", "go": "Start →", "search": "Search topics...",
        "empty": "No matching topics found.",
    },
}

# (mã, biểu tượng, {ngôn ngữ: (nhãn tab, tên giai đoạn)}, [(mã chủ đề, {ngôn ngữ: kiến thức chính})])
STAGES = [
    ("gd1", "🧱", {"vi": ("Giai đoạn 1", "Nền tảng"), "en": ("Stage 1", "Foundations")}, [
        ("coban", {"vi": "Nhập xuất, rẽ nhánh, vòng lặp", "en": "Input/output, conditions, loops"}),
        ("sohoc", {"vi": "Ước, bội, số nguyên tố, đồng dư, lũy thừa nhanh",
                   "en": "Divisors, multiples, primes, modular arithmetic, fast exponentiation"}),
        ("mang", {"vi": "Duyệt mảng, ma trận, tổng tiền tố", "en": "Array traversal, matrices, prefix sums"}),
        ("xau", {"vi": "Xử lý chuỗi, chuẩn hóa, so khớp mẫu", "en": "String processing, normalization, pattern matching"}),
        ("sapxep", {"vi": "Sắp xếp, so sánh theo nhiều tiêu chí", "en": "Sorting, multi-key comparison"}),
    ]),
    ("gd2", "🧩", {"vi": ("Giai đoạn 2", "Kỹ thuật và cấu trúc dữ liệu"), "en": ("Stage 2", "Techniques and data structures")}, [
        ("chatnhiphan", {"vi": "Tìm kiếm nhị phân trên mảng và trên kết quả", "en": "Binary search on arrays and on the answer"}),
        ("haicontro", {"vi": "Hai con trỏ, cửa sổ trượt", "en": "Two pointers, sliding window"}),
        ("ctdl", {"vi": "Ngăn xếp, hàng đợi, heap, bảng băm", "en": "Stacks, queues, heaps, hash tables"}),
        ("tohop", {"vi": "Hoán vị, tổ hợp, nguyên lý bù trừ, số Catalan",
                   "en": "Permutations, combinations, inclusion-exclusion, Catalan numbers"}),
        ("thamlam", {"vi": "Lựa chọn tham lam và cách chứng minh", "en": "Greedy choices and how to prove them"}),
    ]),
    ("gd3", "🚀", {"vi": ("Giai đoạn 3", "Thuật toán nâng cao"), "en": ("Stage 3", "Advanced algorithms")}, [
        ("quaylui", {"vi": "Vét cạn, quay lui, nhánh cận", "en": "Brute force, backtracking, branch and bound"}),
        ("qhd", {"vi": "Cái túi, dãy con tăng, xâu con chung, QHĐ trạng thái",
                 "en": "Knapsack, LIS, LCS, bitmask DP"}),
        ("cayphandoan", {"vi": "Fenwick, cây phân đoạn, cập nhật lười", "en": "Fenwick trees, segment trees, lazy propagation"}),
        ("dothi", {"vi": "BFS, DFS, liên thông, sắp xếp tô-pô, cầu và khớp",
                   "en": "BFS, DFS, connectivity, topological sort, bridges and articulation points"}),
        ("duongdi", {"vi": "Dijkstra, Floyd, Bellman-Ford", "en": "Dijkstra, Floyd, Bellman-Ford"}),
        ("cay", {"vi": "Duyệt cây, tổ tiên chung gần nhất, đường kính", "en": "Tree traversal, lowest common ancestor, diameter"}),
        ("luong", {"vi": "Luồng cực đại, cặp ghép", "en": "Maximum flow, matching"}),
    ]),
]

TOPIC_EN = {
    "coban": "Basics", "sohoc": "Number theory", "mang": "Arrays & prefix sums", "xau": "Strings", "sapxep": "Sorting",
    "chatnhiphan": "Binary search", "haicontro": "Two pointers & sliding window", "ctdl": "Stacks, queues, heaps, hashing",
    "tohop": "Combinatorics", "thamlam": "Greedy", "quaylui": "Backtracking & branch and bound", "qhd": "Dynamic programming",
    "cayphandoan": "Segment trees & Fenwick trees", "dothi": "Graphs", "duongdi": "Shortest paths", "cay": "Trees",
    "luong": "Flows & matching",
}


def get_lang(request):
    code = (getattr(request, "LANGUAGE_CODE", "") or "vi").lower()
    return "en" if code.startswith("en") else "vi"


def build_stages(types, by_type, solved, lang="vi"):
    stages, num = [], 0
    for key, icon, names, topics in STAGES:
        short, name = names[lang]
        cards = []
        for code, desc in topics:
            t = types.get(code)
            if t is None:
                continue
            num += 1
            ids = by_type.get(t.id, set())
            done = len(ids & solved)
            cards.append({
                "num": num, "name": TOPIC_EN.get(code, t.full_name) if lang == "en" else t.full_name,
                "desc": desc[lang], "count": len(ids), "done": done,
                "pct": round(100 * done / len(ids)) if ids else 0,
                "url": "/problems/?type=%d" % t.id,
            })
        stages.append({"key": key, "short": short, "icon": icon, "cards": cards,
                       "title": "%s %d: %s" % (UI[lang]["part"], len(stages) + 1, name)})
    return stages, num


def chu_de(request):
    lang = get_lang(request)
    types = {t.name: t for t in ProblemType.objects.all()}
    by_type = {}
    pairs = Problem.types.through.objects.filter(problem__is_public=True) \
        .values_list("problemtype_id", "problem_id")
    for tid, pid in pairs:
        by_type.setdefault(tid, set()).add(pid)

    solved = set()
    if request.user.is_authenticated:
        profile = getattr(request, "profile", None) or request.user.profile
        solved = set(Submission.objects.filter(user=profile, result="AC")
                     .values_list("problem_id", flat=True))

    stages, total = build_stages(types, by_type, solved, lang)
    t = dict(UI[lang])
    t["page_sub"] = t["page_sub"].format(total=total)
    return render(request, "chude/index.html", {
        "title": t["page_title"], "t": t, "stages": stages, "total": total,
        "logged_in": request.user.is_authenticated,
    })

# BKOJ: tên chủ đề tiếng Anh mới
TOPIC_EN.update({
    "coban": "Programming basics",
    "sohoc": "Number theory",
    "mang": "Arrays",
    "xau": "Strings",
    "sapxep": "Sorting",
    "chatnhiphan": "Binary search",
    "haicontro": "Two pointers",
    "ctdl": "Data structures",
    "tohop": "Combinatorics",
    "thamlam": "Greedy algorithms",
    "quaylui": "Backtracking",
    "qhd": "Dynamic programming",
    "cayphandoan": "Range queries",
    "dothi": "Graphs",
    "duongdi": "Shortest paths",
    "cay": "Trees",
    "luong": "Flows and matching",
})
