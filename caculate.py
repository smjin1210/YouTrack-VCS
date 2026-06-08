#Development Team Lead, please review this. 2026.06.083

import ast
import math
import tkinter as tk
from tkinter import ttk, messagebox


class SafeMathEvaluator:
    """
    Safely evaluates math expressions using ast instead of raw eval.
    Supports common scientific calculator functions.
    """

    def __init__(self, angle_mode_getter):
        self.angle_mode_getter = angle_mode_getter

        self.constants = {
            "pi": math.pi,
            "π": math.pi,
            "e": math.e,
            "tau": math.tau,
        }

        self.functions = {
            "sin": self._sin,
            "cos": self._cos,
            "tan": self._tan,
            "asin": self._asin,
            "acos": self._acos,
            "atan": self._atan,
            "sqrt": math.sqrt,
            "log": math.log10,
            "ln": math.log,
            "exp": math.exp,
            "abs": abs,
            "floor": math.floor,
            "ceil": math.ceil,
            "round": round,
            "factorial": self._factorial,
            "deg": math.degrees,
            "rad": math.radians,
        }

        self.binary_ops = {
            ast.Add: lambda a, b: a + b,
            ast.Sub: lambda a, b: a - b,
            ast.Mult: lambda a, b: a * b,
            ast.Div: lambda a, b: a / b,
            ast.FloorDiv: lambda a, b: a // b,
            ast.Mod: lambda a, b: a % b,
            ast.Pow: lambda a, b: a ** b,
        }

        self.unary_ops = {
            ast.UAdd: lambda a: +a,
            ast.USub: lambda a: -a,
        }

    def _to_radians_if_needed(self, value):
        if self.angle_mode_getter() == "DEG":
            return math.radians(value)
        return value

    def _from_radians_if_needed(self, value):
        if self.angle_mode_getter() == "DEG":
            return math.degrees(value)
        return value

    def _sin(self, value):
        return math.sin(self._to_radians_if_needed(value))

    def _cos(self, value):
        return math.cos(self._to_radians_if_needed(value))

    def _tan(self, value):
        return math.tan(self._to_radians_if_needed(value))

    def _asin(self, value):
        return self._from_radians_if_needed(math.asin(value))

    def _acos(self, value):
        return self._from_radians_if_needed(math.acos(value))

    def _atan(self, value):
        return self._from_radians_if_needed(math.atan(value))

    def _factorial(self, value):
        if isinstance(value, float) and not value.is_integer():
            raise ValueError("factorial은 정수만 사용할 수 있습니다.")
        value = int(value)
        if value < 0:
            raise ValueError("factorial은 음수에 사용할 수 없습니다.")
        return math.factorial(value)

    def evaluate(self, expression):
        expression = self._normalize_expression(expression)

        if not expression.strip():
            raise ValueError("계산식이 비어 있습니다.")

        tree = ast.parse(expression, mode="eval")
        return self._eval_node(tree.body)

    def _normalize_expression(self, expression):
        replacements = {
            "×": "*",
            "÷": "/",
            "^": "**",
            "√": "sqrt",
            "π": "pi",
        }

        for old, new in replacements.items():
            expression = expression.replace(old, new)

        return expression

    def _eval_node(self, node):
        if isinstance(node, ast.Constant):
            if isinstance(node.value, (int, float)):
                return node.value
            raise TypeError("숫자만 사용할 수 있습니다.")

        if isinstance(node, ast.Num):  # for older Python compatibility
            return node.n

        if isinstance(node, ast.BinOp):
            op_type = type(node.op)
            if op_type not in self.binary_ops:
                raise TypeError("지원하지 않는 연산자입니다.")
            left = self._eval_node(node.left)
            right = self._eval_node(node.right)
            return self.binary_ops[op_type](left, right)

        if isinstance(node, ast.UnaryOp):
            op_type = type(node.op)
            if op_type not in self.unary_ops:
                raise TypeError("지원하지 않는 단항 연산자입니다.")
            operand = self._eval_node(node.operand)
            return self.unary_ops[op_type](operand)

        if isinstance(node, ast.Name):
            if node.id in self.constants:
                return self.constants[node.id]
            raise NameError(f"알 수 없는 이름입니다: {node.id}")

        if isinstance(node, ast.Call):
            if not isinstance(node.func, ast.Name):
                raise TypeError("지원하지 않는 함수 호출입니다.")

            func_name = node.func.id

            if func_name not in self.functions:
                raise NameError(f"지원하지 않는 함수입니다: {func_name}")

            args = [self._eval_node(arg) for arg in node.args]

            if len(args) > 2:
                raise TypeError("함수 인자가 너무 많습니다.")

            return self.functions[func_name](*args)

        raise TypeError("지원하지 않는 계산식입니다.")


class ScientificCalculator(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Python 공학 계산기")
        self.geometry("520x720")
        self.minsize(500, 680)

        self.expression_var = tk.StringVar()
        self.result_var = tk.StringVar(value="0")
        self.angle_mode_var = tk.StringVar(value="DEG")
        self.memory_value = 0.0

        self.evaluator = SafeMathEvaluator(lambda: self.angle_mode_var.get())

        self._configure_style()
        self._create_layout()
        self._bind_keys()

    def _configure_style(self):
        self.configure(bg="#1f1f1f")

        style = ttk.Style(self)
        style.theme_use("clam")

        style.configure(
            "Display.TEntry",
            font=("Consolas", 22),
            padding=10,
            fieldbackground="#111111",
            foreground="#ffffff",
            bordercolor="#333333",
        )

        style.configure(
            "Result.TLabel",
            font=("Consolas", 18),
            background="#1f1f1f",
            foreground="#bbbbbb",
            anchor="e",
        )

        style.configure(
            "Mode.TLabel",
            font=("Arial", 11, "bold"),
            background="#1f1f1f",
            foreground="#f0f0f0",
        )

        style.configure(
            "Calc.TButton",
            font=("Arial", 13),
            padding=8,
            background="#333333",
            foreground="#ffffff",
        )

        style.map(
            "Calc.TButton",
            background=[("active", "#444444")],
            foreground=[("active", "#ffffff")],
        )

    def _create_layout(self):
        main = tk.Frame(self, bg="#1f1f1f", padx=12, pady=12)
        main.pack(fill="both", expand=True)

        top_frame = tk.Frame(main, bg="#1f1f1f")
        top_frame.pack(fill="x")

        ttk.Label(top_frame, text="Angle", style="Mode.TLabel").pack(side="left")

        mode_box = ttk.Combobox(
            top_frame,
            textvariable=self.angle_mode_var,
            values=["DEG", "RAD"],
            state="readonly",
            width=6,
            font=("Arial", 11),
        )
        mode_box.pack(side="left", padx=8)

        ttk.Label(
            top_frame,
            text="DEG: 각도 / RAD: 라디안",
            style="Mode.TLabel",
        ).pack(side="left", padx=6)

        self.expression_entry = ttk.Entry(
            main,
            textvariable=self.expression_var,
            style="Display.TEntry",
            justify="right",
        )
        self.expression_entry.pack(fill="x", pady=(16, 8))
        self.expression_entry.focus_set()

        self.result_label = ttk.Label(
            main,
            textvariable=self.result_var,
            style="Result.TLabel",
        )
        self.result_label.pack(fill="x", pady=(0, 10))

        button_area = tk.Frame(main, bg="#1f1f1f")
        button_area.pack(fill="both", expand=True)

        for i in range(8):
            button_area.rowconfigure(i, weight=1)

        for i in range(6):
            button_area.columnconfigure(i, weight=1)

        buttons = [
            ["MC", "MR", "M+", "M-", "C", "⌫"],
            ["sin", "cos", "tan", "(", ")", "÷"],
            ["asin", "acos", "atan", "7", "8", "9"],
            ["log", "ln", "sqrt", "4", "5", "6"],
            ["x²", "xʸ", "exp", "1", "2", "3"],
            ["π", "e", "n!", "0", ".", "×"],
            ["abs", "floor", "ceil", "+", "-", "%"],
            ["ANS", "±", "//", "=", "", ""],
        ]

        for row_index, row in enumerate(buttons):
            for col_index, label in enumerate(row):
                if label == "":
                    continue

                colspan = 1
                if label == "=":
                    colspan = 2

                button = ttk.Button(
                    button_area,
                    text=label,
                    style="Calc.TButton",
                    command=lambda value=label: self._on_button_click(value),
                )
                button.grid(
                    row=row_index,
                    column=col_index,
                    columnspan=colspan,
                    sticky="nsew",
                    padx=3,
                    pady=3,
                )

        history_frame = tk.LabelFrame(
            main,
            text="History",
            bg="#1f1f1f",
            fg="#ffffff",
            font=("Arial", 11, "bold"),
            padx=8,
            pady=8,
        )
        history_frame.pack(fill="both", expand=False, pady=(12, 0))

        self.history_list = tk.Listbox(
            history_frame,
            height=6,
            bg="#111111",
            fg="#ffffff",
            selectbackground="#555555",
            font=("Consolas", 10),
        )
        self.history_list.pack(fill="both", expand=True)
        self.history_list.bind("<Double-Button-1>", self._load_history_item)

    def _bind_keys(self):
        self.bind("<Return>", lambda event: self._calculate())
        self.bind("<KP_Enter>", lambda event: self._calculate())
        self.bind("<Escape>", lambda event: self._clear())
        self.bind("<BackSpace>", lambda event: self._backspace())

    def _on_button_click(self, label):
        if label == "C":
            self._clear()
        elif label == "⌫":
            self._backspace()
        elif label == "=":
            self._calculate()
        elif label == "MC":
            self.memory_value = 0.0
            self._show_status("Memory cleared")
        elif label == "MR":
            self._insert(self._format_number(self.memory_value))
        elif label == "M+":
            self._memory_add()
        elif label == "M-":
            self._memory_subtract()
        elif label == "ANS":
            self._insert(self.result_var.get())
        elif label == "±":
            self._toggle_sign()
        elif label == "sin":
            self._insert("sin(")
        elif label == "cos":
            self._insert("cos(")
        elif label == "tan":
            self._insert("tan(")
        elif label == "asin":
            self._insert("asin(")
        elif label == "acos":
            self._insert("acos(")
        elif label == "atan":
            self._insert("atan(")
        elif label == "log":
            self._insert("log(")
        elif label == "ln":
            self._insert("ln(")
        elif label == "sqrt":
            self._insert("sqrt(")
        elif label == "exp":
            self._insert("exp(")
        elif label == "abs":
            self._insert("abs(")
        elif label == "floor":
            self._insert("floor(")
        elif label == "ceil":
            self._insert("ceil(")
        elif label == "x²":
            self._insert("**2")
        elif label == "xʸ":
            self._insert("**")
        elif label == "n!":
            self._wrap_last_number_or_expression("factorial")
        elif label == "π":
            self._insert("pi")
        elif label == "÷":
            self._insert("/")
        elif label == "×":
            self._insert("*")
        else:
            self._insert(label)

    def _insert(self, text):
        entry = self.expression_entry
        cursor_index = entry.index(tk.INSERT)
        current = self.expression_var.get()
        new_expression = current[:cursor_index] + text + current[cursor_index:]
        self.expression_var.set(new_expression)
        entry.icursor(cursor_index + len(text))
        entry.focus_set()

    def _clear(self):
        self.expression_var.set("")
        self.result_var.set("0")
        self.expression_entry.focus_set()

    def _backspace(self):
        entry = self.expression_entry
        cursor_index = entry.index(tk.INSERT)

        if cursor_index == 0:
            return

        current = self.expression_var.get()
        new_expression = current[:cursor_index - 1] + current[cursor_index:]
        self.expression_var.set(new_expression)
        entry.icursor(cursor_index - 1)
        entry.focus_set()

    def _calculate(self):
        expression = self.expression_var.get()

        try:
            result = self.evaluator.evaluate(expression)
            formatted_result = self._format_number(result)

            self.result_var.set(formatted_result)
            self._add_history(expression, formatted_result)

        except ZeroDivisionError:
            self._show_error("0으로 나눌 수 없습니다.")
        except OverflowError:
            self._show_error("계산 결과가 너무 큽니다.")
        except ValueError as error:
            self._show_error(str(error))
        except Exception as error:
            self._show_error(f"계산식을 확인하세요. ({error})")

        self.expression_entry.focus_set()

    def _format_number(self, value):
        if isinstance(value, bool):
            return str(value)

        if isinstance(value, int):
            return str(value)

        if isinstance(value, float):
            if math.isinf(value) or math.isnan(value):
                return str(value)

            if value.is_integer():
                return str(int(value))

            return f"{value:.12g}"

        return str(value)

    def _add_history(self, expression, result):
        item = f"{expression} = {result}"
        self.history_list.insert(0, item)

        if self.history_list.size() > 30:
            self.history_list.delete(30, tk.END)

    def _load_history_item(self, event):
        selection = self.history_list.curselection()

        if not selection:
            return

        item = self.history_list.get(selection[0])

        if " = " in item:
            expression = item.split(" = ", 1)[0]
            self.expression_var.set(expression)
            self.expression_entry.icursor(tk.END)
            self.expression_entry.focus_set()

    def _memory_add(self):
        try:
            value = self.evaluator.evaluate(self.result_var.get())
            self.memory_value += value
            self._show_status(f"Memory: {self._format_number(self.memory_value)}")
        except Exception:
            self._show_error("현재 결과를 메모리에 더할 수 없습니다.")

    def _memory_subtract(self):
        try:
            value = self.evaluator.evaluate(self.result_var.get())
            self.memory_value -= value
            self._show_status(f"Memory: {self._format_number(self.memory_value)}")
        except Exception:
            self._show_error("현재 결과를 메모리에서 뺄 수 없습니다.")

    def _toggle_sign(self):
        current = self.expression_var.get().strip()

        if not current:
            return

        if current.startswith("-(") and current.endswith(")"):
            self.expression_var.set(current[2:-1])
        else:
            self.expression_var.set(f"-({current})")

        self.expression_entry.icursor(tk.END)
        self.expression_entry.focus_set()

    def _wrap_last_number_or_expression(self, function_name):
        current = self.expression_var.get().strip()

        if not current:
            return

        self.expression_var.set(f"{function_name}({current})")
        self.expression_entry.icursor(tk.END)
        self.expression_entry.focus_set()

    def _show_error(self, message):
        self.result_var.set("Error")
        messagebox.showerror("계산 오류", message)

    def _show_status(self, message):
        self.result_var.set(message)


def main():
    app = ScientificCalculator()
    app.mainloop()


if __name__ == "__main__":
    main()

