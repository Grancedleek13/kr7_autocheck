# -*- coding: utf-8 -*-
"""
Автопроверяемая контрольная работа (7 класс)
Тема: Программы и данные. Программное обеспечение компьютера

Запуск:
  python kr_app.py
"""
import json
import os
import re
import tkinter as tk
from tkinter import messagebox

HERE = os.path.dirname(os.path.abspath(__file__))

def norm_text(s: str) -> str:
    s = (s or "").strip().lower()
    s = s.replace("ё", "е")
    s = re.sub(r"\s+", " ", s)
    s = re.sub(r"[.!,;:]+$", "", s)
    return s

class ScrollFrame(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.canvas = tk.Canvas(self, highlightthickness=0)
        self.vsb = tk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.vsb.set)

        self.inner = tk.Frame(self.canvas)
        self.inner.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas_window = self.canvas.create_window((0, 0), window=self.inner, anchor="nw")

        self.canvas.pack(side="left", fill="both", expand=True)
        self.vsb.pack(side="right", fill="y")

        self.canvas.bind("<Configure>", self._on_canvas_configure)
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

    def _on_canvas_configure(self, event):
        self.canvas.itemconfigure(self.canvas_window, width=event.width)

    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Контрольная — 7 класс (ПО компьютера)")
        self.geometry("900x800")

        top = tk.Frame(self, padx=12, pady=10)
        top.pack(fill="x")

        tk.Label(top, text="ФИО:", font=("Segoe UI", 11)).pack(side="left")
        self.name_var = tk.StringVar()
        tk.Entry(top, textvariable=self.name_var, width=36, font=("Segoe UI", 11)).pack(side="left", padx=(8, 14))

        self.score_var = tk.StringVar(value="Баллы: —")
        tk.Label(top, textvariable=self.score_var, font=("Segoe UI", 11, "bold")).pack(side="left")

        tk.Button(top, text="Проверить", font=("Segoe UI", 11, "bold"), command=self.check).pack(side="right")
        tk.Button(top, text="Сбросить", font=("Segoe UI", 11), command=self.reset).pack(side="right", padx=(0, 10))

        self.sf = ScrollFrame(self)
        self.sf.pack(fill="both", expand=True, padx=12, pady=(0, 12))

        with open(os.path.join(HERE, "questions.json"), "r", encoding="utf-8") as f:
            self.questions = json.load(f)

        self.widgets = []
        self._build()

    def _qbox(self, parent, title: str):
        box = tk.Frame(parent, bd=1, relief="solid", padx=10, pady=10)
        tk.Label(box, text=title, font=("Segoe UI", 12, "bold"), wraplength=840, justify="left").pack(anchor="w")
        return box

    def _build(self):
        for q in self.questions:
            box = self._qbox(self.sf.inner, q.get("title", f"Вопрос {q.get('id','')}"))
            box.pack(fill="x", pady=8)

            prompt = q.get("prompt", "")
            if prompt:
                tk.Label(box, text=prompt, font=("Segoe UI", 11), wraplength=840, justify="left").pack(anchor="w", pady=(6, 8))

            qtype = q["type"]
            record = {"type": qtype, "id": q.get("id")}
            feedback = tk.Label(box, text="", font=("Segoe UI", 10, "bold"), wraplength=840, justify="left")
            record["feedback"] = feedback

            if qtype == "multi_select":
                vars_ = []
                for opt in q["options"]:
                    v = tk.IntVar(value=0)
                    tk.Checkbutton(box, text=opt, variable=v, font=("Segoe UI", 11), wraplength=820, justify="left").pack(anchor="w")
                    vars_.append(v)
                record["get"] = lambda vars_=vars_: [i for i, v in enumerate(vars_) if v.get() == 1]

            elif qtype == "single_select":
                v = tk.IntVar(value=-1)
                for i, opt in enumerate(q["options"]):
                    tk.Radiobutton(box, text=opt, variable=v, value=i, font=("Segoe UI", 11), wraplength=820, justify="left").pack(anchor="w")
                record["get"] = v.get

            elif qtype == "text":
                v = tk.StringVar()
                tk.Entry(box, textvariable=v, width=44, font=("Segoe UI", 11)).pack(anchor="w")
                record["get"] = v.get

            elif qtype == "text_blanks":
                vars_ = []
                for i in range(int(q.get("blanks", 1))):
                    row = tk.Frame(box)
                    row.pack(anchor="w", pady=2, fill="x")
                    tk.Label(row, text=f"Поле {i+1}:", font=("Segoe UI", 11)).pack(side="left")
                    v = tk.StringVar()
                    tk.Entry(row, textvariable=v, width=50, font=("Segoe UI", 11)).pack(side="left", padx=8)
                    vars_.append(v)
                record["get"] = lambda vars_=vars_: [v.get() for v in vars_]

            elif qtype == "matching":
                left = q["left"]
                right = q["right"]
                tk.Label(box, text="Варианты:", font=("Segoe UI", 11, "bold")).pack(anchor="w", pady=(2, 2))
                for r in right:
                    tk.Label(box, text="• " + r, font=("Segoe UI", 11), wraplength=840, justify="left").pack(anchor="w")
                tk.Label(box, text="Ответы (буквы):", font=("Segoe UI", 11, "bold")).pack(anchor="w", pady=(8, 2))

                vars_ = []
                for i, term in enumerate(left):
                    row = tk.Frame(box)
                    row.pack(anchor="w", pady=2, fill="x")
                    tk.Label(row, text=f"{i+1}) {term} →", font=("Segoe UI", 11)).pack(side="left")
                    v = tk.StringVar()
                    tk.Entry(row, textvariable=v, width=10, font=("Segoe UI", 11)).pack(side="left", padx=8)
                    vars_.append(v)
                record["get"] = lambda vars_=vars_: [v.get() for v in vars_]

            else:
                tk.Label(box, text=f"(Неизвестный тип: {qtype})", fg="red").pack(anchor="w")

            feedback.pack(anchor="w", pady=(8, 0))
            self.widgets.append(record)

    def reset(self):
        self.destroy()
        App().mainloop()

    def _check_one(self, q, rec):
        qtype = q["type"]
        user = rec["get"]()

        if qtype == "multi_select":
            correct = sorted(q["answer"])
            ok = sorted(user) == correct
            hint = "Правильные варианты: " + ", ".join(str(i+1) for i in correct)
            return ok, hint

        if qtype == "single_select":
            ok = user == q["answer"]
            hint = f"Правильный вариант: {q['answer']+1}"
            return ok, hint

        if qtype == "text":
            u = norm_text(user)
            ok = any(u == norm_text(a) for a in q["answers"])
            hint = "Пример: " + (q["answers"][0] if q["answers"] else "—")
            return ok, hint

        if qtype == "text_blanks":
            answers = q["answers"]
            if not isinstance(user, list) or len(user) != len(answers):
                return False, "Проверьте заполнение полей."
            ok_all = True
            for i, u in enumerate(user):
                u_n = norm_text(u)
                ok_i = any(u_n == norm_text(a) for a in answers[i])
                ok_all = ok_all and ok_i
            hint = "Проверьте названия категорий/примеров."
            return ok_all, hint

        if qtype == "matching":
            ans = q["answer"]
            ok_all = True
            for i, u in enumerate(user):
                u_n = (u or "").strip().upper()
                u_n = re.sub(r"[^A-ZА-ЯЁ]", "", u_n)
                corr = str(ans.get(str(i), "")).strip().upper()
                if u_n != corr:
                    ok_all = False
            # подсказка: правильные пары
            pairs = []
            for i in range(len(q["left"])):
                pairs.append(f"{i+1}) {q['left'][i]}→{ans.get(str(i),'')}")
            hint = "Правильно: " + "; ".join(pairs)
            return ok_all, hint

        return False, "—"

    def check(self):
        total = len(self.questions)
        score = 0

        for q, rec in zip(self.questions, self.widgets):
            ok, hint = self._check_one(q, rec)
            if ok:
                score += 1
                rec["feedback"].config(text="✅ Верно", fg="green")
            else:
                rec["feedback"].config(text="❌ Неверно. " + hint, fg="red")

        self.score_var.set(f"Баллы: {score}/{total}")

        name = (self.name_var.get() or "").strip()
        if name:
            messagebox.showinfo("Результат", f"{name}, ваш результат: {score}/{total}")
        else:
            messagebox.showinfo("Результат", f"Ваш результат: {score}/{total}")

if __name__ == "__main__":
    App().mainloop()
