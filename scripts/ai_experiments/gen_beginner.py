"""Sinh 50 bai nhap mon C++ bang AI.

Voi moi dang bai: goi Gemini viet de + generator + loi giai tham chieu,
chay generator va solver bang Python de lay test case that,
ghi ra thu muc theo dung cau truc DMOJ.
"""
import json, os, subprocess, tempfile, time
from google import genai
from google.genai import errors

MODEL = "gemini-3.8-flash"
OUT = os.path.expanduser("~/dutoj-data/beginner")
N_TESTS = 15

# (ma, ten bai, chuong, mo ta yeu cau cho AI)
TOPICS = [
    # --- Nhap xuat va bieu thuc ---
    ("Sum of Two Numbers", "Basics", "read two integers (-10^9..10^9) and print their sum"),
    ("Rectangle Area and Perimeter", "Basics", "read width and height (1..1000) and print area and perimeter separated by a space"),
    ("Celsius to Fahrenheit", "Basics", "read an integer Celsius temperature (-100..100) and print Fahrenheit rounded DOWN to an integer"),
    ("Circle Properties", "Basics", "read radius r (1..100), print circumference and area each rounded DOWN to an integer, using pi=3.14159265358979, separated by a space"),
    ("Swap Two Numbers", "Basics", "read two integers and print them in swapped order on one line"),
    ("Seconds to HMS", "Basics", "read a number of seconds (0..86399) and print hours, minutes, seconds separated by spaces"),
    ("Integer Division and Remainder", "Basics", "read two positive integers a and b (1..10^9), print a divided by b and a modulo b separated by a space"),
    ("Average of Three", "Basics", "read three integers and print their average rounded DOWN to an integer"),

    # --- Re nhanh ---
    ("Even or Odd", "Conditionals", "read an integer and print EVEN or ODD"),
    ("Positive Negative Zero", "Conditionals", "read an integer and print POSITIVE, NEGATIVE or ZERO"),
    ("Largest of Three", "Conditionals", "read three integers and print the largest"),
    ("Leap Year", "Conditionals", "read a year (1..9999) and print YES if it is a leap year else NO"),
    ("Quadratic Roots Count", "Conditionals", "read integers a b c (a is not zero, all in -100..100) for ax^2+bx+c=0 and print how many distinct real roots it has: 0, 1 or 2"),
    ("Triangle Type", "Conditionals", "read three integers a b c (1..100) as side lengths; print INVALID if a+b<=c or a+c<=b or b+c<=a, else EQUILATERAL if all equal, ISOSCELES if exactly two equal, else SCALENE. The generator must often produce valid triangles, not only invalid ones."),
    ("Grade Classification", "Conditionals", "read a score 0..100 and print A for 90-100, B for 80-89, C for 70-79, D for 60-69, F below 60"),
    ("Days in Month", "Conditionals", "read a month 1..12 and a year 1..9999, print how many days that month has"),

    # --- Vong lap ---
    ("Sum to N", "Loops", "read n (1..10^6) and print 1+2+...+n"),
    ("Multiplication Table", "Loops", "read n (1..20) and print n lines, line i containing the product n*i"),
    ("Factorial", "Loops", "read n (1..20) and print n factorial"),
    ("Count Digits", "Loops", "read a positive integer (1..10^18) and print how many digits it has"),
    ("Sum of Digits", "Loops", "read a positive integer (1..10^18) and print the sum of its digits"),
    ("Reverse Number", "Loops", "read a positive integer (1..10^9) and print it with digits reversed, without leading zeros"),
    ("Prime Check", "Loops", "read an integer n (2..10^6) and print YES if n is prime else NO"),
    ("Perfect Number", "Loops", "read an integer n (1..10^6) and print YES if n equals the sum of its proper divisors else NO"),
    ("Fibonacci Number", "Loops", "read n (1..40) and print the n-th Fibonacci number where F(1)=1 and F(2)=1"),
    ("GCD and LCM", "Loops", "read two positive integers (1..10^6) and print their greatest common divisor and least common multiple separated by a space"),

    # --- Mang mot chieu ---
    ("Array Maximum", "Arrays", "read n (1..1000) then n integers, print the maximum"),
    ("Array Sum and Average", "Arrays", "read n (1..1000) then n integers (0..1000), print their sum and their average rounded DOWN, separated by a space"),
    ("Count Even in Array", "Arrays", "read n (1..1000) then n integers, print how many are even"),
    ("Linear Search", "Arrays", "read n (1..1000), then n integers, then a value x; print the 1-based index of the FIRST occurrence of x, or -1 if absent"),
    ("Reverse Array", "Arrays", "read n (1..1000) then n integers, print them in reverse order on one line separated by spaces"),
    ("Bubble Sort", "Arrays", "read n (1..1000) then n integers, print them sorted in increasing order on one line separated by spaces"),
    ("Second Largest", "Arrays", "read n (2..1000) then n integers with at least two distinct values, print the second largest distinct value"),
    ("Remove Duplicates", "Arrays", "read n (1..1000) then n integers, print the distinct values in order of FIRST appearance, on one line separated by spaces"),
    ("Binary Search", "Arrays", "read n (1..1000), then n integers sorted in increasing order, then a value x; print the 1-based index of x or -1 if absent"),
    ("Merge Sorted Arrays", "Arrays", "read n then n sorted integers, then m then m sorted integers (n,m in 1..500); print all n+m values sorted on one line separated by spaces"),

    # --- Mang hai chieu ---
    ("Matrix Sum", "Matrices", "read r and c (1..50), then two r-by-c integer matrices; print their element-wise sum as r lines of c numbers"),
    ("Matrix Transpose", "Matrices", "read r and c (1..50) then an r-by-c integer matrix; print its transpose as c lines of r numbers"),
    ("Row and Column Sums", "Matrices", "read r and c (1..50) then an r-by-c integer matrix; print one line with the r row sums, then one line with the c column sums"),
    ("Main Diagonal Sum", "Matrices", "read n (1..50) then an n-by-n integer matrix; print the sum of the main diagonal"),
    ("Matrix Multiplication", "Matrices", "read n, m, p (1..30), then an n-by-m matrix and an m-by-p matrix of integers (-100..100); print their product as n lines of p numbers"),
    ("Symmetric Matrix Check", "Matrices", "read n (1..50) then an n-by-n integer matrix; print YES if it equals its transpose else NO"),

    # --- Chuoi ---
    ("String Length", "Strings", "read one line containing a string of lowercase letters (1..1000 characters) and print its length"),
    ("Reverse String", "Strings", "read one line containing a string of lowercase letters (1..1000 characters) and print it reversed"),
    ("Count Vowels", "Strings", "read one line containing a string of lowercase letters (1..1000 characters) and print how many vowels (a e i o u) it contains"),
    ("Palindrome Check", "Strings", "read one line containing a string of lowercase letters (1..1000 characters) and print YES if it reads the same backwards else NO"),
    ("Uppercase Conversion", "Strings", "read one line containing a string of lowercase letters and spaces (1..1000 characters) and print it in uppercase"),
    ("Count Words", "Strings", "read one line containing lowercase words separated by single spaces (1..1000 characters) and print how many words it has"),

    # --- De quy ---
    ("Recursive Factorial", "Recursion", "read n (1..20) and print n factorial; intended to be solved with recursion"),
    ("Tower of Hanoi Moves", "Recursion", "read n (1..50) and print the minimum number of moves needed to solve the Tower of Hanoi with n disks"),
]

PROMPT = """You are creating a beginner programming exercise for a university judge.

TASK: {task}

Produce exactly three sections, nothing else, no markdown fences:

===STATEMENT===
A short English problem statement in Markdown, at most 120 words.
Structure: one short paragraph describing the task, then a line "## Input"
with the input format and explicit constraints, then a line "## Output" with
the output format, then a line "## Example" containing one small input and its
output in fenced code blocks.

===GENERATOR===
Python 3 code printing ONE random valid input to stdout, obeying every
constraint in the statement. Use the `random` module. Vary the size and the
values between runs. No comments.

===SOLVER===
Python 3 code reading that input from stdin and printing the correct answer.
No comments.

CRITICAL RULES:
- The output must be EXACT text: never print floating point numbers; use
  integer arithmetic only. If the task mentions rounding, round down with //.
- If several answers would be valid, the statement must pin down exactly one.
- The generator and the solver must agree perfectly on the input format.
"""


def ask(client, prompt):
    for attempt in range(1, 7):
        try:
            return client.models.generate_content(model=MODEL, contents=prompt).text
        except errors.ServerError:
            time.sleep(5 * attempt)
    return None


def clean(s):
    return s.replace("```python", "").replace("```markdown", "").strip()


def main():
    os.makedirs(f"{OUT}/problems", exist_ok=True)
    old = f"{OUT}/data.json"
    items_old = json.load(open(old, encoding="utf-8")) if os.path.exists(old) else []
    client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
    items, failed = [], []

    START = int(os.environ.get('START_AT', '1'))
    for i, (title, chapter, task) in enumerate(TOPICS, start=1):
        if i < START:
            continue
        code = "intro%02d" % i
        print("[%2d/%d] %-28s" % (i, len(TOPICS), title), end=" ", flush=True)

        text = ask(client, PROMPT.format(task=task))
        if text is None:
            print("API that bai")
            failed.append(title)
            continue

        try:
            stmt = clean(text.split("===STATEMENT===")[1].split("===GENERATOR===")[0])
            gen = clean(text.split("===GENERATOR===")[1].split("===SOLVER===")[0])
            sol = clean(text.split("===SOLVER===")[1])
        except IndexError:
            print("sai dinh dang")
            failed.append(title)
            continue

        d = f"{OUT}/problems/{code}"
        os.makedirs(d, exist_ok=True)

        with tempfile.TemporaryDirectory() as tmp:
            gp, sp = os.path.join(tmp, "g.py"), os.path.join(tmp, "s.py")
            open(gp, "w").write(gen)
            open(sp, "w").write(sol)

            cases, seen, tries, bad = [], set(), 0, 0
            while len(cases) < N_TESTS and tries < N_TESTS * 4:
                tries += 1
                try:
                    inp = subprocess.run(["python3", gp], capture_output=True,
                                         text=True, timeout=5).stdout
                    r = subprocess.run(["python3", sp], input=inp,
                                       capture_output=True, text=True, timeout=5)
                except subprocess.TimeoutExpired:
                    bad += 1
                    continue
                if r.returncode != 0 or not inp.strip() or not r.stdout.strip():
                    bad += 1
                    continue
                if inp in seen:
                    continue
                seen.add(inp)
                cases.append((inp, r.stdout))

            if len(cases) < 5:
                print("chi %d test - bo qua" % len(cases))
                failed.append(title)
                continue

            n = len(cases)
            base, extra = divmod(100, n)
            for k, (inp, out) in enumerate(cases, start=1):
                open(f"{d}/%02d.in" % k, "w").write(inp)
                open(f"{d}/%02d.out" % k, "w").write(out)
            with open(f"{d}/init.yml", "w") as f:
                f.write("test_cases:\n")
                for k in range(1, n + 1):
                    pts = base + (1 if k <= extra else 0)
                    f.write("- in: %02d.in\n  out: %02d.out\n  points: %d\n" % (k, k, pts))

            open(f"{d}/_generator.py", "w").write(gen)
            open(f"{d}/_solver.py", "w").write(sol)

        items.append({
            "code": code,
            "name": title,
            "description": stmt,
            "time_limit": 1.0,
            "memory_limit": 262144,
            "points": 1,
            "cf_rating": 0,
            "group": "easy",
            "types": ["Introductory"],
            "chapter": chapter,
            "n_tests": len(cases),
        })
        print("OK (%d test, %d lan hong)" % (len(cases), bad))

    with open(f"{OUT}/data.json", "w", encoding="utf-8") as f:
        merged = {x["code"]: x for x in items_old}
        merged.update({x["code"]: x for x in items})
        json.dump(list(merged.values()), f, ensure_ascii=False, indent=2)

    print("\nXong: %d/%d bai -> %s" % (len(items), len(TOPICS), OUT))
    if failed:
        print("That bai:", ", ".join(failed))


if __name__ == "__main__":
    main()
