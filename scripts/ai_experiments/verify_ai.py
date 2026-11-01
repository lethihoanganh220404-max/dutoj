"""Kiem chung: loi giai AI sinh ra co dung voi test case that khong.

Voi moi bai: goi AI viet generator + solver, roi chay solver tren
cac file .in co san, so output voi file .out.
"""
import json, os, subprocess, sys, tempfile, time
from google import genai
from google.genai import errors

PROBLEMS = sys.argv[1:] or ["cc00008"]
MODEL = "gemini-3.8-flash"
PROB_DIR = os.path.expanduser("~/dutoj/problems")

PROMPT = """You are helping build test data for a competitive programming judge.

PROBLEM STATEMENT:
{desc}

Write TWO Python 3 programs. Output them in this exact format, nothing else:

===GENERATOR===
<python code that prints ONE random valid input to stdout, respecting all constraints>
===SOLVER===
<python code that reads that input from stdin and prints the correct answer to stdout>

Rules:
- The solver must be correct, even if slow.
- No comments, no explanation, no markdown fences.
- The generator must use the `random` module and produce varied inputs.
"""


def ask(client, prompt):
    for attempt in range(1, 7):
        try:
            return client.models.generate_content(
                model=MODEL, contents=prompt).text
        except errors.ServerError:
            time.sleep(5 * attempt)
    return None


def strip_fence(s):
    return s.replace("```python", "").replace("```", "").strip()


def main():
    data = json.load(open(os.path.expanduser("~/dutoj/data.json")))
    by_code = {x["code"]: x for x in data}
    client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

    for code in PROBLEMS:
        p = by_code.get(code)
        if p is None:
            print(code, "- khong co trong data.json")
            continue

        print("\n" + "=" * 60)
        print(code, "|", p["name"], "| rating", p["cf_rating"])

        text = ask(client, PROMPT.format(desc=p["description"]))
        if text is None:
            print("  API that bai")
            continue

        try:
            gen = strip_fence(text.split("===GENERATOR===")[1].split("===SOLVER===")[0])
            sol = strip_fence(text.split("===SOLVER===")[1])
        except IndexError:
            print("  AI tra ve sai dinh dang")
            continue

        d = os.path.join(PROB_DIR, code)
        ins = sorted(f for f in os.listdir(d) if f.endswith(".in"))

        with tempfile.TemporaryDirectory() as tmp:
            sp = os.path.join(tmp, "sol.py")
            gp = os.path.join(tmp, "gen.py")
            open(sp, "w").write(sol)
            open(gp, "w").write(gen)

            ok = bad = err = 0
            for fi in ins:
                inp = open(os.path.join(d, fi)).read()
                exp = open(os.path.join(d, fi[:-3] + ".out")).read()
                try:
                    r = subprocess.run(["python3", sp], input=inp,
                                       capture_output=True, text=True, timeout=10)
                    got = r.stdout
                except subprocess.TimeoutExpired:
                    err += 1
                    continue
                if r.returncode != 0:
                    err += 1
                elif got.split() == exp.split():
                    ok += 1
                else:
                    bad += 1
                    if bad == 1:
                        print("  Sai o", fi)
                        print("    can :", exp.strip()[:80])
                        print("    duoc:", got.strip()[:80])

            print("  SOLVER tren %d test that: dung %d, sai %d, loi %d"
                  % (len(ins), ok, bad, err))

            try:
                g = subprocess.run(["python3", gp], capture_output=True,
                                   text=True, timeout=10)
                print("  GENERATOR:", "chay duoc" if g.returncode == 0 else "LOI",
                      "| vi du:", g.stdout.strip()[:60].replace("\n", " | "))
            except subprocess.TimeoutExpired:
                print("  GENERATOR: treo")


if __name__ == "__main__":
    main()
