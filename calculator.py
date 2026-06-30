#!/usr/bin/env python3
"""
Simple Calculator with User History

This program provides a command-line interface for performing basic arithmetic
and complex mathematical expressions safely. It maintains a persistent history
of calculations.
"""

import os
import sys
import re
import math
import json

# ANSI escape codes for styling
COLOR_RESET = "\033[0m"
COLOR_CYAN = "\033[36m"
COLOR_GREEN = "\033[32m"
COLOR_RED = "\033[31m"
STYLE_BOLD = "\033[1m"

HISTORY_FILE = "calculator_history.json"

def load_history():
    """Load history records from JSON file."""
    if not os.path.exists(HISTORY_FILE):
        return []
    try:
        with open(HISTORY_FILE, "r") as f:
            return json.load(f)
    except Exception:
        return []

def save_history(history):
    """Save history records to JSON file."""
    try:
        with open(HISTORY_FILE, "w") as f:
            json.dump(history, f, indent=4)
    except Exception:
        pass

# ----------------- PARSER & TOKENIZER -----------------

def tokenize(expression: str):
    """Convert an expression string into token tuples."""
    token_specification = [
        ('NUMBER',   r'\d+(\.\d*)?|\.\d+'),       # Decimals or integers
        ('IDENT',    r'[a-zA-Z_][a-zA-Z0-9_]*'),   # Constants like pi, e
        ('OP',       r'[+\-*/%^]'),                 # Operators
        ('LPAREN',   r'\('),                       # Left parenthesis
        ('RPAREN',   r'\)'),                       # Right parenthesis
        ('SKIP',     r'[ \t\n]+'),                 # Skip whitespace
        ('MISMATCH', r'.'),                        # Any other character
    ]
    tok_regex = '|'.join(f'(?P<{name}>{pattern})' for name, pattern in token_specification)
    tokens = []
    for mo in re.finditer(tok_regex, expression):
        kind = mo.lastgroup
        value = mo.group()
        if kind == 'NUMBER':
            tokens.append((kind, float(value)))
        elif kind == 'IDENT':
            tokens.append((kind, value))
        elif kind == 'OP' or kind == 'LPAREN' or kind == 'RPAREN':
            tokens.append((kind, value))
        elif kind == 'SKIP':
            continue
        else:
            raise ValueError(f"Unexpected character '{value}'")
    return tokens

class Parser:
    """
    A recursive descent parser that safely parses and evaluates mathematical expressions.
    Avoids using python's unsafe eval().
    """
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    def current_token(self):
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return None

    def consume(self, expected_type=None):
        tok = self.current_token()
        if tok is None:
            raise ValueError("Unexpected end of expression")
        if expected_type and tok[0] != expected_type:
            raise ValueError(f"Expected {expected_type}, got '{tok[1]}'")
        self.pos += 1
        return tok

    def parse(self):
        if not self.tokens:
            raise ValueError("Empty expression")
        result = self.expr()
        if self.current_token() is not None:
            raise ValueError(f"Unexpected symbol at end: '{self.current_token()[1]}'")
        return result

    def expr(self):
        # expr : term (( "+" | "-" ) term)*
        result = self.term()
        while True:
            tok = self.current_token()
            if tok and tok[0] == 'OP' and tok[1] in ('+', '-'):
                op = self.consume()[1]
                right = self.term()
                if op == '+':
                    result += right
                else:
                    result -= right
            else:
                break
        return result

    def term(self):
        # term : factor (( "*" | "/" | "%" ) factor)*
        result = self.factor()
        while True:
            tok = self.current_token()
            if tok and tok[0] == 'OP' and tok[1] in ('*', '/', '%'):
                op = self.consume()[1]
                right = self.factor()
                if op == '*':
                    result *= right
                elif op == '/':
                    if right == 0:
                        raise ZeroDivisionError("Division by zero is undefined")
                    result /= right
                elif op == '%':
                    if right == 0:
                        raise ZeroDivisionError("Modulo by zero is undefined")
                    result %= right
            else:
                break
        return result

    def factor(self):
        # factor : power ( "^" factor )*
        result = self.power()
        tok = self.current_token()
        if tok and tok[0] == 'OP' and tok[1] == '^':
            self.consume()
            right = self.factor()
            try:
                result = result ** right
            except OverflowError:
                raise ValueError("Overflow error: Exponent result too large")
        return result

    def power(self):
        # power : ("+" | "-")? power | atom
        tok = self.current_token()
        if tok and tok[0] == 'OP' and tok[1] in ('+', '-'):
            op = self.consume()[1]
            val = self.power()
            return val if op == '+' else -val
        return self.atom()

    def atom(self):
        tok = self.current_token()
        if tok is None:
            raise ValueError("Expected number, constant, or '('")
        
        if tok[0] == 'NUMBER':
            self.consume()
            return tok[1]
        
        elif tok[0] == 'IDENT':
            name_tok = self.consume()
            name = name_tok[1].lower()
            if name == 'pi':
                return math.pi
            elif name == 'e':
                return math.e
            else:
                raise ValueError(f"Unknown symbol '{name_tok[1]}'")
                
        elif tok[0] == 'LPAREN':
            self.consume('LPAREN')
            val = self.expr()
            self.consume('RPAREN')
            return val
            
        else:
            raise ValueError(f"Unexpected token '{tok[1]}'")

# ----------------- UI FORMATTING & HELPERS -----------------

def format_num(val):
    """Format float values nicely for printing."""
    if isinstance(val, (int, float)):
        if val == int(val):
            return str(int(val))
        s = f"{val:.10f}".rstrip('0').rstrip('.')
        if 'e' in f"{val:g}" or len(s) > 15:
            return f"{val:g}"
        return s
    return str(val)

def display_menu():
    """Display the application menu."""
    print(f"\n{COLOR_CYAN}========================================{COLOR_RESET}")
    print(f"         {STYLE_BOLD}SIMPLE CALCULATOR MENU{COLOR_RESET}")
    print(f"{COLOR_CYAN}========================================{COLOR_RESET}")
    print("1. Perform Calculation")
    print("2. View Calculation History")
    print("3. Clear Calculation History")
    print("4. Exit")
    print(f"{COLOR_CYAN}========================================{COLOR_RESET}")

def show_history():
    """Display calculation history."""
    history = load_history()
    if not history:
        print("\nNo history recorded yet in this session.")
        return

    print(f"\n{COLOR_CYAN}----------------------------------------{COLOR_RESET}")
    print(f"         {STYLE_BOLD}CALCULATION HISTORY{COLOR_RESET}")
    print(f"{COLOR_CYAN}----------------------------------------{COLOR_RESET}")
    for idx, entry in enumerate(history, 1):
        expr = entry.get("expression", "")
        res = entry.get("result", "")
        if res.startswith("Error:"):
            res_colored = f"{COLOR_RED}{res}{COLOR_RESET}"
        else:
            res_colored = f"{COLOR_GREEN}{res}{COLOR_RESET}"
            
        print(f"{idx:2d}. {expr} = {res_colored}")
    print(f"{COLOR_CYAN}----------------------------------------{COLOR_RESET}")

# ----------------- EXECUTION MODES -----------------

def perform_calculation():
    """Prompt the user for a mathematical expression and evaluate it."""
    print(f"\n{COLOR_CYAN}--- Perform Calculation ---{COLOR_RESET}")
    print("Enter your expression (or 'back' to return).")
    
    while True:
        try:
            user_input = input(f"{COLOR_CYAN}Enter expression: {COLOR_RESET}").strip()
            if not user_input:
                continue
            if user_input.lower() == 'back':
                break
                
            # Tokenize and parse
            tokens = tokenize(user_input)
            parser = Parser(tokens)
            result = parser.parse()
            
            res_str = format_num(result)
            print(f"{COLOR_GREEN}Result: {res_str}{COLOR_RESET}\n")
            
            # Save history
            history = load_history()
            history.append({
                "expression": user_input,
                "result": res_str
            })
            save_history(history)
            
        except KeyboardInterrupt:
            print()
            break
        except Exception as e:
            print(f"{COLOR_RED}Error: {e}{COLOR_RESET}\n")

# ----------------- MAIN LOOP -----------------

def main():
    """Main application loop."""
    # Enable ANSI escape codes on Windows Console
    if os.name == 'nt':
        try:
            import ctypes
            kernel32 = ctypes.windll.kernel32
            kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
        except Exception:
            pass

    print("Welcome to Simple Calculator!")
    
    while True:
        display_menu()
        choice = input("Enter your choice (1-4): ").strip()
        
        if choice == '1':
            perform_calculation()
        elif choice == '2':
            show_history()
        elif choice == '3':
            if os.path.exists(HISTORY_FILE):
                try:
                    os.remove(HISTORY_FILE)
                    print("\nCalculation history cleared.")
                except Exception as e:
                    print(f"\nError clearing history: {e}")
            else:
                print("\nCalculation history is already empty.")
        elif choice == '4':
            print("\nThank you for using Simple Calculator! Goodbye.")
            break
        else:
            print(f"\nInvalid choice. Please enter a number between 1 and 4.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\nGoodbye!")
        sys.exit(0)
