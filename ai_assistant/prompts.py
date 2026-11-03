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

Write TWO Python 3 programs. Output them in this exact format, nothing else:

===GENERATOR===
<python code that prints ONE random valid input to stdout, respecting all constraints>
===SOLVER===
<python code that reads that input from stdin and prints the correct answer to stdout>

Rules:
- The solver must be correct, even if slow. Correctness matters, speed does not.
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
