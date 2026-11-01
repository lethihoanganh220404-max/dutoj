"""Sinh trang lo trinh luyen tap tu data.json.

Moi muc chia thanh nhieu bac rating, moi bac lay mot so bai nhat dinh,
nen bai trong muc di tu de den kho. Ghi de templates/practice/index.html.
"""
import argparse, html, json, os

# (tieu de muc, chu de, [(rating, so bai lay o bac do), ...])
SECTIONS = [
    ("Introductory Problems", "Implementation",
     [(800, 5), (900, 5), (1000, 5), (1100, 5), (1200, 5)]),
    ("Sorting and Searching", "Sorting & Searching",
     [(800, 4), (1000, 6), (1200, 6), (1400, 7), (1600, 7)]),
    ("Dynamic Programming", "Dynamic Programming",
     [(1200, 6), (1300, 4), (1400, 6), (1500, 4), (1600, 5), (1800, 2)]),
    ("Graph Algorithms", "Graph Theory",
     [(1000, 4), (1200, 4), (1300, 4), (1400, 5), (1500, 4), (1600, 4)]),
]

HEAD = """{% extends "base.html" %}

{% block body %}
  <p>A guided practice track built from problems hosted on DUT OJ. Each
  section is ordered from easier to harder. Click a problem to read the
  statement and submit your solution — submissions are judged here.</p>
"""

TAIL = """{% endblock %}
"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default=os.path.expanduser("~/dutoj/data.json"))
    ap.add_argument("--out",
                    default=os.path.expanduser("~/dutoj/templates/practice/index.html"))
    args = ap.parse_args()

    with open(args.data, encoding="utf-8") as f:
        items = json.load(f)

    used_codes = set()
    used_names = set()
    parts = [HEAD]
    index = 1

    for title, topic, tiers in SECTIONS:
        chosen = []
        for rating, want in tiers:
            pool = [it for it in items
                    if topic in it.get("types", [])
                    and it["cf_rating"] == rating
                    and it["code"] not in used_codes
                    and it["name"].lower() not in used_names]
            pool.sort(key=lambda it: it["code"])
            for it in pool[:want]:
                used_codes.add(it["code"])
                used_names.add(it["name"].lower())
                chosen.append(it)

        if not chosen:
            print("CANH BAO: muc '%s' khong tim duoc bai nao" % title)
            continue

        parts.append('\n  <h3>%s (%d)</h3>\n  <ol start="%d">\n'
                     % (html.escape(title), len(chosen), index))
        for it in chosen:
            parts.append(
                '    <li><a href="/problem/%s">%s</a> '
                '<span style="color:#888">(%s)</span></li>\n'
                % (it["code"], html.escape(it["name"]), it["cf_rating"]))
            index += 1
        parts.append("  </ol>\n")

        print("%-24s %3d bai  rating %d-%d"
              % (title, len(chosen), chosen[0]["cf_rating"], chosen[-1]["cf_rating"]))

    parts.append(TAIL)

    with open(args.out, "w", encoding="utf-8") as f:
        f.write("".join(parts))

    print("\nTong: %d bai -> %s" % (index - 1, args.out))


if __name__ == "__main__":
    main()
