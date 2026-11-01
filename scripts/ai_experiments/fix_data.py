"""Vá data.json cho 19 bai da sinh test case nhung mat phan de."""
import json, os

OUT = os.path.expanduser("~/dutoj-data/beginner")

P = [
("intro01", "Sum of Two Numbers", "Basics",
 "Read two integers and print their sum.\n\n## Input\nOne line with two integers $a$ and $b$ ($-10^9 \\le a, b \\le 10^9$).\n\n## Output\nPrint a single integer: $a + b$.\n\n## Example\n```\n3 5\n```\n```\n8\n```"),
("intro02", "Rectangle Area and Perimeter", "Basics",
 "Read the width and height of a rectangle and print its area and perimeter.\n\n## Input\nOne line with two integers $w$ and $h$ ($1 \\le w, h \\le 1000$).\n\n## Output\nPrint two integers separated by a space: the area and the perimeter.\n\n## Example\n```\n3 4\n```\n```\n12 14\n```"),
("intro03", "Celsius to Fahrenheit", "Basics",
 "Convert a temperature from Celsius to Fahrenheit using $F = C \\times 9 / 5 + 32$, rounded down to an integer.\n\n## Input\nOne line with an integer $c$ ($-100 \\le c \\le 100$).\n\n## Output\nPrint the temperature in Fahrenheit, rounded down.\n\n## Example\n```\n100\n```\n```\n212\n```"),
("intro04", "Circle Properties", "Basics",
 "Read the radius of a circle and print its circumference and area, each rounded down to an integer. Use $\\pi = 3.14159265358979$.\n\n## Input\nOne line with an integer $r$ ($1 \\le r \\le 100$).\n\n## Output\nPrint two integers separated by a space: the circumference and the area, both rounded down.\n\n## Example\n```\n1\n```\n```\n6 3\n```"),
("intro05", "Swap Two Numbers", "Basics",
 "Read two integers and print them in the opposite order.\n\n## Input\nOne line with two integers $a$ and $b$ ($-10^9 \\le a, b \\le 10^9$).\n\n## Output\nPrint $b$ and $a$ separated by a space.\n\n## Example\n```\n7 2\n```\n```\n2 7\n```"),
("intro06", "Seconds to HMS", "Basics",
 "Convert a number of seconds into hours, minutes and seconds.\n\n## Input\nOne line with an integer $s$ ($0 \\le s \\le 86399$).\n\n## Output\nPrint three integers separated by spaces: the number of whole hours, the remaining whole minutes, and the remaining seconds.\n\n## Example\n```\n3725\n```\n```\n1 2 5\n```"),
("intro07", "Integer Division and Remainder", "Basics",
 "Read two positive integers and print the quotient and the remainder of the integer division.\n\n## Input\nOne line with two integers $a$ and $b$ ($1 \\le a, b \\le 10^9$).\n\n## Output\nPrint two integers separated by a space: $a$ divided by $b$ (rounded down) and $a$ modulo $b$.\n\n## Example\n```\n17 5\n```\n```\n3 2\n```"),
("intro08", "Average of Three", "Basics",
 "Read three integers and print their average, rounded down to an integer.\n\n## Input\nOne line with three integers ($-10^9 \\le a, b, c \\le 10^9$).\n\n## Output\nPrint the average of the three values, rounded down.\n\n## Example\n```\n1 2 4\n```\n```\n2\n```"),
("intro09", "Even or Odd", "Conditionals",
 "Determine whether a number is even or odd.\n\n## Input\nOne line with an integer $n$ ($-10^9 \\le n \\le 10^9$).\n\n## Output\nPrint `EVEN` if $n$ is even, otherwise print `ODD`.\n\n## Example\n```\n4\n```\n```\nEVEN\n```"),
("intro10", "Positive Negative Zero", "Conditionals",
 "Determine the sign of a number.\n\n## Input\nOne line with an integer $n$ ($-10^9 \\le n \\le 10^9$).\n\n## Output\nPrint `POSITIVE` if $n > 0$, `NEGATIVE` if $n < 0$, or `ZERO` if $n = 0$.\n\n## Example\n```\n-5\n```\n```\nNEGATIVE\n```"),
("intro11", "Largest of Three", "Conditionals",
 "Find the largest of three numbers.\n\n## Input\nOne line with three integers ($-10^9 \\le a, b, c \\le 10^9$).\n\n## Output\nPrint the largest of the three values.\n\n## Example\n```\n3 9 5\n```\n```\n9\n```"),
("intro12", "Leap Year", "Conditionals",
 "A year is a leap year if it is divisible by 4, except for years divisible by 100 which are only leap years when also divisible by 400.\n\n## Input\nOne line with an integer $y$ ($1 \\le y \\le 9999$).\n\n## Output\nPrint `YES` if $y$ is a leap year, otherwise `NO`.\n\n## Example\n```\n2000\n```\n```\nYES\n```"),
("intro13", "Quadratic Roots Count", "Conditionals",
 "For the equation $ax^2 + bx + c = 0$, report how many distinct real roots it has.\n\n## Input\nOne line with three integers $a$, $b$, $c$ ($-100 \\le a, b, c \\le 100$, $a \\ne 0$).\n\n## Output\nPrint `0`, `1` or `2`: the number of distinct real roots.\n\n## Example\n```\n1 -2 1\n```\n```\n1\n```"),
("intro14", "Triangle Type", "Conditionals",
 "Given three side lengths, classify the triangle they form.\n\n## Input\nOne line with three integers $a$, $b$, $c$ ($1 \\le a, b, c \\le 100$).\n\n## Output\nPrint `INVALID` if the sides cannot form a triangle. Otherwise print `EQUILATERAL` if all three sides are equal, `ISOSCELES` if exactly two are equal, or `SCALENE` if all are different.\n\n## Example\n```\n3 4 5\n```\n```\nSCALENE\n```"),
("intro15", "Grade Classification", "Conditionals",
 "Convert a numeric score into a letter grade.\n\n## Input\nOne line with an integer $s$ ($0 \\le s \\le 100$).\n\n## Output\nPrint `A` for 90-100, `B` for 80-89, `C` for 70-79, `D` for 60-69, and `F` below 60.\n\n## Example\n```\n85\n```\n```\nB\n```"),
("intro16", "Days in Month", "Conditionals",
 "Report how many days a given month has. February has 29 days in a leap year and 28 otherwise.\n\n## Input\nOne line with two integers $m$ and $y$ ($1 \\le m \\le 12$, $1 \\le y \\le 9999$).\n\n## Output\nPrint the number of days in month $m$ of year $y$.\n\n## Example\n```\n2 2000\n```\n```\n29\n```"),
("intro17", "Sum to N", "Loops",
 "Compute the sum of all integers from 1 to $n$.\n\n## Input\nOne line with an integer $n$ ($1 \\le n \\le 10^6$).\n\n## Output\nPrint the value of $1 + 2 + \\dots + n$.\n\n## Example\n```\n5\n```\n```\n15\n```"),
("intro18", "Multiplication Table", "Loops",
 "Print the multiplication table of a number.\n\n## Input\nOne line with an integer $n$ ($1 \\le n \\le 20$).\n\n## Output\nPrint 20 lines. Line $i$ contains the product $n \\times i$.\n\n## Example\n```\n3\n```\n```\n3\n6\n9\n```\n(The real output has 20 lines; only the first three are shown.)"),
("intro19", "Factorial", "Loops",
 "Compute the factorial of a number.\n\n## Input\nOne line with an integer $n$ ($1 \\le n \\le 20$).\n\n## Output\nPrint $n! = 1 \\times 2 \\times \\dots \\times n$.\n\n## Example\n```\n5\n```\n```\n120\n```"),
]

items = []
for code, name, chapter, desc in P:
    d = f"{OUT}/problems/{code}"
    if not os.path.isdir(d):
        print("thieu thu muc", code)
        continue
    n = len([f for f in os.listdir(d) if f.endswith(".in")])
    items.append({
        "code": code, "name": name, "description": desc,
        "time_limit": 1.0, "memory_limit": 262144, "points": 1,
        "cf_rating": 0, "group": "easy", "types": ["Introductory"],
        "chapter": chapter, "n_tests": n,
    })

with open(f"{OUT}/data.json", "w", encoding="utf-8") as f:
    json.dump(items, f, ensure_ascii=False, indent=2)
print("Da ghi", len(items), "bai vao", f"{OUT}/data.json")
