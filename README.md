# 🧮 Simple Calculator with User History

An elegant, command-line Python calculator that implements a smart expression parser with a persistent JSON-based history log.

---

## Features

- **🧠 Safe Expression Parser (No `eval()`)**:
  - Implements a recursive descent parser. Parses tokens and processes operations safely without using Python's unsafe `eval()`.
- **📐 Mathematical Expression Solver**:
  - Evaluate complex formulas in one line, e.g., `(5 + 3) * pi / (2 ^ 4)`.
  - Supports addition (`+`), subtraction (`-`), multiplication (`*`), division (`/`), modulo (`%`), and power (`^`).
- **🏛️ Built-in Constants**:
  - Recognizes `pi` ($3.14159...$) and `e` ($2.71828...$) naturally in expressions.
- **💾 Persistent History**:
  - History is saved automatically to a persistent `calculator_history.json` file.
  - History can be viewed or cleared directly from the main menu.
- **🎨 Subtle Console Styling**:
  - Beautiful, subtle ANSI colors for clean output.

---

## 🚀 How to Run

1. Open a terminal or Command Prompt in the project folder.
2. Run the application:
   ```bash
   python calculator.py
   ```

---

## 🛠️ Usage

### Main Menu
```text
========================================
         SIMPLE CALCULATOR MENU
========================================
1. Perform Calculation
2. View Calculation History
3. Clear Calculation History
4. Exit
========================================
```

### 1. Perform Calculation
```text
--- Perform Calculation ---
Enter your expression (or 'back' to return).
Enter expression: (12.5 + pi) * 2 ^ 3
Result: 125.1327412287

Enter expression: back
```

### 2. View Calculation History
```text
----------------------------------------
         CALCULATION HISTORY
----------------------------------------
 1. (12.5 + pi) * 2 ^ 3 = 125.1327412287
----------------------------------------
```
