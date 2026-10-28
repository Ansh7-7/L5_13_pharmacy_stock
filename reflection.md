# Reflection

## 1. Which issues were the easiest to fix, and which were the hardest? Why?

The easiest were the style and simple quality issues: removing the unused `os` import, renaming `printStock` to `print_stock`, adding docstrings, wrapping long lines and adding blank lines between functions. The tools pointed to the exact line and the fix was mechanical.

The hardest were the issues that touched the program's logic. Removing the bare `except` in `dispense` meant deciding what should happen for an unknown patient or a drug not in stock, and writing explicit checks for each case. Removing the `global` statement meant moving the shared state into a `Pharmacy` class. The hardest of all were bugs no tool reported, such as the case-sensitive allergy check that let Kavya receive Penicillin, which I only found by running the program and reading the output.

## 2. Did the static analysis tools report any false positives? If so, describe one example.

There were no real false positives, since every warning pointed at a genuine problem. The closest case is Bandit's B608 warning, which Bandit reports with low confidence because it flags any SQL built with string formatting. Here it was a true positive: typing `x' OR '1'='1` at the lookup prompt returned every patient's allergy record.

The bigger limitation was false negatives. None of the tools noticed the case-sensitive allergy check, negative stock, dispensing more than was in stock, or dispensing expired medicine. Static analysis checks how code is written, not whether it does the right thing, so testing is still needed.

## 3. How would you integrate static analysis tools into your actual software development workflow?

Locally, I would run Flake8 and Pylint in my editor and use a pre-commit hook so all three tools run before every commit. In a team, I would add them to a CI pipeline such as GitHub Actions that runs on every pull request, fails if Bandit finds medium or high severity issues or the Pylint score drops below 9.5, and requires a clean run before merging. Shared config files (`.pylintrc`, `.flake8`) would keep the rules consistent.

## 4. What tangible improvements did you observe in code quality, readability, or potential robustness after applying the fixes?

- **Security:** the SQL injection is gone, so patient data can no longer be dumped through the lookup prompt.
- **Safety:** the program refuses to dispense a drug a patient is allergic to, more units than are in stock, or expired stock, and rejects negative deliveries. Before, stock reached -10 and -15.
- **Robustness:** errors are no longer silently swallowed, and each failure prints a clear reason.
- **Maintainability:** state lives in a `Pharmacy` class instead of globals, files are closed with `with`, and the database connection is closed.
- **Readability:** PEP 8 formatting, snake_case names and docstrings throughout.
- **Measured result:** Bandit and Flake8 report no issues, and the Pylint score rose to 10.00/10.