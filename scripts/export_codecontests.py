import argparse, json, os, re, shutil
from collections import Counter
from datasets import load_dataset

SKIP_COLUMNS = ["solutions", "incorrect_solutions", "generated_tests",
                "untranslated_description"]
MAX_BYTES_PER_PROBLEM = 5 * 1024 * 1024
BAD_TAGS = {"*special", "interactive"}

TAG_MAP = {
    "implementation": "Implementation",
    "greedy": "Greedy",
    "math": "Math",
    "number theory": "Math",
    "dp": "Dynamic Programming",
    "brute force": "Brute Force",
    "data structures": "Data Structures",
    "dsu": "Data Structures",
    "graphs": "Graph Theory",
    "dfs and similar": "Graph Theory",
    "shortest paths": "Graph Theory",
    "trees": "Graph Theory",
    "sortings": "Sorting & Searching",
    "two pointers": "Sorting & Searching",
    "binary search": "Sorting & Searching",
    "strings": "Strings",
    "string suffix structures": "Strings",
    "combinatorics": "Combinatorics",
    "probabilities": "Combinatorics",
    "bitmasks": "Bitmask",
    "geometry": "Geometry",
    "constructive algorithms": "Constructive",
    "games": "Game Theory",
    "divide and conquer": "Divide & Conquer",
}

# (ten nhom, rating tu, rating den, so bai toi da)
LEVELS = [
    ("easy",   800, 1200, 400),
    ("medium", 1300, 1700, 400),
    ("hard",   1800, 2200, 200),
]


def level_of(rating):
    for name, lo, hi, quota in LEVELS:
        if lo <= rating <= hi:
            return name, quota
    return None, 0


def types_of(tags):
    out = []
    for t in tags:
        m = TAG_MAP.get(t)
        if m and m not in out:
            out.append(m)
    return out[:3] or ["Uncategorized"]


def clean_name(s):
    s = re.sub(r"^\d+_[A-Z]\d*\.\s*", "", s).strip()
    return (s or "Untitled")[:100]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.expanduser("~/dutoj-data/out"))
    ap.add_argument("--n", type=int, default=1000)
    ap.add_argument("--max-tests", type=int, default=20)
    args = ap.parse_args()

    shutil.rmtree(args.out, ignore_errors=True)
    os.makedirs(f"{args.out}/problems", exist_ok=True)

    ds = load_dataset("deepmind/code_contests", split="train", streaming=True)
    ds = ds.remove_columns(SKIP_COLUMNS)

    items = []
    filled = Counter()
    skip = Counter()
    n_seen = 0

    for i, r in enumerate(ds):
        if len(items) >= args.n:
            break
        n_seen += 1

        level, quota = level_of(r["cf_rating"])
        if level is None:
            skip["rating"] += 1
            continue
        if filled[level] >= quota:
            skip["du quota"] += 1
            continue

        tags = [t for t in r["cf_tags"] if t]
        if BAD_TAGS & set(tags):
            skip["interactive"] += 1
            continue
        if not tags:
            skip["khong tag"] += 1
            continue
        if r["time_limit"] is None:
            skip["thieu time_limit"] += 1
            continue
        if "<image>" in r["description"]:
            skip["<image>"] += 1
            continue

        ins = list(r["public_tests"]["input"]) + list(r["private_tests"]["input"])
        outs = list(r["public_tests"]["output"]) + list(r["private_tests"]["output"])
        if len(ins) < 5:
            skip["it test"] += 1
            continue
        ins, outs = ins[:args.max_tests], outs[:args.max_tests]

        if sum(len(a) + len(b) for a, b in zip(ins, outs)) > MAX_BYTES_PER_PROBLEM:
            skip["qua nang"] += 1
            continue

        code = "cc%05d" % i
        d = f"{args.out}/problems/{code}"
        os.makedirs(d, exist_ok=True)

        cases = []
        for k, (a, b) in enumerate(zip(ins, outs), start=1):
            fi, fo = "%02d.in" % k, "%02d.out" % k
            open(f"{d}/{fi}", "w").write(a if a.endswith("\n") else a + "\n")
            open(f"{d}/{fo}", "w").write(b if b.endswith("\n") else b + "\n")
            cases.append((fi, fo))

        per = max(1, round(100 / len(cases)))
        with open(f"{d}/init.yml", "w") as f:
            f.write("test_cases:\n")
            for fi, fo in cases:
                f.write(f"- in: {fi}\n  out: {fo}\n  points: {per}\n")

        tl = r["time_limit"]["seconds"] + r["time_limit"]["nanos"] / 1e9
        items.append({
            "code": code,
            "name": clean_name(r["name"]),
            "description": r["description"],
            "time_limit": round(max(0.5, tl), 2),
            "memory_limit": r["memory_limit_bytes"] // 1024 or 262144,
            "points": max(1, min(30, round(r["cf_rating"] / 200))),
            "cf_rating": r["cf_rating"],
            "group": level,
            "types": types_of(tags),
            "n_tests": len(cases),
        })
        filled[level] += 1

        if len(items) % 50 == 0:
            print("  ... %d bai (duyet %d)" % (len(items), n_seen), flush=True)

    with open(f"{args.out}/data.json", "w") as f:
        json.dump(items, f, ensure_ascii=False, indent=2)

    print("\nXuat %d bai / duyet %d bai" % (len(items), n_seen))
    print("Theo muc do:", dict(filled))
    print("Bi loai    :", dict(skip))
    tc = Counter(t for it in items for t in it["types"])
    print("Theo chu de:", dict(tc.most_common()))


if __name__ == "__main__":
    main()
