"""Sinh trang bai tap nhap mon C++, nhom theo chuong."""
import argparse, html, json, os

CHAPTERS = ["Basics", "Conditionals", "Loops", "Arrays",
            "Matrices", "Strings", "Recursion"]

CHAPTER_VI = {
    "Basics": "Input, Output and Expressions",
    "Conditionals": "Conditional Statements",
    "Loops": "Loops",
    "Arrays": "One-dimensional Arrays",
    "Matrices": "Two-dimensional Arrays",
    "Strings": "Strings",
    "Recursion": "Recursion",
}

HEAD = """{% extends "base.html" %}

{% block body %}
  <p>Exercises for students starting with C++. Short statements, one concept
  each, ordered the way an introductory programming course is taught. Every
  problem is judged here on DUT OJ.</p>
"""

TAIL = """{% endblock %}
"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default=os.path.expanduser("~/dutoj/data_intro.json"))
    ap.add_argument("--out",
                    default=os.path.expanduser("~/dutoj/templates/practice/basics.html"))
    args = ap.parse_args()

    items = json.load(open(args.data, encoding="utf-8"))
    parts = [HEAD]
    index = 1

    for ch in CHAPTERS:
        group = [x for x in items if x.get("chapter") == ch]
        group.sort(key=lambda x: x["code"])
        if not group:
            continue

        parts.append('\n  <h3>%s (%d)</h3>\n  <ol start="%d">\n'
                     % (html.escape(CHAPTER_VI[ch]), len(group), index))
        for x in group:
            parts.append('    <li><a href="/problem/%s">%s</a></li>\n'
                         % (x["code"], html.escape(x["name"])))
            index += 1
        parts.append("  </ol>\n")
        print("%-22s %2d bai" % (CHAPTER_VI[ch], len(group)))

    parts.append(TAIL)
    open(args.out, "w", encoding="utf-8").write("".join(parts))
    print("\nTong: %d bai -> %s" % (index - 1, args.out))


if __name__ == "__main__":
    main()
