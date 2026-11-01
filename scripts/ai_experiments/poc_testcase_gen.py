import json, os, subprocess, tempfile
from google import genai

PROBLEM = "cc00008"   # Phone Numbers

d = json.load(open(os.path.expanduser("~/dutoj/data.json")))
# neu data.json hien tai la ban 1000 bai thi cc00008 co the khong con
p = next((x for x in d if x["code"] == PROBLEM), None)
if p is None:
    print("Khong tim thay", PROBLEM, "- doi PROBLEM sang ma khac trong data.json")
    print("Vi du:", [x["code"] for x in d[:5]])
    raise SystemExit

prompt = f"""You are helping build test data for a competitive programming judge.

PROBLEM STATEMENT:
{p['description']}

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

import time
from google.genai import errors

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

text = None
for attempt in range(1, 7):
    try:
        resp = client.models.generate_content(
            model="gemini-3.8-flash", contents=prompt)
        text = resp.text
        break
    except errors.ServerError:
        wait = 5 * attempt
        print("Lan %d that bai (may chu qua tai), cho %ds..." % (attempt, wait))
        time.sleep(wait)

if text is None:
    raise SystemExit("Goi API that bai sau 6 lan. Thu lai sau.")

try:
    gen = text.split("===GENERATOR===")[1].split("===SOLVER===")[0].strip()
    sol = text.split("===SOLVER===")[1].strip()
except IndexError:
    print("AI tra ve sai dinh dang:\n", text[:800])
    raise SystemExit

gen = gen.replace("```python", "").replace("```", "").strip()
sol = sol.replace("```python", "").replace("```", "").strip()

print("=== GENERATOR ===\n", gen, "\n")
print("=== SOLVER ===\n", sol, "\n")

with tempfile.TemporaryDirectory() as tmp:
    g = os.path.join(tmp, "gen.py")
    s = os.path.join(tmp, "sol.py")
    open(g, "w").write(gen)
    open(s, "w").write(sol)

    print("=== CHAY THU 3 LAN ===")
    for i in range(3):
        inp = subprocess.run(["python3", g], capture_output=True, text=True, timeout=10).stdout
        out = subprocess.run(["python3", s], input=inp, capture_output=True, text=True, timeout=10).stdout
        print(f"--- lan {i+1} ---")
        print("INPUT :", inp.strip()[:120])
        print("OUTPUT:", out.strip()[:120])
