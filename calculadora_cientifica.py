"""Calculadora científica de escritorio hecha con Tkinter."""

import ast
import math
import operator
import tkinter as tk
from tkinter import ttk


class CalculadoraCientifica:
    def __init__(self, root):
        self.root = root
        self.root.title("Calculadora científica")
        self.root.geometry("420x570")
        self.root.minsize(360, 500)
        self.root.configure(bg="#111827")
        self.expression = tk.StringVar()
        self.result = tk.StringVar(value="0")
        self.angle_mode = tk.StringVar(value="Grados")
        self._build_ui()

    def _build_ui(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TCombobox", fieldbackground="#1f2937", background="#1f2937", foreground="white")

        display = tk.Frame(self.root, bg="#111827", padx=18, pady=18)
        display.pack(fill="x")
        tk.Label(display, text="CALCULADORA CIENTÍFICA", bg="#111827", fg="#9ca3af",
                 font=("Segoe UI", 10, "bold")).pack(anchor="w")
        self.input_entry = tk.Entry(display, textvariable=self.expression, justify="right",
                                    bg="#1f2937", fg="white", insertbackground="white",
                                    relief="flat", font=("Segoe UI", 20), bd=0)
        self.input_entry.pack(fill="x", ipady=12, pady=(10, 5))
        self.input_entry.bind("<Return>", lambda _event: self.calculate())
        tk.Label(display, textvariable=self.result, bg="#111827", fg="#60a5fa",
                 anchor="e", font=("Segoe UI", 17)).pack(fill="x")

        controls = tk.Frame(self.root, bg="#111827", padx=14)
        controls.pack(fill="x", pady=(0, 8))
        tk.Label(controls, text="Ángulo:", bg="#111827", fg="#d1d5db",
                 font=("Segoe UI", 10)).pack(side="left", padx=(4, 8))
        ttk.Combobox(controls, textvariable=self.angle_mode, values=("Grados", "Radianes"),
                     state="readonly", width=10).pack(side="left")

        keys = [
            [("sin", "sin("), ("cos", "cos("), ("tan", "tan("), ("√", "sqrt(")],
            [("ln", "ln("), ("log", "log("), ("n!", "fact("), ("π", "pi")],
            [("7", "7"), ("8", "8"), ("9", "9"), ("÷", "/")],
            [("4", "4"), ("5", "5"), ("6", "6"), ("×", "*")],
            [("1", "1"), ("2", "2"), ("3", "3"), ("−", "-")],
            [("0", "0"), (".", "."), ("e", "e"), ("+", "+")],
            [("(", "("), (")", ")"), ("x²", "**2"), ("^", "**")],
        ]
        grid = tk.Frame(self.root, bg="#111827", padx=14, pady=4)
        grid.pack(fill="both", expand=True)
        for row_index, row in enumerate(keys):
            for column, (label, value) in enumerate(row):
                self._button(grid, label, lambda v=value: self.insert(v), row_index, column)
        self._button(grid, "⌫", self.backspace, 7, 0, color="#374151")
        self._button(grid, "C", self.clear, 7, 1, color="#b91c1c")
        self._button(grid, "=", self.calculate, 7, 2, color="#2563eb", span=2)
        for column in range(4):
            grid.grid_columnconfigure(column, weight=1, uniform="buttons")
        for row in range(8):
            grid.grid_rowconfigure(row, weight=1, uniform="buttons")

    def _button(self, parent, label, command, row, column, color="#1f2937", span=1):
        button = tk.Button(parent, text=label, command=command, bg=color, fg="white",
                           activebackground="#4b5563", activeforeground="white",
                           relief="flat", bd=0, font=("Segoe UI", 13, "bold"), cursor="hand2")
        button.grid(row=row, column=column, columnspan=span, sticky="nsew", padx=4, pady=4, ipady=5)

    def insert(self, value):
        self.input_entry.insert(tk.INSERT, value)
        self.input_entry.focus_set()

    def backspace(self):
        try:
            start, end = self.input_entry.index(tk.SEL_FIRST), self.input_entry.index(tk.SEL_LAST)
            self.input_entry.delete(start, end)
        except tk.TclError:
            position = self.input_entry.index(tk.INSERT)
            if position:
                self.input_entry.delete(position - 1)

    def clear(self):
        self.expression.set("")
        self.result.set("0")

    def calculate(self):
        try:
            parsed = ast.parse(self.expression.get().replace("^", "**"), mode="eval")
            value = self._evaluate(parsed.body)
            if isinstance(value, float) and not math.isfinite(value):
                raise ValueError
            self.result.set(f"= {value:.12g}" if isinstance(value, float) else f"= {value}")
        except (ValueError, TypeError, SyntaxError, ZeroDivisionError, OverflowError):
            self.result.set("Expresión no válida")

    def _evaluate(self, node):
        binary = {ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul,
                  ast.Div: operator.truediv, ast.Pow: operator.pow, ast.Mod: operator.mod}
        unary = {ast.UAdd: operator.pos, ast.USub: operator.neg}
        if isinstance(node, ast.Constant) and type(node.value) in (int, float):
            return node.value
        if isinstance(node, ast.Name) and node.id in {"pi", "e"}:
            return math.pi if node.id == "pi" else math.e
        if isinstance(node, ast.BinOp) and type(node.op) in binary:
            return binary[type(node.op)](self._evaluate(node.left), self._evaluate(node.right))
        if isinstance(node, ast.UnaryOp) and type(node.op) in unary:
            return unary[type(node.op)](self._evaluate(node.operand))
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and len(node.args) == 1 and not node.keywords:
            value = self._evaluate(node.args[0])
            name = node.func.id
            if name in {"sin", "cos", "tan"}:
                angle = math.radians(value) if self.angle_mode.get() == "Grados" else value
                return getattr(math, name)(angle)
            if name == "sqrt": return math.sqrt(value)
            if name == "ln": return math.log(value)
            if name == "log": return math.log10(value)
            if name == "fact" and value >= 0 and float(value).is_integer():
                return math.factorial(int(value))
        raise ValueError("Expresión no permitida")


if __name__ == "__main__":
    ventana = tk.Tk()
    CalculadoraCientifica(ventana)
    ventana.mainloop()
