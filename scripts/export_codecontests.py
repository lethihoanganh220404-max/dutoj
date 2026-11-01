import json, os, re, shutil
from datasets import load_dataset

OUT = os.path.expanduser("~/dutoj-data/out")
N_PROBLEMS = 5          # doi thanh 1000 khi chay that
MAX_TESTS  = 20
SCAN_LIMIT = 500

def points_of(r):
    rating = r["cf_rating"]
    if rating and rating > 0:
        return max(1, min(50, round(rating / 200)))
    return 3

def clean_name(s):
    s = re.sub(r"^\d+_[A-Z]\d*\.\s*", "", s).strip()
    return (s or "Untitled")[:100]

shutil.rmtree(OUT, ignore_errors=True)
os.makedirs(f"{OUT}/problems", exist_ok=True)

ds = load_dataset("deepmind/code_contests", split="train", streaming=True)
items = []

for i, r in enumerate(ds):
    if i >= SCAN_LIMIT or len(items) >= N_PROBLEMS:
        break
    if r["time_limit"] is None:
        continue
    if "<image>" in r["description"]:
        continue

    ins  = list(r["public_tests"]["input"])  + list(r["private_tests"]["input"])
    outs = list(r["public_tests"]["output"]) + list(r["private_tests"]["output"])
    if len(ins) < 5:
        continue
    ins, outs = ins[:MAX_TESTS], outs[:MAX_TESTS]

    code = "cc%05d" % i
    d = f"{OUT}/problems/{code}"
    os.makedirs(d, exist_ok=True)

    cases = []
    for k, (a, b) in enumerate(zip(ins, outs), start=1):
        fi, fo = "%02d.in" % k, "%02d.out" % k
        open(f"{d}/{fi}", "w").write(a if a.endswith("\n") else a + "\n")
        open(f"{d}/{fo}", "w").write(b if b.endswith("\n") else b + "\n")
        cases.append((fi, fo))

    with open(f"{d}/init.yml", "w") as f:
        per = max(1, round(100 / len(cases)))
        f.write("test_cases:\n")
        for fi, fo in cases:
            f.write(f"- in: {fi}\n  out: {fo}\n  points: {per}\n")

    tl = r["time_limit"]["seconds"] + r["time_limit"]["nanos"] / 1e9
    ml = r["memory_limit_bytes"] // 1024 or 262144

    items.append({
        "code": code,
        "name": clean_name(r["name"]),
        "description": r["description"],
        "time_limit": round(max(0.5, tl), 2),
        "memory_limit": ml,
        "points": points_of(r),
        "source": r["source"],
        "cf_rating": r["cf_rating"],
        "n_tests": len(cases),
    })

with open(f"{OUT}/data.json", "w") as f:
    json.dump(items, f, ensure_ascii=False, indent=2)

print("Xuat duoc", len(items), "bai vao", OUT)
for it in items:
    print(" ", it["code"], "|", it["n_tests"], "test |",
          it["time_limit"], "s |", it["memory_limit"], "KB |",
          it["points"], "diem |", it["name"][:45])
