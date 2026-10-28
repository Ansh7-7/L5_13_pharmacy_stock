# Issues Found in `pharmacy_system.py`

Line numbers refer to the original starter file. Issues are ordered by severity (high and medium first).

| # | Issue | Type | Line(s) | Description | Fix Approach |
|---|-------|------|---------|-------------|--------------|
| 1 | SQL injection (Bandit B608) | Security – High impact | 21–22 | The patient name is inserted into the SQL string with `%`. Entering `x' OR '1'='1` returns every patient's ID and allergy, which leaks private medical data. | Use a parameterised query: `WHERE name = ?` with `(name,)` passed to `execute()`. |
| 2 | `try` / bare `except` / `pass` (Bandit B110, Pylint W0702, Flake8 E722) | Security / Bug | 56–59 | Every error in `load_stock` is silently ignored, including a corrupt stock file. | Catch only `FileNotFoundError` and `json.JSONDecodeError` and print a clear message. |
| 3 | Bare `except` in `dispense` (Pylint W0702, Flake8 E722) | Bug | 38–39 | Hides `IndexError` (unknown patient) and `KeyError` (drug not in stock or wrong case), so failures return `False` with no reason. | Removed the `try`/`except`; added explicit checks with messages. |
| 4 | Allergy check is case-sensitive | Logic bug (not flagged by any tool) | 32 | `"Penicillin" in "penicillin"` is `False`, so Kavya, who is allergic to penicillin, was dispensed Penicillin. | Normalise drug names with `.title()` and compare `allergy.lower() == drug.lower()`. |
| 5 | Dispensing more than is in stock | Logic bug (not flagged) | 35 | Arjun was given 30 Amoxicillin when only 20 were in stock, leaving stock at -10. | `stock_problem()` refuses the request if there are not enough units. |
| 6 | Expired medicine dispensed | Logic bug (not flagged) | 35 | Amoxicillin expired on 2025-12-31 but could still be dispensed. | `stock_problem()` checks the expiry date before dispensing. |
| 7 | Negative stock accepted | Logic bug (not flagged) | 25, 71 | `add_stock("Ibuprofen", -15, ...)` created a stock level of -15 units. | `add_stock` raises `ValueError` for units ≤ 0 and validates the date; `main` reports the rejected delivery. |
| 8 | Mutable default argument (Pylint W0102) | Bug | 24 | `batch_log=[]` is shared between every call. | Default changed to `None`, with a new list used inside the method. |
| 9 | Files opened without `with` or encoding (Pylint R1732, W1514) | Resource leak | 50–52, 57 | Files may never be closed; no encoding specified. | Use `with open(..., encoding="utf-8")`. |
| 10 | `global` statement (Pylint W0603) | Design | 55 | Global mutable state makes the code hard to test. | Moved state into a `Pharmacy` class. |
| 11 | Unused import (Pylint W0611, Flake8 F401) | Quality | 3 | `os` is never used. | Removed. |
| 12 | Naming convention (Pylint C0103) | Style | 61 | `printStock` is not snake_case. | Renamed to `print_stock`. |
| 13 | Missing docstrings (Pylint C0114, C0115, C0116) | Documentation | Whole file | No module, class or function docstrings. | Added docstrings throughout. |
| 14 | Iterating keys then indexing (Pylint C0206) | Quality | 43, 63 | `for d in stock:` followed by `stock[d]`. | Use `stock.items()`. |
| 15 | Lines too long (Flake8 E501, Pylint C0301) | Style | 25, 36 | 90 and 112 characters, over the 79-character limit. | Wrapped the lines. |
| 16 | Wrong blank lines (Flake8 E302, E305) | Style | 11, 19, 24, 29, 41, 49, 54, 61, 66, 83 | Only one blank line between top-level definitions. | Two blank lines around top-level functions and classes. |
| 17 | No `__main__` guard; DB never closed | Quality | 7, 83 | `main()` runs on import; the connection is never closed. | Added `if __name__ == "__main__":` and a `close()` method. |