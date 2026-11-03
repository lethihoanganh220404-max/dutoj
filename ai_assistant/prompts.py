"""Toan bo prompt de rieng mot cho, de sua va de dua vao bao cao."""

ANH_SANG_MARKDOWN = """You are helping to digitise competitive programming problems.

Read the problem statement in the image and convert it to Markdown.

Rules:
- Output the statement in ENGLISH. If the image is in another language, translate it.
- Use LaTeX for all mathematical formulas: $n \\le 10^5$ inline, $$...$$ for display.
- Follow this structure exactly, using these headings:

  Line 1: a level-1 heading with the problem name
  Then: the statement body
  Then: a level-2 heading "Input", followed by the input format
  Then: a level-2 heading "Output", followed by the output format
  Then: a level-2 heading "Constraints", followed by the constraints, one per line
  Then: a level-2 heading "Examples", and under it a level-3 heading
        "Example 1" (and "Example 2" etc. if the image shows more)

- Inside each example, put the sample input after the word "Input:" and the sample
  output after the word "Output:". Wrap each of them in a fenced code block
  (three backtick characters on their own line before and after).
- If something is unreadable in the image, write an HTML comment saying
  UNCLEAR plus what you could not read, instead of guessing. Never invent
  a constraint or a sample value.
- Return ONLY the Markdown. No preamble, no explanation, no outer code fence.
"""


SINH_GOI_Y = """You are a teaching assistant for a university programming course.

Below is a problem statement. Write three progressive hints for a student who is
stuck. The student should be able to read hint 1, think, and only move on if still
stuck.

Level 1 - A nudge. Point at what to observe about the problem. Name no algorithm.
          Two or three sentences.
Level 2 - Name the algorithm or data structure to use, and say why it fits.
          Mention the time complexity. Do not write code.
Level 3 - A full walkthrough of the solution: the steps in order, the edge cases
          to watch for, and a short C++ code sketch.

Write in English. Use LaTeX for formulas, as $n \\le 10^5$.

Return ONLY a JSON object, no preamble and no code fence, exactly like this:
{"muc1": "...", "muc2": "...", "muc3": "..."}

The three values are Markdown strings. Escape newlines inside them as \\n.

--- PROBLEM STATEMENT ---
%s
"""


SINH_TEST_CASE = """You are helping build test data for a competitive programming judge.

PROBLEM STATEMENT:
%s

First, answer one question about the problem, then write three programs.
Output everything in this exact format, nothing else:

===DA_DAP_AN===
<Write YES if a valid input can have MORE THAN ONE correct output - for example
 the statement says "print any valid answer", or asks for any arrangement,
 any path, any assignment. Write NO if every input has exactly one correct
 output. Then on the next line, one sentence saying why.>
===GENERATOR===
<python code that prints ONE random valid input to stdout, respecting all constraints>
===SOLVER===
<python code that reads that input from stdin and prints the correct answer to stdout>
===SOLVER2===
<a SECOND solver, written independently, using a DIFFERENT approach from the first>
===CHECKER===
<Only if you answered YES above: a Python 3 special judge for the DMOJ judge.
 If you answered NO, write exactly: KHONG CAN

 The checker must have exactly this signature:

     from dmoj.result import CheckerResult

     def check(process_output, judge_output, judge_input=None, point_value=1, **kwargs):
         ...

 - process_output is the contestant's output, as bytes.
 - judge_output is the reference output, as bytes.
 - judge_input is the original test input, as bytes; it may be a lazy object,
   so always call bytes(judge_input) before using it. Decode with .decode().
 - Return CheckerResult(True, point_value) when the answer is valid.
 - Return CheckerResult(False, 0, None, '<short reason>') when it is not.
 - Do NOT compare process_output to judge_output token by token. VERIFY the
   contestant's answer against the problem's rules, using judge_input.
 - If the contestant claims no solution exists, check that judge_output says so too.
 - Wrap parsing in try/except; on exception return
   CheckerResult(False, 0, 'Checker error', str(e)).
 - Standard library and dmoj.result only.>

Rules:
- Both solvers must be correct, even if slow. Correctness matters, speed does not.
- SOLVER2 must NOT be a copy of SOLVER with renamed variables. Use a genuinely
  different method: if SOLVER iterates, SOLVER2 might use a formula, a different
  data structure, recursion, or brute force over a different quantity.
  The point is that if one solver misreads the problem, the other probably will not.
- The generator must use the `random` module and produce varied inputs.
- The generator must respect EVERY constraint in the statement.
- No comments, no explanation, no markdown fences.

IMPORTANT - the generator must read one argument from the command line:

    import sys
    muc = sys.argv[1] if len(sys.argv) > 1 else 'vua'

  'nho'  -> smallest valid inputs: edge cases, minimum sizes, empty-ish cases,
            all-same values, extreme values allowed by the constraints
  'vua'  -> medium random inputs
  'lon'  -> inputs AT the upper limit of every size constraint in the statement

  For 'lon', use the true maximum the statement allows, not a smaller safe number.
  The solver may be slow on these; that is acceptable and expected.
"""


SINH_CHECKER = """You are writing a special judge (checker) for a programming problem
that accepts MANY different correct answers.

PROBLEM STATEMENT:
%s

A reference answer looks like this (for the sample input below):

INPUT:
%s

REFERENCE OUTPUT:
%s

Write a Python 3 checker for the DMOJ judge. Output ONLY the code, no fences,
no explanation.

The checker MUST have exactly this signature:

    from dmoj.result import CheckerResult

    def check(process_output, judge_output, judge_input=None, point_value=1, **kwargs):
        ...

Rules:
- process_output is the contestant's output, as bytes.
- judge_output is the reference output, as bytes.
- judge_input is the original test input, as bytes. It may be a lazy object,
  so always call bytes(judge_input) before using it.
- Decode bytes with .decode() before parsing text.
- Return CheckerResult(True, point_value) when the contestant's answer is valid.
- Return CheckerResult(False, 0, None, '<short reason>') when it is not.
- Do NOT compare the contestant's output to judge_output token by token.
  VERIFY the contestant's answer against the problem's rules, using judge_input.
- If the contestant claims no solution exists, check whether judge_output also
  says so; disagreement means the contestant is wrong.
- Wrap all parsing in try/except; on any exception return
  CheckerResult(False, 0, 'Checker error', str(e)).
- No imports other than the standard library and dmoj.result.
"""
